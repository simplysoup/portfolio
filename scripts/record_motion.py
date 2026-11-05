#!/usr/bin/env python3
"""Browser recording of our own portfolio (not the two external reference sites)."""
from pathlib import Path
import math,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
MARKUP=(ROOT/'portfolio-preview.html').read_text()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx=b.new_context(viewport={'width':1280,'height':800},record_video_dir=str(ROOT),record_video_size={'width':960,'height':600},device_scale_factor=1)
    page=ctx.new_page();page.set_content(MARKUP,wait_until='load')
    page.wait_for_timeout(1000)
    r=page.locator('[data-sculpture-interaction]').bounding_box()
    for i in range(15):
        a=i/14*math.pi*2
        page.mouse.move(r['x']+r['width']*(.5+.27*math.cos(a)),r['y']+r['height']*(.5+.25*math.sin(a)),steps=2)
        page.wait_for_timeout(80)
    page.locator('[data-field-pulse]').click();page.wait_for_timeout(550)
    page.locator('[data-motion-gallery]').scroll_into_view_if_needed();page.wait_for_timeout(900)
    page.locator('[data-gallery-next]').click();page.wait_for_timeout(1600)
    page.locator('[data-gallery-next]').click();page.wait_for_timeout(1450)
    v=page.video
    ctx.close();b.close()
    path=v.path()
    target=ROOT/'atelier09-motion.webm'
    Path(path).rename(target)
    print('Recorded browser video:',target,'bytes',target.stat().st_size)
