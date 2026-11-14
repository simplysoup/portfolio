# Phase 2 — global shell, hero, marquee (visual). Implementer: GPT-6.1 Terra.

Repo: /home/soup/Projects/portfolio, branch `redesign-v14`. Read AGENTS.md, then docs/redesign-v14/SPEC.md completely (it is the source of truth — class strings in it are to be used verbatim). Phase 1 already added Tailwind (`tailwind.config.js`, `assets/src/app.css`, `scripts/tailwind.py`, fonts, `content/profile.yaml`, `profile` in template context). Do NOT commit.

## Scope (implement exactly)
1. `templates/base.html` rewritten per SPEC §3:
   - `<head>`: keep existing meta/OG/canonical logic; `<html lang="en" class="no-js">` + inline head script `document.documentElement.classList.replace('no-js','js')`; `<link rel="preload" as="font" type="font/woff2" crossorigin>` for BigShouldersDisplay and Geist; `<link rel="stylesheet" href="{{base}}assets/app.css">`; `theme-color` `#050505`.
   - TEMPORARY legacy bridge: on non-home pages only (`nav != 'home'`) ALSO link the old `styles.css` after app.css and load `site.js`, so sub-pages keep working until phase 5. The home page must not load styles.css/world.css/scrollchapters.css/world.js/scrollchapters.js.
   - Scripts (defer, end order): `assets/js/art.js`, `assets/js/main.js`.
   - Body: `class="bg-ink text-paper"`; skip link (`sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] btn-solid`); frame §3.1; header §3.2; mobile menu §3.3; `<main id="main">`; footer §3.4 (on every page — replaces the old footer).
   - Header nav hrefs: on home `#about`, `#work`, `#research`, `#contact`; elsewhere `{{base}}#about` etc. `aria-current` handled by JS on home only.
2. `templates/index.html` → `{% include 'partials/hero.html' %}` and `{% include 'partials/marquee.html' %}` only. Delete the old directory/folio/room markup from index.html (it remains in git history). Add empty placeholder anchors `<div id="about"></div><div id="work"></div><div id="research"></div><div id="contact"></div>` at the end so nav links resolve (later phases replace them).
3. `templates/partials/hero.html` per SPEC §4.1 and `templates/partials/marquee.html` per §4.2. Copy from `profile.hero.intro`.
4. `assets/js/main.js` (vanilla, no deps, IIFE, `'use strict'`) implementing SPEC §7 + header/menu behaviour from §3: `data-split`, `data-reveal`, `data-fit` (fit text to parent's content-box width after `document.fonts.ready`, ResizeObserver, debounce 100ms; must give the hero `NICHOLAS` wordmark a rendered width within 96–100% of the shell inner width), `data-clock` (America/Toronto `HH:MM` 24h via Intl, every 15s), mobile menu (aria-expanded, hidden+inert, Esc, focus management, close on link click), active nav (IntersectionObserver per §3.2; only the sections that exist), and `window.initSite()` idempotent (guard with data attributes).
5. `assets/js/art.js` — the registry scaffold per SPEC §5.1 (`window.initArt(root)`, common DPR/resize/visibility/reduced-motion/PRNG machinery) and the **`sphere`** art fully implemented. Unknown keys are ignored. Later phases add more arts into the same registry, so structure it as `const ARTS = { sphere: { setup(ctx, w, h, opts), frame(ctx, w, h, t, state) } }` or similar clean pattern.
   The sphere must read as a dot-matrix / halftone globe: lit hemisphere bright squares, terminator falling off to nothing, a visible crater/dent rotating through, sparse dots outside. At 1440×900 its diameter is ~min(52vh,540px).

## Verification you must do
- `uv run python scripts/build.py && uv run python scripts/build_preview.py` succeed.
- Serve `dist` (`uv run python -m http.server 8765 --directory dist` in background; kill it after) and with Playwright (use `tests/_browser.py` launch helper; `uv run --with playwright --with pillow python …`) screenshot `/` at 390×844, 768×1024, 1440×900, 1920×1080 (first viewport + one scroll down) into `screenshots/v14/phase2/`. LOOK at them and fix issues before reporting. Check: no horizontal overflow (`document.documentElement.scrollWidth <= innerWidth`) at 320, 390, 768, 1024, 1440, 1920; no console errors; hero fits in 100svh at 1440×900 with no overlaps between headline / card / sphere; wordmark fit 96–100%; menu opens/closes with keyboard at 390; reduced-motion emulation shows static sphere and no marquee animation; the offline `OPEN_PORTFOLIO.html` home renders the same hero (fonts inlined).
- Open one sub-page (`/work/evaluated-rag/`) and confirm it is still readable (legacy bridge) — cosmetic imperfections there are acceptable for now, broken layout is not.

## Output
Report: files changed, screenshot paths, measured numbers (wordmark fit ratio per viewport, overflow results), anything in the spec you could not satisfy and exactly why. Stop and report rather than redesigning if the spec seems wrong.
