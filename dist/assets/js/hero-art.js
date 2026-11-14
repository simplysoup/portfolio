/* Generative hero field: an original animated torus in a moving point lattice. */
(() => {
  'use strict';
  let activeCleanup = null;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const coarse = matchMedia('(pointer: coarse)');
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function initHeroArt(root = document) {
    const canvas = root.querySelector('[data-hero-art]');
    if (!canvas) { activeCleanup?.(); return; }
    if (canvas.dataset.heroArtReady) return;
    activeCleanup?.(); canvas.dataset.heroArtReady = 'true';
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const hero = canvas.closest('.hero'), container = canvas.parentElement;
    const abort = new AbortController();
    let visible = false, frame = 0, disposed = false, w = 0, h = 0, last = 0;
    let x = 0, y = 0, tx = 0, ty = 0;
    let pointerX = 0, pointerY = 0, active = 0, targetActive = 0, energy = 0;
    const stars = Array.from({length: 95}, (_, i) => {
      const rand = n => { const v = Math.sin(n * 127.1 + 71.3) * 43758.5453; return v - Math.floor(v); };
      return [rand(i * 3), rand(i * 3 + 1), rand(i * 3 + 2)];
    });
    const resize = new ResizeObserver(entries => {
      const box = entries[0].contentRect; w = box.width; h = box.height;
      if (!w || !h) return;
      const dpr = Math.min(devicePixelRatio || 1, coarse.matches ? 1 : 1.5);
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); request();
    });
    const intersection = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (visible) request(); else cancel(); });
    function cancel() { if (frame) cancelAnimationFrame(frame); frame = 0; }
    function cleanup() {
      if (disposed) return; disposed = true; cancel(); abort.abort(); resize.disconnect(); intersection.disconnect();
      container.classList.remove('is-rendered'); if (activeCleanup === cleanup) activeCleanup = null;
    }
    activeCleanup = cleanup;
    function request() { if (!disposed && visible && !document.hidden && !frame && w && h) frame = requestAnimationFrame(draw); }
    function draw(now) {
      frame = 0;
      if (disposed || !canvas.isConnected) { cleanup(); return; }
      if (coarse.matches && !reduced.matches && now - last < 32) { request(); return; }
      last = now;
      const elapsed = reduced.matches ? 2 : Math.max(0, (now - (window.heroEntranceStart || now)) / 1000);
      const intro = reduced.matches ? 1 : 1 - Math.pow(1 - Math.min(1, elapsed / 1.45), 4);
      const scroll = clamp(-hero.getBoundingClientRect().top / Math.max(1, hero.offsetHeight), 0, 1);
      x += (tx - x) * .045; y += (ty - y) * .045;
      active += (targetActive - active) * .08; energy *= .94;
      const cx = w * .5, cy = h * (.50 - scroll * .10), scale = Math.min(w * .42, h * .42) * (.78 + intro * .22) * (1 - scroll * .18);
      const fade = intro * (1 - scroll * .65);
      hero.style.setProperty('--ambient-x', `${(Math.sin(elapsed * .11) * 5 + x * 8).toFixed(1)}px`);
      hero.style.setProperty('--ambient-y', `${(Math.cos(elapsed * .11) * 5 + y * 8).toFixed(1)}px`);
      ctx.clearRect(0, 0, w, h);
      // The outer field moves with the same rotation and scroll as the form.
      ctx.strokeStyle = 'rgb(242,242,238)'; ctx.lineWidth = .7;
      for (let ring = 0; ring < 3; ring++) {
        ctx.globalAlpha = fade * (.025 + ring * .008); ctx.beginPath();
        ctx.ellipse(cx, cy, scale * (1.15 + ring * .22), scale * (.38 + ring * .1), -.25 + Math.sin(elapsed * .09) * .12, 0, Math.PI * 2); ctx.stroke();
      }
      ctx.fillStyle = 'rgb(242,242,238)';
      stars.forEach(([sx, sy, a]) => {
        ctx.globalAlpha = fade * (.035 + a * .12);
        const drift = reduced.matches ? 0 : Math.sin(elapsed * .12 + a * 6) * 4;
        ctx.fillRect(sx * w + drift, sy * h - scroll * 18, a > .85 ? 1.5 : 1, a > .85 ? 1.5 : 1);
      });
      const turn = elapsed * .11 + x * .7, ct = Math.cos(turn), st = Math.sin(turn);
      const tilt = .72 + y * .35, ca = Math.cos(tilt), sa = Math.sin(tilt);
      const points = [];
      const rings = coarse.matches ? 112 : 144, segments = coarse.matches ? 36 : 44;
      for (let i = 0; i < rings; i++) {
        const u = i * Math.PI * 2 / rings;
        for (let j = 0; j < segments; j++) {
          const v = j * Math.PI * 2 / segments;
          const wave = .075 * Math.sin(5 * u + 2 * v - elapsed * .55) + .035 * Math.sin(9 * u - 3 * v + elapsed * .3);
          const tube = .37 + wave, radius = .72 + tube * Math.cos(v);
          const px = radius * Math.cos(u), py = tube * Math.sin(v), pz = radius * Math.sin(u);
          const rx = px * ct - pz * st, rz = px * st + pz * ct;
          const ry = py * ca - rz * sa, depth = py * sa + rz * ca;
          let screenX = cx + rx * scale, screenY = cy + ry * scale;
          // A soft, local lens follows the pointer; movement sends a decaying ripple
          // through the original point surface without replacing its visual language.
          if (active > .001 && scale > 0) {
            const dx = (screenX - pointerX) / scale, dy = (screenY - pointerY) / scale;
            const distance = Math.hypot(dx, dy);
            const influence = Math.exp(-distance * distance * 3) * active;
            const push = influence * (.22 + energy * .28) * scale;
            screenX += dx * push; screenY += dy * push;
            screenY += influence * energy * scale * .12 * Math.sin(distance * 12 - elapsed * 7);
          }
          points.push([screenX, screenY, depth, i, j]);
        }
      }
      points.sort((a, b) => a[2] - b[2]);
      points.forEach(([px, py, depth, i, j]) => {
        const light = .5 + .5 * Math.sin(i * .105 + j * .14 - elapsed * .38);
        const alpha = clamp(.28 + depth * .30 + light * .16, .12, .9) * fade;
        const size = clamp(scale * .009 * (1 + depth * .25), .8, 2.1);
        ctx.globalAlpha = alpha * ((i + j) % 5 === 0 ? .6 : 1);
        ctx.fillRect(px - size / 2, py - size / 2, size, size);
      });
      ctx.globalAlpha = 1;
      container.classList.add('is-rendered');
      if (!reduced.matches) request();
    }
    const opts = {signal: abort.signal, passive: true};
    hero.addEventListener('pointermove', e => {
      if (reduced.matches || e.pointerType === 'touch') return;
      const rect = hero.getBoundingClientRect(), artRect = canvas.getBoundingClientRect();
      tx = clamp((e.clientX - rect.left) / rect.width - .5, -.5, .5);
      ty = clamp((e.clientY - rect.top) / rect.height - .5, -.5, .5);
      const nextX = e.clientX - artRect.left, nextY = e.clientY - artRect.top;
      if (targetActive) energy = clamp(energy + Math.hypot(nextX - pointerX, nextY - pointerY) / Math.max(w, h) * 2, 0, 1);
      pointerX = nextX; pointerY = nextY; targetActive = 1;
    }, opts);
    hero.addEventListener('pointerleave', () => { tx = 0; ty = 0; targetActive = 0; }, opts);
    document.addEventListener('visibilitychange', () => { if (document.hidden) cancel(); else request(); }, opts);
    reduced.addEventListener('change', () => {
      if (reduced.matches) { x = y = tx = ty = active = targetActive = energy = 0; }
      cancel(); request();
    }, {signal: abort.signal});
    resize.observe(canvas); intersection.observe(canvas);
  }
  window.initHeroArt = initHeroArt;
})();
