#!/usr/bin/env python3
"""Download the pinned standalone Tailwind CLI and compile the portfolio CSS."""
from pathlib import Path
import argparse
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TAILWIND_VERSION = "v3.4.17"
RELEASE_URL = f"https://github.com/tailwindlabs/tailwindcss/releases/download/{TAILWIND_VERSION}"


def asset_name(system=None, machine=None):
    system = (system or platform.system()).lower()
    machine = (machine or platform.machine()).lower()
    if system == "linux":
        if machine in ("x86_64", "amd64"):
            return "tailwindcss-linux-x64"
        if machine in ("aarch64", "arm64"):
            return "tailwindcss-linux-arm64"
    elif system == "darwin":
        if machine in ("x86_64", "amd64"):
            return "tailwindcss-macos-x64"
        if machine in ("arm64", "aarch64"):
            return "tailwindcss-macos-arm64"
    elif system in ("windows", "win32"):
        return "tailwindcss-windows-x64.exe"
    raise RuntimeError(f"Unsupported Tailwind platform: {system} {machine}")


def binary_path():
    override = os.environ.get("TAILWIND_BIN")
    if override:
        path = Path(override).expanduser()
        if not path.is_file():
            raise RuntimeError(f"TAILWIND_BIN does not point to a file: {path}")
        return path
    asset = asset_name()
    path = ROOT / ".cache" / f"tailwindcss-{TAILWIND_VERSION}-{asset}"
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"{RELEASE_URL}/{asset}"
        temporary = path.with_suffix(path.suffix + ".download")
        try:
            urllib.request.urlretrieve(url, temporary)
            temporary.replace(path)
        except (OSError, urllib.error.URLError) as exc:
            temporary.unlink(missing_ok=True)
            raise RuntimeError(f"Could not download Tailwind CLI {TAILWIND_VERSION} from {url}: {exc}") from exc
    if os.name != "nt":
        path.chmod(path.stat().st_mode | 0o111)
    return path


def _compile(out_path, minify=True, watch=False):
    executable = binary_path()
    output = Path(out_path)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [str(executable), "-c", "tailwind.config.js", "-i", "assets/src/app.css", "-o", str(output)]
    if minify:
        command.append("--minify")
    if watch:
        command.append("--watch")
    try:
        subprocess.run(command, cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Tailwind CSS compilation failed (exit {exc.returncode}): {' '.join(command)}") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not run Tailwind CLI at {executable}: {exc}") from exc


def compile(out_path, minify=True):
    """Compile assets/src/app.css to out_path, raising a useful error on failure."""
    _compile(out_path, minify=minify)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true", help="rebuild dist/assets/app.css on changes")
    args = parser.parse_args(argv)
    try:
        _compile(Path("dist/assets/app.css"), minify=True, watch=args.watch)
    except RuntimeError as exc:
        print(f"tailwind: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
