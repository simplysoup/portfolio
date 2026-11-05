/* Original interactive filament field. Pure Canvas2D, progressive enhancement. */
(() => {
'use strict';
function initializeField() {
  const hero = document.querySelector('[data-hero-scene]');
  const canvas = hero?.querySelector('[data-field-study]');
  if (!canvas || canvas.dataset.ready === '1') return;
  const plate=canvas.parentElement;
  const ctx=canvas.getContext('2d', { alpha:true });
  if (!ctx) return;
  canvas.dataset.ready = '1';
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pointer={ x:.5,y:.5,targetX:.5,targetY:.5,active:false };
  let w=0,h=0,dpr=1,raf=0,frame=0,visible=true,disposed=false;
  const TAU=Math.PI*2;
  function resize() {
    const b=plate.getBoundingClientRect();
    w=Math.max(1,b.width);h=Math.max(1,b.height);
    dpr=Math.min(window.devicePixelRatio||1,1.75);
    canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    render(performance.now());
  }
  function render(t) {
    if (!w || !h) return;
    const scale=Math.min(w,h);const time=reduced?0:t*.001;
    if(!reduced){pointer.x+=(pointer.targetX-pointer.x)*.075;pointer.y+=(pointer.targetY-pointer.y)*.075;}
    const cx=w*.53,cy=h*.51;
    ctx.clearRect(0,0,w,h);
    // A set of deformed, closely spaced ribbons. The changing offset is intentionally
    // subtle; the pointer introduces a local distortion of the existing structure.
    const total=124;
    const mx=pointer.x*w, my=pointer.y*h;
    for(let k=total-1;k>=0;k--){
      const p=k/(total-1);
      const radius=(.075 + .385*p)*scale;
      const lineAlpha=.08 + .55*(1-p) + .08*Math.sin(p*9);
      const useSignal=k%13===0;
      const useBlue=k%7===0;
      const alpha=useSignal?Math.min(1,lineAlpha*1.35):useBlue?lineAlpha*.8:lineAlpha*.75;
      ctx.lineWidth=useSignal?Math.max(.9,1.35*scale/650):Math.max(.55,.8*scale/650);
      ctx.strokeStyle=useSignal?`rgba(217,239,139,${alpha})`:useBlue?`rgba(126,157,234,${alpha})`:`rgba(215,229,223,${alpha})`;
      ctx.beginPath();
      for(let j=0;j<=240;j++){
        const a=j/240*TAU;
        const ripple=(Math.sin(a*3.0+p*10-time*.36)*.043 + Math.cos(a*6.0-p*8+time*.22)*.016 + Math.sin(a*9.0+p*13)*.008)*scale*(.25+.75*p);
        const r=radius+ripple;
        let x=cx+Math.cos(a)*r*(1.11+.11*Math.sin(p*7+time*.11)) + Math.sin(a*2.8+p*6)*scale*.019;
        let y=cy+Math.sin(a)*r*(.92-.12*Math.sin(p*8+time*.1)) + Math.cos(a*2+p*8)*scale*.028;
        if(pointer.active && !reduced){
          const dx=x-mx,dy=y-my,dist2=dx*dx+dy*dy;
          const falloff=Math.exp(-dist2/(2*(scale*.18)**2));
          x+=dx*falloff*.20;
          y+=dy*falloff*.20;
        }
        if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
      }
      ctx.closePath();ctx.stroke();
    }
    // Small technical registration marks, not an invented data chart.
    ctx.globalAlpha=.55;ctx.strokeStyle='#9BAEB0';ctx.lineWidth=.6;
    for(const [x,y] of [[w*.06,h*.09],[w*.94,h*.09],[w*.06,h*.91],[w*.94,h*.91]]){
      ctx.beginPath();ctx.moveTo(x-7,y);ctx.lineTo(x+7,y);ctx.moveTo(x,y-7);ctx.lineTo(x,y+7);ctx.stroke();
    }
    ctx.globalAlpha=1;
    canvas.dataset.rendered=String(++frame);
  }
  function tick(t){raf=0;if(disposed||!visible)return;render(t);if(!reduced)raf=requestAnimationFrame(tick);}
  function start(){if(!raf && visible && !reduced)raf=requestAnimationFrame(tick);}
  hero.addEventListener('pointermove',e=>{
    if(reduced)return;
    const b=plate.getBoundingClientRect();
    pointer.targetX=(e.clientX-b.left)/Math.max(1,b.width);
    pointer.targetY=(e.clientY-b.top)/Math.max(1,b.height);
    pointer.active=true;
    canvas.dataset.pointerActive='true';
    start();
  },{passive:true});
  hero.addEventListener('pointerleave',()=>{
    pointer.active=false;canvas.dataset.pointerActive='false';
  },{passive:true});
  if('ResizeObserver' in window)new ResizeObserver(resize).observe(plate);
  else window.addEventListener('resize',resize,{passive:true});
  if('IntersectionObserver' in window){
    new IntersectionObserver(entries=>{
      visible=entries[0].isIntersecting;
      if(visible)start();
      else if(raf){cancelAnimationFrame(raf);raf=0;}
    },{threshold:.01}).observe(plate);
  }
  resize();start();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initializeField);
else initializeField();
window.initializeField=initializeField;
})();
