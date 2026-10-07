"""Extract the documented native-review queue without claiming visual acceptance."""
import json,re
from pathlib import Path
source=Path('../docs/MULTI_ANGLE_SCENE_REVIEW.md')
raw=source.read_bytes()
try:text=raw.decode('utf-8')
except UnicodeDecodeError:text=raw.decode('cp1252')
rows=[]
# These layouts still lack a fresh native home-pose inspection.
# Completed home inspection does not certify controller motion or acceptance.
latest_pending=set()
# Evidence triage of the literal FAIL/open rows in the source matrix. A
# verification limitation must not be presented as a confirmed collision or
# missing implementation. Preserve the original result text below for review.
implementation_gaps={
 'lab-10-05-motor-struct-data': 'STRUCT record and power/temperature data',
 'lab-10-06-ten-motor-array-startup': 'Typed array-value interface',
 'lab-11-06-wastewater-collection': 'Fluid and analog process model',
 'lab-11-11-service-elevator': 'Hoist/access depiction and modeled door travel',
 'lab-11-12-mobile-traffic-lights': 'Timed reference cycle, vehicle motion and clear feedback',
}
verification_gaps={
 'lab-10-03-vision-package-sorter': 'Continuous clearance between sampled poses',
 'lab-2-14-sump-pump': 'Continuous float visualization and physical/process limits',
 'lab-2-17-pallet-robot': 'Continuous clearance between sampled poses',
 'lab-2-18-pallet-pickup': 'Last-active native scan and intermediate-pose coverage',
 'tank-high-low': 'Exact switch frames and current-source operator checks',
 'tank-level': 'Native threshold-cycle and operator coverage',
}
for line in text.splitlines():
 if not re.match(r'^\| \d+ \|',line):continue
 cells=[c.strip() for c in line.split('|')[1:-1]]
 if len(cells)!=5:raise RuntimeError('Unexpected matrix row: '+line)
 index,scene,bounds,views,result=cells;scene=scene.strip('`')
 angles={name:bool(re.search(r'\b'+pattern+r'\b',views)) for name,pattern in [('FR','FR'),('FL','FL'),('RL','RL'),('RR','RR'),('Top','(?:Top|T)')]}
 explicit_failure=bool(re.search(r'\bFAIL\b',result,re.I))
 current_pending=scene in latest_pending
 # Unknown future FAIL records need triage, not an inferred repair order.
 gap_kind=('IMPLEMENTATION_GAP' if scene in implementation_gaps else
           'VERIFICATION_GAP' if scene in verification_gaps else
           'UNTRIAGED_RECORD' if explicit_failure else 'NOT_TRIAGED')
 disposition=('IMPLEMENT_RECORDED_GAP' if gap_kind=='IMPLEMENTATION_GAP' else
              'VERIFY_RECORDED_GAP' if gap_kind=='VERIFICATION_GAP' else
              'TRIAGE_RECORDED_FAILURE' if explicit_failure else
              'REVIEW_CHANGED_SCENE' if current_pending else 'RECONCILE_CURRENT_EVIDENCE')
 rows.append(dict(index=int(index),sceneId=scene,recordedNativeViews=views,recordedAngles=angles,recordedResult=result,
  latestNativeReviewPending=current_pending,explicitFailureRecorded=explicit_failure,
  gapKind=gap_kind,gapSummary=implementation_gaps.get(scene,verification_gaps.get(scene)),
  disposition=disposition,
  acceptance='NOT_CERTIFIED_BY_THIS_INVENTORY'))
assert len(rows)==77 and len({r['sceneId'] for r in rows})==77
report={'source':'MULTI_ANGLE_SCENE_REVIEW.md','scope':'Inventory of documented observations only; views may predate current geometry. Pending flags refer to changed home layouts only. Runtime, collision and visual acceptance remain separate.',
 'sceneCount':len(rows),'allFiveAnglesRecordedCount':sum(all(r['recordedAngles'].values()) for r in rows),
 'explicitFailureCount':sum(r['explicitFailureRecorded'] for r in rows),
 'triagedImplementationGapCount':sum(r['gapKind']=='IMPLEMENTATION_GAP' for r in rows),
 'triagedVerificationGapCount':sum(r['gapKind']=='VERIFICATION_GAP' for r in rows),
 'knownChangedSceneCount':sum(r['latestNativeReviewPending'] for r in rows),'scenes':rows}
Path('../docs/SCENE_NATIVE_REVIEW_QUEUE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='scenes'},indent=2))
for r in rows:
 if r['explicitFailureRecorded'] or r['latestNativeReviewPending']:print(r['sceneId']+' '+r['disposition'])
