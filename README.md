# Nicholas Bode · Work & experiments / Atelier 09

An original, art-directed personal portfolio. Ten static routes, three public code case studies, original MSc research, two synthetic interactive exhibits, and a touch-capable generative artwork. Public employer copy is general and intentionally avoids restricted product names, code, screenshots, private data and internal results.

## Setup with uv

```bash
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python -m http.server 8000 --bind 0.0.0.0 --directory dist
```

Open **http://localhost:8000** in a browser. `dist/` is fully deployable to a static host. For mobile testing, open `http://<COMPUTER_LAN_IP>:8000` from a phone connected to the same network, or publish `dist/` over HTTPS. See `MOBILE_PREVIEW.md`.

This execution environment did not have PyPI access, so **`uv.lock` could not be generated**; run `uv lock` or `uv sync` with network access before committing. The built preview and smoke tests were successfully run using preinstalled dependencies. `uv` remains the declared dependency manager for the project.

## Run interaction tests

```bash
uv sync --extra test
uv run --extra test playwright install chromium
uv run --extra test python tests/check_interactions.py
```

Automated checks cover the exact self-contained preview: desktop pointer response, autonomous sculpture, mobile touch and a genuine swipe, mobile navigation, reduced-motion behavior, article routing, no-JS fallback and a disclosure scan. The browser check uses Chromium emulation, **not a physical Android phone**.

## Site structure

- `templates/`: layouts for the home page, work index, research, articles, about/contact and résumé route
- `content/work/`: three public technical case studies
- `content/research/`: thesis article and primary academic links
- `assets/sculpture.js`: original lightweight parametric sculpture with a Canvas2D fallback
- `assets/motion.js`, `gallery.js`, `nav.js`, `scroll.js`, `studio-effects.js`: independent motion and interaction systems
- `assets/site.js`: accessible synthetic trend explorer and illustrative RAG trace explorer
- `scripts/build.py`: prerenders route HTML using Jinja, YAML and Markdown
- `scripts/build_preview.py`: creates a single-file offline preview with static fallback and in-page routing
- `tests/check_interactions.py`: browser regression tests
- `ART_DIRECTION.md`, `MOTION_SYSTEM.md`: design and implementation decisions

## Publish

```bash
SITE_URL=https://your-domain.example uv run python scripts/build.py
```

For GitHub Pages serving a repository subpath, also set `SITE_BASE=your-repo`. Upload only `dist/`; do not publish employer source material or internal draft files.

## Public content boundaries

The three featured repositories are public work by the author, separate from the employer's proprietary systems. Environics Analytics is mentioned as an employer only. The site claims neither ownership of a private team platform nor confidential business outcomes. The trend visual is an ordinary OLS illustration, not a recreation of the thesis's algorithms. The RAG trace explorer uses invented example traces and links to the actual public evaluation repository.

## Offline preview limitations

`OPEN_PORTFOLIO.html` works in a full desktop browser. Some Android in-app HTML viewers refuse to execute local JavaScript, so a bundled HTML preview is **not** a substitute for hosting the site over HTTP/HTTPS. The static homepage remains visible without JavaScript.
