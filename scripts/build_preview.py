#!/usr/bin/env python3
"""Build a single-file offline preview containing the site, styles, scripts and images."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import base64
import json
import os
import re
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
pages = {}


def local_asset(url):
    """Resolve a root-relative URL inside dist, refusing path traversal."""
    path = unquote(urlsplit(url).path)
    if not path.startswith('/'):
        return None
    candidate = (DIST / path.lstrip('/')).resolve()
    if not candidate.is_relative_to(DIST.resolve()):
        return None
    return candidate


def inline_images(markup):
    def replace(match):
        url = match.group(1)
        path = local_asset(url)
        if path is None or path.suffix.lower() not in ('.png', '.svg') or not path.is_file():
            return match.group(0)
        media = 'image/png' if path.suffix.lower() == '.png' else 'image/svg+xml'
        data = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'data:{media};base64,{data}'

    return re.sub(r'(?<![\w])(/assets/[^\s\"\'<>)]*?\.(?:png|svg)(?:\?[^\s\"\'<>)]*)?)', replace, markup, flags=re.I)


def inline_font_urls(css, stylesheet_url):
    stylesheet = local_asset(stylesheet_url)
    stylesheet_dir = stylesheet.parent if stylesheet else DIST

    def replace(match):
        url = match.group(2).strip()
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith('.woff2'):
            return match.group(0)
        path = local_asset(url) if parsed.path.startswith('/') else (stylesheet_dir / unquote(parsed.path)).resolve()
        if path is None or not path.is_file() or 'fonts' not in path.parts:
            return match.group(0)
        data = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'url("data:font/woff2;base64,{data}")'

    return re.sub(r"url\(\s*(['\"]?)(.*?)\1\s*\)", replace, css, flags=re.I)


for page_path in DIST.rglob('index.html'):
    route = '/' if page_path == DIST / 'index.html' else '/' + page_path.parent.relative_to(DIST).as_posix() + '/'
    doc = BeautifulSoup(page_path.read_text(encoding='utf-8'), 'html.parser')
    pages[route] = {
        'title': doc.title.get_text() if doc.title else '',
        'content': inline_images(str(doc.find('main').decode_contents())) if doc.find('main') else '',
    }

base = BeautifulSoup((DIST / 'index.html').read_text(encoding='utf-8'), 'html.parser')
styles = []
local_scripts = []
first_style = None
for node in list(base.find_all(['link', 'script'])):
    if node.name == 'link' and 'preload' in (node.get('rel') or []) and node.get('as') == 'font':
        node.decompose()
    elif node.name == 'link' and 'stylesheet' in (node.get('rel') or []) and (node.get('href') or '').startswith('/'):
        href = node['href']
        path = local_asset(href)
        if path and path.is_file():
            styles.append(inline_font_urls(path.read_text(encoding='utf-8'), href))
            if first_style is None:
                first_style = base.new_tag('style')
                node.replace_with(first_style)
            else:
                node.decompose()
    elif node.name == 'script' and node.get('src', '').startswith('/'):
        path = local_asset(node['src'])
        if path and path.is_file():
            local_scripts.append(path.read_text(encoding='utf-8'))
            node.decompose()

if styles:
    if first_style is None:
        first_style = base.new_tag('style')
        base.head.append(first_style)
    first_style.string = '\n'.join(styles)

# The initial document also displays content before the router handles navigation.
main = base.find('main')
if main:
    main['id'] = 'main'
    initial_content = BeautifulSoup(inline_images(main.decode_contents()), 'html.parser')
    main.clear()
    main.append(initial_content)

# Convert static links even before the router runs; external links remain unchanged.
for anchor in base.select('a[href]'):
    href = anchor.get('href', '')
    if href.startswith('/#'):
        anchor['href'] = '#' + href[2:]
    elif href.startswith('/'):
        anchor['href'] = '#' + href

if base.body:
    base.body.append(BeautifulSoup('<noscript><p style="padding:120px 7vw 0">This HTML preview requires a browser with JavaScript enabled for chapter transitions. The source project can also be hosted as an ordinary static website.</p></noscript>', 'html.parser'))

raw = json.dumps(pages, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
router = r'''(() => {
 const pages=__PAGES__;
 const main=document.getElementById('main');
 function convert(scope){
   scope.querySelectorAll('a[href]').forEach(a=>{
     const h=a.getAttribute('href');
     if(h.startsWith('/#'))a.setAttribute('href','#'+h.slice(2));
     else if(h.startsWith('/'))a.setAttribute('href','#'+h);
   });
 }
 function route(){
   let hash=location.hash;
   const chapter=['top','about','work','research','contact'].includes(hash.slice(1));
   let name=hash.startsWith('#/')?hash.slice(1):'/';
   name=name.replace(/\/?$/,'/');
   const isHome=name==='/' || chapter;
   if(!pages[name])name='/';
   main.innerHTML=pages[name].content;document.title=pages[name].title;
   document.body.classList.toggle('is-home',isHome);
   document.body.classList.toggle('is-document',!isHome);
   convert(main);
   window.initSite?.();
   window.initArt?.();
   window.initWorld?.();
   window.initPortfolioExhibits?.();
   if(!isHome)window.scrollTo(0,0);
   else if(chapter) document.getElementById(hash.slice(1))?.scrollIntoView();
 }
 window.addEventListener('hashchange',()=>{
   if(location.hash.startsWith('#/') || ['#top','#about','#work','#research','#contact'].includes(location.hash)){
     const onHome=!!main.querySelector('#top');
     if(location.hash.startsWith('#/') || !onHome)route();
   }
 });
 if(location.hash.startsWith('#/'))route();
})();'''.replace('__PAGES__', raw)

if base.body:
    for content in (*local_scripts, router):
        script = base.new_tag('script')
        script.string = content.replace('</script', '<\\/script')
        base.body.append(script)

output = Path(os.environ.get('PREVIEW_OUTPUT', ROOT / 'OPEN_PORTFOLIO.html'))
output.write_text(inline_images(str(base)), encoding='utf-8')
print('Wrote', output, 'bytes', output.stat().st_size)
