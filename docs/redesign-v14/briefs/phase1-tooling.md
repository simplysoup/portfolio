# Phase 1 — tooling (mechanical). Implementer: GPT-6 Luna.

Repo: /home/soup/Projects/portfolio, branch `redesign-v14` (already checked out). Read AGENTS.md and docs/redesign-v14/SPEC.md §0, §1, §2, §8 first.
You are the only writer right now. Do NOT commit. Do NOT edit templates/*.html or any old CSS/JS in assets/ (styles.css, world.css, world.js, scrollchapters.*, site.js). The current site must keep looking exactly as it does now after your phase.

## Tasks
1. `tailwind.config.js` at repo root — copy SPEC §2 literally.
2. `scripts/tailwind.py`:
   - Pinned `TAILWIND_VERSION = "v3.4.17"`. Map platform → asset name: linux x86_64 → `tailwindcss-linux-x64`, linux aarch64 → `tailwindcss-linux-arm64`, darwin x86_64 → `tailwindcss-macos-x64`, darwin arm64 → `tailwindcss-macos-arm64`, windows → `tailwindcss-windows-x64.exe`.
   - Binary cached at `.cache/tailwindcss-v3.4.17-<asset>` (repo root; `.cache/` is already gitignored). Download from `https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.17/<asset>` with urllib if missing; chmod +x. Env `TAILWIND_BIN` overrides the path.
   - `def compile(out_path, minify=True)` runs `<bin> -c tailwind.config.js -i assets/src/app.css -o <out_path> [--minify]` with cwd=repo root, raising a clear error on failure. Also runnable as `uv run python scripts/tailwind.py [--watch]` writing to `dist/assets/app.css`.
3. `assets/src/app.css` — `@tailwind base; @tailwind components; @tailwind utilities;` plus the `@font-face`, `@layer base` and `@layer components` exactly per SPEC §2.1–2.2 (the `.prose-nb` component can be a stub comment for now). Add the motion CSS from SPEC §7 for `[data-reveal]` and the reduced-motion resets. Font urls are relative: `url('../fonts/<file>.woff2')` (app.css is served from `/assets/app.css`, so make it `url('fonts/<file>.woff2')` relative to `/assets/` — verify the final path resolves in the built site).
4. Fonts in `assets/fonts/`: download the **latin** subset woff2 variable fonts from the Google Fonts CSS2 API using a modern Chrome User-Agent (e.g. `https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@100..900&family=Geist:wght@100..900&family=Geist+Mono:wght@100..900&display=swap`). Pick the `/* latin */` block of each family. Save as `BigShouldersDisplay-var.woff2`, `Geist-var.woff2`, `GeistMono-var.woff2`. Add `assets/fonts/LICENSE-OFL.txt` noting all three are SIL Open Font License 1.1 with their copyright holders (Big Shoulders: The Big Shoulders Project Authors; Geist/Geist Mono: Vercel). Use the families in the @font-face names exactly: "Big Shoulders Display", "Geist", "Geist Mono".
5. `content/profile.yaml` — transcribe SPEC §8 YAML verbatim as valid YAML, then add `projects:` from §8.6 (fields slug, title, tagline, year "2026", desc, chips, repo as full https URL). For evaluated-rag / analytics-pipeline / piano-transcription `desc`, copy the `description` from the matching content/work/*.md front matter. Validate it parses with PyYAML and that every string survived (watch for `#`, `:`, `—`, `[`, quotes).
6. `scripts/build.py`:
   - Load `content/profile.yaml` into a `PROFILE` dict and pass `profile=PROFILE` into every `render(...)` context.
   - After `shutil.copytree(ROOT/'assets', OUT/'assets', ignore=shutil.ignore_patterns('src'))`, call `tailwind.compile(OUT/'assets'/'app.css')` (import from scripts/tailwind.py; make the import work when run as `uv run python scripts/build.py`).
   - Keep everything else (routes, manifest, sitemap) as-is. Note: `content/drafts` may not exist — make that glob safe.
7. `scripts/build_preview.py` — make asset inlining generic instead of the hard-coded file lists:
   - Inline every local `<link rel="stylesheet" href="/…">` from `dist/` in document order into one `<style>`; inside CSS replace `url('fonts/X.woff2')`/`url(fonts/X.woff2)`/`url("…")` variants pointing at local fonts with `data:font/woff2;base64,…`.
   - Inline every local `<script src="/…">` in document order (preserve `defer` semantics by appending at end of body in order, before the router script).
   - Preserve any inline `<script>` already in `<head>` (phase 2 adds one that sets `html.js`).
   - Router: after swapping `main.innerHTML`, call `window.initSite?.()`, `window.initArt?.()`, `window.initWorld?.()`, `window.initPortfolioExhibits?.()` if defined (keep backward compatibility with the current site). Keep the existing route behaviour otherwise.
   - Inline image assets referenced as `/assets/*.png|svg` in page contents as data URIs (generalise the field-study.png special case).
8. Tests: every `tests/verify_*.py` hard-codes `executable_path='/usr/bin/chromium'`, which does not exist on this machine. Replace with a helper in `tests/_browser.py`: `def launch(p, **kw)` → uses `os.environ.get('CHROMIUM_PATH')` if set, else Playwright's default bundled chromium (`p.chromium.launch(headless=True, args=['--no-sandbox','--disable-dev-shm-usage'])`). If the bundled browser for the installed playwright version is missing, fall back to the newest `~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome`. Update all four tests to use it.

## Validation (must all pass; report output)
- `uv run python scripts/build.py` succeeds, `dist/assets/app.css` exists, is minified, contains `@font-face` with the 3 families and the classes `.shell`, `.label`, `.chip`, `.btn-solid`, `.h2-display`.
- `uv run python scripts/build_preview.py` succeeds.
- `uv run --with playwright python tests/verify_v13.py` and `tests/verify_directory.py` run (report pass/fail; failures that are pre-existing and unrelated to your change should be reported, not fixed).
- `git diff --stat` shows no changes to templates/ or old assets.

## Output
A short report: files created/changed, validation command outputs (tails), any deviation from this brief and why.
