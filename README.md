# Nicholas Bode — personal portfolio / atelier 05

A dark, editorial engineering portfolio with original interactive signal-point artwork, curated public case studies, a research article, and two synthetic technical exhibits. This is a static site: the built output requires no database, Python runtime or JavaScript bundler in production.

## Build with `uv`

Install [uv](https://docs.astral.sh/uv/) first, then run:

```sh
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
```

`dist/` is the deployable static site. `portfolio-preview.html` is a single-file, offline preview (all 10 routes embedded); open it directly in a browser. No local server is needed for the preview.

For normal local development:

```sh
uv run python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. When content or assets change, rerun `uv run python scripts/build.py`.

A lockfile can be generated with `uv lock` when PyPI is reachable. This project has a `pyproject.toml` as the dependency source of truth. The build environment used for this deliverable had PyPI network access blocked, so no generated lockfile is represented as verified.

## Browser regression checks

```sh
uv sync --extra test
uv run --extra test playwright install chromium
uv run --extra test python tests/check_interactions.py
```

The test checks real canvas pixel changes after pointer movement on desktop and narrow layouts, reduced-motion behavior, client-side navigation within the offline preview, and technical exhibit initialization. Set `BROWSER_EXECUTABLE` if you want to use a system Chromium binary instead of Playwright's own browser.

## Design notes

- **Identity:** Ink background, Paper text, Cobalt secondary accent, Signal highlights, Slate interface annotations.
- **Typography:** a large editorial sans-serif display with a single italic serif accent, understated body copy, and monospaced technical annotations. No downloaded font files.
- **Hero:** the point-based polar signal artwork from Atelier 03, now with visible pointer-responsive deformation. Pointer handling lives on the hero so the non-interactive decorative canvas cannot intercept input. Static under `prefers-reduced-motion`.
- **Architecture:** Jinja2 and MarkdownIt for prerendering, authored Markdown articles, dependency-light vanilla JS for the client-side exhibits and artwork. No confidential APIs or data.
- **Ownership:** professional experience is described generically; all featured source links are independent public projects. Employer product names, internal code, and unapproved claims are excluded.

## Publication

Set `SITE_URL=https://your-domain.example` when building for production. For subpath hosting, also set `SITE_BASE=repo-name`. Review content against the current public repositories before a final deployment, and add an approved resume PDF if required. Never publish employer repository code, internal tools, unpublished metrics, or confidential assets.
