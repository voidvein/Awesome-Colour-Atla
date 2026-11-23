import requests,json,time
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
R=Path(__file__).parent
ids=['3d_reconstruction','image_restoration','video_understanding','autonomous_driving','medical_imaging']
for item in json.loads((R/'research/papers.json').read_text(encoding='utf8')):
 if item['id'] not in ids: continue
 s=BeautifulSoup((R/'research'/f"{item['id']}.html").read_text(encoding='utf8'),'html.parser').select_one('article')
 urls=[a['href'] for a in s.select('a[href]') if any(h in a['href'] for h in ['arxiv.org/','openaccess.thecvf.com','github.io'])]
 for url in urls:
  if 'arxiv.org/abs/' in url:url=url.replace('/abs/','/html/')
  try:
   r=requests.get(url,timeout=45); print(item['id'],r.status_code,url,flush=True)
   if r.status_code!=200:continue
   (R/'research'/f"{item['id']}-original.html").write_text(r.text,encoding='utf8')
   b=BeautifulSoup(r.text,'html.parser')
   print('IMAGES',[(x.get('src'),x.get('alt','')[:150]) for x in b.select('img')][:14],flush=True)
   print('PDF',[(a.get_text(),a['href']) for a in b.select('a[href]') if '.pdf' in a['href']][:3],flush=True)
   if b.select('figure'):print('FIGURES',[(x.get('id'),x.get_text(' ',strip=True)[:280]) for x in b.select('figure')][:6],flush=True)
  except Exception as e:print(str(e),flush=True)
  time.sleep(.4)
