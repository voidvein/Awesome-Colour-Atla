"""Record a manually inspected architecture panel crop without losing source identity."""
from pathlib import Path
import hashlib,json
from PIL import Image
from collect_batch import RECORDS,atomic_json
from extract_figures import extract_palette

def crop(paper_id,box,note):
 path=RECORDS/(paper_id+'.json');r=json.loads(path.read_text(encoding='utf8'));e=r['extraction'];source=Path(e['image'])
 with Image.open(source) as im:
  w,h=im.size;x0,y0,x1,y1=box;assert 0<=x0<x1<=w and 0<=y0<y1<=h
  out=source.with_name('reviewed-architecture.png');im.crop(box).save(out)
 old_crop=e.get('crop')
 if old_crop and len(old_crop)==4:
  a,b,c,d=old_crop;sx=(c-a)/w;sy=(d-b)/h
  e['sourceFigureCrop']=[a+x0*sx,b+y0*sy,a+x1*sx,b+y1*sy]
 e['sourceImageSHA256']=hashlib.sha256(source.read_bytes()).hexdigest();e['sourcePixelCrop']=list(box)
 e['sourceImagePath']=str(source);e['sourceCaption']=e.get('sourceCaption',e['caption']);e['reviewCropNote']=note
 e['image']=str(out);e['imageSHA256']=hashlib.sha256(out.read_bytes()).hexdigest();e.update(extract_palette(out))
 atomic_json(path,r);print(paper_id,'crop',box,e['colors']);return r
