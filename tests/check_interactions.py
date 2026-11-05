#!/usr/bin/env python3
"""Checks the exact self-contained preview bytes, including touch emulation.

Does not claim Android file-manager viewers permit scripts. A normal browser
served over HTTP/HTTPS is the supported way to test on a physical phone.
"""
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'portfolio-preview.html').read_text()


def make_page(browser, mobile=False, reduce=False, js=True):
    ctx=browser.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},
                            device_scale_factor=1,is_mobile=mobile,has_touch=mobile,java_script_enabled=js)
    page=ctx.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    if reduce:page.emulate_media(reduced_motion='reduce')
    page.set_content(HTML,wait_until='load',timeout=20000)
    page.wait_for_timeout(400)
    return ctx,page,errors


def assert_clean(page,errors):
    assert not errors,errors
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2'),'horizontal overflow'


def desktop(browser):
    ctx,p,errors=make_page(browser)
    c=p.locator('[data-signal-sculpture]')
    p.wait_for_function("document.querySelector('[data-signal-sculpture]').dataset.rendered==='true'",timeout=6000)
    a=c.evaluate('(node)=>node.toDataURL()');p.wait_for_timeout(170)
    assert a!=c.evaluate('(node)=>node.toDataURL()'),'artwork does not animate autonomously'
    plate=p.locator('[data-sculpture-interaction]');b=plate.bounding_box()
    p.mouse.move(b['x']+b['width']*.31,b['y']+b['height']*.6)
    p.wait_for_timeout(65)
    assert c.get_attribute('data-mode')=='pointer'
    p.locator('[data-field-pulse]').click()
    assert int(c.get_attribute('data-interactions'))>=1
    assert p.locator('.sculpture-ripple').count()>=1
    assert p.locator('[data-motion-gallery]').get_attribute('data-gallery-ready')=='true'
    assert_clean(p,errors);ctx.close();print('PASS desktop — autonomous art, pointer and activation')


def mobile(browser):
    ctx,p,errors=make_page(browser,mobile=True)
    plate=p.locator('[data-sculpture-interaction]');plate.scroll_into_view_if_needed();b=plate.bounding_box()
    assert b['x']>=-2 and b['x']+b['width']<=392,b
    p.touchscreen.tap(b['x']+b['width']*.6,b['y']+b['height']*.5)
    assert int(p.locator('[data-signal-sculpture]').get_attribute('data-interactions'))>=1
    assert p.locator('.sculpture-ripple').count()>=1
    gallery=p.locator('[data-motion-gallery]');gallery.scroll_into_view_if_needed()
    assert gallery.get_attribute('data-gallery-index')=='0'
    display=p.locator('[data-gallery-swipe]');display.scroll_into_view_if_needed();r=display.bounding_box()
    # Dispatch input through the Chromium touch stack, not app JS callbacks.
    cdp=ctx.new_cdp_session(p)
    x1=r['x']+r['width']*.78;x2=r['x']+r['width']*.22;y=r['y']+r['height']*.51
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x1,'y':y}]})
    for i in range(1,9):
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x1+(x2-x1)*i/8,'y':y}]})
        p.wait_for_timeout(15)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    p.wait_for_function("document.querySelector('[data-motion-gallery]').dataset.galleryIndex==='1'",timeout=6000)
    p.wait_for_timeout(1000)
    assert p.locator('[data-gallery-copy="1"]').is_visible()
    p.locator('[data-mobile-nav-toggle]').click()
    p.wait_for_function("document.querySelector('[data-mobile-nav-toggle]').getAttribute('aria-expanded')==='true'",timeout=3000)
    assert p.locator('[data-mobile-nav]').get_attribute('aria-hidden')=='false'
    p.wait_for_timeout(720)
    p.locator('[data-mobile-nav] a[href="#/research/"]').click(force=True)
    p.wait_for_function("location.hash==='#/research/'",timeout=4000)
    assert p.locator('main h1').count()==1
    assert_clean(p,errors);ctx.close();print('PASS mobile — touchscreen art, real swipe, menu, navigation')


def reduced_and_static(browser):
    ctx,p,errors=make_page(browser,reduce=True)
    c=p.locator('[data-signal-sculpture]');p.wait_for_function("document.querySelector('[data-signal-sculpture]').dataset.rendered==='true'")
    a=c.evaluate('x=>x.toDataURL()');p.wait_for_timeout(120)
    assert a==c.evaluate('x=>x.toDataURL()'),'reduced-motion artwork must be static'
    p.locator('[data-gallery-next]').click()
    assert p.locator('[data-motion-gallery]').get_attribute('data-gallery-index')=='1'
    p.locator('[data-gallery-step="0"]').click()
    p.locator('.gallery-text.is-active a[href="#/work/evaluated-rag/"]').click()
    p.wait_for_function("location.hash==='#/work/evaluated-rag/'",timeout=3000)
    assert p.locator('[data-exhibit="rag"]').count()==1
    assert_clean(p,errors);ctx.close()
    ctx,p,errors=make_page(browser,mobile=True,js=False)
    assert p.locator('main h1').count()==1,'static homepage required without scripts'
    assert p.locator('noscript').count()>=1
    assert_clean(p,errors);ctx.close();print('PASS reduced motion, RAG article, no-JS fallback')


def privacy():
    import re
    dist=ROOT/'dist'
    rendered='\n'.join(p.read_text() for p in dist.rglob('*.html'))
    assert not re.search(r'APPROVAL REQUIRED|confidential workflows',rendered,re.I)
    assert 'The repository is an **experimental tool**' not in rendered
    assert (dist/'work'/'piano-transcription'/'index.html').exists()
    print('PASS public-only content and generated routes')


if __name__=='__main__':
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,executable_path=shutil.which('chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            desktop(b);mobile(b);reduced_and_static(b)
        finally:b.close()
    privacy()
