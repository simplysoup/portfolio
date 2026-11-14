# Phase 6 — verification, cleanup, docs (mechanical). Implementer: GPT-6 Luna.
Repo /home/soup/Projects/portfolio, branch redesign-v14. Read docs/redesign-v14/PROJECT_RULES.md and docs/redesign-v14/SPEC.md. Do not commit; never git checkout/restore/stash. Do not change visual design; if a check fails because of a real bug, fix it minimally and report it.

1. Delete obsolete tests (fold anything useful from tests/verify_phase5.py into verify_v14.py, then delete verify_phase5.py): tests/verify_directory.py, verify_typography_motion.py, verify_v12.py, verify_v13.py (they test the removed v10–v13 directory). Delete scripts/record_directory.py and scripts/record_scroll.py if they reference removed markup.
2. Write tests/verify_v14.py (Playwright, uses tests/_browser.py; serves dist/ itself on a free port via http.server in a thread; exits non-zero on failure; prints a PASS/FAIL table). Checks:
   a. Every route in dist/build-manifest.json at 320×640, 390×844, 768×1024, 1024×768, 1440×900, 1920×1080: HTTP 200, no console errors/pageerrors, `scrollWidth <= innerWidth`, `document.fonts.check('16px "Big Shoulders Display"')` true, no request to a non-local host.
   b. Home: hero wordmark width/shell-inner-width ∈ [0.96, 1.0] at 390/1440/1920; sections #about #work #research #contact exist; no element with text "Off the clock"; header nav aria-current updates when scrolling to each section (1440).
   c. Mobile menu at 390: opens by click and Enter, Esc closes, focus returns to the button.
   d. Work rail at 1440: html.rail-on; scroll to 0/50/100% of the rail → track transform changes monotonically, every card bounding box inside viewport height at its centered position; with reduced motion emulated → no rail-on and 6 cards in a grid. At 390 → no rail-on.
   e. Reduced motion: marquee animation-name none; canvases draw ≤1 frame after load (instrument requestAnimationFrame count over 1s ≤ 2).
   f. Contact form: fill fields, submit → `data-last-mailto` (or equivalent the implementation exposes) starts with `mailto:` and contains the encoded name.
   g. Articles: each /work/<slug>/ has h1, TOC links resolve to element ids; at 390 tables have `data-label` cells and no overflow. RAG exhibit and trend lab interact without errors.
   h. /resume/: print-emulated PDF ≤ 3 pages; body text colour is black under print media.
   i. Offline OPEN_PORTFOLIO.html (file://): home renders, clicking a case-study link swaps content, back to home works, no console errors, fonts inlined (no font requests).
   j. Publication safety: grep all dist HTML + OPEN_PORTFOLIO.html (case-insensitive) for: envision, mobilescapes, esri, 52tb, "52 tb", "customer 360", cortex, onyx, "statistics canada", "six-figure", "6-figure" → must be 0 hits.
   Save representative screenshots to screenshots/v14/final/ (home full-page at 390 and 1440, each article first viewport at 1440, resume).
3. Run: `uv run python scripts/build.py && uv run python scripts/build_preview.py && uv run --with playwright python tests/verify_v14.py`. Iterate until green or report precisely what fails and why.
4. Docs: rewrite README.md (structure, build, Tailwind pinned binary note, fonts/licences, interaction, verification command, publication-safety note, "no physical device testing performed"), replace SCROLL_SYSTEM.md content with a short description of the v14 work rail (sticky + progress, no wheel capture, reduced-motion fallback), update DESIGN_NOTES.md with a v14 section (reference influence: language borrowed, nothing copied), update AGENTS-equivalent docs/redesign-v14/PROJECT_RULES.md verification commands. Bump pyproject version to 0.14.0. Add `playwright` usage note.
Output: test table, files changed/deleted, any fixes made.
