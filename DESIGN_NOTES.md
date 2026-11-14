# Design notes

## V14 — Instrument

V14 organizes the portfolio as an editorial instrument panel: fine grid lines, compact mono labels, oversized condensed type, measured monochrome contrast, and restrained original dot-matrix canvas art. Home sections present professional background, expertise, skills, experience, selected work, research, and contact in a direct reading flow.

The work rail is a sticky viewport driven by native scroll progress. It does not capture wheel or touch input. Mobile and reduced-motion users receive the same six projects in a vertical grid. Canvas artwork and the moving marquee are decorative and stop animating under reduced-motion preferences.

The visual reference influence is the language of monochrome condensed typography, mono labels, hairline grids, dot-matrix artwork, and numbered chapters. That language was borrowed as inspiration; no reference text, code, logo, or images were copied. All portfolio copy, artwork, and implementation are original.

## Verification and content boundary

`tests/verify_v14.py` covers responsive routes, navigation and exhibits, reduced motion, print output, the offline preview, and a generated-HTML publication-safety scan. The scan is an additional safeguard, not a substitute for editorial review. No physical device testing has been performed.
