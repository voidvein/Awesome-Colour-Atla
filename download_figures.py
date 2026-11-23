import requests,json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
R=Path(__file__).parent
(R/'dist/assets').mkdir(parents=True,exist_ok=True)
items=[]
for item in json.loads((R/'research/papers.json').read_text(encoding='utf8')):
 id=item['id']
 if id not in ['3d_reconstruction','image_restoration','video_understanding','autonomous_driving','medical_imaging']:continue
 note=BeautifulSoup((R/'research'/f'{id}.html').read_text(encoding='utf8'),'html.parser').select_one('article')
 if id in ['video_understanding','autonomous_driving']:
  url={'video_understanding':'https://arxiv.org/html/2512.02425v2/fig_method.png','autonomous_driving':'https://arxiv.org/html/2505.16278v2/drivemoe.png'}[id]
  path=R/'dist/assets'/f'{id}.png'
  paper=item['arxiv'];figure='Figure 2'
 else:
  source=next(a['href'] for a in note.select('a[href]') if 'openaccess.thecvf.com' in a['href'])
  orig=BeautifulSoup((R/'research'/f'{id}-original.html').read_text(encoding='utf8'),'html.parser')
  url=urljoin(source,next(a['href'] for a in orig.select('a[href]') if a.get_text(strip=True)=='pdf'))
  path=R/'research'/f'{id}.pdf'; paper=source;figure=None
 r=requests.get(url,timeout=90);r.raise_for_status();path.write_bytes(r.content)
 items.append(dict(item,paper=paper,figure=figure,source_image=url,file=str(path.relative_to(R))))
 print(id,len(r.content),str(path),flush=True)
(R/'research/assets-b.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
