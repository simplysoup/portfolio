"""Homepage scroll rooms, mobile table reflow, and piano regression (offline preview)."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'screenshots'; OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for name,w,h,mobile in [('desktop',1440,900,False),('phone',390,844,True),('short-phone',320,640,True)]:
  page=browser.new_page(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'OPEN_PORTFOLIO.html').read_text(),wait_until='load')
  page.wait_for_timeout(400)
  assert page.locator('[data-folio]').count()==4
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,'hero overflow')
  page.screenshot(path=str(OUT/f'v13-{name}-hero.png'),animations='disabled')
  for num,key in enumerate(('rag','pipeline','thesis','piano')):
   scene=page.locator(f'[data-folio="{key}"]')
   # emulate a real scroll gesture; as a fallback perform wheel by browser API
   scene.evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})')
   page.wait_for_timeout(250)
   assert scene.locator('a.folio-link').count()==1
   assert scene.locator('.folio-visual').count()==1
   assert scene.evaluate('(e)=>getComputedStyle(e.querySelector(".folio-screen")).position')=='sticky'
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,key,'overflow')
   # On mobile, the artwork and CTA must occupy separate bands, even at 320x640.
   if mobile:
    link_box=scene.locator('a.folio-link').bounding_box()
    art_box=scene.locator('.folio-visual').bounding_box()
    assert link_box and art_box and link_box['y']+link_box['height']<=art_box['y']+2,(name,key,'CTA overdraw',link_box,art_box)
   if key in ('rag','piano'):
    page.screenshot(path=str(OUT/f'v13-{name}-{key}.png'),animations='disabled')
   start=scene.evaluate('(e)=>getComputedStyle(e).getPropertyValue("--progress")')
   page.mouse.wheel(0,300)
   page.wait_for_timeout(400)
   end=scene.evaluate('(e)=>getComputedStyle(e).getPropertyValue("--progress")')
   assert float(end)>float(start),(name,key,'scroll progress not updating',start,end)
  # Benchmark table routes directly from scroll profile; test mobile card reflow
  page.locator('[data-folio="rag"] .folio-link').click(force=True)
  page.wait_for_timeout(200)
  table=page.locator('.article-prose table').first
  assert table.count()==1
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(name,'table layout overflow')
  if mobile:
   table.scroll_into_view_if_needed()
   page.wait_for_timeout(160)
   assert table.locator('td[data-label]').count()>=10
   assert table.locator('tbody tr').first.evaluate('(e)=>getComputedStyle(e).display')=='block'
   page.screenshot(path=str(OUT/f'v13-{name}-table.png'),animations='disabled')
  assert not errors,(name,errors)
  print(name, '4 scenes, scroll progress, one-tap case study, table fit, no errors')
  page.close()
 # Music scene canvas rendered at two distinct moments
 pg=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 pg.set_content((ROOT/'OPEN_PORTFOLIO.html').read_text(),wait_until='load')
 pg.evaluate("location.hash='#music'");pg.wait_for_timeout(160)
 cv=pg.locator('[data-music-art]')
 signature=lambda:cv.evaluate('e=>{const d=e.getContext("2d").getImageData(0,0,e.width,e.height).data;let sum=0;for(let i=0;i<d.length;i+=89)sum=(sum*33+d[i]+d[i+1]+d[i+2])>>>0;return sum}')
 before=signature();pg.wait_for_timeout(430);after=signature()
 assert before!=after,('MIDI not animated',before,after)
 pg.screenshot(path=str(OUT/'v13-phone-music.png'),animations='disabled')
 print('MIDI timeline renders and animates')
 pg.close();browser.close()
