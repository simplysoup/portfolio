# Nicholas Bode — The Directory

A navigation-led personal engineering portfolio. The homepage is the index: four distinct chapters for systems, research, music, and background, plus direct links to the four featured showcases. The work and research articles remain static, readable deep dives.

## Build

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
```

Preview the production output with a local HTTP server:

```bash
uv run python -m http.server 8000 --directory dist
```

Open `http://localhost:8000` in a browser. For mobile testing, open the equivalent local-network address on your phone. Hosting via HTTPS is strongly recommended for reliable mobile navigation and canvas interaction.

`OPEN_PORTFOLIO.html` is a self-contained offline preview with embedded CSS, JavaScript, and route content. Opening it from a restricted file viewer on Android may prevent scripts from running, despite the static page being visible.

## Structure

- `templates/index.html` — the four-part index and scenes
- `templates/base.html` — global directory and page chrome
- `assets/world.css` — site art direction and transition styling
- `assets/world.js` — index transitions, touch navigation, graphic engines
- `content/work/*.md` — publicly releasable case studies
- `content/research/*.md` — research articles
- `assets/site.js` — synthetic trend and RAG exhibits
- `scripts/build.py` — static site generator (Jinja / MarkdownIt)
- `scripts/build_preview.py` — self-contained multipage HTML generator
- `tests/verify_directory.py` — desktop + touchscreen navigation checks

To deploy at the root of a domain: set `SITE_URL` to your domain and run the build. For path-hosting, set `SITE_BASE` to the repository subdirectory (e.g. `SITE_BASE=my-portfolio`). Build output goes in `dist/`.

## Interaction

- From the homepage, click or tap a chapter row to enter its room, **or choose a project in SELECTED WORK to open its case study in one step**.
- `INDEX` opens a full-screen directory from any page. Its project shortcuts also link directly to the featured case studies.
- On chapter screens, use the numeric pager, the chapter's `INDEX` button, the keyboard arrow keys, or horizontal swipe gestures.
- Escape returns to the index (or closes the full-screen directory).
- All chapter and project deep links are regular anchors in the source, and navigation has a no-JS fallback.
- `prefers-reduced-motion` disables the cinematic transitions and continuous canvas animation.

## Publication safety

Only independent public-project material and sanitized professional background are included. There are no employer source files, tenant identifiers, API endpoints, private metrics, internal screenshots, or named proprietary products. No employer-owned project name appears in the published content. Case-study status and ownership are deliberately differentiated.

## Validation

The site was built and the self-contained HTML exercised in headless Chromium at 1440×900 and 390×844. The checks cover opening chapters, direct one-tap showcase routes, the directory overlay, changing chapters, returning to the index, stable MIDI canvas rendering, mobile layout overflow, and JavaScript errors. The RAG and synthetic time-series exhibits were also exercised after offline route navigation.

No physical Android-device test or public deployment has been performed.

See `V12_CHANGES.md` for the routing, design and piano-roll improvements.
