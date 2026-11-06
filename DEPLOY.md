# Publish The Directory — GitHub Pages

The repo is already public: https://github.com/simplysoup/portfolio.

This release builds the PDF from source with `scripts/generate_resume.py`, then copies it to the deployed site as `resume.pdf`. No sensitive employer material or internal performance comparison is included in the public résumé.

## One-time setup

1. In GitHub, open **Settings → Pages** for `simplysoup/portfolio`, and set **Build and deployment → Source → GitHub Actions**.
2. Make the release changes available on `main`. The workflow at `.github/workflows/publish-pages.yml` runs on every push to `main` (and also supports manual runs).
3. Watch the **Publish portfolio to GitHub Pages** workflow under **Actions**. The deployment URL will appear in the `github-pages` environment when it succeeds.
4. Check `https://simplysoup.github.io/portfolio/` and `https://simplysoup.github.io/portfolio/resume.pdf` from a phone and desktop, and test the nav and page transitions.
5. Check the social preview with the actual publicly reachable URL in a link-preview debugger; a locally generated absolute URL alone doesn't prove the preview is accessible.

## Applying this release to the current v13 checkout

Copy all source files from the release archive into the root of a clean clone of `simplysoup/portfolio`, preserving the existing `.git` directory. Then:

```sh
uv sync --frozen
uv run --with 'reportlab>=4,<5' python scripts/generate_resume.py
SITE_BASE=portfolio PUBLIC_ROOT=https://simplysoup.github.io/portfolio uv run python scripts/build.py
uv run python tests/verify_publication.py --require-resume
# Optionally remove old tracked generated artifacts:
# git rm -r --cached dist OPEN_PORTFOLIO.html

git add -A
git commit -m 'Publish public-safe portfolio with résumé and Pages workflow'
git push origin main
```

The initial source checkout tracks some generated files; the new `.gitignore` excludes fresh builds, but existing tracked files remain tracked until explicitly removed.

## Restrictions / actual status

- Local build & publication checks pass.
- GitHub rejected the assistant's create-branch request with HTTP 403 (`Resource not accessible by integration`), so this release has **not** been pushed or deployed by the assistant.
- Firefox, WebKit and physical Android testing remain outstanding until CI / actual devices run.
- The repository URL and GitHub Pages URL are distinct. The Pages URL is **not confirmed live** until the GitHub Actions workflow succeeds.
