"""Bounded first-18 repairs; does not touch accepted or rejected papers."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from collect_batch import ROOT,WORK,RECORDS,atomic_json
from extract_figures import extract_palette,make_contact_sheet

fresh={
 'cvpr26-8ea2ffc84c58':ROOT/'research/extraction-review/repaired/cvpr26-8ea2ffc84c58.json',
 'cvpr26-c58926db1673':ROOT/'research/extraction-review/repaired/cvpr26-c58926db1673.json',
 'cvpr26-cc3d6f737359':ROOT/'research/extraction-review/repaired/cvpr26-cc3d6f737359.json',
 'cvpr26-39c79b6b46e1':ROOT/'research/extraction-review/repaired/cvpr26-39c79b6b46e1.json',
 'cvpr26-1cf488782e68':ROOT/'research/extraction-review/jarvis-alternate/cvpr26-1cf488782e68.json',
 'cvpr26-f6fefeca849e':ROOT/'research/extraction-review/first-revised/cvpr26-f6fefeca849e.json',
}
masks={
 'cvpr26-c58926db1673':[[970,310,1430,385]],
 'cvpr26-39c79b6b46e1':[[1380,245,1560,580]],
 'cvpr26-012c5a980a26':[[590,156,900,519],[0,0,900,156]],
 'cvpr26-c6b54c86d8be':[[0,0,430,460],[1269,0,1692,460]],
 'cvpr26-bf8daf9a666b':[[0,0,3747,1136],[0,1136,1745,2418],[3330,1136,5133,2418],[1745,1136,3330,1765]],
 # Sample only policy-output node papers, excluding dataset pie, cartoons and example photograph.
 'cvpr26-f6fefeca849e':[[0,0,1050,863],[0,0,1692,190],[0,345,1692,863],[1500,0,1692,863]],
}
packet=json.loads((WORK/'contacts/first/packet.json').read_text(encoding='utf8'));updated=[]
for item in packet:
 id=item['id'];rp=RECORDS/f'{id}.json';r=json.loads(rp.read_text(encoding='utf8'))
 review=WORK/'reviews'/f'{id}.json'
 if review.exists() and json.loads(review.read_text(encoding='utf8'))['verdict'] in ['accepted','rejected']:continue
 e=r['extraction']
 if id in fresh:
  old=dict(e);new=json.loads(fresh[id].read_text(encoding='utf8'))
  image=WORK/'candidates'/id/'reviewed-figure.png';image.parent.mkdir(exist_ok=True)
  shutil.copyfile(new['image'],image)
  for key in ['paper','sourceType','sourceTitle','titleSimilarity','sourcePDFSHA256','source_url']:
   if key in old:new[key]=old[key]
  new.pop('repairAudit',None);new['image']=str(image.resolve());e=new
 regions=masks.get(id,e.get('excludedRegions',[]))
 e.update(extract_palette(e['image'],exclude_regions=regions))
 if id=='cvpr26-bf8daf9a666b':
  # The grey SigLIP2 node is a meaningful neutral fill below the automatic
  # text-exclusion brightness floor. Add its exact source-pixel mode explicitly.
  a=np.asarray(Image.open(e['image']).convert('RGB'));roi=a[450:1000,3747:5000]
  ys,xs=np.where(np.all(roi==[136,136,136],axis=2));assert len(ys)>1000
  e['colors'].append('#888888');e['colorEvidence'].append({'hex':'#888888','rgb':[136,136,136],'sampleXY':[int(xs[0]+3747),int(ys[0]+450)],'exactSamples':len(ys),'neutral':True,'manualRole':'SigLIP2 encoder module fill','sampleRegion':[3747,450,5000,1000]})
 e['imageSHA256']=hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 a=Image.open(e['image']).convert('RGB')
 for evidence in e['colorEvidence']:assert a.getpixel(tuple(evidence['sampleXY']))==tuple(evidence['rgb']),id
 e['paletteStatus']='needs_visual_review' if len(e['colors'])>=2 else 'insufficient_flat_colours'
 e['status']='needs_visual_review';r['extraction']=e;r['status']='needs_visual_review';atomic_json(rp,r)
 updated.append(dict(e,id=id,title=r['title']))
out=WORK/'contacts/first-repaired';out.mkdir(exist_ok=True)
atomic_json(out/'packet.json',updated)
for i in range(0,len(updated),4):make_contact_sheet(updated[i:i+4],out/f'contact-{i//4+1:02d}.png',columns=2,thumb_size=(1000,500))
print([(r['id'],r['figure'],r['colors']) for r in updated])
