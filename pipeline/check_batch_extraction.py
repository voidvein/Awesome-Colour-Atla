"""Regression evidence for real batch failures, retaining manual review status."""
import json
from extract_figures import ROOT, process_pdf, make_contact_sheet

cache=ROOT/'research/batch500/cache'
out=ROOT/'research/extraction-review/repaired'
expected={
 'cvpr26-8ea2ffc84c58':('Figure 3',4),
 'cvpr26-75c25d499e1c':(None,None),
 'cvpr26-c58926db1673':('Figure 3',5),
 'cvpr26-cc3d6f737359':('Figure 5',5),
 'cvpr26-39c79b6b46e1':('Figure 3',5),
}
report=[]
for paper_id,(figure,page) in expected.items():
 r=process_pdf(cache/f'{paper_id}.pdf',out,paper_id)
 assert r.get('figure')==figure and r.get('page')==page,(paper_id,r)
 if figure:
  assert r['status']=='needs_visual_review'
  assert r['crop'][2]-r['crop'][0]>500, 'real full-width examples must retain both columns'
  assert r['crop'][3]<r['captionRect'][1]
 else:
  assert r['status']=='no_architecture_candidate'
  assert not r.get('image')
 report.append(r)
(out/'repair-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
make_contact_sheet([r for r in report if r.get('image')],out/'contact.png',columns=2,thumb_size=(800,350))
print('PASS: 5 real PDF regressions. Dataset-only Charge rejected; real methods selected; cross-column figures preserved.')
print('Report:',out/'repair-results.json')
