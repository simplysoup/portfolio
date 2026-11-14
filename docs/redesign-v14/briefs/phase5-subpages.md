# Phase 5 — Sub-pages, articles, web résumé (visual). Implementer: GPT-6.1 Terra.

Repo /home/soup/Projects/portfolio, branch redesign-v14. Read docs/redesign-v14/PROJECT_RULES.md and docs/redesign-v14/SPEC.md (§6 is yours; §2 tokens; §7 motion). Phases 1–4 are done. Do NOT commit; never run git checkout/restore/stash. Do not restyle the home page.

## Scope
1. Remove the legacy bridge: base.html must no longer load `styles.css` on any page. Every page renders with app.css only. `site.js` (RAG + trend exhibits) is still loaded on article pages only — restyle its generated markup by adding Tailwind-compatible classes in site.js or `@layer components` rules in assets/src/app.css (monochrome, hairlines, mono labels; controls ≥40px; range inputs styled with `accent-color: rgb(242 242 238)`).
2. `templates/article.html` per SPEC §6 (header, meta grid, project SVG art from `partials/project_art/<slug>.svg.html` if it exists — research article uses a `<canvas data-art="trend" data-variant="segments">` instead, sticky TOC built at build time in scripts/build.py by collecting h2s and adding `id`s (slugified, unique), `.prose-nb` content, exhibit band, next-project footer cycling through `work_order`). Implement `.prose-nb` in `assets/src/app.css` `@layer components` exactly as SPEC §6 (+ table reflow below 700px using `data-label`: each row a bordered card, each cell `grid grid-cols-[minmax(96px,40%)_1fr] gap-3` with `content: attr(data-label)` as a `label`).
3. `/work/` (work.html): chapter header `[ 02 / 04 ] · Work`, h2 "Selected work", then Mode-A card grid of all 6 projects (reuse the card partial from phase 4 — refactor it into `partials/project_card.html` if it isn't already).
4. `/research/`: header `[ 03 / 04 ] · Research` + the research rows partial.
5. `/about/`: about + experience + skills partials, then `offclock` (only place it appears) — remove the legacy about markup.
6. `/contact/`: contact partial.
7. `/resume/`: printable web résumé per SPEC §6 from profile.yaml: name block (name, "AI Engineer — LLM and agentic systems", Toronto, email, GitHub, LinkedIn), Experience (all bullets), Projects (6, one line each + repo URL), Education & publication, Skills (grouped; portfolio-only group labelled). Screen: `.shell max-w-[880px] pt-28 lg:pt-36 pb-24`, section heads `label-strong border-b border-line pb-3 mt-14`, role rows `grid sm:grid-cols-[1fr_auto]` title `heading text-[28px]` + date `label`. Button `btn-solid` "Print / save PDF" (`onclick=window.print()`, also in a `<noscript>` note). Print CSS (`@media print` in app.css): white bg, black text, hide header/frame/footer/menu/buttons, 10.5pt Geist, 0.5in margins via `@page`, avoid breaking inside role blocks, links print as text + URL for external links.
8. Delete now-unused legacy files: assets/styles.css, assets/world.css, assets/world.js, assets/scrollchapters.css, assets/scrollchapters.js, assets/field-study.png if unreferenced (grep first; keep og-cover.png & favicon.svg). Update build_preview.py if it still names them.
9. Offline preview: router must handle all routes, run `initSite/initArt/initPortfolioExhibits` after swaps, scroll to top on route change, and in-page `#about` style anchors on home must still work.

## Acceptance
- Every route (`/`, `/work/`, 6 × `/work/<slug>/`, `/research/`, `/research/trend-dependencies/`, `/about/`, `/contact/`, `/resume/`) at 390 and 1440: no overflow, no console errors, fonts loaded, no unstyled legacy markup left.
- Article tables reflow at 390; TOC links jump correctly under the fixed header (scroll-padding).
- RAG and trend exhibits work (click each scenario / move each slider) on the hosted site AND offline preview.
- Print emulation (`page.emulate_media(media='print')`) of /resume/ produces a PDF (`page.pdf`) of ≤ 3 Letter pages, black on white; save to screenshots/v14/phase5/resume.pdf.
Screenshots to screenshots/v14/phase5/ — look at them and iterate.

## Output
Files changed/deleted, screenshot paths, PDF page count, deviations with reasons.
