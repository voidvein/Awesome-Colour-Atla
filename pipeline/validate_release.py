"""Validate every published card, asset and approval. Count is explicit at release."""
import argparse,hashlib,json,re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image

R=Path(__file__).resolve().parents[1]
def validate(expected=None):
 data=json.loads((R/'dist/palettes.json').read_text(encoding='utf8'))
 if expected is not None:assert len(data)==expected,f'{len(data)} papers, expected {expected}'
 assert data and len({p['id'] for p in data})==len(data)
 assert [p['order'] for p in data]==list(range(len(data))), 'Collection order must be stable and complete'
 seen_titles=set();seen_notes=set()
 for p in data:
  canonical=re.sub(r'[^a-z0-9\u4e00-\u9fff]','',p['title'].lower())
  assert canonical not in seen_titles,'Duplicate article title: '+p['title'];seen_titles.add(canonical)
  assert p['noteUrl'] not in seen_notes,'Duplicate source article';seen_notes.add(p['noteUrl'])
  assert 2<=len(p['colors'])<=8 and len(set(p['colors']))==len(p['colors'])
  assert all(re.fullmatch(r'#[0-9A-F]{6}',c) for c in p['colors'])
  assert p['tags'] and p['domain'] in p['tags']
  assert urlparse(p['paper']).scheme=='https' and urlparse(p['noteUrl']).hostname=='papernotes.org'
  assert p['figure'].startswith('Figure ')
  for key in ['image','thumbnail']:
   if key not in p:continue
   rel=Path(p[key]);assert not rel.is_absolute() and '..' not in rel.parts
   with Image.open(R/'dist'/rel) as im:im.verify()
 for name in ['index.html','app.js','style.css']:assert (R/'dist'/name).stat().st_size>100
 seed=json.loads((R/'research/seed-palettes.json').read_text(encoding='utf8'))
 seed_ids={p['id'] for p in seed};new=[p for p in data if p['id'] not in seed_ids]
 for p in data:
  if p['id'] not in seed_ids:continue
  with Image.open(R/'dist'/p['image']) as source:
   image=Image.new('RGBA',source.size,'white');image.alpha_composite(source.convert('RGBA'))
   counts=Counter(image.convert('RGB').getdata())
   assert all(counts[tuple(int(h[i:i+2],16) for i in (1,3,5))]>0 for h in p['colors']),'Seed palette RGB absent from source image'
 if new:
  audits=json.loads((R/'dist/collection-audit.json').read_text(encoding='utf8'))
  def relative_paths(value):
   if isinstance(value,dict):return all(relative_paths(v) for v in value.values())
   if isinstance(value,list):return all(relative_paths(v) for v in value)
   return not (isinstance(value,str) and re.match(r'^[A-Za-z]:[\\/]',value))
  assert relative_paths(audits),'Public audit must use portable relative paths'
  by_id={a['id']:a for a in audits};assert len(by_id)==len(new)
  for p in new:
   a=by_id[p['id']];review=a['review'];e=a['extraction']
   assert review['verdict']=='accepted' and review['reviewer']
   assert e.get('paper')==p['paper'] and e.get('sourceType') and e.get('sourceTitle')
   assert str(e.get('source_url') or e.get('image_url') or '').startswith('https://')
   assert review['reviewedImageSHA256']==e['imageSHA256']
   assert review['reviewedPalette']==p['colors']==e['colors']
   assert review.get('paletteObservation'),'Missing paper-specific colour observation'
   assert len(e['colorEvidence'])==len(p['colors'])
   assert [x['hex'] for x in e['colorEvidence']]==p['colors']
   for c in e['colorEvidence']:assert len(c['sampleXY'])==2 and c['exactSamples']>0
   for path_key,hash_key in [('image','publishedImageSHA256'),('thumbnail','publishedThumbnailSHA256')]:
    assert hashlib.sha256((R/'dist'/p[path_key]).read_bytes()).hexdigest()==a[hash_key]
 manifest=json.loads((R/'dist/collection.json').read_text(encoding='utf8'))
 assert manifest['target']==manifest['published']==len(data) and manifest['reviewed'] is True
 assert manifest['domains']==len({p['domain'] for p in data})
 if 'previousPublished' in manifest:
  assert manifest['added']==7 and manifest['previousPublished']==len(data)-7
  assert manifest['newIds']==[p['id'] for p in data[-7:]]
 assert manifest['colours']==sum(len(p['colors']) for p in data)
 print(f'PASS: {len(data)} unique papers, {len({p["domain"] for p in data})} domains, {sum(len(p["colors"]) for p in data)} colours; all assets and {len(new)} new visual approvals verified.')
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-count',type=int);a=p.parse_args();validate(a.expected_count)
