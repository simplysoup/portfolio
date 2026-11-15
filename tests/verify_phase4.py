"""Local grid, responsive layout and email-button regression checks.

Replaces the former work-rail checks: the homepage now shows the six
projects in a plain grid with a visible project index, and contact is a
direct email button instead of a mailto form.
"""
from pathlib import Path
from subprocess import Popen, DEVNULL
import sys
import time
from playwright.sync_api import sync_playwright
from _browser import launch

ROOT = Path(__file__).resolve().parents[1]
shots = ROOT / 'screenshots/v14/phase4'
shots.mkdir(parents=True, exist_ok=True)
server = Popen([sys.executable, '-m', 'http.server', '38477', '--directory', 'dist'], cwd=ROOT, stdout=DEVNULL, stderr=DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser = launch(p)
        for w, h in [(320,640),(390,844),(768,1024),(1024,768),(1280,800),(1440,900),(1920,1080)]:
            page = browser.new_page(viewport={'width':w,'height':h})
            errors=[]
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.goto('http://127.0.0.1:38477/', wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (w, 'overflow')
            # No horizontal rail at any width: six cards in a grid, index links resolve.
            assert not page.locator('html').evaluate("e=>e.classList.contains('rail-on')"), (w, 'rail-on present')
            assert page.locator('.rail-card').count() == 6, (w, 'card count')
            assert page.locator('nav[aria-label="Project index"] a').count() == 6, (w, 'project index')
            first = page.locator('.rail-card').first.locator('h3').inner_text()
            assert first == 'AgentShield', (w, first)
            if w in (390, 768, 1440):
                page.screenshot(path=str(shots/f'grid-{w}.png'))
            if w == 1440:
                for section in ['research','contact']:
                    page.locator('#'+section).scroll_into_view_if_needed();page.wait_for_timeout(300);page.screenshot(path=str(shots/f'{section}.png'))
                link = page.locator('#contact a[href="mailto:nickbode71@gmail.com"]')
                assert link.count() >= 1, 'email button missing'
                assert page.locator('form[data-mailto]').count() == 0, 'mailto form still present'
            assert not errors, errors
            page.close()
        page=browser.new_page(viewport={'width':1440,'height':900},reduced_motion='reduce');page.goto('http://127.0.0.1:38477/');assert not page.locator('html').evaluate("e=>e.classList.contains('rail-on')");assert page.locator('.rail-card').count()==6;page.close()
        page=browser.new_page(viewport={'width':1440,'height':900},java_script_enabled=False);page.goto('http://127.0.0.1:38477/');assert page.locator('.rail-card').count()==6 and not page.locator('html').evaluate("e=>e.classList.contains('rail-on')");page.close()
        page=browser.new_page(viewport={'width':1440,'height':900});page.goto((ROOT/'OPEN_PORTFOLIO.html').as_uri());assert page.locator('.rail-card').count()==6;page.locator('a[href="#/work/trainstore/"]').first.click();page.wait_for_timeout(300);assert 'trainstore' in page.locator('main h1').inner_text().lower();page.close()
        browser.close()
finally:
    server.terminate();server.wait()
