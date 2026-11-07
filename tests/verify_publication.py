"""Static publication smoke test; never mistakes generated URLs for live HTTPS deployment."""
import argparse
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'

def check(require_resume=False):
    failures=[]
    index=BeautifulSoup((DIST/'index.html').read_text(),'html.parser')
    shortcuts=index.select('.directory-shortcuts a[href]')
    links=index.select('.directory-links a[href]')
    if len(shortcuts)<3: failures.append('homepage missing direct public project links')
    if links and shortcuts and index.select_one('.directory-shortcuts').sourceline > index.select_one('.directory-links').sourceline:
        failures.append('direct work links are hidden after directory links in HTML')
    if not index.select_one('a[href$="work/agent-shield/"]'): failures.append('homepage missing AgentShield featured link')
    if 'secure ai integrations' not in index.get_text(' ',strip=True).lower():
        failures.append('homepage missing work positioning')
    for page in DIST.rglob('index.html'):
        doc=BeautifulSoup(page.read_text(),'html.parser')
        for selector,attr in [('link[rel=canonical]','href'),('meta[property="og:url"]','content'),('meta[property="og:image"]','content')]:
            tag=doc.select_one(selector)
            value=tag.get(attr,'') if tag else ''
            parsed=urlparse(value)
            if parsed.scheme!='https' or not parsed.netloc:
                failures.append(f'{page.relative_to(DIST)}: {selector} not absolute HTTPS')
        if not doc.select_one('meta[name="description"]'):
            failures.append(f'{page.relative_to(DIST)}: missing meta description')
    agent=(DIST/'work'/'agent-shield'/'index.html')
    if not agent.is_file(): failures.append('AgentShield article missing')
    else:
        a=BeautifulSoup(agent.read_text(),'html.parser')
        body=a.get_text(' ',strip=True)
        for marker in ['GPT-OSS 20B','1 / 1','0 / 1','68','v0.1.0','not evidence','no authorization denial']:
            if marker not in body: failures.append(f'AgentShield article missing evidence: {marker}')
        if not a.select_one('.shield-flow'): failures.append('AgentShield paired-run diagram missing')
    og=DIST/'assets'/'og-cover.png'
    if not og.is_file() or og.stat().st_size<1000: failures.append('missing OG image asset')
    resume=DIST/'resume.pdf'
    if require_resume and not resume.is_file(): failures.append('publication-approved resume.pdf missing')
    if resume.is_file() and not resume.read_bytes().startswith(b'%PDF-'):
        failures.append('downloadable resume.pdf is invalid')
    for route in ['contact','resume']:
        page=BeautifulSoup((DIST/route/'index.html').read_text(),'html.parser')
        for anchor in page.select('a[href$="resume.pdf"]'):
            if not resume.is_file(): failures.append(f'{route}: broken PDF download link')
    if resume.is_file():
        for route in ['', 'contact', 'resume']:
            page=BeautifulSoup(((DIST/route/'index.html') if route else (DIST/'index.html')).read_text(),'html.parser')
            if not page.select_one('a[href$="resume.pdf"]'):
                failures.append(f'{route or "home"}: missing résumé PDF link')
    about=(DIST/'about'/'index.html').read_text()
    for value in ['April 2026','February 2024','team-owned','OAuth2/PKCE']:
        if value not in about: failures.append(f'about: missing {value}')
    contact=(DIST/'contact'/'index.html').read_text()
    if 'Toronto' not in contact or 'open to conversations' not in contact:
        failures.append('contact missing location and availability')
    return failures

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--require-resume',action='store_true');args=p.parse_args()
    errors=check(args.require_resume)
    print(('PASS' if not errors else 'FAIL') + ': publication smoke test')
    for error in errors: print(' -',error)
    raise SystemExit(1 if errors else 0)
