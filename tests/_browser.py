"""Shared Playwright Chromium launcher for local verification scripts."""
from glob import glob
import os
from pathlib import Path


def launch(p, **kw):
    options = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
    options.update(kw)
    executable = os.environ.get("CHROMIUM_PATH")
    if executable:
        return p.chromium.launch(executable_path=executable, **options)

    try:
        return p.chromium.launch(**options)
    except Exception as bundled_error:
        cache = Path.home() / ".cache" / "ms-playwright"
        candidates = glob(str(cache / "chromium-*" / "chrome-linux*" / "chrome"))
        candidates = [Path(candidate) for candidate in candidates if Path(candidate).is_file()]
        if not candidates:
            raise bundled_error
        newest = max(candidates, key=lambda path: int(path.parents[1].name.removeprefix("chromium-")))
        return p.chromium.launch(executable_path=str(newest), **options)
