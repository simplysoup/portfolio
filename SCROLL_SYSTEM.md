# Directory 13 — Scroll chapters

The homepage keeps the four-door Directory index and its direct case-study links. Scrolling past the hero opens an independent sequence of four full-viewport project profiles (RAG evaluation, incremental data pipeline, thesis, piano transcription), followed by a closing contact chapter.

## Behavior

- Each profile is a **154svh track on desktop / 142svh on mobile** with a **100svh sticky viewport**. This gives each project time to enter, hold, build pressure and release without taking control of the scroll wheel.
- Native `scroll-snap-type: y proximity` helps the viewport settle at the beginning of a chapter but does not force snap on every wheel gesture. `prefers-reduced-motion` disables snapping and motion.
- `scrollchapters.js` reads bounding rectangles in a requestAnimationFrame scheduled by passive scroll/resize events and sets `--entry`, `--progress`, `--pressure`, `--release`. No timer-driven fake scroll and no scroll-locking.
- `--pressure = sin(pi * progress)^2` is zero at each end and peaks midway through the hold. The artwork scales and the text lifts as pressure accumulates; both relax before the next scene takes over. `--release` controls the visual mask late in the scene.
- Each scene contains an original, technical visual with a direct link to its public case study. The visuals are **illustrative** and do not claim to reproduce employer systems or measured research data.
- The index still supports click/tap chapter navigation. Project showcases are accessible with one click from the hero and by scrolling. No project access is animation-gated.

## Mobile and accessibility

- At 320px and short phone heights, profile layouts allocate separate bands for copy/CTA and artwork. There is no overlapping case-study link.
- Case-study HTML tables are enhanced at build-time with `data-label` cells. Below 700px, each table row becomes a labeled comparison card. Table semantics remain intact in the markup on larger screens.
- The music chapter restores a soft, luminous note-bar appearance with a continuously scrolling timeline. Consecutive score cycles render adjacent to one another so notes never wrap across the viewport as individual bars. The renderer pauses when the chapter is hidden.
- Animations are decorative only. Reduced-motion mode shows the complete artwork and all links in place. The index, project links, and articles use semantic anchors.

## Evidence and boundaries

Public work only; no confidential code, screenshots, unpublished employer metrics, or proprietary product names. The research visual is synthetic. Project links point to the three public repositories or the thesis article.

## Checks

`tests/verify_v13.py` runs the real bundled offline HTML in Chromium at 1440×900, 390×844, and 320×640; checks all four scenes, scroll progress, project CTA routing, mobile table reflow, overflow, browser errors, and music-canvas animation. Physical Android testing is not included.
