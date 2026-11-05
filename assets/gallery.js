/* Independent motion study: cinematic project sequencing + touch-first controls.
   Motion timings are inspired by (not copied from) the supplied creative references.
   Smooth curtain: cubic-bezier(.65,0,.35,1); reveals: cubic-bezier(.16,1,.3,1).
*/
(() => {
  'use strict';
  const CURTAIN='cubic-bezier(.65,0,.35,1)';
  const REVEAL='cubic-bezier(.16,1,.3,1)';
  const mq=matchMedia('(prefers-reduced-motion: reduce)');
  let teardown=()=>{};
  const animate=(node,frames,options)=>{
    if(!node || mq.matches || typeof node.animate !== 'function') return Promise.resolve();
    const animation=node.animate(frames,{...options,fill:'both'});
    return animation.finished.catch(()=>{}).then(()=>animation.cancel());
  };
  function initGallery(){
    teardown();
    const root=document.querySelector('[data-motion-gallery]');
    if(!root) return;
    const captions=[...root.querySelectorAll('[data-gallery-copy]')];
    const scenes=[...root.querySelectorAll('[data-gallery-scene]')];
    const steps=[...root.querySelectorAll('[data-gallery-step]')];
    const display=root.querySelector('[data-gallery-swipe]');
    const veil=root.querySelector('.gallery-curtain');
    const count=root.querySelector('[data-gallery-count]');
    const prev=root.querySelector('[data-gallery-prev]');
    const next=root.querySelector('[data-gallery-next]');
    const signal=root.querySelector('.gallery-hover-signal');
    let active=0,busy=false,desired=null,gesture=null,gestureAt=0;
    root.dataset.galleryReady='true';
    root.dataset.galleryIndex='0';
    root.dataset.galleryChanges='0';
    function paint(index){
      active=(index+scenes.length)%scenes.length;
      root.dataset.galleryIndex=String(active);
      count.innerHTML=String(active+1).padStart(2,'0')+' <span>/ 03</span>';
      captions.forEach((el,i)=>{el.hidden=i!==active;el.classList.toggle('is-active',i===active)});
      scenes.forEach((el,i)=>{el.hidden=i!==active;el.classList.toggle('is-active',i===active)});
      steps.forEach((el,i)=>{el.classList.toggle('is-active',i===active);el.setAttribute('aria-current',String(i===active))});
    }
    async function go(index,source='button'){
      index=(index+scenes.length)%scenes.length;
      if(index===active){return;}
      if(busy){desired=index;return;}
      busy=true;
      const outgoing=captions[active];
      root.dataset.galleryMode=source;
      if(!mq.matches){
        await Promise.all([
          animate(outgoing,[{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(-22px)'}],{duration:250,easing:CURTAIN}),
          animate(veil,[{transform:'scaleX(0)'},{transform:'scaleX(1)'}],{duration:390,easing:CURTAIN})
        ]);
      }
      paint(index);
      root.dataset.galleryChanges=String(Number(root.dataset.galleryChanges)+1);
      if(!mq.matches){
        await Promise.all([
          animate(veil,[{transform:'scaleX(1)',transformOrigin:'right'},{transform:'scaleX(0)',transformOrigin:'right'}],{duration:520,easing:CURTAIN}),
          animate(captions[active],[{opacity:0,transform:'translate3d(0,36px,0)'},{opacity:1,transform:'translate3d(0,0,0)'}],{duration:810,delay:75,easing:REVEAL}),
          animate(scenes[active].querySelector('.gallery-art'),[{opacity:.25,transform:'translate3d(12px,12px,0) scale(1.07)'},{opacity:1,transform:'translate3d(0,0,0) scale(1)'}],{duration:1050,easing:REVEAL})
        ]);
      }
      busy=false;
      if(desired!==null){const d=desired;desired=null;go(d,'queued');}
    }
    function advance(n,source){go(active+n,source)}
    function elasticOut(t){
      if(t===0||t===1)return t;
      const period=.4,shift=period/(2*Math.PI)*Math.asin(1);
      return Math.pow(2,-10*t)*Math.sin((t-shift)*2*Math.PI/period)+1;
    }
    function feedback(node,direction){
      if(mq.matches||typeof node.animate!=='function')return;
      // Keyframed GSAP-like elastic return, independently sampled and
      // applied only to the tiny arrow, never to reading content.
      const glyph=node.querySelector('span[data-arrow]');if(!glyph)return;
      const frames=Array.from({length:26},(_,i)=>{
        const t=i/25;return {offset:t,transform:`translateX(${(direction*(1-elasticOut(t))*16).toFixed(2)}px)`};
      });
      glyph.animate(frames,{duration:760,easing:'linear'});
    }
    function onPrev(){advance(-1,'button');feedback(prev,-1)};function onNext(){advance(1,'button');feedback(next,1)}
    prev.addEventListener('click',onPrev);next.addEventListener('click',onNext);
    const stepCallbacks=steps.map((node,i)=>{const fn=()=>go(i,'tab');node.addEventListener('click',fn);return fn});
    function trackStart(x,y){gesture={x,y,t:performance.now()}}
    function trackEnd(x,y){
      if(!gesture)return;
      const dx=x-gesture.x,dy=y-gesture.y,elapsed=performance.now()-gesture.t;gesture=null;
      if(Math.abs(dx)>45 && Math.abs(dx)>Math.abs(dy)*1.2){advance(dx<0?1:-1,'swipe');gestureAt=Date.now();}
      else if(Math.abs(dx)<12 && Math.abs(dy)<12 && elapsed<700){advance(1,'tap');}
    }
    function pointerDown(e){if(e.pointerType==='touch'||e.pointerType==='pen')trackStart(e.clientX,e.clientY)}
    function pointerUp(e){if(gesture)trackEnd(e.clientX,e.clientY)}
    function touchStart(e){if(!('PointerEvent' in window) && e.changedTouches.length)trackStart(e.changedTouches[0].clientX,e.changedTouches[0].clientY)}
    function touchEnd(e){if(!('PointerEvent' in window) && e.changedTouches.length)trackEnd(e.changedTouches[0].clientX,e.changedTouches[0].clientY)}
    function onKey(e){if(e.target.closest('a,button,input'))return;if(e.key==='ArrowRight'){e.preventDefault();advance(1,'keyboard')}if(e.key==='ArrowLeft'){e.preventDefault();advance(-1,'keyboard')}}
    function onMove(e){if(e.pointerType==='touch'||mq.matches)return;const r=display.getBoundingClientRect();signal.style.setProperty('--mx',`${(e.clientX-r.left)/r.width*100}%`);signal.style.setProperty('--my',`${(e.clientY-r.top)/r.height*100}%`)}
    function onExit(){signal.style.setProperty('--mx','50%');signal.style.setProperty('--my','50%')}
    display.addEventListener('pointerdown',pointerDown,{passive:true});
    display.addEventListener('pointerup',pointerUp,{passive:true});
    display.addEventListener('touchstart',touchStart,{passive:true});
    display.addEventListener('touchend',touchEnd,{passive:true});
    display.addEventListener('pointermove',onMove,{passive:true});
    display.addEventListener('pointerleave',onExit,{passive:true});
    root.addEventListener('keydown',onKey);
    paint(0);
    teardown=()=>{
      prev.removeEventListener('click',onPrev);next.removeEventListener('click',onNext);
      steps.forEach((node,i)=>node.removeEventListener('click',stepCallbacks[i]));
      display.removeEventListener('pointerdown',pointerDown);display.removeEventListener('pointerup',pointerUp);
      display.removeEventListener('touchstart',touchStart);display.removeEventListener('touchend',touchEnd);
      display.removeEventListener('pointermove',onMove);display.removeEventListener('pointerleave',onExit);
      root.removeEventListener('keydown',onKey);
    };
  }
  window.initGallery=initGallery;
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initGallery);
  else initGallery();
})();
