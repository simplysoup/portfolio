#!/usr/bin/env python3
"""Browser regression tests: genuine phone touch, idle motion, navigation,
reduced-motion preferences, responsive layout, and research exhibits.

Online installation:
    uv sync --extra test
    uv run playwright install chromium
    uv run --extra test python tests/check_interactions.py

For a system browser, set BROWSER_EXECUTABLE=/usr/bin/chromium.
"""
from __future__ import annotations
from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "portfolio-preview.html"
assert PREVIEW.is_file(), "Run `uv run python scripts/build_preview.py` first"


def launch(playwright):
    binary = os.environ.get("BROWSER_EXECUTABLE") or shutil.which("chromium")
    return playwright.chromium.launch(
        headless=True,
        executable_path=binary if binary else None,
        args=["--no-sandbox"],
    )


def open_preview(browser, *, width=1440, height=900, mobile=False, reduced=False):
    page = browser.new_page(
        viewport={"width": width, "height": height},
        is_mobile=mobile,
        has_touch=mobile,
        device_scale_factor=1,
    )
    errors = []
    page.on("pageerror", lambda exception: errors.append(str(exception)))
    if reduced:
        page.emulate_media(reduced_motion="reduce")
    page.set_content(PREVIEW.read_text(encoding="utf-8"), wait_until="load")
    page.wait_for_timeout(250)
    assert page.locator("main").get_attribute("data-motion-ready") == "true"
    return page, errors


def assert_clean(page, errors):
    assert not errors, f"JavaScript errors: {errors}"
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Horizontal overflow"


def test_desktop(browser):
    page, errors = open_preview(browser)
    canvas = page.locator("[data-field-study]")
    assert canvas.get_attribute("data-ready") == "1"
    initial = canvas.evaluate("e => e.toDataURL()")
    page.wait_for_timeout(250)
    assert initial != canvas.evaluate("e => e.toDataURL()"), "Idle animation must run"
    box = page.locator(".artwork-plate").bounding_box()
    page.mouse.move(box["x"] + box["width"] * .26, box["y"] + box["height"] * .4)
    page.wait_for_timeout(120)
    assert canvas.get_attribute("data-pointer-active") == "true", "Desktop pointer not tracked"
    assert canvas.get_attribute("data-mode") == "pointer"
    # A button creates a real impulse, not an inert decorative icon.
    page.locator("[data-field-pulse]").click()
    page.wait_for_timeout(100)
    assert float(canvas.get_attribute("data-energy")) > .1
    assert_clean(page, errors)
    print("PASS desktop: idle motion, pointer, button impulse")
    page.close()


def test_real_touch(browser):
    page, errors = open_preview(browser, width=390, height=844, mobile=True)
    canvas = page.locator("[data-field-study]")
    plate = page.locator(".artwork-plate")
    plate.scroll_into_view_if_needed()
    box = plate.bounding_box()
    # On phones the stage must have an actual touchable area in the viewport.
    assert box and box["x"] >= 0 and box["x"] + box["width"] <= 391, box
    page.touchscreen.tap(box["x"] + box["width"] * .55, box["y"] + box["height"] * .55)
    page.wait_for_timeout(150)
    assert int(canvas.get_attribute("data-touch-count") or 0) == 1, "Touch event did not reach art"
    assert float(canvas.get_attribute("data-energy")) > .1, "Touch impulse had no state effect"
    assert page.evaluate("window.scrollX") == 0, "Tapping art must not scroll horizontally"
    assert_clean(page, errors)
    print("PASS mobile: real touchscreen tap, responsive independent art stage")
    page.close()


def test_reduced_motion(browser):
    page, errors = open_preview(browser, reduced=True)
    canvas = page.locator("[data-field-study]")
    assert canvas.get_attribute("data-mode") == "reduced"
    a = canvas.evaluate("e => e.toDataURL()")
    page.wait_for_timeout(350)
    assert a == canvas.evaluate("e => e.toDataURL()"), "Reduced-motion animation didn't stop"
    assert_clean(page, errors)
    print("PASS reduced-motion: static graphic, no animation")
    page.close()


def test_page_transition_and_exhibits(browser):
    page, errors = open_preview(browser)
    page.locator('a[href="#/work/evaluated-rag/"]').first.click()
    page.wait_for_function("location.hash === '#/work/evaluated-rag/'")
    page.wait_for_function("getComputedStyle(document.querySelector('[data-route-veil]')).visibility === 'hidden'", timeout=3000)
    assert "RAG" in page.locator("main h1").first.inner_text()
    assert page.locator('[data-exhibit="rag"]').count() == 1
    assert page.locator('[data-route-veil]').evaluate('e=>getComputedStyle(e).visibility') == 'hidden'
    page.evaluate("location.hash = '#/research/trend-dependencies/'")
    page.wait_for_function("!!document.getElementById('trend-noise')")
    page.locator('#trend-noise').evaluate("e=>{e.value='1.2';e.dispatchEvent(new Event('input',{bubbles:true}))}")
    assert page.locator('#noise-out').inner_text() == '1.20'
    assert_clean(page, errors)
    print("PASS: animated local navigation, RAG and trend exhibits")
    page.close()


def test_scroll_reveal(browser):
    page, errors = open_preview(browser)
    target = page.locator('.atelier-project-rag')
    target.scroll_into_view_if_needed()
    page.wait_for_timeout(220)
    assert target.get_attribute('data-motion-entered') == 'true'
    target.hover()
    assert 'is-interacting' in (target.get_attribute('class') or '')
    assert_clean(page, errors)
    print("PASS: scroll sequencing and project micro-interaction")
    page.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        browser = launch(playwright)
        try:
            test_desktop(browser)
            test_real_touch(browser)
            test_reduced_motion(browser)
            test_page_transition_and_exhibits(browser)
            test_scroll_reveal(browser)
        finally:
            browser.close()
