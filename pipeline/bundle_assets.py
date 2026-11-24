"""Package reviewed figure derivatives for efficient, checksum-verified GitHub transport."""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from release_common import ROOT,atomic_json

def build():
 rows=json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'))
 release=json.loads((ROOT/'dist/collection.json').read_text(encoding='utf8'))
 assert rows and release['reviewed'] is True and release['target']==release['published']==len(rows),'The bundle requires the complete reviewed collection.'
 paths=sorted({p[k] for p in rows for k in ['image','thumbnail'] if k in p and p[k].startswith('assets/batch500/')})
 out=ROOT/'data/figure-assets';out.mkdir(parents=True,exist_ok=True)
 archive=ROOT/'outputs/figure-assets.zip';archive.parent.mkdir(exist_ok=True)
 folder=ROOT/'data/figure-assets'
 wanted={'dist/'+p for p in paths}
 with (archive.with_suffix('.previous.zip')).open('w+b') as previous:
  prior_manifest=(folder/'manifest.json').exists()
  if prior_manifest:
   prior=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
   total=hashlib.sha256()
   for item in prior['chunks']:
    assert Path(item['file']).name==item['file']
    b=(folder/item['file']).read_bytes()
    assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
    previous.write(b);total.update(b)
   assert total.hexdigest()==prior['archiveSHA256']
   previous.seek(0)
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
   if prior_manifest:
    with zipfile.ZipFile(previous) as prior_zip:
     for entry in prior_zip.infolist():
      if entry.filename=='dist/collection-audit.json':continue
      assert entry.filename in wanted,f'Existing reviewed asset missing: {entry.filename}'
      payload=prior_zip.read(entry)
      assert (ROOT/entry.filename).read_bytes()==payload, f'Existing reviewed asset changed: {entry.filename}'
      z.writestr(copy.copy(entry),payload)
      wanted.remove(entry.filename)
   for name in sorted(wanted):z.write(ROOT/name,arcname=name)
   z.write(ROOT/'dist/collection-audit.json',arcname='dist/collection-audit.json')
 archive.with_suffix('.previous.zip').unlink()
 chunk_archive(archive)

def chunk_archive(archive):
 out=ROOT/'data/figure-assets';out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive) as z:files=z.namelist()
 # Each chunk is below the connector's safe binary transport envelope.
 chunks=[];total=hashlib.sha256()
 with archive.open('rb') as f:
  while b:=f.read(1_048_576):
   name=f'part-{len(chunks):03d}.bin';part=out/name;total.update(b)
   if not part.exists() or part.read_bytes()!=b:part.write_bytes(b)
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
