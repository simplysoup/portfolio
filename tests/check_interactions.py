#!/usr/bin/env python3
"""Atelier 07 regression checks for the distributable standalone HTML.

Important: the runtime used for these checks blocks Playwright navigation to
file:// and localhost HTTP URLs. We load the same self-contained HTML bytes with
page.set_content and test interactions with emulated browser input. This is not
a guarantee that a third-party Android file viewer allows JavaScript at all.

Run after building:
    uv run --extra test python tests/check_interactions.py
Or set BROWSER_EXECUTABLE=/usr/bin/chromium for an installed Chromium.
"""
from pathlib import Path
import os, shutil, re
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'portfolio-preview.html'
assert HTML.exists(), 'Run scripts/build.py and scripts/build_preview.py'
MARKUP=HTML.read_text(encoding='utf-8')

def launch(p):
    browser=os.getenv('BROWSER_EXECUTABLE') or shutil.which('chromium')
    return p.chromium.launch(headless=True,executable_path=browser or None,args=['--no-sandbox'])

def open_site(browser, mobile=False, reduce=False, javascript_enabled=True):
    # Separate context so JavaScript can be disabled for static-fallback checks.
    context=browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},
                                is_mobile=mobile,has_touch=mobile,device_scale_factor=1,
                                java_script_enabled=javascript_enabled)
    page=context.new_page(); errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    if reduce:page.emulate_media(reduced_motion='reduce')
    page.set_content(MARKUP,wait_until='load');page.wait_for_timeout(350)
    return context,page,errors

def clean(page,errors):
    assert not errors,errors
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), 'Horizontal overflow'

def test_desktop(browser):
    ctx,page,errors=open_site(browser)
    canvas=page.locator('[data-field-study]')
    assert canvas.get_attribute('data-ready')=='1'
    first=canvas.evaluate('c=>c.toDataURL()')
    page.wait_for_timeout(160)
    assert first!=canvas.evaluate('c=>c.toDataURL()'), 'Field should animate without input'
    plate=page.locator('.artwork-plate');b=plate.bounding_box()
    page.mouse.move(b['x']+.35*b['width'],b['y']+.43*b['height'])
    page.wait_for_timeout(120)
    assert canvas.get_attribute('data-mode')=='pointer'
    page.locator('[data-field-pulse]').click()
    assert page.locator('.field-impact').count()>0, 'Visible pulse feedback required'
    assert float(canvas.get_attribute('data-energy'))>.2
    assert page.locator('[data-motion-gallery]').get_attribute('data-gallery-ready')=='true'
    clean(page,errors);ctx.close();print('PASS desktop: live field, pointer, pulse and gallery')

def test_mobile(browser):
    ctx,page,errors=open_site(browser,mobile=True)
    canvas=page.locator('[data-field-study]');plate=page.locator('.artwork-plate')
    plate.scroll_into_view_if_needed();b=plate.bounding_box()
    assert b['x']>=0 and b['x']+b['width']<=391,b
    page.touchscreen.tap(b['x']+b['width']*.5,b['y']+b['height']*.4)
    page.wait_for_timeout(150)
    assert canvas.get_attribute('data-touch-count')=='1','Touch did not reach field'
    assert float(canvas.get_attribute('data-energy'))>.2
    assert page.locator('.field-impact').count()>0,'Mobile feedback not visible'
    gallery=page.locator('[data-motion-gallery]');gallery.scroll_into_view_if_needed()
    assert gallery.get_attribute('data-gallery-index')=='0'
    page.locator('[data-gallery-step="1"]').click()
    page.wait_for_function("document.querySelector('[data-motion-gallery]').dataset.galleryIndex==='1'")
    page.wait_for_timeout(1800)
    assert page.locator('[data-gallery-copy="1"]').is_visible()
    display=page.locator('[data-gallery-swipe]');display.scroll_into_view_if_needed();box=display.bounding_box()
    # Dispatch actual touch events through Chromium's input stack. Not a
    # direct state assignment or a mocked application callback.
    cdp=ctx.new_cdp_session(page)
    x1=box['x']+box['width']*.76; x2=box['x']+box['width']*.21;y=box['y']+box['height']*.52
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x1,'y':y}]})
    for i in range(1,9):
        x=x1+(x2-x1)*i/8
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y}]})
        page.wait_for_timeout(15)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    page.wait_for_function("document.querySelector('[data-motion-gallery]').dataset.galleryIndex==='2'",timeout=5000)
    assert gallery.get_attribute('data-gallery-mode') in ('swipe','queued')
    page.wait_for_timeout(1350)
    box=display.bounding_box()
    page.touchscreen.tap(box['x']+box['width']*.52,box['y']+box['height']*.52)
    page.wait_for_function("document.querySelector('[data-motion-gallery]').dataset.galleryIndex==='0'",timeout=4000)
    page.locator('[data-mobile-nav-toggle]').click()
    page.wait_for_function("document.querySelector('[data-mobile-nav-toggle]').getAttribute('aria-expanded')==='true'")
    assert page.locator('[data-mobile-nav]').get_attribute('aria-hidden')=='false'
    page.wait_for_timeout(760)
    page.locator('[data-mobile-nav] a[href="#/research/"]').click(force=True)
    page.wait_for_function("location.hash==='#/research/'",timeout=5000)
    assert page.locator('main h1').count()>0
    clean(page,errors);ctx.close();print('PASS mobile: canvas tap, visible ripple, tab, real swipe, menu and route')

def test_content_and_accessibility(browser):
    ctx,page,errors=open_site(browser,reduce=True)
    canvas=page.locator('[data-field-study]');assert canvas.get_attribute('data-mode')=='reduced'
    first=canvas.evaluate('c=>c.toDataURL()');page.wait_for_timeout(150)
    assert first==canvas.evaluate('c=>c.toDataURL()')
    page.locator('[data-gallery-next]').click();page.wait_for_timeout(30)
    assert page.locator('[data-motion-gallery]').get_attribute('data-gallery-index')=='1'
    page.locator('[data-gallery-step="0"]').click()
    page.locator('.gallery-text.is-active a[href="#/work/evaluated-rag/"]').click()
    page.wait_for_function("location.hash==='#/work/evaluated-rag/'",timeout=2000)
    assert page.locator('[data-exhibit="rag"]').count()==1
    clean(page,errors);ctx.close()
    assert '[VERIFY / APPROVAL REQUIRED]' not in MARKUP
    print('PASS reduced motion, routing, RAG exhibit, public-copy scan')

def test_noscript_fallback(browser):
    ctx,page,errors=open_site(browser,mobile=True,javascript_enabled=False)
    assert page.locator('main h1').count()==1, 'Preview must show readable homepage if JS blocked'
    assert page.locator('noscript').count()>=1
    clean(page,errors);ctx.close();print('PASS restricted Android-like viewer: visible static homepage')

if __name__=='__main__':
    with sync_playwright() as p:
        browser=launch(p)
        try:
            test_desktop(browser)
            test_mobile(browser)
            test_content_and_accessibility(browser)
            test_noscript_fallback(browser)
        finally:browser.close()
