"""Append one reviewed NeurIPS batch; requires the currently released assets restored."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tempfile
import time
import unicodedata
from urllib.parse import urlsplit, unquote

from PIL import Image, ImageChops, ImageOps

from release_common import ROOT, atomic_json, colour_name, paper_key
from validate_release import validate

BATCH = 7
LICENSE = 'https://creativecommons.org/licenses/by/4.0/'

def json_file(path):
    return json.loads(path.read_text(encoding='utf8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def title_key(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())

def note_key(s):
    u = urlsplit(s)
    return (u.hostname, unquote(u.path).rstrip('/').casefold())

def on_host(url, host):
    u = urlsplit(url)
    return u.scheme == 'https' and u.hostname == host and not u.username and not u.password

def rgb_image(path):
    with Image.open(path) as source:
        source = source.convert('RGBA')
    background = Image.new('RGBA', source.size, 'white')
    background.alpha_composite(source)
    return background.convert('RGB')

def append(packet, baseline_sha):
    dist = ROOT / 'dist'
    palette_file = dist / 'palettes.json'
    audit_file = dist / 'collection-audit.json'
    collection_file = dist / 'collection.json'
    rows, audits, collection = [json_file(p) for p in (palette_file,audit_file,collection_file)]
    assert sha(palette_file) == baseline_sha, 'Wrong or concurrently changed baseline'
    assert collection['target'] == collection['published'] == len(rows), 'Baseline totals differ'
    validate(len(rows))
    batch = json_file(packet)
    assert isinstance(batch,list) and len(batch) == BATCH, 'Exactly 7 reviewed cards are required'
    seen_ids = {x['id'] for x in rows}
    seen_titles = {title_key(x['title']) for x in rows}
    seen_papers = {paper_key(x['paper']) for x in rows}
    seen_notes = {note_key(x['noteUrl']) for x in rows}
    staged, added_rows, added_audits = [], [], []
    # A failed record must not leave edited catalogues or derivative files in dist.
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        for card in batch:
            key = card['id']
            assert re.fullmatch(r'neurips2026-[a-z0-9][a-z0-9-]{1,65}',key), f'{key}: unsafe ID'
            assert re.fullmatch(r'Figure [1-9][0-9]*[a-z]?',card['figure']), f'{key}: unverified figure number'
            for field in ('title','observation','reviewer','reviewedAt','attribution','domain','rightsSource'):
                assert isinstance(card[field],str) and card[field].strip(), f'{key}: missing {field}'
            paper = card['arxiv']
            note = card['noteUrl']
            assert on_host(paper,'arxiv.org') and re.fullmatch(r'/html/\d{4}\.\d{4,5}v\d+',urlsplit(paper).path), f'{key}: exact arXiv text version required'
            assert on_host(note,'papernotes.org') and urlsplit(note).path.startswith('/NeurIPS2026/'), f'{key}: wrong Paper Notes conference'
            assert on_host(card['rightsSource'],'arxiv.org') and urlsplit(card['rightsSource']).path.split('/',2)[-1]==urlsplit(paper).path.split('/',2)[-1], f'{key}: rights must identify this exact paper version'
            assert card['rights'] == 'CC BY 4.0' and card['license_url']==LICENSE, f'{key}: incompatible or unverified license'
            assert card.get('reviewReason','').strip(), f'{key}: record what was visually approved'
            assert on_host(card['imageUrl'],'arxiv.org') and urlsplit(card['imageUrl']).path.startswith(urlsplit(paper).path+'/'), f'{key}: supplied asset is not under the verified paper version'
            keys = (key,title_key(card['title']),paper_key(paper),note_key(note))
            for seen,value in zip((seen_ids,seen_titles,seen_papers,seen_notes),keys):
                assert value not in seen, f'{key}: duplicate id/title/paper/note'
                seen.add(value)
            def relative(field):
                filename = card[field]
                path = (packet.parent/filename).resolve()
                assert not Path(filename).is_absolute() and path.is_relative_to(packet.parent.resolve()), f'{key}: figure file must reside beside packet'
                return path
            original = relative('sourceImage')
            review_path = relative('localImage')
            source_sha = sha(original)
            review_sha = sha(review_path)
            assert source_sha == card['sourceSHA256'], f'{key}: cited source bytes changed'
            assert review_sha == card['imageSHA256'], f'{key}: visually reviewed image changed'
            assert card.get('modifications','').strip(), f'{key}: figure transformation must be disclosed'
            raster = relative('sourceRaster') if card.get('sourceRaster') else original
            if raster != original:
                assert original.suffix.lower()=='.svg' and sha(raster)==card['sourceRasterSHA256'], f'{key}: only checksum-bound SVG rasterization is supported'
            image = rgb_image(review_path)
            source_raster = rgb_image(raster)
            bbox = card.get('cropBox')
            if bbox is None:
                bbox = (0,0,source_raster.width,source_raster.height)
            else:
                assert len(bbox)==4 and all(type(v) is int for v in bbox),f'{key}: invalid crop coordinates'
                l,t,r,b = bbox
                assert 0<=l<r<=source_raster.width and 0<=t<b<=source_raster.height,f'{key}: crop outside source image'
            expected_raster = source_raster.crop(bbox)
            assert expected_raster.size==image.size and ImageChops.difference(expected_raster,image).getbbox() is None, f'{key}: shown raster is not the claimed untouched raster/crop'
            counts = Counter(image.getdata())
            samples = []
            seen_hex = set()
            for item in card['colors']:
                h = item['hex']
                assert re.fullmatch(r'#[A-F0-9]{6}',h) and h not in seen_hex, f'{key}: invalid or duplicate hex'
                seen_hex.add(h)
                rgb = tuple(bytes.fromhex(h[1:]))
                x,y = item['sampleXY']
                assert type(x) is int and type(y) is int and 0<=x<image.width and 0<=y<image.height and image.getpixel((x,y))==rgb, f'{key}: literal pixel sample disagrees'
                assert item.get('exactSamples') == counts[rgb] > 0, f'{key}: inconsistent exact pixel count'
                source_xy = [x+bbox[0],y+bbox[1]]
                assert card.get('coordinateBasis') and item.get('sourceSampleXY')==source_xy, f'{key}: source coordinate disagrees'
                samples.append({'hex':h,'rgb':list(rgb),'sampleXY':[x,y],'sourceSampleXY':source_xy,'exactSamples':counts[rgb]})
            colours = [c['hex'] for c in samples]
            assert 2<=len(colours)<=8 and len(seen_hex)==len(colours), f'{key}: 2–8 unique reviewed colours'
            assert isinstance(card['tags'],list) and all(isinstance(t,str) and t.strip() for t in card['tags']), f'{key}: invalid tags'
            tags = list(dict.fromkeys([card['domain']]+card['tags']))
            label = card.get('name') or card['title'].split(':')[0]
            if len(label)>68: label=label[:65]+'…'
            full = f'assets/batch500/{key}.webp'
            thumb = f'assets/batch500/{key}-thumb.webp'
            for rel, size, quality in ((full,(2200,2200),94),(thumb,(820,500),88)):
                out = temp / Path(rel).name
                assert not (dist/rel).exists(), f'{key}: refusing to replace existing image'
                ImageOps.contain(image,size).save(out,'WEBP',quality=quality,method=6)
                staged.append((out,dist/rel))
            derivation = card['modifications']+'；网页版本以白底合成透明区（如有）、等比缩放并转存 WebP。'
            row = dict(id=key,order=len(rows)+len(added_rows),name=label,title=card['title'],
                       domain=card['domain'],tags=tags,mood=' × '.join(list(dict.fromkeys(colour_name(c) for c in colours))[:3]),
                       colors=colours,analysis=card['observation'],
                       usage=card.get('usage') or '可参考模块填色与强调色分工；保留深色文字和连线以维持可读性。',
                       image=full,thumbnail=thumb,figure=card['figure'],venue='NeurIPS 2026',paper=paper,
                       sourceLabel='arXiv · 原论文',noteUrl=note,
                       provenance=f"{card['attribution']} · {card['figure']} · CC BY 4.0",
                       imageSource=card['imageUrl'],license=LICENSE,
                       note=derivation+'色卡等宽，不表示面积比例。',reviewStatus='visually_reviewed')
            extraction = dict(id=key,figure=row['figure'],source_url=row['imageSource'],
                              sourceType='versioned_author_arxiv_figure',sourceTitle=row['title'],paper=paper,
                              imageSHA256=review_sha,originalSourceSHA256=source_sha,sourceRasterSHA256=sha(raster),
                              sourceRasterDimensions=list(source_raster.size),crop=list(bbox),coordinateBasis=card['coordinateBasis'],
                              figureAnchor=card.get('figureAnchor'),
                              colors=colours,colorEvidence=samples,
                              excluded=card.get('excluded'),license='CC BY 4.0',licenseUrl=LICENSE,
                              licenseEvidence=card['rightsSource'],attribution=card['attribution'],
                              modifications=derivation)
            review = dict(id=key,verdict='accepted',reviewer=card['reviewer'],reason=card['reviewReason'],
                          reviewedImageSHA256=review_sha,reviewedPalette=colours,
                          paletteObservation=card['observation'],reviewedAt=card['reviewedAt'])
            added_rows.append(row)
            added_audits.append(dict(id=key,extraction=extraction,review=review,noteUrl=note,sourceTitle=row['title'],
                                     publishedImage=full,publishedThumbnail=thumb,
                                     publishedImageSHA256=sha(staged[-2][0]),publishedThumbnailSHA256=sha(staged[-1][0])))
        assert sha(palette_file)==baseline_sha, 'Catalogue changed while preparing derivatives'
        total = len(rows)+BATCH
        merged = rows+added_rows
        updated = dict(collection,target=total,published=total,domains=len({r['domain'] for r in merged}),
                       colours=sum(len(r['colors']) for r in merged),reviewed=True,
                       updatedAt=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                       previousPublished=len(rows),added=BATCH,newIds=[r['id'] for r in added_rows])
        for src,dst in staged:
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(src.read_bytes())
        atomic_json(audit_file, audits+added_audits)
        atomic_json(palette_file, merged)
        atomic_json(collection_file, updated)
    validate(total)
    assert json_file(palette_file)[:len(rows)] == rows
    assert json_file(audit_file)[:len(audits)] == audits
    print(f'Release QA: {len(rows)} preserved + {BATCH} reviewed additions = {total}.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet',type=Path)
    parser.add_argument('--baseline-sha256',required=True)
    args = parser.parse_args()
    append(args.packet.resolve(),args.baseline_sha256)
