from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
MARKUP=(ROOT/'portfolio-preview.html').read_text()
OUT=Path('/mnt/data/atelier07-motion-frames');OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':1100,'height':750},device_scale_factor=1)
 page=c.new_page();page.set_content(MARKUP,wait_until='load')
 page.wait_for_timeout(1200)
 gal=page.locator('[data-motion-gallery]');gal.scroll_into_view_if_needed();page.wait_for_timeout(1000)
 # Keep the gallery fixed in the viewport for capture.
 page.evaluate('''() => { let e=document.querySelector('.motion-gallery');e.scrollIntoView({block:'start',behavior:'instant'});window.scrollBy(0,-12) }''')
 page.wait_for_timeout(500)
 index=0
 def shot(count=1):
  global index
  for _ in range(count):
   page.screenshot(path=str(OUT/f'{index:04d}.png'),animations='allow')
   index+=1
   page.wait_for_timeout(63)
 shot(5)
 page.locator('[data-gallery-step="1"]').click(no_wait_after=True,force=True)
 shot(17)
 page.wait_for_timeout(650)
 page.locator('[data-gallery-step="2"]').click(no_wait_after=True,force=True)
 shot(18)
 b.close()
 print('captured',index)
