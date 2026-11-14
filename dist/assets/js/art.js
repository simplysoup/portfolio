(() => {
  'use strict';
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const mulberry32 = seed => () => { let t = seed += 0x6D2B79F5; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const ARTS = {
    sphere: {
      setup(ctx, w, h) {
        const random = mulberry32(104); const dots = [];
        for (let y = 6; y < h; y += 12) for (let x = 6; x < w; x += 12) if (random() < 0.15) dots.push([x, y]);
        return {dots, pointer: 0, target: 0};
      },
      frame(ctx, w, h, t, state) {
        const r = Math.min(w, h) * 0.46, cx = w / 2, cy = h / 2, cell = Math.min(w, h) < 320 ? 5 : 6;
        ctx.clearRect(0, 0, w, h); ctx.fillStyle = 'rgb(242,242,238)'; ctx.globalAlpha = .1;
        state.dots.forEach(([x, y]) => { if (Math.hypot(x-cx, y-cy) > r) ctx.fillRect(x, y, 2, 2); });
        state.pointer += (state.target - state.pointer) * .06;
        const angle = t * .14, lightLength = Math.hypot(-.55, -.45, .70);
        const baseLx = -.55/lightLength, ly = -.45/lightLength, baseLz = .70/lightLength;
        const cosNudge = Math.cos(state.pointer), sinNudge = Math.sin(state.pointer);
        const lx = baseLx*cosNudge + baseLz*sinNudge, lz = -baseLx*sinNudge + baseLz*cosNudge;
        const craterX = Math.sin(angle - .7) * Math.sqrt(1 - .25*.25), craterZ = Math.cos(angle - .7) * Math.sqrt(1 - .25*.25), craterY = -.25;
        for (let y = cy-r; y <= cy+r; y += cell) for (let x = cx-r; x <= cx+r; x += cell) {
          const nx = (x-cx)/r, ny = (y-cy)/r, d = nx*nx + ny*ny; if (d >= 1) continue;
          const nz = Math.sqrt(1-d), dist = Math.hypot(nx-craterX, ny-craterY, nz-craterZ);
          const crater = .35*Math.exp(-(dist*dist)/(2*.18*.18));
          const lum = Math.max(0, Math.min(1, .04 + Math.max(0, nx*lx + ny*ly + nz*lz) - crater));
          if (lum <= .015) continue;
          const size = cell*.92*Math.pow(lum, .8); ctx.globalAlpha = .35 + .65*lum; ctx.fillRect(x-size/2, y-size/2, size, size);
        }
        ctx.globalAlpha = 1;
      }
    }
  };
  ARTS.burst = {
    setup() { const random = mulberry32(201); return Array.from({length:260}, (_, i) => ({a:i*Math.PI*2/260, length:.3+random()*1.1, alpha:.08+random()*.42, width:.6+random()*.4, phase:random()*6.28})); },
    frame(ctx,w,h,t,lines) { ctx.clearRect(0,0,w,h); const x=w*.62,y=h*.55,diag=Math.hypot(w,h); lines.forEach(line => { const a=line.a+t*.01, length=line.length*diag*(.96+.04*Math.sin(t*.3+line.phase)); ctx.strokeStyle=`rgba(242,242,238,${line.alpha})`; ctx.lineWidth=line.width; ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(x+Math.cos(a)*length,y+Math.sin(a)*length); ctx.stroke(); }); ctx.fillStyle='rgb(242,242,238)'; ctx.beginPath(); ctx.arc(x,y,4.5,0,Math.PI*2); ctx.fill(); ctx.lineWidth=2; ctx.strokeStyle='rgba(242,242,238,.6)'; ctx.beginPath(); ctx.arc(x,y,10,0,Math.PI*2); ctx.stroke(); }
  };
  ARTS.ridges = {
    setup() { return {}; },
    frame(ctx,w,h,t) { ctx.clearRect(0,0,w,h); for(let row=0;row<34;row++) { const base=h*.1+row*h/40, amplitude=h*.13*Math.sin(Math.PI*row/34); ctx.beginPath(); for(let x=0;x<=w+3;x+=3) { const gaussian=(center,width) => Math.exp(-((x/w-center)**2)/(2*width*width)); const offset=amplitude*(gaussian(.37+.015*Math.sin(t*.15),.09)+.75*gaussian(.53,.065)+.55*gaussian(.67,.1)); const y=Math.round(base-offset)+.5; if(!x) ctx.moveTo(x,y); else ctx.lineTo(x,y); } ctx.lineTo(w,h); ctx.lineTo(0,h); ctx.closePath(); ctx.fillStyle='rgb(11,11,11)'; ctx.fill(); ctx.strokeStyle='rgba(242,242,238,.85)'; ctx.lineWidth=1; ctx.stroke(); } }
  };
  ARTS.halftone = {
    setup() { return {}; },
    frame(ctx,w,h,t) { ctx.clearRect(0,0,w,h); ctx.fillStyle='rgba(242,242,238,.7)'; for(let y=5;y<h;y+=10) for(let x=5;x<w;x+=10) { const size=1+7*(.5+.5*Math.sin(x*.035+t)*Math.cos(y*.03-t*.6)); ctx.fillRect(x-size/2,y-size/2,size,size); } ctx.setLineDash([5,6]); ctx.strokeStyle='rgba(242,242,238,.9)'; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(w*.2,h*.65); ctx.lineTo(w*.5,h*.32); ctx.lineTo(w*.8,h*.55); ctx.stroke(); ctx.setLineDash([]); [[.2,.65],[.5,.32],[.8,.55]].forEach(([x,y])=>{ctx.beginPath();ctx.arc(w*x,h*y,5,0,Math.PI*2);ctx.fillStyle='rgb(242,242,238)';ctx.fill();}); }
  };
  ARTS.trend = {
    setup(ctx,w,h,data) { const random=mulberry32(204); return {noise:Array.from({length:220},()=>random()-.5), variant:data.variant}; },
    frame(ctx,w,h,t,state) { ctx.clearRect(0,0,w,h); const left=w*.1, right=w*.91, top=16, bottom=h-36, width=right-left, height=bottom-top; const value=x => x<.33?.72-x*.45:x<.67?.57-(x-.33)*.65:.35+(x-.67)*.45; const point=x=>bottom-value(x)*height; ctx.fillStyle='rgba(242,242,238,.08)'; ctx.beginPath(); for(let i=0;i<=100;i++){let x=i/100;ctx.lineTo(left+x*width,point(x)-height*.07);} for(let i=100;i>=0;i--){let x=i/100;ctx.lineTo(left+x*width,point(x)+height*.07);} ctx.closePath();ctx.fill(); ctx.fillStyle='rgba(242,242,238,.7)'; state.noise.forEach((n,i)=>{const x=i/219;ctx.beginPath();ctx.arc(left+x*width,point(x)+n*height*.12,1.2,0,Math.PI*2);ctx.fill();}); ctx.strokeStyle='rgba(242,242,238,.95)';ctx.lineWidth=1.5;ctx.beginPath(); [0,.33,.67,1].forEach((x,i)=>{if(!i)ctx.moveTo(left+x*width,point(x));else ctx.lineTo(left+x*width,point(x));});ctx.stroke(); ctx.setLineDash([4,5]);ctx.strokeStyle='rgba(242,242,238,.4)';ctx.lineWidth=1; [.33,.67].forEach((x,i)=>{const px=Math.round(left+x*width)+.5;ctx.beginPath();ctx.moveTo(px,top);ctx.lineTo(px,bottom);ctx.stroke();ctx.fillStyle='rgba(242,242,238,.7)';ctx.font='11px Geist Mono, monospace';ctx.fillText(i?'t₂':'t₁',px+4,bottom-4);});ctx.setLineDash([]); if(state.variant==='segments') ['A','B','C'].forEach((v,i)=>ctx.fillText(v,left+width*(i+.5)/3,top+12)); const scan=Math.round(left+width*((t%8)/8))+.5;ctx.strokeStyle='rgba(242,242,238,.45)';ctx.beginPath();ctx.moveTo(scan,top);ctx.lineTo(scan,bottom);ctx.stroke(); }
  };
  ARTS.pianoroll = {
    setup() { return Array.from({length:40},(_,i)=>({beat:i*.72+(i%6===3?.18:0),row:[3,7,10,8,5,12,4,9,6,11,3,14,7,5,2,10][i%16],duration:[.44,1.12,.72,.57,1.4,.85][i%6],strength:.62+(i%5)*.085})); },
    frame(ctx,w,h,t,events) { ctx.clearRect(0,0,w,h); const left=30, top=36, bottom=22, rows=16, rowH=(h-top-bottom)/rows, beat=Math.max(35,Math.min(86,w*.1)), cycle=40*.72*beat, scroll=t*40; ctx.strokeStyle='rgba(242,242,238,.12)';ctx.lineWidth=1;for(let r=0;r<=rows;r++){const y=Math.round(top+r*rowH)+.5;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w,y);ctx.stroke();} ctx.save();ctx.beginPath();ctx.rect(left,top,w-left,h-top-bottom);ctx.clip();const firstBar=Math.floor(scroll/(4*beat))-1;for(let b=firstBar;b<firstBar+Math.ceil(w/(4*beat))+3;b++){let x=Math.round(left+b*4*beat-scroll)+.5;ctx.beginPath();ctx.moveTo(x,top);ctx.lineTo(x,h-bottom);ctx.stroke();} const start=Math.floor(scroll/cycle)-1;for(let c=start;c<=Math.floor((scroll+w)/cycle)+1;c++)for(const n of events){const x=left+c*cycle+n.beat*beat-scroll,width=n.duration*beat,y=top+n.row*rowH+rowH*.22;if(x+width<left||x>w)continue;ctx.fillStyle=`rgba(242,242,238,${n.strength})`;ctx.beginPath();ctx.roundRect(x,y,width,Math.max(2,rowH*.56),3);ctx.fill();}ctx.restore(); for(let r=0;r<rows;r++){let y=top+r*rowH;ctx.strokeStyle='rgba(242,242,238,.35)';ctx.strokeRect(.5,Math.round(y)+.5,left-1,Math.ceil(rowH)); if([1,3,6,8,10].includes(r%12)){ctx.fillStyle='rgba(242,242,238,.35)';ctx.fillRect(0,y,left*.6,rowH*.7);}} const head=Math.round(w*.62)+.5;ctx.strokeStyle='rgba(242,242,238,.9)';ctx.beginPath();ctx.moveTo(head,top);ctx.lineTo(head,h-bottom);ctx.stroke(); }
  };
  function initArt(root = document) {
    const canvases = [...root.querySelectorAll('[data-art]')]; if (root.matches?.('[data-art]')) canvases.unshift(root);
    canvases.forEach(canvas => {
      const art = ARTS[canvas.dataset.art]; if (!art || canvas.dataset.artReady) return; canvas.dataset.artReady = 'true';
      const ctx = canvas.getContext('2d'); let w = 0, h = 0, state, visible = false, raf = 0;
      const draw = time => { raf = 0; if (!state) return; art.frame(ctx, w, h, motion.matches ? .6 : time/1000, state); if (!motion.matches && visible && !document.hidden) raf = requestAnimationFrame(draw); };
      const update = () => { if (raf) cancelAnimationFrame(raf); raf = 0; if (state && (motion.matches || (visible && !document.hidden))) draw(performance.now()); };
      new ResizeObserver(entries => { const box = entries[0].contentRect; w = box.width; h = box.height; if (!w || !h) return; const dpr = Math.min(devicePixelRatio || 1, 2); canvas.width = Math.round(w*dpr); canvas.height = Math.round(h*dpr); ctx.setTransform(dpr,0,0,dpr,0,0); state = art.setup(ctx,w,h,canvas.dataset); update(); }).observe(canvas);
      new IntersectionObserver(entries => { visible = entries[0].isIntersecting; update(); }).observe(canvas);
      document.addEventListener('visibilitychange', update); motion.addEventListener('change', update);
      if (canvas.dataset.art === 'sphere' && matchMedia('(pointer: fine)').matches) { canvas.parentElement.parentElement.addEventListener('pointermove', e => { if (state) state.target = ((e.clientX-canvas.getBoundingClientRect().left)/w-.5)*.5; }); canvas.parentElement.parentElement.addEventListener('pointerleave', () => { if (state) state.target = 0; }); }
    });
  }
  window.initArt = initArt; initArt();
})();
