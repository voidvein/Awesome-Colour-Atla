"""Package reviewed figure derivatives for efficient, checksum-verified GitHub transport."""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from collect_batch import ROOT,atomic_json

def build():
 rows=json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'))
 assert len(rows)==500,'The release bundle requires all 500 approved cards.'
 paths=sorted({p[k] for p in rows for k in ['image','thumbnail'] if k in p and p[k].startswith('assets/batch500/')})
 out=ROOT/'data/figure-assets';out.mkdir(parents=True,exist_ok=True)
 archive=ROOT/'outputs/figure-assets.zip';archive.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
  for rel in paths:z.write(ROOT/'dist'/rel,arcname='dist/'+rel)
  z.write(ROOT/'dist/collection-audit.json',arcname='dist/collection-audit.json')
 chunk_archive(archive)

def chunk_archive(archive):
 out=ROOT/'data/figure-assets';out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive) as z:files=z.namelist()
 # Each chunk is below the connector's safe binary transport envelope.
 chunks=[];total=hashlib.sha256()
 with archive.open('rb') as f:
  while b:=f.read(1_048_576):
   name=f'part-{len(chunks):03d}.bin';(out/name).write_bytes(b);total.update(b)
   chunks.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 atomic_json(out/'manifest.json',{'format':'zip-chunks-v1','archiveSHA256':total.hexdigest(),'files':len(files),'figures':len(files)-1,'audit':True,'chunks':chunks})
 print(f'Bundled {len(files)-1} reviewed image derivatives in {len(chunks)} chunks.')

def refresh_audit():
 archive=ROOT/'outputs/figure-assets.zip';temporary=archive.with_suffix('.refreshed.zip')
 with zipfile.ZipFile(archive) as source,zipfile.ZipFile(temporary,'w') as target:
  for info in source.infolist():
   data=(ROOT/'dist/collection-audit.json').read_bytes() if info.filename=='dist/collection-audit.json' else source.read(info)
   target.writestr(copy.copy(info),data)
 temporary.replace(archive);chunk_archive(archive)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refresh-audit',action='store_true');a=p.parse_args()
 refresh_audit() if a.refresh_audit else build()
