"""Phase 5 route, exhibit, preview and print checks."""
from pathlib import Path
import subprocess
import time
from playwright.sync_api import sync_playwright
from _browser import launch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'screenshots/v14/phase5'
OUT.mkdir(parents=True, exist_ok=True)
ROUTES = ['/', '/work/', *[f'/work/{s}/' for s in ('trainstore','agent-shield','casestruct-lora','evaluated-rag','analytics-pipeline','piano-transcription')], '/research/', '/research/trend-dependencies/', '/about/', '/contact/', '/resume/']
server = subprocess.Popen(['python', '-m', 'http.server', '18765', '--directory', str(ROOT / 'dist')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(.5)
    with sync_playwright() as p:
        browser = launch(p)
        errors = []
        for width, height in [(390, 844), (1440, 900)]:
            page = browser.new_page(viewport={'width': width, 'height': height}, reduced_motion='reduce')
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
            for route in ROUTES:
                page.goto('http://127.0.0.1:18765' + route, wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width, page.evaluate('document.documentElement.scrollWidth'))
                assert page.evaluate('document.fonts.check("15px Geist")')
                page.screenshot(path=str(OUT / ((route.strip('/').replace('/', '-') or 'home') + f'-{width}.png')), full_page=True)
            page.close()
        for width, height in [(320, 640), (768, 1024), (1024, 768), (1920, 1080)]:
            page = browser.new_page(viewport={'width': width, 'height': height}, reduced_motion='reduce')
            for route in ROUTES:
                page.goto('http://127.0.0.1:18765' + route, wait_until='networkidle')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (route, width)
            page.close()
        page = browser.new_page(reduced_motion="reduce")
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
        for route in ROUTES:
            page.goto((ROOT / 'OPEN_PORTFOLIO.html').as_uri() + ('#' + route if route != '/' else ''), wait_until='networkidle')
            assert page.locator('main').inner_text().strip(), route
        for root in ['http://127.0.0.1:18765', (ROOT / 'OPEN_PORTFOLIO.html').as_uri() + '#']:
            page.goto(root + '/work/evaluated-rag/', wait_until='networkidle')
            for choice in page.locator('[data-case]').all():
                choice.click()
                assert choice.get_attribute('aria-pressed') == 'true'
            page.goto(root + '/research/trend-dependencies/', wait_until='networkidle')
            for slider in page.locator('input[type=range]').all():
                slider.fill(slider.get_attribute('max'))
                assert slider.input_value() == slider.get_attribute('max')
            assert page.locator('.prose-nb h2[id]').count() > 0
            toc = page.locator('nav[aria-label="On this page"] a').first
            target = page.locator(toc.get_attribute('href'))
            toc.click()
            page.wait_for_timeout(500)
            assert target.bounding_box()['y'] >= 48, target.bounding_box()

        page.goto('http://127.0.0.1:18765/resume/', wait_until='networkidle')
        page.emulate_media(media='print')
        page.pdf(path=str(OUT / 'resume.pdf'), format='Letter', print_background=True)
        assert not errors, errors
        browser.close()
finally:
    server.terminate()
    server.wait()
print('Phase 5 route, exhibit, preview and print checks passed')
