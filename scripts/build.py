#!/usr/bin/env python3
"""Build the dependency-light, static engineering portfolio.

All public article content lives in content/work and content/research.
Professional drafts are kept outside the public project directory.
"""
from pathlib import Path
from datetime import date
from html import escape
import json, os, re, shutil, xml.etree.ElementTree as ET
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
BASE='/' + os.getenv('SITE_BASE','').strip('/')
if BASE!='/' : BASE += '/'
SITE_URL=os.getenv('SITE_URL','https://example.com').rstrip('/')
assert BASE.startswith('/') and BASE.endswith('/')

MD=MarkdownIt('commonmark',{'html':False,'linkify':False}).enable('table')
ENV=Environment(loader=FileSystemLoader(ROOT/'templates'),autoescape=select_autoescape(['html','xml']),trim_blocks=True,lstrip_blocks=True)

work_order=['evaluated-rag','analytics-pipeline','piano-transcription']

SITE={
 'name':'Nicholas Bode',
 'description':'Nicholas Bode is an AI engineer in Toronto working on AI applications, model evaluation, data systems, and time-series research.',
 'email':'nickbode71@gmail.com',
 'github':'https://github.com/simplysoup',
 'linkedin':'https://www.linkedin.com/in/nicholas-bode-6a29ab1bb/',
 'thesis':'https://ontariotechu.scholaris.ca/server/api/core/bitstreams/af2acd24-e895-43e3-8781-b04aca070e66/content',
 'publication':'https://doi.org/10.1007/978-3-031-23161-2_501',
}

def parse_md(path):
 text=path.read_text(encoding='utf-8')
 match=re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$',text,re.S)
 if not match: raise ValueError(f'Missing YAML front matter: {path}')
 meta=yaml.safe_load(match.group(1))
 meta['slug']=path.stem
 meta['body']=MD.render(match.group(2))
 return meta

WORK={p.stem:parse_md(p) for p in (ROOT/'content/work').glob('*.md')}
RESEARCH={p.stem:parse_md(p) for p in (ROOT/'content/research').glob('*.md')}
PUBLIC_WORK={k:v for k,v in WORK.items() if v.get('public') is True}
PUBLIC_RESEARCH={k:v for k,v in RESEARCH.items() if v.get('public') is True}

def route_url(path):
 return BASE + path.strip('/') + ('/' if path.strip('/') else '')

def render(route, template, **context):
 filename=OUT/route.strip('/')/'index.html' if route.strip('/') else OUT/'index.html'
 filename.parent.mkdir(parents=True,exist_ok=True)
 full_url=SITE_URL + route_url(route)
 rendered=ENV.get_template(template).render(site=SITE, base=BASE, route=route, url=full_url, route_url=route_url,
                                               work=PUBLIC_WORK,research=PUBLIC_RESEARCH,**context)
 filename.write_text(rendered,encoding='utf-8')

if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir(parents=True)
shutil.copytree(ROOT/'assets',OUT/'assets')

render('', 'index.html', title='AI engineer and applied research',description=SITE['description'], nav='home')
render('work','work.html',title='Selected engineering work', description='Applied AI, evaluation, and systems engineering projects by Nicholas Bode.',nav='work')
for slug,article in PUBLIC_WORK.items():
 render('work/'+slug,'article.html',title=article['title'],description=article['description'],nav='work',article=article,kind='work')
render('research','research.html',title='Research & writing',description='Original MSc research on trend dependencies and work in accessible AI.',nav='research')
for slug,article in PUBLIC_RESEARCH.items():
 render('research/'+slug,'article.html',title=article['title'],description=article['description'],nav='research',article=article,kind='research')
render('about','about.html',title='About',description='Engineering perspective, background, and research interests.',nav='about')
render('contact','contact.html',title='Contact',description='Contact Nicholas Bode about applied AI engineering and research.',nav='contact')
render('resume','resume.html',title='Résumé',description='Professional background and résumé availability.',nav='resume')

paths=['','work','research','about','contact','resume']+[f'work/{s}' for s in PUBLIC_WORK]+[f'research/{s}' for s in PUBLIC_RESEARCH]
# Sitemap must not advertise placeholder domain: a real SITE_URL is required.
if SITE_URL!='https://example.com':
 ns='http://www.sitemaps.org/schemas/sitemap/0.9'
 root=ET.Element('urlset',xmlns=ns)
 for p in paths:
  u=ET.SubElement(root,'url');ET.SubElement(u,'loc').text=SITE_URL+route_url(p)
 ET.ElementTree(root).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {SITE_URL}{BASE}sitemap.xml\n' if SITE_URL!='https://example.com' else ''),encoding='utf-8')
manifest={'generated':str(date.today()),'base':BASE,'routes':[route_url(p) for p in paths], 'excluded_drafts':sorted(p.name for p in (ROOT/'content/drafts').glob('*.md'))}
(OUT/'build-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(f"Built {len(paths)} pages in {OUT} ({len(manifest['excluded_drafts'])} private drafts excluded).")
