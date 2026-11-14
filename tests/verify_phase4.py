"""Local rail, responsive layout and mailto regression checks."""
from pathlib import Path
from subprocess import Popen, DEVNULL
from urllib.parse import parse_qs, urlsplit
import time
from playwright.sync_api import sync_playwright
from _browser import launch

ROOT = Path(__file__).resolve().parents[1]
shots = ROOT / 'screenshots/v14/phase4'
shots.mkdir(parents=True, exist_ok=True)
server = Popen(['uv', 'run', 'python', '-m', 'http.server', '38477', '--directory', 'dist'], cwd=ROOT, stdout=DEVNULL, stderr=DEVNULL)
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
            rail = page.locator('[data-rail]')
            assert page.locator('html').evaluate("e=>e.classList.contains('rail-on')") == (w>=1024)
            if w >= 1024:
                dims=page.locator('.rail-card').evaluate_all("es=>es.map(e=>({card:e.getBoundingClientRect().height, art:e.querySelector('.rail-art').getBoundingClientRect().height, body:e.querySelector('.rail-body').getBoundingClientRect().height}))")
                print(w,h,dims)
                assert all(d['art']>=180 and d['card']<=h-56-96 for d in dims), (w,dims)
                wrapper=page.locator('[data-rail-wrapper]')
                for progress in [0,0.5,1]:
                    page.evaluate("([p])=>{const w=document.querySelector('[data-rail-wrapper]'),v=document.querySelector('[data-rail-viewport]');window.scrollTo({top:window.scrollY+w.getBoundingClientRect().top-56+p*(w.offsetHeight-v.offsetHeight-56),behavior:'instant'});}",[progress])
                    page.wait_for_timeout(200)
                    if w==1440:
                        assert page.locator('[data-rail-count]').inner_text().endswith('/ 06')
                        page.screenshot(path=str(shots/f'rail-{progress}.png'))
                if w==1440:
                    for i in range(6):
                        link=page.locator('.rail-card').nth(i).locator('a').first
                        link.focus();page.wait_for_timeout(100)
                        bounds=page.locator('.rail-card').nth(i).bounding_box()
                        assert bounds['x']>=-1 and bounds['x']+bounds['width']<=w+1,(i,bounds)
                        page.locator('.rail-card').nth(i).locator('svg').screenshot(path=str(shots/f'diagram-{i+1}.png'))
                    first=page.locator('.rail-card').first.locator('a').first
                    first.focus();page.wait_for_timeout(100)
                    for index in range(12):
                        active=page.locator(':focus')
                        assert active.evaluate('e=>!!e.closest(".rail-card")'), index
                        bounds=active.locator('xpath=ancestor::article').bounding_box()
                        assert bounds['x']>=-1 and bounds['x']+bounds['width']<=w+1,(index,bounds)
                        if index < 11:
                            page.keyboard.press('Tab');page.wait_for_timeout(120)
                    # Native scrolling is not intercepted by the rail.
                    wrapper.scroll_into_view_if_needed(); page.wait_for_timeout(200)
                    start=page.evaluate('scrollY'); page.mouse.wheel(0,400);page.wait_for_timeout(300);assert page.evaluate('scrollY')>start
                    for key in ['PageDown','Space','ArrowDown']:
                        start=page.evaluate('scrollY');page.keyboard.press(key);page.wait_for_timeout(350);assert page.evaluate('scrollY')>start,key
            else:
                rail.scroll_into_view_if_needed();page.wait_for_timeout(300)
                if w in (390,768): page.screenshot(path=str(shots/f'grid-{w}.png'))
            if w==1440:
                for section in ['research','contact']:
                    page.locator('#'+section).scroll_into_view_if_needed();page.wait_for_timeout(300);page.screenshot(path=str(shots/f'{section}.png'))
                form=page.locator('[data-mailto]'); assert not form.evaluate('e=>e.checkValidity()')
                form.locator('[name=name]').fill('A & B'); form.locator('[name=email]').fill('a@example.com');form.locator('[name=message]').fill('Hello\nWorld')
                form.locator('button').click();value=form.get_attribute('data-last-mailto'); parts=urlsplit(value); query=parse_qs(parts.query)
                assert parts.path=='nickbode71@gmail.com' and query['subject']==['Hello from A & B'] and query['body']==['Hello\nWorld\n\n— A & B (a@example.com)'],value
            assert not errors, errors
            page.close()
        page=browser.new_page(viewport={'width':1440,'height':900},reduced_motion='reduce');page.goto('http://127.0.0.1:38477/');assert not page.locator('html').evaluate("e=>e.classList.contains('rail-on')");page.close()
        page=browser.new_page(viewport={'width':1440,'height':900});page.goto('http://127.0.0.1:38477/');page.set_viewport_size({'width':768,'height':1024});page.wait_for_timeout(100);assert not page.locator('html').evaluate("e=>e.classList.contains('rail-on')");assert page.locator('[data-rail-wrapper]').evaluate("e=>e.style.height") == '';assert page.locator('[data-rail-track]').evaluate("e=>e.style.transform") == '';page.set_viewport_size({'width':1440,'height':900});page.wait_for_timeout(100);assert page.locator('html').evaluate("e=>e.classList.contains('rail-on')");page.close()
        page=browser.new_page(viewport={'width':1440,'height':900},java_script_enabled=False);page.goto('http://127.0.0.1:38477/');assert page.locator('.rail-card').count()==6 and not page.locator('html').evaluate("e=>e.classList.contains('rail-on')");page.close()
        page=browser.new_page(viewport={'width':1440,'height':900});page.goto((ROOT/'OPEN_PORTFOLIO.html').as_uri());assert page.locator('html').evaluate("e=>e.classList.contains('rail-on')");page.evaluate("()=>{const w=document.querySelector('[data-rail-wrapper]'),v=document.querySelector('[data-rail-viewport]');window.scrollTo({top:window.scrollY+w.getBoundingClientRect().top-56+0.5*(w.offsetHeight-v.offsetHeight-56),behavior:'instant'})}");page.wait_for_timeout(200);assert page.locator('[data-rail-track]').evaluate("e=>e.style.transform").startswith('translate3d(-');page.close()
        browser.close()
finally:
    server.terminate();server.wait()
