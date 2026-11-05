/* Scroll-synchronized illustration study. A small, deterministic analogue of
   ScrollTrigger-style scrub, without smoothing the user's scroll position.
   Only properties of existing illustrations are updated. */
(()=>{
 'use strict';
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 let scheduled=false,active=true;
 const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 function tick(){
   scheduled=false;
   if(reduced.matches || document.hidden)return;
   const research=document.querySelector('.atelier-research');
   if(research){
     const r=research.getBoundingClientRect();
     if(r.top<innerHeight && r.bottom>0){
       const amount=clamp((innerHeight-r.top)/(innerHeight+r.height),0,1);
       research.style.setProperty('--research-turn',`${((amount-.5)*45).toFixed(2)}deg`);
       research.style.setProperty('--research-lift',`${((amount-.5)*-30).toFixed(2)}px`);
       research.dataset.scrollPhase=String(Math.round(amount*100));
     }
   }
   const showcase=document.querySelector('.motion-gallery');
   if(showcase){
     const r=showcase.getBoundingClientRect();
     if(r.top<innerHeight && r.bottom>0){
       const amount=clamp((innerHeight-r.top)/(innerHeight+r.height),0,1);
       showcase.style.setProperty('--gallery-turn',`${((amount-.5)*18).toFixed(2)}px`);
       showcase.dataset.scrollPhase=String(Math.round(amount*100));
     }
   }
 }
 function request(){if(!scheduled){scheduled=true;requestAnimationFrame(tick)}}
 window.addEventListener('scroll',request,{passive:true});
 window.addEventListener('resize',request,{passive:true});
 document.addEventListener('visibilitychange',request);
 window.addEventListener('hashchange',request);
 reduced.addEventListener?.('change',request);
 request();
})();
