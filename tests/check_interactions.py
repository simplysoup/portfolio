#!/usr/bin/env python3
"""Regression checks against the portable, offline portfolio preview.

uv run --extra test python tests/check_interactions.py
uv run --extra test playwright install chromium  # first time only
"""
from pathlib import Path
import os
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "portfolio-preview.html"
if not PREVIEW.exists():
    raise SystemExit("Run `uv run python scripts/build_preview.py` first")


def launch(p):
    supplied = os.environ.get("BROWSER_EXECUTABLE")
    path = supplied or shutil.which("chromium") or shutil.which("google-chrome")
    return p.chromium.launch(headless=True, executable_path=path if path else None,
                             args=["--no-sandbox"])


def page_with_preview(browser, *, width=1400, height=900, reduced=False):
    page = browser.new_page(viewport={"width": width, "height": height})
    if reduced:
        page.emulate_media(reduced_motion="reduce")
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    # set_content avoids requiring an HTTP server and verifies the self-contained bundle.
    page.set_content(PREVIEW.read_text(encoding="utf-8"), wait_until="load")
    page.wait_for_timeout(150)
    return page, errors


def test_pointer(browser, width):
    page, errors = page_with_preview(browser, width=width, height=900 if width > 700 else 850)
    canvas = page.locator("[data-field-study]")
    assert canvas.get_attribute("data-ready") == "1", "Field failed to initialize"
    start = canvas.evaluate("c => c.toDataURL()")
    box = canvas.bounding_box()
    assert box and box["width"] > 150
    # On narrow screens part of the decorative field intentionally extends off-screen.
    # Only test pointer locations that are actually inside the viewport.
    points = ((.25, .30), (.56, .62)) if width <= 700 else ((.25, .30), (.76, .62))
    for x, y in points:
        page.mouse.move(box["x"] + box["width"] * x, box["y"] + box["height"] * y)
        page.wait_for_timeout(250)
    end = canvas.evaluate("c => c.toDataURL()")
    assert canvas.get_attribute("data-pointer-active") == "true", "Pointer input did not reach drawing"
    assert start != end, "Canvas did not redraw after pointer movement"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Horizontal overflow"
    assert not errors, errors
    print(f"PASS: pointer-responsive drawing at {width}px")
    page.close()


def test_reduced_motion(browser):
    page, errors = page_with_preview(browser, reduced=True)
    canvas = page.locator("[data-field-study]")
    original = canvas.evaluate("c => c.toDataURL()")
    page.wait_for_timeout(350)
    later = canvas.evaluate("c => c.toDataURL()")
    assert original == later, "Reduced-motion preference ignored"
    assert not errors, errors
    print("PASS: reduced-motion freezes drawing")
    page.close()


def test_navigation_and_exhibits(browser):
    page, errors = page_with_preview(browser)
    page.locator('a[href="#/work/evaluated-rag/"]').first.click()
    page.wait_for_function("document.querySelector('main h1')?.textContent.includes('RAG')")
    assert "RAG" in page.locator('h1').first.inner_text()
    assert page.locator('[data-exhibit="rag"]').count() == 1
    # Internal offline navigation continues to work after new client-side render.
    page.evaluate("location.hash = '#/research/trend-dependencies/'")
    page.wait_for_timeout(100)
    assert page.locator('[data-exhibit="trend"]').count() == 1
    slider = page.locator('#trend-noise')
    assert slider.count() == 1
    assert not errors, errors
    print("PASS: offline navigation and technical exhibits")
    page.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser = launch(playwright)
        try:
            test_pointer(browser, 1440)
            test_pointer(browser, 390)
            test_reduced_motion(browser)
            test_navigation_and_exhibits(browser)
        finally:
            browser.close()
