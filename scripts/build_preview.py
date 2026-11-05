#!/usr/bin/env python3
"""Make a portable, offline HTML preview of every prerendered page."""
from pathlib import Path
import os
from bs4 import BeautifulSoup
import json, re, html, base64
ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
pages={}
for p in sorted(DIST.rglob('index.html')):
    route='/' if p==DIST/'index.html' else '/'+p.parent.relative_to(DIST).as_posix()+'/'
    doc=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    pages[route]={'title':doc.title.get_text(), 'content':str(doc.find('main').decode_contents())}
# Inline original SVG illustration so the offline preview needs no assets.
svg_path=DIST/'assets/field-study.png'
if svg_path.exists():
    embedded='data:image/png;base64,'+base64.b64encode(svg_path.read_bytes()).decode('ascii')
    for page in pages.values():
        page['content']=page['content'].replace('src="/assets/field-study.png"','src="'+embedded+'"')
base=BeautifulSoup((DIST/'index.html').read_text(),'html.parser')
# Embed styles and scripts to remove asset-server dependencies.
for n in base.select('link[rel="stylesheet"],script[src],link[rel="icon"],link[rel="canonical"],meta[property="og:image"]'):
    n.decompose()
style=base.new_tag('style');style.string=(DIST/'assets/styles.css').read_text();base.head.append(style)
# Keep the homepage rendered in the document as a progressive static fallback.
# Previous versions removed all <main> content before JavaScript started, so
# restrictive Android file viewers could display an empty, non-interactive site.
main=base.find('main')
for a in main.select('a[href^="/"]'):
    href=a.get('href','')
    a['href']='#'+href
noscript=base.new_tag('noscript')
noscript.string='Interactive elements require JavaScript. This file may open in a restricted document viewer on Android. Choose Open with Chrome/Firefox or serve the built site over HTTP.'
main.insert_before(noscript)
# Protect script contents from accidental HTML parsing.
payload=json.dumps(pages,ensure_ascii=True,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e')
script="""
(() => {
 const pages = __PAGE_DATA__;
 const target = document.getElementById('main');
 const convertLinks = (scope) => scope.querySelectorAll('a[href]').forEach(a => {
   const href=a.getAttribute('href');
   if (href && href.startsWith('/')) a.setAttribute('href','#'+href);
 });
 convertLinks(document.querySelector('header'));
 convertLinks(document.querySelector('footer'));
 document.querySelector('.skip-link').addEventListener('click',(e) => {e.preventDefault();target.setAttribute('tabindex','-1');target.focus();});
 function render(){
   const raw = location.hash.startsWith('#/') ? location.hash.slice(1) : '/';
   const [part, anchor] = raw.split('#');
   const path = part.replace(/\\/?$/, '/') || '/';
   const page = pages[path] || pages['/'];
   target.innerHTML=page.content;
   document.title=page.title;
   convertLinks(target);
   document.querySelectorAll('nav a').forEach(a => {
     const current=a.getAttribute('href').slice(1);
     if(path.startsWith(current) && current!=='/') a.setAttribute('aria-current','page');
     else a.removeAttribute('aria-current');
   });
   if(typeof initPortfolioExhibits === 'function') initPortfolioExhibits();
   if(typeof initializeField === 'function') initializeField();
   if(typeof initSculpture === 'function') initSculpture();
   if(typeof initMotionSystem === 'function') initMotionSystem();
   if(typeof initGallery === 'function') initGallery();
   if(typeof initMobileNav === 'function') initMobileNav();
   requestAnimationFrame(() => { if(anchor){const el=document.getElementById(anchor);if(el)el.scrollIntoView();}else window.scrollTo(0,0); });
 }
 window.addEventListener('hashchange',()=>{
   if(location.hash.startsWith('#/')) render();
   else if(location.hash.length>1){
      const id=decodeURIComponent(location.hash.slice(1));
      const node=document.getElementById(id);
      if(node) node.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
   }
 });
 render();
})();
""".replace('__PAGE_DATA__',payload)
js='\n'.join((DIST/'assets'/name).read_text() for name in ('site.js','sculpture.js','motion.js','gallery.js','nav.js','scroll.js','studio-effects.js'))
new_script=base.new_tag('script');new_script.string=js
base.body.append(new_script)
router=base.new_tag('script');router.string=script
base.body.append(router)
preview=Path(os.getenv('PREVIEW_OUTPUT', ROOT/'portfolio-preview.html'))
preview.write_text(str(base),encoding='utf-8')
print(f'Wrote {preview} with {len(pages)} pages, {len(preview.read_bytes())} bytes.')
