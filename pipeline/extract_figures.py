"""Local, evidence-preserving architecture-figure selection and colour sampling.

Selection is a candidate, never a visual verification. All exported records retain
``status=needs_visual_review`` until an independent reviewer accepts the crop.
No network requests are made by this module.
"""
from __future__ import annotations
import argparse, colorsys, hashlib, json, math, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.pdfdeps'))
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

POSITIVE = {
    'architecture': 10, 'framework': 9, 'pipeline': 8, 'overall': 5,
    'overview': 7, 'proposed method': 6, 'network': 6, 'model structure': 8,
    'training procedure': 4, 'training process': 4, 'system': 3,
    'methodology': 5, 'encoder': 2, 'decoder': 2, 'module': 3,
}
NEGATIVE = {
    'qualitative': -12, 'quantitative': -12, 'visualization': -5,
    'comparison': -6, 'ablation': -12, 'performance': -8, 'teaser': -10,
    'benchmark': -5, 'accuracy': -5, 'failure cases': -10,
    'examples of': -5, 'example results': -10, 'illustrative results': -10,
}
FIG = re.compile(r'^\s*(?:Figure|Fig\.)\s*(\d+)\s*[.:：]?', re.I)
CAPTION_START = re.compile(r'^\s*(?:Figure|Fig\.)\s*(\d+)\s*[.:：]', re.I)


def score_caption(caption: str) -> tuple[int, list[str]]:
    """Caption-only score; a high score is not proof that a graphic is a network."""
    text = re.sub(r'\s+', ' ', caption).lower()
    header = FIG.sub('', text).strip()[:180]
    forbidden = ['user study', 'user interface', 'study interface', 'statistical distribution', 'histogram', 'qa samples', 'question types']
    if any(term in header for term in forbidden):
        return -80, ['non-model interface/statistics:-80']
    named_model_overview=bool(re.search(r'\boverview of .{0,55}(?:net|model|method|ours|our)\b',header))
    strong = named_model_overview or any(term in text for term in ['architecture','framework','pipeline','model structure','proposed method','training procedure','training process'])
    if ('dataset' in header or 'benchmark' in header or '-bench' in header) and not strong:
        return -60, ['dataset/benchmark without model structure:-60']
    reasons = [f'{word}:{score:+d}' for word, score in {**POSITIVE, **NEGATIVE}.items() if word in text]
    score = sum(int(x.rsplit(':', 1)[-1]) for x in reasons)
    mechanism = [term for term in ['latent block','kv cache','kv caching','attention','encoder','decoder','token','projection','feature fusion','denoising','positional encoding','rope coordinates'] if term in text]
    if len(mechanism)>=3 and not strong:
        score+=10;reasons.append('multiple computational-mechanism cues:+10')
    if any(term in header[:110] for term in ['architecture','framework','pipeline','model structure']):
        score+=12;reasons.append('architecture in caption lead:+12')
    if named_model_overview:
        score+=14;reasons.append('named model overview:+14')
    if not strong and len(mechanism)<3:
        score -= 20
        reasons.append('no strong model-structure evidence:-20')
    return score, reasons


def _lab(rgb):
    a = np.asarray(rgb, dtype=float) / 255
    a = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)
    xyz = np.array([[.4124564,.3575761,.1804375],[.2126729,.7151522,.072175],[.0193339,.119192,.9503041]]) @ a
    xyz /= np.array([.95047,1,1.08883])
    f = np.where(xyz > .008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116*f[1]-16,500*(f[0]-f[1]),200*(f[1]-f[2])])


def extract_palette(image_path, n_colors=7, exclude_regions=None):
    """Sample exact source RGB pixels from locally flat fills and strokes.

    Returns colours and pixel evidence. Small textured photos are suppressed by
    local-flatness and colour-frequency checks; review remains mandatory.
    """
    with Image.open(image_path) as source:
        im = source.convert('RGBA')
        background = Image.new('RGBA', im.size, 'white')
        im = Image.alpha_composite(background, im).convert('RGB')
    original = np.asarray(im)
    hi = np.asarray(im.filter(ImageFilter.MaxFilter(3))).astype(np.int16)
    lo = np.asarray(im.filter(ImageFilter.MinFilter(3))).astype(np.int16)
    step = max(1, int(math.ceil(max(im.size) / 1400)))
    pix = original[::step, ::step]
    flat = np.max((hi-lo)[::step, ::step], axis=2) <= 14
    maximum = pix.max(axis=2).astype(int)
    minimum = pix.min(axis=2).astype(int)
    chroma = maximum-minimum
    # Exclude white paper, dark neutral text, and very pale near-white antialiasing.
    eligible = flat & (minimum < 245) & (maximum > 65) & ((chroma >= 12) | ((maximum < 225) & (minimum > 140)))
    for rect in exclude_regions or []:
        x0,y0,x1,y1=rect
        eligible[max(0,int(y0)//step):math.ceil(y1/step),max(0,int(x0)//step):math.ceil(x1/step)]=False
    yxs = np.argwhere(eligible)
    if not len(yxs):
        return {'colors': [], 'colorEvidence': [], 'paletteStatus': 'insufficient_flat_colours', 'method': 'exact RGB, flat 3x3 neighbourhood'}
    values = pix[eligible]
    # Bins merge slight gradient/antialias variants, but representatives remain actual pixels.
    bins = (values.astype(np.int32)//8)
    keys = bins[:,0]*1024+bins[:,1]*32+bins[:,2]
    counts = Counter(keys.tolist())
    candidates=[]
    minimum_count = max(8, int(len(yxs)*.0015))
    for key, count in counts.most_common(250):
        if count < minimum_count:
            break
        indices = np.flatnonzero(keys == key)
        exact = Counter(map(tuple, values[indices].tolist()))
        rgb, exact_count = exact.most_common(1)[0]
        neutral = max(rgb)-min(rgb) < 12
        candidates.append((rgb, count, exact_count, indices, neutral))
    chosen=[]
    for threshold in [17, 12, 8]:
        for rgb, count, exact_count, indices, neutral in candidates:
            lab=_lab(rgb)
            if any(np.linalg.norm(lab-e['_lab']) < threshold for e in chosen):
                continue
            if neutral and sum(e['neutral'] for e in chosen)>=1:
                continue
            chosen_index = next(i for i in indices if tuple(values[i]) == rgb)
            yy,xx = yxs[chosen_index]
            chosen.append({'hex':'#%02X%02X%02X'%rgb, 'rgb':list(map(int,rgb)),
                'flatBinSamples':int(count), 'exactSamples':int(exact_count),
                'sampleXY':[int(xx*step),int(yy*step)], 'sampledStride':step,
                'flatSampleShare':round(count/len(yxs),5), 'neutral':bool(neutral), '_lab':lab})
            if len(chosen)>=n_colors:break
        if len(chosen)>=n_colors:break
    for e in chosen:e.pop('_lab')
    return {'colors':[e['hex'] for e in chosen], 'colorEvidence':chosen,
        'paletteStatus':'needs_visual_review' if len(chosen)>=2 else 'insufficient_flat_colours',
        'eligibleSamples':len(yxs), 'imageSize':list(im.size),
        'excludedRegions':exclude_regions or [],
        'method':'exact RGB pixel modes in locally flat 3x3 areas; Lab-distance diversity; white/dark text excluded; max one neutral',
        'warning':'Flat colours inside photographs can remain; reviewer must check module correspondence. Equal swatches do not indicate area shares.'}


def _text_blocks(page):
    return [{'rect':fitz.Rect(b[:4]),'text':re.sub(r'\s+',' ',b[4]).strip()} for b in page.get_text('blocks') if len(b)>4 and isinstance(b[4],str)]


def pdf_candidates(pdf_path):
    if fitz is None:raise RuntimeError('PyMuPDF is required; use the project .pdfdeps environment.')
    doc=fitz.open(pdf_path)
    candidates=[]
    supplementary=False
    for pi in range(min(len(doc),20)):
        page=doc[pi]
        if pi>4 and re.search(r'(?im)^\s*(supplementary material|supplemental material|appendix)\s*$',page.get_text()):supplementary=True
        for block in page.get_text('dict')['blocks']:
            lines=block.get('lines',[])
            for li,line in enumerate(lines):
                text=''.join(s.get('text','') for s in line['spans']).strip()
                match=CAPTION_START.match(text)
                if not match:continue
                # Search individual lines: a final diagram label and a caption
                # are often merged into one MuPDF text block (VLM-3R Fig.3).
                base=max(s['size'] for s in line['spans'])
                picked=[line];last_y=line['bbox'][3]
                for other in lines[li+1:]:
                    ot=''.join(s.get('text','') for s in other['spans']).strip()
                    size=max((s['size'] for s in other['spans']),default=base)
                    if FIG.match(ot) or size>base+.65 or other['bbox'][1]-last_y>max(8,base*.9):break
                    picked.append(other);last_y=other['bbox'][3]
                caption=' '.join(''.join(s.get('text','') for s in ln['spans']).strip() for ln in picked)
                caption=re.sub(r'\s+',' ',caption)
                rect=fitz.Rect(picked[0]['bbox'])
                for ln in picked[1:]:rect|=fitz.Rect(ln['bbox'])
                score,reasons=score_caption(caption)
                if supplementary:score-=10;reasons.append('supplementary material:-10')
                elif pi>=8:score-=4;reasons.append('late-page candidate:-4')
                candidates.append({'figure':f'Figure {match[1]}','caption':caption,'page':pi+1,
                    'captionRect':list(rect),'score':score,'scoreReasons':reasons,'captionFontSize':round(base,2)})
    doc.close()
    return sorted(candidates,key=lambda c:(-c['score'],c['page']))


def _crop_rect(page, candidate):
    """Find graphics immediately above caption; retain full column or page width."""
    cr=fitz.Rect(candidate['captionRect']); width=page.rect.width
    full=cr.width>width*.57 or (cr.x0<width*.5-10 and cr.x1>width*.5+10)
    if full:x0,x1=page.rect.x0+24,page.rect.x1-24
    elif cr.x0<width*.4:x0,x1=24,width/2-5
    else:x0,x1=width/2+4,width-24
    bottom=cr.y0-.5
    # Caption highlight backgrounds may protrude above the text bbox. Exclude
    # those without stealing the preceding diagram's low-sitting text labels.
    for drawing in page.get_drawings():
        r=fitz.Rect(drawing['rect'])
        if 0<r.height<22 and r.width<110 and cr.y0-7<r.y0<cr.y0 and r.y1>cr.y0 and r.x1>cr.x0 and r.x0<cr.x1:
            bottom=min(bottom,r.y0-.5)
    shapes=[]
    for d in page.get_drawings():
        r=fitz.Rect(d['rect'])
        if r.is_empty:r=fitz.Rect(r.x0-1,r.y0-1,r.x1+1,r.y1+1)
        if r.y1<=bottom+2 and r.y0>22 and r.x1>x0 and r.x0<x1 and (r.width>3 or r.height>3):
            shapes.append(r)
    for info in page.get_image_info():
        r=fitz.Rect(info['bbox'])
        if r.y1<=bottom+3 and r.y0>22 and r.x1>x0 and r.x0<x1 and r.width*r.height>200:
            shapes.append(r)
    near=[r for r in shapes if r.y1>=bottom-90]
    warnings=[]
    if not near:
        top=max(30,bottom-240);warnings.append('No graphics near caption; conservative 240pt fallback requires crop review.')
    else:
        top=min(r.y0 for r in near)
        changed=True
        while changed:
            changed=False
            for r in shapes:
                if r.y1>=top-18 and r.y0<top:
                    top=r.y0;changed=True
        first_graphic_top=top
        top=max(24,top-12)
        # Padding must not reintroduce the final line of the preceding caption
        # or body paragraph, particularly for stacked method figures.
        for block in _text_blocks(page):
            r=block['rect']
            if r.y1<=first_graphic_top-1 and r.y1>top and r.x1>x0 and r.x0<x1:
                top=max(top,r.y1+3)
    # Figure labels can extend horizontally beyond caption edges, so retain the full column.
    rect=fitz.Rect(x0,top,x1,bottom)&page.rect
    if rect.height<35:warnings.append('Very shallow crop; manual correction required.')
    return rect,warnings


def process_pdf(pdf_path, outdir, paper_id, source_url=None, candidate_index=0):
    candidates=pdf_candidates(pdf_path)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    if not candidates or candidates[0]['score']<3:
        return {'id':paper_id,'status':'no_architecture_candidate','source_url':source_url,'candidates':candidates}
    candidate=candidates[candidate_index]
    with fitz.open(pdf_path) as doc:
        page=doc[candidate['page']-1];rect,warnings=_crop_rect(page,candidate)
        target=outdir/f'{paper_id}.png'
        zoom=min(3,2000/max(rect.width,rect.height))
        page.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=rect,alpha=False,annots=False).save(target)
    result={'id':paper_id,**candidate,'source_url':source_url,'sourcePdf':str(Path(pdf_path).resolve()),
        'image':str(target.resolve()),'crop':list(rect),'cropWarnings':warnings,
        'status':'needs_visual_review','candidates':candidates,**extract_palette(target)}
    (outdir/f'{paper_id}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return result


def process_html(html_path, outdir=None, paper_id=None, base_url='', fetch=None):
    """Discover arXiv/author HTML figures. ``fetch`` retained for caller compatibility; unused."""
    from bs4 import BeautifulSoup
    if isinstance(html_path,Path) or not str(html_path).lstrip().startswith('<'):
        html=Path(html_path).read_text(encoding='utf8')
    else:
        html=str(html_path)
    soup=BeautifulSoup(html,'html.parser');candidates=[]
    for n,figure in enumerate(soup.select('figure'),1):
        caption=figure.select_one('figcaption')
        caption=caption.get_text(' ',strip=True) if caption else figure.get_text(' ',strip=True)
        if not caption or caption.lstrip().lower().startswith('table'):continue
        score,reasons=score_caption(caption)
        number=re.search(r'(?:Figure|Fig\.)\s*(\d+)',caption,re.I)
        images=[i for i in figure.select('img') if i.get('src') and not i['src'].startswith('data:')]
        if not images:continue
        for index,image in enumerate(images):
            candidates.append({'figure':f'Figure {number[1]}' if number else f'Figure candidate {n}',
                'caption':caption,'image_url':urljoin(base_url,image['src']),
                'figureAnchor':figure.get('id'),'panelIndex':index,'panelCount':len(images),
                'score':score,'scoreReasons':reasons,'status':'needs_visual_review'})
    candidates.sort(key=lambda c:-c['score'])
    result={'id':paper_id,'source_url':base_url,'status':'needs_visual_review' if candidates and candidates[0]['score']>=3 else 'no_architecture_candidate','candidates':candidates}
    if outdir:
        Path(outdir).mkdir(parents=True,exist_ok=True)
        (Path(outdir)/f'{paper_id or "html"}-candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return result


def make_contact_sheet(records, outpath, columns=3, thumb_size=(520,250)):
    rows=math.ceil(len(records)/columns);w,h=thumb_size
    sheet=Image.new('RGB',(columns*w,rows*(h+46)),'#edf0f4');draw=ImageDraw.Draw(sheet)
    try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    except OSError:font=ImageFont.load_default()
    for i,record in enumerate(records):
        x=(i%columns)*w;y=(i//columns)*(h+46)
        image=record.get('image') or record.get('localPath')
        if image:
            image=Path(image) if Path(image).is_absolute() else ROOT/image
            try:
                with Image.open(image) as source:thumb=ImageOps.contain(source.convert('RGB'),(w-18,h-12))
                sheet.paste(thumb,(x+(w-thumb.width)//2,y+24+(h-thumb.height)//2))
            except (OSError,ValueError):draw.text((x+10,y+50),'IMAGE UNAVAILABLE',fill='red',font=font)
        label=f'{record.get("reviewIndex",i+1)}. {str(record.get("id", "?"))[:38]} | {record.get("figure", "?")} p{record.get("page", "-")}'
        draw.text((x+9,y+5),label[:74],fill='#263248',font=font)
        colors=record.get('colors',[])
        for j,color in enumerate(colors):draw.rectangle((x+10+j*30,y+h+26,x+38+j*30,y+h+40),fill=color)
    Path(outpath).parent.mkdir(parents=True,exist_ok=True);sheet.save(outpath)
    return str(Path(outpath).resolve())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input');parser.add_argument('--outdir',default='research/extraction-review');parser.add_argument('--id',default='paper');parser.add_argument('--source-url',default='')
    args=parser.parse_args();p=Path(args.input)
    if p.suffix.lower()=='.pdf':result=process_pdf(p,args.outdir,args.id,args.source_url)
    elif p.suffix.lower() in ['.html','.htm']:result=process_html(p,args.outdir,args.id,args.source_url)
    else:result={'id':args.id,'image':str(p.resolve()),'status':'needs_visual_review',**extract_palette(p)}
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
