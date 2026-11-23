"""Second visual pass: remove surviving photograph/decorative samples."""
import json
from PIL import Image
import numpy as np
from collect_batch import WORK,RECORDS,atomic_json
from review_batch import packet
items=json.loads((WORK/'contacts/audit-m/packet.json').read_text(encoding='utf8'))
keep={4:['#FAE4D5','#DAE2F3','#C5DFB4','#ACB8C9','#E1EFD9'],18:['#FFC5C5','#E0D5E8'],19:['#D6E2F8','#DEF5ED','#EB7D79','#8ED973','#69A7DC'],23:['#EEF7FD','#F15A29','#1D78BE','#3F9564','#BF1E2D','#662C91']}
for i,item in enumerate(items,1):
 if i not in {*keep,17}:continue
 p=RECORDS/(item['id']+'.json');r=json.loads(p.read_text(encoding='utf8'));e=r['extraction'];im=Image.open(e['image']).convert('RGB')
 if i in keep:
  e['colors']=[c for c in keep[i] if c in e['colors']];e['colorEvidence']=[x for x in e['colorEvidence'] if x['hex'] in e['colors']]
 if i==4:
  e['excludedRegions'][0]=[0,0,158,186];e['paletteSelectionNote']='Bird image extends beyond initial mask by one pixel row; photo mask extended and its brown sample removed. Only encoder/token/prototype semantic palette retained.'
 if i==17:
  a=np.asarray(im);box=[350,250,750,350];rgb=[226,213,231];x0,y0,x1,y1=box;ys,xs=np.where(np.all(a[y0:y1,x0:x1]==rgb,axis=2));assert len(xs)>5
  e['colors'].insert(0,'#E2D5E7');e['colorEvidence'].insert(0,{'hex':'#E2D5E7','rgb':rgb,'sampleXY':[int(xs[len(xs)//2]+x0),int(ys[len(ys)//2]+y0)],'exactSamples':int(len(xs)),'sampleRegion':box,'manualRole':'SocialNav Brain neural-model body fill'})
 for pt in e['colorEvidence']:
  x,y=pt['sampleXY'];assert im.getpixel((x,y))==tuple(pt['rgb']);assert not any(a<=x<c and b<=y<d for a,b,c,d in e.get('excludedRegions',[]))
 r['extraction']=e;atomic_json(p,r)
packet('audit-m',27)
