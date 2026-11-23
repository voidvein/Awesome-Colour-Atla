"""Bounded, explicit semantic palette edits after audit-g visual inspection."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from extract_figures import extract_palette
from review_batch import packet
items=json.loads((WORK/'contacts/audit-g/packet.json').read_text(encoding='utf8'))
keep={
1:['#D9D9D9','#C00000','#FF0000','#548235','#4472C4'],
2:['#F1F4FD','#C2C3C7','#FB8A90'],
8:['#FFF1CC','#FFD966','#A9D18E','#D9D9D9','#E1EFD9'],
9:['#FFDDDD','#DFEAFC','#F8F4AC','#FFBC8D','#C1EBA3','#78C1F3'],
11:['#F7E97D','#9FCE7E','#9FCFFF','#FFC184','#FFF1CC','#FC7158'],
15:['#D9E7FB','#F7CDCC','#D5E7D4'],
18:['#EF634B','#28C3C3','#FABE0A'],
19:['#D9ECFF','#FAEFE0','#FBD0A9','#F9E9FB'],
20:['#FBE4D5','#B7D6EE','#A6D089','#8BA6D6','#FDE694'],
21:['#FAE4D5','#D2E3F4','#8FAADC','#F4B083','#C5DFB4','#DDCCE4'],
23:['#EE9F6A','#6D8FCE','#172B51'],
25:['#C1E5F5','#F2CFED','#D9F2D0','#FBE3D6'],
26:['#BDBDBD','#EAF5F6'],
27:['#E2EAF4','#57391F','#D7C09A','#7D9DC4','#2F4871'],
30:['#F2DCC9','#C1E5F5','#B4E5A1','#F2AA84','#9CD9C2'],
32:['#E6EFFC','#EBB6B2','#E5F2DF','#F7E8ED','#CFD7E2'],
33:['#FFF8E4','#C8D3DB','#EED2BE','#E1EFD9','#EBF4F8','#DFCEE1'],
34:['#BA9EDB','#D1C4DC','#91ACE0','#8451E1','#F5B7BF','#EDDDD5'],
35:['#FFF1D6','#DEEBF7','#FFD09B','#F0CCD3','#F5EBDF'],
36:['#D9D9D9','#E0EAD7'],
38:['#FDF3E8','#C9C6DA','#D5B18E','#C9E0D5','#E5F3EA'],
39:['#DAE7FB','#FFF1CC','#E1EFD7','#F1FDFD'],
42:['#CCE6BA','#F5BEC4','#9BB4E2','#D3DFE6','#FBB52B','#1870B7'],
45:['#FFF1CC','#DEEBF7','#A9D18E','#F8CAAC','#E1EFD9'],
47:['#F8CDAC','#AEEBE5','#FDEAA9','#D7C6E4','#FAE2E5'],
50:['#DCEAF7','#D1BCD3','#FFECA9','#F7CAAC','#FFFFF2','#FCE2E0'],
51:['#FFE6A9','#FFD1C7','#FFF2E0'],
54:['#BED4E9','#BDD9CD','#73A69D','#8EAEBB'],
}
for i,item in enumerate(items,1):
 if i in {4,7,10,43,44}:continue
 p=RECORDS/(item['id']+'.json');r=json.loads(p.read_text(encoding='utf8'));e=r['extraction']
 if i==15 and not e.get('sourcePixelCrop'):
  src=Path(e['image']);box=[0,0,1692,610];dest=src.parent/'reviewed-diagram.png';Image.open(src).crop(box).save(dest)
  e['sourcePixelCrop']={'sourceImage':str(src),'sourceImageSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'box':box};e['reviewCropNote']='Original Fig3 two complete diagram panels; their prose explanations below the diagrams excluded.';e['image']=str(dest.resolve())
  # Palette points are re-extracted after changing raster coordinates.
  e.update(extract_palette(e['image'],exclude_regions=[[200,390,330,580],[550,235,850,520],[950,380,1550,600]]))
 if i==29:
  im=Image.open(e['image']);w,h=im.size;e.update(extract_palette(e['image'],exclude_regions=[[0,0,w,800]]))
 if i in keep:
  selected=[c for c in keep[i] if c in e['colors']]
  e['colors']=selected;e['colorEvidence']=[x for x in e['colorEvidence'] if x['hex'] in selected]
  e['paletteSelectionNote']='Reviewer retained only visible neural-module or semantic diagram fills/lines; photograph, result heatmap, decorative and redundant modes removed.'
 if i in {29,37,53}:
  a=np.asarray(Image.open(e['image']).convert('RGB'));evidence=[]
  specs={29:[([250,228,213],'Trainable policy neural model',[505,875,695,1000]),([218,226,243],'Reference neural model and GRPO module',[1325,880,1555,1050]),([222,235,247],'Verifiable-reward module',[750,880,1300,1060]),([197,90,17],'GRPO policy-update feedback connector',[600,825,1450,880])],37:[([222,245,255],'Video-summary/temporal-grounding task panels',[0,130,505,384]),([250,226,213],'MedGRPO neural training module',[533,280,641,340]),([4,35,51],'LLM Judge and MedGRPO neural module outlines',[548,30,752,192])],53:[([234,153,153],'Pretrained/adapted stereo neural-network blocks',[1427,40,1597,485]),([230,145,56],'Trainable neural adaptation module',[1428,337,1465,487])]}[i]
  for rgb,role,box in specs:
   x0,y0,x1,y1=box;ys,xs=np.where(np.all(a[y0:y1,x0:x1]==rgb,axis=2));assert len(xs)>5,(i,rgb)
   evidence.append({'hex':'#%02X%02X%02X'%tuple(rgb),'rgb':rgb,'sampleXY':[int(xs[len(xs)//2]+x0),int(ys[len(ys)//2]+y0)],'exactSamples':int(len(xs)),'sampleRegion':box,'manualRole':role})
  e['colors']=[x['hex'] for x in evidence];e['colorEvidence']=evidence;e['method']='Explicit exact-source neural module fill/outline pixels in reviewer-selected semantic regions; image examples and numerical output plots excluded.'
 if i==26:
  a=np.asarray(Image.open(e['image']).convert('RGB'));evidence=[]
  for rgb,role,box in [([189,189,189],'Patch neural-feature blocks',[430,60,500,240]),([87,179,186],'Cell-type prototype feature matrix outlines',[835,95,995,214]),([236,78,40],'Learned cell-type weighting matrix outlines',[650,85,754,217])]:
   x0,y0,x1,y1=box;ys,xs=np.where(np.all(a[y0:y1,x0:x1]==rgb,axis=2));assert len(xs)>5
   evidence.append({'hex':'#%02X%02X%02X'%tuple(rgb),'rgb':rgb,'sampleXY':[int(xs[len(xs)//2]+x0),int(ys[len(ys)//2]+y0)],'exactSamples':int(len(xs)),'sampleRegion':box,'manualRole':role})
  e['colors']=[x['hex'] for x in evidence];e['colorEvidence']=evidence;e['method']='Exact-source neural feature blocks and semantic learned-weight/prototype matrix line colours; histology and gene-result plots excluded.'
 e['imageSHA256']=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 im=Image.open(e['image']).convert('RGB');assert 2<=len(e['colors'])<=8,(i,e['colors'])
 for x in e['colorEvidence']:assert im.getpixel(tuple(x['sampleXY']))==tuple(x['rgb']),(i,x)
 r['extraction']=e;atomic_json(p,r);print(i,e['colors'],flush=True)
packet('audit-g',54)
