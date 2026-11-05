# Nicholas Bode — personal portfolio / atelier 06

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

The browser checks cover autonomous animation, desktop pointer response, an emulated touchscreen tap on mobile, reduced-motion behavior, page transitions, project reveals, and both interactive exhibits. Set `BROWSER_EXECUTABLE` if you want to use a system Chromium binary instead of Playwright's own browser.

## Design notes

- **Identity:** Ink background, Paper text, Cobalt secondary accent, Signal highlights, Slate interface annotations.
- **Typography:** a large editorial sans-serif display with a single italic serif accent, understated body copy, and monospaced technical annotations. No downloaded font files.
- **Hero:** an original animated polar point field that follows a spring-driven pointer and responds to tap impulses. On small screens it is a visible, touchable stage beneath the introduction. It remains static under `prefers-reduced-motion`.
- **Architecture:** Jinja2 and MarkdownIt for prerendering, authored Markdown articles, dependency-light vanilla JavaScript for the client-side exhibits, original canvas artwork, WAAPI sequence direction, and responsive page transitions. No confidential APIs or data.
- **Ownership:** professional experience is described generically; all featured source links are independent public projects. Employer product names, internal code, and unapproved claims are excluded.

See [MOTION_SYSTEM.md](MOTION_SYSTEM.md) for the reference study, independent implementation, timing specifications, touch design, and test coverage.

## Publication

Set `SITE_URL=https://your-domain.example` when building for production. For subpath hosting, also set `SITE_BASE=repo-name`. Review content against the current public repositories before a final deployment, and add an approved resume PDF if required. Never publish employer repository code, internal tools, unpublished metrics, or confidential assets.
