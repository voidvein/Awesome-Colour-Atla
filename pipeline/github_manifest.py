"""Prepare only task-owned release files for connector-based GitHub upload.

No credentials are read or stored. Remote mutation is done by the connected GitHub tools.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from collect_batch import ROOT,atomic_json

def blob_sha(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def make(remote_tree=None):
 rows=json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'));assert len(rows)==500
 bundle=ROOT/'data/figure-assets/manifest.json';assert bundle.exists()
 tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,check=True,capture_output=True).stdout.decode().split('\0')
 paths={p for p in tracked if p and p!='.openai/hosting.json'}
 for pattern in ['pipeline/*.py','tests/*.py','tests/*.cjs','data/figure-assets/manifest.json','data/figure-assets/part-*.bin','research/batch500/reviews/*.json']:
  paths.update(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pattern))
 paths.update(['dist/collection.json','research/seed-palettes.json','research/batch500/catalog.json','research/batch500/README.md'])
 remote={}
 if remote_tree:
  remote={x['path']:x['sha'] for x in json.loads(Path(remote_tree).read_text(encoding='utf8'))['tree'] if x['type']=='blob'}
 result=[]
 for rel in sorted(paths):
  path=(ROOT/rel).resolve();assert path.is_relative_to(ROOT) and '.git' not in Path(rel).parts
  if not path.is_file():continue
  data=path.read_bytes();sha=blob_sha(data)
  if remote.get(rel)==sha:continue
  binary=rel.startswith('data/figure-assets/part-') or path.suffix.lower() in ['.png','.jpg','.webp','.bin']
  if not binary:data.decode('utf8')
  result.append({'path':rel,'bytes':len(data),'sha':sha,'encoding':'base64' if binary else 'utf-8'})
 out=ROOT/'outputs/github-transfer.json';out.parent.mkdir(exist_ok=True);atomic_json(out,result)
 print(json.dumps({'changedFiles':len(result),'binaryChunks':sum(x['encoding']=='base64' for x in result),'bytes':sum(x['bytes'] for x in result),'manifest':str(out)},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--remote-tree');a=p.parse_args();make(a.remote_tree)
