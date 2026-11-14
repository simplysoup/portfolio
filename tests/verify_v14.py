"""End-to-end verification for the generated v14 portfolio."""
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import re
import socket
import threading
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from _browser import launch

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "screenshots/v14/final"
VIEWPORTS = [(320, 640), (390, 844), (768, 1024), (853, 480), (1024, 768), (1440, 900), (1920, 600), (1920, 1080)]
SLUGS = ("trainstore", "piano-transcription", "casestruct-lora", "analytics-pipeline", "evaluated-rag", "agent-shield")
FORBIDDEN = ("envision", "mobilescapes", "esri", "52tb", "52 tb", "customer 360", "cortex", "onyx", "statistics canada", "six-figure", "6-figure")
results: list[tuple[str, bool, str]] = []


def check(name, fn):
    try:
        detail = fn()
        results.append((name, True, str(detail or "PASS")))
    except Exception as exc:  # keep running so the report lists all failed checks
        results.append((name, False, f"{type(exc).__name__}: {exc}"))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    routes = json.loads((DIST / "build-manifest.json").read_text(encoding="utf-8"))["routes"]
    server = ThreadingHTTPServer(("127.0.0.1", free_port()), lambda *a, **kw: QuietHandler(*a, directory=str(DIST), **kw))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as p:
            browser = launch(p)
            for width, height in VIEWPORTS:
                route_results = []
                page = browser.new_page(viewport={"width": width, "height": height})
                errors, external = [], []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
                page.on("request", lambda req: external.append(req.url) if urlparse(req.url).hostname not in ("127.0.0.1", "localhost") else None)
                for route in routes:
                    response = page.goto(base + route, wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    status = response.status if response else 0
                    okay = status == 200 and page.evaluate("document.documentElement.scrollWidth <= innerWidth") and page.evaluate('document.fonts.check(\'16px "Big Shoulders Display"\')')
                    route_results.append((route, width, okay, status, page.evaluate("document.documentElement.scrollWidth")))
                page.wait_for_timeout(50)
                check(f"routes × viewport {width}×{height}", lambda rr=[x for x in route_results if x[1] == width], e=errors, x=external: (
                    (_ for _ in ()).throw(AssertionError(f"route failures={[(r,w,s,sw) for r,w,ok,s,sw in rr if not ok]}; errors={e}; external={x}"))
                    if any(not row[2] for row in rr) or e or x else f"{len(rr)} routes HTTP 200, font loaded, no overflow/errors/external requests"))
                page.close()

            # Header controls sit between the outer rim and the header divider.
            for width, height in [(320, 640), (768, 1024), (1440, 900)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/", wait_until="networkidle")
                spacing = page.evaluate("""() => {
                  const rim = document.querySelector('body > .pointer-events-none.fixed').getBoundingClientRect();
                  const header = document.querySelector('body > header').getBoundingClientRect();
                  return [...document.querySelectorAll('header .btn-ghost')].filter(e => e.getClientRects().length).map(e => {
                    const r = e.getBoundingClientRect();
                    return {top: r.top - rim.top - 1, bottom: header.bottom - 1 - r.bottom};
                  });
                }""")
                check(f"header rim spacing {width}×{height}", lambda s=spacing: (s and all(x['top'] >= 0 and x['bottom'] >= 0 and abs(x['top'] - x['bottom']) <= 1 for x in s)) or (_ for _ in ()).throw(AssertionError(str(s))))
                page.close()

            # Hero fits common and non-standard viewports without covering its copy.
            for width, height in [(320, 640), (390, 844), (768, 1024), (1024, 768), (1440, 900), (1920, 600)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/", wait_until="networkidle")
                metrics = page.evaluate("""() => {
                  const rect = s => document.querySelector(s).getBoundingClientRect();
                  const hero = rect('#top'), copy = rect('.hero-copy'), art = rect('.hero-art'), name = rect('.hero-name-wrap');
                  return {bottom: hero.bottom, nameBottom: name.bottom,
                    overlap: copy.left < art.right && copy.right > art.left && copy.top < art.bottom && copy.bottom > art.top};
                }""")
                check(f"hero layout {width}×{height}", lambda m=metrics, h=height: (m['bottom'] <= h + 1 and m['nameBottom'] <= h + 1 and not m['overlap']) or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()

            # The original point artwork responds to pointer movement and keeps rendering.
            page = browser.new_page(viewport={"width": 1024, "height": 768})
            page.goto(base + "/", wait_until="networkidle")
            page.wait_for_timeout(500)
            art = page.locator('[data-hero-art]')
            before = art.evaluate("e => e.toDataURL()")
            box = art.bounding_box()
            page.mouse.move(box['x'] + box['width'] * .4, box['y'] + box['height'] * .4)
            page.mouse.move(box['x'] + box['width'] * .7, box['y'] + box['height'] * .55, steps=8)
            page.wait_for_timeout(250)
            after = art.evaluate("e => e.toDataURL()")
            check("hero artwork pointer interaction", lambda: (before != after and page.locator('.hero-art').evaluate("e => e.classList.contains('is-rendered')")) or (_ for _ in ()).throw(AssertionError("art did not update")))
            page.close()

            # A missing canvas implementation must leave the static fallback visible.
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.add_init_script("""(() => { const get = HTMLCanvasElement.prototype.getContext;
              HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                return this.hasAttribute('data-hero-art') ? null : get.call(this, type, ...args);
              }; })();""")
            page.goto(base + "/", wait_until="networkidle")
            page.wait_for_timeout(600)
            check("hero artwork fallback without canvas", lambda: (page.locator('.hero-art-fallback').is_visible() and not page.locator('.hero-art').evaluate("e => e.classList.contains('is-rendered')")) or (_ for _ in ()).throw(AssertionError("fallback hidden")))
            page.close()

            # Wordmark scales uniformly, filling the width when height permits.
            for width, height in [(320, 640), (375, 667), (390, 844), (1440, 900), (1920, 600)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/", wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(1600)
                m = page.evaluate("""() => { const el=document.querySelector('.hero-name'), n=el.getBoundingClientRect(), p=document.querySelector('.hero-name-wrap').getBoundingClientRect(); return {ratio:n.width/p.width, bottom:n.bottom, transform:getComputedStyle(el).transform}; }""")
                check(f"hero wordmark {width}×{height}", lambda m=m, h=height: (0 < m['ratio'] <= 1.02 and m['bottom'] <= h + 1 and m['transform'] == 'none') or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()

            # Outcome cards stay compact and readable on mobile.
            for width in (320, 390):
                page = browser.new_page(viewport={"width": width, "height": 844})
                page.goto(base + "/", wait_until="networkidle")
                m = page.evaluate("""() => [...document.querySelectorAll('.outcome-card')].map(card => {
                  const number = card.querySelector('.outcome-number').getBoundingClientRect();
                  const copy = card.querySelector('.outcome-copy').getBoundingClientRect();
                  return {height: card.getBoundingClientRect().height, separated: number.right <= copy.left, contained: copy.right <= card.getBoundingClientRect().right};
                })""")
                check(f"compact outcomes {width}px", lambda m=m: (len(m) == 6 and all(c['height'] < 160 and c['separated'] and c['contained'] for c in m)) or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()

            # Contact details and form share the viewport at desktop sizes.
            for width, height in [(1280, 633), (1440, 900)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/contact/", wait_until="networkidle")
                m = page.evaluate("""() => {
                  const form = document.querySelector('.contact-form').getBoundingClientRect();
                  const links = document.querySelector('.contact-links').getBoundingClientRect();
                  const name = document.querySelector('[name=name]').getBoundingClientRect();
                  const email = document.querySelector('[name=email]').getBoundingClientRect();
                  return {bottom: Math.max(form.bottom, links.bottom), aligned: Math.abs(name.top - email.top) < 1, inputHeight: name.height};
                }""")
                check(f"contact layout {width}×{height}", lambda m=m, h=height: (m['bottom'] <= h - 8 and m['aligned'] and m['inputHeight'] <= 44) or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()

            # The band moves with scrolling, then comes to rest.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base + "/", wait_until="networkidle")
            page.evaluate("scrollTo({top:650,behavior:'instant'})")
            page.wait_for_timeout(1300)
            band_before = page.locator('[data-motion-track]').evaluate('e => getComputedStyle(e).transform')
            page.wait_for_timeout(500)
            band_idle = page.locator('[data-motion-track]').evaluate('e => getComputedStyle(e).transform')
            page.evaluate("scrollTo({top:900,behavior:'instant'})")
            page.wait_for_timeout(1300)
            band_after = page.locator('[data-motion-track]').evaluate('e => getComputedStyle(e).transform')
            check("band follows scroll and rests", lambda: (band_before == band_idle and band_after != band_before) or (_ for _ in ()).throw(AssertionError(f'{band_before} / {band_idle} / {band_after}')))
            card = page.locator('.motion-copy').first
            page.evaluate("scrollTo({top:0,behavior:'instant'})")
            page.wait_for_timeout(200)
            hidden_opacity = float(card.evaluate("e => getComputedStyle(e).opacity"))
            page.evaluate("""() => { const r=document.querySelector('.motion-copy').getBoundingClientRect(); scrollTo({top:scrollY+r.top-innerHeight*.55,behavior:'instant'}); }""")
            page.wait_for_timeout(300)
            shown_opacity = float(card.evaluate("e => getComputedStyle(e).opacity"))
            check("description reveal follows scroll", lambda: (hidden_opacity < shown_opacity and shown_opacity > .95) or (_ for _ in ()).throw(AssertionError(f'{hidden_opacity} / {shown_opacity}')))
            page.close()

            # Section structure and active section nav.
            for width in (390, 1440, 1920):
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.goto(base + "/", wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                if width == 390:
                    check("home required sections and removed off-clock copy", lambda pg=page: (all(pg.locator('#'+s).count() for s in ('about','work','research','contact')) and not pg.get_by_text("Off the clock", exact=True).count()) or (_ for _ in ()).throw(AssertionError("required section missing or off-clock content present")))
                if width == 1440:
                    for section in ("about", "work", "research", "contact"):
                        page.evaluate("id => { const y=document.getElementById(id).getBoundingClientRect().top+scrollY-innerHeight*.355; scrollTo({top:y,behavior:'instant'}); }", section)
                        page.wait_for_timeout(200)
                        active = page.locator(f'[data-nav="{section}"]').get_attribute("aria-current")
                        check(f"nav active at #{section}", lambda a=active, s=section: a == "true" or (_ for _ in ()).throw(AssertionError(f"aria-current={a}")))
                if width in (390, 1440):
                    page.screenshot(path=str(OUT / f"home-{width}.png"), full_page=True)
                page.close()

            # Mobile menu click / keyboard operation and focus restoration.
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(base + "/", wait_until="networkidle")
            button = page.locator("[data-menu-toggle]")
            button.click()
            check("mobile menu opens by click", lambda: page.locator("#site-menu").is_visible() or (_ for _ in ()).throw(AssertionError("menu did not open")))
            page.keyboard.press("Escape")
            check("mobile menu Esc closes and restores focus", lambda: (page.locator("#site-menu").is_hidden() and button.evaluate("e => e === document.activeElement")) or (_ for _ in ()).throw(AssertionError("close/focus restoration failed")))
            button.focus(); page.keyboard.press("Enter")
            check("mobile menu opens by Enter", lambda: (page.locator("#site-menu").is_visible() and page.evaluate("document.activeElement.closest('#site-menu') !== null")) or (_ for _ in ()).throw(AssertionError("keyboard open/focus failed")))
            page.keyboard.press("Escape"); page.close()

            # Rail transform and card sizing at desktop; progressive fallback at reduced motion/mobile.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base + "/", wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            check("work rail desktop active", lambda: page.locator("html").evaluate("e => e.classList.contains('rail-on')") or (_ for _ in ()).throw(AssertionError("rail-on absent")))
            rail_data = page.evaluate("""() => {
              const w=document.querySelector('[data-rail-wrapper]'), v=document.querySelector('[data-rail-viewport]'), t=document.querySelector('[data-rail-track]');
              return {top:w.getBoundingClientRect().top+scrollY, range:w.offsetHeight-v.offsetHeight-56, distance:t.scrollWidth-v.clientWidth,
                cards:[...document.querySelectorAll('.rail-card')].map(c=>{const r=c.getBoundingClientRect();return {center:r.left+r.width/2, top:r.top,bottom:r.bottom}}), vw:v.clientWidth};
            }""")
            transforms = []
            for fraction in (0, .5, 1):
                page.evaluate("({top,range,p})=>scrollTo({top:top-56+p*range,behavior:'instant'})", {"top": rail_data["top"], "range": rail_data["range"], "p": fraction})
                page.wait_for_timeout(120)
                transforms.append(page.locator("[data-rail-track]").evaluate("e => new DOMMatrixReadOnly(getComputedStyle(e).transform).m41"))
            check("work rail transform monotonic", lambda: (transforms[0] >= transforms[1] >= transforms[2] and transforms[0] > transforms[2]) or (_ for _ in ()).throw(AssertionError(f"x positions {transforms}")))
            for index, card in enumerate(rail_data["cards"]):
                pcent = max(0, min(1, (card["center"] - rail_data["vw"] / 2) / rail_data["distance"]))
                page.evaluate("({top,range,p})=>scrollTo({top:top-56+p*range,behavior:'instant'})", {"top": rail_data["top"], "range": rail_data["range"], "p": pcent})
                page.wait_for_timeout(80)
                box = page.locator(".rail-card").nth(index).bounding_box()
                check(f"rail card {index+1} fits viewport at center", lambda b=box: (b and b["y"] >= 0 and b["y"] + b["height"] <= 900) or (_ for _ in ()).throw(AssertionError(f"card box={b}")))
            page.emulate_media(reduced_motion="reduce"); page.wait_for_timeout(300)
            check("reduced-motion work rail grid", lambda: (not page.locator("html").evaluate("e=>e.classList.contains('rail-on')") and page.locator(".rail-card").count() == 6) or (_ for _ in ()).throw(AssertionError("rail did not fall back to 6-card grid")))
            page.close()
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(base + "/", wait_until="networkidle")
            check("mobile work rail disabled", lambda: not page.locator("html").evaluate("e=>e.classList.contains('rail-on')") or (_ for _ in ()).throw(AssertionError("rail-on on mobile")))
            page.close()

            # Reduced motion suppresses marquee and recurring canvas RAF loops.
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            page.add_init_script("""(() => { const raf=window.requestAnimationFrame.bind(window); window.__rafRequests=0; window.requestAnimationFrame=(fn)=>{window.__rafRequests++;return raf(fn)}; })();""")
            page.goto(base + "/", wait_until="networkidle")
            page.wait_for_timeout(1000)
            before = page.evaluate("window.__rafRequests")
            page.wait_for_timeout(500)
            check("reduced-motion band and canvas RAF", lambda: (page.locator("[data-motion-track]").evaluate("e=>getComputedStyle(e).transform") == "none" and page.evaluate("window.__rafRequests") == before) or (_ for _ in ()).throw(AssertionError(f"raf={page.evaluate('window.__rafRequests')}")))
            page.close()

            # Contact uses a local submit dispatch so no mail client is launched.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base + "/", wait_until="networkidle")
            form = page.locator("form[data-mailto]")
            form.locator('[name="name"]').fill("Verification Name")
            form.locator('[name="email"]').fill("verify@example.test")
            form.locator('[name="message"]').fill("Verification message")
            page.evaluate("document.querySelector('form[data-mailto]').dispatchEvent(new SubmitEvent('submit',{bubbles:true,cancelable:true}))")
            mailto = form.get_attribute("data-last-mailto") or ""
            check("contact mailto encodes submitted name", lambda: (mailto.startswith("mailto:") and "Verification%20Name" in mailto) or (_ for _ in ()).throw(AssertionError(f"data-last-mailto={mailto}")))
            page.close()

            # Articles: heading, real TOC targets, responsive labeled tables, interactive exhibits.
            for slug in SLUGS + ("/research/trend-dependencies/",):
                route = slug if slug.startswith("/") else f"/work/{slug}/"
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                exhibit_errors = []
                page.on("pageerror", lambda error: exhibit_errors.append(str(error)))
                page.on("console", lambda message: exhibit_errors.append(message.text) if message.type == "error" else None)
                page.goto(base + route, wait_until="networkidle")
                check(f"article {route} h1 and TOC", lambda pg=page: (pg.locator("h1").count() == 1 and pg.locator("nav[aria-label='On this page'] a").count() > 0 and all(pg.locator("#" + pg.locator("nav[aria-label='On this page'] a").nth(i).get_attribute("href").lstrip("#")).count() == 1 for i in range(pg.locator("nav[aria-label='On this page'] a").count()))) or (_ for _ in ()).throw(AssertionError("h1/TOC target absent")))
                page.screenshot(path=str(OUT / (route.strip("/").replace("/", "-") + ".png")))
                if route.endswith("evaluated-rag/"):
                    for option in page.locator('[data-exhibit="rag"] [data-case]').all(): option.click()
                    check("RAG exhibit interaction", lambda pg=page, errors=exhibit_errors: (pg.locator('[data-exhibit="rag"] #rag-answer').inner_text().strip() != "" and not errors) or (_ for _ in ()).throw(AssertionError(f"RAG output/errors={errors}")))
                if route.endswith("trend-dependencies/"):
                    slider = page.locator("#trend-noise")
                    slider.fill(slider.get_attribute("max"))
                    check("trend lab interaction", lambda pg=page, errors=exhibit_errors: (pg.locator("#trend-chart path").count() >= 2 and not errors) or (_ for _ in ()).throw(AssertionError(f"trend chart/errors={errors}")))
                page.close()
            page = browser.new_page(viewport={"width": 390, "height": 844})
            for route in (f"/work/{s}/" for s in SLUGS):
                page.goto(base + route, wait_until="networkidle")
                ok = page.evaluate("""() => document.documentElement.scrollWidth <= innerWidth && [...document.querySelectorAll('table td')].every(td=>td.hasAttribute('data-label'))""")
                check(f"mobile article tables {route}", lambda valid=ok: valid or (_ for _ in ()).throw(AssertionError("table labels/overflow check failed")))
            page.close()

            # Print-emulated résumé: use Chromium PDF page objects and actual computed print color.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base + "/resume/", wait_until="networkidle")
            page.emulate_media(media="print")
            pdf = page.pdf(format="Letter", print_background=True)
            pages = len(re.findall(rb"/Type\s*/Page\b", pdf))
            color = page.locator("body").evaluate("e=>getComputedStyle(e).color")
            check("resume print pages and black body text", lambda: (pages <= 3 and color in ("rgb(0, 0, 0)", "rgb(0,0,0)")) or (_ for _ in ()).throw(AssertionError(f"PDF pages={pages}, body color={color}")))
            page.screenshot(path=str(OUT / "resume.png"), full_page=True)
            page.close()

            # Offline file router, content navigation, back home, and inlined fonts.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            offline_errors, font_requests = [], []
            page.on("pageerror", lambda error: offline_errors.append(str(error)))
            page.on("console", lambda message: offline_errors.append(message.text) if message.type == "error" else None)
            page.on("request", lambda req: font_requests.append(req.url) if ".woff" in req.url.lower() else None)
            page.goto((ROOT / "OPEN_PORTFOLIO.html").as_uri(), wait_until="networkidle")
            page.locator('a[href="#/work/trainstore/"]').first.click()
            page.wait_for_timeout(300)
            swapped = page.locator("main h1").count() == 1 and "trainstore" in page.locator("main h1").inner_text().lower()
            page.locator("header a").first.click(); page.wait_for_timeout(300)
            home_back = page.locator("main #top h1").count() == 1
            fonts_inline = page.evaluate("document.fonts.check('16px \\\"Big Shoulders Display\\\"')")
            check("offline file route, back home, inlined fonts", lambda: (swapped and home_back and fonts_inline and not font_requests and not offline_errors) or (_ for _ in ()).throw(AssertionError(f"swapped={swapped}, home={home_back}, fonts={fonts_inline}, font_requests={font_requests}, errors={offline_errors}")))
            page.close()
            browser.close()

        # Publication-safety scan includes all generated HTML files and the offline artifact.
        def safety():
            html_files = list(DIST.rglob("*.html")) + [ROOT / "OPEN_PORTFOLIO.html"]
            data_uri = re.compile(r"data:[^\s\"')]+;base64,[A-Za-z0-9+/=]+", re.IGNORECASE)
            hits = []
            for path in html_files:
                html = path.read_text(encoding="utf-8", errors="replace")
                source_without_data_uris = data_uri.sub("", html).lower()
                visible_text = BeautifulSoup(html, "html.parser").get_text().lower()
                hits.extend((str(path.relative_to(ROOT)), "html", term) for term in FORBIDDEN if term in source_without_data_uris)
                hits.extend((str(path.relative_to(ROOT)), "visible text", term) for term in FORBIDDEN if term in visible_text)
            if hits: raise AssertionError(f"publication-safety hits={hits}")
            return f"0 forbidden phrase hits in source and visible text across {len(html_files)} HTML files"
        check("publication safety scan", safety)
    finally:
        server.shutdown(); server.server_close()

    report()
    raise SystemExit(1 if any(not passed for _, passed, _ in results) else 0)


def report():
    print("\nCHECK                                      RESULT  DETAIL")
    print("-" * 110)
    for name, passed, detail in results:
        print(f"{name[:40]:40} {'PASS' if passed else 'FAIL':6}  {detail}")
    failed = sum(not passed for _, passed, _ in results)
    print(f"\n{len(results)-failed} passed, {failed} failed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        results.append(("verification runner", False, f"{type(exc).__name__}: {exc}"))
        report()
        raise SystemExit(1)
