# Nicholas Bode — The Directory

A navigation-led personal engineering portfolio. The homepage opens as an index for four distinct chapters, then scrolls through four full-screen featured project scenes and a closing contact chapter. The work and research articles remain static, readable deep dives.

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
- `assets/world.js` — index transitions, touch navigation, music renderer
- `assets/scrollchapters.css` and `assets/scrollchapters.js` — scroll-aware full-viewport project scenes (no scroll-jacking)
- `content/work/*.md` — publicly releasable case studies
- `content/research/*.md` — research articles
- `assets/site.js` — synthetic trend and RAG exhibits
- `scripts/build.py` — static site generator (Jinja / MarkdownIt)
- `scripts/build_preview.py` — self-contained multipage HTML generator
- `tests/verify_directory.py` — desktop + touchscreen navigation checks
- `tests/verify_v13.py` — scroll progression, short-phone CTA layout, mobile table comparisons, and music animation checks

To deploy at the root of a domain: set `SITE_URL` to your domain and run the build. For path-hosting, set `SITE_BASE` to the repository subdirectory (e.g. `SITE_BASE=my-portfolio`). Build output goes in `dist/`.

## Interaction

- From the homepage, click/tap one of the four index rows, or scroll past the hero through four full-screen project profiles. Every profile links directly to its case study.
- `INDEX` opens a full-screen directory from any page.
- On chapter screens, use `INDEX`, the keyboard arrow keys, or the close-to-index button. Horizontal swipes retain their normal scrolling behavior.
- Escape returns to the index (or closes the full-screen directory).
- All chapter and project deep links are regular anchors in the source, and navigation has a no-JS fallback.
- `prefers-reduced-motion` disables the cinematic transitions and continuous canvas animation.

## Publication safety

Only independent public-project material and sanitized professional background are included. There are no employer source files, tenant identifiers, API endpoints, private metrics, internal screenshots, or named proprietary products. No employer-owned project name appears in the published content. Case-study status and ownership are deliberately differentiated.

## Validation

The site was built and the self-contained HTML exercised in headless Chromium at 1440×900 and 390×844. The checks cover opening chapters, the directory overlay, changing chapters, returning to the index, mobile layout overflow, and JavaScript errors. The RAG and synthetic time-series exhibits were also exercised after offline route navigation.

No physical Android-device test or public deployment has been performed.

For the new full-screen scroll mechanics and mobile table layout, see [`SCROLL_SYSTEM.md`](SCROLL_SYSTEM.md).

### Responsive / cross-browser regression

The directory and sticky project scenes size to both viewport width and height.
To check short desktops, ultrawide displays and small phones:

```bash
uv sync --extra test
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python tests/verify_viewport_composition.py --browsers chromium
```

To require Chromium, Firefox and WebKit, install the Playwright browsers and run
both test scripts with `--require-all`. See [CROSS_BROWSER.md](CROSS_BROWSER.md).

## Publication checklist (unreleased)

This revision adds SEO absolute URLs and an optional approved résumé download. Generate the public-safe PDF with `python scripts/generate_resume.py` (ReportLab), or supply a reviewed `public/resume.pdf` before building. The build copies it to `/resume.pdf` and makes download links visible in the résumé and contact pages. Without an approved PDF the résumé page remains a useful experience summary and offers email contact; no broken PDF links are emitted. Do not copy employer-owned assets or an application-specific résumé containing unapproved figures into this folder.

The canonical and social URLs default to `https://simplysoup.github.io/portfolio/`. For another deployment root, set `PUBLIC_ROOT` to the full HTTPS root without a trailing slash, plus `SITE_BASE` for any subpath. For example:

```bash
SITE_BASE=portfolio PUBLIC_ROOT=https://simplysoup.github.io/portfolio uv run python scripts/build.py
```

Deployment and link-preview verification require a live HTTPS endpoint. The GitHub Pages workflow generates a public-safe PDF before building, and runs on pushes to `main` as well as manually. Configure Settings → Pages → Source: GitHub Actions once.

For publishing this release, see [DEPLOY.md](DEPLOY.md).


## AgentShield v0.1.0 case study

The public-source security evaluation case study is at `/work/agent-shield/` and is linked first from the homepage and Work index. It uses the verified public `v0.1.0` tag and documents the one-case 20B comparison without conflating model refusal with runtime policy denial. The figure is a labeled reconstruction of observed results, not a raw execution log. The PDF résumé includes a concise independent-project entry.

The upstream AgentShield repository is public but its README currently states that no license has been granted; avoid calling it permissively licensed or reusable until the repository has an explicit license.
