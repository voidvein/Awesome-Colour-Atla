"""Apply explicitly reviewed exclusion rectangles to sampling, preserving the original figure."""
import argparse,json
from pathlib import Path
from PIL import Image
from collect_batch import RECORDS,atomic_json
from extract_figures import extract_palette

def repair(paper_id,regions,relative=False):
 path=RECORDS/(paper_id+'.json');r=json.loads(path.read_text(encoding='utf8'));e=r['extraction']
 with Image.open(e['image']) as im:w,h=im.size
 if relative:regions=[[round(x0*w),round(y0*h),round(x1*w),round(y1*h)] for x0,y0,x1,y1 in regions]
 assert all(0<=x0<x1<=w and 0<=y0<y1<=h for x0,y0,x1,y1 in regions)
 e.update(extract_palette(e['image'],exclude_regions=regions));atomic_json(path,r)
 print(paper_id,e['colors']);return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('regions');p.add_argument('--relative',action='store_true');a=p.parse_args();repair(a.id,json.loads(a.regions),a.relative)
