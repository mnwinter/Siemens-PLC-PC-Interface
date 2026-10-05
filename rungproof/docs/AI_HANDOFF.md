# RungProof / PLC Visual Simulator AI handoff

Dual Spindle failure reproduction (2026-10-05, current): Scene 36 now has an
explicit offline `--audit-dual-spindle` diagnostic in Main.DualSpindleAudit.cs.
It is deliberately separate from the accepted geometry regression suite.
Clean build and app-shell pass; help validates 77 scenes/294 assets. The audit
exits 1 with seven failures and two passes, with no exception. It checks the
actual delivered meshes and 3000 preview/adapter ticks at 2 ms; no PLC transport.

Measured home: shared subplate bottom Y=1.16, steel stock Y=1.205..1.265,
X=-2.38243..0.38243, Z=-0.05652..0.85652. Drill axes are approximately
(-1.22,-1.35) and (1.78,-1.35) in X/Z, with home tips Y=1.61. Both retain
their separate yellow coupons at Y=1.585..1.695. Neither axis lies over
the shared steel workpiece, and its subplate has no bearing contact. The
declared position motions produce zero axial travel for both rotation-only
adapters. The fixture translates 3.2 m while the actual slide plate moves
2.2000003 m; no slide/fixture contact or bearing surface is found throughout.
Timed completion and Reset pass, which does not accept the process.

Native Windows baseline: home FR/FL/RL/RR/Top; held 0.5 s drilling Top/FR;
released preview to completion; endpoint FR/FL/RL/RR/Top; Reset to home.
The endpoint is visibly unsupported and detached from the slide. Intermediate
transfer was not captured as a held native frame or continuous video. Existing
two drill-base/slide-base bounds candidates remain unresolved. Logs:
`.tools/dual-spindle-{audit-red,audit-shell,native-baseline}.log`.
No geometry/controller repair is claimed for Scene 36. Next action: build a
supported shared fixture, align both heads with its actual stock, remove
duplicate coupons, provide axial feed with matching home feedback, and couple
fixture transfer to a mounted slide with a supported receiving route. Do not
merely change the timed completion expectation. Goal remains active; the user
carton window is preserved. The previous goal turn verified the receiving
surface; this continuation commits the prior tote repair and reproduces these
next failures. Do not restart or repeat this audit instead of repairing them.

Tote Finishing installation checkpoint (2026-10-05, previous): Scene 35 now
opts into `toteFinishingLine` mounting variants in SceneComposer.ToteFinishing.cs.
Filler/capper columns, labeler pedestal and vision arch posts are clear of
the belt and conveyor solids/cables. Grounded feet and connected overhead
mounts are checked. Catalog masters and all other installations remain unchanged.
The tote origin moves Y=0.99 -> 0.9 to contact the belt; length 13 -> 14 m
keeps the full delivered footprint supported at the existing X=6.4 discharge.
Nozzle tip/stream, spindle chuck and main camera optic now follow their parent
actuators. The label roll rotates about its actual cross-belt axle.

Twelve focused checks (`--verify-tote-finishing`) cover static station/conveyor
clearance, 245 route samples, five column/foot bearings, overhead connections,
and 5000 actual preview ticks at 2 ms, including all actuator commands, visible
supported discharge, attached moving tools, commands-off completion and Reset.
The red checks reproduced missing contact/support and station/tote collisions;
a later clearance screen found the capper foot intersecting a conveyor anchor.
The verifier caches bounds within a frame; its initial uncached run was
intentionally terminated to improve review speed, not accepted as completed.
Final build is clean. Geometry/workflow checks: 487, zero failures. Controller
tests: 144, zero failures. Scene contract and 77-scene/294-asset shell pass.
Logs: `.tools/tote-finishing-{red-build,red-geometry,clearance-red,build-final,
motion-final,geometry-final,controller-tests,contract,shell-check,native,
native-fixed,native-final,native-shell}.log`.

Native Windows: initial and discharge poses inspected FR/FL/RL/RR/Top. Held
fill pose inspected FR/FL/RL/RR, plus filler-focused RR/Top close views. Released
preview clock traversed the remaining steps to the visible supported endpoint;
Reset restored infeed. No continuous video or held intermediate cap/label/
inspection frames were captured. The normal shell opened this exact repaired
scene; Run opened an empty editor with NO CONTROLLER LOADED, and Start produced
the corresponding blocked-action message. Both own QA windows were closed;
the user's Conveyor Pusher window is preserved.

Still FAIL/open for functional acceptance: selected-controller tote transport,
Start binding, actual uncapped fill/volume, axial cap application, label transfer,
measured inspection feedback, preview restart/resume and dynamics. The preview
still scripts inspection_ok=True and the IBC fill cap remains present; never
call its green contract a proven process. No PLC transport/live test occurred.
Whole-program goal remains active. Continue controller/process work here or
the next placement failure (Scene 36 dual spindle); no new automation/delegation.

Bottle Shuttle controller checkpoint (2026-10-05, previous): Scene 34's
motor_direction is now PLC-owned INT (-1 left, 0 stopped, +1 right), replacing
the incompatible legacy STRING. Scene/help/verification/migration notes agree.
No repository external profile mapping was supplied or changed. DB14 and PLC
ownership remain unchanged. The editable eight-network example is
rungproof-next/programs/examples/02-bottle-shuttle-reference.rpproj.json:
Open Logic Editor > Project > Open project, return to scene, Run, then Start.

Selected-controller plant travel now uses the accepted run/direction image
at 0.75 m/s; it never reverses/stops commands on behalf of the program. Actual
body-triangle optical feedback reaches the next 20 ms scan (15 mm travel per
scan). Both-leg playback Stop/Run retains the ladder step; Reset clears plant
and controller memory. SIM completion observes the stopped return after right
detection. The bounded X=-3..3 model holds a missed-sensor/invalid-direction
image without rewriting PLC commands or claiming completion. Belt/drum travel
shares the plant clock. Native pause exposed a green stacklight after Stop;
the SIM indicator now changes to amber immediately.

Twenty added integration/contract checks pass within 475 geometry/workflow
checks; 144 controller tests, clean build, 77-scene/294-asset shell, editable
project/scene contracts and help validation pass. Red project validation
reproduced IO002 (INT tag vs STRING point) before migration. Logs:
.tools/bottle-controller-{red-contract,build-final,geometry-final,tests-final,
contract,scene-contract,shell,native,native-final}.log.

Windows project opening selected the scene and loaded a stopped controller.
Start while stopped was blocked; Run alone held home. Scene Start produced
right travel, outward Stop/Run resumed, reversal produced -1, and left feedback
ended the trip with run=False/direction=0. Held outward and completed-left
poses were inspected FR/FL/RL/RR/Top. Final rebuilt window verified amber Stop
at a right-side return pose, Run restored -1 without machine Start, and Reset
restored home/scan 0. The first right contact itself was not captured as a
held native frame. Five-view poses and scan-sampled optics/support do not
establish continuous video, acceleration/slip/stability or full mechanical
acceptance. No external transport/live PLC was tested. Whole review remains
active; preserve the user's carton window and continue remaining catalog
motion/placement findings.

Bottle Shuttle motion checkpoint (2026-10-05, previous): Scene 34 now uses
one prescribed 0.75 m/s travel clock for the bottle, belt UV and drums. The
fixed-duration route and timed PC sensor writes are removed. Actual body
triangles and lens-to-lens segments determine feedback and first-contact
reference transitions (right X=2.7688888321 m, left X=-2.7688888321 m).
Stop retains pose and travel leg; Run resumes either leg, rejects repeated
active starts and can start a fresh cycle at the completed left pose. Large
steps consume both transitions without endpoint overshoot. Reset restores
the supported X=-3 m home and actual feedback.

Thirteen motion/ownership checks were added to the eight placement checks;
455 geometry/workflow checks, clean build, 143 controller tests, 77-scene /
294-asset shell and the 16-second declared contract pass. Before repair,
checks reproduced early feedback clearing, speed mismatch, active-start
replacement and both-leg restart failures. The original red run also exposed
unsupported STRING output at the external seam; no transport was constructed.
Logs: `.tools/bottle-motion-{red-build,red,build,geometry,controller,contract,
shell,native}.log`; final strengthened checks are in
`.tools/bottle-motion-geometry-final.log`.

Native Windows: Start while held retained left=True, first half-second cleared
the beam, Stop/held step kept pose, Run/step advanced further. A released
real-time cycle returned with left=True, motor=False, complete=True. Completed
left pose and held right-side return pose were inspected FR/FL/RL/RR/Top.
A second cycle started at the completed pose; fifteen individual half-second
steps inspected outward travel and reversal. At 7.5 s it had already reversed
and moved clear of the right beam; this screenshot is not a captured contact
instant. The log records right=True at reversal. Return-leg Stop/Run/step and
Reset were also inspected. Top distinguishes apparent diagonal-view beam
occlusion from intersection. This is sampled native motion evidence, not
continuous video or dynamics proof.

FAIL/open: normal controller round trip. The legacy motor_direction is STRING;
virtual/external seams currently accept BOOL/numeric only. The reference is
blocked under selected-controller/external playback ownership and does not
manufacture direction. No PLC profile, address or transport changed. Reference
reversal is instantaneous; acceleration, slip, bottle stability and real-machine
sensor response remain unverified. Whole review goal stays active. Preserve
the user's open carton window. Next: resolve the scene/controller direction
contract and test normal operator playback, then remaining catalog failures.


This document is the versioned project-memory handoff for a new AI agent or
developer starting from a fresh branch. It records the durable context that
would otherwise be trapped in a local Codex session. It intentionally excludes
machine-local Codex databases, credentials, screenshots from private chats, and
temporary runtime state.

Bottle Shuttle placement checkpoint (2026-10-05, previous): Scene 34's 162.9 mm bottle
belt gap is repaired by root Y=0.8270833333 m. Both sensor stand spans are
3.2 m, clear of conveyor/Start/status bounds. Product name and capacity fit
separate label regions. Base bottle source/delivery/local review previews
rebuilt with an asset filter; collision unchanged. Eight focused checks pass
within 442 geometry total; build clean, controller 143, shell 77/294, scene
contract/help pass. Native home/right endpoint five views, label close views,
held outward steps, Stop/Run, real-time return and Reset inspected. Start
clears left feedback while the bottle remains at its beam; Stop holds pose,
but Run restarts the timed route and its next half-second repeats the old
pose. Six metres/2.5 s conflicts with configured 0.75 m/s. See
MULTI_ANGLE_SCENE_REVIEW.md for logs and bounded evidence. Next: continuous
command/feedback, Stop/resume and normal controller round trip. Goal active;
preserve the user's open carton window.

Shipping strap checkpoint (2026-10-05, previous checkpoint): Scene 32's six disconnected
bars are now two closed 35 mm wide, 1.2 mm thick bands based on evaluated
load sections. Their returns pass beneath stringers inside fork openings,
128.8 mm above the belt. Convex hulls bridge recessed case faces. Source,
delivery, four model renders and thumbnail rebuilt; collision geometry is
unchanged (autogenerated mesh name only). Four checks failed before repair;
434 total now pass. Build clean, controller 143, shell 77/294, scene contract
and help pass. Native home/pickup five views plus camera-only underside,
automatic completion and Reset inspected. Low views show entry/partial return;
wood occludes the complete underside. See MULTI_ANGLE_SCENE_REVIEW.md for
exact sampling and visual boundaries. Normal loaded-controller lesson and
full mechanical/dynamic acceptance remain open. Goal active.

Shipping load contact checkpoint (2026-10-05, previous checkpoint): base palletized case
asset builder now derives connected bearing planes, removing the 40 mm
stringer/deck gap, 22.5 mm case/deck gap and block/lower-board penetration.
Runner/deck datums remain unchanged. Thin seated tape supports upper cases.
Source/delivery/four review renders/thumbnail rebuilt; only Scene 32 directly
composes this base asset. Five checks failed before repair; geometry 430,
clean build/controller 143/shell 77/294/contracts/help pass. Native focused
home/pickup five views and unheld automatic completion inspected; optical
endpoint stays X=2.5626 m. Logs `.tools/shipping-load-contact-*.log`.
Next: strap side/underside routing, then normal loaded-controller lesson.
Historical hero/scale/wireframe/blind evidence is for the earlier model;
no fresh independent recognition or mechanical acceptance is claimed.
Whole review goal remains active; preserve the user's open carton window.

Shipping pallet reference checkpoint (2026-10-05, previous checkpoint): fixed-start Scene
32 sequences were replaced by an opt-in ShippingPallet reference partial.
AUTO Run/MANUAL jog are guarded, four quarter-route jogs advance from the held
pose, pickup rejects another start, Stop/resume keeps position and mode loss
stops on the next tick. Actual case triangles determine the first beam crossing
at X=2.5626 m and live pickup feedback; continuous progress uses the 6.1626 m
route. Nominal speed is 0.75 m/s (8.217 s total; 2.0542 s quarter jog).
Native 50%/pickup five views, four jogs/fifth blocked, MANUAL Run guard,
held Stop/resume/mode loss/Reset and unheld auto completion were inspected.
Preview text uses G6 while retaining full precision, with stationary controls.
Build clean; geometry 425/controller 143/shell 77/294/contracts pass. Logs:
`.tools/pallet-pickup-motion-{geometry-final,controller,contract-v2,native}.log`
and `.tools/pallet-pickup-motion-hud-{build,shell,native}.log`.
The selected-controller guard deliberately excludes the standalone reference
from virtual/external playback. Next work: normal loaded-controller lesson and
internal case/deck seating; do not claim dynamic or mechanical acceptance.
Whole review goal remains active; no live PLC actions were used.

Shipping pallet installation checkpoint (2026-10-05, previous checkpoint): Scene 32 now
starts at (-3.6, 0.8625, 0), seating all three imported bottom boards on the
900 mm belt with 193 mm flat-span margin. Sensor span 3.6 m clears conveyor
hardware/cable bounds. Automatic endpoint remains X=3.1; first jog ends at
-1.925, exactly 25% of the new 6.7 m route. Five added checks give geometry
411; build/controller 143/shell 77/294/contracts pass. Native home, held
mid-travel and pickup have five views each, plus Stop/Reset and an unheld
automatic run. See [multi-angle evidence](MULTI_ANGLE_SCENE_REVIEW.md).
Scene 32 remains FAIL/open: native post-completion Jog is accepted in AUTO,
jumps to the fixed authored start and retains pickup_sensor=true away from
the beam. Next repair incremental bounded jog, mode requirements, restart
continuity, position/optical feedback and speed agreement; do not repeat the
completed installation review. Normal loaded-controller lesson and internal
case/deck seating remain unaccepted. Logs `.tools/pallet-pickup-*.log`.
Whole goal remains active; no live PLC actions were used.

Pallet robot handling checkpoint (2026-10-05, current): the offline Scene 31
reference now uses PalletRobotMotion on the imported six joints, with held
load/tool attachment, wrist-mounted jaws and following forearm cable. Robot
and receiver have grounded supports and face 180 degrees. Rollers are at
1.195 m; final load bays are X=2.07/0.93, Z=2.15 m. The first carry goes in
front of the cell; approach/park routes use the staging side to avoid the
catalog base-axis limit. Nameplate is on the backstop. Duration 41.446 s;
contract waits 44 s. Stop freezes the pose; Reset is required before restarting
an interrupted/completed reference. Unreachable/malformed motion rejects
before placement/completion. Build, controller 143, shell 77/294, motion 32,
geometry 406, contract/help pass. Native final-model evidence is recorded in
[multi-angle evidence](MULTI_ANGLE_SCENE_REVIEW.md). Scene 31 remains FAIL/open
for normal controller-driven robot operation and unproven physical limits,
self-collision and handling. No live PLC action/transport was used. Continue
those catalog failures; the broad goal remains active.

Pallet receiver checkpoint (2026-10-05, previous checkpoint): Scene 31's stale transfer
targets and height are repaired. The timed reference uses lift/carry/lower
phases to seat both tote bottoms on the 395 mm receiver rollers at
X=3.03/4.17, Z=2.4 m, then counts placements and releases the empty pallet.
Staged roots/nail seating are corrected; carry bottom 2.1 m clears the other
tote. Reference duration is about 30.23 seconds; contract waits 31 seconds.
Four new geometry checks raise coverage to 396; build/controller/shell/motion/
contract/help pass. Native held carry and final landing each have five views,
plus Stop/Reset. Details: [multi-angle evidence](MULTI_ANGLE_SCENE_REVIEW.md).
The robot visibly does not grip/reach the tote: this remains a schematic
reference, not accepted robot transfer or normal controller-driven operation.
Continue that unresolved finding and the catalog failures. Goal remains active.

Demo 5 review-clock checkpoint (2026-10-05, previous checkpoint): opt-in offline Hold/Step
now supports repeatable inspection of the existing command-driven gantry.
Launch with --app-shell --visual-scene-review --shell-scene=lab-11-13-xy-palletizing.
Enable the three manual permissives and normal Run; hold freezes controller and
equipment clocks, and each step advances 25 existing 20 ms scan/motion ticks.
Editor, scene and source changes release hold. It is not a generic plant step.
Seven outward/return phases in five native views were inspected; native
Stop/Reset and editor/source transitions passed. --verify-plant-motion
--visual-scene-review runs 32 checks, including seven clock regressions.
Build/controller/shell/rendered-input/geometry also pass. Details and occlusions:
[multi-angle evidence](MULTI_ANGLE_SCENE_REVIEW.md). Continue unresolved catalog
motion and actual carton/home-feedback work; do not repeat static inspection
or infer pickup/transport from this illustrative sweep. Goal remains active.

Carton static installation (2026-10-05, previous checkpoint): cable surface inspection
found the low RX stand crossing the conveyor rail and the pusher base crossing
conveyor feet. Move RX stand to Z=-1.55 m, configured optical height 0.8470945 m;
keep the inclined optical line unchanged. Move pusher to X=-0.4 m, Z=-2.4 m.
Its additional 250 mm setback is compensated by plateExtensionM=0.87973 m,
keeping plate contact and the 1.35 m stroke. The placement repair also clears
RX foot/head from the pusher. No canonical plant or ownership changes.

New cable-triangle/local-component bounds screen (5 mm broad overlaps, 1 mm
world allowance): 18 original home candidates,
11 remaining in the first repair, nine final; all nine final candidates exclude
cable surface. Optical ray now checks cable triangles instead of empty cable
route bounds. Focused --verify-carton-static-routes runs seven static/optical
checks; full geometry 392, motion 25, controller 143, shell 77 and build pass.
Native final home and held-transfer endpoint FR/FL/RL/RR/Top inspected, plus
pusher-focused RR/Top, Stop hold and Reset/scan zero. Rear views hide lower
sensor hardware; close Top crops receiver/carton edges. Full stroke remains
sampled at 2 ms, not continuously observed in five native views. Reviewer exit
zero. This closes the static cable/stand/base findings at the stated screen
resolution; arbitrary output sequences and complete catalog motion remain open.
Logs: .tools/carton-static-cable-*.log. Goal remains active.

Carton transfer photoeye (2026-10-05, previous checkpoint): the receiving table and retained
carton are confirmed. The former horizontal beam still crossed the received
load after feedback cleared. Scene 74 now inclines the heads from 1.047 m to
2.405 m, with beam X=0.225 m and pusher X=-0.3 m to clear moving members.
Heads aim at each other; posts remain grounded and cloned cable meshes bend
with the heads while keeping their lower M12 endpoints. Other installations
retain their previous geometry. Canonical timing, feedback and ownership are
unchanged. Continuous lens-to-lens tests replace the horizontal-dash assumption.

Six added geometry checks prove aim, support, cable connections, collinear
beam dashes, sampled transfer clearance (2 mm grazing tolerance at 80%), and
absence of other solids in the cleared ray. Repeated real 20 ms ladder scans
also agree with the carton optical path. Build clean; geometry 391, motion 25,
controller 143, 77-scene shell, Python reference 8 cases/83 snapshots and help
pass. Native Windows normal Open/Verify + Load/Run with the existing held
solenoid fixture: staged and received endpoint FR/FL/RL/RR/Top, photoeye-focused
Top/FR/RL, Stop hold and Reset to scan zero inspected; reviewer exit zero.
Rear views hide the lower head; close views crop surrounding equipment. Full
stroke is sampled, not continuously observed from all five native angles.

This closes the horizontal optical-path discrepancy for the reference cycles.
Scene 74 remains FAIL/open for residual static cable candidates and complete
physical acceptance. Current home enclosing-bound candidates total 18 (9
sensor/conveyor, 5 pusher/conveyor, 4 receiver/conveyor), not established solid
collisions. Earlier optical-open and ten-candidate notes are historical.
No sensor vendor performance, rated mechanism, carton accumulation or live PLC
acceptance is claimed. Evidence: `.tools/photoeye-incline-*.log`. Goal active.

Carton plate contact (2026-10-05, latest): Scene 74 configures plateExtensionM
629.73 mm. Composer moves plate/front hardware and adds two rigid yoke arms
seated in the carriage and plate before controller home capture. Hardware and
lettering recessed to avoid carton penetration. Fixed cylinder/frame and 1.35 m
stroke unchanged. Actual-ladder contact red before/green after; five new full
stroke geometry checks at 151 two-ms samples. Build, geometry 385, motion 24,
controller 143, shell and help pass. Native existing held-solenoid fixture
opened/verified/run normally: received endpoint five views, close Top/RL,
Stop/Reset/home checked; owned reviewer exited zero. Contact bottom is partly
occluded in rear views; close views crop surrounding equipment. Continuous
five-angle stroke remains unobserved. Initial direct launch missed DOTNET_ROOT;
fixed to bundled .NET10, helper reset fixed stale window IDs. Scene still
FAIL/open: optical feedback geometry (feedback clears while received carton
can intersect drawn beam), static cable candidates, full physical acceptance.
Current home broad bounds count ten; moving solids pass targeted sweep. No
canonical model/ownership/reference program changed. Earlier plate-gap notes
are historical. Logs: `.tools/carton-contact-*.log`. Goal remains active.

Carton retention (2026-10-05, latest): Scene 74 now retains its released
visual carton separately from the canonical infeed leading edge. It stays
visible at 80% release, follows the rest of the stroke, holds during retraction
and recycles only on plant reload. Reset clears the retained pose. This is one
recycled mesh, not receiver accumulation. Plant timing/counts/feedback and
point ownership remain unchanged. Four added actual-ladder checks pass within
23 motion checks; Python parity eight cases/83 snapshots, build, controller
143, shell and 380 geometry checks pass. Native normal Open/Verify/Run loaded
the ignored `plant-review-scene2-held-transfer.rpproj.json` fixture: two rungs,
hold solenoid after transfer for endpoint inspection. Production reference
unchanged. Received FR/FL/RL/RR/Top inspected, Stop retained load/cleared
commands, Reset restored home/infeed/scan zero, owned window exited zero.
Automatic retraction/reload is scan-tested, not continuously observed native.
Scene remains FAIL/open: plate trails carton, optical feedback geometry and
residual cable candidates unresolved. Earlier disappearance notes are
historical. Logs: `.tools/carton-retention-*.log`. Whole goal remains active.

Pallet outbound support (2026-10-05, latest): Scene 31 adds a 4 m outbound
conveyor at X=5.4 m and a 425 mm bridge deck on a centered 200 mm bearer,
connected posts/feet. All surfaces carry at 900 mm. Tangent gaps are 70/35 mm;
the deeper bearer clears the curved wraps. Flush splice witnesses avoid
runner interference. Same existing conveyor_run drives both belts. Reference
release extends to X=5.2 over 12.307692 s (8 m at 0.65 m/s); contract runs 16 s.
Catalog totals are 604 instances/11 in scene 31. Ten added checks (380 total)
sample actual reference support and complete pallet clearance at 10 ms,
require >=100 mm longitudinal contact per runner, check landing/shared
command/Reset. Round belt/drum and cable conflicts use transformed triangle
bounds after enclosing-box screening. Build, controller 143, shell, plant
motion, scene contract and help 294/77 pass. Native initial/final five views,
unheld completion, held post-bridge Top/RR and bridge Top/RL/RR inspected;
occlusions/cropping are documented. Exact crossing poses have sampled geometry
proof, not continuous native five-angle proof. Full robot transfer remains
FAIL/open: detached loads, miss receiver bays, reach/attachment unproven.
Normal shell remains controller-owned; reference QA does not prove controller
handling, slip/acceleration or loads. Earlier outbound-support notes below are
historical. Logs: `.tools/pallet-outbound-*.log`. Continue with robot/container
path and receiving-bay geometry, then remaining catalog failures.

Pallet-cell installation (2026-10-05): Scene 31's pallet/container roots are
80 mm lower, receiver Z=2.4 m and photoeye span=2.5 m. Five new checks prove
static support/clearance/pigtail seating. Shared photoeye cables now translate
by TX/RX side rather than zero imported object origin, and grow from fixed M12
connections for optical-height changes. Pusher clearance screens curved cable
triangle bounds, avoiding an empty-space AABB false positive. 370 geometry
checks pass; build, shell and the scene reference contract pass. Native five
angles, focused sensor Top/FL/RR and normal Reset were inspected. Full robot
transfer is still FAIL/open: container endpoints miss receiver bays, attachment
is unproven and empty-pallet release goes beyond belt support. Do not accept
the symbolic reference contract as physical transfer proof. Evidence is in
`.tools/pallet-robot-*.log`; full details are in `MULTI_ANGLE_SCENE_REVIEW.md`.
Native pusher regression used the existing ignored endpoint QA project through
normal Open/Verify/Run/Stop/Reset: home/full-extension focused FR/Top inspected,
Stop command FALSE/pose held, Reset home/scan zero. No carton was transferred.
Both owned reviewers exited zero; PLC stayed disconnected.

Tank drain-valve installation (2026-10-05, latest): Scenes 75/76 now declare
one full-size actuated ball valve each, appended to the outlet spool. The
continuous bore's measured near face meets the spool flange at approximately
(0,1.130952,5.464483) m; valve root is (0,0.410952,6.574483) m and the TO DRAIN
boundary is now at its far bore end Z=7.684483 m. A hollow mating flange joins
the installed end. Both shoes are grounded, their posts extended to the
original saddles, and ground fasteners lowered with their respective shoes.
The scene-specific position binding projects existing drain_valve_open: TRUE
is pointer parallel/open, FALSE perpendicular/closed. Inversion is explicit;
autonomous travel is disabled. This uses the existing instantaneous process
command, not an actuator-travel simulation or new valve-position feedback.
No reusable GLB, level calculation, symbolic point ownership, DB14 or live
transport changed. Catalog totals are recomputed from all 77 definitions:
602 equipment instances / seven valves; this also corrects the previously
stale receiver total from one to two. Eighteen new checks pass, including
101 pointer sweep positions, shoe/saddle/anchor contact, joint alignment,
other-equipment clearance and real offline ladder scans across fill/drain
transitions and Stop/Reset: 365 geometry/workflow checks total PASS.
Build zero warnings/errors; app-shell 77 scenes / 294 assets / one existing
diagnostic PASS; 19 plant-motion checks and 143 controller tests PASS;
help 294 assets / 77 scenes PASS. Logs: .tools/tank-drain-{build,geometry,
shell,motion,controller}.log and tank-drain-red.log (both absent-valve checks
failed before repair). Native Windows FR/FL/RL/RR/Top and valve-focused Top/FL
were inspected in both scenes. Temporary ignored four-rung QA projects were
opened through File > Open Ladder Agent Project, then Online > Verify + load
offline, Return to scene and normal Run/Stop/Reset. Actual native snapshots
showed closed/filling and open/draining pointers, stopped commands and reset
initial levels (50%; 42% / 10.72 mA). Native log: .tools/tank-drain-native.log;
owned window exited zero, PLC disconnected throughout. These observations
prove the bounded offline QA path, not all possible student programs or
external-controller behavior. Internal tank visibility and broader operator
process acceptance remain open; the whole-program goal remains active.

Tank piping installation (2026-10-05, earlier checkpoint): Scenes 75/76 explicitly opt
both spools into tankPiping with inlet/outlet roles. The pump and inlet spool
approach the vessel diagonally, clearing the ladder. A 450 mm centreline-radius
elbow joins the pump's upward discharge to the full-size delivered inlet spool;
a hollow radial nozzle/flange joins that spool to the tank at Y=4.6 m. The
outlet spool is rotated to +Z and seated on the actual delivered outlet flange.
Four existing spool feet are grounded and their posts extended to the shoes.
Pump root is (-5.345727,0,-5.345727), inlet root (-2.612760,3.72,-2.612760),
outlet root approximately (0,0.250952,3.699483) m. Port face centres are measured
through accumulated mesh transforms, including the diagonal installations.
A native rear view caught the first straight suction line crossing a support.
It now bends sideways to a FROM SUPPLY boundary, with its own grounded shoe.
The final shoe post is clear of the tube and its saddle meets the underside;
that last height adjustment received a fresh native FR/RR close check in both
scenes. TO DRAIN identifies the outlet boundary. There is no new supply vessel
or physical drain-valve model; the symbolic drain command remains unchanged.
No reusable GLB, level calculation, point ownership, DB14 or live transport changed.
The route helper's optional wall thickness permits a correctly bored inlet
flange; existing calls retain their 22 mm wall. These are visual installation
connections, not hydraulic, hardware-compatibility, fabrication or stress proof.
Twelve original-layout checks failed before the repair. Sixteen new piping
checks now pass, including suction/post clearance and supply shoe contact:
347 total geometry/workflow checks PASS. The shell-radius clearance screen
uses the complete projected part box, including edge interiors, rather than
mistaking empty cylinder-box corners for vessel material.
Build has zero warnings/errors; app-shell 77 scenes / 294 assets / one existing
diagnostic PASS; 19 plant-motion checks PASS; help 294 assets / 77 scenes PASS.
Logs: `.tools/tank-piping-red.log`, `tank-piping-build.log`,
`tank-piping-geometry.log`, `tank-piping-shell.log`, `tank-piping-motion.log`.
Both lessons received native Windows FR/FL/RL/RR/Top static inspection and
inlet top/RR and outlet close inspection. Logs: `.tools/tank-piping-accepted-native.log`
and final shoe adjustment `.tools/tank-piping-shoe-native.log`. Both owned review
windows exited zero. Runtime stayed STOPPED and PLC disconnected throughout.
This closes the disconnected tank-piping and floating-support findings only.
Full controller/operator process behavior, physical drain-valve representation
and internal tank visibility remain open; whole-program goal stays active.

Tank analog transmitter mounting (2026-10-05, earlier checkpoint): Scene 76 now explicitly
opts into roofAnalogProbe. The transmitter is installed at (0.35, 6.233334,
-0.85) m above a short hollow roof socket. Its flange seats on the socket;
the head clears delivered manway/guardrail geometry. Native close top review
showed a tight cable-gland margin in the first candidate, so the final mount
was moved inward and all five full-scene angles were inspected again.
The scene-specific sensing rod is extended to 4.844525 m with its 50 mm
diameter retained; the 120 mm tip weight reaches the modeled zero-level
Y=1.2738094 m. It spans the full authored sight-glass/liquid range. Reusable
GLB assets, symbolic points, DB14 and runtime level behavior are unchanged.
This is a custom virtual installation, not purchased hardware compatibility,
calibration, service-clearance or pressure-vessel design proof.
Five new checks pass: 331 geometry/workflow checks total. Build zero warnings/
errors; app-shell 77 scenes / 294 assets / one existing diagnostic and
19 plant-motion checks PASS. Logs: `.tools/tank-analog-build.log`,
`tank-analog-geometry.log`, `tank-analog-shell.log`, `tank-analog-plant-motion.log`.
Final native Windows FR/FL/RL/RR/Top, transmitter-focused top close and side
views were inspected. The exterior socket/head mounting is visible; internal
rod/tip placement is measured only because the vessel is opaque. Runtime
stayed STOPPED, PLC disconnected, owned review window exit zero. Final native
log: `.tools/tank-analog-final-native.log`. Pipe connections/supports and full
operator process behavior remain open. Whole-program goal stays active.

Tank point-level switch mounting (2026-10-05, earlier checkpoint): Scenes 75/76 explicitly
opt into tankSwitchMounts. Four formerly external/downward probes now enter
the positive-Z vessel wall horizontally through short hollow mounting sockets.
Their tip centres use the full authored sight-glass liquid range, after tank
sizing, and the same low/high thresholds as the runtime. Actual elevations:
High/Low tank 2.196429 and 4.041667 m; Analog tank 2.011905 and 4.226191 m.
Process seals meet the socket ends. Source assets and symbolic point contracts
are unchanged; other tank installations retain their prior geometry.
Eight initial mounting checks failed before the fix. They pass afterward,
plus four checks for clearance from separate equipment: 326 total geometry/
workflow checks PASS. Build has zero warnings/errors; app-shell 77 scenes /
294 assets / one existing diagnostic and 19 plant-motion checks PASS. Logs:
`.tools/tank-switch-red.log`, `tank-switch-build.log`,
`tank-switch-geometry.log`, `tank-switch-shell.log`, `tank-switch-plant-motion.log`.
Both scenes received final native Windows FR/FL/RL/RR/Top inspection, with
mounting-side close views. Exterior socket/head joints are visible; interior
probe placement is proven only by transformed mesh measurements because the
vessel is opaque. PLC stayed disconnected and owned window exit was zero.
Native log: `.tools/tank-switch-native.log`.
This closes only the low/high probe placement finding. Pump/inlet/outlet
connections, elevated pipe supports, analog-transmitter mounting and complete
operator process behavior remain open. The whole-program goal remains active.

Carton transfer investigation: two actual ladder-driven deterministic runs
reproduced four disappearing transfers each. The first scan publishing each
new count had visible=False, position=(-3,0.9,0), stroke=86.666667%, photoeye=False.
ConveyorPlantModel clears LeadingEdge at its 80% transfer crossing; the
renderer copies ObjectPresent to visibility and resets its target without
LeadingEdge/photoeye. This is the cause, not camera clipping. Canonical plant,
DB14 and controller behavior were not changed. Temporary tagged probes were
removed. Evidence: `.tools/carton-transfer-probe-a.log` and `-b.log`.
Receiving lifecycle clarification was requested: manual table clearing or an
automatic takeaway conveyor. It remains unanswered; do not invent accumulation
or remove cartons invisibly as a purported completed-transfer repair.

Carton receiving surface (2026-10-05, latest): Scene 74 now includes a
flat steel table at the 900 mm belt height. Its near edge meets the belt;
the deck is 1.40 x 1.805 m, with four grounded legs, supporting frame and
lower shelf. The existing workbench asset is reused without vise/drawer.
The front supports/shelf were moved beyond the conveyor bracing after the
first clearance check failed. The positive-side photoeye stand is moved to
Z=2.90 m beyond the table; the beam remains across the carton path. Other
receivers and default photoeye installations keep their prior geometry.
Four new receiver checks pass (314 scene/workflow checks total), including
101 geometric carton offsets and 101 pusher positions. Cable candidates use
actual triangle bounds because a routed cable's enclosing box contains empty
space. This is geometry screening, not physical contact or load-rating proof.
Native Windows FR/FL/RL/RR/Top plus receiver-focused Top/FR were inspected:
continuous deck/belt seam, grounded supports and external photoeye stand.
PLC remained disconnected. Logs: `.tools/carton-receiver-build.log`,
`carton-receiver-geometry.log`, `carton-receiver-native.log`.
The missing-surface finding is closed. Plate/carton contact timing and canonical
carton disappearance remain open; no completed transfer is accepted. The whole
program review remains incomplete. Earlier absent-receiver notes are historical.

Pusher installation continuation (2026-10-05, latest): SceneComposer.Pusher
adds explicit conveyorPusher mounting only for Scene 74. It honors 1.38 m
centre height with grounded barrel/guide-bearing/manifold supports; rigid guide
tails remain in their bearings at full stroke, outboard guides clear caps and
attach to the widened crossmember, and four plate bolts now move. Photoeye
X=-0.55 and optional visual stationCenterXM=-0.20 preserve detected beam/body
overlap while clearing moving members. Pure plant/DB14/owners/reusable delivery
assets unchanged. Ten new geometry checks pass, 310 total; clean build,
app-shell, 19 plant checks and eight Python traces/83 frames pass. Native home
and extended five views plus pusher Top/RR at both ends inspected; extended
clevis now visible. Normal Open/Verify/Run endpoint fixture, Stop held scan
4688/pose, Reset home/False/0; PLC disconnected, owned window exit zero. Scene
still FAIL/open: receiver absent, plate/carton contact timing, disappearing
transfer and seven cable broad-phase candidates. No full transfer acceptance.
Details and logs in WHOLE_PROGRAM_REVIEW.md. Older checkpoint findings below
are historical and superseded only where this note explicitly records repair.

Control feedback continuation (2026-10-05): fixed numeric stands must never
depress on input clicks. SceneControlInteractor now limits press travel to
modeled button members or explicitly bound meshes, preserves original home
across repeated pulses, and uses declared travel. The seven-check composed Box
Volume suite fails before/passes after; rendered control/picking/ownership/E-stop
verification and zero-warning build pass. Native wide FR/FL/close FL repeated
readout clicks yielded 850/720/720 with fixed stands; three actual length-valid
cap clicks set True with a fixed mount; Reset restored zero/False. Empty
exercise, PLC disconnected, owned window exit zero. No new five-angle or
loaded calculation acceptance. Details/logs in WHOLE_PROGRAM_REVIEW.md.

Pusher continuation (2026-10-05): EquipmentMotionController now stretches the
960 mm delivered rod in parent X (imported local X is vertical), preventing
detached ends and diameter changes. SceneSimulationRuntime now applies
lateral pusher offset only to the detected station carton; off-station strokes
no longer drag the infeed load off its belt. Plant model/DB14/owners/assets and
scene placement unchanged. Red rod/off-station regressions fail before fixes;
final clean build and 300 scene/workflow, 19 plant execution, eight canonical
Python trace / 83 snapshot and app-shell checks pass. Native endpoint fixture
opened via normal Project/Open and Verify + load (one block/task/network,
six tags); Run, five extended views, pusher Top/RR focus, Stop hold and Reset
inspected. Carton stayed seated at infeed; rod gland visible, clevis obscured
by conveyor. PLC disconnected, owned review window exit zero. Scene 74 remains
FAIL/open for low plate/photoeye interference/guide shafts/missing receiver/
disappearing transferred carton. No full transfer or mechanical acceptance.
See WHOLE_PROGRAM_REVIEW.md for logs and exact verification boundaries.

Box Volume numeric repair (2026-10-05): scene 70 preserves its four Boolean
point names/owners and adds PC-owned DINT length_mm/width_mm/height_mm plus
PLC-owned volume_mm3. Four live readouts replace the static MEASUREMENT legend;
input cycles are 0,250,500,720,850,1000 mm. All six native sidebar actions fit.
The carton/bench/three-head fixture remains static; manual dimensions neither
resize the carton nor simulate sensor acquisition. An empty exercise still
requires a loaded/authored controller. The opt-in project is
`programs/examples/09-box-volume-reference.rpproj.json`: Main always calls FB_Volume;
two MUL networks use global base_area_mm2 memory, then publish validity from
all three manual flags and 1..1000 mm numeric bounds. The maximum product is
1000000000 mm3, within DINT range. Missing validity or invalid dimensions clears
validity while retaining the last numeric result; Stop zeroes output image;
Reset clears inputs/results. FB parameter/instance semantics and source parity
are not established. No transport or physical PLC writes were introduced.
Native Windows FR/FL/RL/RR/Top and close FL were individually inspected: grounded,
supported stands, no separate-equipment penetration, carton seated on bench.
Close FL clips the far-left fixture edge and output-display base; wide views
supply that coverage. Project > Open loaded the actual reference; Online >
Verify + load offline reported 2 blocks, 1 task, 4 networks and 10 tags. Run
and all six actual 3D inputs produced 850*720*720 = 440640000 and a green lamp.
Changing all inputs to 1000 displayed 1000000000; both numeric strings fit
the readout. Width-valid loss cleared lamp/validity but retained that result;
restoration revalidated it; zero height again cleared validity. Stop showed
volume 0; Reset showed all four readouts 0, shown flags False and scan 0.
PLC stayed disconnected. Owned review window closed with exit 0.
17 new integration/geometry checks replace three static-readout checks; all
290 checks PASS. The missing-live-readout regression first failed on the old
scene. Negative/above-limit guard tests use an in-memory sampled-input fixture,
not UI entry or transport. Build zero warnings/errors; app-shell 77 scenes/294
assets/one existing SYSREADY diagnostic PASS; help 294/77 PASS. Controller tests
rerun: 143 PASS/0 FAIL, no PLC transport constructed. Catalog now has 599
equipment instances, including 119 training accessories.
Logs: .tools/box-volume-{red,build,geometry,shell,help,controller,native}.log.
Automatic dimension acquisition, candidate reusable-asset approval, remaining
scene/runtime findings and full packaging acceptance remain open.

Shared 3D control picking repair (2026-10-05): the previous picker merged
all meshes of a control into one world-axis bounding box. Empty space between
readout head, mast and foot could intercept another control's click; rotations
also enlarged the target and hidden meshes were included. The picker now tests
each visible mesh in its own local coordinates and preserves world ray distance
under nonuniform scale. Explicit scene-action routing and point ownership stay
unchanged. Eight fixture checks cover assembly gaps, empty space, head selection,
hidden meshes, rotated targets, scale and nearest-hit ordering. The old picker
failed six of these eight checks; the repaired picker passes all eight.
The rendered --verify-scene-controls run passes the existing Start/mechanical
pulse/E-stop/Reset/controller/external-image/review-overlay checks and exits 0.
A headless run of the old picker also failed existing injected-UI checks; use
the rendered verifier for that UI evidence. Build has zero warnings/errors;
app-shell passes 77 scenes, 294 assets and the existing SYSREADY diagnostic.
Native Windows close front-left clicks individually exercised all five actual
3D inputs in Sum, Product and Sum/Counter, and all six in Function Selector.
Correct action names were observed after every click; A/B displayed 1 after
single cycles, Function Selector choice advanced to 1, and Calculate did not
change B. Reset cleared the readouts and shown Boolean inputs in all four.
These picking checks used stopped empty exercises; prior reference-project
calculation evidence is separate. PLC remained disconnected. Owned window
closed with exit 0. Logs: .tools/control-picking-{build,red,rendered,shell,native}.log.
Bounds remain mesh boxes, not exact triangle hits, and do not establish occlusion
by non-control equipment. Remaining scene/runtime and packaging findings stay
open; whole-program acceptance is not complete.

Function Selector numeric repair (2026-10-05): scene 69 preserves its four
Boolean point names/owners and adds PC-owned DINT operand_a, operand_b and
function_choice plus PLC-owned selected_result. Four live readouts replace
the static FUNCTION legend; A/B cycle 0,1,2,5,10 and FUNC NEXT cycles
0,1 SUM,2 PRODUCT,99 invalid. All six actions fit in the native sidebar.
The opt-in programs/examples/09-function-selector-reference.rpproj.json has
four blocks, one continuous 20 ms task, six networks and nine tags. Main
always calls FB_Selector; qualified comparisons call only FC_Sum or FC_Product.
Unsupported choices clear validity even when manual FUNC VALID is true;
permissive loss retains the last numeric result but clears validity.
Stop clears the output image; Reset clears values and manual inputs.
This is an original offline reference using global tags, not original-source
selector parity, FB parameter transfer, instance-local memory or PLC transport.
The student exercise remains empty until a program is loaded/authored.
Native testing exposed a picking conflict: clicking the visible CALCULATE
button changed B because the B readout picking area intercepted the click.
Moved all four readouts behind the buttons, then individually repeated native
FR/FL/RL/RR/Top inspection and close FL control testing on the final layout.
Wide views show grounded/support-connected equipment and no intersections;
the top QA bar partly obscures the uppermost readout and close FL clips the
left edge/base, so these views alone are not complete support evidence.
Normal Project > Open loaded the actual reference; explicit Online > Verify
+ load offline passed before the layout-only move (4 blocks/1 task/6 networks/
9 tags). Final-layout Project > Open loaded it again. Run and all six actual
3D input controls set A=2/B=5/choice=1 and all permissives: RESULT 7/lamp on.
Choice 2 gave 10; choice 99 cleared validity/lamp and retained 10. CALCULATE
no longer changed B. Stop displayed RESULT 0; Reset restored all four numeric
readouts to 0, shown Boolean inputs False and scan 0. PLC stayed disconnected.
17 new workflow/geometry checks replace three obsolete static-readout checks;
all 276 checks PASS. Build zero warnings/errors, app-shell 77 scenes/294 assets/
one existing SYSREADY diagnostic PASS, help 294 assets/77 scenes PASS.
Controller core unchanged; preceding 143 PASS/0 FAIL run remains current.
Catalog now has 596 equipment instances and 116 training accessories.
Logs: .tools/function-selector-{build,geometry,shell,native,native-before-layout}.log.
Added tools/demo-projects/.gdignore so Godot does not import the console
generator's C# source; removed only its newly generated Program.cs.uid.
Broader scene/runtime, packaging and candidate asset approval findings remain
open. Recheck other numeric lessons for the same front-view picking conflict;
their previous sidebar/clearance checks do not prove every 3D button clickable.

Sum/Product numeric repair (2026-10-05): scenes 66/67 preserve their existing
Boolean validity/request point names and ownership, and now add two PC-owned
DINT inputs plus a PLC-owned DINT result. Three live numeric readouts replace
the static RESULT legend and add clickable A NEXT/B NEXT inputs (0,1,2,5,10);
layout spacing keeps all seven equipment items grounded and mutually clear.
Both remain empty exercises until the student loads/authors a controller.
Opt-in projects: programs/examples/09-sum-function-reference.rpproj.json and
09-product-function-reference.rpproj.json. Each Main always calls its FB, which
uses ADD or MUL and publishes validity from all three manual permissives.
They use global symbolic tags; FB parameter transfer/instance-local storage
are not modeled. Permissive loss clears validity but retains the last result;
Stop zeroes the output image; Reset clears manual inputs and numeric values.
Native Windows FR/FL/RL/RR/Top and close front readout views were individually
inspected for both. Normal Project > Open loaded each actual reference; Run,
A=2/B=5 and all permissives displayed SUM 7 or PRODUCT 10 and a green lamp.
Both Stop/Reset transitions were inspected. Product A-valid loss showed
validity False/lamp off while the result remained 10. Sum received actual 3D
A/B readout clicks; Product used sidebar cycles. Individual Product 3D inputs
were not clicked in this pass. Final shorter scene descriptions were reloaded
and inspected; all five actions fit in each native sidebar at 1602x936.
24 added integration/clearance checks cover initial readouts, qualified and
changed calculations, permissive loss, Stop, restart and Reset; six former
static-readout checks removed because these are now live displays. All 262
geometry/workflow checks pass; build zero warnings/errors; app-shell 77 scenes,
294 assets and one existing SYSREADY scope diagnostic PASS; help 294/77 PASS.
An initial run caught missing numeric-binding labels; corrected bindings pass.
Controller core unchanged; the preceding 143 PASS/0 FAIL run remains current.
Catalog now has 593 equipment instances, including 113 training accessories.
Logs: .tools/arithmetic-numeric-{build,red-geometry,geometry,shell,help,native}.log.
This is offline/source/native evidence only. Candidate asset approval,
physical PLC parity and the remaining scene/runtime findings stay open.

Saved demo file parity repair (2026-10-05): all five programs/demos files
were stale relative to the actual Demo-menu documents. Demo 5 incorrectly
selected conveyor-cell; Demo 4 used unbound recipe/transfer tags instead of
pallet inputs and the live DINT count. Regenerated all five from the current
AuthoredDemoLadderPrograms documents. tools/demo-projects is a dependency-free
.NET 10 generator/checker: default and --check are read-only, --write changes
only the five mapped paths. App-shell verification compares each loaded saved
document with its authored document, preventing this drift from passing again.
The initial check failed all five; regeneration and the read-only check pass.
Normal RUN-RUNGPROOF-NEXT.cmd opened the native Windows application without QA
flags. Project > Open loaded each of the five actual saved files and selected
its correct scene and bindings. Demo 5 Run with three manual permissives showed
both commands True, green indications and visible XY motion; Stop cleared the
commands and Reset restored initial inputs/pose/scan 0. Demo 4 Run accepted a
valid manual pallet edge and published pallet_count DINT 1; Reset cleared it.
Demo 2 Run showed request True/output False immediately, then output True and
an illuminated lamp after the delay; removing the request cleared both, and
Reset returned stopped/scan 0. Demo 1 and Demo 3 file selection/bindings were
inspected stopped in this pass; their complete runtime sequences were not
repeated here. PLC stayed disconnected. The owned review window was closed.
Build: zero warnings/errors; controller: 143 PASS, 0 FAIL; app-shell: 77 scenes,
3 groups, 5 demos, 294 assets, one existing SYSREADY scope diagnostic, PASS.
Logs: .tools/demo-projects-{before,regenerate,build,controller,shell,native}.log.
This repairs saved-file/menu consistency, not automatic physical feedback,
packaging or the remaining scene/runtime findings. Whole-program review is open.

Sum and Counter numeric repair (2026-10-05): scene 68 now declares DINT
operand_a/operand_b (PC), sum_result/event_count (PLC), and four live numeric
readouts. The unbound CNC was removed; three manual Boolean input plates were
labeled. Existing Boolean points and ownership remain intact. Clicking the
A NEXT/B NEXT 3D readouts or sidebar actions cycles 0, 1, 2, 5, 10. The exercise
still opens with an empty project. An explicit editable reference is supplied
at programs/examples/09-sum-counter-reference.rpproj.json; its always-scanned FC
uses ADD and a qualified rising call_complete edge, then Main uses CTU and MOV
ACC to the count output. Counter state is global memory, not FC-local instance
storage; call_complete is manual PC feedback, not automatic machine feedback.
Native full-scene FR/FL/RL/RR/Top and close operand/result views were inspected.
Both 3D operand readouts accepted clicks and displayed changed input values.
The normal Project > Open workflow loaded the reference; Online > Verify + load
offline reported 2 blocks, 1 task, 6 networks and 11 tags. Operator Run, operands
2 and 5, and the three manual inputs displayed SUM 7 and COUNT 1. The held input
did not recount across later scans. Stop showed SUM/COUNT 0; Run restored 7/1
without a new event; Reset showed input/readout zero, BOOL False and scan 0.
Eleven added integration/clearance checks cover these transitions plus invalid
completion followed by permissive restoration. Build has zero warnings/errors;
244 geometry/workflow checks, app-shell 77 scenes/294 assets (one existing
SYSREADY scope diagnostic), and help 294/77 pass. This is offline/source evidence;
physical PLC behavior, independent candidate asset approval and full-program
acceptance remain open. Logs: .tools/sum-counter-{build,geometry,shell,help,native}.log.

Normal launch and retained Qt/packaging review (2026-10-05): executed
RUN-RUNGPROOF-NEXT.cmd without QA flags. Restore/build/import completed and the
native application opened the default Conveyor Inspection Cell. The ordinary
Scenario Browser loaded Demo 5; Operator Run started the built-in controller,
three sidebar manual permissives produced vacuum_pick/gantry_cycle=True, green
indications and visible XY gantry motion. Stop cleared both commands; Reset
restored initial geometry, inputs False and scan 0. PLC stayed disconnected.
This confirms the normal source launcher and that bounded Demo 5 sequence; it
does not establish automatic carton transport or completed physical picks.
The retained Qt source startup initially failed for missing PySide6. Installing
its exact locked Qt wheels in the deep checkout hit the Windows 260-character
path limit (LongPathsEnabled=0). A shorter isolated Qt environment completed
hash-checked Qt and Python-3.12-compatible JSON-schema dependencies and pip check;
no Windows settings were changed. Its native Operator/Immersive/Engineering
layouts and transition to Conveyor Inspection Cell review were inspected; the
review correctly shows PLC disabled, no transport and locked playback. This is
Qt source/disconnected UI evidence only, not packaged EXE, Qt3D or live acceptance.
The full package lock has a cp314 Windows rpds-py wheel hash (confirmed against
PyPI metadata); the local cp312 wheel correctly fails it, and Python 3.12 also
needs an additional typing-extensions dependency. The release script formerly
used py -3 and deleted its environment before discovering these mismatches.
It now preflights exact Python 3.14.5 x64 before removing/installing anything,
uses py -3.14 or an explicit -PythonExecutable, and validates a reused SkipBuild
environment too. Actual explicit-3.12, reused-3.12 and missing-launcher cases were
rejected; an existing environment marker was preserved (unchanged hash on the
missing-launcher case). The project lock is unchanged. Python 3.14.5 is absent
here, so the full Windows package build/installer remains unverified.
Evidence: .tools/normal-launch-review.log, legacy-native-{review,short-review}.log,
legacy-qt-{install,short-install}.log, legacy-jsonschema-install.log,
legacy-source-runtime-install.log and legacy-package-preflight.log. The deep
checkout Qt installation was partial; only the short isolated environment passed
installation/checks. Whole-program review continues; these launch checks do not
close open scene/runtime findings.

Arithmetic validity layout repair (2026-10-05): scenes 66, 67 and 69
remove their unused CNC and function-block panel substitutes. Delivered node
inspection proves the alleged panels were pillow-block bearing/shaft models;
none of the removed items had point bindings. Three actual input stations now
carry A VALID / B VALID / CALCULATE plates for Sum and Product, and OPERANDS /
FUNC VALID / CALCULATE for Function Selector. Descriptions, guides, requirements
and help consistently describe manual Boolean validity/request exercises, with
no numeric operand/result or actual function choice modeled. Each scene's five
full-scene native Windows views were individually inspected after the change,
plus focused Top/RL/RR readout views. The previously CNC-obscured readout backs,
masts and floor bases are clear. Sum and Function Selector each received actual
3D input-button clicks with readable close face plates; Product used its native
sidebar actions. Each corresponding PC input toggles True, all three together
were observed, PLC-owned result remains False while stopped, and Reset restores
all inputs False. Six layout/plate checks pass, alongside existing support and
readout-clearance checks (233 total). Build zero warnings/errors; app-shell and
full help audit pass. Controller core unchanged; preceding 143 tests remain the
latest controller result. Catalog equipment total now 586 across 77 scenes.
Evidence: .tools/arithmetic-layout-{build,geometry,shell,help,native}.log. Numeric
sum/product/selector computation, authored-ladder operator output and independent
asset approval remain open. This supersedes the CNC/bearing-prop and rear-readout
occlusion findings for these three scenes only. Whole-program review continues.

Box-volume fixture repair (2026-10-05): the dimension_sensors shutter
substitute is replaced by an original static bench/portal with three orthogonal
sensor heads. The unused CNC is removed from scene 70. The carton now sits at
Y=0.9 on the carrying bench; the earlier floor-contact check was valid for the
old placement and is superseded by this supported fixture layout. Actual mesh
checks verify full carton footprint on the bench, seven grounded feet, connected
legs/posts/heads, correct LENGTH/WIDTH/HEIGHT face plates, and clearance between
the carton, fixture and separate controls/readout. Seven fixture checks pass
(227 total geometry/reference/workflow checks). Native Windows full scene plus
FR/FL/RL/RR/Top focused fixture and readout views were individually inspected:
carton contact and supports are clear; rear views now reveal the readout mast
and base that the CNC previously obscured. Head visibility varies by view, with
all three inspected across those views. Clicking each actual 3D LENGTH, WIDTH,
HEIGHT button sets its corresponding PC-owned validity input; all three True
were observed together while the PLC-owned result stayed False with runtime
stopped. Reset clears all three. This is static geometry/manual-input acceptance;
numeric acquisition, calibration, dimension values, volume calculation and a live
MEASUREMENT display remain unimplemented. Catalog quality remains candidate /
unapproved, prior shutter approval evidence is preserved as historical-invalid,
and descriptions/help state the limitation. Catalog equipment totals are
recomputed from actual scene entries (592 across 77 scenes). Build zero
warnings/errors; 143 controller tests, app-shell and full help audit pass.
Evidence: .tools/dimension-fixture-{build,final-build,final-geometry,controller,
shell,help,native}.log. Whole-program review remains open and continues.

Catalog success-message scope repair (2026-10-05): SYS-READY now says
catalog data checks passed for 294 assets/77 scenes, followed by the requirement
to verify scene appearance, motion, control logic and PLC operation separately.
It no longer describes the combined production/candidate asset catalog as all
candidate assets or implies no corrective action remains. Native Windows scene
browser shows the complete message on one readable line without clipping at
1602 x 936. Build has zero warnings/errors. Evidence: .tools/catalog-status-
{build,native}.log. This wording change does not close the open visual/runtime
findings or establish real PLC compatibility. Review continues.

Radar installation and range repair (2026-10-05): five native focused views
reproduced electronics buried in the roof/manway. The transmitter now mounts
at X=0.7, Y=6.213333, Z=0.5: its process flange bottom contacts the delivered
roof at Y=6.083333, clear of the manway. Actual ring vertices distinguish the
hollow guard from its misleading solid bounding box; electronics remain inside
the ring with clearance. The horn enters the opaque roof intentionally as a
symbolic process penetration; no fabricated opening or mechanical approval is
claimed. Radar distance now starts at the antenna lens lower face and ends at
the world-transformed liquid surface. The beam shares these datums and stretches
to the surface instead of retaining its fixed imported length. An initial
placement protruded the widened beam through the wall; the inward adjustment
and imported-vertex radial check now keep the beam inside the shell. Seven
mount/range/fill/drain/stop/reset checks pass (222 total). Fill and drain are
sampled for 200 steps each at 0.02 s through the typed symbolic output boundary;
this is plant geometry/runtime evidence, not an authored-ladder operator pass.
Native final FR/FL/RL/RR/Top views show the head above the roof, the flange
separate from the manway in Top, and no wall protrusion; rear-left flange detail
is partly manway/rail-obscured. The normal I/O panel shows radar_distance
3.10036 at 35%. Normal Run still opens the empty ladder editor with NO CONTROLLER
LOADED, so interactive fill/drain acceptance remains open. Description/help
explicitly state the opaque beam occlusion and idealized echo-health behavior.
Disconnected inlet pump/high pipe route and outlet/drain assembly remain open.
Build zero warnings/errors; 143 controller tests, app-shell and full help audit
pass, without real PLC transport. Evidence: .tools/radar-mount-{verified-build,
verified-geometry,controller,shell,verified-help,native-final}.log. Initial
failed mount/rail-hull checks are preserved in radar-mount-{geometry,collision}.log.
Whole-program review continues; no goal status change or completion claim.

Box-volume floor-contact correction (2026-10-05): a focused perspective view
looked like the carton was suspended. Current delivered mesh bounds instead
confirm carton bottom Y=0 on the actual 40 x 40 floor at Y=0, with its full
footprint on that floor and no separate-equipment penetration. Two explicit
checks pass (215 total geometry/reference/workflow checks); clean build. The
carton placement was correctly left unchanged. This supersedes the unsupported-
carton claim in the preceding readout checkpoint. The scene still lacks actual
dimension sensing/numeric volume and retains a substitute sensor asset.
Evidence: .tools/box-volume-contact-{build,geometry}.log. Whole-program acceptance
remains open; review continues.

Static readout and diagnostics follow-up (2026-10-05): six mislabeled shutter/
selector substitutes were replaced with original stand/readout assets. They
display MEASUREMENT, RESULT, FUNCTION, COUNT, PROGRESS or WEIGHT plus NO LIVE
VALUE; they have no numeric binding. Catalog bounds, help and candidate status
now describe the delivered geometry. Invalid former recognition/reference
evidence is archived as historical, not reused as approval. The shared builder
preserves the cut-length entry point. Parking and hand-dryer readouts moved
from Z=1.8 to 3.1 after imported-mesh checks reproduced their wall/shutter
intersections. Twenty-one identity/support/clearance checks were added; all 213
geometry/reference/workflow checks pass. These checks do not accept the scenes.
All seven affected scenes were individually inspected in native Windows at
FR/FL/RL/RR/Top with the readout focused. Parking RL is shutter-obscured; hand
FL text is partly lamp-obscured and RL shutter/CNC-obscured; sum/product both
rear views are CNC-obscured; selector and box-volume RR are CNC-obscured;
weight RL is CNC-obscured and RR partly lamp/CNC-obscured. Those remain failed
detail views. Front readout labels and separate Top footprints were observed;
box-volume also still has an unsupported carton. Scene descriptions/guide/help
now state the manual or symbolic scope and missing numeric behavior explicitly.
The full help audit now passes 294 assets/77 scenes normally and with Python -O,
superseding the six failures in the previous checkpoint below.
The diagnostic whitelist omitted the renderer's implemented speedPercent and
numericDisplay modes. Both now validate; an isolated unknown-mode fixture still
fails as expected. Native scenario browser shows 0 errors, 0 warnings, 1 SYS-READY
info. Build has zero warnings/errors, 143 controller tests pass, app-shell passes;
no real PLC transport was constructed. Evidence: .tools/static-readouts-{build,
final-geometry,final-help,native,native-final}.log and render-binding-{final-build,
controller,shell}.log. Whole-program acceptance remains open. Saved goal status
is blocked from the earlier run; review work is continuing without a status change.

Whole-catalog help-audit repair (2026-10-05): the validator now reports every
missing contract entry before returning exit 1, instead of stopping at the
first assertion. Missing documents are reported once and repeated runs clear
old findings. Explicit checks also preserve failure under Python -O, where the
previous assertions could be disabled. Two regression tests pass normally and
with -O: multiple conflicts remain failures, repaired fixtures become valid,
and a missing file does not prevent other assets from being checked.
The actual full audit returns exit 1 in both modes, covering 294 assets and 77
scenes. Six conflicts remain: numeric_measurement_display, numeric_result_display,
numeric_selector_display, occupancy_counter_display, progress_display and
weight_display (all training.accessory.*.v1). Their help omits catalog-declared
shutter/selector motion paths. This is a documentation failure, not acceptance
of those questionable geometry identities. Evidence: .tools/help-full-audit.log,
help-full-audit-optimized.log and help-audit-unit{-optimized}.log. The review is
ongoing and acceptance remains open. The saved goal tool currently reports
blocked; no completion or status change was issued in this work session.
Cut-length display identity repair (2026-10-05): the delivered asset was a
roller shutter, while its help described a parking display. It now uses original
Blender-source stand/readout geometry with LENGTH / NO MEASUREMENT. Catalog
bounds come from evaluated geometry; shutter kinematics, generic basis and
unrelated reference evidence were removed. Historical shutter/parking review
files are preserved as invalid identity history. No numeric point or measurement
algorithm is bound. Scene 53 describes its manual permissive scope explicitly;
three START plates are now CABLE / LENGTH / HOME. Four identity, support,
clearance and plate checks pass; total 192 scene geometry/reference/workflow
checks pass. Native Windows FR/FL readout text/base/mast and Top footprint were
inspected. Rear-left is shutter-occluded and rear-right camera is blocked by the
CNC; those are failed detail views, not acceptance. Each actual 3D button was
clicked and its corresponding PC-owned input became True; outputs stayed False
while stopped. Reset cleared all three inputs. Build zero warnings/errors,
143 controller tests pass without real transport, initial scene contract and
app-shell pass with no ERROR lines. Expected missing-workspace warning remains.
Global help now passes this asset and fails at the existing numeric_measurement_
display KIN_bottom_bar mismatch. Scene 53 remains open: payoff reel is a shutter,
dancer/cutter are cable trays, encoder is unbound, continuous measurement/cutting
and the assembled layout are unverified. Evidence: .tools/cut-length-display-
{build,code-build,import,geometry,controller,contract,shell,help,native}.log.
Whole-program acceptance remains open; goal active.
CALL/JSR block-name repair (2026-10-05): instruction boxes now resolve the
stable call-target ID to the current declared block name. Serialization and
execution still use the same ID; unresolved targets retain that ID for diagnosis.
Native Windows Demo 5 normal Run and Logic Editor were inspected in both TIA
and Studio 5000 styles. FB_SafetyInterlock, FB_PickAndPlace,
FC_SequenceSupervisor and FC_InspectionMath fit their CALL/JSR boxes without
clipping. Scan counts advanced and green power flow remained visible. This
closes the CALL readability finding recorded below. Build has zero warnings/
errors, all 143 controller tests pass without real transport or connection, and
app-shell verification passes for 77 scenes/294 assets with no ERROR lines.
Native rename and unresolved-target workflows were not individually tested.
Evidence: .tools/call-name-{build,controller,shell,native}.log. Whole-program
and scene acceptance remain open; the goal remains active.
Demo 5 moving assembly and operator plates follow-up (2026-10-05): the full
three-second sampled sweep now checks all four moving parts against posts and
separate equipment, tool height above the empty pallet, rod/carriage/tool seating
and carriage support inside the bridge span. All four checks pass; total 188
scene geometry/reference/workflow checks pass after an additional plate check.
Three misleading START plates are now CARTON / HOME / PALLET. Build clean,
143 controller tests pass without real transport, initial contract and app shell
pass with no ERROR lines. Native normal Scenario menu selected Demo 5 and Run
loaded its authored ladder. Manual permissives start the gantry/vacuum outputs;
running FR/FL/RL/RR/Top views were inspected. Rear-left rod detail is robot-
occluded and overhead hides the rod; FR/FL/RR cover those details. Native Stop
removed commands and held the same pose on a later capture; Reset restored it
and scan zero. Fresh rendered CARTON/HOME/PALLET plates were each inspected and
each actual 3D button was clicked: matching PC-owned points became True, outputs
remained False while stopped. Normal Run then preserved those manual inputs and
issued matching commands. Editor opens Palletizing_Cell_Main and shows green
power flow. An open editor readability bug was found: CALL shows stable block-3
instead of the FB name. No automatic carton transport, optical home feedback,
physical vacuum pickup or real-PLC acceptance is established. Evidence:
batch-display-native-final.log (Demo 5 navigation/motion after Demo 4),
demo5-full-sweep-{build,geometry,final-build,final-geometry,controller,contract,
shell}.log and demo5-label-native-final.log. Goal remains active.

Pallet count readout workflow repair (2026-10-05): authored Demo 4 now publishes
PLC-owned DINT pallet_count via MOV batch_count.ACC after the counter call.
Scene 71 binds that point to a live COUNT readout; the reusable display remains
static when used without this scene configuration. A regression first failed
because the output did not exist. The composed-scene check then exposed INT/
DINT commits being promoted to Double by the REAL switch arm. Integer branches
now box Int64 before that promotion; INT/DINT limits and truncation and REAL
fraction preservation pass. Nine count workflow checks cover invalid events,
later permissives, five edges, held detection, validity loss, Stop/Run/Reset.
All 183 geometry/reference/workflow checks pass; build zero warnings/errors,
143 controller tests pass without real transport, initial contract and app-shell
checks pass with zero ERROR lines. The expected missing-workspace warning remains.
Native Windows normal Run, action rail, Stop, Run and Reset were individually
observed: COUNT 0 rejects an invalid event and later validity; valid detection
edges show 1/2/3/4/5 matching the DINT point, validity is false before five and
true at five, loss of type validity clears validity but retains count five.
Stop shows zero; Run republishes five without a new edge; Reset shows zero,
cleared visible inputs/outputs and scan zero. Live text was inspected FR and FL
close. This does not establish optical classification, pallet travel, CNC
integration or physical PLC behavior. Scene help was regenerated from the new
contract; global asset-help validation still has the cut_length_display mismatch.
Evidence: batch-display-{red-controller,final-build,controller,geometry,
probe-build,probe,typed-build,typed-geometry,final-controller,final-contract,
final-shell,native-final}.log. Goal remains active; catalog acceptance is open.

Pallet Counting prop repair (2026-10-05): the type sensor was a pallet and the
count display was a roller shutter, with unrelated recognition records. Both
now use original Blender-source geometry: an optical-profile fixture and a
stand readout. Stale motion/basis/reference/quality evidence was cleared; old
review files are preserved as invalid identity history. Help was rebuilt for
these two assets only. The fixture surrounds the conveyor at (-1.1,0,0).
The first version failed delivered feet/control/cable clearance; the widened
version passes six identity/support/solid-clearance checks. All 171 geometry/
reference checks pass. Final native scene FR/FL/RL/RR/T wide, fixture Top/FL/RL
close and display FR close were inspected. Rear display detail is CNC-occluded
and is not an acceptance view. COUNT / NO LIVE VALUE is readable; base/mast
are seated. Type algorithm, numeric count binding, pallet motion and a new
controller workflow remain unverified; the CNC is still unrelated/unbound.
Build clean, import without ERROR, initial contract and 142 controller tests
pass; app shell passes without ERROR, with the expected missing-workspace
warning. Global help validation now fails at the existing cut_length_display
KIN_bottom_bar mismatch. Evidence: pallet-props-{build,code-build,geometry,
collision-build,collision,clearance-build,clearance-import,clearance-geometry,
final-build,final-import,native-final,help,controller,contract,shell}.log.
Goal active. All 77 initial native inspections include failures, not acceptance.

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
