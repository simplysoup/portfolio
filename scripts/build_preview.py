#!/usr/bin/env python3
"""Single-file offline preview containing all prerendered pages, CSS and JS."""
from pathlib import Path
import os,json,base64
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]; DIST=ROOT/'dist'
pages={}
for p in DIST.rglob('index.html'):
    route='/' if p==DIST/'index.html' else '/'+p.parent.relative_to(DIST).as_posix()+'/'
    doc=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    pages[route]={'title':doc.title.get_text(),'content':str(doc.find('main').decode_contents())}
base=BeautifulSoup((DIST/'index.html').read_text(encoding='utf-8'),'html.parser')
for n in base.select('link[rel="stylesheet"],script[src],link[rel="icon"],link[rel="canonical"],meta[property="og:image"]'):n.decompose()
style=base.new_tag('style');style.string='\n'.join((DIST/'assets'/n).read_text() for n in ('styles.css','world.css','scrollchapters.css'));base.head.append(style)
# Convert static links even before script loads; the initial index remains in the HTML.
for a in base.select('a[href]'):
    href=a.get('href','')
    if href.startswith('/#'):a['href']='#'+href[2:]
    elif href.startswith('/'):a['href']='#'+href
# Ensure visual fallback artwork remains present when canvas cannot render.
base.find('main')['id']='main'
base.body.append(BeautifulSoup('<noscript><p style="padding:120px 7vw 0">This HTML preview requires a browser with JavaScript enabled for chapter transitions. The source project can also be hosted as an ordinary static website.</p></noscript>','html.parser'))
asset=(DIST/'assets'/'field-study.png')
if asset.exists():
    data='data:image/png;base64,'+base64.b64encode(asset.read_bytes()).decode('ascii')
    for p in pages.values():p['content']=p['content'].replace('src="/assets/field-study.png"','src="'+data+'"')
js='\n'.join((DIST/'assets'/n).read_text() for n in ('site.js','scrollchapters.js','world.js'))
raw=json.dumps(pages,ensure_ascii=True,separators=(',',':')).replace('<','\\u003c')
router=r'''(() => {
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
   const chapter=['systems','research','music','about'].includes(hash.slice(1));
   let name=hash.startsWith('#/')?hash.slice(1):'/';
   name=name.replace(/\/?$/,'/');
   const isHome=name==='/' || chapter;
   if(!pages[name])name='/';
   main.innerHTML=pages[name].content;document.title=pages[name].title;
   document.body.classList.toggle('is-home',isHome);
   document.body.classList.toggle('is-document',!isHome);
   convert(main);
   if(typeof window.initWorld==='function')window.initWorld();
   if(typeof initPortfolioExhibits==='function')initPortfolioExhibits();
   if(!isHome)window.scrollTo(0,0);
 }
 window.addEventListener('hashchange',()=>{
   if(location.hash.startsWith('#/') || ['#systems','#research','#music','#about'].includes(location.hash)){
     const onWorld=!!document.querySelector('[data-world]');
     if(location.hash.startsWith('#/') || !onWorld)route();
   }
 });
 if(location.hash.startsWith('#/'))route();
})();'''.replace('__PAGES__',raw)
for content in (js,router):
    script=base.new_tag('script');script.string=content.replace('</script','<\\/script');base.body.append(script)
output=Path(os.environ.get('PREVIEW_OUTPUT',ROOT/'OPEN_PORTFOLIO.html'))
output.write_text(str(base),encoding='utf-8')
print('Wrote',output,'bytes',output.stat().st_size)
