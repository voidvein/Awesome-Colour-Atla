"""Write one explicit human/agent visual decision bound to the inspected assets."""
import argparse,hashlib,json,time
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json

def record_review(paper_id,verdict,reason,reviewer='root',palette_observation='',exclude_regions=None):
 r=json.loads((RECORDS/(paper_id+'.json')).read_text(encoding='utf8'));e=r['extraction']
 from pathlib import Path
 digest=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 if verdict=='accepted':
  assert str(e.get('paper','')).startswith('https://'),'A primary paper URL is required before acceptance'
  assert e.get('sourceType') and e.get('sourceTitle'),'Primary source type/title must survive figure replacement'
  assert str(e.get('source_url') or e.get('image_url') or '').startswith('https://'),'Original figure/PDF URL is required'
  assert e.get('imageSHA256')==digest,'Update extraction imageSHA256 after changing the figure'
  assert 2<=len(e.get('colors',[]))<=8
  assert len(set(e['colors']))==len(e['colors']),'Palette colours must be distinct'
  assert palette_observation.strip(),'A figure-specific visual observation is required'
  assert [c['hex'] for c in e.get('colorEvidence',[])]==e['colors']
  with Image.open(e['image']) as source:
   im=Image.new('RGBA',source.size,'white');im.alpha_composite(source.convert('RGBA'));im=im.convert('RGB')
   for colour in e['colorEvidence']:
    x,y=colour['sampleXY'];assert 0<=x<im.width and 0<=y<im.height
    assert '#%02X%02X%02X'%im.getpixel((x,y))==colour['hex'],'Sample must match the actual original pixel'
    assert colour['exactSamples']>0
    assert not any(a<=x<c and b<=y<d for a,b,c,d in e.get('excludedRegions',[])),'Sample is inside an excluded region'
 review={'id':paper_id,'verdict':verdict,'reviewer':reviewer,'reason':reason,'reviewedImageSHA256':digest,'reviewedPalette':e['colors'],'paletteObservation':palette_observation,'reviewedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 if exclude_regions:review['excludeRegions']=exclude_regions
 folder=WORK/'reviews';folder.mkdir(exist_ok=True);atomic_json(folder/(paper_id+'.json'),review);return review
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('verdict',choices=['accepted','rejected','needs_recrop','needs_palette_mask']);p.add_argument('reason');p.add_argument('--observation',default='');p.add_argument('--reviewer',default='root');a=p.parse_args();print(json.dumps(record_review(a.id,a.verdict,a.reason,a.reviewer,a.observation),ensure_ascii=False))
