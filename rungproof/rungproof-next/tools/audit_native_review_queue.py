"""Extract the documented native-review queue without claiming visual acceptance."""
import json,re
from pathlib import Path
source=Path('../docs/MULTI_ANGLE_SCENE_REVIEW.md')
raw=source.read_bytes()
try:text=raw.decode('utf-8')
except UnicodeDecodeError:text=raw.decode('cp1252')
rows=[]
# These scenes were modified after their last recorded native inspection.
latest_pending={'lab-2-21-tote-finishing','lab-3-01-guarded-pallet-transfer','lab-9-12-ev-charging-manager','tank-radar'}
for line in text.splitlines():
 if not re.match(r'^\| \d+ \|',line):continue
 cells=[c.strip() for c in line.split('|')[1:-1]]
 if len(cells)!=5:raise RuntimeError('Unexpected matrix row: '+line)
 index,scene,bounds,views,result=cells;scene=scene.strip('`')
 angles={name:bool(re.search(r'\b'+pattern+r'\b',views)) for name,pattern in [('FR','FR'),('FL','FL'),('RL','RL'),('RR','RR'),('Top','(?:Top|T)')]}
 explicit_failure=bool(re.search(r'\bFAIL\b',result,re.I))
 current_pending=scene in latest_pending
 rows.append(dict(index=int(index),sceneId=scene,recordedNativeViews=views,recordedAngles=angles,recordedResult=result,
  latestNativeReviewPending=current_pending,explicitFailureRecorded=explicit_failure,
  disposition='REPAIR_RECORDED_FAILURE' if explicit_failure else 'REVIEW_CHANGED_SCENE' if current_pending else 'RECONCILE_CURRENT_EVIDENCE',
  acceptance='NOT_CERTIFIED_BY_THIS_INVENTORY'))
assert len(rows)==77 and len({r['sceneId'] for r in rows})==77
report={'source':'MULTI_ANGLE_SCENE_REVIEW.md','scope':'Inventory of documented observations only; views may predate current geometry. Runtime, collision and visual acceptance remain separate.',
 'sceneCount':len(rows),'allFiveAnglesRecordedCount':sum(all(r['recordedAngles'].values()) for r in rows),
 'explicitFailureCount':sum(r['explicitFailureRecorded'] for r in rows),'knownChangedSceneCount':sum(r['latestNativeReviewPending'] for r in rows),'scenes':rows}
Path('../docs/SCENE_NATIVE_REVIEW_QUEUE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='scenes'},indent=2))
for r in rows:
 if r['explicitFailureRecorded'] or r['latestNativeReviewPending']:print(r['sceneId']+' '+r['disposition'])
