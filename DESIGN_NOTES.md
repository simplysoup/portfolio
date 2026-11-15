# Design notes

## V14 — Instrument

V14 organizes the portfolio as an editorial instrument panel: fine grid lines, compact mono labels, oversized condensed type, measured monochrome contrast, and restrained original dot-matrix canvas art. The home page leads with selected work — a project grid with a visible index — followed by concise experience, about, research, and contact. Full expertise, skills and experience live on the about and résumé pages.

The six projects are shown in a plain grid with a numbered project index at every width, so they can be compared without scrolling through a horizontal rail. Canvas artwork and the moving marquee are decorative and stop animating under reduced-motion preferences.

The visual reference influence is the language of monochrome condensed typography, mono labels, hairline grids, dot-matrix artwork, and numbered chapters. The reference uses Big Shoulders Display, Geist, and Geist Mono; these are self-hosted here. The hero uses an original animated torus and surrounding point field, with a static reduced-motion state and SVG fallback. Its copy and artwork occupy separate layout regions, and its viewport-aware sizing allows content to grow rather than clip on exceptionally short screens. No reference text, code, logo, or images were copied.

## Verification and content boundary

`tests/verify_v14.py` covers responsive routes, navigation and exhibits, reduced motion, print output, the offline preview, and a generated-HTML publication-safety scan. The scan is an additional safeguard, not a substitute for editorial review. No physical device testing has been performed.
