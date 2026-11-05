from playwright.sync_api import sync_playwright
from pathlib import Path
import hashlib, time
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'OPEN_PORTFOLIO.html').read_text(encoding='utf-8')
out=ROOT/'screenshots';out.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for tag,vp,touch in [('desktop',{'width':1440,'height':900},False),('mobile',{'width':390,'height':844},True)]:
  page=browser.new_page(viewport=vp,is_mobile=touch,has_touch=touch,device_scale_factor=1)
  errors=[];page.on('pageerror',lambda ex:errors.append(str(ex)))
  page.set_content(source,wait_until='load',timeout=20000)
  page.wait_for_timeout(850)
  print(tag,'TITLE',page.title(),'ERRS',errors[:3]);print('SCROLL',page.evaluate('({width:document.body.scrollWidth,inner:innerWidth})'))
  page.screenshot(path=str(out/f'{tag}-index.png'),full_page=False)
  page.locator('[data-room-link="systems"]').click()
  page.wait_for_timeout(1650)
  print(tag,'OPEN SYSTEMS',page.locator('.room-systems').get_attribute('aria-hidden'),'HASH',page.evaluate('location.hash'))
  page.screenshot(path=str(out/f'{tag}-systems.png'),full_page=False)
  page.locator('[data-map-toggle]').click();page.wait_for_timeout(850)
  print(tag,'MAP',page.locator('#world-map').get_attribute('aria-hidden'))
  page.screenshot(path=str(out/f'{tag}-map.png'),full_page=False)
  page.locator('[data-map-dest="music"]').click();page.wait_for_timeout(1650)
  print(tag,'OPEN MUSIC',page.locator('.room-music').get_attribute('aria-hidden'),'ERRS',errors[:3])
  page.screenshot(path=str(out/f'{tag}-music.png'),full_page=False)
  if touch:
   page.touchscreen.tap(120,420);page.wait_for_timeout(100)
  page.locator('[data-room-close]').filter(visible=True).first.click();page.wait_for_timeout(1600)
  print(tag,'BACK',page.locator('[data-directory]').get_attribute('aria-hidden'),'ERRS',errors[:3])
  page.close()
 browser.close()
