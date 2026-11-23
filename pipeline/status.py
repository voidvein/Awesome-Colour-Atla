"""A truthful snapshot: candidate acquisition is separate from approved publication."""
import hashlib,json
from collections import Counter
from pathlib import Path
from collect_batch import ROOT,WORK,RECORDS,atomic_json
from publish_dataset import title_key,paper_key

def status():
 seed=json.loads((ROOT/'research/seed-palettes.json').read_text(encoding='utf8'))
 titles={title_key(p['title']) for p in seed};papers={paper_key(p['paper']) for p in seed}
 valid=[];problems=[];review_states=Counter()
 for path in (WORK/'reviews').glob('*.json'):
  review=json.loads(path.read_text(encoding='utf8'));review_states[review['verdict']]+=1
  if review['verdict']!='accepted':continue
  r=json.loads((RECORDS/(review['id']+'.json')).read_text(encoding='utf8'));e=r['extraction']
  missing=[k for k in ['paper','sourceType','sourceTitle','figure','imageSHA256'] if not e.get(k)]
  if missing:
   problems.append(review['id']+': missing '+','.join(missing));continue
  if not 2<=len(e.get('colors',[]))<=8 or len(e.get('colorEvidence',[]))!=len(e['colors']):
   problems.append(review['id']+': incomplete colour evidence');continue
  if hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()!=review.get('reviewedImageSHA256') or review.get('reviewedPalette')!=e['colors']:
   problems.append(review['id']);continue
  t=title_key(e.get('sourceTitle') or r['title']);p=paper_key(e['paper'])
  if t in titles or p in papers:continue
  titles.add(t);papers.add(p);valid.append(r['id'])
 records=[json.loads(p.read_text(encoding='utf8')) for p in RECORDS.glob('*.json')]
 result={'target':500,'approvedUniqueIncludingSeed':len(seed)+len(valid),'approvedNewUnique':len(valid),'publishedInWorkspace':len(json.loads((ROOT/'dist/palettes.json').read_text(encoding='utf8'))),'metadataRecords':len(records),'recordStates':dict(Counter(r['status'] for r in records)),'reviewStates':dict(review_states),'approvalProblems':problems}
 atomic_json(WORK/'status.json',result);print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':status()
