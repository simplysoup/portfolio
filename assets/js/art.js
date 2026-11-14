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
        const angle = t * .14 + state.pointer, lx = Math.sin(angle - .65), lz = Math.cos(angle - .65);
        const craterX = Math.sin(t * .14 - .7) * Math.sqrt(1 - .25*.25), craterZ = Math.cos(t * .14 - .7) * Math.sqrt(1 - .25*.25), craterY = -.25;
        for (let y = cy-r; y <= cy+r; y += cell) for (let x = cx-r; x <= cx+r; x += cell) {
          const nx = (x-cx)/r, ny = (y-cy)/r, d = nx*nx + ny*ny; if (d >= 1) continue;
          const nz = Math.sqrt(1-d), dist = Math.hypot(nx-craterX, ny-craterY, nz-craterZ);
          const lum = Math.max(0, nx*lx - ny*.35 + nz*lz - .35*Math.exp(-(dist*dist)/(2*.18*.18)));
          if (lum <= .015) continue;
          const size = cell*.92*Math.pow(Math.min(lum, 1), .8); ctx.globalAlpha = .35 + .65*Math.min(lum, 1); ctx.fillRect(x-size/2, y-size/2, size, size);
        }
        ctx.globalAlpha = 1;
      }
    }
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
      if (matchMedia('(pointer: fine)').matches) { canvas.parentElement.parentElement.addEventListener('pointermove', e => { if (state) state.target = ((e.clientX-canvas.getBoundingClientRect().left)/w-.5)*.5; }); canvas.parentElement.parentElement.addEventListener('pointerleave', () => { if (state) state.target = 0; }); }
    });
  }
  window.initArt = initArt; initArt();
})();
