"""Only audit-m: original architecture repairs and photo-free palette candidates."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from extract_figures import extract_palette
from review_batch import packet
items=json.loads((WORK/'contacts/audit-m/packet.json').read_text(encoding='utf8'))
mask={
1:[[.13,.39,.23,.65],[.25,.62,.36,.90],[.40,.59,.47,.78],[.49,.32,.55,.51],[.71,.40,.81,.69]],
2:[[0,0,.33,.22],[.24,.80,.33,1]],
3:[[0,0,.55,.21],[0,.50,.18,.85]],
4:[[0,0,.17,.31],[0,.50,.15,.92]],
5:[[.27,.12,.36,.27],[.23,.43,.46,.74],[.67,.02,.90,.36],[.70,.48,1,1]],
7:[[0,.40,.20,1],[.68,.48,1,1]],
9:[[0,0,1,.43],[0,.43,.27,1]],
10:[[0,0,.20,1]],
11:[[0,0,.15,.33],[.88,0,1,.33],[.47,.54,1,1]],
12:[[0,0,.30,1],[.30,0,.55,.35]],
13:[[0,0,.35,1],[.32,.70,.55,1]],
17:[[.35,.75,.55,1],[.72,.60,.90,.90]],
18:[[.40,0,.93,.43],[.20,.53,.43,.95]],
20:[[0,.35,.18,.95],[.85,.56,.91,.90]],
21:[[0,0,.15,1],[.70,.35,.80,.80]],
22:[[0,0,.22,.34]],
23:[[0,.60,.22,.90],[.78,0,.92,.30]],
24:[[.45,.25,.58,.45],[.83,.54,.93,.73],[.83,.76,.93,.97]],
25:[[0,0,.27,.32],[0,.50,.27,.90],[.77,0,1,.90]],
26:[[0,0,.11,.32]],
27:[[0,0,.25,1],[.75,0,1,1]],
}
keep={
5:['#EEF3FF','#F6C6AC','#83CAEB','#5783FF'],
7:['#D9F2D0','#CAEDFB','#F6C6AD'],
9:['#DFDEEB','#A2BDD5','#D2E6D7'],
10:['#BCD0E9','#E1EFD9','#FFDF7C','#A4A4A4','#2D75B5','#759FCC','#A8D08D'],
12:['#FAF5ED','#D9E7FB','#FFE6CC'],
13:['#CBE4BD','#FBE5D7','#BDD7EE','#4473C5'],
17:['#E9ECF5','#A8E7C8','#F7CBCC','#FEECD4','#B1B4D5','#C4DAF1'],
18:['#FFC5C5','#E0D5E8','#FFECD8','#AFE3FD','#FE282D'],
20:['#7EE4E4','#B3B3B3','#F3D2D2','#F2AA45','#9999FF','#A7AAE1'],
21:['#C55F10','#2C4981','#B6C6EA'],
27:['#BC422C','#249B5D','#D07E2C','#7758BA','#E7A399'],
}
for i,item in enumerate(items,1):
 if i in {6,15}:continue
 path=RECORDS/(item['id']+'.json');r=json.loads(path.read_text(encoding='utf8'));e=r['extraction'];im=Image.open(e['image']).convert('RGB');w,h=im.size
 if i in mask:
  regions=[[round(a*w),round(b*h),round(c*w),round(d*h)] for a,b,c,d in mask[i]]
  e.update(extract_palette(e['image'],exclude_regions=regions))
 if i in keep:
  chosen=[c for c in keep[i] if c in e['colors']];e['colors']=chosen;e['colorEvidence']=[x for x in e['colorEvidence'] if x['hex'] in chosen]
  e['paletteSelectionNote']='Retained neural-module/semantic fills and connectors only; natural images, output heatmaps, plot and decorative candidate modes removed.'
 if i==14:
  a=np.asarray(im);evidence=[]
  for rgb,role,box in [([180,179,179],'Cross-attention/head neural blocks',[650,300,1100,675]),([226,118,49],'Orange motion-stream attention connectors',[820,350,900,655]),([63,164,186],'Teal motion-stream attention connectors',[820,350,900,655])]:
   x0,y0,x1,y1=box;ys,xs=np.where(np.all(a[y0:y1,x0:x1]==rgb,axis=2));assert len(xs)>5,(i,rgb)
   evidence.append({'hex':'#%02X%02X%02X'%tuple(rgb),'rgb':rgb,'sampleXY':[int(xs[len(xs)//2]+x0),int(ys[len(ys)//2]+y0)],'exactSamples':int(len(xs)),'sampleRegion':box,'manualRole':role})
  e['colors']=[x['hex'] for x in evidence];e['colorEvidence']=evidence;e['excludedRegions']=[[100,75,215,260],[785,145,980,300],[140,575,300,715],[420,575,565,715],[735,680,985,835],[1120,65,1600,835]];e['method']='Exact source neural-block fill and cross-stream attention connector samples; all human motion renderings excluded.'
 e['imageSHA256']=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest();assert 2<=len(e['colors'])<=8,(i,e['colors'])
 for x in e['colorEvidence']:
  assert im.getpixel(tuple(x['sampleXY']))==tuple(x['rgb']),(i,x)
  px,py=x['sampleXY'];assert not any(x0<=px<x1 and y0<=py<y1 for x0,y0,x1,y1 in e.get('excludedRegions',[])),(i,x)
 r['extraction']=e;atomic_json(path,r);print(i,e['colors'],flush=True)
packet('audit-m',27)
