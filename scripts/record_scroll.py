"""Create a short, honest scroll-through capture of the generated offline HTML."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scroll-frames';OUT.mkdir(exist_ok=True)
html=(ROOT/'OPEN_PORTFOLIO.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1140,'height':720},device_scale_factor=1)
 page.set_content(html,wait_until='load')
 page.wait_for_timeout(200)
 hero=page.locator('[data-directory]').evaluate('(e)=>e.getBoundingClientRect().height')
 total=page.evaluate('document.documentElement.scrollHeight-innerHeight')
 positions=[round(total*i/47) for i in range(48)]
 for i,y in enumerate(positions):
  page.evaluate('(v)=>window.scrollTo({top:v,left:0,behavior:"instant"})',y)
  page.wait_for_timeout(55)
  page.screenshot(path=str(OUT/f'{i:03d}.jpg'),type='jpeg',quality=78)
 print('Capture frames:',len(positions),'hero height:',hero,'full scroll:',total)
 b.close()
