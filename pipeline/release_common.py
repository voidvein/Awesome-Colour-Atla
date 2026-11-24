"""Small dependency-free shared release helpers."""
import colorsys,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def atomic_json(path,data):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');tmp.replace(path)
def paper_key(url):
 m=re.search(r'arxiv.org/(?:abs|html|pdf)/(\d+\.\d+)',url)
 return 'arxiv:'+m[1] if m else url.split('?')[0].replace('/html/','/papers/').replace('_paper.html','_paper.pdf')
def colour_name(hx):
 rgb=tuple(int(hx[i:i+2],16)/255 for i in [1,3,5]);h,l,s=colorsys.rgb_to_hls(*rgb)
 if s<.12:return '黑色' if l<.15 else '浅灰色' if l>.85 else '灰色'
 d=h*360;name='红色' if d<15 or d>=345 else '橙色' if d<45 else '黄色' if d<70 else '绿色' if d<155 else '青色' if d<195 else '蓝色' if d<255 else '紫色' if d<290 else '粉色'
 return ('浅' if l>.76 else '深' if l<.36 else '')+name
