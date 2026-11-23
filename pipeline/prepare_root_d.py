"""Prepare bounded root-d visual repairs; this never records acceptance."""
import json,hashlib
from pathlib import Path
from PIL import Image
from collect_batch import ROOT,WORK,RECORDS,atomic_json
from extract_figures import extract_palette,process_html
from review_batch import packet

source=json.loads((WORK/'contacts/root-d/packet.json').read_text(encoding='utf8'))
reject={14:'Numerical RKPM/eigenanalysis/deformable simulation; not a neural architecture.',23:'Classical DCT/perceptual-hash deduplication; no neural module.',28:'Dataset sizes/staged training overview and result examples, no neural structure.',30:'PDF Fig1 inspected: task capability examples, not model internals; Fig3 dataset and Fig4 formulas, no neural architecture.',34:'Benchmark construction/evaluation only; no neural model architecture.'}
# Fractions in the unmodified current architecture image; images remain intact.
masks={
1:[[0,0,.3,1],[.92,0,1,1]],
4:[[0,.26,.48,.48],[.78,.64,1,1]],
5:[[0,0,.22,1],[.68,0,1,.75]],
6:[[0,0,.30,1]],
8:[[0,0,.37,.29]],
9:[[0,0,.115,.32]],
11:[[0,0,.12,.45]],
12:[[0,0,.47,1],[.65,.15,.81,.60]],
15:[[.17,.1,.48,.32],[.03,.48,.48,.61],[.58,.03,1,.50],[.85,.8,1,1]],
16:[[.58,0,1,1],[0,0,.085,1]],
17:[[0,0,1,.23]],
18:[[0,0,.12,1],[.87,0,1,1]],
19:[[0,0,.45,1],[.84,.5,1,1]],
20:[[0,0,.20,1],[.85,0,1,1]],
21:[[0,0,.30,1]],
22:[[0,0,.23,.51],[.76,0,1,.51],[0,.48,.34,1],[.34,.64,.67,1]],
24:[[0,0,.14,1],[.86,0,1,1],[.14,.5,.30,1]],
26:[[0,0,.35,.35],[0,.35,.16,.64]],
27:[[0,0,.18,.50]],
29:[[.70,0,1,1]],
31:[[0,.38,.50,.75]],
32:[[0,0,.18,.60],[.18,.10,.50,.56],[.50,0,.69,.60]],
35:[[0,.54,.16,.90]],
36:[[0,0,1,.51],[.67,0,1,1]],
}
for i,item in enumerate(source,1):
 id=item['id'];path=RECORDS/f'{id}.json';r=json.loads(path.read_text(encoding='utf8'));e=r['extraction']
 if i in reject:continue
 if i==7 and not e.get('rasterSubcrop'):
  image=Image.open(e['image']);crop=[550,50,1010,705];out=WORK/'candidates'/id/'training-panel.png';image.crop(crop).save(out)
  e['rasterSubcrop']={'sourceImage':e['image'],'sourceImageSHA256':hashlib.sha256(Path(e['image']).read_bytes()).hexdigest(),'box':crop};e['image']=str(out.resolve());e['figure']='Figure 3 (middle training panel)'
  e['excludedRegions']=[[10,440,110,620],[350,400,420,610]]
 if i==36:
  hp=WORK/'cache'/f'{id}-arxiv.html';url=r['arxivUrls'][0].replace('/abs/','/html/')
  c=next(c for c in process_html(hp,base_url=url)['candidates'] if c['figure']=='Figure 1')
  e.update({k:c[k] for k in ['figure','caption','score','scoreReasons','figureAnchor']});e['source_url']=c['image_url'];e['image']=str((WORK/'candidates'/id/'reviewed-figure.png').resolve())
 im=Image.open(e['image']);w,h=im.size
 regions=[[round(a*w),round(b*h),round(c*w),round(d*h)] for a,b,c,d in masks.get(i,[])] if i in masks else e.get('excludedRegions',[])
 e.update(extract_palette(e['image'],exclude_regions=regions));e['imageSHA256']=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 r['extraction']=e;atomic_json(path,r)
 print(i,id,len(e['colors']),e['colors'],flush=True)
packet('root-d',36)
