# Preview on mobile

**Preferred:** host the generated `dist/` directory over HTTP or HTTPS. Android's HTML/file viewers do not consistently allow JavaScript when opening standalone files, even if the HTML is self-contained. This cannot be fixed by changing the site's event listeners alone.

For a laptop and phone on the same Wi-Fi:

1. Extract the source ZIP and change into `nicholas-bode-portfolio/`.
2. Run `uv sync` and `uv run python scripts/build.py` (if you do not want to rebuild, `dist/` is already included).
3. Run `uv run python -m http.server 8000 --bind 0.0.0.0 --directory dist`.
4. Find the laptop's LAN IP. On your phone open `http://<LAPTOP_IP>:8000` in Chrome or Firefox (allow the port through your firewall).

The standalone `OPEN_PORTFOLIO.html` is useful for desktop offline viewing. On mobile, choose a full browser if your file manager offers **Open with**; if your viewer disables scripts, you will see the static homepage and a notice, but not motion. The website must be loaded by a JavaScript-enabled browser to run the interactions.

### Touch controls

- **Hero field:** tap the drawing, or its **Send a ripple** control. A visible ring should expand from the contact point.
- **Selected work:** tap a project number; tap the artwork to advance; swipe horizontally to change projects. The arrow buttons always work.
- **Navigation:** tap **Menu**. The full-screen index animates in. Tap a destination or press Escape on a connected keyboard.
- **Accessibility:** system reduced-motion settings disable non-essential motion.
