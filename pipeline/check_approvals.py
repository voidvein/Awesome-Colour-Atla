"""Check every accepted review against its current primary metadata and exact source pixels."""
import hashlib,json
from pathlib import Path
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json

def check():
 cache_path=WORK/'pixel-checks.json';cache=json.loads(cache_path.read_text(encoding='utf8')) if cache_path.exists() else {}
 issues=[];checked=0;new_checks=0
 for path in (WORK/'reviews').glob('*.json'):
  review=json.loads(path.read_text(encoding='utf8'))
  if review['verdict']!='accepted':continue
  checked+=1;r=json.loads((RECORDS/(review['id']+'.json')).read_text(encoding='utf8'));e=r['extraction'];image=Path(e['image'])
  try:
   assert all(e.get(k) for k in ['paper','sourceType','sourceTitle','figure','imageSHA256'])
   assert str(e.get('source_url') or e.get('image_url') or '').startswith('https://')
   assert review.get('paletteObservation') and 2<=len(e['colors'])<=8
   digest=hashlib.sha256(image.read_bytes()).hexdigest();assert digest==e['imageSHA256']==review['reviewedImageSHA256']
   assert e['colors']==review['reviewedPalette']==[c['hex'] for c in e['colorEvidence']]
   signature=hashlib.sha256(json.dumps([digest,e['colors'],e['colorEvidence'],e.get('excludedRegions',[])],sort_keys=True).encode()).hexdigest()
   if cache.get(review['id'])==signature:continue
   with Image.open(image) as source:
    rgba=source.convert('RGBA');bg=Image.new('RGBA',source.size,'white');bg.alpha_composite(rgba);im=bg.convert('RGB')
    for colour in e['colorEvidence']:
     x,y=colour['sampleXY'];assert 0<=x<im.width and 0<=y<im.height
     assert '#%02X%02X%02X'%im.getpixel((x,y))==colour['hex'],f"wrong RGB at {(x,y)}"
     assert colour['exactSamples']>0
     assert not any(a<=x<c and b<=y<d for a,b,c,d in e.get('excludedRegions',[])),f"sample {(x,y)} inside excluded region"
   cache[review['id']]=signature;new_checks+=1
  except Exception as error:issues.append({'id':review['id'],'error':str(error) or type(error).__name__})
 atomic_json(cache_path,cache);atomic_json(WORK/'approval-check.json',{'checked':checked,'newPixelChecks':new_checks,'issues':issues})
 print(json.dumps({'checked':checked,'newPixelChecks':new_checks,'issues':issues},ensure_ascii=False,indent=2))
 if issues:raise SystemExit(1)
if __name__=='__main__':check()
