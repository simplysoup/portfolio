# Push the reconstructed history to a private GitHub repository

1. Create a new repository on GitHub, choose **Private**, and **do not**
   initialize it with a README, license, or `.gitignore`.
2. From this folder, confirm tags are present:

   ```bash
   git log --oneline --decorate --reverse
   git tag --list
   ```

3. Push the full history (replace `<YOUR-PRIVATE-REPO-URL>`):

   ```bash
   git remote add origin <YOUR-PRIVATE-REPO-URL>
   git push -u origin main
   git push origin --tags
   ```

The username/email on the reconstructed commits intentionally describe an
archival process rather than suggesting these are your original commits.
To inspect an older version without losing your current checkout, use
`git show v07:README.md` or `git switch --detach v07`.

## Build the latest version

```bash
uv sync
uv run python scripts/build.py
uv run python scripts/build_preview.py
uv run python -m http.server 8000 --directory dist
```

The published build should be reviewed for proprietary information before
making the repository public. No reference-site bundles or internal work
notes have been included here.
