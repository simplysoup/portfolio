# Phase 3 — About chapter + canvas arts (visual). Implementer: GPT-6.1 Terra.

Repo: /home/soup/Projects/portfolio, branch `redesign-v14`. Read docs/redesign-v14/PROJECT_RULES.md and docs/redesign-v14/SPEC.md completely; SPEC class strings are used verbatim. Phases 1–2 are done (Tailwind pipeline, base shell, hero, marquee, main.js, art.js with `sphere`). Do NOT commit. Do not change the hero/marquee/header/footer except to fix a bug you introduce.

## Scope
1. Partials, rendered from `profile` (content/profile.yaml — never hard-code copy that exists there):
   - `partials/about.html` §4.3 (`<section id="about" class="section">`)
   - `partials/expertise.html` §4.4
   - `partials/skills.html` §4.5
   - `partials/experience.html` §4.6 (incl. education sub-block)
   - `partials/highlights.html` §4.7
   - `partials/offclock.html` §4.8
   Insert them in `templates/index.html` after the marquee in that order, replacing the `<div id="about"></div>` placeholder (keep the other placeholders).
2. Shared tiny Jinja macros in `templates/partials/_macros.html`: `chapter_header(tag_num, tag_name, title)`, `chip_list(items, extra_classes='')`, `ticks()` (outputs the four corner `.tick` spans). Refactor hero/marquee only if trivially needed.
3. `assets/js/art.js`: implement `burst`, `ridges`, `halftone`, `trend` (+ `data-variant="segments"`), `pianoroll` per SPEC §5.1 inside the existing registry. `pianoroll`: port the note-generation/scrolling logic from `assets/world.js` (`data-music-art` renderer) into monochrome. All arts obey the common rules (DPR ≤2, pause offscreen/hidden, reduced motion = one static frame, seeded PRNG).
   Quality bar: each art must read clearly at 390px wide and at 1440px wide; lines crisp (align 1px strokes to half-pixels), no blurry upscaling, no visible seams in the piano roll.
4. `[data-reveal]` on: about profile table, each expertise text block, skills cells (stagger `--d` 0/60/120ms per column), experience articles, highlight cells, offclock stats.
5. Header active-state: the `01 ABOUT` link must be current from #about through the end of the off-clock section (wrap about→offclock in a `<div data-chapter="about">` or give the observer that range).

## Exact layout acceptance (check in screenshots)
- 1440×900: about grid statement 7 cols / profile table 4 cols starting col 9; expertise rows alternate art left/right with art 6 cols; skills 3 columns × 2 rows with ticks at intersections; experience rows 2/4/6 cols; highlights 3×2; offclock 5/6 cols.
- 768×1024: skills 2 columns; highlights 2 columns; expertise stacked art-above-text.
- 390×844: everything single column, art boxes full width, chips wrap, no text smaller than 11px, profile table rows don't overflow (long values wrap right-aligned).
- `<details>` "+ Read more" toggles and shows "− Less" when open; works by keyboard.

## Verification
- build + preview succeed; screenshots of every new section at 390, 768, 1440, 1920 into `screenshots/v14/phase3/` (full-page captures are fine, plus one viewport crop per section at 1440). LOOK at them; iterate until they match the spec.
- No horizontal overflow at 320/390/768/1024/1440/1920; no console errors; reduced-motion: all content visible, arts static.
- Measure: canvases pause when offscreen (log rAF count while scrolled away — must be 0 for offscreen arts).

## Output
Report files changed, screenshot paths, any spec deviations with reasons.
