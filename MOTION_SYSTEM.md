# Motion system / Atelier 09

## Observed in the user-provided reference archives

Christen Dijoux: GSAP 3.12.5, ScrollTrigger and Lenis; character entrances with `expo.out`, about 1.15 s duration and ~22 ms per-character stagger; pointer proximity effects; scroll-linked typography and kinetic text. Roberto Attanasio: a Motion/Framer Motion system with spring-based motion and a full-screen transition using `cubic-bezier(.65, 0, .35, 1)` over approximately one second. The actual live websites were not capturable from this environment; these observations derive from the supplied archived assets and code.

## Independent implementation

- Main masked type: `cubic-bezier(.16,1,.3,1)` with 105 ms line delay; 1230–1450 ms line entrance.
- Gallery switch: 250 ms outgoing, 390 ms curtain in, 520 ms curtain out, 810 ms staggered copy arrival, 1050 ms art arrival; curtain `cubic-bezier(.65,0,.35,1)`.
- Route veil: 470 ms coverage then 560 ms exit via symmetric curve. Full mobile menu: 670 ms open, 560 ms close, 85 ms stagger.
- Kinetic type: velocity-coupled movement with exponential decay and no interception of wheel/touch scrolling.
- Sculpture: original folded ribbon. Vertex-shaded WebGL2 when available, with a Canvas2D printed-ribbon fallback (30 fps cap, paused out of view). Pointer and touch influence orientation and impulse. Both renderers are independent artwork created for this portfolio, not reproductions of a reference shader.
- Mobile project art: touch swipes, taps and visible buttons. Navigation remains functional without motion.
- Reduced motion: freeze time-dependent sculpture movement and skip entrance and gallery transitions.

These primitives are synchronized around scene entry/exit, rather than independently animating arbitrary elements. The purpose of each effect is visual continuity or an understandable response to input.

## Verification

`tests/check_interactions.py` runs browser-emulated real pointer and touch input against the actual single-file preview bytes. Confirmed: canvas render and autonomous motion, tap wave, swipe, gallery state changes, mobile index, article routing, reduced-motion and no-script fallback. Directly viewing `.html` inside an Android file manager may block JavaScript; serve `dist/` over HTTP/HTTPS for device verification. No physical Android-device test is claimed.
