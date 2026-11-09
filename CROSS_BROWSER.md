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
chapter receives a **300px programmatic scroll** (`window.scrollBy(0, 300)`)
at each viewport to measure scroll-progress response and post-scroll settling
efficiently. A programmatic scroll test is not equivalent to real touch
inertia or native trackpad feel. The report never claims to validate physical
Safari or mobile Firefox touch scrolling.

It used to be a synthetic mouse-wheel gesture, changed 2026-11-08 after the
v14 CI run failed WebKit-only for test-harness reasons, not site reasons
(see below): `mouse.wheel` throws on mobile WebKit, and on desktop WebKit
the wheel scroll is delayed and then snap-forwarded to the next chapter, so
it never measures a 300px scroll there. The page listens for scroll events,
not wheel events, so `scrollBy` exercises exactly the code under test and
lands at +300px in every engine, mobile included.

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

At a 300px scroll input, project scroll progress advanced by approximately:

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

## Diagnosis from the v14 CI failure (7 November 2026, fixed 8 November)

The v14 release branch failed CI WebKit-only, 15/18: Chromium 6/6, Firefox
6/6, WebKit 3/6. The three WebKit failures were all in the scroll-progress
check, and none was a site bug. Reproduced locally in Playwright WebKit
1.64.1 / WebKit 27.2:

- **Phone and short-phone:** `mouse.wheel` throws outright — mouse-wheel
  input is not supported in mobile WebKit.
- **Wide desktop (1920×1080):** the wheel scroll is delayed, then
  `scroll-snap-type: y proximity` snaps forward to the next chapter, so
  progress jumps to 1.0 instead of ~0.51 — or, on a loaded CI runner, the
  wheel has not moved anything yet at the 320ms read, giving 0.0 -> 0.0.
  The same race showed up intermittently at 1440×900 locally (still 0.0 at
  100ms after the wheel, 1.0 by 320ms).
- **The site itself is fine in WebKit:** `window.scrollBy(0, 300)` lands at
  exactly +300px at all five viewports, with progress 0.51 / 0.62 / 0.51 /
  0.85 / ~1.00 — matching the Chromium wheel numbers in the table above.

Fix: the scroll check now uses `window.scrollBy(0, 300)` in all engines,
and polls briefly for the progress update instead of trusting a single
320ms read on a loaded runner. No site CSS or JS changed.

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

## Diagnosis from the v14 composition failures (8 November 2026)

Once the cross-browser check above went green, this step was the next red
one locally (it never ran in the 7 November CI, because the workflow stops
at the first failing step). Two separate causes, both reproduced locally:

- **WebKit "artwork overlaps footer" on the RAG scene, several viewports:**
  test timing, not layout. The check measured 35ms after `scrollIntoView`,
  while WebKit was still animating the scroll-snap settle, with `--entry`
  near 0 — and `--entry` translates the artwork down by up to 88px, so it
  read as overlapping the footer. By 100–300ms `--entry` reaches 1.0 and
  the artwork sits 12–55px clear of the footer. Fix: the check now waits
  for `--entry` to reach 1 before measuring geometry. No site change.
- **Horizontal overflow at 320×480 in Firefox and WebKit:** a real site
  bug. The short-height rules in `assets/world.css` set
  `.directory-stage{overflow:visible}`, which also un-clipped the decorative
  directory-art canvas (140% wide, `right: -43%` at narrow widths), enlarging
  the layout viewport to 474px. Chromium's mobile emulation masked it by
  reporting `innerWidth` as 474. Fix: those rules now use
  `overflow-x:hidden;overflow-y:auto` — vertical flow is unchanged (the
  stage is `height:auto`, so there is nothing to scroll inside it), and the
  art stays inside the index, as the existing "Decorative art stays inside
  the narrow index" rule intends.
