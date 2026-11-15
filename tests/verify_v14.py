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

            # Homepage order: work first, then concise experience, then about/research.
            # The project index lists all six projects and the first three are featured,
            # led by AgentShield and Evaluated RAG ahead of TrainStore.
            for width in (390, 1440):
                page = browser.new_page(viewport={"width": width, "height": 900})
                page.goto(base + "/", wait_until="networkidle")
                m = page.evaluate("""() => {
                  const order = [...document.querySelectorAll('#work, #about, #research, #contact')].map(e => e.id);
                  const cards = [...document.querySelectorAll('.rail-card')].map(c => c.querySelector('h3').textContent.trim());
                  const index = [...document.querySelectorAll('nav[aria-label="Project index"] a')].map(a => a.getAttribute('href'));
                  const targets = index.map(h => !!document.querySelector(h));
                  const featured = [...document.querySelectorAll('.rail-card')].slice(0, 3).map(c => c.textContent.includes('Featured'));
                  return {order, cards, index, targets, featured, rail: document.documentElement.classList.contains('rail-on')};
                }""")
                check(f"homepage order and project index {width}px", lambda m=m: (m['order'] == ['work', 'about', 'research', 'contact'] and m['cards'][:3] == ['AgentShield', 'Evaluated RAG', 'TrainStore'] and len(m['index']) == 6 and all(m['targets']) and all(m['featured']) and not m['rail']) or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()

            # Contact offers a direct email button instead of a mailto form.
            for width, height in [(1280, 633), (1440, 900)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/contact/", wait_until="networkidle")
                m = page.evaluate("""() => {
                  const btn = document.querySelector('.contact-email a[href^="mailto:"]');
                  const section = document.querySelector('#contact').getBoundingClientRect();
                  return {href: btn?.getAttribute('href'), text: btn?.textContent.trim(), form: !!document.querySelector('form[data-mailto]'), bottom: section.bottom};
                }""")
                check(f"contact email button {width}x{height}", lambda m=m, h=height: (m['href'] == "mailto:nickbode71@gmail.com" and not m['form'] and m['bottom'] <= h - 8) or (_ for _ in ()).throw(AssertionError(str(m))))
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
            # Expertise (and its .motion-copy rows) now lives on /about/; the homepage
            # reveal check uses the about statement instead.
            card = page.locator('#about [data-scroll-reveal]').first
            page.evaluate("scrollTo({top:0,behavior:'instant'})")
            page.wait_for_timeout(200)
            hidden_opacity = float(card.evaluate("e => getComputedStyle(e).opacity"))
            page.evaluate("""() => { const r=document.querySelector('#about [data-scroll-reveal]').getBoundingClientRect(); scrollTo({top:scrollY+r.top-innerHeight*.55,behavior:'instant'}); }""")
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
                        # IntersectionObserver delivery can lag under load; wait for the
                        # nav state instead of sampling it on a fixed short delay.
                        page.wait_for_function("s => document.querySelector(`[data-nav='${s}']`)?.getAttribute('aria-current') === 'true'", arg=section, timeout=5000)
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

            # Work is a plain grid with a visible project index at every width:
            # no horizontal rail, no rail-on class, all six cards present.
            for width, height in [(1440, 900), (390, 844)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(base + "/", wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                m = page.evaluate("""() => ({
                  rail: document.documentElement.classList.contains('rail-on'),
                  cards: document.querySelectorAll('.rail-card').length,
                  grid: getComputedStyle(document.querySelector('#work .grid')).display === 'grid',
                  first: document.querySelector('.rail-card h3')?.textContent.trim(),
                })""")
                check(f"work grid {width}x{height}", lambda m=m: (not m['rail'] and m['cards'] == 6 and m['grid'] and m['first'] == 'AgentShield') or (_ for _ in ()).throw(AssertionError(str(m))))
                page.close()
            page = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
            page.goto(base + "/", wait_until="networkidle")
            check("reduced-motion work grid visible", lambda: (page.locator(".rail-card").count() == 6 and all(float(page.locator(".rail-card").nth(i).evaluate("e => getComputedStyle(e).opacity")) > 0.9 for i in range(6))) or (_ for _ in ()).throw(AssertionError("cards hidden under reduced motion")))
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

            # Contact section links straight to email with no form in between.
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(base + "/", wait_until="networkidle")
            check("contact email button on homepage", lambda: (page.locator('#contact a[href="mailto:nickbode71@gmail.com"]').count() >= 1 and page.locator("form[data-mailto]").count() == 0) or (_ for _ in ()).throw(AssertionError("email button missing or mailto form still present")))
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
                if route.startswith("/work/"):
                    check(f"article {route} at-a-glance summary", lambda pg=page: (pg.locator(".at-a-glance").count() == 1 and [pg.locator(".at-a-glance dt").nth(i).text_content() for i in range(5)] == ["Problem", "What I built", "Key result", "Main limitation", "Evidence"]) or (_ for _ in ()).throw(AssertionError("at-a-glance summary missing or incomplete")))
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
            check("resume PDF download link", lambda: (page.locator('a[href$="nicholas-bode-resume.pdf"]').count() == 1) or (_ for _ in ()).throw(AssertionError("downloadable resume PDF link missing")))
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
