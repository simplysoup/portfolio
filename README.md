# Nicholas Bode — Portfolio

A static portfolio for independent AI engineering, data systems, research, and selected public projects. The v14 “Instrument” design uses a typographic grid, restrained monochrome styling, original canvas illustrations, and a native-scroll work rail.

## Build and preview

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. `dist/` is the generated static site. `OPEN_PORTFOLIO.html` is a self-contained offline preview with route content and fonts embedded. Both are generated artifacts; make changes in source files and rebuild.

The build uses the standalone Tailwind CSS CLI **v3.4.17**, pinned by `scripts/tailwind.py`. Its platform-specific binary is stored in `.cache/` and downloaded on demand; it is not an npm dependency. `TAILWIND_BIN` may point to an existing compatible CLI binary.

## Structure

- `templates/` — Jinja page layouts and home-page sections
- `content/profile.yaml` — portfolio content and home-page data
- `content/work/*.md`, `content/research/*.md` — articles and case studies
- `assets/src/app.css` — Tailwind input and component styles
- `assets/fonts/` — self-hosted Big Shoulders Display, Geist, and Geist Mono variable fonts
- `assets/js/main.js`, `assets/js/art.js`, `assets/site.js` — progressive enhancement, canvas art, and interactive exhibits
- `scripts/build.py` — builds `dist/` and its route manifest
- `scripts/build_preview.py` — creates `OPEN_PORTFOLIO.html`
- `tests/verify_v14.py` — browser verification for production routes and offline preview

The included Big Shoulders Display font is copyright The Big Shoulders Project Authors; Geist and Geist Mono are copyright Vercel. All three are distributed under the SIL Open Font License 1.1; the license and notices are in `assets/fonts/LICENSE-OFL.txt`.

## Interaction and accessibility

Navigation uses ordinary links and native scrolling. The work rail is sticky and progress-driven on wide screens, with no wheel interception; reduced-motion and small-screen modes show a vertical project list. The mobile menu supports keyboard operation and restores focus when closed. Decorative animation respects `prefers-reduced-motion`, and content remains available as static HTML.

RAG and trend-lab examples are synthetic, client-side exhibits. Contact form submission creates a `mailto:` link; it does not send information to a server.

## Verification

Install the optional browser test dependency and run the complete build and verification sequence:

```bash
uv sync --extra test
uv run python scripts/build.py && uv run python scripts/build_preview.py && uv run --with playwright python tests/verify_v14.py
```

The verifier starts its own local HTTP server, tests all generated routes at the project viewport sizes, exercises key interactions and print layout in Chromium, scans generated HTML for publication-safety phrases, and writes representative screenshots to `screenshots/v14/final/`. Playwright is used only for this local automated browser verification; `tests/_browser.py` selects an installed Chromium browser or falls back to Playwright's bundled browser.

## Publication safety

Published material is limited to independent public-project work and sanitized professional background. Generated HTML is checked for disallowed names, metrics, and phrases before release. This automated text scan does not replace a human publication review. No physical device testing has been performed.
