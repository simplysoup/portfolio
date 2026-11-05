# Motion system — Atelier 06

The motion design is **original**. The two user-supplied site archives were examined for technique, timing, and orchestration, not used as a source of artwork, assets, or transplantable implementation code.

## Reference findings from the supplied bundles

**Christen Dijoux:** The captured production code includes GSAP 3.12.5, ScrollTrigger, Lenis, and a separate Framer Motion bundle. An observed text animation uses `yPercent:115` to `0`, `duration:1.15`, `ease:"expo.out"`, with configurable per-character staggering; one default stagger in the bundle is `0.022`. A word-opacity effect is scroll-scrubbed, and an interaction uses `elastic.out(1, 0.4)` for the magnetic return. Its procedural hero is described in the provided lab article; the separately loaded dither-hero chunk is **not** present in the saved archive, so its exact shader behavior is not independently verified here.

**Roberto Attanasio:** The saved bundle contains Motion's animation engine, spring logic, and a page-curtain implementation using `cubic-bezier(0.65, 0, 0.35, 1)`. A transition duration of 1000 milliseconds appears alongside the curtain implementation. The site combines sections of work, music, and poetry. Not every asset or production runtime interaction is reproducible from its saved archive.

## Translation into this portfolio

| Intent | Implementation | Timing |
| --- | --- | --- |
| Masked headline entrance | Native Web Animations API, three line masks | 1.23–1.45s; 105ms stagger; cubic-bezier(.16,1,.3,1) |
| Meta/intro entrance | Individually timed fade + vertical translation | 1.05s; delayed 180–960ms |
| Artwork reveal | Scale + rotation + opacity transition | 1.70s; expo-out family |
| Scroll choreography | IntersectionObserver + native WAAPI reveal | 0.85–0.95s; 125ms card offsets |
| Page transition | Fixed full-screen veil with out/in phases | 470ms + 560ms; cubic-bezier(.65,0,.35,1) |
| Fine pointer-following | Damped spring, time-step integration | Stiffness 72, damping 17 for field; 15 for arrows |
| Canvas art | Original time-varying polar point field | ~60fps mouse / ~30fps coarse touch |
| Mobile feedback | Pointer-down impulse propagating through canvas | 2.2-second damped wave, independent of hover |
| Project previews | Purposeful per-project transit/scan/phase signals | Activated by hover/focus or intersection |

The stack deliberately uses native browser animation APIs rather than importing GSAP or Motion from the reference bundles. Neither reference bundle is distributed. Using this approach keeps the portable single-file preview runnable offline without external dependencies. If the project is later migrated to a Node-bundled frontend, GSAP, ScrollTrigger, or Motion could be installed from their official distributions; the motion specifications above would still apply.

## Mobile and accessibility

- Idle field animation starts without hover. On mobile, the art appears **below**, not behind, the text; touch generates an observable impulse.
- `touch-action:pan-y` preserves ordinary page scrolling.
- The *Disturb* control is a native button with a keyboard-focus indicator and accessible label.
- `prefers-reduced-motion` freezes the canvas and prevents entrance/scroll/page animations.
- The canvas stops when it leaves the viewport, the page becomes hidden, or the route changes.
- Animation uses `requestAnimationFrame`, clamps time deltas, and limits device pixel ratio on coarse pointers.

## Validation

`tests/check_interactions.py` verifies idle animation, desktop pointer response, an actual emulated touchscreen tap, reduced motion, page transitions, the two interactive exhibits, and scroll/hover interactions. `scripts/build_preview.py` embeds all pages and the motion scripts into a portable HTML preview. Browser tests are necessary; compilation alone cannot verify motion.
