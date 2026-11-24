"""Build a public dataset from source- and image-hash-bound visual approvals."""
import argparse,concurrent.futures,hashlib,json,re,time
from pathlib import Path
from PIL import Image,ImageOps
from collect_batch import ROOT,WORK,RECORDS
from release_common import atomic_json, colour_name, paper_key

def title_key(t):return re.sub('[^a-z0-9\u4e00-\u9fff]','',t.lower())

def public_paths(value):
 if isinstance(value,dict):return {k:public_paths(v) for k,v in value.items()}
 if isinstance(value,list):return [public_paths(v) for v in value]
 if isinstance(value,str) and re.match(r'^[A-Za-z]:[\\/]',value):
  return Path(value).relative_to(ROOT).as_posix()
 return value
def export(target=500,output=None):
 seed=json.loads((ROOT/'research/seed-palettes.json').read_text(encoding='utf8'))
 rows=list(seed);audits=[];seen_titles={title_key(r['title']) for r in rows};seen_papers={paper_key(r['paper']) for r in rows};seen_notes={r['noteUrl'] for r in rows}
 order={r['id']:i for i,r in enumerate(json.loads((WORK/'catalog.json').read_text(encoding='utf8')))}
 reviews=[]
 for p in (WORK/'reviews').glob('*.json'):
  review=json.loads(p.read_text(encoding='utf8'))
  if review.get('verdict')=='accepted':reviews.append(review)
 reviews.sort(key=lambda r:order.get(r['id'],10000))
 errors=[]
 for review in reviews:
  r=json.loads((RECORDS/(review['id']+'.json')).read_text(encoding='utf8'));e=r['extraction'];path=Path(e['image'])
  if not all(e.get(k) for k in ['paper','sourceType','sourceTitle','figure','imageSHA256']):errors.append(r['id']+': incomplete primary source metadata');continue
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  if review.get('reviewedImageSHA256')!=sha:errors.append(r['id']+': stale or absent image review hash');continue
  if review.get('reviewedPalette')!=e.get('colors'):errors.append(r['id']+': stale or absent palette review');continue
  if len(e.get('colors',[]))<2 or not e.get('colorEvidence'):errors.append(r['id']+': incomplete colour evidence');continue
  title=e.get('sourceTitle') or r['title'];tk=title_key(title);pk=paper_key(e['paper'])
  if tk in seen_titles or pk in seen_papers or r['noteUrl'] in seen_notes:continue
  if not 2<=len(e['colors'])<=8:errors.append(r['id']+': invalid colour count');continue
  seen_titles.add(tk);seen_papers.add(pk);seen_notes.add(r['noteUrl'])
  families=list(dict.fromkeys(colour_name(c) for c in e['colors']))
  name=r['title'].split(':')[0]
  if len(name)>48:name=' '.join(name.split()[:7])
  if len(name)>68:name=name[:65]+'…'
  row=dict(id=r['id'],order=len(rows),name=name,title=title,domain=r['domain'],tags=r.get('tags') or [r['domain']],mood=' × '.join(families[:3]),colors=e['colors'],
   analysis=review.get('paletteObservation') or '这张架构图的代表配色包括'+ '、'.join(families[:5])+'。相近色可以保持同类模块的一致性，差异较大的颜色可用于区分不同分支。',
   usage='适合'+r['domain']+'中的模块与数据流示意。沿用这组色彩划分不同功能，文字和细连接线保持深色，以便阅读。',
   image=f"assets/batch500/{r['id']}.webp",thumbnail=f"assets/batch500/{r['id']}-thumb.webp",figure=e['figure'],venue=r['venue'],paper=e['paper'],sourceLabel='arXiv · 原论文' if 'arxiv.org' in e['paper'] else 'CVF · 原论文',noteUrl=r['noteUrl'],
   provenance=f"{e['paper']}，{e['figure']}"+(f"，PDF 第 {e['page']} 页" if e.get('page') else ''),imageSource=e.get('source_url') or e.get('image_url'),
   note='展示原论文中的架构部分，已逐张审查并适屏转存；完整原图见论文链接。色卡等宽，不表示面积比例。',reviewStatus='visually_reviewed')
  compact={k:v for k,v in e.items() if k not in ['candidates','previousExtraction','traceback']}
  rows.append(row);audits.append({'id':r['id'],'extraction':compact,'review':review,'noteUrl':r['noteUrl'],'sourceTitle':title})
  if len(rows)>=target:break
 if len(rows)<target:raise SystemExit(f'NOT COMPLETE: {len(rows)}/{target} unique visually reviewed papers. Approval problems: {errors[:8]}')
 if errors:raise SystemExit('Approval errors: '+str(errors[:10]))
 # Only render asset derivatives once a complete, approved dataset exists.
 asset_dir=ROOT/'dist/assets/batch500';asset_dir.mkdir(exist_ok=True)
 def render(pair):
  row,audit=pair
  with Image.open(audit['extraction']['image']) as source:im=source.convert('RGBA')
  bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);rgb=bg.convert('RGB')
  full=ImageOps.contain(rgb,(2200,2200));full.save(ROOT/'dist'/row['image'],'WEBP',quality=94,method=6)
  thumb=ImageOps.contain(rgb,(820,500));thumb.save(ROOT/'dist'/row['thumbnail'],'WEBP',quality=88,method=6)
  audit['publishedImage']=row['image'];audit['publishedThumbnail']=row['thumbnail']
  audit['publishedImageSHA256']=hashlib.sha256((ROOT/'dist'/row['image']).read_bytes()).hexdigest()
  audit['publishedThumbnailSHA256']=hashlib.sha256((ROOT/'dist'/row['thumbnail']).read_bytes()).hexdigest()
  for key in ['image','sourcePdf','sourceImagePath','originalImage']:
   if key in audit['extraction']:
    try:audit['extraction'][key]=str(Path(audit['extraction'][key]).relative_to(ROOT)).replace('\\','/')
    except ValueError:pass
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
  list(executor.map(render,zip(rows[len(seed):],audits)))
 audits=public_paths(audits)
 atomic_json(WORK/'published-audit.json',audits)
 atomic_json(ROOT/'dist/collection-audit.json',audits)
 result=Path(output) if output else ROOT/'dist/palettes.json';atomic_json(result,rows)
 atomic_json(ROOT/'dist/collection.json',{'target':target,'published':len(rows),'domains':len({r['domain'] for r in rows}),'colours':sum(len(r['colors']) for r in rows),'updatedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'reviewed':True})
 print(f'Published dataset: {len(rows)} unique visually reviewed papers, {len(audits)} new audits.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--target',type=int,default=500);p.add_argument('--output');a=p.parse_args();export(a.target,a.output)
