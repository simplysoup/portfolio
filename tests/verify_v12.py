"""V12 regression: showcase shortcuts, themed index, music timeline and offline navigation."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'screenshots'
OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for name,size,phone in [('desktop',(1440,900),False),('mobile',(390,844),True),('small',(320,640),True)]:
  page=browser.new_page(viewport={'width':size[0],'height':size[1]},is_mobile=phone,has_touch=phone,device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'OPEN_PORTFOLIO.html').read_text(encoding='utf-8'),wait_until='load')
  page.wait_for_timeout(240)
  assert page.locator('.directory-shortcuts a').count()==4, name
  assert page.locator('.dir-motif svg').count()==4, name
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),name
  page.screenshot(path=str(OUT/f'v12-{name}-index.png'),full_page=True,animations='disabled')
  # One click from homepage directly to a publicly releasable project.
  page.locator('.directory-shortcuts a[href="#/work/evaluated-rag/"]').click()
  page.wait_for_timeout(140)
  assert '/work/evaluated-rag/' in page.url,(name,page.url)
  assert page.locator('.article-header').count()==1,name
  # Map should work from the article, exposing direct project links without a chapter hop.
  page.locator('[data-map-toggle]').click()
  page.wait_for_timeout(690)
  assert page.locator('.map-shortcuts a').count()==4,name
  page.screenshot(path=str(OUT/f'v12-{name}-map.png'),animations='disabled')
  page.locator('.map-shortcuts a[href="#/work/piano-transcription/"]').click()
  page.wait_for_timeout(120)
  assert '/work/piano-transcription/' in page.url,(name,page.url)
  assert page.locator('.article-header').count()==1,name
  # Navigate to the live music chapter and sample its canvas across animation frames.
  page.set_content((ROOT/'OPEN_PORTFOLIO.html').read_text(encoding='utf-8'),wait_until='load');page.evaluate("location.hash='#music'")
  page.wait_for_timeout(120)
  assert page.locator('.room-music').get_attribute('aria-hidden')=='false',name
  canvas=page.locator('[data-music-art]')
  check=lambda:canvas.evaluate('el=>({w:el.width,h:el.height,signature:(()=>{const d=el.getContext("2d").getImageData(0,0,el.width,el.height).data;let v=0;for(let i=0;i<d.length;i+=137)v=(v*33+d[i]+d[i+1]+d[i+2])>>>0;return v})()})')
  before=check();page.wait_for_timeout(400);after=check()
  assert before['w']>200 and before['h']>100,(name,before)
  assert before['signature']!=after['signature'],(name,before,after)
  page.screenshot(path=str(OUT/f'v12-{name}-music.png'),animations='disabled')
  # Leave music and return: canvas should resume with correctly-sized content.
  page.locator('.room-music [data-room-close]').click()
  page.wait_for_timeout(1250)
  assert page.locator('[data-directory]').get_attribute('aria-hidden')=='false',name
  page.locator('[data-room-link="music"]').click()
  page.wait_for_timeout(1300)
  current=check()
  assert current['w']>200 and current['h']>100,(name,current)
  assert not errors,(name,errors)
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),name
  print(f'{name}: showcases reachable in 1 tap, MIDI animating, navigation stable, no overflow/errors')
  page.close()
 page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
 page.set_content((ROOT/'OPEN_PORTFOLIO.html').read_text(encoding='utf-8'),wait_until='load');page.evaluate("location.hash='#music'")
 page.wait_for_timeout(150)
 assert page.locator('.room-music').get_attribute('aria-hidden')=='false'
 assert page.locator('[data-music-art]').evaluate('e=>e.width')>200
 print('reduced-motion static piano roll: passed')
 page.close();browser.close()
