# Directory 12 — shorter routes, themed index, stable piano roll

## Navigation and discovery

- The four chapters remain the conceptual structure of the site.
- The homepage now includes direct, one-step links to the evaluated RAG system, incremental analytics pipeline, Trend Dependencies thesis/lab, and solo piano transcription project.
- The full-screen INDEX directory has the same four direct links, making every showcase reachable without first navigating through a chapter.
- Each chapter now has an original, compact, monochrome technical motif directly in its index row (system graph, segmented signal, piano-roll notes, personal mark). These correspond to the chapter's existing accent color without introducing another typography family.
- The existing background interference illustration and four distinct chapter rooms remain intact.

## Music timeline rendering

- Replaced the old modulo-based piano-roll bars (which jumped or disappeared at canvas boundaries) with a deterministic cyclic score, with notes repeated into neighboring cycles to eliminate visible edge discontinuities.
- The piano-roll draws only when the music chapter is visible, resumes safely after re-entry, and resets its delta clock on entry. It no longer animates an invisible 1×1 canvas or advances time while its chapter is hidden.
- Pixel density and timeline scale respond to the visible canvas size. On narrow screens a fixed read-head, keyboard, grid, and notes remain distinct. The scene becomes static under `prefers-reduced-motion`.
- The illustration is explicitly synthetic and is **not** represented as an actual transcription result.

## Mobile fixes

- Fixed article wide-table intrinsic sizing that expanded the mobile layout viewport. This pushed the fixed INDEX button off-screen after opening a case study in the offline preview.
- Confined decorative index graphics to the visible stage so mobile full-page width remains equal to the viewport.
- Ensured the full-screen directory's fixed header switches to the directory's light surface even when opened over an article.

## Testing

The offline HTML was rendered in Chromium at 1440×900, 390×844 touch, and 320×640 touch. Regression tests cover:

- All four direct showcase links visible on the homepage and inside INDEX.
- One-tap homepage → RAG article and INDEX → piano article.
- No horizontal overflow after route transitions.
- Music canvas draws at its actual visible size, changes over time, and resumes after navigation away and back.
- No uncaught JavaScript errors in the tested flows.
- Static music illustration under reduced-motion settings.

The standalone HTML is a development preview; mobile browser file viewers may restrict JavaScript. Hosting over HTTPS remains the recommended way to verify interactions on a physical phone.

## Development

Python tools and tests use `uv`; project dependencies are declared in `pyproject.toml`. The working environment's PyPI cache is incomplete, so this iteration was built through `uv run --no-project --python /opt/pyvenv/bin/python` using preinstalled local dependencies. A lockfile has not been generated. For a regular checkout with package-index access, use `uv sync` then `uv run python scripts/build.py` and `uv run python scripts/build_preview.py`.
