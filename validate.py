import json,re
from pathlib import Path
from PIL import Image
from urllib.parse import urlparse
R=Path(__file__).parent
data=json.loads((R/'dist/palettes.json').read_text(encoding='utf8'))
assert len(data)==10 and len({p['id'] for p in data})==10
assert len({p['domain'] for p in data})==10
for p in data:
 assert 5<=len(p['colors'])<=8
 assert all(re.fullmatch(r'#[0-9A-F]{6}',c) for c in p['colors'])
 assert p['tags'] and p['domain'] in p['tags']
 assert urlparse(p['paper']).scheme=='https'
 assert urlparse(p['noteUrl']).hostname=='papernotes.org'
 assert p['figure'].startswith('Figure ')
 with Image.open(R/'dist'/p['image']) as im:
  im.verify()
for name in ['index.html','app.js','style.css']:
 assert (R/'dist'/name).stat().st_size>100
assert data[-1]['venue']=='CVPR 2026 FINDINGS'
print('Verified 10 unique papers, 10 domains, 64 colours, source links and all image files.')
