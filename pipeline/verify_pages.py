"""Verify the deployed release byte-for-byte, including every full figure and thumbnail."""
import argparse,concurrent.futures,hashlib,json,threading,time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE='https://voidvein.github.io/Awesome-Colour-Atla/'
LOCAL=threading.local()

def verify(base=BASE):
 rows=json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'))
 assert len(rows)==500,'Only a complete 500-card release can pass the deployment check'
 paths={'index.html','style.css','app.js','i18n.js','content-en.json','content-zh.json','palettes.json','collection.json','collection-audit.json'}
 paths.update(p[k] for p in rows for k in ('image','thumbnail') if p.get(k))
 version=hashlib.sha256((ROOT/'dist/palettes.json').read_bytes()).hexdigest()[:16]
 def check(rel):
  expected=hashlib.sha256((ROOT/'dist'/rel).read_bytes()).hexdigest()
  if not hasattr(LOCAL,'session'):LOCAL.session=requests.Session()
  last=''
  for attempt in range(4):
   try:
    response=LOCAL.session.get(base+rel+'?release='+version,timeout=(15,60),headers={'Cache-Control':'no-cache'})
    response.raise_for_status()
    assert hashlib.sha256(response.content).hexdigest()==expected,'deployed bytes differ from reviewed release'
    return {'path':rel,'status':response.status_code,'bytes':len(response.content),'sha256':expected}
   except Exception as error:
    last=str(error)
    if attempt<3:time.sleep(2*(attempt+1))
  return {'path':rel,'error':last}
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
  results=list(executor.map(check,sorted(paths)))
 errors=[r for r in results if 'error' in r]
 report={'url':base,'papers':len(rows),'resources':len(results),'passed':len(results)-len(errors),'errors':errors,'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':results}
 output=ROOT/'outputs/github-pages-verification.json';output.parent.mkdir(exist_ok=True);output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False,indent=2),flush=True)
 if errors:raise SystemExit(1)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--base',default=BASE);args=parser.parse_args();verify(args.base)
