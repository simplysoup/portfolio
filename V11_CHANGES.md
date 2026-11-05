# Directory 11 — typography and navigation corrections

This is a focused revision of The Directory, not a new visual concept.

- Consolidated navigation, chapter headings, project links and article headings around a single monospaced font stack. No third-party font files are included.
- Removed the special italic Georgia treatment and the oversized Arial uppercase headings.
- Increased headline line-height and allowed glyphs to extend outside previous clipping areas.
- Replaced four independently timed shutter strips with one continuous clip-path transition, using cubic-bezier(.65, 0, .35, 1).
- Fixed the animation lifecycle: each keyframe effect persists its final state before cancellation, avoiding gaps/flicker.
- Made rapid menu open/close operations reversible, with a single current animation handle.
- Fixed the menu's previous invisible state by separating its opacity from clip-path visibility.
- Removed mobile swipe-to-change-chapter (which interfered with normal touch scrolling).
- Removed the fixed mobile chapter pager (which obscured project links). Use INDEX or the chapter's back button.
- Kept reduced-motion handling and offline fallback.

## Testing

`tests/verify_typography_motion.py` checks 1440px, 390px, and 320px widths, glyph bounds, the full shutter at the page switch point, menu visibility, chapter changes, rapid menu reversal, JS errors, viewport overflow and reduced motion.

Build with `uv sync` / `uv run python scripts/build.py` / `uv run python scripts/build_preview.py`. If dependencies aren't available offline, uv will need network access to resolve them. `uv.lock` is not present.
