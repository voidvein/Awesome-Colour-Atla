import requests,json,time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

ROOT=Path(__file__).parent
(ROOT/'research').mkdir(exist_ok=True)
base='https://papernotes.org/CVPR2026/'
s=BeautifulSoup((ROOT/'source-index.html').read_text(encoding='utf8'),'html.parser').select_one('article')
domains=['image_generation','3d_reconstruction','object_detection','segmentation','image_restoration','remote_sensing','video_understanding','autonomous_driving','robotics','medical_imaging']
items=[]
for domain in domains:
    a=s.select_one(f'a[href^="{domain}/"][href$="/"]')
    url=urljoin(base,a['href'])
    r=requests.get(url,timeout=40); r.raise_for_status()
    (ROOT/'research'/f'{domain}.html').write_text(r.text,encoding='utf8')
    n=BeautifulSoup(r.text,'html.parser').select_one('article')
    links=[x['href'] for x in n.select('a[href]') if 'arxiv.org/' in x['href']]
    item={'id':domain,'title':a.get_text(strip=True),'note':url,'arxiv':links[0] if links else None}
    items.append(item)
    print(json.dumps(item,ensure_ascii=False),flush=True)
    time.sleep(.3)
(ROOT/'research'/'papers.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
