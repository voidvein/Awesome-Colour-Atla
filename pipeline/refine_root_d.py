"""Explicit palette refinements following the root-d contact-sheet inspection."""
import json
import numpy as np
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from extract_figures import extract_palette
from review_batch import packet
rs=json.loads((WORK/'contacts/root-d/packet.json').read_text(encoding='utf8'))
keep={
4:['#E6EFF7','#F4CDD0','#46B0E0'],
7:['#FFFAF2','#E7D8B8','#D9D9D9'],
12:['#F0F9ED','#356E3A','#ACD6B0','#52AC5C'],
15:['#E4E6F0','#FDE3C0','#FBE1E2'],
20:['#D9F1D0','#C9EDFA'],
22:['#CFD4E8','#FBE4D6','#FDE499','#FFF4D1'],
24:['#E7EFF9','#F8D7BE','#D3EAD4','#C0D6FB','#F6B082','#BEBFBE'],
25:['#3A729A','#AC4877','#388E37'],
}
for i,r0 in enumerate(rs,1):
 path=RECORDS/(r0['id']+'.json');r=json.loads(path.read_text(encoding='utf8'));e=r['extraction'];im=Image.open(e['image']).convert('RGB');w,h=im.size
 if i in [6,9,29]:
  regions={6:[[0,0,.38,.52],[0,.50,.35,1]],9:[[0,0,.16,.33]],29:[[.62,0,1,1]]}[i]
  regions=[[round(a*w),round(b*h),round(c*w),round(d*h)] for a,b,c,d in regions];e.update(extract_palette(e['image'],exclude_regions=regions))
 if i in keep:
  e['colors']=[c for c in keep[i] if c in e['colors']];e['colorEvidence']=[x for x in e['colorEvidence'] if x['hex'] in e['colors']]
  e['paletteSelectionNote']='Reviewer kept only diagram-module/semantic encodings; rejected photograph, heatmap, decorative or redundant candidate colours.'
 if i==13:
  # Histology panels are evidence images, not architecture palette. The neural
  # block schematic itself uses purposeful black outlines and red loss arrows.
  a=np.asarray(im);evidence=[]
  for rgb,role,box in [([0,0,0],'UNet/SAFB module outlines',[250,50,900,350]),([255,0,0],'Equation/loss connector arrows',[600,0,1500,360])]:
   x0,y0,x1,y1=box;ys,xs=np.where(np.all(a[y0:y1,x0:x1]==rgb,axis=2));assert len(xs)>10
   evidence.append({'hex':'#%02X%02X%02X'%tuple(rgb),'rgb':rgb,'sampleXY':[int(xs[0]+x0),int(ys[0]+y0)],'exactSamples':len(xs),'sampleRegion':box,'manualRole':role})
  e['colors']=[x['hex'] for x in evidence];e['colorEvidence']=evidence;e['method']='Explicit exact-source neural-module outline and loss-connector samples; histology/prediction images excluded.'
 if i not in [14,23,28,30,34]:
  assert 2<=len(e['colors'])<=8,(i,e['colors'])
  for x in e['colorEvidence']:assert im.getpixel(tuple(x['sampleXY']))==tuple(x['rgb']),(i,x)
  for field in ['paper','sourceType','sourceTitle','source_url','imageSHA256']:assert e.get(field),(i,field)
  r['extraction']=e;atomic_json(path,r)
  print(i,e['colors'],flush=True)
packet('root-d',36)
