"""Round-trip, checksum, and path confinement checks for the real release restorer."""
import hashlib,io,json,sys,tempfile,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pipeline'))
from restore_assets import restore

def fixture(root,names,audit=False):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:
  for name,content in names.items():z.writestr(name,content)
 raw=b.getvalue();folder=root/'data/figure-assets';folder.mkdir(parents=True,exist_ok=True)
 chunks=[]
 for i,start in enumerate(range(0,len(raw),31)):
  part=raw[start:start+31];name=f'part-{i:03d}.bin';(folder/name).write_bytes(part);chunks.append({'file':name,'bytes':len(part),'sha256':hashlib.sha256(part).hexdigest()})
 (folder/'manifest.json').write_text(json.dumps({'format':'zip-chunks-v1','archiveSHA256':hashlib.sha256(raw).hexdigest(),'files':len(names),'audit':audit,'chunks':chunks}),encoding='utf8')
 return folder
with tempfile.TemporaryDirectory() as d:
 root=Path(d);payload=b'RIFF sample exact image bytes';fixture(root,{'dist/assets/batch500/paper.webp':payload});restore(root)
 assert (root/'dist/assets/batch500/paper.webp').read_bytes()==payload
with tempfile.TemporaryDirectory() as d:
 root=Path(d);payload=b'[{"id":"reviewed-paper"}]';fixture(root,{'dist/collection-audit.json':payload},audit=True);restore(root)
 assert (root/'dist/collection-audit.json').read_bytes()==payload
with tempfile.TemporaryDirectory() as d:
 root=Path(d);fixture(root,{'dist/collection-audit.json':b'[]'})
 try:restore(root);raise RuntimeError('audit restored without manifest permission')
 except AssertionError:pass
with tempfile.TemporaryDirectory() as d:
 root=Path(d);folder=fixture(root,{'dist/assets/batch500/paper.webp':b'x'});(folder/'part-000.bin').write_bytes(b'corrupt')
 try:restore(root);raise RuntimeError('corrupt bundle accepted')
 except AssertionError:pass
with tempfile.TemporaryDirectory() as d:
 root=Path(d);fixture(root,{'../escape.webp':b'x'})
 try:restore(root);raise RuntimeError('unsafe archive path accepted')
 except AssertionError:pass
 assert not (root.parent/'escape.webp').exists()
print('PASS: exact image/audit bytes restored, audit permission enforced, corrupt chunks rejected, unsafe paths rejected.')
