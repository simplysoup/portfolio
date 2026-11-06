# Directory v14 — hiring-funnel review candidate

Based on v13 and the separate responsive fix, with no public deployment and no résumé revisions.

## Implemented

- Homepage now opens with secure AI integrations, model evaluation, and data-quality research while retaining a personal voice.
- Four clickable work links appear before the four-door index and before the animated chapters. The first opens a brief professional overview; the other three lead to independent work and research.
- The work and About pages now summarize independently owned authorization and evaluation work, a tested but undeployed OAuth2/PKCE remote service, and distinct team contributions. No proprietary product name or implementation details are included.
- Contact includes Toronto, Canada and openness to AI/applied-ML/research engineering conversations.
- `/resume/` contains a useful employment overview and direct email link. The build exposes `/resume.pdf` download links **only if** an approved PDF is added at `public/resume.pdf`.
- Canonical, `og:url`, `og:image`, and `twitter:image` point to absolute HTTPS URLs configured by `PUBLIC_ROOT`. The Open Graph cover is 1200×630.
- `tests/verify_publication.py` checks publication metadata, professional positioning, links, and the PDF gate.
- A **manually dispatched** GitHub Pages workflow refuses to deploy without an approved public résumé.
- The responsive viewport test was updated to enforce the reordered homepage geometry.

## Release blockers / remaining work

1. **Approval and inclusion of a general-purpose public résumé PDF**. A previously available application-specific PDF was intentionally excluded because it includes an internal metric not cleared for publication.
2. **Enable GitHub Pages and run the manual publishing workflow** after approving the PDF and site copy.
3. **Verify social link previews on the live HTTPS URL**. Static HTML tests pass, but live fetching by social crawlers has not happened.
4. **Test a physical phone** on the deployed site. Headless Chromium tests cannot reproduce device-specific scroll physics.
5. **Cross-browser CI execution** for Firefox and WebKit is pending. Their browser binaries were unavailable locally.
6. **Optional later enhancements:** real publicly releasable RAG traces, a synthetic secure-tool demo, held-out RAG datasets and repeated evaluation runs.

## Commands

```sh
uv sync --extra test
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python tests/verify_publication.py
uv run python tests/verify_viewport_composition.py --browsers chromium
uv run python tests/verify_cross_browser.py --browsers chromium
```

To simulate the GitHub Pages build locally:

```sh
SITE_BASE=portfolio PUBLIC_ROOT=https://simplysoup.github.io/portfolio uv run python scripts/build.py
```

To publish, first add `public/resume.pdf` (only after approval), push changes to `main`, enable Pages using GitHub Actions as the source, then manually run **Publish portfolio to GitHub Pages**.
