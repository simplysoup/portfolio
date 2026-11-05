/* Original touch-first navigation study. Native WAAPI, ease curves from the
   motion references; no reference artwork, scripts or licensed components. */
(() => {
  'use strict';
  const EASE='cubic-bezier(.65,0,.35,1)';
  const EXPO='cubic-bezier(.16,1,.3,1)';
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let teardown=()=>{};
  function initMobileNav(){
    teardown();
    const panel=document.querySelector('[data-mobile-nav]');
    const toggle=document.querySelector('[data-mobile-nav-toggle]');
    if(!panel||!toggle)return;
    const links=[...panel.querySelectorAll('nav a')];
    let opened=false,animating=false;
    const animate=(node,frames,options)=>reduced.matches?Promise.resolve():node.animate(frames,{...options,fill:'both'}).finished.catch(()=>{});
    async function open(){
      if(animating||opened)return;
      animating=true;opened=true;
      panel.inert=false;panel.setAttribute('aria-hidden','false');
      toggle.setAttribute('aria-expanded','true');toggle.setAttribute('aria-label','Close navigation');
      toggle.querySelector('span').textContent='Close';
      document.body.classList.add('menu-open');
      panel.style.visibility='visible';
      const a=animate(panel,[{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)'}],{duration:670,easing:EASE});
      links.forEach((link,i)=>{if(!reduced.matches)link.animate([{opacity:0,transform:'translateY(80px)'},{opacity:1,transform:'translateY(0)'}],{duration:980,delay:100+i*85,easing:EXPO,fill:'both'}).finished.then(()=>link.getAnimations().forEach(x=>x.cancel())).catch(()=>{})});
      await a;animating=false;links[0]?.focus({preventScroll:true});
    }
    async function close(restoreFocus=true){
      if(!opened||animating)return;
      animating=true;opened=false;
      const a=animate(panel,[{clipPath:'inset(0 0 0% 0)'},{clipPath:'inset(0 0 100% 0)'}],{duration:560,easing:EASE});
      await a;
      panel.style.visibility='hidden';panel.setAttribute('aria-hidden','true');panel.inert=true;
      toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','Open navigation');
      toggle.querySelector('span').textContent='Menu';
      document.body.classList.remove('menu-open');
      animating=false;
      if(restoreFocus)toggle.focus({preventScroll:true});
    }
    function onToggle(){opened?close():open()}
    function onKey(e){
      if(!opened)return;
      if(e.key==='Escape'){e.preventDefault();close();return;}
      if(e.key==='Tab'){const focusables=[toggle,...links];const at=focusables.indexOf(document.activeElement);if(at<0)return;if(e.shiftKey&&at===0){e.preventDefault();links.at(-1).focus()}else if(!e.shiftKey&&at===focusables.length-1){e.preventDefault();toggle.focus()}}
    }
    function onNavigate(){close(false)}
    function onHash(){if(opened){close(false)}}
    toggle.addEventListener('click',onToggle);
    document.addEventListener('keydown',onKey);
    window.addEventListener('hashchange',onHash);
    links.forEach(a=>a.addEventListener('click',onNavigate));
    teardown=()=>{toggle.removeEventListener('click',onToggle);document.removeEventListener('keydown',onKey);window.removeEventListener('hashchange',onHash);links.forEach(a=>a.removeEventListener('click',onNavigate));document.body.classList.remove('menu-open')};
  }
  window.initMobileNav=initMobileNav;
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initMobileNav);
  else initMobileNav();
})();
