"""Bounded, resumable collection from the user-specified Paper Notes index."""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, re, time, threading
from pathlib import Path
from urllib.parse import urljoin,urlparse
import requests
from bs4 import BeautifulSoup

from release_common import ROOT,atomic_json
BASE='https://papernotes.org/CVPR2026/'
WORK=ROOT/'research/batch500'
CACHE=WORK/'cache'
RECORDS=WORK/'records'
for d in [WORK,CACHE,RECORDS]:d.mkdir(parents=True,exist_ok=True)
DOMAIN_PRIORITY=['image_generation','video_generation','3d_reconstruction','3d_generation','3d_understanding','depth_stereo','localization_slam','object_detection','segmentation','image_restoration','remote_sensing','anomaly_detection','human_understanding','video_understanding','autonomous_driving','robotics','medical_imaging','multimodal_vlm','vlm_reasoning','llm_agent']
_local=threading.local()
def session():
 if not hasattr(_local,'s'):
  _local.s=requests.Session();_local.s.headers['User-Agent']='ColourAtlasResearch/0.2 (bounded figure indexing)'
 return _local.s
def fetch(url,path,maxbytes=40_000_000):
 if path.exists() and path.stat().st_size>100:return path
 t=time.monotonic();part=path.with_suffix(path.suffix+'.part')
 try:
  with session().get(url,timeout=(12,25),stream=True) as r:
   r.raise_for_status()
   if int(r.headers.get('Content-Length','0'))>maxbytes:raise ValueError('source exceeds bounded download size')
   size=0
   with part.open('wb') as f:
    for chunk in r.iter_content(65536):
     size+=len(chunk)
     if size>maxbytes or time.monotonic()-t>80:raise ValueError('bounded source fetch limit reached')
     f.write(chunk)
  part.replace(path);return path
 except:
  part.unlink(missing_ok=True);raise
def soup(path):return BeautifulSoup(path.read_text(encoding='utf8'),'html.parser')
def catalog():
 fetch(BASE,CACHE/'index.html',maxbytes=5_000_000)
 a=soup(CACHE/'index.html').select_one('article')
 domains=[]
 for h in a.select('h2[id]'):
  key=h['id'];label=re.sub(r'[^\u4e00-\u9fffA-Za-z0-9 /]','',re.sub(r'\(\d+\)','',h.get_text(' ',strip=True))).replace('¶','').strip()
  domains.append((key,label))
 domain_order={x[0]:i for i,x in enumerate(domains)}
 domains.sort(key=lambda x:DOMAIN_PRIORITY.index(x[0]) if x[0] in DOMAIN_PRIORITY else 100+domain_order[x[0]])
 def one(d):
  key,label=d;url=BASE+key+'/'
  try:
   p=fetch(url,CACHE/(key+'.html'),maxbytes=6_000_000);a=soup(p).select_one('article');out=[];seen=set()
   for x in a.select('a[href]'):
    u=urljoin(url,x['href']).split('#')[0]
    title=x.get_text(' ',strip=True)
    if u.startswith(url) and len(urlparse(u).path.strip('/').split('/'))==3 and len(title)>15 and u not in seen:
     seen.add(u);out.append({'id':'cvpr26-'+hashlib.sha1(u.encode()).hexdigest()[:12],'title':title,'domainKey':key,'domain':label,'noteUrl':u})
   print('CATEGORY',key,len(out),flush=True);return out
  except Exception as e:print('CATEGORY_ERROR',key,str(e),flush=True);return []
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:groups=list(ex.map(one,domains))
 ordered=[];seen=set()
 for rank in range(max(map(len,groups),default=0)):
  for g in groups:
   if rank<len(g) and g[rank]['noteUrl'] not in seen:ordered.append(g[rank]);seen.add(g[rank]['noteUrl'])
 atomic_json(WORK/'catalog.json',ordered)
 print('CATALOG_TOTAL',len(ordered),flush=True)
 return ordered
def collect_note(item):
 path=RECORDS/(item['id']+'.json')
 if path.exists():
  old=json.loads(path.read_text(encoding='utf8'))
  if old.get('status') not in ['note_error']:return old
 r=dict(item)
 try:
  p=fetch(item['noteUrl'],CACHE/(item['id']+'-note.html'),maxbytes=3_000_000)
  s=soup(p);a=s.select_one('article');txt=a.get_text(' ',strip=True)
  links=[x['href'] for x in a.select('a[href]')]
  r['arxivUrls']=list(dict.fromkeys(x for x in links if re.match(r'https?://arxiv.org/(abs|html|pdf)/',x)))
  r['cvfUrls']=list(dict.fromkeys(x for x in links if 'openaccess.thecvf.com/content/' in x))
  r['projectUrls']=list(dict.fromkeys(x for x in links if ('.github.io' in x or 'github.com/' in x) and '#image' not in x))[:4]
  tagmeta=s.select_one('meta[name="keywords"]')
  tags=[x.get_text(' ',strip=True) for x in a.select('.md-tag')]
  if not tags and tagmeta:tags=[x.strip() for x in tagmeta.get('content','').split(',')]
  if not tags:
   m=re.search(r'关键词\s*[:：]\s*(.*?)(?:一句话总结|研究背景)',txt)
   if m:tags=[x.strip() for x in re.split('[,，、;；]',m[1])]
  r['tags']=list(dict.fromkeys([item['domain']]+[x for x in tags if 1<len(x)<40 and 'CVPR' not in x]))[:8]
  summary=a.find(id=re.compile('一句话|summary|^_1$'))
  r['summary']=txt[txt.find('一句话总结')+5:txt.find('研究背景')].strip(' ¶')[:500] if '一句话总结' in txt else ''
  r['venue']='CVPR 2026 FINDINGS' if any('/CVPR2026F/' in x for x in r['cvfUrls']) or 'CVPR 2026 Findings' in txt[:1500] else 'CVPR 2026'
  r['status']='note_ready';r['collectedAt']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
 except Exception as e:r.update(status='note_error',error=str(e))
 atomic_json(path,r);return r
def notes(limit):
 items=json.loads((WORK/'catalog.json').read_text(encoding='utf8'))[:limit]
 seed={x['noteUrl'] for x in json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'))}
 items=[x for x in items if x['noteUrl'] not in seed]
 count=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
  for r in ex.map(collect_note,items):
   count+=1
   if count%20==0:print('NOTES',count,'/',len(items),r['status'],flush=True)
 print('NOTES_DONE',count,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['catalog','notes']);p.add_argument('--limit',type=int,default=900);a=p.parse_args()
 if a.stage=='catalog':catalog()
 else:notes(a.limit)
