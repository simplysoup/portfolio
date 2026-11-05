"""Capture desktop/mobile static previews from built single-file HTML."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'portfolio-preview.html').read_text(encoding='utf-8')
OUT=Path('/mnt/data')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for mobile in (False,True):
  ctx=b.new_context(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  page=ctx.new_page();page.set_content(HTML,wait_until='load');page.wait_for_timeout(1800)
  prefix='mobile' if mobile else 'desktop'
  page.screenshot(path=str(OUT/f'atelier07-{prefix}-hero.png'))
  gal=page.locator('[data-motion-gallery]')
  gal.scroll_into_view_if_needed();page.wait_for_timeout(900)
  page.screenshot(path=str(OUT/f'atelier07-{prefix}-gallery.png'))
  page.locator('[data-gallery-step="2"]').click();page.wait_for_timeout(1400)
  page.screenshot(path=str(OUT/f'atelier07-{prefix}-piano.png'))
  if mobile:
   page.locator('[data-mobile-nav-toggle]').click();page.wait_for_timeout(920)
   page.screenshot(path=str(OUT/'atelier07-mobile-menu.png'))
   page.locator('[data-mobile-nav-toggle]').click();page.wait_for_timeout(680)
   plate=page.locator('.artwork-plate');plate.scroll_into_view_if_needed();r=plate.bounding_box()
   page.touchscreen.tap(r['x']+r['width']*.48,r['y']+r['height']*.45)
   page.wait_for_timeout(145);page.screenshot(path=str(OUT/'atelier07-mobile-touch.png'))
  ctx.close()
 b.close()
