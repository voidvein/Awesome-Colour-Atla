from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).parent
urls={'image_restoration':'https://arxiv.org/html/2505.21541v3/Fig3.png','medical_imaging':'https://raw.githubusercontent.com/CVIU-CSU/GVL-MIL/main/assets/main_framework_01.png'}
def get(kv):
 k,v=kv
 try:
  r=requests.get(v,timeout=40);r.raise_for_status();(R/'dist/assets'/f'{k}.png').write_bytes(r.content);print(k,len(r.content),flush=True)
 except Exception as e: print(k,str(e),flush=True)
with ThreadPoolExecutor(2) as ex:list(ex.map(get,urls.items()))
