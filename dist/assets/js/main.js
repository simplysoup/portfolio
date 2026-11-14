(() => {
  'use strict';
  const revealObserver = new IntersectionObserver(entries => entries.forEach(entry => {
    if (entry.isIntersecting) { entry.target.classList.add('is-in'); revealObserver.unobserve(entry.target); }
  }), { threshold: 0.2 });
  const fit = el => {
    const parent = el.parentElement;
    const width = parent.clientWidth - parseFloat(getComputedStyle(parent).paddingLeft) - parseFloat(getComputedStyle(parent).paddingRight);
    if (!width) return;
    el.style.fontSize = '100px';
    const range = document.createRange(); range.selectNodeContents(el);
    const measured = range.getBoundingClientRect().width;
    if (measured) {
      const size = 100 * width / measured;
      el.style.fontSize = `${size}px`;
      if (parent.hasAttribute('data-fit-crop')) parent.style.height = `${size * 0.8}px`;
    }
  };
  let fitTimer;
  const fitObserver = new ResizeObserver(entries => {
    clearTimeout(fitTimer);
    fitTimer = setTimeout(() => entries.forEach(entry => entry.target.querySelectorAll('[data-fit]').forEach(fit)), 100);
  });
  function split(el) {
    el.setAttribute('aria-label', el.textContent.trim().replace(/\s+/g, ' '));
    let index = 0;
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      const fragment = document.createDocumentFragment();
      node.textContent.split(/(\s+)/).filter(Boolean).forEach(part => {
        if (/^\s+$/.test(part)) { fragment.append(part); return; }
        const outer = document.createElement('span'); outer.className = 'inline-block overflow-hidden pb-[0.06em] align-top'; outer.setAttribute('aria-hidden', 'true');
        const inner = document.createElement('span'); inner.className = 'split-word inline-block translate-y-[105%] transition-transform duration-[900ms] ease-out-expo'; inner.style.transitionDelay = `${index++ * 45}ms`; inner.textContent = part;
        outer.append(inner); fragment.append(outer);
      }); node.replaceWith(fragment);
    });
  }
  const navObservers = new WeakMap();
  // A single rail controller follows whichever home DOM the preview router installed.
  const initRail = (() => {
    const wide = matchMedia('(min-width: 1024px)'), reduced = matchMedia('(prefers-reduced-motion: reduce)');
    let rail, wrapper, viewport, track, cards, progress, fill, counter, frame = 0;
    const update = () => {
      frame = 0;
      if (!rail || !document.documentElement.classList.contains('rail-on')) return;
      const distance = Math.max(0, track.scrollWidth - viewport.clientWidth);
      const range = wrapper.offsetHeight - viewport.offsetHeight - 56;
      const p = Math.max(0, Math.min(1, (56 - wrapper.getBoundingClientRect().top) / range));
      track.style.transform = `translate3d(${-p * distance}px,0,0)`;
      fill.style.transform = `scaleX(${p})`;
      counter.textContent = `${String(Math.min(cards.length, Math.floor(p * cards.length) + 1)).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
    };
    const request = () => { if (!frame) frame = requestAnimationFrame(update); };
    const configure = () => {
      const on = !!rail && wide.matches && !reduced.matches;
      document.documentElement.classList.toggle('rail-on', on);
      if (!rail) return;
      wrapper.style.height = on ? `calc(${cards.length} * 70vh + 100svh)` : '';
      track.style.transform = ''; progress.hidden = !on;
      if (on) request();
    };
    addEventListener('scroll', request, {passive:true});
    addEventListener('resize', () => { configure(); request(); }, {passive:true});
    wide.addEventListener('change', configure); reduced.addEventListener('change', configure);
    return () => {
      const next = document.querySelector('[data-rail]');
      if (next === rail) { configure(); return; }
      rail = next;
      if (!rail) { configure(); return; }
      wrapper = rail.querySelector('[data-rail-wrapper]'); viewport = rail.querySelector('[data-rail-viewport]'); track = rail.querySelector('[data-rail-track]');
      cards = [...rail.querySelectorAll('.rail-card')]; progress = rail.querySelector('[data-rail-progress]'); fill = rail.querySelector('[data-rail-fill]'); counter = rail.querySelector('[data-rail-count]');
      rail.addEventListener('focusin', event => {
        if (!document.documentElement.classList.contains('rail-on')) return;
        const card = event.target.closest('.rail-card'); if (!card) return;
        const rect = card.getBoundingClientRect(), visible = viewport.getBoundingClientRect();
        if (rect.left >= visible.left && rect.right <= visible.right) return;
        const distance = track.scrollWidth - viewport.clientWidth;
        const centre = card.offsetLeft + card.offsetWidth / 2 - viewport.clientWidth / 2;
        const p = Math.max(0, Math.min(1, centre / distance));
        window.scrollTo({top: window.scrollY + wrapper.getBoundingClientRect().top - 56 + p * (wrapper.offsetHeight - viewport.offsetHeight - 56), behavior: 'instant'});
      });
      configure();
    };
  })();
  function initSite() {
    document.querySelectorAll('[data-split], [data-reveal]').forEach(el => {
      if (el.dataset.siteRevealReady) return; el.dataset.siteRevealReady = 'true';
      if (el.hasAttribute('data-split')) split(el);
      revealObserver.observe(el);
    });
    document.querySelectorAll('[data-fit]').forEach(el => {
      if (el.dataset.fitReady) return; el.dataset.fitReady = 'true';
      fitObserver.observe(el.parentElement); document.fonts.ready.then(() => fit(el));
    });
    document.querySelectorAll('[data-clock]').forEach(el => { el.textContent = new Intl.DateTimeFormat('en-GB', {timeZone: 'America/Toronto', hour: '2-digit', minute: '2-digit', hourCycle: 'h23'}).format(new Date()); });
    const button = document.querySelector('[data-menu-toggle]'), menu = document.getElementById('site-menu');
    if (button && menu && !button.dataset.menuReady) {
      button.dataset.menuReady = 'true'; menu.inert = menu.hidden;
      const close = (restore = true) => { menu.hidden = true; menu.inert = true; button.setAttribute('aria-expanded', 'false'); button.textContent = 'Menu'; if (restore) button.focus(); };
      button.addEventListener('click', () => { if (!menu.hidden) close(); else { menu.hidden = false; menu.inert = false; button.setAttribute('aria-expanded', 'true'); button.textContent = 'Close'; menu.querySelector('a')?.focus(); } });
      menu.addEventListener('click', e => { if (e.target.closest('a')) close(); });
      document.addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) close(); });
    }
    document.querySelectorAll('[data-mailto]').forEach(form => {
      if (form.dataset.mailtoReady) return;
      form.dataset.mailtoReady = 'true';
      form.addEventListener('submit', event => {
        event.preventDefault();
        const fields = new FormData(form), name = fields.get('name'), email = fields.get('email'), message = fields.get('message');
        const mailto = `mailto:${form.dataset.email}?subject=${encodeURIComponent(`Hello from ${name}`)}&body=${encodeURIComponent(`${message}\n\n— ${name} (${email})`)}`;
        form.dataset.lastMailto = mailto;
        form.querySelector('[data-mailto-status]').hidden = false;
        location.href = mailto;
      });
    });
    initRail();
    document.querySelectorAll('[data-nav]').forEach(link => {
      const href = link.getAttribute('href');
      if (!href.startsWith('#')) return;
      const section = document.querySelector(`[data-chapter="${link.dataset.nav}"]`) || document.getElementById(link.dataset.nav); if (!section) return;
      const previous = navObservers.get(link); if (previous?.section === section) return;
      previous?.observer.disconnect();
      const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { document.querySelectorAll('[data-nav]').forEach(a => a.removeAttribute('aria-current')); link.setAttribute('aria-current', 'true'); } else link.removeAttribute('aria-current'); }), {rootMargin: '-35% 0px -64% 0px'});
      observer.observe(section); navObservers.set(link, {section, observer});
    });
  }
  window.initSite = initSite; initSite(); setInterval(() => document.querySelectorAll('[data-clock]').forEach(el => { el.textContent = new Intl.DateTimeFormat('en-GB', {timeZone:'America/Toronto', hour:'2-digit', minute:'2-digit', hourCycle:'h23'}).format(new Date()); }), 15000);
})();
