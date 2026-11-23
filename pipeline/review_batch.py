"""Prepare explicit review packets. This command never approves a paper."""
import argparse,json,math,textwrap
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from collect_batch import ROOT,WORK,RECORDS,atomic_json

def packet(name,count=24,exclude=None):
 folder=WORK/'contacts'/name;folder.mkdir(parents=True,exist_ok=True)
 previous=json.loads((folder/'packet.json').read_text(encoding='utf8')) if (folder/'packet.json').exists() else None
 frozen_ids=[r['id'] for r in previous] if previous is not None else None
 reviews=WORK/'reviews';reviews.mkdir(exist_ok=True)
 assigned=set(exclude or [])
 for p in (WORK/'contacts').glob('*/packet.json'):
  if p.parent==folder:continue
  assigned.update(x['id'] for x in json.loads(p.read_text(encoding='utf8')))
 order={r['id']:i for i,r in enumerate(json.loads((WORK/'catalog.json').read_text(encoding='utf8')))}
 records=[]
 for p in RECORDS.glob('*.json'):
  r=json.loads(p.read_text(encoding='utf8'))
  if frozen_ids is not None:
   if r['id'] in frozen_ids:records.append(r)
  elif r['status']=='needs_visual_review' and not (reviews/(r['id']+'.json')).exists() and r['id'] not in assigned:records.append(r)
 records.sort(key=lambda r:frozen_ids.index(r['id']) if frozen_ids is not None else order.get(r['id'],10000))
 if frozen_ids is None:records=records[:count]
 atomic_json(folder/'packet.json',records)
 try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
 except:font=ImageFont.load_default()
 try:small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
 except:small=font
 for start in range(0,len(records),9):
  part=records[start:start+9];w,h=600,410
  sheet=Image.new('RGB',(w*3,h*math.ceil(len(part)/3)),'#edf0f4');d=ImageDraw.Draw(sheet)
  for j,r in enumerate(part):
   x=(j%3)*w;y=(j//3)*h;ex=r['extraction']
   d.text((x+9,y+5),f"{start+j+1}. {r['id']} | {ex.get('figure')} p{ex.get('page','-')}",fill='#27374b',font=font)
   title=r['title']
   for k,line in enumerate(textwrap.wrap(title,73)[:2]):d.text((x+9,y+26+k*16),line,fill='#4b586b',font=small)
   with Image.open(ex['image']) as im:
    rgba=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(rgba)
    thumb=ImageOps.contain(bg.convert('RGB'),(w-22,280));tx=x+(w-thumb.width)//2;ty=y+64+(280-thumb.height)//2;sheet.paste(thumb,(tx,ty))
    for k,c in enumerate(ex.get('colorEvidence',[])):
     px=tx+c['sampleXY'][0]*thumb.width/im.width;py=ty+c['sampleXY'][1]*thumb.height/im.height
     d.ellipse((px-6,py-6,px+6,py+6),fill='white',outline='#111111',width=1)
     d.text((px-3,py-6),str(k+1),font=small,fill='#111111')
   colors=ex.get('colors',[])
   for k,c in enumerate(colors):
    d.rectangle((x+10+k*80,y+350,x+84+k*80,y+374),fill=c)
    d.text((x+10+k*80,y+378),c,fill='#27374b',font=small)
  sheet.save(folder/f'contact-{start//9+1:02}.jpg',quality=94)
 print(json.dumps({'packet':str(folder/'packet.json'),'count':len(records),'sheets':math.ceil(len(records)/9)},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--count',type=int,default=24);a=p.parse_args();packet(a.name,a.count)
