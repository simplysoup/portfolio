"""Capture actual Web Animations API movements of the offline preview."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import time
R=Path(__file__).resolve().parents[1]
out=R/'motion_frames';out.mkdir(exist_ok=True)
s=(R/'OPEN_PORTFOLIO.html').read_text(encoding='utf-8')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
    page.set_content(s,wait_until='load')
    actions={12:lambda:page.locator('[data-room-link="research"]').click(),
             37:lambda:page.locator('[data-map-toggle]').click(),
             54:lambda:page.locator('[data-map-dest="music"]').click(),
             79:lambda:page.locator('.room.is-visible [data-room-close]').click()}
    errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
    start=time.monotonic()
    for i in range(98):
        if i in actions: actions[i]()
        page.screenshot(path=str(out/f'{i:03d}.png'),animations='allow')
        next_frame=start+(i+1)*.10
        if time.monotonic()<next_frame: time.sleep(next_frame-time.monotonic())
    b.close()
    print('captured',len(list(out.glob('*.png'))),'errors',errors,'elapsed',round(time.monotonic()-start,1))
