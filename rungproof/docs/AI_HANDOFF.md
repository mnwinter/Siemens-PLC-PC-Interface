# RungProof / PLC Visual Simulator AI handoff

This document is the versioned project-memory handoff for a new AI agent or
developer starting from a fresh branch. It records the durable context that
would otherwise be trapped in a local Codex session. It intentionally excludes
machine-local Codex databases, credentials, screenshots from private chats, and
temporary runtime state.

Headless dialog repair (2026-10-04): unsaved ladder PopupCentered was
spawning at (-293,-128) on the headless display. Headless now uses explicit
(0,0,650,320) Popup; normal Windows keeps PopupCentered and the same guard
lifecycle. Build zero warnings/errors; headless and rendered app-shell checks
pass with zero ERROR lines, including all-scene unsaved detection, Cancel,
failed-save blocking, wait-for-each-save, successful saves and Discard. The
expected missing-workspace warning remains. Controller suite 142 pass/0 fail,
no real transport/connection. Evidence: headless-dialog-{build,shell,
rendered-shell,controller}.log; prior base-conveyor-shell.log has four errors.
Rendered verifier is automated UI evidence; its transient dialogs were not
individually visually inspected. Goal active; catalog defects remain open.
Earlier checkpoint:

Base conveyor carton repair (2026-10-04): scene 73/74 cartons move from
(-3.3,0.99,0) to (-3.0,0.9,0), eliminating a measured 90 mm carrying-surface
gap and 219 mm loading-end overhang. Ten checks cover initial contact/full
footprint, travel through first photoeye detection, optical envelope, stopped
clock hold and Reset; eight fail before, all pass after. Total 165 geometry/
reference checks pass; build zero warnings/errors, 142 controller tests pass
without real transport, app shell passes with its four known headless position
errors/workspace warning. Each rebuilt normal scene inspected FR/FL/RL/RR/T
plus carton Top/FL close. Repaired Demo 3 normal Run/rail Start advances carton
to photoeye, output stops; FR close shows support, Stop holds, Reset restores
load end/contact and clears feedback/output/scan. Pusher transfer/receiver,
head/photoeye clearance, full discharge and mid-travel native Stop remain open.
No controller or native pusher cycle was accepted. Evidence: base-conveyor-
{red-build,red-geometry,build,geometry,controller,shell,native-final}.log.
Goal active: finish the recorded identity, interference and workflow repairs.
Earlier checkpoint:

Luggage/Pallet carton repair (2026-10-04): scene 64 and 71 box_1 origins
Y=0 -> 0.9 m match the measured carrying belt. Four delivered-mesh support/
solid-clearance checks fail before and pass after. Fresh normal native instances
of each inspected FR/FL/RL/RR/T and carton Top/FL close confirm contact and
footprint. This does not repair luggage identities/weight contract or pallet
sensor/post/display assembly. Build zero warnings/errors; all 155 geometry/
reference checks, both initial-state contracts and 142 controller checks pass;
no real PLC transport/connection. App shell passes 77 scenes/294 assets but
retains four known headless position errors and missing-workspace warning.
Evidence: luggage-pallet-{red-build,red-geometry,build,geometry,luggage-contract,
count-contract,controller,shell}.log, luggage-carton-native-final.log,
pallet-count-carton-native-final.log. Initial 77-scene coverage includes failures;
all open repairs and unverified motion remain. Goal active.
Earlier checkpoint:

Catalog completion checkpoint (2026-10-04): all 77 scenes now have initial
native FR/FL/RL/RR/T inspections, including failed scenes. No pending initial
static rows; repairs and motion/controller acceptance remain open. Scenes
66-72 expose wrong numeric/function/display/EV props and missing numeric
contracts. Pallet Counting's carton/type-sensor/post layout still fails;
normal authored Demo 4 five detection rising edges, permissive removal,
Stop/Run retention and Reset were observed. Conveyor Stop's authored Demo 3
Start advances carton to photoeye and stops, with Stop hold and Reset checked;
its carton support and full clearance remain open. Conveyor Pusher lacks
receiver support and needs motion clearance. Tanks show disconnected piping,
external probe mounting and opaque vessels; radar instrument/cone needs
focused inspection. Radar declared Run/inlet blocked unloaded; normal Run
opens empty editor. Evidence: bag-carton-native-final.log, scene JSON,
AuthoredDemoLadderPrograms.cs. No production changes or additional automated
acceptance since the 151-check carton checkpoint. Goal active: continue repairs.

Earlier checkpoint:
Latest crossing/process checkpoint (2026-10-04): coverage 65/77 five-view native
static inspections; 12 pending including failures. Scenes 60-65 FR/FL/RL/RR/T
screenshots inspected. Crossing is a vertical wall/amber heads with green stop
binding; drawbridge scissor table/guard/shutter, outputs only lamps. Bag Indexing
box_1 Y=0 -> 0.9 repairs buried carton: both delivered-mesh checks red before,
green after, native rebuilt five wide/top/FR close contact inspected. All 151
geometry/reference checks and initial-state contract pass; clean build. Coating
CNC occupies belt; luggage carton still buried with shutter display/no measured
weight contract; dryer overlapping shutters/no remaining-time contract. No
loaded-ladder/actions/Run/Stop/Reset or complete machine motion accepted for these
six. Evidence: catalog-51-native.log and bag-carton-{red-build,red-geometry,build,
geometry,contract,native-final}.log. Continue at 66 then all open repairs.
Goal active. MULTI_ANGLE_SCENE_REVIEW.md records exact bounded acceptance.

Earlier checkpoint:

Latest timer/packaging checkpoint (2026-10-04): coverage 59/77 five-view native
static inspections; 18 pending including failures. All 51-59 FR/FL/RL/RR/T
screenshots inspected. Cookie product is meat tray below indexing belt (close),
barrel load motor starter (close), cable reel/dancer are shutters. Machine
outputs only lamps. Timer panels clear spacing, but persistent pulse/tick,
pushbutton/selector identities and missing tower-level outputs remain open.
Demo 2 normal native Run, rail request -> initially off then green, actual 3D
button -> false request/output, reapplied request -> green, Stop -> off with
request true, Reset -> false points/stopped scan zero. Authored preset 2 s;
native screenshots prove before/after, not exact elapsed timing. Other eight
scenes had no loaded controller/actions tested. Evidence: catalog-51-native.log,
scene JSON and AuthoredDemoLadderPrograms.cs. No production changes since
carton repair. Continue at 60 and remaining catalog, then open repairs.
Goal active. See MULTI_ANGLE_SCENE_REVIEW.md for bounded acceptance.

Earlier checkpoint:

Latest catalog/carton checkpoint (2026-10-04): coverage 50/77 native five-view
static inspections; 27 pending including failures. Scenes 43-50 inspected;
clear counter/pattern panels do not prove actual counting/press workflows.
Four-color lesson has three tiers/green-only bindings. Garage vehicle is a
motor starter (native close); shutter/barrier motion bindings absent. Package
and chain-lift outputs only beacons; chain-lift conveyor/tables overlap.
Guarded Transfer (40) and Package Grouping (49) box_1 origins move from Y=0 to
0.9 m measured belt top. Rebuilt native normal-shell instances each inspected
in FR/FL/RL/RR/T plus carton top/FR close. Four new support/clearance checks fail
before and pass after; all 149 geometry/reference checks and both initial-state
contracts pass, build zero warnings/errors. No controller/motion acceptance
added. Logs: transfer-carton-{red-build,red-geometry,build,geometry,guard-contract,
group-contract,guard-native,group-native}.log. Baseline scenes 43-50 in
press-count-fixed-native.log. Continue with scene 51 and all remaining scenes,
then open placement, identity, output-binding and workflow repairs. Goal active.

Earlier checkpoint:

Latest press-count checkpoint (2026-10-04): coverage 42/77 native five-view
inspections, 35 pending including failures. Demo 1 aliases scene 42, not a
separate catalog scene. Native baseline three action clicks left input true and
lamp false because the scene action was toggle. Action ID/binding retained for
compatibility; type now pulse, label Pulse count button and plate PULSE. Guide
states starter preset three and Stop-retain/Reset-clear semantics. New
Main.PressCountWorkflowReview.cs integrates actual scene action, authored
ladder, mapper, fixed scan session and projection; four checks failed before
repair, all five pass after. Total 145 geometry/reference checks, 142 controller
tests and initial-state contract pass, build zero warnings/errors. No transport.
Fresh native Run, two rail pulses off, third 3D press green/released input,
Stop off, Run green from retained count, Reset false/scan zero and FR close
plate observed. Earlier baseline has five wide views; geometry unchanged.
Revised startup guidance readable in native window. Evidence: catalog-42-native.log,
press-count-fixed-native.log and press-count-{red-build,red-geometry,build,
geometry,controller,contract}.log. Inspection-toggle-{build,contract,shell}.log
also pass with shell's four known headless position errors/workspace warning.
Continue at scene 43, then all remaining scenes and open repairs. Goal active.

Earlier checkpoint:

Latest native catalog/editor checkpoint (2026-10-04): coverage 41/77 five-view
inspections, 36 pending including failures. Scene 38 robot behind CNC closed
back, transfer/reach unverified. Scene 39 TOGGLE plate repaired and freshly
inspected close. Real native editor test: added one NO toggle_button_pressed
contact and SET inspection_light_on coil, Online > Verify + load offline, Return
to scene, Run, pulse -> beacon lit; Stop -> dark; Reset -> all false, scan zero.
Temporary draft discarded via unsaved prompt; this is not the toggle lesson's
odd/even logic. Stopped pulses queue until accepted scan, not a proven stuck-input
bug. Startup guidance now explains blank exercises and verify/load prerequisite.
Scene 40 five views + carton top/FR close: buried carton; sensors/curtain/gate
outside conveyor route; native guard toggle/Reset checked. Scene 41 five views:
arm occupies CNC, wall is not a perimeter; persistent reset_complete toggle
confirmed and Reset checked; only beacon output bindings, no robot-motion
binding. Full protective/restart/transfer behavior unverified. Local evidence:
catalog-34-native.log (38/39/editor), catalog-39-final-native.log (label/40/41).
Continue at scene 42, then remaining catalog and open repairs. No live PLC.
Goal active. Exact observations in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Latest service-door/catalog checkpoint (2026-10-04): coverage 37/77 native
five-view inspections, 40 pending including failures. Scene 33 door button/guide
and beacon/curtain overlaps repaired; controls 1 m forward, signal stands beyond
right equipment envelope, OPEN/STOP/CLOSE plates inspected close. Signals label
raw NC truth and description removes unsupported cable monitoring. Native
reference reproduced stale position and reversal opening jump; opt-in fromCurrent
captures actual adapter input pose, sequencePositionOnly removes autonomous creep,
and reference-only positionFeedback validates SIM REAL/PC BOOL owners and skips
controller/external clocks. Native fresh stopped 60% pose, Close to 68%, resumed
100% closed, unheld 0% open, open five views and Reset observed. Eleven added
checks bring total to 140; build zero warnings/errors, two door contracts, 142
controller tests, 19 motion checks, rendered controls and shell pass. Geometry
stderr clean; shell still four headless position errors/missing-workspace warning.
Compressed slat animation, physical limits/cable faults and loaded-controller
operation unaccepted. Local .tools evidence: service-door-native.log,
service-door-plant-native.log (repro), service-door-fixed-plant-native.log and
service-door-{build,geometry,contract,controller,motion,controls,shell}.log.
Scenes 32 and 34-36 also have five native views and recorded close inspections:
pallet/sensor support needs measurement; bottle label overlaps; finishing columns
occupy belt corridor; shared plate offset below two separate drill coupons, both
drill adapters rotation only. Start/Jog blocks without controller. catalog-32-native.log
and catalog-34-native.log contain navigation evidence. Goal active; continue at
scene 38 (37 was inspected earlier), then remaining catalog and all open failures.
No live PLC transport exercised. Detailed findings in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Latest fixture/feed checkpoint (2026-10-04): coverage 32/77 native five-view
inspections, 45 pending including failures. Opt-in fixtureDrill moves the actual
delivered yellow coupon into the workpiece root at its vise center, removing the
buried second fixture. Actual original tip Y=1.610 vs stock Y=1.585..1.695;
235 mm raised home gives 150 mm clearance, 245 mm feed ends at Y=1.600. New
SpindleFeed adapter separates BOOL rotation from declared position feed and
keeps quill/chuck/bit together, head/guard/table/vise fixed. Stop's honest label
now says Stop spindle and hold; guide states no retraction. Start additionally
requires drill_at_top to prevent false top feedback on a stopped bottom pose.
Normal native repaired FR/FL/RL/RR/T, stock FR close and both rendered 3D hand
buttons verified; rendered cycle button blocks no controller and output stays
false. Standalone held home/downstroke/bottom four close side views, Stop across
two stepped seconds, blocked restart, visible Reset and intermediate retract
inspected; resumed real-time and wholly unheld reference cycles reach top/complete.
Stock top focus is head-occluded. No material removal/safety-rated two-hand/guard
feedback model established; hints explain latched demonstration inputs. Normal
controller lesson remains unaccepted. Build zero warnings/errors; 129 geometry/
reference checks, four drill contracts, 142 controller tests, 19 motion checks,
rendered controls and shell pass. Shell has four existing headless position
errors and missing-workspace warning. Evidence rungproof-next/.tools/drill-datum.log,
drill-feed-native.log, drill-feed-plant-native.log and drill-feed-*.log.
Both owned reviewers exit 0, user Demo 1 preserved. Scene 31 Twin-Container
Pallet Cell now has five native views and receiver top/FR close: FAIL, receiver
backstop crosses conveyor end and pallet appears above belt. 23 bounds candidates
include 13 conveyor/receiver, six conveyor/photoeye, four pallet/tote pairs;
contact datums, sensor attachment, robot transfer/reach and empty pallet travel
still open. Normal Run unloaded. Goal active. Next scene 32 Pallet Pickup, then
all 45 pending scenes and recorded failures; normal controller lessons, sump/fume/
coolant identity/service gaps and shared lift follow-ups remain outstanding.

Earlier checkpoint:

Latest drill checkpoint (2026-10-04): coverage 31/77 inspected, 46 pending,
including failures. Scene 30 has normal native FR/FL/RL/RR/T and workpiece
top/FR close inspection. FAIL: mapped drill press contains a yellow coupon
already; separate drill_workpiece maps to another clamped-plate fixture under
the table. Native held bottom feedback changes without axial spindle travel:
ContinuousRotation ignores SetPositionNormalized. Stop and retract has only
type=stop, retaining bottom=true/top=false after two stepped seconds. Normal
Run unloaded. Three faceLabel plates now LEFT HAND/RIGHT HAND/DRILL CYCLE,
all checked in native close views. QA action bar bottom anchor fixes overlap
with wrapped status/Run/Stop/Reset; popup opens upward and remains visible.
Uncovered RunDefault bypass: default sequence skipped Start requirements.
It now dispatches the unique matching declared Start action. Four negative
checks reproduce before-fix failures and all pass repaired; valid completion
and unconditional sump start remain available. Native final Run blocked with
both requests false and left only; both true start completes in real time,
Reset restores inputs. These QA checks do not accept normal controller lesson
execution, feed geometry or safety-rated two-hand operation. One 3D button
click in QA did not change its point; normal rendered-button interaction is
still unverified. Build 0 warnings/errors; 117 geometry/reference checks,
two drill contracts, 19 motion checks, 142 controller tests, rendered controls
and shell pass (four existing headless position errors). Evidence under
rungproof-next/.tools: safe-drill-native.log, safe-drill-plant-native.log,
safe-drill-label-native.log, safe-drill-layout-native.log,
drill-permissive-before.log, drill-permissive-final-native.log and
drill-permissive-*.log. All isolated reviewers exit 0; user Demo 1 stays open.
Goal active. Next: measure/reconcile the drill's actual coupon/fixture and
spindle feed/stop/guard behavior, then scene 31 Twin-Container Pallet Cell and
all 46 pending scenes. Sump vessel/probes/level motion, fume identity gaps,
coolant service piping, shared lift follow-ups and earlier failures remain open.

Latest sump piping checkpoint (2026-10-04): coverage remains 30/77 inspected,
47 pending including failures. Opt-in installation=sumpPiping uses actual mesh
datums before tree entry to connect tank/pump, rotate/align valve/spool and
ground five pipe shoes/posts without modifying other scene assets. Suction
uses two 45-degree bends (350 mm centerline radius, 180 mm tube radius),
discharge a 350 mm elbow; local curvature guard catches undersized bends.
Final normal Windows five wide views plus top/FL/RL/FR pump-focused close
views were inspected. Normal Run opens NO CONTROLLER LOADED. Six new
actual-mesh checks all fail with original scene JSON and pass repaired.
Build 0 warnings/errors; 111 geometry checks, one sump reference contract,
19 motion checks, 142 controller tests, rendered controls and shell pass.
Shell retains four existing headless position errors. Evidence under
rungproof-next/.tools: sump-piping-before.log, sump-piping-geometry.log,
sump-piping-final-native.log and sump-piping-*.log. Reviewer exits 0 and
user Demo 1 stays open. Sump still FAIL: closed vessel rather than established
sump, named floats are tuning-fork assets, low probe Y=-0.175 below floor,
process fittings/threshold alignment and full native level motion unverified.
Annular visible connectors do not prove internal flow or hydraulic design.
Goal active. Next: finish sump vessel/sensor/motion review and scene 30 Safe
Drill, then all 47 pending scenes and previously recorded open failures.

Latest fume speed/Stop checkpoint (2026-10-04): coverage remains 30/77 inspected,
47 pending, including failures. Numeric speedPercent binding scales the existing
720 rpm fan animation while keeping BOOL run separate and unbound asset defaults.
Six actual blade world transforms reproduce 35/65/zero failures before repair;
all ten new checks now pass. Hub is one valid pivot owning blades/shaft. Native
QA running 35% five angles, 65/100 speed indications and Off inspected. Stop
originally immediately reasserted run via reference rules; standalone boolean
preview latch now holds declared initial outputs through selector changes until
Run/Reset. Fresh native Stop, retained-selector Run, Off retaining light and
Reset inspected. Selected-controller image remains authoritative; QA preview
does not accept normal controller lesson execution, rpm measurement or physical
blade/guard clearance. Hood/duct/inspection illumination still absent. Build has
0 warnings/errors, 105 geometry checks, five fume contracts, 19 motion checks,
142 controller tests, rendered controls and shell pass. Four existing headless
position errors remain. Evidence fume-speed-before.log, fume-stop-before.log,
fume-speed-native.log, fume-speed-stop-native.log and fume-speed-*.log under
rungproof-next/.tools. Both isolated previews exit 0; user Demo 1 remains open.
Goal active. Next: repair measured Sump ports/probe mounts/routing/support,
then scene 30 and remaining 47 inspections. Earlier scene failures, shared lift
native follow-ups and coolant service piping still require work.

Historical sump/fume checkpoint (2026-10-04): coverage 30/77 inspected, 47 pending,
including failures. Scene 28 Sump has native five angles and close overhead/FL
discharge inspection. FAIL: disconnected pump, elevated pipe/valve/support
assembly interferes with ladder/cage, low tuning-fork probe at Y=-0.175 below
floor, actual process fittings/float identity unestablished. Its reference
pump-hysteresis contract passes but is not geometry or normal-run acceptance.
Scene 29 Fume has five native views with clear spacing. LIGHT REQUEST replaces
the wrong START plate and fresh native FR/FL close views verify it. Native
selector pointer/input follows 0-1-2-3-0; PC light request toggles while unloaded
PLC outputs remain false. Five expanded reference contract cases pass for four
speeds, one indication, light independence and return to off. No runtime rule
rewrite: boolean-panel outputs already reset each scan. Open: fan speed percent
unbound to renderer, beacon used as inspection light, hood/duct absent, normal
Run unloaded editor. All 95 geometry checks, 142 controller tests, shell and a
zero-warning/error build pass; shell retains four headless position errors.
Logs sump-native.log, fume-label-native.log, fume-contract.log and
sump-fume-*.log under rungproof-next/.tools. Both isolated reviewers exit 0;
user Demo 1 remains open. Goal active. Next: repair measured sump ports/probe
mounts/routing/support and fume speed/identity gaps, then scene 30 Safe Drill
and remaining 47 inspections; coolant service pipe, shared lift follow-ups
and previously recorded failures remain required. Do not merely shift parts
to hide intersections without establishing a connected supported installation.

Historical coolant repair (2026-10-04): coverage stays 28/77, 49 pending, including
failures. Opt-in SceneComposer.CoolantJug adapts the standalone imported filler
to a grounded portal outside the conveyor, opens only this jug's neck/removes
its cap, supports its actual bottom on the belt and keeps the full exit footprint
on it. Tip and valve-driven stream follow the moving nozzle. Ten added actual
geometry checks reproduce failures with original scene config; all 95 now pass.
Native normal catalog five initial angles, QA five held filling angles and close
FL open-mouth/stream inspected. Held steps advance runtime sequence bindings;
independent equipment physics stays held. Resume reaches complete discharge;
real-time Run indexing/exit and Reset inspected. Stop was endpoint-only.
Build has zero warnings/errors. One fill contract case, 19 plant motion checks,
142 controller tests, rendered overlay/control checks and shell pass; shell has
four existing headless window-position errors. Attachment ownership is cleared
before reparenting, removing new warnings. AABB candidates now 13, solid OBB
checks exclude cables/optical beam; no physical clearance/strength claim.
Open: external metering skid service pipe is absent, normal catalog Run still
opens EDIT INVALID / NO CONTROLLER LOADED, real probe/fluid physics unverified.
Logs coolant-install-*-final.log, coolant-install-native-held.log and
coolant-install-shell-native.log under rungproof-next/.tools. Both isolated
reviewers exited cleanly; user Demo 1 window preserved. Goal active. Next: finish
coolant service integration/workflow findings, shared lift-scene follow-up, scene
28 Sump Pump and remaining 49 inspections plus recorded failure repairs.

Historical pre-repair inspection (2026-10-04): coverage 28/77, 49 pending, including failures.
Scene 27 Coolant Jug has native FR/FL/RL/RR/T and close overhead/FL fill-unit
inspection. FAIL/open: red cap still on jug and fixed fill solids in its indexing
lane. Source uses the jerry-can and standalone volumetric tote filling assets.
Measure actual imported cap/nozzle, belt/support and sensor bounds before
repairing the integration. The 53 AABB candidates are screening evidence only.
Normal Run opens blank ladder editor with EDIT INVALID / NO CONTROLLER LOADED;
no filling sequence, high-probe, endpoint or moving-clearance acceptance.
Evidence coolant-jug-native.log in rungproof-next/.tools and current native
screenshot observations. Isolated window closed, user Demo 1 preserved.
Goal active. Next: repair/verify Coolant Jug installation and full motion, shared
lift-scene follow-up, then scene 28 Sump Pump and the remaining 49 inspections
plus recorded failure repairs. Do not substitute a shifted assembly without a
usable fill path, floor/mount support and full jug travel clearance.

Earlier hydraulic follow-up (2026-10-04): the fixed rod/clevis failure is repaired.
EquipmentMotionController binds the delivered lower-front arm, base/tip pins,
barrel, rod and clevis/lug siblings. The clevis/pin/lug follow the driven arm,
the fixed-length barrel pivots at its base, and only the rod's longitudinal mesh
axis extends to the moving tip. Missing nodes/mixed parents warn and skip this
attachment motion. Four new actual-mesh/Stop/Reset checks reproduce two failures
before repair; all 85 geometry checks, two lift contract cases, 19 plant-motion
checks and a zero-warning/error build pass. Native five angles, closer lift view,
FL/RR raising/lowering and endpoints, FR raised attachment and Reset inspected.
Stop was endpoint-only; deterministic check covers mid-cycle hold. Logs:
hydraulic-before.log, hydraulic-final.log, hydraulic-final-build.log,
hydraulic-contract.log, hydraulic-plant-motion.log, hydraulic-native.log under
rungproof-next/.tools. Current asset has exposed arms; stale bellows recognition
is historical and does not prove current guarding/independent approval. Normal
Run still needs a lesson controller. Coverage unchanged: 27/77, 50 pending.
Shared asset motion/framing needs native follow-up in Gallery, Service Elevator,
Chain Drive Lift and Drawbridge. User Demo 1 preserved; isolated preview closed.
Goal active. Next: shared lift-scene follow-up and scene 27 Coolant Jug, then the
remaining 50 static inspections plus previously recorded failure repairs.

Earlier follow-up (2026-10-04): native coverage is 27/77 inspected, 50 pending,
including failures. Assembly Lift has five native angles, close RAISE/LOWER
plates and FL/RR raise/lower movement/endpoints. Fixture support now matches
the actual deck at Y=1.64 (raised Y=3.84); 16 rollers/washers follow their pins.
Camera framing includes remaining lift travel, and explicit no-controller plant
QA exposes both declared actions. All 81 geometry checks pass (six new), as do
build, two scene-contract cases, 19 plant-motion checks, 142 controller tests
and shell verification. Shell still emits four headless window-position errors.
Rendered mouse-control checks pass with/without the review overlay; the headless
invocation fails mouse-click checks. Native Stop was endpoint-only; mid-cycle
Stop is deterministic. Normal Run still opens a blank exercise. Full lift motion
remains FAIL/open: KIN_lift_rod stays authored while its driven arm moves; cylinder,
clevis and drive-lug attachment need review as a complete chain. The old asset
recognition describes bellows absent from the current master/source, so it is
historical evidence only. Do not infer current guarding or independent approval.
Shared motion/framing changes require native follow-up in Gallery, Service
Elevator, Chain Drive Lift and Drawbridge. User Demo 1 preserved; isolated
reviewers closed. Exact logs and limits in MULTI_ANGLE_SCENE_REVIEW.md.
Goal active. Next: repair/verify the hydraulic attachment and reconcile current
asset evidence, then scene 27 Coolant Jug and the remaining 50 static inspections,
plus previously recorded failures. Do not mark the full program accepted.

Earlier follow-up (2026-10-04): native coverage is 26/77 inspected, 51 pending,
including failures. Scenes 22, 24 and 25 have final five-view native inspections
and close plate/tote views. VOTE A / VOTE B / STOP labels repaired; actual 3D
PC inputs and Reset checked. All three ordinary Run attempts still open a blank
exercise with NO CONTROLLER LOADED. Inbound tote bottom contact, sensor/frame
clearance and full endpoint support are repaired with Y=0.8905, span=3.8,
clear endpoint X=3.4. Six new imported-mesh checks reproduce three failures
before repair; all 75 geometry checks now pass. Three contracts/six cases and
zero-warning/error build pass. Native preview movement/completion inspected
from FL/RR, finished footprint overhead, Reset and completed-endpoint Stop.
Native mid-cycle Stop was not captured; deterministic check verifies it.
Seven cable/frame AABB candidates remain; solid OBB checks pass. No optical
barcode, PLC sequence or dust-process acceptance. Isolated reviewers closed
cleanly; user Demo 1 preserved. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.
Goal active. Next: full scene 26 Assembly Lift review (only its initial view was
seen; fixture appears obscured under the platen and needs close/multi-angle
inspection), then remaining 51 static reviews and recorded failure repairs.

Earlier follow-up (2026-10-04): native coverage was 23/77 inspected, 54 pending,
including failures. Scenes 18-21 and 23 have final FR/FL/RL/RR/T inspections and
close plates/dial views. Five plates now use NORTH CALL / SOUTH CALL / ATTENTION /
RESET NO / TEST NC. Native PC input actions and Reset were checked. All five
normal Run attempts open the blank lesson editor with NO CONTROLLER LOADED;
no lesson output sequence acceptance is implied. Ready/Attention's toggle versus
spring-return description remains open.

Shared selector repair: actual imported face is X/Y and handle axis is Z, while
old runtime applied Y. The master has three marks despite its stale four-position
approval. Composed variants now show configured 2-4 detents with readable numbers
outside the rim and ticks resting on the plate. Z projection honors initialPosition
and Reset. Windows close checks cover Bay Light 0/1 and Maintenance 0-3/wrap/Reset.
Master GLB/Blend is unchanged; catalog entry moved to candidates, quality cleared,
stale recognition/review archived. Master re-authoring, approval/help reconciliation,
and native rechecks of Gallery/Fume Extractor/Pallet Pickup variants remain pending.
Final build zero warnings/errors and 69 geometry checks pass. Plant checks 19,
authored cases 71, controller tests 142, shell 77 scenes/294 assets and normal
rendered controls pass; behavior suites preceded the last tick/legend adjustment.
Evidence and exact boundaries are recorded in MULTI_ANGLE_SCENE_REVIEW.md and
the selector asset review. Isolated windows closed cleanly; user Demo 1 preserved.
At that checkpoint, next was scene 22 Inspection Vote, then remaining native reviews and
repairs of recorded failed packages/layouts/workflows. Do not mark all scenes done.

Earlier follow-up (2026-10-04): native coverage was 18/77 inspected, 59 pending,
including failures. Scenes 9-12 (Wastewater Collection, Multi-Conveyor Pallet
Route, Service Elevator, Mobile Traffic Lights) each have inspected FR/FL/RL/RR/T
views and a separately clicked normal Run. All four fail geometry/identity and
open an empty editor with NO CONTROLLER LOADED. See MULTI_ANGLE_SCENE_REVIEW.md
for concrete findings. Source confirms their fresh ladder drafts are intentionally
tag-only exercises; Run rejects empty networks. Missing reference controllers and
machine behavior remain open alongside the visual repairs, not a transport bug.

Workstation Call / Dual Confirmation / Service Marker now use four faceLabel
settings: MATERIAL CALL / OPERATOR OK / QUALITY OK / INHIBIT. Their final five
views and four close plate views were inspected. All three existing scene-contract
checks pass, but each normal Run still opens its empty exercise editor. This is
a JSON-only plate repair; prior build/49-geometry/19-plant results were not rerun.
Evidence under rungproof-next/.tools: catalog-scenes-9-12-native.log,
catalog-scenes-9-12-source.log, call-panel-native-final.log and the three
lab-2-0*-plate-contract.log files. Isolated review windows closed cleanly; user's
Demo 1 preserved. Goal remains active. Next: continue the remaining native
inspections and repair the recorded failed source packages/layouts/workflows.


Label-print repair and review-input follow-up (2026-10-04): four wrong
source packages are replaced by original static training props: food tray,
weigh deck/readout, supported desktop printer and label-preview display. The
unbound CNC placeholder was removed (11 equipment items). The staged carton
rests on the actual 0.9 m belt; the tray rests on the actual 0.9 m weigh deck.
Readout feet/masts and printer-paper contact are checked. Inherited recognition
and unrelated pictures are archived as invalid identity evidence; quality stays
candidate/unapproved, stale kinematics and unrelated industrial references are
removed. Five final native FR/FL/RL/RR/T views and focused support, printer,
display and three button-plate views were inspected. A tighter check caught a
5 mm printer-paper gap, failed before repair and passes after correction.

Native camera review then reproduced an input conflict: Wide/close triggered
the label-data-valid button behind the review bar instead of changing the camera.
The shared pick path now defers to the visible review bar and its open menu in
both raw and unhandled input. Rendered regression cases put the real Start mesh
behind the coverage label and an open menu: both failed before repair, both pass
afterward. Normal rendered 3D controls still pass. The exact native overhead
Wide click was repeated: camera changes, no scene-action event. This repair is
for the opt-in review overlay; it does not certify all other overlays.

Normal Run after the final repair still opens the empty editor with NO CONTROLLER
LOADED. No measured weight, label formatting, product transfer or actual printing
is implemented. Static layout repair does not pass the lesson workflow.
Fresh build: zero warnings/errors. All 49 geometry checks, 19 plant checks,
rendered controls (with and without review bar) and 71 authored cases pass.
The 77-scene inventory has 42 scenes with positive bounds counts; scene 4 is now
zero. Shared printer-package changes also alter Cookie Packaging's inventory
196 -> 146; that scene remains uninspected and unapproved. Global help validation
still has the previously recorded unrelated Count Display identity problem.
Evidence under rungproof-next/.tools: label-print-{props-build,build,import,
geometry,paper-red,inventory,scene-contracts,plant-regression,rendered-controls,
native-final,native-paper-final,native-overlay-final}.log and
review-overlay-{red,green}.log. Camera logs record navigation; screenshots were
inspected separately. Isolated native windows closed cleanly; the user's Demo 1
window was preserved. Coverage stays 14/77 inspected, 63 pending, with recorded
failures still open. Goal active.

Catalog scenes 4-8 follow-up (2026-10-04): Chicken Label Print, Vision Package
Sorter, Motor Operating-State Enum, Motor STRUCT Data and Ten-Motor Array Startup
have native FR/FL/RL/RR/T inspections. Each normal Run was clicked and opens an
empty editor with NO CONTROLLER LOADED. Wrong asset identities, unsupported or
intersecting equipment, missing four-lane routing, five rather than ten motors,
and absent weight/class/enum/STRUCT/array data are recorded in the visual ledger.
These are failed/open inspections, not acceptance. Motor-state plates/colors and
the missing motor_running shaft binding are repaired; final five views and all
three plate close-ups were inspected. The description/help explicitly disclose
the Boolean scope and missing enum/controller. Four added projection checks
reproduce plate/shaft failures before repair and pass afterward. Current build
has zero warnings/errors, all 42 geometry checks and 71 authored scene cases
pass. Prior 19 plant/rendered-controls evidence was not rerun for this JSON-only
scene repair and verifier addition. Evidence: catalog-scenes-4-8-native.log,
motor-state-{red-build,red-geometry,build,geometry,scene-contracts,native-final}.log
under rungproof-next/.tools. Coverage is 14/77 inspected, 63 pending; not 14 passed.
No native motor-state controller motion, real PLC execution or hardware behavior
was proven. Goal active; next work includes replacing verified wrong source
packages and repairing failed layouts/workflows, plus the remaining inspections.

## Product intent

Visual review reopened (2026-10-04): the user reported a pallet intersecting a
Demo 5 gantry post. The previous final checkpoint did not inspect every scene
from multiple angles. The active goal now requires catalog-wide native visual
coverage and repair; do not mark it complete after Demo 5. Use
`MULTI_ANGLE_SCENE_REVIEW.md` as the coverage ledger. Demo 5 placement and attached
gripper motion are corrected and inspected from five angles; seven focused
geometry checks pass. REAL scene initial JSON integer tokens now normalize at
the scene-project boundary; the previously mismatched catalog test reproduces
the production reader and all 142 tests pass. The complete 77-scene shell bounds
inventory now flags 43 scenes for interpretation. Powder-mixer placement and
tank shell sizing are repaired; an original static open chute replaces the
copied roller-shutter, and inherited door evidence is archived/removed from
current approval. Its five-view native reinspection verifies bounded static
clearance, not a powder-flow process. Scaled radar feedback and Reset projection
are corrected. Thirty-eight focused geometry, 19 plant, three family-selection and
71 authored scene-case checks pass (six scenes have no authored cases).
Parcel-sorter geometry is repaired: flat indexed tables, supported bridge and
takeaway paths, common deck elevations, raised header and configured optical
heights. Five static views plus final portal/table details were inspected. Native
declared plant preview Run/Stop/Reset and count=3 completion were observed from
front-left/rear-right; this is scripted geometry, not contact dynamics or sensor
validation. Normal shell Run opens the blank editor with NO CONTROLLER LOADED;
no supplied sorter reference controller exists. Do not count preview as operator
Run acceptance. Shared conveyor width/deck sizing now works; Demo 5 static
five-view regression passes, and the inspection conveyor is now reviewed; other conveyor scenes still need native review. Fourteen scenes inspected; 63 pending (including failed inspections).
Conveyor inspection now has supported cartons, grounded/photoeye stands clear
of frame/pull-cord hardware, and correctly projected beam feedback. Five native
views plus normal offline Run/Start/Stop/Reset and simulated E-stop/restart gating
were inspected. Feedback/recirculation remain simplified, not physical sensing.
Gallery probes are supported on illustrative stands; pipe/valve supports are
grounded and the transmitter clears the pipe. Five static native views and
instrument details were inspected. Gallery normal Run opens a blank editor with
NO CONTROLLER LOADED: its animation workflow remains open. Current evidence is
catalog-*.log under rungproof-next/.tools; 38 geometry, 19 plant, rendered scene
controls and 71 scene cases pass. Do not use headless GUI-input checks as evidence.
Workstation Call, Dual Confirmation and Service Marker have clear supports/spacing but incorrect
generic START plates. Global help validation fails at Count Display's inherited
door-axis metadata; investigate actual identity before refreshing that help.
Drive-alarm scene: three incorrectly inherited models replaced by original supported training props, stale reviews/references archived or removed, operator face labels corrected and five native views inspected. Close review caught and repaired a mast outside its base and hidden keypad buttons. It remains a Boolean exercise with static text legends; no fieldbus/string parsing or supplied controller. Normal Run was retested and still opens NO CONTROLLER LOADED. Seven added checks cover floor, separate equipment, mast support, identity, plates and symbolic alarm true/reset projection. Current evidence is drive-alarm-*.log; 38 focused geometry, 19 plant, rendered controls and 71 authored cases pass. Goal active; 68 native scene inspections remain.

Candidate AABB flags and scene loading are never visual acceptance. Restore tag
`codex/multi-angle-review-baseline-20261004` preserves `2c3de4b`. No hardware or
push. Continue the remaining ledger and asset/placement repairs.

Whole-program review final checkpoint (2026-10-04): Windows startup, all five
authored demos, controller ownership, editor/history/persistence, native
workspace authoring and malformed-file rejection were inspected and repaired.
Native tank fill/drain, analog feedback, Stop hold and Reset are verified.
Final suites pass: 142 controller, 16 connection, 129 canonical Python,
16 fake Python, 69 selected legacy Python and 28 Node tests; eight plant traces
match 83 snapshots. All 77 scenes load; 71 have passing declared cases and six
have none. Rendered app-shell/editor/split/controls/playback/plant checks pass.
The vendor manifest now matches the reviewed existing adapter patches and
normalizes Windows line endings while rejecting other changes. The legacy
renderer rejects 31 Godot-only accessory scenes explicitly.

Use the current matrix in `WHOLE_PROGRAM_REVIEW.md`; older checkpoint statuses
below are historical. Remaining capabilities include crash recovery, full lab
reference programs, actual FB instances/closed-loop pallet placement, automatic
reconnect/profile editing UI and a standalone installer. Full visual/runtime
acceptance of every scene and live PLC commissioning remain unverified. No
hardware connection or push was performed.

Editor completion checkpoint (2026-10-04): timer Reset records its tag creation
inside Undo; rejected interface edits retain history/monitoring. Native tag and
block forms now wrap at minimum/default window sizes with readable labels.
Unknown startup scene IDs recover to the default and report the reason.
Instruction Help now reveals its dock through the shared open path; native TON
documentation and scrolling inspected. Build and rendered ladder regression
pass. Whole-program review remains active; see the current review matrix.

Fresh-source startup checkpoint (2026-10-04): the launcher now restores NuGet
packages and imports assets before native startup. A tracked-source copy with
no generated caches reproduced NETSDK1004 before the fix, then built/imported
and ran the conveyor through normal Windows controls. Missing Godot/.NET/console
checks stop with exact paths. Portable tool setup remains required, and there
is no standalone export preset/installer. Review copy and logs are ignored at
`build/cold-start-review-20261004`; its `.tools` is a junction to the pinned
tools, so do not recursively delete through that junction. Goal remains active.

Current checkpoint (2026-10-04, watch review): controller suite 142/142;
plant regression 19 checks; rendered ladder interaction passes. Native Demo 5
first Run preserves preconfigured inputs, its four-pick layer stops commands,
and command-driven XYZ motion holds on Stop and resets. Demo 4 now calls its
counter FB and validation FC. Demo 5 has two FBs, two FCs, two populated DB
declaration views, timer/counter/comparison/math/parallel logic. It remains a
manual-feedback visualization; DB interfaces are declarations/shared tags.
Watch rows/pickers retain identity across scans; Remove/Clear update both
editor titles and toolbar Undo without dropping runtime monitoring. Native
Remove/Clear/Undo in TIA and Studio 5000 passed; sessions closed cleanly.
The Windows overlay mentioned in older checkpoints below is gone, and native
pusher/tank, authoring and watch workflows have since been inspected. See
`WHOLE_PROGRAM_REVIEW.md` for current matrix and evidence. Goal remains active;
fresh install/export and remaining native flows are still under review.

Latest local review checkpoint (2026-10-04): scene navigation retains each
ladder draft, saved baseline/path, and Undo/Redo; Demo 4 counts only valid
pallet-detection edges. Labs now open blank exercises with their own typed
scene bindings; empty Run reports missing logic and hidden scene rules cannot
compete with the selected controller. Fresh editor drawers fit at 1200x675 and
1600x900. Native demo 1-4 and Lab 2.1 author/run workflows were exercised. See
`WHOLE_PROGRAM_REVIEW.md` for regression and Windows evidence. Drafts remain
in memory; Save is required before exit. Rejected drafts now retain the loaded
controller's truthful state and show editor errors without stale monitoring.
New/Open and window close now guard unsaved current/cached drafts with Save,
Discard, or Cancel; failed writes cannot authorize continuation. Complete
lab/reference coverage, crash recovery,
remaining native workflows, broader external profile coverage, and longer sessions
still require work. The whole-program review is active; no live PLC acceptance
or complete product acceptance has been established.

The shutdown leak was traced to an unparented hidden Studio block selector.
Both vendor workbenches now own that control and its popup. Settled orphan,
rendered editor, and split tests exit without resource leak reports. Current
controller tests pass 140/140 and offline connection/process/playback tests 16/16.
External Connect no longer runs plant playback. Run requires the existing
reference readiness policy; Stop/Reset hold playback while exchange continues.
Readiness recovery requires a new Run. Full-app fake exchange and native
Run/Stop/Reset were verified without a PLC adapter or network. External source,
playback and cycle labels now report actual state; REAL display is bounded.

Latest plant checkpoint: Scene 2 lacked a conveyor/pusher physics implementation,
and tank motion depended on a local Run flag not set by ladder execution. The
ported canonical conveyor/pusher model now produces feedback and repeated
transfers from real offline ladder scans; tank fill/drain and analog/limit
feedback run from selected-controller playback. Stop holds the plant. Pure
model comparison passes eight Python traces / 83 snapshots; the full-app
`--verify-plant-motion` regression passes. All 77 scene files load, 71 with
declared cases pass, and six have no declared cases. Native pusher/tank 3D and
File/Open inspection are still pending because a Windows update overlay
blocks native input. Generated native review projects are under
`rungproof-next/.tools/plant-review-*.rpproj.json`. Keep the goal active.

Workspace save now completes a temporary file before replacing the destination;
Windows failed-replacement preservation/cleanup/retry and the rendered workspace
regression pass. Unsaved placements/groups/links still need scene/Load/close
guards and saved-baseline comparison for Undo. Preserve synchronous scene
attachment during ladder Open; a deferred Main SceneRequested callback alone
would reopen that prior corruption bug. See the workspace write checkpoint.

Saved-baseline comparison for workspace dirty state is now implemented.
Rendered tests reproduce the former Undo-to-baseline false UNSAVED state and
verify original and nonempty saved baselines with Edit/Undo/Redo/Save. Scene,
workspace Load and close protection is still pending. The current tree's
`Main.WorkspaceVerification.cs` also tests failed atomic replacement.

Workspace replacement guards are now implemented and tested for scene changes,
workspace Load, cross-scene ladder Open, and close. Save cancellation/failure
blocks replacement; Discard does not falsely save; queued ladder opens still
attach the scene before restoring the project. Rendered workspace/editor tests
pass. Native launch, pusher/tank File/Open and motion, placement, Undo/Redo,
close Cancel, scene-change Save and workspace Open were inspected after the
Windows overlay cleared. Native inspection found clipped operator runtime and
navigation on the tank, and stale gizmo/selection after Undo to empty; these
remain to be repaired. Prior pending-overlay statements above describe earlier
checkpoints, not current availability. No PLC connection was attempted.

Operator and PLC-health rails now scroll complete content; native 1600x900 and
1200x675 inspection confirmed readable runtime/health and reachable navigation.
Undo to empty now removes the gizmo and stale placement inspector. Rendered
workspace, app-shell/orphan, split and controller UI checks pass; controller
suite is 140/140. Native windows closed normally without error/leak reports.
Next review areas are remaining editor workflows, Demo 4/5 presentation and
complete sequence boundaries, external profiles, install/export and legacy
conflicts. The goal is active; prior pending-rail statements are historical.

Latest editor checkpoint: block navigation no longer marks a project dirty or
prompts on clean close; save files still preserve the active block. The
controller suite passes 141/141. Native FB/FC/DB browsing and drag insertion/Undo
were exercised. All editor Tree browsers now use readable selected/hovered
states; interface summaries are bounded and explicitly identify declarations
and shared project tags. Offline calls do not implement parameter passing or
per-instance FB storage. Build, rendered ladder interaction and split tests
pass. See the editor browsing checkpoint in `WHOLE_PROGRAM_REVIEW.md`; keep the
goal active for remaining editor, demo sequence, external and install review.

Latest authored demo checkpoint: first Run preserves operator-established scene
feedback instead of resetting it during initial controller load. Demo 4 now
executes its qualified counter in an FB and validation in an FC; its unused
timer was removed without changing completion behavior. Demo 5 includes
comparisons, a parallel actuator-status branch and two populated DB declaration
views. A completed four-pick layer stops pick commands and requires Reset.
Its three delivered XYZ nodes now animate from gantry_cycle and hold on Stop
or command loss; Reset restores them. The coordinate-sensor shutter substitute
was replaced in this scene by a sensor pair. The scene/help explicitly retain
manual feedback and identify the motion as a command visualization, not a
closed-loop placement model. Build, 142 controller tests, app-shell/guard/orphan
checks and 19 plant checks pass. Native first Run, motion, Stop/Reset, four-pick
completion and block views were inspected. Next review: watch-table row
stability under scans, remaining native editor workflows, external profiles,
install/export and generic accessory substitutions. The goal stays active.

RungProof is a Windows PLC visual simulator and training environment. A user
selects a scenario, sees the 3D machine, edits ladder logic in a TIA Portal or
Studio 5000 styled workbench, runs a deterministic built-in controller, and
observes typed symbolic scene I/O. The longer-term product also supports an
authorized external PLC session using the existing guarded Siemens runtime.

The user expects the product to feel like an industrial engineering tool:

- Scenario, Logic Editor, and split-view navigation are quick and reliable.
- The complete operator scene is on the left and the ladder editor is on the
  right in split mode, with a draggable divider and local-model point tables
  remaining visible below.
- Side drawers never overlap the top toolbar or local-model points panel.
- Ladder symbols can be dragged onto visible rung insertion boxes and edited,
  moved, deleted, and added like the target vendor workflows.
- PLC source selection is explicit: built-in Simulator or External PLC.
- External PLC settings show the complete profile, connection, mapping, status,
  readiness, and test results instead of a generic disconnected badge.

## Two application generations

### Legacy/native live-PLC path

The existing guarded live path is under `rungproof/` in the canonical repository
and is the source of truth for real PLC behavior. Paths in the list below are
relative to `rungproof/`:

- `tools/rungproof_native.py` — native Qt application and operator controls;
- `tools/native_runtime.py` — plant/runtime/session lifecycle;
- `tools/plc_live.py` — guarded S7 session and typed exchange;
- `tools/plc_diagnostics.py` — read-only diagnostic path;
- `prototype/src/livePlcBinding.js` — browser/reference binding semantics;
- `prototype/src/player.js` — reference UI flow for Connect Real PLC;
- `prototype/plc-profiles/*.json` — validated scene/profile contracts;
- `vendor/siemens-plc-pc-interface/` — pinned S7 interface implementation.

The live session has separate states for connection, playback, and readiness.
It performs typed cycles, writes only the configured PC-to-PLC scope, reads only
the configured PLC-to-PC scope and status bits, and relies on the PLC watchdog
for safe output handling when cycles stop. Stop and Reset do not intentionally
disconnect the session.

The live path is launched by `RUN-3D-PLAYER.cmd`. The normal release/build
switch that exposes real writes is documented in `rungproof/README.md` and build
scripts. Do not silently enable real writes in an offline test build.

### RungProof Next

`rungproof-next/` is the Godot 4.7.2 .NET application launched by
`rungproof-next/RUN-RUNGPROOF-NEXT.cmd`. It currently provides:

- real 3D scene rendering with reviewed assets;
- scenario browser grouped as User Created, Labs, and exactly five authored
  Demos;
- TIA Portal and Studio 5000 styled ladder editor;
- editable contacts, coils, branches, timers, counters, comparisons, math,
  program-control blocks, tags, watch tables, block/interface lifecycle, and
  save/load of `.rpproj.json` projects;
- deterministic virtual controller and symbolic scene-I/O mapping;
- operator/logic split view, cycle/scan display, diagnostics, local model point
  tables, and training asset help.

The ladder workbench follows the TIA-style ownership model: the left project
dock contains separate Project tree, PLC tags, and Blocks / tasks tabs. The
editor's instruction palette remains the insertion surface, while the old
right-side Instructions / PLC tags / Blocks / Search / Help rail is hidden from
the visible layout. Search and instruction help remain available through their
internal commands without consuming editor width.

The five authored demos now load paired ladder documents when their scenario is
selected. Demo 5 is intentionally the more complex `Lab 11.13 - XY Palletizing
Cell`, not another conveyor view; its ladder contains the OB entry routine,
multiple FBs, multiple FCs, and a DB with visible interfaces and calls. The
app-shell verifier compiles every authored demo document and checks the active
Demo 5 bindings/FB-FC structure.

Its C# connection seam is `src/Connections/GuardedRuntimeClient.cs`. The Next
shell now starts `tools/plc_bridge.py` only when an operator uses the External
PLC settings, and that bridge delegates to the existing `tools/plc_live.py`
controller. The scene/profile contract is retained in the scene's optional
`plcTestProfile` field. Built-in Simulator remains the default source.

The 2026-10-04 whole-program review moved JSON bridge exchanges into bounded
async work through `ProcessBridgeChannel`. `Main._Process` polls completed
requests so UI, connection events and scene commits stay on Godot's main
thread. One request may be outstanding. Scene/source changes cancel pending
work and invalidate approval; a late reply cannot become another scene's
image. Profile cycleMs is currently a minimum frame-driven interval, not a
real-time timing guarantee. The bridge passes the verified descriptor into
`LivePlcController.connect` to reject changed configuration before creating
transport. Typed symbolic scope validation is in `ExternalSceneContract`.
Settings details scroll without stretching the dialog beyond the viewport.
See `WHOLE_PROGRAM_REVIEW.md` for current verified boundaries and open work.

## External PLC feature requirements

The implemented PLC menu provides the following without changing the existing
simulator behavior:

1. **Execution source**
   - Built-in Simulator: uses the virtual controller and local symbolic model.
   - External PLC: scene exchange delegates to the existing guarded live
     session. Next currently blocks local Stop/Reset and unmapped PLC-owned
     actions. Complete playback/command equivalence with the legacy UI remains
     under review; it must not be represented as commissioned or complete.
   - The selected source is visible in the toolbar, operator console, and PLC
     inspector.

2. **External PLC settings**
   - scene/profile selection;
   - CPU family/protocol as supported by the existing adapter;
   - IP/host, rack, slot, cycle, connection timeout, heartbeat timeout;
   - exact PC-to-PLC write scope and PLC-to-PC read scope;
   - typed scene-point mapping and required readiness/status bits;
   - explicit connect/disconnect controls and current session identity/health.

3. **Connection verification**
   - local profile/schema validation;
   - endpoint and transport availability;
   - authorized connection and exact write-scope confirmation;
   - protocol handshake and typed readback;
   - required `simulation_enable`, `simulation_comm_ok`, and
     `simulation_timeout` readiness checks;
   - scene/profile identity and point type/direction validation;
   - watchdog/cycle health and reconnect behavior;
   - read-only diagnostics that prove zero writes when the user selects a test.

4. **Testing**
   - use the existing in-memory transport adapter for automated live-path tests;
   - never contact the plant from CI, headless app verification, or simulator
     tests;
   - keep one explicit operator-run authorization step for a real connection;
   - test disconnect, timeout, stale session, scene change, malformed profile,
     invalid scope, missing status tags, and type mismatch;
   - prove simulator mode still runs when no PLC is available.

## Important prior user feedback

These are not optional polish items; they are recurring acceptance criteria:

- Do not report “complete” until the interaction has been exercised, not just
  compiled or inspected.
- The initial scene must run and animate; RUNNING text without green ladder
  state or animation is a defect.
- E-stop is a physical/momentary safety input, not a latched ordinary command.
  Reset/restart behavior must be explicit and testable.
- Green ladder state, cycle clock, elapsed timer values, and scene animation must
  agree with the same execution source.
- Scene/Event History drawers must remain below the toolbar; the ladder editor
  must stop above Local Model Points.
- Collapsing project/tool drawers must give the editor the recovered width.
- Instruction/tool tabs need vendor-like vertical/horizontal divides and must
  remain aligned at all window sizes.
- Local Model Points columns must stay aligned as values change.
- Scenario names must sort numerically (`2`, `3`, `10`), and groups must not be
  flattened into every row being called “Demo”.
- Save/load must use a named `.rungproof.json` file dialog and preserve the
  ladder/scenario content.

## Current evidence and commands

The last verified Next baseline was:

- C# build: passed with 0 warnings and 0 errors;
- virtual-controller suite: 137 passed, 0 failed;
- app-shell verifier: passed with 77 scenes, 3 groups, 5 demos, 294 assets;
- verifier connection state: disconnected/offline by design;
- Godot may print non-fatal RID/ObjectDB cleanup warnings at process exit.

Run from `rungproof-next/`:

```powershell
& '.tools/dotnet/dotnet.exe' build RungProof.Next.csproj --no-restore
& '.tools/dotnet/dotnet.exe' run --project tests/RungProof.Next.VirtualController.Tests.csproj --no-restore
& '.tools/godot/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe' --headless --path . -- --verify-app-shell
```

The exact pinned Godot path can be found with:

```powershell
Get-ChildItem .tools/godot -Recurse -File -Filter '*console.exe'
```

For the legacy live path, use `rungproof/README.md`, `rungproof/CONTEXT.md`,
`PROJECT_INFORMATION.md`, `tools/test_native_runtime.py`,
`tools/test_player_live_ui.mjs`, and the PLC profile/transport tests. Live
commissioning is not proven by the offline checks.

## Git handoff

The local checkout is authoritative when integration is requested. The current
working branch and remote must be inspected before push. Preserve unrelated
asset/training work. Commit meaningful checkpoints and report the exact commit,
branch, remote, verification results, and whether the tree is clean.
