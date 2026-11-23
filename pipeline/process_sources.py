"""Fetch only primary paper figures/PDFs; produce candidates requiring visual review."""
from __future__ import annotations
import argparse,concurrent.futures,difflib,hashlib,json,re,time,traceback,threading
from pathlib import Path
from urllib.parse import urljoin
from PIL import Image
from collect_batch import ROOT,WORK,CACHE,RECORDS,fetch,soup,atomic_json
from extract_figures import process_html,process_pdf,extract_palette

OUT=WORK/'candidates';OUT.mkdir(exist_ok=True)
PDF_LOCK=threading.Lock() # MuPDF is not thread safe; networking remains concurrent.
def norm(s):return re.sub(r'[^a-z0-9\u4e00-\u9fff]','',s.lower())
def match(a,b):return difflib.SequenceMatcher(None,norm(a),norm(b)).ratio()
def raster(p):
 with Image.open(p) as im:
  im.verify()
 with Image.open(p) as im:return im.width>=250 and im.height>=90
def from_arxiv(r,out):
 errors=[]
 for u in r.get('arxivUrls',[])[:1]:
  aid=re.search(r'(?:abs|html|pdf)/([\d.]+(?:v\d+)?)',u)
  if not aid:continue
  url='https://arxiv.org/html/'+aid[1]
  try:
   path=fetch(url,CACHE/(r['id']+'-arxiv.html'),maxbytes=6_000_000)
   s=soup(path);h=s.select_one('h1.ltx_title_document') or s.select_one('h1')
   title=h.get_text(' ',strip=True) if h else ''
   title=re.sub(r'\s+\d+$','',title)
   similarity=match(r['title'],title)
   if not title or similarity<.5:raise ValueError('arxiv title mismatch: '+title[:120])
   info=process_html(path,paper_id=r['id'],base_url=url)
   candidates=[c for c in info['candidates'] if c['score']>=3 and c.get('panelCount',1)==1]
   for i,c in enumerate(candidates[:3]):
    try:
     image=fetch(c['image_url'],out/f'html-{i}.png',maxbytes=15_000_000)
     if not raster(image):raise ValueError('invalid or undersized architecture image')
     pal=extract_palette(image)
     if len(pal['colors'])<2:raise ValueError('fewer than two distinct representative module colours')
     return dict(c,**pal,image=str(image.resolve()),paper='https://arxiv.org/abs/'+aid[1],source_url=c['image_url'],sourceType='arxiv_html',sourceTitle=title,titleSimilarity=similarity,status='needs_visual_review',imageSHA256=hashlib.sha256(image.read_bytes()).hexdigest())
    except Exception as e:errors.append(str(e))
   raise ValueError('no suitable single-panel architecture candidate; '+str(errors[-2:]))
  except Exception as e:errors.append(str(e))
 return {'errors':errors}
def from_pdf(r,out):
 errors=[];sources=[]
 for u in r.get('cvfUrls',[])[:1]:
  try:
   page=fetch(u,CACHE/(r['id']+'-cvf.html'),maxbytes=2_000_000);s=soup(page)
   h=s.select_one('#papertitle');title=h.get_text(' ',strip=True) if h else ''
   if title and match(r['title'],title)<.5:raise ValueError('CVF title mismatch: '+title)
   pdf=next((urljoin(u,a['href']) for a in s.select('a[href]') if a.get_text(strip=True).lower()=='pdf'),None)
   if pdf:sources.append((pdf,u,title))
  except Exception as e:errors.append(str(e))
 if not sources:
  for u in r.get('arxivUrls',[])[:1]:
   m=re.search(r'(?:abs|html|pdf)/([\d.]+(?:v\d+)?)',u)
   if m:sources.append(('https://arxiv.org/pdf/'+m[1],'https://arxiv.org/abs/'+m[1],r['title']))
 for url,paper,title in sources:
  try:
   p=fetch(url,CACHE/(r['id']+'.pdf'),maxbytes=35_000_000)
   if not p.read_bytes()[:5]==b'%PDF-':raise ValueError('response is not a PDF')
   with PDF_LOCK:result=process_pdf(p,out,r['id'],source_url=url)
   if result['status']=='no_architecture_candidate':raise ValueError('PDF has no architecture-caption candidate')
   if len(result.get('colors',[]))<2:raise ValueError('PDF architecture has insufficient representative colours')
   result.update(paper=paper,sourceType='pdf_crop',sourceTitle=title,titleSimilarity=match(r['title'],title),sourcePDFSHA256=hashlib.sha256(p.read_bytes()).hexdigest())
   result['imageSHA256']=hashlib.sha256(Path(result['image']).read_bytes()).hexdigest()
   return result
  except Exception as e:errors.append(str(e))
 return {'errors':errors}
def process(path):
 r=json.loads(path.read_text(encoding='utf8'));out=OUT/r['id'];out.mkdir(exist_ok=True)
 try:
  a=from_arxiv(r,out)
  if not a.get('image'):
   b=from_pdf(r,out)
   if not b.get('image'):
    r.update(status='source_unavailable_or_unsuitable',sourceErrors=a.get('errors',[])+b.get('errors',[]));atomic_json(path,r);return r
   a=b
  r['extraction']=a;r['status']='needs_visual_review'
 except Exception as e:r.update(status='source_error',sourceErrors=[str(e)],traceback=traceback.format_exc()[-1000:])
 atomic_json(path,r);return r
def run(limit,seconds,workers):
 catalog=json.loads((WORK/'catalog.json').read_text(encoding='utf8'))[:limit]
 order={r['id']:i for i,r in enumerate(catalog)}
 completed=0;scheduled=set();deadline=time.monotonic()+seconds;last_report=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  futures={}
  while time.monotonic()<deadline or futures:
   pending=[]
   for p in RECORDS.glob('*.json'):
    if p.stem not in order or p.stem in scheduled:continue
    r=json.loads(p.read_text(encoding='utf8'))
    if r['status']=='note_ready':pending.append(p)
   pending.sort(key=lambda p:order[p.stem])
   while pending and len(futures)<workers and time.monotonic()<deadline:
    p=pending.pop(0);scheduled.add(p.stem);futures[pool.submit(process,p)]=p
   if not futures:
    unresolved=[x for x in catalog if not (RECORDS/(x['id']+'.json')).exists()]
    if not unresolved:break
    time.sleep(2);continue
   done,_=concurrent.futures.wait(futures,timeout=3,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    p=futures.pop(future)
    try:r=future.result();completed+=1;print('SOURCE',completed,r['id'],r['status'],len(r.get('extraction',{}).get('colors',[])),flush=True)
    except Exception as e:print('WORKER_ERROR',p.name,str(e),flush=True)
   if time.monotonic()-last_report>30:
    allr=[json.loads(p.read_text(encoding='utf8')) for p in RECORDS.glob('*.json')]
    counts={s:sum(r['status']==s for r in allr) for s in set(r['status'] for r in allr)}
    print('PROGRESS',json.dumps(counts), 'live',len(futures),flush=True);atomic_json(WORK/'progress.json',{'counts':counts,'liveWorkers':len(futures),'updatedAt':time.time()});last_report=time.monotonic()
 print('SOURCE_BATCH_DONE',completed,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=850);p.add_argument('--seconds',type=int,default=2400);p.add_argument('--workers',type=int,default=3);a=p.parse_args();run(a.limit,a.seconds,a.workers)
