/* SCROLL CHAPTERS / scroll-driven composition, not scroll-jacking.
   The browser owns the scroll. We only map progress to CSS parameters. */
(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const clamp = x => Math.max(0, Math.min(1,x));
  let cleanup = () => {};
  function initShowcases(){
    cleanup();
    const root = document.querySelector('[data-showcases]');
    if(!root) return;
    const sections = [...root.querySelectorAll('[data-folio]')];
    let raf=0;
    function measure(){
      raf=0;
      const vh = window.innerHeight || document.documentElement.clientHeight;
      for(const section of sections){
        const rect=section.getBoundingClientRect();
        // Completely outside viewport: avoid unnecessary style recalculation.
        if(rect.bottom < -vh*.3 || rect.top > vh*1.35) continue;
        const hold = Math.max(1, rect.height-vh);
        const progress = clamp(-rect.top/hold);
        const entry = clamp((vh-rect.top)/(vh*.86));
        const pressure = Math.pow(Math.sin(Math.PI*progress),2);
        const release = clamp((progress-.72)/.28);
        section.style.setProperty('--entry',reduce.matches?'1':entry.toFixed(4));
        section.style.setProperty('--progress',progress.toFixed(4));
        section.style.setProperty('--pressure',reduce.matches?'0':pressure.toFixed(4));
        section.style.setProperty('--release',reduce.matches?'0':release.toFixed(4));
        section.classList.toggle('is-engaged',entry>.8&&release<.7);
      }
    }
    const schedule = () => {if(!raf)raf=requestAnimationFrame(measure)};
    window.addEventListener('scroll',schedule,{passive:true});
    window.addEventListener('resize',schedule,{passive:true});
    reduce.addEventListener?.('change',schedule);
    schedule();
    cleanup = () => {
      window.removeEventListener('scroll',schedule);
      window.removeEventListener('resize',schedule);
      reduce.removeEventListener?.('change',schedule);
      if(raf)cancelAnimationFrame(raf);
    };
  }
  window.initShowcases=initShowcases;
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initShowcases);
  else initShowcases();
})();
