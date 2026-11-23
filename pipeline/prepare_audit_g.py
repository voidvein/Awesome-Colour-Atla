"""Bounded audit-g repairs; no approval is recorded here."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
from collect_batch import ROOT,WORK,RECORDS,atomic_json
from extract_figures import extract_palette,process_html
from review_batch import packet
items=json.loads((WORK/'contacts/audit-g/packet.json').read_text(encoding='utf8'))
reject={4,7,10,43,44}
fresh={30:'cvpr26-51e90f31b99e',49:'cvpr26-427424aaf035',51:'cvpr26-7c7f0990a589'}
mask={
1:[[0,0,.45,1],[.88,.55,1,1]],
3:[[0,0,.33,.40]],
5:[[0,0,.28,.53],[0,.53,.34,1]],
6:[[0,.18,.30,.40]],
8:[[0,0,.17,1],[.20,0,.32,1],[.45,0,.62,1]],
9:[[0,.5,.20,1],[.83,.5,1,1]],
11:[[0,0,.13,1],[.83,0,1,1]],
12:[[0,0,.18,1],[.83,0,1,1]],
13:[[0,0,1,.13],[0,0,.15,.30],[.50,0,.63,.30]],
14:[[0,0,.105,1]],
16:[[0,0,.34,1],[.82,0,1,1]],
17:[[.30,0,1,1],[0,0,.30,.28]],
18:[[0,.4,.30,1],[.65,0,1,1]],
20:[[0,0,.13,1],[.20,.30,.42,.53],[.64,.30,.85,.53]],
21:[[0,0,.22,.35],[.35,0,.66,.35],[.77,0,1,.35],[0,.37,.5,.66]],
23:[[0,0,.32,.70],[.40,.67,.61,1],[.73,.45,.81,.68]],
25:[[.58,0,1,1],[0,.90,.58,1]],
26:[[0,0,.25,.45],[0,.5,.4,1],[.83,.5,1,1]],
27:[[.67,0,1,1],[0,.45,.20,1]],
28:[[0,0,.20,.13],[.80,0,1,.16]],
30:[[0,0,.22,1],[.35,.50,.50,1],[.45,0,.52,.34],[.70,0,1,1]],
31:[[0,0,.30,1]],
32:[[0,.60,.15,1],[.62,0,1,1]],
33:[[0,0,.10,1],[.75,.10,.86,.90]],
34:[[0,0,.36,.22],[.80,.50,1,1],[.05,.32,.12,.45],[.24,.32,.31,.45]],
35:[[0,0,.33,.45]],
36:[[.30,.42,.64,.85],[.68,.42,1,.85],[.85,.87,1,1]],
39:[[0,0,1,.18],[0,.35,.20,.70]],
47:[[0,0,.25,.25],[.75,0,1,.5],[.75,.70,1,1]],
48:[[0,0,.30,.45],[.70,.10,1,.60],[.47,.65,.65,.90]],
50:[[.55,0,1,1],[0,.75,.32,1]],
51:[[.15,.25,.67,1],[.15,0,.45,.25],[.68,0,1,.42]],
52:[[.70,0,1,.34],[.32,.55,.69,1],[0,.50,.22,1],[.85,.50,1,1]],
53:[[0,0,.72,1],[.83,0,1,1]],
54:[[0,0,.34,1],[.65,.80,.98,1]],
}
for i,item in enumerate(items,1):
 if i in reject:continue
 id=item['id'];p=RECORDS/f'{id}.json';r=json.loads(p.read_text(encoding='utf8'));e=r['extraction']
 if i in fresh:
  new=json.loads((ROOT/'research/extraction-review/audit-g'/f'{fresh[i]}.json').read_text(encoding='utf8'))
  for key in ['paper','sourceType','sourceTitle','titleSimilarity','sourcePDFSHA256','source_url']:
   if key in e:new[key]=e[key]
  image=WORK/'candidates'/id/'reviewed-architecture.png';shutil.copyfile(new['image'],image);new['image']=str(image.resolve());e=new
 if i==19 and not e.get('sourcePixelCrop'):
  box=[0,890,1692,1200];original=Path(e['image']);new=original.parent/'reviewed-training.png';Image.open(original).crop(box).save(new)
  e['sourcePixelCrop']={'sourceImage':str(original),'sourceImageSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),'box':box};e['reviewCropNote']='Only original Figure 4 training-strategy diagram; preceding performance table excluded.';e['image']=str(new.resolve())
 if i==37:
  original=WORK/'candidates'/id/'reviewed-method.png';new=original.parent/'reviewed-training-panel.png';box=[0,0,1025,384];Image.open(original).crop(box).save(new)
  c=next(c for c in process_html(WORK/'cache'/f'{id}-arxiv.html',base_url=r['arxivUrls'][0].replace('/abs/','/html/'))['candidates'] if c['figure']=='Figure 2')
  e.update({k:c[k] for k in ['figure','caption','score','scoreReasons']});e['source_url']=c['image_url'];e['image']=str(new.resolve())
  e['sourcePixelCrop']={'sourceImage':str(original),'sourceImageSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),'box':box};e['reviewCropNote']='Original Figure 2(a) reward-normalized MedGRPO model-training system; empirical entropy plot (b) excluded.'
  e['excludedRegions']=[[0,0,504,130],[875,0,1010,170],[695,240,835,384]]
 im=Image.open(e['image']);w,h=im.size
 regions=[[round(a*w),round(b*h),round(c*w),round(d*h)] for a,b,c,d in mask.get(i,[])] if i in mask else e.get('excludedRegions',[])
 e.update(extract_palette(e['image'],exclude_regions=regions));e['imageSHA256']=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest();r['extraction']=e;atomic_json(p,r)
 print(i,e['figure'],len(e['colors']),e['colors'],flush=True)
packet('audit-g',54)
