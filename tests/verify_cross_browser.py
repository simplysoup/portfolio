"""Cross-engine compatibility checks for Directory 13.

Runs the exact self-contained `OPEN_PORTFOLIO.html` markup, without relying on
file:// JavaScript permissions. Desktop wheel measurements are a diagnostic,
not a simulation of native phone touch momentum or Safari browser chrome.

Run: python tests/verify_cross_browser.py --require-all
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from playwright.sync_api import Error as PlaywrightError, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "OPEN_PORTFOLIO.html"
REPORT = ROOT / "cross-browser-report.json"
CASES = {
    "wide-desktop": (1920, 1080, False),
    "desktop": (1440, 900, False),
    "tablet": (820, 1180, False),
    "phone": (390, 844, True),
    "short-phone": (320, 640, True),
}
PROJECTS = ("rag", "pipeline", "thesis", "piano")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def checksum(page, selector: str):
    return page.locator(selector).evaluate("""el => {
      const ctx=el.getContext('2d');
      if (!ctx || el.width < 2 || el.height < 2) return null;
      const pixels=ctx.getImageData(0, 0, el.width, el.height).data;
      let hash=5381;
      for (let i=0;i+2<pixels.length;i+=89)
        hash=(Math.imul(hash,33)+pixels[i]+pixels[i+1]+pixels[i+2])>>>0;
      return hash;
    }""")


def scroll_sample(page):
    """Measure one chapter per viewport; all four receive structural checks."""
    scene = page.locator('[data-folio="rag"]')
    scene.evaluate('(el) => el.scrollIntoView({block:"start",behavior:"instant"})')
    page.wait_for_timeout(100)
    y0 = page.evaluate('scrollY')
    p0 = float(scene.evaluate('(el)=>getComputedStyle(el).getPropertyValue("--progress")||0'))
    page.mouse.wheel(0, 300)
    page.wait_for_timeout(320)
    y1 = page.evaluate('scrollY')
    p1 = float(scene.evaluate('(el)=>getComputedStyle(el).getPropertyValue("--progress")||0'))
    page.wait_for_timeout(240)
    y2 = page.evaluate('scrollY')
    require(p1 > p0 + 0.01, f'scroll progress not updating: {p0} -> {p1}')
    return {
        "input": "synthetic mouse wheel; not touch momentum",
        "wheel_delta_px": 300,
        "scroll_delta_320ms_px": round(y1-y0, 1),
        "post_wheel_drift_240ms_px": round(y2-y1, 1),
        "progress_before": round(p0, 4),
        "progress_after": round(p1, 4),
    }


def run_case(browser, engine: str, viewport: str, size, html: str):
    width, height, mobile = size
    actual_mobile = mobile and engine != 'firefox'
    page = browser.new_page(
        viewport={"width": width, "height": height},
        device_scale_factor=1,
        is_mobile=actual_mobile,
        has_touch=actual_mobile,
    )
    page.set_default_timeout(7000)
    errors = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    result = {
        "status": "FAIL", "viewport": viewport, "width": width, "height": height,
        "mobile_emulation": actual_mobile, "checks": [],
    }
    try:
        page.set_content(html, wait_until='domcontentloaded', timeout=14000)
        page.wait_for_timeout(180)
        require(page.locator('[data-folio]').count()==4,'expected four project chapters')
        require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'homepage horizontal overflow')
        result['checks'].append('homepage layout and scene count')
        result['css_support'] = page.evaluate('''() => ({
          has:CSS.supports('selector(:has(*))'),
          svh:CSS.supports('height','100svh'),
          clipPath:CSS.supports('clip-path','inset(50% 0 0 0)'),
          colorMix:CSS.supports('color','color-mix(in srgb, red 50%, blue)'),
          scrollSnap:CSS.supports('scroll-snap-type','y proximity'),
          webAnimations:typeof Element.prototype.animate==='function'
        })''')
        result['track'] = page.locator('[data-folio="rag"]').evaluate('''el => ({
          height:Math.round(el.getBoundingClientRect().height),
          viewport:innerHeight,
          hold:Math.round(el.getBoundingClientRect().height-innerHeight)
        })''')
        for key in PROJECTS:
            scene=page.locator(f'[data-folio="{key}"]')
            require(scene.locator('a.folio-link').count()==1, f'{key}: missing case study link')
            require(scene.locator('.folio-visual').count()==1, f'{key}: missing artwork')
            pos=scene.locator('.folio-screen').evaluate('(el)=>getComputedStyle(el).position')
            require(pos=='sticky',f'{key}: screen is {pos}, expected sticky')
            if mobile:
                # compare in same CSS coordinate system; avoids viewport-relative
                # bounding boxes becoming misleading when scene is far off-screen
                positions=scene.evaluate('''el=>{
                   const link=el.querySelector('a.folio-link').getBoundingClientRect();
                   const art=el.querySelector('.folio-visual').getBoundingClientRect();
                   return {linkBottom:link.bottom, artTop:art.top};
                }''')
                require(positions['linkBottom']<=positions['artTop']+2,
                        f'{key}: primary link visually overlaps artwork')
        result['checks'].append('four sticky project chapters, links and art')
        result['scroll'] = scroll_sample(page)
        result['checks'].append('synthetic wheel scroll changes chapter progress')
        require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'scrolled homepage overflow')
        # Click the project's actual link so the offline router is exercised.
        page.locator('[data-folio="rag"] a.folio-link').evaluate('(el)=>el.click()')
        page.wait_for_function("document.querySelector('.article-prose table') !== null",timeout=6000)
        require(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'article horizontal overflow')
        if mobile:
            row=page.locator('.article-prose table tbody tr').first.evaluate('(el)=>getComputedStyle(el).display')
            require(row=='block',f'expected stacked mobile table row, got {row}')
            require(page.locator('td[data-label]').count()>=10,'mobile table labels missing')
        result['checks'].append('case-study route and responsive table')
        # Reduced motion should be off from the initial render, not applied
        # after the page starts animating.
        page.emulate_media(reduced_motion='reduce')
        page.set_content(html,wait_until='domcontentloaded',timeout=14000)
        page.wait_for_timeout(120)
        if result['css_support']['has']:
            snap=page.evaluate('getComputedStyle(document.documentElement).scrollSnapType')
            require(snap=='none',f'reduced motion leaves scroll-snap active: {snap}')
        require(not errors,f'uncaught JavaScript errors: {errors}')
        result['checks'].append('reduced motion and no JS exceptions')
        result['status']='PASS'
    except Exception as exc:
        result['error']=str(exc)
        result['browser_errors']=errors
    finally:
        page.close()
    return result


def run_music(browser, engine: str, html: str):
    page=browser.new_page(viewport={"width":390,"height":844},
                          is_mobile=engine!='firefox',has_touch=engine!='firefox')
    page.set_default_timeout(7000)
    try:
        page.set_content(html,wait_until='domcontentloaded',timeout=14000)
        page.evaluate("location.hash='#music'")
        page.wait_for_timeout(180)
        first=checksum(page,'[data-music-art]')
        page.wait_for_timeout(450)
        second=checksum(page,'[data-music-art]')
        status='PASS' if first is not None and second is not None and first!=second else 'FAIL'
        return {'status':status,'first_checksum':first,'second_checksum':second}
    except Exception as exc:
        return {'status':'FAIL','error':str(exc)}
    finally:
        page.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--require-all',action='store_true',help='Fail if a requested browser is unavailable')
    parser.add_argument('--report',type=Path,default=REPORT)
    parser.add_argument('--browsers',nargs='+',choices=('chromium','firefox','webkit'),
                        default=('chromium','firefox','webkit'))
    parser.add_argument('--viewports',nargs='+',choices=tuple(CASES),default=list(CASES))
    args=parser.parse_args()
    html=HTML.read_text(encoding='utf8')
    out={
        'test':'Directory v13 compatibility',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'source':'OPEN_PORTFOLIO.html',
        'platform':sys.platform,
        'notes':[
            'Playwright WebKit runs Safari WebKit engine, not Safari for macOS/iOS.',
            'Narrow Firefox viewports are desktop Firefox responsive layout tests.',
            'Wheel metrics are not native touchscreen scroll inertia.',
            'set_content tests bundled scripts, not Android file-viewer policies.',
        ],
        'browsers':{},
    }
    with sync_playwright() as p:
        for engine in args.browsers:
            kind=getattr(p,engine)
            kwargs={'headless':True}
            if engine=='chromium' and not Path(kind.executable_path).exists() and Path('/usr/bin/chromium').exists():
                kwargs.update(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
            if not Path(kwargs.get('executable_path',kind.executable_path)).exists():
                out['browsers'][engine]={'status':'SKIP','reason':'Browser binary not installed'}
                print(f'{engine}: SKIP (browser binary not installed)',flush=True)
                continue
            try:
                browser=kind.launch(**kwargs)
            except PlaywrightError as exc:
                out['browsers'][engine]={'status':'SKIP','reason':str(exc)[:350]}
                print(f'{engine}: SKIP (launch error)',flush=True)
                continue
            with browser:
                cases=[]
                for viewport in args.viewports:
                    result=run_case(browser,engine,viewport,CASES[viewport],html)
                    cases.append(result)
                    extra=f' {result.get("error","")[:135]}' if result['status']=='FAIL' else ''
                    print(f'{engine:8} {viewport:12} {result["status"]}{extra}',flush=True)
                music=run_music(browser,engine,html)
                print(f'{engine:8} music        {music["status"]}',flush=True)
            ok=all(c['status']=='PASS' for c in cases) and music['status']=='PASS'
            out['browsers'][engine]={'status':'PASS' if ok else 'FAIL','cases':cases,'music':music}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(f'Report: {args.report}',flush=True)
    failed=any(v['status']=='FAIL' for v in out['browsers'].values())
    missing=args.require_all and any(v['status']=='SKIP' for v in out['browsers'].values())
    return 1 if failed or missing else 0


if __name__=='__main__':
    sys.exit(main())
