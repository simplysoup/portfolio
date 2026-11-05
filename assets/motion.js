/* Atelier motion direction, inspired by general techniques observed in the
 * supplied reference bundles: masked entrance, motion timing, scroll reveals,
 * spring followers and a page curtain. Original implementation, using native
 * Web Animations API + IntersectionObserver rather than copied site code.
 */
(function(){
 'use strict';
 const ENTER='cubic-bezier(0.16, 1, 0.3, 1)'; // expo-out family
 const CURTAIN='cubic-bezier(0.65, 0, 0.35, 1)'; // smooth symmetric transition
 const prefers=window.matchMedia('(prefers-reduced-motion: reduce)');
 let teardown=()=>{},navigating=false;
 const animate=(el,frames,opts)=>{
   if(!el||prefers.matches||typeof el.animate!=='function')return null;
   const a=el.animate(frames,{fill:'both',...opts});
   a.finished.then(()=>a.cancel()).catch(()=>{});
   return a;
 };
 const safeNext=(fn)=>requestAnimationFrame(()=>requestAnimationFrame(fn));
 function initMotionSystem(){
   teardown();
   const root=document.querySelector('main');if(!root)return;
   root.dataset.motionReady='true';
   if(prefers.matches){root.dataset.motionMode='reduced';return;}
   root.dataset.motionMode='full';
   const hero=root.querySelector('[data-hero-scene]');
   const observers=[];
   const destroyers=[];
   if(hero){
     const lines=hero.querySelectorAll('[data-line-inner]');
     lines.forEach((el,i)=>animate(el,[
       {transform:'translate3d(0,112%,0)',opacity:.3},
       {transform:'translate3d(0,0,0)',opacity:1}
     ],{duration:1230+110*i,delay:80+105*i,easing:ENTER}));
     const nodes=[
       ['.atelier-greeting',220],['.atelier-hero-meta',180],
       ['.atelier-intro',610],['.atelier-actions',720],['.hero-bottom-line',960]
     ];
     for(const [selector,delay] of nodes){
       const el=hero.querySelector(selector);
       animate(el,[{opacity:0,transform:'translate3d(0,22px,0)'},{opacity:1,transform:'translate3d(0,0,0)'}],{duration:1050,delay,easing:ENTER});
     }
     animate(hero.querySelector('.artwork-plate'),[
       {opacity:.2,transform:'translate3d(30px,12px,0) scale(.92) rotate(-4deg)'},
       {opacity:1,transform:'translate3d(0,0,0) scale(1) rotate(0deg)'}
     ],{duration:1700,delay:230,easing:ENTER});
   }
   // Scroll choreography: real motion only when an element enters the viewport.
   const targets=[
     ...root.querySelectorAll('.atelier-now-inner,.atelier-section-head,.atelier-project,.atelier-section-end,.atelier-research-text,.research-fig,.page-head,.article-header,.article-layout,.interactive-intro,.rag-exhibit,.trend-exhibit,.footer-intro,.about-layout')
   ];
   if('IntersectionObserver' in window){
     const observed=new IntersectionObserver(entries=>{
       for(const entry of entries){
         if(!entry.isIntersecting)continue;
         const el=entry.target;
         observed.unobserve(el);
         const isProject=el.classList.contains('atelier-project');
         const rank=isProject?Array.prototype.indexOf.call(el.parentElement.children,el):0;
         const isFig=el.classList.contains('research-fig');
         animate(el,[
           {opacity:0,transform:`translate3d(0,${isProject?60:34}px,0) ${isFig?'scale(.96)':'scale(1)'}`,filter:isProject?'blur(5px)':'blur(0px)'},
           {opacity:1,transform:'translate3d(0,0,0) scale(1)',filter:'blur(0px)'}
         ],{duration:isProject?950:850,delay:Math.min(rank,4)*125,easing:ENTER});
         el.dataset.motionEntered='true';
       }
     },{rootMargin:'0px 0px -9% 0px',threshold:.12});
     targets.forEach(el=>observed.observe(el));
     observers.push(observed);
   }else targets.forEach(el=>el.dataset.motionEntered='true');
   // Active project illustrations in the viewport on touch devices.
   const projects=root.querySelectorAll('.atelier-project');
   if(projects.length){
     if('IntersectionObserver' in window){
       const activeObserver=new IntersectionObserver(entries=>{
         for(const entry of entries){
           if(entry.isIntersecting&&entry.intersectionRatio>.42)entry.target.classList.add('is-current');
           else entry.target.classList.remove('is-current');
         }
       },{threshold:[0,.25,.42,.6,.9]});
       projects.forEach(el=>activeObserver.observe(el));observers.push(activeObserver);
     }
     projects.forEach(el=>{
       const onEnter=()=>el.classList.add('is-interacting');
       const onLeave=()=>el.classList.remove('is-interacting');
       el.addEventListener('mouseenter',onEnter);el.addEventListener('mouseleave',onLeave);
       el.addEventListener('focusin',onEnter);el.addEventListener('focusout',onLeave);
       destroyers.push(()=>{
         el.removeEventListener('mouseenter',onEnter);el.removeEventListener('mouseleave',onLeave);
         el.removeEventListener('focusin',onEnter);el.removeEventListener('focusout',onLeave);
       });
     });
   }
   // Small spring-like proximity motion for inline arrows, never for text or cards.
   if(window.matchMedia('(pointer:fine)').matches){
     root.querySelectorAll('.atelier-text-link').forEach(link=>{
       const arrow=link.querySelector('span[aria-hidden]');if(!arrow)return;
       let x=0,y=0,vx=0,vy=0,tx=0,ty=0,frame=0,last=0,active=false;
       const follow=t=>{
         if(!arrow.isConnected){frame=0;return;}
         const dt=Math.min(.04,(t-(last||t-16))/1000);last=t;
         vx+=(72*(tx-x)-15*vx)*dt;vy+=(72*(ty-y)-15*vy)*dt;
         x+=vx*dt;y+=vy*dt;
         arrow.style.transform=`translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0)`;
         if(active||Math.abs(x)+Math.abs(y)+Math.abs(vx)+Math.abs(vy)>.09)frame=requestAnimationFrame(follow);
         else frame=0;
       };
       const move=e=>{
         const r=link.getBoundingClientRect();
         tx=Math.max(-7,Math.min(7,(e.clientX-r.left-r.width/2)*.14));
         ty=Math.max(-5,Math.min(5,(e.clientY-r.top-r.height/2)*.13));
         active=true;if(!frame)frame=requestAnimationFrame(follow);
       };
       const leave=()=>{active=false;tx=ty=0;if(!frame)frame=requestAnimationFrame(follow)};
       link.addEventListener('pointermove',move,{passive:true});link.addEventListener('pointerleave',leave,{passive:true});
       destroyers.push(()=>{cancelAnimationFrame(frame);arrow.style.transform='';link.removeEventListener('pointermove',move);link.removeEventListener('pointerleave',leave)});
     });
   }
   teardown=()=>{observers.forEach(o=>o.disconnect());destroyers.forEach(fn=>fn())};
 }
 function shouldHandle(a,e){
   if(!a||e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.altKey||e.shiftKey||a.hasAttribute('download')||a.target==='_blank')return false;
   const href=a.getAttribute('href');
   if(!href||href.startsWith('mailto:')||href.startsWith('tel:')||href==='#'||href.startsWith('#selected')||href.startsWith('#main'))return false;
   if(href.startsWith('#/'))return true; // portable preview navigation
   if(href.startsWith('#'))return false;
   try{const u=new URL(href,location.href);return u.origin===location.origin && u.pathname!==location.pathname && !u.pathname.match(/\.(pdf|zip|png|svg|jpg|webp)$/i)}catch{return false}
 }
 async function transitionNavigation(href){
   if(navigating)return;
   if(prefers.matches){location.href=href;return;}
   const veil=document.querySelector('[data-route-veil]');
   if(!veil||typeof veil.animate!=='function'){location.href=href;return;}
   navigating=true;document.documentElement.dataset.transition='out';
   veil.style.visibility='visible';
   const enter=veil.animate([{transform:'translate3d(0,101%,0)'},{transform:'translate3d(0,0,0)'}],{duration:470,easing:CURTAIN,fill:'forwards'});
   try{await enter.finished}catch{} enter.cancel();
   veil.style.transform='translate3d(0,0,0)';
   if(href.startsWith('#/')){
     location.hash=href;
     await new Promise(resolve=>setTimeout(resolve,65));
     document.documentElement.dataset.transition='in';
     const leave=veil.animate([{transform:'translate3d(0,0,0)'},{transform:'translate3d(0,-101%,0)'}],{duration:560,easing:CURTAIN,fill:'forwards'});
     try{await leave.finished}catch{} leave.cancel();
     veil.style.visibility='hidden';veil.style.transform='translate3d(0,101%,0)';
     delete document.documentElement.dataset.transition;navigating=false;
   }else location.href=href;
 }
 document.addEventListener('click',e=>{
   const a=e.target.closest?.('a[href]');
   if(!shouldHandle(a,e))return;
   e.preventDefault();transitionNavigation(a.getAttribute('href'));
 });
 window.initMotionSystem=initMotionSystem;
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initMotionSystem);
 else initMotionSystem();
})();
