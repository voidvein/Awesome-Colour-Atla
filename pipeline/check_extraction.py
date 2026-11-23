"""Behaviour checks using a real original PDF and exact source-pixel evidence."""
from pathlib import Path
from PIL import Image, ImageDraw
from extract_figures import process_pdf, process_html, extract_palette, score_caption, make_contact_sheet, ROOT

out=ROOT/'research/extraction-review'
out.mkdir(parents=True,exist_ok=True)
record=process_pdf(ROOT/'research/3d_reconstruction.pdf',out,'arca-gs')
assert record['figure']=='Figure 2' and record['page']==3
assert record['status']=='needs_visual_review'
assert record['crop'][3]<record['captionRect'][1]
assert 2<=len(record['colors'])<=8
im=Image.open(record['image']).convert('RGB')
for evidence in record['colorEvidence']:
    assert im.getpixel(tuple(evidence['sampleXY']))==tuple(evidence['rgb'])
html='''<figure id="fig2"><img src="diagram.png"><figcaption>Figure 2: Overview of our proposed architecture.</figcaption></figure>
<figure><img src="chart.png"><figcaption>Figure 3: Performance comparison and ablation results.</figcaption></figure>'''
h=process_html(html,base_url='https://arxiv.org/html/test/')
assert h['candidates'][0]['figure']=='Figure 2'
assert h['candidates'][0]['image_url']=='https://arxiv.org/html/test/diagram.png'
assert h['candidates'][1]['score']<0
make_contact_sheet([record],out/'contact.png',columns=1)
# Bright pastel fill with a full 255 channel must remain eligible.
test=Image.new('RGB',(240,40),'white');draw=ImageDraw.Draw(test)
testcolors=['#FFEFBE','#FADDCB','#BDD7ED','#A9D18E','#7D88CD','#172B51']
for i,c in enumerate(testcolors):draw.rectangle((i*40,0,i*40+39,39),fill=c)
test.save(out/'flat-test.png')
p=extract_palette(out/'flat-test.png',6)
assert set(testcolors)==set(p['colors']),p
p2=extract_palette(out/'flat-test.png',6,exclude_regions=[[0,0,40,40]])
assert '#FFEFBE' not in p2['colors']
print('PASS: real PDF Figure 2/page 3 crop; exact source RGB pixels; HTML architecture vs result discrimination; bright pastels; excluded regions; contact sheet.')
print('PDF candidate:',record['figure'],'page',record['page'],'crop',record['crop'],'colours',record['colors'])
