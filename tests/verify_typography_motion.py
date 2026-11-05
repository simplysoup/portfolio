"""Regression: uniform type, non-clipping chapter titles, and robust navigation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'OPEN_PORTFOLIO.html').read_text(encoding='utf-8')
OUT = ROOT / 'screenshots'
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    for name, size, is_mobile in [('desktop',(1440,900),False),('mobile',(390,844),True),('small-mobile',(320,640),True)]:
        page = browser.new_page(viewport={'width':size[0],'height':size[1]}, is_mobile=is_mobile,has_touch=is_mobile,device_scale_factor=1)
        errors=[]
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(HTML, wait_until='load')
        page.screenshot(path=str(OUT/f'v11-{name}-index.png'))
        fonts=page.locator('.dir-name').evaluate_all('els=>els.map(el=>getComputedStyle(el).fontFamily)')
        assert len(set(fonts))==1, (name,fonts)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name
        clips=page.locator('.directory-link').evaluate_all('els=>els.map(el=>{const t=el.querySelector(".dir-name").getBoundingClientRect(), r=el.getBoundingClientRect();return t.right > r.right + 2 || t.left < r.left - 2;})')
        assert not any(clips), (name,clips)
        page.locator('[data-room-link="systems"]').click()
        page.wait_for_timeout(560)
        # At the switch point the wipe is fully covering the old and new scene.
        assert page.locator('[data-wipe]').evaluate('el=>getComputedStyle(el).visibility')=='visible'
        page.wait_for_timeout(780)
        assert page.locator('.room-systems').get_attribute('aria-hidden')=='false'
        assert page.locator('[data-wipe]').evaluate('el=>getComputedStyle(el).visibility')=='hidden'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),name
        page.locator('[data-map-toggle]').click()
        page.wait_for_timeout(650)
        assert page.locator('[data-world-map]').evaluate('el=>getComputedStyle(el).visibility')=='visible'
        assert page.locator('[data-world-map]').evaluate('el=>getComputedStyle(el).opacity')=='1'
        page.screenshot(path=str(OUT/f'v11-{name}-menu.png'))
        menu_clips=page.locator('.map-destinations a').evaluate_all('els=>els.map(el=>{const t=el.querySelector("strong").getBoundingClientRect(),r=el.getBoundingClientRect();return t.right > r.right + 2 || t.top < r.top - 2 || t.bottom > r.bottom + 2;})')
        assert not any(menu_clips), (name,menu_clips)
        page.locator('[data-map-dest="research"]').click()
        page.wait_for_timeout(1340)
        assert page.locator('.room-research').get_attribute('aria-hidden')=='false'
        page.screenshot(path=str(OUT/f'v11-{name}-research.png'))
        if is_mobile:
            assert page.locator('.room-pager').evaluate('el=>getComputedStyle(el).display')=='none'
        page.locator('[data-room-close]').filter(visible=True).first.click()
        page.wait_for_timeout(1340)
        assert page.locator('[data-directory]').get_attribute('aria-hidden')=='false'
        # Open then immediately reverse the menu to catch racing animations.
        page.locator('[data-map-toggle]').click()
        page.wait_for_timeout(100)
        page.locator('[data-map-toggle]').click()
        page.wait_for_timeout(580)
        assert page.locator('[data-world-map]').get_attribute('aria-hidden')=='true'
        assert not errors,(name,errors)
        print(f'{name}: all checks passed')
        page.close()
    # Reduced motion skips curtain while still changing scenes.
    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    page.set_content(HTML,wait_until='load')
    page.locator('[data-room-link="about"]').click()
    assert page.locator('.room-about').get_attribute('aria-hidden')=='false'
    page.close()
    browser.close()
    print('reduced motion: passed')
