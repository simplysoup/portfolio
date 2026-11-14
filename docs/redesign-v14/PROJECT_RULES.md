# Project rules (mirror of the owner's AGENTS.md guidance — read this instead of AGENTS.md)

- Static personal portfolio: Python 3.11+, Jinja2, Markdown-It, PyYAML, Beautiful Soup; HTML, CSS (Tailwind v3 standalone), vanilla JS; deps via `uv`.
- `templates/` Jinja pages; `content/work/`, `content/research/` Markdown + YAML front matter; `assets/` source CSS/JS/images; `scripts/build.py` → `dist/`; `scripts/build_preview.py` → `OPEN_PORTFOLIO.html` (self-contained offline preview); `tests/` Playwright checks.
- Keep changes scoped; no new dependencies or frontend frameworks.
- Preserve semantic links/controls, keyboard and touch navigation, reduced-motion behaviour, native scroll. No scroll locking, no scroll-jacking.
- Published content: only independent public-project material and sanitized professional background. No confidential code, internal product names, private metrics, proprietary details (see SPEC §9).
- `dist/` and `OPEN_PORTFOLIO.html` are generated: change sources and rebuild, never hand-edit.
- Build: `uv run python scripts/build.py && uv run python scripts/build_preview.py`; preview `uv run python -m http.server 8000 --directory dist`.
- Browser checks: Playwright via `tests/_browser.py` launch helper. Report checks that could not run; never claim physical-device testing.
