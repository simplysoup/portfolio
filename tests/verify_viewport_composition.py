"""Geometric regression: every Directory and project scene must fit its viewport.

Unlike horizontal-overflow checks, this also catches content clipped by the
scene's overflow:hidden or the sticky viewport's bottom edge.

uv run python tests/verify_viewport_composition.py --require-all
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
import sys

from playwright.sync_api import sync_playwright, Error as PlaywrightError

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'OPEN_PORTFOLIO.html'
VIEWPORTS = {
    'ultrawide': (2560, 700),
    'wide-short': (1600, 600),
    'standard': (1440, 900),
    'laptop': (1366, 768),
    'compact-laptop': (1280, 720),
    'short-laptop': (1280, 550),
    'short-tablet-landscape': (1024, 600),
    'narrow-landscape': (820, 600),
    'short-landscape': (768, 480),
    'breakpoint-desktop': (701, 600),
    'breakpoint-mobile': (700, 750),
    'phone': (390, 844),
    'small-phone': (320, 568),
    'very-short-phone': (320, 480),
}

COMPOSITION_CHECK = r'''() => {
  const box = (el) => {
    const r = el.getBoundingClientRect();
    return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};
  };
  const q = s => box(document.querySelector(s));
  const stage = q('.directory-stage');
  const last = q('.directory-link:last-child');
  const shortcuts = q('.directory-shortcuts');
  const cue = q('.directory-scroll-cue');
  const floor = q('.directory-floor');
  const errors = [];
  if (document.documentElement.scrollWidth > innerWidth + 1)
    errors.push('horizontal overflow');
  const tinyIndex = matchMedia('(max-width:700px) and (max-height:520px)').matches;
  if (!tinyIndex && Math.abs(stage.bottom - innerHeight) > 2)
    errors.push('directory does not occupy exactly one viewport');
  // Public project links precede the four-door directory in the v14 layout.
  if (shortcuts.bottom > document.querySelector('.directory-links').getBoundingClientRect().top + 2)
    errors.push('selected work overlaps directory navigation');
  const actions = q('.directory-action-row');
  if (last.bottom > actions.top + 2)
    errors.push('directory navigation overlaps action links');
  if (actions.bottom > floor.top + 2)
    errors.push('action links overlap footer');
  if (shortcuts.bottom > innerHeight + 2 && !tinyIndex)
    errors.push('featured projects are below the first viewport');
  if (floor.bottom > stage.bottom + 2)
    errors.push('directory footer clipped');
  if (innerWidth <= 1100 && getComputedStyle(document.querySelector('.dir-desc')).display !== 'none')
    errors.push('compact directory descriptions were not hidden');
  return {errors, stage:stage.bottom, floor:floor.bottom};
}'''

PROJECT_CHECK = r'''key => {
  const root = document.querySelector(`[data-folio="${key}"]`);
  const box = selector => {
    const r = root.querySelector(selector).getBoundingClientRect();
    return {top:r.top,bottom:r.bottom,left:r.left,right:r.right};
  };
  const screen = box('.folio-screen');
  const top = box('.folio-topline');
  const overline = box('.folio-overline');
  const heading = box('h2');
  const prose = box('.folio-copy p');
  const link = box('.folio-link');
  const art = box('.folio-visual');
  const footer = box('.folio-floor');
  const errors = [];
  const tinyPortrait = matchMedia('(max-width:700px) and (max-height:540px)').matches;
  if (!tinyPortrait && (screen.top < -2 || screen.bottom > innerHeight + 2))
    errors.push('sticky screen exceeds viewport');
  if (top.bottom > overline.top + 3)
    errors.push('topline overlaps overline');
  if (overline.bottom > heading.top + 3)
    errors.push('overline overlaps heading');
  if (heading.bottom > prose.top + 3)
    errors.push('heading overlaps prose');
  if (prose.bottom > link.top + 3)
    errors.push('prose overlaps link');
  if (link.bottom > footer.top + 3)
    errors.push('link overlaps footer');
  if (art.bottom > footer.top + 3)
    errors.push('artwork overlaps footer');
  if (innerWidth <= 700 && link.bottom > art.top + 3)
    errors.push('mobile link overlaps artwork');
  if (innerWidth > 700 && link.right > art.left + 3)
    errors.push('columns overlap horizontally');
  if (document.documentElement.scrollWidth > innerWidth + 1)
    errors.push('horizontal overflow');
  return {errors, linkBottom:Math.round(link.bottom),
          artBottom:Math.round(art.bottom), footerTop:Math.round(footer.top)};
}'''


def check_case(browser, engine, label, width, height, html):
    mobile = width <= 700 and engine != 'firefox'
    page = browser.new_page(viewport={'width':width,'height':height},
                            is_mobile=mobile, has_touch=mobile,
                            device_scale_factor=1)
    failures = []
    page_errors = []
    page.on('pageerror', lambda error: page_errors.append(str(error)))
    try:
        page.set_content(html, wait_until='domcontentloaded', timeout=15000)
        page.wait_for_timeout(60)
        directory = page.evaluate(COMPOSITION_CHECK)
        if directory['errors']:
            failures.append({'directory':directory['errors']})
        projects = {}
        for key in ('rag','pipeline','thesis','piano'):
            page.locator(f'[data-folio="{key}"]').evaluate(
                '(el) => el.scrollIntoView({block:"start", behavior:"instant"})'
            )
            # WebKit animates the scroll-snap settle for a few hundred ms
            # after scrollIntoView, and the entry animation runs off it:
            # measuring at a fixed 35ms catches --entry near 0, which
            # translates the artwork down by up to 88px, so it reads as
            # overlapping the footer even though the settled layout fits
            # (verified: entry reaches 1.0 by 100-300ms in WebKit, and the
            # artwork then sits 12-55px clear of the footer). Wait for the
            # scene to settle at --entry 1 before measuring geometry.
            for _ in range(20):
                entry = page.locator(f'[data-folio="{key}"]').evaluate(
                    '(el)=>parseFloat(getComputedStyle(el).getPropertyValue("--entry"))||0')
                if entry >= 0.99:
                    break
                page.wait_for_timeout(100)
            project = page.evaluate(PROJECT_CHECK, key)
            projects[key] = project
            if project['errors']:
                failures.append({key:project['errors']})
        if page_errors:
            failures.append({'page_errors':page_errors})
        return {'status':'PASS' if not failures else 'FAIL',
                'viewport':[width,height], 'directory':directory,
                'projects':projects, 'failures':failures}
    except Exception as exc:
        return {'status':'FAIL', 'viewport':[width,height], 'failures':[str(exc)]}
    finally:
        page.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browsers', nargs='+', default=['chromium','firefox','webkit'],
                        choices=['chromium','firefox','webkit'])
    parser.add_argument('--require-all',action='store_true')
    parser.add_argument('--report',type=Path,default=ROOT/'viewport-composition-report.json')
    args=parser.parse_args()
    html=HTML.read_text(encoding='utf-8')
    report={'checked_at':datetime.now(timezone.utc).isoformat(), 'browsers':{}}
    with sync_playwright() as p:
        for engine in args.browsers:
            browser_type = getattr(p, engine)
            kwargs = {'headless':True}
            if engine=='chromium' and not Path(browser_type.executable_path).exists() and Path('/usr/bin/chromium').exists():
                kwargs.update({'executable_path':'/usr/bin/chromium',
                               'args':['--no-sandbox','--disable-dev-shm-usage']})
            if not Path(kwargs.get('executable_path',browser_type.executable_path)).exists():
                report['browsers'][engine]={'status':'SKIP','reason':'Browser binary is not installed'}
                print(f'{engine}: SKIP (browser unavailable)',flush=True)
                continue
            try:
                browser=browser_type.launch(**kwargs)
            except PlaywrightError as exc:
                report['browsers'][engine]={'status':'SKIP','reason':str(exc)[:300]}
                print(f'{engine}: SKIP (cannot launch)',flush=True)
                continue
            with browser:
                results={}
                for label,(width,height) in VIEWPORTS.items():
                    result=check_case(browser,engine,label,width,height,html)
                    results[label]=result
                    print(f'{engine:8} {label:24} {result["status"]}',flush=True)
            status='PASS' if all(r['status']=='PASS' for r in results.values()) else 'FAIL'
            report['browsers'][engine]={'status':status,'cases':results}
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    failed=any(row['status']=='FAIL' for row in report['browsers'].values())
    missing=args.require_all and any(row['status']=='SKIP' for row in report['browsers'].values())
    print('Report:',args.report,flush=True)
    return 1 if failed or missing else 0

if __name__ == '__main__':
    sys.exit(main())
