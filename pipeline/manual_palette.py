"""Use visually identified module pixels without sampling demonstration photos."""
import json,hashlib
from collections import Counter
from PIL import Image
from collect_batch import RECORDS,atomic_json

def set_palette(paper_id,points,labels,reason):
 path=RECORDS/(paper_id+'.json');r=json.loads(path.read_text(encoding='utf8'));e=r['extraction']
 with Image.open(e['image']) as source:
  rgba=source.convert('RGBA');bg=Image.new('RGBA',source.size,'white');bg.alpha_composite(rgba);im=bg.convert('RGB')
 count=Counter(im.getdata());chosen=[];seen=set()
 for (x,y),label in zip(points,labels):
  rgb=im.getpixel((x,y));hx='#%02X%02X%02X'%rgb
  assert min(rgb)<245,'White background is not a representative module colour'
  if hx in seen:continue
  seen.add(hx);chosen.append({'hex':hx,'rgb':list(rgb),'sampleXY':[x,y],'exactSamples':count[rgb],'moduleLabel':label,'samplingMethod':'explicit visually identified module pixel'})
 assert 2<=len(chosen)<=8
 e.update(colors=[c['hex'] for c in chosen],colorEvidence=chosen,paletteStatus='needs_visual_review',method='Manual module-fill/line samples after visual inspection',paletteSamplingReason=reason)
 e['imageSHA256']=hashlib.sha256(open(e['image'],'rb').read()).hexdigest()
 atomic_json(path,r);print(paper_id,e['colors']);return r
