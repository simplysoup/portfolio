# Nicholas Bode — personal portfolio / Atelier 07

Dark editorial portfolio with an original generative field, motion-directed project index, research writing, and two synthetic exhibits. This is a **static website**; no backend or employer assets are included.

## Build and run using `uv`

```sh
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python -m http.server 8000 --directory dist
```

Open `http://localhost:8000` on your computer. For a phone on the same Wi-Fi network, use `http://YOUR_COMPUTER_LAN_IP:8000` (and allow the connection through your firewall). **Serving the site over HTTP is the recommended way to test interactions on a real phone.** You can also deploy `dist/` to any static host.

`portfolio-preview.html` is a single-file route preview. It contains no external scripts or CSS. On desktop, open it in a full browser. **Android file-manager and in-app HTML viewers can disable JavaScript, so opening the HTML directly on a phone is not a reliable interactive test.** When script execution is blocked, the preview now shows a readable homepage and warning instead of an empty page. To test interactions, serve the real site over HTTP as above.

`uv.lock` is not included because the working environment could not reach the package registry; do not interpret the lack of a lockfile as a successful resolution. Run `uv lock` in a normal networked environment.

## Motion specification

The original visual language remains Paper / Ink / Cobalt / Signal / Slate. Animation principles are drawn from **both user-supplied site bundles**, but all code, visuals and words in the portfolio were implemented independently:

- Masked, staggered headline lines: exponential-out style cubic `(.16,1,.3,1)` and approximately 100 ms offsets.
- Cinematic project-switch curtain: cubic `(.65,0,.35,1)` with a coordinated outgoing text, scene change and incoming text; not a simple opacity fade.
- A new full-size project gallery: three original SVG artworks with trace movement, state transitions, and audio-to-notation timing. Prev/next buttons, numbered tabs, arrow keys, and horizontal swipes all work.
- Mobile navigation as a full-screen typographic curtain with focus management and escape close.
- Generative canvas field: idle animation, spring-following on desktop, and a large, visible ripple on tap or button input on mobile.
- Scroll-synchronized motion on research artwork and project scene; no scroll-jacking.
- Reduced-motion support across entrances, gallery, menu, canvas and page transitions.

See [MOTION_SYSTEM.md](MOTION_SYSTEM.md) for the measured easing curves, interaction details, and reference interpretation.

## Test the *distributable HTML*

```sh
uv sync --extra test
uv run --extra test playwright install chromium
uv run --extra test python tests/check_interactions.py
```

The tests use the packaged HTML bytes and emulate a touchscreen tap and a genuine Chromium touch-swipe, as well as mobile navigation, links, keyboard/reduced motion, and the no-script fallback. The test environment forbids direct automation of `file://` and `http://localhost` navigation, so tests inject the **same HTML bytes** into Chromium; they do not assert that Android's external file viewers run JavaScript. Physical-device testing via HTTP remains necessary.

## Publish responsibly

Public case studies link to independently owned GitHub projects. The employer description is deliberately high-level; the proprietary product name, unreleasable metrics, internal tooling and unapproved architecture are excluded. Do not add any employer screenshot, client data, or internal code without approval.

To deploy at the domain root:

```sh
SITE_URL=https://your-domain.example uv run python scripts/build.py
```

For GitHub Pages project-subpath hosting, additionally set `SITE_BASE=repository-name`. Publish only `dist/`.
