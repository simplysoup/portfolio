# Testing on a phone

**Best experience:** serve the generated site over HTTP/HTTPS in Chrome or Firefox. Android document/file viewers may prevent locally opened HTML from running JavaScript, even when scripts are inline.

```bash
uv sync
uv run python scripts/build.py
uv run python -m http.server 8000 --bind 0.0.0.0 --directory dist
```

With both devices on the same network, open `http://YOUR_COMPUTER_LAN_IP:8000` on the phone. Allow the port through your firewall. A deployed HTTPS URL is preferable for sharing.

Touch interactions: drag or tap the ribbon, use the visible `make it move` button, horizontally swipe the project artwork, or select project numbers. The full-screen mobile menu opens from the top-right. Native vertical scrolling remains intact. The OS reduced-motion preference is honored.

The offline ZIP includes `OPEN_PORTFOLIO.html` and does not require installation for viewing the **static** content, but JavaScript-dependent interactions require a full browser that permits script execution.
