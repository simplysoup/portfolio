# Nicholas Bode's engineering portfolio

A dark, static portfolio built from Markdown, Jinja templates, and plain CSS and JavaScript. The visual system uses Ink (`#17242B`), Paper (`#F5F3EC`), Cobalt (`#405BCB`), Signal (`#D9EF8B`), and Slate (`#77817E`). The opening homepage section leads with the current AI Engineer role at Environics Analytics, followed by a sanitized professional summary, public projects, and research. Case studies live in `content/work/`; the research article is in `content/research/`. The two interactive examples run entirely in the browser on synthetic data.

## Run locally

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server --directory dist 8000
```

Open `http://localhost:8000`.

The generated site is in `dist/` and can be deployed as static files. The portable preview can also be opened offline from `OPEN_PORTFOLIO.html` in the separately packaged preview ZIP. Set `SITE_URL=https://your-actual-domain` before building for production. Set `SITE_BASE=repo-name` if hosted at a subdirectory on GitHub Pages.

## Preview

```sh
python scripts/build_preview.py
```

The preview script writes `portfolio-preview.html` at the project root. It's a self-contained HTML file with all routes and scripts bundled, intended for local review without a web server. For normal deployment, use `dist/`, not the preview file.

## Before publication

- Check all public claims against the linked repositories and thesis.
- Replace the résumé request page only when a current approved PDF exists.
- Do not commit proprietary code, screenshots, diagrams, metrics, internal system names, or unpublished case-study drafts.
- The professional case-study drafts have been deliberately kept outside this project directory to prevent accidental publication.
- Review the generated files in `dist/` before pushing to a public repository.

The site contains no API keys, tracking pixels, external JavaScript libraries, or client-side calls to private services. No deployment has been performed.
