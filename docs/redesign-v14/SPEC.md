# v14 "Instrument" redesign — architecture & visual spec

Owner/architect: parent session. Implementers follow this document literally. If something here is
impossible or contradictory, STOP and report it rather than improvising a different design.

Reference for art direction: https://christendijoux.com/ (monochrome, condensed display type, mono labels,
hairline grid, dot-matrix canvas art, numbered chapters). We borrow the *language*, never its text, images,
code or logo. Everything below is original to Nicholas Bode.

---------------------------------------------------------------------------------------------------
## 0. Hard constraints

1. Static site: Python build (`scripts/build.py`, Jinja2, Markdown-It, PyYAML, BeautifulSoup). No JS framework,
   no npm. Tailwind CSS **v3.4.17 standalone CLI binary** is the only new tool (downloaded by `scripts/tailwind.py`).
2. Native scroll only. No scroll locking, no wheel capture, no `preventDefault` on wheel/touch. Sticky +
   scroll-progress transforms are allowed (same approach as the existing `scrollchapters.js`).
3. `prefers-reduced-motion: reduce` ⇒ no marquee animation, no canvas animation loops (render one static frame),
   no reveal transitions, horizontal work rail becomes a vertical list.
4. Everything works without JS: content visible, links work. JS-only hidden states are scoped under `html.js`.
5. Keyboard: visible focus everywhere (`focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-2 focus-visible:outline-paper`).
   Touch targets ≥ 40px tall.
6. Publication safety (see §9). No internal product names, client names, dataset sizes, deal values.
7. `dist/` and `OPEN_PORTFOLIO.html` are generated. Never hand-edit them.
8. Test viewports: 320×640, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080. No horizontal overflow at any.

---------------------------------------------------------------------------------------------------
## 1. File architecture (target)

```
tailwind.config.js                 Tailwind v3 config (tokens below)
assets/src/app.css                 Tailwind input: @tailwind + @layer base/components
assets/fonts/*.woff2               self-hosted: BigShouldersDisplay[wght].woff2, Geist[wght].woff2, GeistMono[wght].woff2 (latin subset)
assets/js/main.js                  header state, menu, clock, reveals, word-split, work rail, contact form, window.initSite()
assets/js/art.js                   canvas art registry: [data-art="sphere|burst|ridges|halftone|trend|pianoroll"], window.initArt()
assets/site.js                     (kept) article exhibits RAG/trend — restyled in phase 4
content/profile.yaml               ALL home-page data (§8). Templates loop over it; no copy hard-coded in templates except labels.
content/work/*.md                  case studies (6 total, §8.6)
content/research/*.md              thesis article
templates/base.html                frame, header, menu, footer, font preload, app.css, main.js, art.js
templates/partials/*.html          one partial per home section (hero, marquee, about, expertise, skills, experience,
                                   highlights, offclock, work, research, contact)
templates/index.html               includes the partials in order
scripts/tailwind.py                ensure pinned binary in .cache/, compile assets/src/app.css → dist/assets/app.css --minify
scripts/build.py                   loads profile.yaml into context `profile`; calls tailwind after copying assets
scripts/build_preview.py           inlines app.css (fonts as base64 data URIs), main.js, art.js, site.js; hash router
tests/verify_v14.py                Playwright checks (phase 5)
```
Old `styles.css`, `world.css`, `scrollchapters.css/js`, `world.js` are deleted in phase 5 once nothing references them.

---------------------------------------------------------------------------------------------------
## 2. Tokens — `tailwind.config.js` (exact)

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './assets/js/**/*.js', './assets/site.js', './content/**/*.yaml'],
  theme: {
    extend: {
      colors: {
        ink:   'rgb(5 5 5 / <alpha-value>)',        // page background
        stage: 'rgb(11 11 11 / <alpha-value>)',     // raised panels
        paper: 'rgb(242 242 238 / <alpha-value>)',  // text / foreground
        line:  'rgb(242 242 238 / 0.12)',           // hairlines
        'line-strong': 'rgb(242 242 238 / 0.28)',
        signal:'rgb(215 255 58 / <alpha-value>)',   // ONLY: live dots, active marquee star, form success. Never body text.
      },
      fontFamily: {
        display: ['"Big Shoulders Display"', '"Arial Narrow"', 'sans-serif'],
        sans:    ['Geist', 'system-ui', '-apple-system', '"Segoe UI"', 'sans-serif'],
        mono:    ['"Geist Mono"', 'ui-monospace', 'SFMono-Regular', 'Consolas', 'monospace'],
      },
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(.16,1,.3,1)',
        'in-out-quint': 'cubic-bezier(.65,0,.35,1)',
        spring: 'cubic-bezier(.34,1.56,.64,1)',
      },
      keyframes: { marquee: { from: { transform: 'translate3d(0,0,0)' }, to: { transform: 'translate3d(-50%,0,0)' } } },
      animation: { marquee: 'marquee 48s linear infinite' },
      maxWidth: { shell: '1600px' },
    },
  },
  plugins: [],
};
```
Breakpoints are Tailwind defaults: sm 640, md 768, lg 1024, xl 1280, 2xl 1536.

### 2.1 `@layer base` (assets/src/app.css)
- `@font-face` for the three variable fonts: `font-display: swap`, weight ranges `100 900` (Big Shoulders), `100 900` (Geist), `100 900` (Geist Mono); src `url('../fonts/<file>.woff2') format('woff2')`.
- `html { color-scheme: dark; scroll-padding-top: 64px; }` (`lg:` 72px via media query). `scroll-behavior: smooth` only inside `@media (prefers-reduced-motion: no-preference)`.
- `body`: `bg-ink text-paper font-sans antialiased text-[15px] leading-[1.6] overflow-x-hidden`.
- `::selection { background: rgb(242 242 238); color: rgb(5 5 5); }`
- `.dot-field` background: `background-image: radial-gradient(rgb(242 242 238 / .10) 1px, transparent 1.2px); background-size: 24px 24px;` (`md:` 28px).
- `.dot-field-fine`: same with `/.14` and `8px 8px`.

### 2.2 `@layer components` (exact @apply strings)
| class | definition |
|---|---|
| `.shell` | `mx-auto w-full max-w-shell px-4 sm:px-6 md:px-8 lg:px-10 xl:px-12` (16/24/32/40/48px gutters) |
| `.label` | `font-mono text-[11px] uppercase leading-[1.4] tracking-[0.14em] text-paper/60` |
| `.label-strong` | `.label` + `text-paper` |
| `.chip` | `inline-flex items-center border border-line px-2.5 py-1 font-mono text-[11px] uppercase tracking-[0.06em] text-paper/70 transition-colors duration-200 hover:border-line-strong hover:text-paper` |
| `.display` | `font-display font-light uppercase leading-[0.86] tracking-[-0.01em]` |
| `.heading` | `font-display font-normal leading-[0.95]` |
| `.btn` | `inline-flex h-10 items-center justify-center gap-2 whitespace-nowrap px-4 font-mono text-[11px] uppercase tracking-[0.12em] transition-colors duration-200 focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-2 focus-visible:outline-paper` |
| `.btn-solid` | `.btn` + `bg-paper text-ink hover:bg-paper/85` |
| `.btn-ghost` | `.btn` + `border border-line-strong text-paper hover:bg-paper/[0.06]` |
| `.h2-display` | `.display` + `text-[52px] sm:text-[64px] md:text-[80px] lg:text-[104px] xl:text-[120px]` |
| `.section` | `relative border-t border-line py-24 md:py-32 lg:py-40` |
| `.chapter-tag` | `.label` ; content pattern `[ 01 / 04 ] · ABOUT` with brackets/slash in `text-paper/35` |
| `.prose-nb` | article typography (phase 4) |
| `.tick` | `pointer-events-none absolute h-[9px] w-[9px]` with `::before` (1px × 9px vertical) and `::after` (9px × 1px horizontal) centered, colour `rgb(242 242 238 / .45)`. Placed with `-left-[5px] -top-[5px]` etc. on grid corners. |

Typography scale (use these, nothing else):
- Body 15px/1.6 Geist 400 (`text-[15px] leading-[1.6]`), secondary `text-paper/70`.
- Lead 18px/1.55 mobile, 20px/1.5 `md:`.
- Label 11px mono +0.14em.
- H3 heading `heading text-[36px] md:text-[44px] lg:text-[52px]`.
- H2 `h2-display`.
- Hero H1 §4.1.
- Numerals in highlights `font-display font-thin text-[64px] lg:text-[80px] leading-none`.

---------------------------------------------------------------------------------------------------
## 3. Global chrome (templates/base.html)

### 3.1 Frame (decorative, aria-hidden)
`<div aria-hidden="true" class="pointer-events-none fixed inset-1 z-[60] border border-line md:inset-2">` with four `.tick`s at the
corners (`-left-[5px] -top-[5px]`, `-right-[5px] -top-[5px]`, `-left-[5px] -bottom-[5px]`, `-right-[5px] -bottom-[5px]`). Hidden in print.

### 3.2 Header
- `<header class="fixed inset-x-0 top-0 z-50 border-b border-line bg-ink/80 backdrop-blur-md">`; inner `.shell flex h-12 items-center justify-between lg:h-14`.
- Left: brand link to `/`: `font-mono text-[12px] uppercase tracking-[0.12em] text-paper` → `NICHOLAS<span class="text-paper/40">.</span>BODE`.
- Center (`hidden lg:flex items-center gap-8`, absolutely centred: `absolute left-1/2 -translate-x-1/2`):
  `01 ABOUT`, `02 WORK`, [monogram], `03 RESEARCH`, `04 CONTACT`. Link classes:
  `relative py-2 font-mono text-[11px] uppercase tracking-[0.12em] text-paper/70 transition-colors hover:text-paper aria-[current=true]:text-paper`
  number span `mr-1.5 text-paper/40`. Active underline: `after:absolute after:inset-x-0 after:-bottom-[13px] after:h-px after:origin-left after:scale-x-0 after:bg-paper after:transition-transform after:duration-500 after:ease-out-expo aria-[current=true]:after:scale-x-100` (underline sits on the header bottom border at lg h-14).
  Monogram: link to `#top`, `grid h-7 w-7 place-items-center border border-paper/70 font-display text-[13px] font-bold tracking-tight` text `NB`.
  On sub-pages the anchors are `/#about` etc.; home uses `#about`.
- Right: `flex items-center gap-2`: `<a class="btn-ghost hidden h-8 sm:inline-flex" href="/resume/">Résumé ↗</a>` and on `<lg` a menu button
  `<button class="btn-ghost h-8 px-3 lg:hidden" aria-expanded="false" aria-controls="site-menu">Menu</button>` (text swaps to `Close`).
- main.js sets `aria-current="true"` on the nav link whose section crosses the viewport line at 35% height (IntersectionObserver with
  `rootMargin: '-35% 0px -64% 0px'`).

### 3.3 Mobile menu (`<lg` only)
`<div id="site-menu" class="fixed inset-0 z-40 flex flex-col bg-ink pt-12 lg:hidden" hidden>` (JS toggles `hidden` + `inert`).
- Inner `.shell flex flex-1 flex-col justify-between pb-6 pt-8`.
- Nav list: each `<a>` row `flex items-baseline justify-between border-b border-line py-4`; number `label`; name `display text-[56px] sm:text-[72px]`.
  Rows: About, Work, Research, Contact. Clicking closes the menu then navigates.
- Bottom: email `font-mono text-[12px]` + GitHub / LinkedIn / Résumé `chip`s, `flex flex-wrap gap-2`.
- Esc closes; focus moves to first link on open and back to the button on close. No body scroll lock.

### 3.4 Footer (all pages)
`<footer class="relative border-t border-line">` inner `.shell`:
- Row 1 `grid gap-6 py-10 md:grid-cols-3 md:py-12`: col1 `label` "Nicholas Bode — Toronto, Canada"; col2 email link `font-mono text-[12px] uppercase tracking-[0.12em] hover:text-paper`; col3 `md:text-right` links GitHub ↗ · LinkedIn ↗ · Résumé ↗ (`label` with `hover:text-paper`).
- Row 2 footer wordmark: `<div class="overflow-hidden"><p aria-hidden="true" data-fit class="display font-extrabold leading-[0.78] tracking-[-0.02em] whitespace-nowrap select-none text-paper/[0.07]">NICHOLAS BODE</p></div>` — fitted to the shell inner width by the same `data-fit` routine as §4.1 (fallback `text-[11vw]`).
- Row 3 `flex items-center justify-between border-t border-line py-4 label`: `© 2026` · `Local time <span data-clock>--:--</span> EST/EDT` · `<a href="#top">Back to top ↑</a>`.

---------------------------------------------------------------------------------------------------
## 4. Home page sections (in order). `id`s are anchors.

All sections except the hero use `.section` spacing. The chapter header block for a section is:
```html
<div class="shell">
  <p class="chapter-tag mb-6 md:mb-8">[ 01 / 04 ] · About</p>
  <h2 class="h2-display" data-split>From data to agents</h2>
</div>
```

### 4.1 Hero `#top` — `templates/partials/hero.html`
Container: `<section id="top" class="relative flex min-h-[100svh] flex-col overflow-hidden pt-12 lg:pt-14">` with a full-bleed `dot-field` layer `absolute inset-0 -z-10 opacity-60`.

1. **Ticker strip** `border-b border-line`; inner `.shell flex h-10 items-center justify-between gap-4`:
   left `label-strong` with a 6px square icon `inline-block h-1.5 w-1.5 bg-signal` + text `Open to AI engineering conversations`; right `<a class="label hover:text-paper" href="#contact">Write ↗</a>`.
2. **Meta row** `border-b border-line`; inner `.shell grid grid-cols-2 gap-x-4 gap-y-3 py-4 md:grid-cols-4 md:py-5`. Each cell two lines: `label-strong` + `label`.
   - `Nicholas` / `Bode`
   - `Toronto` / `Ontario, Canada`
   - `AI Engineer` / `LLM · Agents · Evaluation`
   - `Local time` / `<span data-clock>--:--</span>` (America/Toronto, HH:MM, updates every 15s), right-aligned on md+ (`md:text-right`).
3. **Stage** `.shell relative flex-1 grid grid-cols-1 lg:grid-cols-12 lg:gap-x-6`:
   - Sphere canvas `<canvas data-art="sphere" aria-hidden="true">` wrapper:
     - `<lg`: `relative mx-auto mt-6 aspect-square w-[min(78vw,380px)]`.
     - `lg+`: `lg:absolute lg:left-[58%] lg:top-[calc(50%+32px)] lg:mt-0 lg:w-[min(44vh,460px)] lg:pointer-events-none lg:-translate-x-1/2 lg:-translate-y-1/2`.
   - Headline block `relative z-10 mt-6 lg:col-span-5 lg:mt-0 lg:self-end lg:pb-10`:
     - pre-label `label mb-4` : `● [ 00 ] · Currently AI Engineer` (● is `text-signal`).
     - `<h1 class="display text-[56px] sm:text-[72px] md:text-[88px] lg:text-[80px] xl:text-[96px] 2xl:text-[112px]" data-split>` lines (each a `<span class="block">`):
       `Building AI` / `systems that` / `show their work`. Third line `text-paper/40` with no other change.
   - Intro card `relative z-10 mt-6 lg:col-span-4 lg:col-start-9 lg:mt-0 lg:self-center`: `border border-line bg-ink/70 p-5 backdrop-blur-sm md:p-6 lg:max-w-[400px]`.
     Paragraph `text-[15px] leading-[1.6] text-paper/80`: copy from `profile.hero.intro`.
     Buttons `mt-5 flex flex-wrap gap-2`: `btn-ghost` "See work" → `#work`; `btn-solid` "Get in touch →" → `#contact`.
4. **Wordmark** (bottom, `mt-10 lg:mt-6`): `.shell relative` containing
   `<p aria-hidden="true" class="display font-extrabold leading-[0.78] tracking-[-0.02em] text-paper select-none whitespace-nowrap" data-fit>NICHOLAS</p>`
   - `data-fit`: main.js sets font-size so the text width equals the shell inner width (measure with font loaded: `document.fonts.ready`, re-run on resize, debounced 100ms). CSS fallback before JS: `text-[19vw]`.
   - Vertical `BODE` on `sm+`: `absolute right-4 sm:right-6 md:right-8 lg:right-10 xl:right-12 bottom-[12%] origin-bottom-right -rotate-90 translate-x-full font-display font-extrabold text-[clamp(18px,2.4vw,40px)] leading-none` — (implementer: it must sit flush against the wordmark's right edge, reading bottom-to-top; adjust translate to achieve that, verify visually at 768/1440/1920.)
   - The wordmark is cropped at the bottom: wrapper `overflow-hidden` with `h-[0.8em]` relative to its font size (bottom of glyphs touches the section bottom edge).
   - Accessible name lives in h1/header; wordmark `aria-hidden`.

Acceptance: at 1440×900 the hero (ticker → wordmark) fits within 100svh, no overlap between headline, card and sphere; at 390×844 order is ticker, meta, sphere, headline, card, wordmark.

### 4.2 Marquee — `partials/marquee.html`
`<section aria-label="Practice" class="relative overflow-hidden border-t border-line py-8 md:py-10">`
- Track `flex w-max animate-marquee motion-reduce:animate-none hover:[animation-play-state:paused]`, content duplicated twice (second copy `aria-hidden="true"`).
- Words: `Evaluate ✳ Retrieve ✳ Orchestrate ✳ Ship ✳` — word classes `display px-6 text-[72px] md:text-[120px] lg:text-[160px] leading-none`; alternate words (2nd, 4th) are outline: `text-transparent [-webkit-text-stroke:1px_rgb(242_242_238_/_0.7)]`. The ✳ glyph: `font-mono text-[28px] md:text-[40px] text-paper/50 self-center`.
- Under the track: `.shell mt-4 text-center label` → `LLM applications, agents & data systems — measured, not assumed`.

### 4.3 About `#about` — `partials/about.html` (chapter 01/04)
Chapter header: tag `[ 01 / 04 ] · About`, h2 `From data to agents`.
Body grid `.shell mt-12 grid gap-12 md:mt-16 lg:grid-cols-12 lg:gap-x-6`:
- Left `lg:col-span-7`:
  - Lead statement `heading font-light text-[28px] leading-[1.15] sm:text-[32px] md:text-[40px] lg:text-[44px]`; first sentence `text-paper`, rest `text-paper/45` (copy: `profile.about.statement` = list of 2 strings).
  - Paragraphs `mt-10 max-w-[62ch] space-y-5 text-[15px] leading-[1.7] text-paper/70` (`profile.about.body`).
- Right `lg:col-span-4 lg:col-start-9`: profile table `border border-line` + `.tick`s at its 4 corners.
  - Caption row `border-b border-line px-5 py-3 label` "Profile".
  - Rows (`profile.about.facts`): `flex items-baseline justify-between gap-6 border-b border-line px-5 py-3 last:border-b-0`; key `label`, value `font-mono text-[12px] uppercase tracking-[0.08em] text-paper text-right`.
  - Below table `mt-3 grid gap-2`: `btn-solid w-full justify-between` "View résumé →" (/resume/) ; `btn-ghost w-full justify-between` "Email" + `text-paper/50` "@".

### 4.4 Expertise — `partials/expertise.html` (still chapter 01)
`<section class="relative border-t border-line">` — no chapter header; a `label` row `.shell py-6 flex justify-between`: `Areas of practice` / `04`.
Four rows (`profile.expertise`), each `<article class="border-t border-line">` inner `.shell grid gap-8 py-16 md:py-20 lg:grid-cols-12 lg:items-center lg:gap-x-6 lg:py-28`:
- Art box: `relative aspect-[4/3] border border-line bg-stage lg:col-span-6` (+ `.tick`s) containing `<canvas data-art="{{row.art}}" class="absolute inset-0 h-full w-full">` and a caption `absolute bottom-3 left-3 label` (`row.caption`).
- Text `lg:col-span-5 lg:col-start-8`; on even rows the art goes right: art `lg:order-2 lg:col-start-7`, text `lg:order-1 lg:col-span-5 lg:col-start-1`.
  - `label mb-4` → `#01 · Agents`
  - `<h3 class="heading text-[36px] md:text-[44px] lg:text-[52px]">`
  - `<p class="mt-4 max-w-[46ch] text-[15px] leading-[1.65] text-paper/70">`
  - chips `mt-6 flex flex-wrap gap-1.5`.
Arts: row1 `burst`, row2 `ridges`, row3 `halftone`, row4 `trend`.

### 4.5 Skills — `partials/skills.html`
Section `.section` with header row (not a chapter): `.shell flex items-end justify-between` h2 `h2-display` "Skills" + `label` `Stack · {{count}}` (count = total chips).
Grid `.shell mt-12 md:mt-16`: `<div class="relative grid border-l border-t border-line sm:grid-cols-2 lg:grid-cols-3">`; cells `relative border-b border-r border-line p-5 md:p-6 lg:p-8 min-h-[180px] lg:min-h-[220px]`:
head `flex justify-between label-strong` (`group.name` / `0{{loop.index}}` as `label`), chips `mt-5 flex flex-wrap gap-1.5`. Put `.tick` on each inner grid intersection (top-left corner of every cell).
The "Portfolio-only" group gets an extra line under the head: `label mt-2 normal-case tracking-[0.04em]` "Used in public projects, not professionally."

### 4.6 Experience — `partials/experience.html`
Header: h2 "Experience" + right `label` `Path`.
List `.shell mt-12 md:mt-16`. Each role `<article class="grid gap-y-4 border-t border-line py-10 md:py-12 lg:grid-cols-12 lg:gap-x-6">`:
- `lg:col-span-2 label` → `#1 · Apr 2026 — Present`
- `lg:col-span-4`: `heading text-[32px] md:text-[40px]` title; `label mt-2` org.
- `lg:col-span-6`: summary `text-[15px] leading-[1.65] text-paper/75`; bullets `mt-5 space-y-2 text-[14px] leading-[1.6] text-paper/65` with `before:` 6px square marker (`relative pl-5 before:absolute before:left-0 before:top-[0.6em] before:h-1.5 before:w-1.5 before:bg-paper/40`); first 3 bullets visible, rest inside `<details class="group mt-3">` with summary `label hover:text-paper cursor-pointer list-none` "+ Read more" / "− Less" (swap via `group-open:`). Chips `mt-6 flex flex-wrap gap-1.5`.
Education sub-block below, `mt-20`: `label mb-6` "Education & publication"; grid like Skills (`sm:grid-cols-2 lg:grid-cols-3`), cell content: `label` year, `heading text-[24px] md:text-[28px] mt-3` title, `text-[13px] text-paper/60 mt-2` org/detail, optional link `label mt-4 hover:text-paper` "Read ↗".

### 4.7 Highlights — `partials/highlights.html`
`.section` header h2 "Selected outcomes" (no chapter tag). Grid `.shell mt-12 grid border-l border-t border-line sm:grid-cols-2 lg:grid-cols-3`; cell `border-b border-r border-line p-6 lg:p-8 min-h-[220px] flex flex-col justify-between`: numeral `font-display font-thin text-[64px] lg:text-[80px] leading-none text-paper/90` (`01`…`06`), text `mt-8 text-[15px] leading-[1.55] text-paper/80 max-w-[34ch]`.

### 4.8 Off the clock — `partials/offclock.html`
`.section` grid `.shell lg:grid-cols-12 lg:gap-x-6 gap-12 grid`:
- Left `lg:col-span-5`: `label` "[ ∞ ] · Off the clock"; h2 `h2-display mt-6` "Keys & cameras"; p `mt-8 max-w-[44ch] text-paper/70` (profile.offclock.body); stats `mt-10 grid grid-cols-2 border-t border-line`: each stat `py-5 pr-4` numeral `display text-[64px] md:text-[80px]` + `label mt-2` caption.
- Right `lg:col-span-6 lg:col-start-7`: `relative aspect-[5/4] border border-line bg-stage` with `<canvas data-art="pianoroll">` + caption `label absolute left-3 top-3` "Piano roll · generative".

### 4.9 Selected work `#work` — `partials/work.html` (chapter 02/04)
Data: `profile.projects` (6 items, order §8.6).
Outer `<section id="work" class="relative border-t border-line" data-rail>`.
Header always rendered first: `.shell pt-24 md:pt-32 lg:pt-40` with chapter tag `[ 02 / 04 ] · Work`, h2 `Selected work`, p `mt-6 max-w-[52ch] text-paper/70` (profile.work_intro), `label mt-6` `All public on GitHub · {{n}} projects`.

Card markup (same in both modes): `<article class="rail-card flex flex-col border border-line bg-ink">`
- top meta `flex justify-between border-b border-line px-4 py-3 md:px-6 label`: `01 / 06` · `Independent project · 2026`.
- art `relative aspect-[16/10] border-b border-line bg-stage dot-field-fine overflow-hidden` containing the project's inline SVG diagram (§5.2) `absolute inset-0 h-full w-full`.
- body `grid gap-6 p-4 md:p-6 xl:grid-cols-2 xl:gap-8`: left `heading text-[32px] md:text-[40px] xl:text-[48px]` title + `label mt-3` tagline; right desc `text-[14px] leading-[1.6] text-paper/70 line-clamp-4`, chips `mt-4 flex flex-wrap gap-1.5`, buttons `mt-5 flex flex-wrap gap-2`: `btn-solid h-9` "Case study" → `/work/<slug>/`; `btn-ghost h-9` "Source ↗" → repo.

**Mode A — vertical (default, `<lg`, and any width when reduced motion or no JS):** `.shell mt-12 grid gap-6 pb-24 md:grid-cols-2 md:gap-6 md:pb-32`.
**Mode B — horizontal rail (`lg+` and JS and motion allowed; main.js adds `html.rail-on`):**
- Outer track wrapper `relative` with inline `style="height: calc(N × 70vh + 100svh)"` (N = number of cards, computed in JS).
- Sticky viewport `sticky top-14 h-[calc(100svh-56px)] overflow-hidden flex flex-col justify-center`.
- Track `flex gap-6 pl-10 xl:pl-12 pr-[30vw] will-change-transform` translated `translate3d(-p × (trackWidth − viewportWidth), 0, 0)` where p ∈ [0,1] from the wrapper's scroll progress (rAF, passive listeners).
- Cards `w-[min(64vw,880px)] shrink-0`; art `aspect-[16/9]`; body forced to `xl:grid-cols-2`. Height must fit: card ≤ `calc(100svh − 56px − 96px)`.
- Progress row under track `mt-6 flex items-center gap-4 px-10 xl:px-12`: `label` `01 / 06` (live), `relative h-px flex-1 bg-line` with fill `absolute inset-y-0 left-0 bg-paper origin-left` `scaleX(p)`, `label` "Scroll →".
- Keyboard: on `focusin` inside a card that is outside the sticky viewport, `window.scrollTo` the wrapper offset that centres that card (instant if reduced motion). Tab order stays DOM order.
- After the last card the section releases naturally.

### 4.10 Research `#research` — `partials/research.html` (chapter 03/04)
Header: tag `[ 03 / 04 ] · Research`, h2 `Patterns inside change`.
Rows `.shell mt-12 md:mt-16` each `<article class="grid gap-8 border-t border-line py-12 lg:grid-cols-12 lg:gap-x-6 lg:py-16">`:
1. Thesis: left `lg:col-span-5` `relative aspect-[4/3] border border-line bg-stage` with `<canvas data-art="trend" data-variant="segments">`; right `lg:col-span-6 lg:col-start-7`: `label` "MSc thesis · 2023", h3 `heading text-[36px] md:text-[48px]` "Discovery of Trend Dependencies Over Time-Series", p (profile.research.thesis.summary), list of 3 method chips, buttons `btn-solid` "Read the explainer" → /research/trend-dependencies/ and `btn-ghost` "Thesis PDF ↗".
2. Publication: no art; `lg:col-span-5 label` "Springer Nature · 2024"; `lg:col-span-6 lg:col-start-7` title h3 `heading text-[28px] md:text-[36px]` "Automated Image Captioning for the Visually Impaired", p `text-paper/70` "Bode, N. & Sukhai, M. Encyclopedia of Computer Graphics and Games. First and corresponding author.", `btn-ghost mt-6` "DOI ↗".

### 4.11 Contact `#contact` — `partials/contact.html` (chapter 04/04)
Header: tag `[ 04 / 04 ] · Contact`, h2 `Let's work together` (on `<sm` force 2 lines via `<br class="sm:hidden">`).
Grid `.shell mt-12 grid gap-12 md:mt-16 lg:grid-cols-12 lg:gap-x-6`:
- Left `lg:col-span-5`: p `max-w-[40ch] text-paper/70` (profile.contact.intro). Rows `mt-8 border-t border-line`, each `flex items-center justify-between border-b border-line py-4`: key `label` (Email, LinkedIn, GitHub, Base), value `font-mono text-[12px] md:text-[13px] uppercase tracking-[0.08em]` link with ↗.
- Right `lg:col-span-6 lg:col-start-7`: `<form data-mailto class="relative border border-line p-5 md:p-8">` `.tick`s on corners. Header `flex justify-between label` "› New message" / "mailto". Fields stacked `mt-6 space-y-6`: `<label class="block"><span class="label">01 · Name</span><input class="mt-2 w-full border-0 border-b border-line bg-transparent px-0 py-3 text-[15px] text-paper placeholder:text-paper/30 focus:border-paper focus:outline-none focus:ring-0" …></label>` (02 · Email type=email, 03 · Message `<textarea rows="5">`). Submit `btn-solid mt-8 w-full sm:w-auto` "Compose email →". JS builds `mailto:{{email}}?subject=Hello from {name}&body={message}\n\n— {name} ({email})` and sets `location.href`; shows `label text-signal mt-3` "Opening your mail app…". No network requests.

---------------------------------------------------------------------------------------------------
## 5. Art

### 5.1 Canvas registry (`assets/js/art.js`)
Common rules: DPR-aware (`Math.min(devicePixelRatio, 2)`), ResizeObserver sizing to the element box, IntersectionObserver pauses rAF when
offscreen, `document.hidden` pauses, reduced motion ⇒ draw a single frame at t=0.6s and stop. Colour = paper `rgb(242,242,238)` with alpha only.
Deterministic PRNG (mulberry32, seed per art) — no `Math.random` so frames are stable. `window.initArt(root=document)` (idempotent: mark `data-art-ready`).

| key | description |
|---|---|
| `sphere` | Dot-matrix halftone sphere. Cell 6px (5px if canvas < 320px CSS). For each cell centre inside radius R=0.46·min(w,h): normal from sphere eqn, Lambert with light dir rotating (0.14 rad/s around Y) + crater: subtract `0.35·gauss(dist to crater centre, σ=0.18)` where crater centre lies on the rotating surface. Draw square of side `cell·0.92·lum^0.8`, alpha 0.35+0.65·lum. Outside sphere: sparse static dots (cell 12px, alpha .10). Pointer (fine pointers only) nudges light ±0.25 with 0.06 easing. |
| `burst` | 260 lines from a centre at (0.62w, 0.55h): each angle θ_i, length 0.3–1.4·diag, alpha .08–.5, width .6–1px; slow rotation 0.01 rad/s and per-line length breathing. A 9px white disc + 2px ring at centre. |
| `ridges` | 34 horizontal ridgelines, spacing h/40, each y offset by sum of 3 gaussians near centre (amplitude grows toward middle rows) + time drift 0.15 rad/s; fill ink beneath each line (occlusion), stroke paper alpha .85, 1px. |
| `halftone` | Grid cell 10px; size = 0.5+0.5·sin(x·0.035 + t) · cos(y·0.03 − t·0.6) mapped to squares; plus a 3-node flow line overlay (dashed). Reads as "data". |
| `trend` | Noisy series (220 pts) with 2 structural breaks; scatter dots r=1.2 alpha .7; fitted segment lines 1.5px paper; dashed vertical breakpoint lines alpha .4 with mono labels `t₁`, `t₂`; tolerance band (±ε) alpha .08 fill. Animate a scanning cursor left→right over 8s loop. `data-variant="segments"` adds segment labels `A`,`B`,`C`. |
| `pianoroll` | Port the existing music canvas from `assets/world.js` (`data-music-art`) but monochrome: rounded note bars paper alpha .25–.9 by velocity, keyboard strip on left (white/black keys outline), playhead at 62% width, scrolling 40px/s, adjacent cycles never wrap visibly. |

### 5.2 Project diagrams (inline SVG in `templates/partials/project_art/<slug>.svg.html`)
Style: `viewBox="0 0 800 500"`, stroke `rgb(242 242 238 / .7)` 1px, boxes `fill="#0b0b0b"`, labels `font-family: Geist Mono; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; fill: rgb(242 242 238 / .7)`, one highlighted box filled with a 3px dot pattern (`<pattern>`), `aria-hidden="true"` (the card text describes it). Content:
- trainstore: 3 host boxes `HOST A · AZ1`, `HOST B · AZ1`, `HOST C · AZ2` (k3s), arrows to `S3 · OBJECTS` and `VALKEY · METADATA`; `JUICEFS (POSIX)` layer box; `CHECKPOINT MANIFEST` highlighted with label `IF-MATCH`.
- agent-shield: two horizontal lanes `VULNERABLE` and `POLICY-ENFORCED`; each `PROMPT → AGENT → TOOL`; an `INJECTED INSTRUCTION` packet enters both; lane 1 ends at `NOTIFY ✕ EXECUTED`, lane 2 at `IGNORED` (highlighted). Caption `SINGLE-CASE DEMONSTRATION`.
- casestruct-lora: grouped bar chart, two groups `CONSTRUCTCIE N=80`, `OSHA N=333`; bars baseline 82.1 / 64.0 (outline) and LoRA v2 93.1 / 80.1 (dot pattern) with CI whisker labels `+11.0 PP [+1.7, +21.1]`, `+16.0 PP [+9.2, +22.1]`; y-axis `MACRO-F1`; footnote `EXPLORATORY · NOT A PRISTINE HOLDOUT`.
- evaluated-rag: `RETRIEVE → DRAFT → CHECK → ANSWER | ABSTAIN` with `CITATION`, `GROUNDING` gates; `30-Q DEV SET`.
- analytics-pipeline: layered DAG `RAW → STAGING → INTERMEDIATE → MARTS → FACT (INCREMENTAL)` with test diamonds `UNIQUE`, `NOT NULL`, `IDEMPOTENT`.
- piano-transcription: `AUDIO → ONSETS → MIDI → SCORE` with mini piano-roll bars.

---------------------------------------------------------------------------------------------------
## 6. Sub-pages (phase 4)
- `/work/<slug>/` article: header block `.shell pt-28 lg:pt-36` — back link `label hover:text-paper` "← All work"; `chapter-tag mt-10` `{{category}} · {{year}}`; `<h1 class="display text-[48px] sm:text-[64px] md:text-[80px] lg:text-[96px] max-w-[16ch]">`; deck `mt-8 max-w-[60ch] text-[18px] md:text-[20px] text-paper/70`; meta `mt-12 grid border-l border-t border-line sm:grid-cols-3` cells `border-b border-r border-line p-5` (`dt label`, `dd mt-2 text-[14px]`). Project SVG art full-width `mt-12 aspect-[16/9] border border-line bg-stage dot-field-fine`.
  Body `.shell grid lg:grid-cols-12 gap-x-6 py-20`: sticky rail `lg:col-span-3 lg:sticky lg:top-24 self-start` (`label` On this page + generated h2 TOC), prose `lg:col-span-7 lg:col-start-5 prose-nb`.
  `.prose-nb`: h2 `heading text-[32px] md:text-[40px] mt-16 mb-5`; h3 `heading text-[24px] mt-10 mb-3`; p `text-[16px] leading-[1.75] text-paper/75 my-5`; a `underline decoration-paper/30 underline-offset-4 hover:decoration-paper`; strong `text-paper font-medium`; ul markers like §4.6; code `font-mono text-[13px] bg-paper/[0.06] px-1.5 py-0.5`; table `w-full border-collapse text-[14px]` th `label text-left border-b border-line-strong py-3 pr-4` td `border-b border-line py-3 pr-4 text-paper/75`; tables reflow to labeled cards below 700px using existing `data-label` attributes; blockquote `border-l border-paper/40 pl-5 text-paper/80`.
  Next-project footer: `border-t border-line` full-width link `display text-[48px] md:text-[96px]` "Next → {{title}}".
- `/work/`: chapter header + Mode A card grid (all 6).
- `/research/`: header + the two research rows from §4.10.
- `/about/`: reuse about + experience + skills partials.
- `/resume/`: a web résumé — single column `.shell max-w-[880px]`, sections Experience / Projects / Education / Skills rendered from profile.yaml, `print:` styles (white bg, black text, hide header/frame/footer), button `btn-solid` "Print / save PDF" (`window.print()`).
- `/contact/`: contact partial.

---------------------------------------------------------------------------------------------------
## 7. Motion (main.js)
- Add `js` class on `<html>` in an inline head script before CSS paints.
- `[data-split]`: wrap each word in `<span class="inline-block overflow-hidden pb-[0.06em] align-top"><span class="inline-block translate-y-[105%] transition-transform duration-[900ms] ease-out-expo" style="transition-delay:{i*45}ms">word</span></span>`; set `aria-label` on the heading to the original text and `aria-hidden` on the wrappers. On intersect (threshold .2) add `is-in` → inner `translate-y-0`. Preserve existing child `<span class="block">` line structure.
- `[data-reveal]`: `html.js [data-reveal]{opacity:0; transform:translateY(24px)}` → `.is-in` opacity 1 / none, `transition 900ms cubic-bezier(.16,1,.3,1)`, delay from `--d`.
- Reduced motion: none of the hidden states apply (`@media (prefers-reduced-motion: reduce)` resets).
- Buttons arrows `→` nudge `group-hover:translate-x-0.5 transition-transform duration-300 ease-spring`.
- `window.initSite()` re-binds everything idempotently (needed by the offline preview router).

---------------------------------------------------------------------------------------------------
## 8. Content (`content/profile.yaml`) — copy is part of the spec
Use this copy verbatim unless a field is marked (draft).

```yaml
hero:
  intro: "I build LLM-powered applications, agent tooling and evaluation harnesses — and I care about knowing when they are wrong. Before that, I built ML models and production data pipelines on large, real-world location data."
about:
  statement:
    - "AI Engineer in Toronto."
    - "I turn messy, real-world data into LLM applications and agents that can be tested, audited and trusted."
  body:
    - "I'm an AI Engineer at Environics Analytics, building LLM-powered applications that combine models, data and cloud infrastructure: agent-facing tool servers, secured remote access, review workflows with humans in the loop, and the evaluations that decide whether any of it ships."
    - "Before that I spent two years as a Research Associate in machine learning — building production data pipelines, automated quality control and XGBoost models over foot-traffic, GPS, demographic and mapping data, and investigating anomalies down to their root cause."
    - "I hold an MSc in Computer Science from Ontario Tech University, where my thesis introduced trend dependencies: approximate, learned constraints over noisy time series. Outside of work I play piano, and for five years I worked as a screen actor."
  facts:  # key, value
    - [Based in, "Toronto, ON"]
    - [Role, "AI Engineer"]
    - [At, "Environics Analytics"]
    - [Before, "Research Associate, ML"]
    - [Education, "MSc Computer Science"]
    - [Focus, "LLMs · Agents · Evaluation"]
expertise:
  - {tag: "#01 · Agents", title: "Agents & tool interfaces", art: burst, caption: "Fig. 01 — tool fan-out",
     body: "Agent-facing tool servers (MCP) with permission-gated read, write and delete tool families, authenticated remote access via OAuth with PKCE, and composite tools that bundle expensive sequences into single agent-usable operations.",
     chips: [MCP, LangGraph, Microsoft Agent Framework, FastAPI, pydantic, OAuth / PKCE]}
  - {tag: "#02 · Evaluation", title: "Evaluation & guardrails", art: ridges, caption: "Fig. 02 — distributions",
     body: "Benchmarks with baselines, paired comparisons and stated limits. Grounding and citation checks, prompt-injection test suites, random audits and human review queues — so a model's output is accepted on evidence, not fluency.",
     chips: [LangSmith, MLflow, RAG evaluation, Red-teaming, Human-in-the-loop]}
  - {tag: "#03 · Data", title: "Data & ML pipelines", art: halftone, caption: "Fig. 03 — signal field",
     body: "Production pipelines in dbt and Airflow on Snowflake, QC gates that decide release readiness, geospatial ingestion, and XGBoost models carried into production QA.",
     chips: [Snowflake, dbt, Airflow, PySpark, XGBoost, Databricks]}
  - {tag: "#04 · Research", title: "Time-series research", art: trend, caption: "Fig. 04 — trend dependencies",
     body: "An MSc on discovering approximate, learned relationships over noisy time series — symbolic regression, policy-gradient regression and change-point segmentation.",
     chips: [PyTorch, Transformers, Symbolic regression, Segmentation]}
skills:
  - {name: "LLMs & agents", items: [LLMs, RAG, Prompt engineering, LangGraph, LangSmith, Microsoft Agent Framework, Azure AI Foundry, MCP, pydantic]}
  - {name: "Machine learning", items: [PyTorch, scikit-learn, XGBoost, Neural networks, CNNs, Time series]}
  - {name: "Data engineering", items: [Python, SQL, Snowflake, dbt, Airflow, PySpark, Pandas, Databricks]}
  - {name: "Cloud & platform", items: [Microsoft Azure, AWS, Azure DevOps, Docker, Git]}
  - {name: "Applications", items: [FastAPI, REST APIs, TypeScript, React, Node.js, Power BI]}
  - {name: "Portfolio-only", portfolio_only: true, items: [Go, Kubernetes (k3s), JuiceFS, MLflow, Hugging Face PEFT / TRL, Weights & Biases]}
experience:
  - {when: "Apr 2026 — Present", title: "AI Engineer", org: "Environics Analytics · Toronto (hybrid)",
     summary: "Building LLM-powered applications that combine AI, data and cloud infrastructure, and supporting other teams as they adopt AI through regular sessions and shared demos.",
     bullets:
       - "Extended an agent-facing MCP tool platform: authenticated remote HTTPS access per client alongside a local stdio entry point, and SDK extensions for native report creation and PDF export."
       - "Built an OAuth-secured remote tool service (Azure AD B2C, PKCE, per-profile tokens, encrypted server-side token storage) exposing existing business APIs to agents."
       - "Built an LLM-assisted review workbench: rule-based auto-approval plus LLM review of justification quality, random 100-record audits and a human review queue."
       - "Implemented authorization enforcement across document search, connectors and tools for a self-hosted enterprise search deployment, with audit trails and access revocation."
       - "Built a human-labelling and outlier-review pipeline (HDBSCAN, UMAP) on top of an existing rule-based dbt model."
       - "Designed reusable agent skills for data-quality exploration, anomaly diagnosis and root-cause workflows, and agent automations that require explicit approval before any mutation."
     chips: [Azure AI Foundry, LangGraph, LangSmith, FastAPI, pydantic, RAG]}
  - {when: "Feb 2024 — Apr 2026", title: "Research Associate, Machine Learning", org: "Environics Analytics · Toronto",
     summary: "Statistical and ML evaluation of large-scale mobile and location datasets, production data pipelines, automated quality control and release investigations.",
     bullets:
       - "Built a mobility data product end to end on Snowflake: weekly incremental processing and QC gates that produce a release-readiness recommendation."
       - "Benchmarked four model versions across nine evaluation dimensions against public retail benchmarks and client ground truth, recommending a conditional go."
       - "Built XGBoost foot-traffic models that went into production QA, chosen over alternatives for retraining speed and fit."
       - "Traced apparent traffic spikes to an upstream methodology change rather than real-world movement, after reimplementing the outlier method."
       - "Built a unified product-health and QC repository: weekly and annual reporting, volume estimation, outlier detection and orchestration."
       - "Wrote pipelines in dbt for two years and ported them to Airflow 3.x; built batched OpenStreetMap ingestion into Snowflake."
     chips: [Snowflake, dbt, Airflow, XGBoost, Python, SQL]}
  - {when: "Jan 2020 — Feb 2024", title: "Teaching Assistant", org: "Ontario Tech University · Oshawa",
     summary: "Part-time teaching assistant for undergraduate computer science alongside BSc and MSc studies.", bullets: [], chips: []}
education:
  - {year: "2021 — 2024", title: "MSc, Computer Science", org: "Ontario Tech University", detail: "Thesis: Discovery of Trend Dependencies Over Time-Series", link: "/research/trend-dependencies/"}
  - {year: "2017 — 2021", title: "BSc, Computer Science", org: "Ontario Tech University", detail: "Mathematics minor"}
  - {year: "2024", title: "Automated Image Captioning for the Visually Impaired", org: "Springer Nature", detail: "Encyclopedia entry · first & corresponding author", link: "https://doi.org/10.1007/978-3-031-23161-2_501"}
highlights:
  - "Agent tool servers with permission-gated tool families and authenticated remote access."
  - "OAuth + PKCE secured remote tooling with encrypted server-side token storage."
  - "LLM review workflows that pair automatic rules with audits and a human queue."
  - "A QC-gated mobility data product, built end to end on Snowflake."
  - "A four-version, nine-dimension release benchmark ending in a go / no-go call."
  - "XGBoost foot-traffic models carried into production QA."
offclock:
  body: "I passed Grade 10 piano with the Royal Conservatory of Music, and from 2011 to 2016 I worked as a professional screen actor — including roles on Hannibal and Murdoch Mysteries. Both taught me the same thing engineering does: rehearse, then perform under scrutiny."
  stats: [["10", "RCM piano grade"], ["5", "Years on set"]]
work_intro: "Independent projects, all public on GitHub. Each one states what it measured, what it did not, and where it breaks."
contact:
  intro: "Open to conversations about AI engineering, agents, evaluation and data systems. The fastest way to reach me is email."
  base: "Toronto, Canada"
research:
  thesis:
    summary: "Introduces trend dependencies — constraints built from a learned function and an allowed deviation — and methods to discover them in noisy time series, including approximate and conditional variants that hold only over particular regimes."
    chips: [Symbolic regression, Policy-gradient regression, Change-point segmentation]
```

### 8.6 Projects (order) — `profile.projects`
Fields: `slug, title, tagline, year, desc, chips, repo`.
1. `trainstore` — "TrainStore" — tagline "Kubernetes-native ML storage" — desc "S3-compatible object storage, JuiceFS POSIX access and checkpointing for PyTorch on a k3s cluster across two AWS availability zones — with a manifest-committed checkpoint protocol that a stale writer cannot overwrite." — chips [Python, Go, k3s, AWS, JuiceFS, PyTorch] — repo github.com/simplysoup/trainstore
2. `agent-shield` — "AgentShield" — "Prompt-injection evaluation for tool-using agents" — "Paired vulnerable and policy-enforced agent runs, frozen fixtures, adaptive attack generation and tool-level authorization with audit events. 68 automated tests." — [Python, LangGraph, OpenAI, Groq, pytest] — github.com/simplysoup/agent-shield
3. `casestruct-lora` — "CaseStruct-LoRA" — "LoRA study for incident-text classification" — "A reproducible Qwen3-0.6B LoRA study on construction-accident and occupational-injury classification, with paired-bootstrap confidence intervals against the strongest baselines." — [PyTorch, PEFT, TRL, Hugging Face, Qwen] — github.com/simplysoup/casestruct-lora
4. `evaluated-rag` — "Evaluated RAG" — "Grounded document QA, measured" — existing case-study description — [Python, LangGraph, Pydantic, MLflow] — github.com/simplysoup/evaluated-rag-agentic
5. `analytics-pipeline` — "Analytics pipeline" — "Incremental dbt models that prove idempotency" — existing description — [Python, DuckDB, dbt] — github.com/simplysoup/analytics-pipeline-dbt
6. `piano-transcription` — "Piano transcription" — "Expressive audio to editable notation" — existing description — [Python, Audio ML, MIDI] — github.com/simplysoup/yt-piano-transcription

---------------------------------------------------------------------------------------------------
## 9. Publication safety rules (content writers)
Allowed: employer name, job titles, dates, generic descriptions of work types and tools (as in §8).
Forbidden anywhere in published output: internal product/platform names (Envision, MobileScapes, Customer 360, Cortex,
Onyx), client or partner names (Esri, Statistics Canada), dataset sizes (52TB), deal values, internal compute sizes,
unreleased-product timelines, PR/deployment status of internal work, colleague names other than publication co-author.
Project case studies must keep the resume's stated caveats (exploratory numbers, single-case demos, synthetic data, no production claims).

---------------------------------------------------------------------------------------------------
## 10. Phases
1. Tooling (Luna): tailwind pipeline, fonts, preview inlining, test chromium path.
2. Shell + hero + marquee + footer + menu (Terra). → demo
3. About chapter: about, expertise, skills, experience, highlights, offclock + art.js (Terra). → demo
4. Work rail + project SVGs + research + contact + new case studies (Terra). → demo
5. Sub-pages/articles/resume (Terra). → demo
6. Cleanup, verify_v14, preview, docs (Luna). → final demo
