# Nicholas Bode — Personal Portfolio (Atelier prototype)

A personal engineering portfolio with an original procedural illustration, work/research pages, and two lightweight technical exhibits. It uses a dark Ink / Paper / Cobalt / Signal / Slate palette. The top of the homepage introduces Nicholas as a person; current employment is visible immediately below the hero, rather than being the hero.

## Local build

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8000 --directory dist
```

Then open `http://localhost:8000`. For a single HTML file you can inspect offline, run `python scripts/build_preview.py` and open `portfolio-preview.html` directly from your browser. The preview embeds its CSS, JavaScript, page content, and hero illustration.

## Deployment

The distributable is the generated `dist/` directory. Set `SITE_URL=https://your-domain.example` when building for real canonical links and sitemap generation. For a GitHub Pages subpath, also set `SITE_BASE=repo-name`. No APIs, keys, server processes, or image-hosting account are required.

## Design and content

- Homepage: personal introduction, subtle pointer-reactive signal-field illustration, visible professional background, three public-code projects, original research, and contact.
- `/work/`: individually documented public projects and code links.
- `/research/`: thesis, published reference entry, and synthetic interactive explanation.
- The reference bundle was inspected for design principles only. The artwork, CSS, code, and interactions here were created separately.
- Synthetic examples in the RAG and time-series exhibits are visibly labeled and are not employer assets.
- No proprietary product names, internal source code, client data, tenant IDs, unpublished metrics, or private case-study drafts are included.

## Publication checklist

- Verify article details and links against the current public repositories.
- Add a current résumé PDF only after approving the version intended for public access.
- Replace the placeholder domain with the final deployment URL and test on a real browser/device.
- Check responsive layout, reduced motion, keyboard navigation, and the static build on the final host.

This is a design prototype; not yet deployed publicly.
