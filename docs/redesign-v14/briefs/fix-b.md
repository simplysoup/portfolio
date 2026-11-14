# Fix batch B (mechanical). Implementer: GPT-6 Luna.
Repo /home/soup/Projects/portfolio, branch redesign-v14. Read docs/redesign-v14/PROJECT_RULES.md. Do not commit. Do not run `git checkout`/`git restore` on any file.

1. OWNER DECISION: the "Off the clock" section must NOT be on the home page. Remove `{% include 'partials/offclock.html' %}` from `templates/index.html`. Include it in `templates/about.html` at the end of the content block (it will be restyled in phase 5; just make it render).
2. `content/profile.yaml` `about.body[2]`: replace the tail " Outside of work I play piano, and for five years I worked as a screen actor." with " Outside of work, I play piano." (Leave `offclock.body` untouched.) Validate YAML parses.
3. Art captions (expertise art boxes `Fig. 0x — …`, offclock caption, and any other `label absolute` caption over a canvas): add `z-10 bg-ink/80 px-1.5 py-0.5` so they stay legible over bright art.
4. `assets/js/art.js` `trend`: reserve a bottom band of 36 CSS px and a top band of 16 px where no series/labels are drawn (plot area = inset), so the `t₁`/`t₂` labels never collide with the bottom-left caption. Check at 390 and 1440.
Validation: build + preview; screenshots of the expertise rows #03 and #04 at 390 and 1440 into screenshots/v14/fix-b/; look at them; `grep -c offclock dist/index.html` must be 0 and `dist/about/index.html` must contain the offclock section; no horizontal overflow at 320/390/1440. Short report.
