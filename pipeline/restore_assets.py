"""Restore only allowlisted figure assets; reject corrupt or unsafe archives."""
import hashlib,json,tempfile,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def restore(root=ROOT):
 folder=root/'data/figure-assets';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
 assert manifest['format']=='zip-chunks-v1'
 with tempfile.TemporaryFile() as combined:
  digest=hashlib.sha256()
  for item in manifest['chunks']:
   assert Path(item['file']).name==item['file']
   b=(folder/item['file']).read_bytes();assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256']
   combined.write(b);digest.update(b)
  assert digest.hexdigest()==manifest['archiveSHA256'],'Figure bundle checksum mismatch'
  combined.seek(0)
  with zipfile.ZipFile(combined) as z:
   names=z.namelist();assert len(names)==manifest['files'] and len(set(names))==len(names)
   for name in names:
    p=Path(name)
    assert not p.is_absolute() and '..' not in p.parts
    if name=='dist/collection-audit.json':
     assert manifest.get('audit') is True
    else:
     assert name.startswith('dist/assets/batch500/') and name.endswith('.webp')
     assert (root/p).resolve().is_relative_to((root/'dist/assets/batch500').resolve())
   for name in names:
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
 print(f'Restored {manifest["files"]} checksummed figure derivatives.')
if __name__=='__main__':restore()
