# Nicholas Bode's engineering portfolio

A small, static portfolio built from Markdown, Jinja templates, and plain CSS and JavaScript. Case studies live in `content/work/`; the research article is in `content/research/`. The two interactive examples run entirely in the browser on synthetic data.

## Run locally

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server --directory dist 8000
```

Open `http://localhost:8000`.

The generated site is in `dist/` and can be deployed as static files. Set `SITE_URL=https://your-actual-domain` before building for production. Set `SITE_BASE=repo-name` if hosted at a subdirectory on GitHub Pages.

## Preview

```sh
python scripts/build_preview.py
```

The preview script writes `/mnt/data/portfolio-preview.html` in this project environment. It's a self-contained HTML file with all routes and scripts bundled, intended for local review without a web server. For normal deployment, use `dist/`, not the preview file.

## Before publication

- Check all public claims against the linked repositories and thesis.
- Replace the résumé request page only when a current approved PDF exists.
- Do not commit proprietary code, screenshots, diagrams, metrics, internal system names, or unpublished case-study drafts.
- The professional case-study drafts have been deliberately kept outside this project directory to prevent accidental publication.
- Review the generated files in `dist/` before pushing to a public repository.

The site contains no API keys, tracking pixels, external JavaScript libraries, or client-side calls to private services. No deployment has been performed.
