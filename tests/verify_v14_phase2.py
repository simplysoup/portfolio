"""Phase 2 shell checks. Run after build with the preview server on port 8766."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from _browser import launch

URL = 'http://localhost:8766/'
with sync_playwright() as p:
    browser = launch(p)
    for width, height in [(320, 640), (390, 844), (768, 1024), (1024, 768), (1280, 800), (1440, 900), (1920, 1080)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
        page.goto(URL, wait_until='networkidle')
        page.wait_for_timeout(250)
        metrics = page.evaluate('''() => {
          const el = document.querySelector('#top [data-fit]'), r = document.createRange(); r.selectNodeContents(el);
          const box = selector => { const r = document.querySelector(selector).getBoundingClientRect(); return {x:r.x,y:r.y,right:r.right,bottom:r.bottom}; };
          return {scroll:document.documentElement.scrollWidth, ratio:r.getBoundingClientRect().width/el.parentElement.clientWidth,
            headline:box('h1'), sphere:box('[data-art=sphere]'), card:box('#top .backdrop-blur-sm'), meta:box('#top > .border-b:nth-of-type(3)')};
        }''')
        assert metrics['scroll'] <= width, (width, metrics)
        assert .96 <= metrics['ratio'] <= 1.001, (width, metrics)
        if width >= 1024:
            assert metrics['sphere']['x'] - metrics['headline']['right'] >= 24, (width, metrics)
            assert metrics['sphere']['y'] - metrics['meta']['bottom'] >= 16, (width, metrics)
        assert not errors, errors
        if width == 390:
            button = page.locator('[data-menu-toggle]'); button.focus(); page.keyboard.press('Enter')
            assert page.locator('#site-menu').is_visible()
            assert page.evaluate("document.activeElement.closest('#site-menu') !== null")
            page.keyboard.press('Escape')
            assert page.locator('#site-menu').is_hidden() and button.evaluate('(e) => e === document.activeElement')
        print(width, metrics['ratio'], metrics['scroll'])
        page.close()
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    page.goto(URL, wait_until='networkidle'); page.wait_for_timeout(300)
    assert page.locator('.animate-marquee').evaluate('(e) => getComputedStyle(e).animationName') == 'none'
    image = page.locator('canvas').evaluate('(c) => c.toDataURL()'); page.wait_for_timeout(500)
    assert image == page.locator('canvas').evaluate('(c) => c.toDataURL()')
    page.goto((Path(__file__).resolve().parents[1] / 'OPEN_PORTFOLIO.html').as_uri(), wait_until='networkidle')
    assert page.locator('h1').count() == 1 and page.evaluate('document.fonts.check("100px Big Shoulders Display")')
    page.goto(URL + 'work/evaluated-rag/', wait_until='networkidle')
    assert page.locator('h1').is_visible()
    browser.close()
print('Phase 2 checks passed')
