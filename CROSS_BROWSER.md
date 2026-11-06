# Directory 13 — Browser compatibility validation

## What this checks

`tests/verify_cross_browser.py` executes the complete `OPEN_PORTFOLIO.html` bundle
in Chromium, Firefox and Playwright WebKit at 1920×1080, 1440×900, 820×1180, 390×844 and 320×640.
It checks:

- four project chapters, sticky-layout behavior, chapter links and responsive overflow;
- scrolling updates project `--progress` CSS state;
- article navigation and responsive comparison tables;
- reduced-motion disables home-page scroll snapping;
- canvas MIDI rendering changes over time;
- uncaught JavaScript errors;
- recorded engine support for CSS `:has`, `svh`, `clip-path`, `color-mix`, scroll snap and Web Animations.

All four projects receive structural and responsive-layout checks. The RAG
chapter receives a **300px synthetic wheel gesture** at each viewport to measure
scroll-progress response and post-gesture settling efficiently. A synthetic wheel test
is not equivalent to real touch inertia or native trackpad feel. The report
never claims to validate physical Safari or mobile Firefox touch scrolling.

## Local setup

```sh
uv sync --extra test
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run playwright install --with-deps chromium firefox webkit
uv run python tests/verify_cross_browser.py --require-all
```

If Firefox/WebKit downloads are blocked, running without `--require-all` writes
`SKIP` rather than counting those engines as passed. The report is
`cross-browser-report.json`.

The included `.github/workflows/cross-browser.yml` runs the three-engine test
in GitHub Actions whenever the workflow is committed and changes are pushed,
on pull requests, or manually via Actions → Portfolio browser compatibility → Run workflow. Download the
`directory-cross-browser-report` artifact for engine-by-engine results.

## Browser-engine scope

- Chromium: Chromium/Chrome engine on desktop and emulated mobile.
- Firefox: Firefox engine at desktop and narrow responsive viewports; Playwright
  doesn't emulate Firefox mobile's native input in the same way.
- WebKit: Safari's core web engine on Linux, **not** Apple's full Safari browser.

For final release, test Safari on a physical iPhone and macOS Safari because
mobile scroll momentum, toolbar-driven viewport resizing, font rendering and
GPU compositing may differ from Playwright WebKit.

## Diagnosis from local Chromium run (5 November 2026)

At a 300px wheel input, project scroll progress advanced by approximately:

| Viewport | Scroll hold (track minus viewport) | Progress change |
|---|---:|---:|
| Wide desktop 1920×1080 | 583px | 0.51 |
| Desktop 1440×900 | 486px | 0.62 |
| Tablet 820×1180 | 590px | 0.51 |
| Phone 390×844 | 354px | 0.85 |
| Short phone 320×640 | 269px | ~1.00 |

This illustrates how the **same physical scroll distance consumes more of a
project chapter on smaller screens**. It is consistent with the reported
mobile-fast/desktop-slow imbalance, without establishing real-phone inertial
jitter. Native `scroll-snap-type: y proximity` is another plausible source
of abrupt mobile settling; it deserves a touch-device A/B comparison.

The tests intentionally do **not** change the scroll design. The matrix
completed in local Chromium at all five sizes; Firefox and WebKit were **not
run locally** because their browser binaries were unavailable. A CI run is
required before claiming those engines pass. A subsequent
calibration can adjust the track's hold distance by viewport and evaluate
whether scroll snapping should be disabled below the mobile breakpoint.

## Viewport composition regression (short desktop / unusual aspect ratios)

`tests/verify_viewport_composition.py` checks the index, all four showcase
screens, links and artwork at fourteen representative aspect ratios, including
2560×700, 1600×600, 1280×550, 1024×600, 768×480 and 320×480.
Unlike a horizontal-overflow-only check, it compares actual DOM rectangles to
catch vertical clipping, links overlapping artwork and artwork overlapping the
footer. This runs across Chromium, Firefox and WebKit in the same CI workflow.

```sh
uv run python tests/verify_viewport_composition.py --require-all
```

At desktop/laptop sizes, each sticky scene is exactly one viewport high. On
extremely short portrait screens (up to 540px tall), scenes deliberately flow
vertically rather than overlap legible text and artwork. The directory behaves
similarly below 520px. This fallback is an intentional content flow, not clipped
canvas. Browser zoom, dynamic Safari toolbar changes and physical-device touch
momentum still merit human checks.
