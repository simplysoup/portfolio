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
    document.querySelectorAll('[data-nav]').forEach(link => {
      const href = link.getAttribute('href');
      if (!href.startsWith('#')) return;
      const section = document.getElementById(link.dataset.nav); if (!section) return;
      const previous = navObservers.get(link); if (previous?.section === section) return;
      previous?.observer.disconnect();
      const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { document.querySelectorAll('[data-nav]').forEach(a => a.removeAttribute('aria-current')); link.setAttribute('aria-current', 'true'); } else link.removeAttribute('aria-current'); }), {rootMargin: '-35% 0px -64% 0px'});
      observer.observe(section); navObservers.set(link, {section, observer});
    });
  }
  window.initSite = initSite; initSite(); setInterval(() => document.querySelectorAll('[data-clock]').forEach(el => { el.textContent = new Intl.DateTimeFormat('en-GB', {timeZone:'America/Toronto', hour:'2-digit', minute:'2-digit', hourCycle:'h23'}).format(new Date()); }), 15000);
})();
