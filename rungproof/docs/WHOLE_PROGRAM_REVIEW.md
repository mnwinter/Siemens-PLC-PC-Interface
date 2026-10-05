# Whole program review - 2026-10-03

Demo 5 review-clock checkpoint (2026-10-05, current): seven held phases of the
complete outward/return gantry sweep were inspected in five native Windows
views (35 pose/view observations). No pallet/post intersection or detached tool
appeared. The opt-in offline Hold/Step controls use the existing ladder and
20 ms motion path; normal Run and manual permissives remain required. Native
Stop/Reset and editor/source transitions were checked. Build, controller 143,
shell 77 scenes/294 assets, rendered input guards, plant motion 32 and geometry
392 checks pass. See [multi-angle evidence](MULTI_ANGLE_SCENE_REVIEW.md) for
occlusions and scope. Carton pickup/transport, automatic home feedback and full
catalog motion remain open; this is not whole-program acceptance.

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

Carton plate contact (2026-10-05, latest): a 629.73 mm rigid two-arm yoke now
connects Scene 74's plate to its carriage and closes the measured load gap.
Cylinder frame and 1.35 m stroke remain unchanged; front hardware/lettering is
recessed. Actual-ladder contact failed before repair and now passes through
repeated transfers. Five new geometry checks cover station acquisition,
connections, contact, solid clearance and support at 151 two-ms samples.
Build, 385 geometry checks, 24 plant-motion checks, controller 143, shell and
help pass. Native normal Open/Verify/Run with the held-solenoid QA fixture:
received endpoint five views, close Top/RL, Stop and Reset/home inspected;
reviewer exited zero. Continuous five-angle stroke observation is unproven.
Scene remains FAIL/open for optical feedback geometry and static cable
candidates; earlier plate-gap findings are historical. No rated mechanism,
accumulation or live PLC proof. Evidence: `.tools/carton-contact-*.log`.

Carton retention (2026-10-05, latest): Scene 74's receiver is present and its
carton now remains visible after canonical transfer. The renderer follows the
remaining stroke and holds the load on the table through retraction, recycling
the one visual carton only on actual plant reload. Reset restores the infeed.
No plant timing, feedback, counts or ownership changed; accumulation is not
modeled. Four new actual-ladder checks pass (23 motion checks total), along
with canonical Python parity (eight cases/83 snapshots), build, 143 controller
tests, 77-scene shell and 380 geometry checks. Native normal Open/Verify/Run
with an ignored held-solenoid QA fixture showed the received carton in all
five views; Stop retained it and Reset restored infeed/home/scan zero.
Automatic retraction/reload has scan evidence, not continuous native visual
coverage. Scene 74 remains FAIL/open for plate contact, optical feedback
geometry and residual cable candidates. Earlier disappearance notes below
are historical. Evidence: `.tools/carton-retention-*.log`; reviewer exited zero.

Pallet outbound support (2026-10-05, latest): Scene 31 has a second conveyor
and grounded bridge at the same 900 mm carrying height. Its full 8 m timed
reference release ends with the pallet entirely on the outbound flat belt.
Both conveyors use the existing command. Ten new checks prove bounded
geometric support/clearance throughout that reference, final landing and Reset
(380 total); build, 143 virtual-controller tests, shell, plant motion, scene
contract and help validation pass. Native staged/final five views, unheld
completion, held post-bridge Top/RR and bridge-focused Top/RL/RR inspected;
close-view occlusions/cropping are recorded in MULTI_ANGLE_SCENE_REVIEW.md.
Crossing geometry has 10 ms sampled proof, not continuous five-angle native
observation. Container paths still miss receiver bays and robot attachment is
unproven; scene 31 remains FAIL/open. No full physical handling, controller
sequence or live PLC acceptance is claimed. Earlier outbound-support notes
below are historical. Evidence: `.tools/pallet-outbound-*.log`.

Pallet-cell installation (2026-10-05): Scene 31's 80 mm pallet/belt gap,
receiver/conveyor intersection and sensor/brace placement are repaired.
Both containers moved down with the pallet. The shared photoeye composer now
uses TX/RX ownership for cable translation and stretches raised-head pigtails
from their fixed M12 connections. Five new checks pass (370 geometry/workflow
checks total); build is clean, the existing reference contract and 77-scene
shell verifier pass. Native Windows five-angle static inspection, sensor close
Top/FL/RR and normal Reset confirm the repaired installation. Robot attachment,
container paths/receiver seating and supported outbound pallet travel remain
open; the reference contract only checks symbolic sequence results. See the
latest note and scene 31 row in `MULTI_ANGLE_SCENE_REVIEW.md` for evidence.
The affected carton pusher was also checked in Windows at home/full extension
from focused FR/Top, using normal Open/Verify/Run/Stop/Reset with the existing
offline endpoint QA program. Stop clears its command while holding the pose;
Reset restores home. This empty stroke does not verify carton transfer.

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

Pusher installation repair (2026-10-05, after the rod-only checkpoint below):
Scene 74 explicitly opts into a composed conveyor mounting. Its existing
centerHeight=1.38 m is honored without stretching the cylinder diameter.
The floor base remains grounded; two columns contact the barrel bottom, a
wider third column supports both fixed guide bearings, and a new base-mounted
post supports the raised air manifold. The low unconnected wear rails are
hidden in this installation. Reusable source/delivery assets are unchanged.
Guide shafts have rigid rear tails extended by the stroke, with their front
seats preserved; guides/bearings/brackets/locknuts are moved outboard to clear
the cylinder caps, and the crossmember is widened to retain bracket contact.
All four formerly fixed plate bolts now follow the moving plate.
Photoeye X=-0.55 m clears the full moving assembly. Optional visual
stationCenterXM=-0.20 m puts the carton body across that beam when canonical
photoeye feedback first becomes True; it does not alter the pure plant model,
point owners or DB14. Default scene projections retain their previous datum.

The first eight installation checks exposed seven failures before opt-in.
All ten added checks now pass, including 101 samples for rigid guide bearing
engagement, cap clearance, attached brackets, sensor-solid clearance and
following fasteners. Total scene/workflow checks: 310 PASS. Final build has
zero warnings/errors; app-shell 77 scenes/294 assets/one existing diagnostic,
19 plant execution checks and eight Python traces/83 snapshots pass. Logs:
`.tools/pusher-installation-red.log`, `pusher-installation-final-build.log`,
`pusher-installation-final-geometry.log`, `pusher-installation-shell.log`,
`pusher-installation-plant-motion.log`, `pusher-installation-plant-reference.log`.

Native Windows final home and full extension were each inspected in FR/FL/RL/
RR/Top, with pusher-focused Top/RR at both ends. Unlike the lower prior mount,
the extended clevis is now visible above the belt and both guides are visibly
engaged. Normal Project > Open and Verify + load used the ignored endpoint
review file (one block/task/network, six tags). Run held full extension with
conveyor OFF/photoeye FALSE and the infeed carton seated. Stop held pose/scan
4688 across fresh captures; Reset restored home/output FALSE/scan zero.
PLC remained DISCONNECTED; owned window exit zero. Native log:
`.tools/pusher-installation-final-native.log`.
Scene 74 remains FAIL/open for absent receiver, plate-to-carton contact timing
and disappearance at canonical transfer. Seven residual broad-phase cable
candidates (two photoeye/conveyor, five pusher/conveyor) are not cleared by
these moving-member checks. No complete supported transfer or mechanical
design approval is established.

Control feedback repair (2026-10-05): clickable numeric displays previously
depressed their entire fixed stand; repeated clicks during a press captured
the depressed pose as a new home and accumulated permanent drift. Mechanical
feedback now targets modeled button members or explicitly bound individual
meshes. Repeated presses retain the original home, and use declared travel.
The seven-check composed-asset suite failed before the fix and passes afterward;
the rendered scene-control verifier, picking, controller ownership and E-stop
checks pass. Build has zero warnings/errors. Logs are
`.tools/control-feedback-red.log` and `.tools/control-feedback-rendered.log`.
Native Windows Box Volume wide FR/FL and close FL were inspected. Four L,
three W and three H readout clicks produced 850/720/720 without moving their
stands. Three actual length-valid cap clicks set its flag True without moving
the mount; Reset showed four zero readouts and the shown flags False. PLC
remained DISCONNECTED and no controller was loaded for this input/geometry
pass. Owned window exited zero. This is not a new five-angle or calculation
acceptance pass; those are recorded separately below.

Pusher rod and off-station projection repair (2026-10-05): native Scene 74
dragged its infeed carton sideways when the pusher extended with the conveyor
OFF and photoeye FALSE. The plant correctly withheld transfer/counting; the
renderer applied the stroke to every carton. Lateral projection now requires
the carton to be detected at the transfer station. This symbolic qualification
does not establish physical plate contact or a supported transfer.

The rod adapter stretched the imported cylinder's local X (vertical), using
stroke as the scale divisor. Full-extension parent bounds were X=0.745..1.705 m
and vertical diameter doubled to 180 mm. The correction stretches parent X by
the delivered 960 mm rod length and shifts its centre by half the extension:
the gland stays at X=0.070 m, the free end reaches X=2.380 m and remains seated
in the moving clevis, and both transverse dimensions stay 90 mm. No mesh,
scene placement, point owner, DB14 contract or canonical plant logic changed.

Red checks failed six rod assertions and both off-station carton assertions.
Final build: zero warnings/errors; all 300 scene/workflow checks pass, including
101 stroke samples in each of two world orientations and rod Stop/Reset.
Plant execution passes 19 checks; the pure plant retains eight Python traces /
83 matching snapshots. App-shell passes 77 scenes / 294 assets with its
existing single diagnostic. Logs are `.tools/pusher-rod-red.log`,
`pusher-offstation-red.log`, `pusher-geometry-final.log`,
`pusher-final-plant-motion.log`, `pusher-rod-plant-reference.log`, and
`pusher-final-shell.log`.

Final native Windows Project > Open loaded the ignored endpoint review file
`.tools/pusher-rod-review.rpproj.json`; Online > Verify + load reported one
block/task/network and six tags. Actual Run held full extension with conveyor
OFF and photoeye FALSE. FR/FL/RL/RR/Top were individually inspected: carton
stayed seated at infeed. Pusher-focused Top/RR showed the rod at the gland;
the conveyor hides the extended clevis. Stop held pose/scan 4466 across fresh
captures; Reset restored home, output FALSE and scan zero. PLC remained
DISCONNECTED; the owned review window closed with exit zero.

At that earlier rod-only checkpoint, Scene 74 remained FAIL/open: plate too low, home intersects rear photoeye support,
guide-shaft engagement at full stroke unresolved, and no receiving surface.
Canonical transfer still hides the carton at its configured threshold. This
endpoint fixture is not acceptance of a complete supported carton transfer.

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
Crossing/process checkpoint (2026-10-04): coverage 65/77 native five-view static
inspections; 12 pending, including failures. Scenes 60-65 expose wrong traffic,
bridge, coating, weighing and dryer equipment identities, disconnected routes,
lamp-only machine outputs and missing measured weight/remaining-time contracts.
Bag Indexing's buried carton now rests on its measured 0.9 m belt. Two focused
checks fail before/pass after; rebuilt native five wide and top/FR close views
confirm static contact. Build zero warnings/errors; all 151 geometry/reference
checks and initial-state contract pass. These six lessons have no loaded-ladder
or machine-motion acceptance. Luggage's buried carton still needs repair.
See MULTI_ANGLE_SCENE_REVIEW.md for exact findings/evidence. Goal active.

Earlier checkpoint:

Timer/packaging checkpoint (2026-10-04): coverage 59/77 native five-view static
inspections; 18 pending including failures. Scenes 51-59 inspected. Cookie
product is packaged meat below the conveyor, barrel is a motor starter, cable
reel/dancer are shutters; machine outputs only lamps. Timer panels have clear
stands but input semantics/control identities and tower-level output gaps.
Demo 2 normal Run loads authored TON: request initially off then green, 3D
button clears request/output, Stop removes output, Reset clears both points
and scan. Source preset two seconds; precise native timing not measured.
Other eight scenes have no loaded controller behavior acceptance. Details in
MULTI_ANGLE_SCENE_REVIEW.md. No code changes since carton repair. Goal active.

Earlier checkpoint:

Catalog/carton checkpoint (2026-10-04): coverage 50/77 native five-view static
inspections; 27 pending, and inspection includes failures. Scenes 43-50 expose
count/pattern and machine-behavior gaps. Four-color lesson binds only green
lamps; garage vehicle is a motor starter, barrier output only a lamp; package
and chain-lift outputs also only lamps. Chain-lift equipment overlaps.
Guarded Transfer and Package Grouping cartons were below their belts. Both now
rest on measured 0.9 m belt tops, confirmed in rebuilt native five wide views
and top/FR close views. Four new delivered-mesh checks fail before/pass after;
all 149 geometry/reference checks and both initial-state contracts pass, build
zero warnings/errors. Machine motion, protective behavior and complete counter
workflows are still unaccepted. See MULTI_ANGLE_SCENE_REVIEW.md for exact scope
and evidence. Goal active.

Earlier checkpoint:

Press-count checkpoint (2026-10-04): coverage 42/77 native five-view inspections,
35 pending including failures. Demo 1's input was a persistent toggle: three
clicks created only two rising edges. It now pulses and its plate reads PULSE.
Native authored Run, two rail presses (off), third 3D press (green), Stop (off),
Run (green from retained count), Reset (false points/scan zero), and final close
plate inspected. Guide distinguishes Stop from counter Reset. Five integration
checks exercise the actual scene action through authored ladder and scan session;
four failed before repair, all pass afterward. All 145 geometry/reference checks,
142 controller tests and initial-state contract pass; build zero warnings/errors.
Inspection-toggle reference contracts and shell pass; shell retains four existing
headless position errors/missing-workspace warning. Revised startup guidance was
visually inspected. Full catalog and open repairs remain; goal active.

Earlier checkpoint:

Native catalog/editor checkpoint (2026-10-04): coverage 41/77 five-view
inspections, 36 pending including failures. Scenes 38-41 inspected. Guarded
transfer's carton is buried under its belt; protective props are outside the
route. Robot restart's arm occupies the CNC and outputs bind only to lamps.
Its persistent reset toggle does not provide a spring-return reset request.
Inspection Toggle now has a TOGGLE plate, freshly inspected close. Through the
normal native editor, a temporary NO contact / SET lamp network was created,
verified/loaded offline, run and pulsed; beacon lit, Stop extinguished it, Reset
restored false values and scan zero. Draft discarded via native unsaved guard.
This bounded editor test does not validate odd/even toggle logic or other scenes.
Startup message now explains the empty-exercise and Verify + load prerequisite.
Exact observations/evidence in MULTI_ANGLE_SCENE_REVIEW.md. Goal remains active.

Earlier checkpoint:

Service-door and catalog checkpoint (2026-10-04): coverage 37/77 native
five-view inspections, 40 pending including failures. Door controls no longer
intersect the shutter; their plates read OPEN/STOP/CLOSE. Its raw NC signal
stands are separate and explicitly labeled. Standalone reference motion now
reverses from the current pose and projects matching SIM position/PC NC feedback,
with autonomous adapter travel disabled only for this installation. Native
held opening/Stop/reversal, resumed closing, unheld opening, five open views and
Reset inspected. No physical limit/cable or loaded-controller acceptance.
Build zero warnings/errors; 140 geometry/reference checks, two door contracts,
142 controller tests, 19 motion checks, rendered controls and shell pass. Shell
retains four headless position errors. Scenes 32 and 34-36 reviewed: pallet/sensor
mounting, overlapping bottle text, finishing columns in belt corridor and shared
plate misalignment remain open; normal Start/Jog blocks without a controller.
Exact scope and evidence are in MULTI_ANGLE_SCENE_REVIEW.md. Goal remains active.

Earlier checkpoint:

Drill geometry checkpoint (2026-10-04): one delivered stock mesh replaces the
buried duplicate fixture; measured 150 mm home clearance and 245 mm feed now
move the quill/chuck/bit while retaining spindle rotation. Stop explicitly holds
feed; Start requires top, and Reset restores it. Native repaired five views,
close feed/bottom/retract/Stop/Reset views and unheld reference completion inspected.
Normal 3D hand buttons work; cycle start blocks without a loaded controller.
129 geometry/reference checks, four drill contracts, 142 controller tests, 19
motion checks, rendered controls and shell pass; build has zero warnings/errors.
Shell retains four existing headless position errors. Guard/two-hand safety
behavior and normal loaded-controller lesson remain unaccepted. Scene 31 also
has five native views and receiver top/FR close views: FAIL, receiver intersects
conveyor, pallet appears above belt, full transfer unverified. Coverage 32/77,
45 pending including failures. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Drill inspection / Run repair (2026-10-04): coverage now 31/77 native five-view
inspections, 46 pending including failures. Close inspection finds an extra
clamped fixture buried below the press table. Native reference bottom feedback
changes without axial feed; the rotation-only adapter ignores feed commands.
Stop and retract stops but does not retract. Three operator plates and the QA
HUD/action overlap are repaired and native checked. Exposing Run also reproduced
a default-sequence permissive bypass; Run now uses the declared Start action.
Four negative cases fail before repair and pass afterward; positive completion
and unconditional sump start remain available. Native blocked Run, valid
real-time reference completion and Reset verified. Build 0 warnings/errors;
117 geometry/reference checks, two drill contracts, 19 motion checks, 142
controller tests, rendered controls and shell pass. Shell retains four existing
headless position errors. Reviewer windows exit 0; user Demo 1 preserved.
Drill feed/fixture/stop and guard/two-hand model remain open, along with prior
failures. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Sump piping repair (2026-10-04): actual tank/pump flange connections, suction
offset/discharge elbow, horizontal valve/spool alignment and five grounded
pipe supports replace the disconnected/interfering installation. Final native
five wide views and four pump-focused close views were inspected. Six new
mesh checks fail on original placement and pass after repair. Build has zero
warnings/errors; 111 geometry checks, one sump contract, 19 motion checks,
142 controller tests, rendered controls and shell pass. Shell retains four
headless position errors. Normal Run still opens NO CONTROLLER LOADED.
This is a partial repair: closed-vessel sump identity, tuning-fork float assets,
buried low probe/process fittings and full native level motion remain open.
Coverage stays 30/77 inspected, 47 pending including failures. Isolated reviewer
exits 0; user Demo 1 preserved. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Fume speed / Stop repair (2026-10-04): coverage remains 30/77 native five-view
inspections, 47 pending including failures. The missing speed-percent binding
now projects 0/35/65/100% onto the imported rotor hierarchy without bypassing
the separate run command. Actual six-blade transforms reproduce the original
fault and pass after repair. Native QA five running angles, speed indications,
Stop across a selector change, resumed Run, independent-light Off and Reset
were inspected. Stop also exposed reference rules immediately restarting the
fan; a standalone boolean-panel latch now holds the declared initial outputs
until Run/Reset. Selected-controller ownership remains separate. Ten new
checks bring geometry verification to 105; build, five fume contracts, 19 plant
motion checks, 142 controller tests, rendered controls and shell pass. Shell
retains four headless position errors. Preview windows exit 0; user Demo 1
preserved. Sump installation still fails, and fume hood/duct/illumination and
loaded-controller lesson execution remain open. Exact evidence in
MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Sump / fume follow-up (2026-10-04): coverage now 30/77 native five-view
inspections, 47 pending including failures. Sump fails installation review:
disconnected pump, elevated unsupported/interfering pipe/valve assembly and
low probe below floor. Its passing reference contract does not accept that
geometry. Fume extractor equipment spacing is clear in five views; its START
plate is repaired to LIGHT REQUEST and checked in fresh native close views.
Native selector pointer/input cycles through all four positions. Five reference
contract cases pass, including one speed indication, independent light and
return to off. Normal Run opens an unloaded editor; rendered fan speed percent
is unbound, and hood/duct/inspection-light identity remain open. Build has zero
warnings/errors; 95 geometry checks and 142 controller tests pass. Shell passes
with four existing headless position errors. Isolated windows closed; user
Demo 1 preserved. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Coolant installation repair (2026-10-04): the jug now contacts the actual belt,
has an open annular mouth and clears the fill structure/photoeyes throughout
sampled travel. Grounded portal supports and an attached nozzle tip/valve-driven
visual stream replace the obstructed standalone installation. Native catalog
five views and five held QA filling views, close FL mouth/stream, real-time
indexing/exit and Reset were inspected. Native Stop was endpoint-only. All 95
geometry checks, one fill contract case, 19 motion checks, 142 controller tests,
rendered control checks and a zero-warning/error build pass. Shell passes with
four existing headless window-position errors. Normal Run still opens an unloaded
controller editor; external skid service piping is missing. This is a bounded
geometry repair, not full process/lesson acceptance. Coverage remains 28/77,
49 pending including failures. Isolated reviewers closed; user Demo 1 preserved.
See MULTI_ANGLE_SCENE_REVIEW.md for exact evidence and remaining limitations.

Earlier checkpoint:

Coolant Jug inspection (2026-10-04): coverage is now 28/77 native five-view
inspections, 49 pending, including failures. Five angles and close fill-unit
views expose a capped jug and fixed fill-assembly solids in its indexing lane.
Visual acceptance remains failed/open; imported cap/nozzle, belt/support and
sensor bounds need measurement before repairing the installation. The 53 AABB
candidates are not 53 proven collisions. Normal Run opens a blank controller
editor with EDIT INVALID / NO CONTROLLER LOADED. No filling sequence, probe,
transfer endpoint or moving clearance acceptance. Isolated window closed and
user Demo 1 preserved. See MULTI_ANGLE_SCENE_REVIEW.md for exact evidence.

Earlier checkpoint:

Hydraulic attachment follow-up (2026-10-04): Assembly Lift's fixed rod/clevis
failure is repaired with a connected arm/clevis/rod/barrel chain. Actual imported
mesh-cap checks reproduce two failures before repair and pass through both
directions after repair. All 85 geometry checks, both lift contract cases,
19 plant-motion checks and a zero-warning/error build pass. Native Windows
reinspection covers all five angles, closer lift view, FL/RR raising/lowering
and endpoints, FR raised attachment and Reset. Stop was clicked at the completed
top endpoint; mid-cycle hold is deterministic evidence only. This does not
establish physical hydraulics, PLC-controlled lesson execution, independent
asset recognition or guarding. Historical bellows evidence remains stale, and
the four other scenes sharing this lift need native follow-up. Coverage remains
27/77 inspected, 50 pending, including failures. User Demo 1 preserved and the
isolated preview closed. Exact evidence in MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Assembly Lift follow-up (2026-10-04): coverage is now 27/77 native five-view
inspections, 50 pending, including failures. Imported deck contact corrected
from fixture Y=0.82 to 1.64, with matching raise/lower endpoints. Six new checks
cover support, moving rollers/washers, full travel framing, Stop and Reset;
all 81 geometry checks pass. Close RAISE/LOWER plates and both directions were
inspected in Windows, with FL/RR motion and five final static angles. The shared
lift adapter now moves 16 rollers/washers with their pins, and the camera fits
the remaining travel. The no-controller QA toolbar can select Lower as well
as Raise. Normal Run still opens a blank controller exercise. Full motion is
not accepted: the hydraulic rod remains fixed while its driven arm moves, and
the historical bellows review describes geometry absent from the current asset.
Native Stop was checked at an endpoint; mid-cycle Stop is deterministic evidence.
Build, two contract cases, 19 plant-motion checks, 142 controller tests and shell
verification pass. Shell emits four headless window-position errors. Rendered
control checks pass with/without the review overlay; headless mouse-control
checks fail and are retained as failed evidence. Shared lift revisions require
native follow-up in the four other catalog scenes using this asset. User Demo 1
preserved and isolated windows closed. Goal active; hydraulic repair, 50 pending
inspections and prior failures remain. See MULTI_ANGLE_SCENE_REVIEW.md.

Earlier checkpoint:

Vote, collector and tote follow-up (2026-10-04): coverage is now 26/77 native
five-view inspections, 51 pending, including recorded failures. Inspection Vote
and Dust Collector have corrected VOTE A / VOTE B / STOP plates, close views,
native PC input clicks and Reset. Inbound Tote Stop previously floated 99.5 mm
above its belt, intersected the conveyor frame with photoeye solids, and finished
partly beyond the belt end. Three scene values now correct bottom contact,
photoeye clearance and full endpoint support. Final five views and close tote
views were inspected; plant-preview movement/completion was observed from FL/RR
and the finished footprint overhead. Native Stop holds the completed endpoint;
mid-cycle Stop is verified in the deterministic check only. Reset was checked.
All three ordinary Run attempts open an empty exercise with NO CONTROLLER LOADED.
No PLC-controlled lesson sequence, barcode detection or dust process is accepted.
Fresh build has zero warnings/errors. All 75 geometry checks and three focused
scene contracts (six cases) pass. Six new geometry checks include three reproduced
before-fix failures; remaining seven cable/frame AABB candidates are documented.
See MULTI_ANGLE_SCENE_REVIEW.md for evidence and boundaries. Isolated windows
closed cleanly; user Demo 1 was preserved. Goal active; 51 scenes plus recorded
failures remain open. Next full inspection is scene 26, Assembly Lift.

Earlier checkpoint:

Selector and panel follow-up (2026-10-04): coverage is now 23/77 native five-view
inspections, 54 pending, including previously recorded failures. Two Station
Call, Bay Light Selector, Ready/Attention, Dual Contact Permissive and Maintenance
Beacon have final FR/FL/RL/RR/T inspections with clear spacing and grounded
supports. Five wrong START plates now read NORTH CALL / SOUTH CALL / ATTENTION /
RESET NO / TEST NC. Close views confirm fit. Native input actions and Reset were
checked; actual 3D controls were clicked in both selector lessons and the
Ready/Attention and Dual Contact lessons. All five normal Run attempts open
the empty exercise editor with NO CONTROLLER LOADED. Their output sequences
remain unaccepted. Ready/Attention's persistent toggle also does not establish
its described spring-return interaction.

The selector used three fixed marks regardless of positionCount and rotated its
handle around Y, away from the imported dial face. Composed variants now use
configured 2-4 detents, readable external numbers, plate-contacting tick solids,
and the actual Z-axis pivot, including initialPosition and Reset. Final Windows
close views cover Bay Light's 0/1 and Maintenance's 0/1/2/3 plus wrap/Reset.
The unchanged three-mark master contradicts its old four-position approval;
its entry is now candidate with cleared quality flags, and old recognition and
review are archived. No independent approval is fabricated. Master re-authoring,
approval/help reconciliation and native rechecks of its other variants remain open.

Fresh build has zero warnings/errors; all 69 geometry checks pass (20 new selector
checks across four bound lessons). Before-fix count/alignment/plane failures are
preserved. Plant checks (19), authored cases (71), virtual-controller tests (142),
77-scene shell verification and normal rendered controls pass. Final build,
geometry and native views include the last tick/legend adjustment; the behavior
suites preceded that geometry-only adjustment. Evidence and per-scene boundaries
are in MULTI_ANGLE_SCENE_REVIEW.md. Reviewers closed cleanly; user's Demo 1 preserved.
Goal active; 54 scenes remain pending and recorded failures still need repair.

Earlier checkpoint:

Catalog scenes 9-12 and panel plates follow-up (2026-10-04): coverage is now
18/77 native five-view inspections, 59 pending. Wastewater Collection has
overlapping tanks and a pneumatic valve bank labeled as process piping. The
Pallet Route has three superimposed belts, a disconnected roller zone and no
pallet; its handoff sensor package contains a vibration sensor/bearing assembly.
Service Elevator has a shutter intersecting a scissor platform, a bucket
elevator labeled car/shaft and cabinets labeled call station/position sensor.
Mobile Traffic Lights uses a vertical observation-window wall as roadway and
single amber beacons as traffic head/synchronization link. All four have failed
FR/FL/RL/RR/T inspections; close transmitter and conveyor views were inspected.
Normal Run was separately clicked on each: empty editor, NO CONTROLLER LOADED.
Shared source review confirms these labs are tag-only exercises, not supplied
reference ladder programs. No controller was fabricated to mask that boundary.

The previously observed START-plate errors in Workstation Call, Dual Confirmation
and Service Marker are repaired through four scene faceLabel settings. Final
five-view inspections and all four close plates were inspected; MATERIAL CALL,
OPERATOR OK, QUALITY OK and INHIBIT fit their plates. Existing scene-contract
checks pass for all three. Normal Run on each still opens its empty exercise
editor; no runtime behavior acceptance follows from the label change. No C# or
asset geometry changed; the prior build/49-geometry/19-plant results were not
rerun for this label-only change. Evidence: .tools/catalog-scenes-9-12-native.log,
catalog-scenes-9-12-source.log, call-panel-native-final.log and
lab-2-0{1-workstation-call,2-dual-confirmation,3-service-marker-inhibit}-plate-contract.log.
The isolated review windows closed cleanly and the user's Demo 1 was preserved.
Goal active; the four newly inspected failures need source/layout/runtime work.

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


## Current status: visual review reopened (2026-10-04)

The user identified a pallet intersecting a Demo 5 gantry post after the prior
software review checkpoint. That checkpoint did **not** include multi-angle
inspection of every scene and cannot establish whole-program visual acceptance.
The visual-review goal is active. See [MULTI_ANGLE_SCENE_REVIEW.md](MULTI_ANGLE_SCENE_REVIEW.md)
for the complete catalog coverage ledger and remaining repairs.

Demo 5's pallet, conveyor carton, robot clearance and coordinate-sensor placement
are corrected. The gantry gripper now moves with its Z axis. Native Windows
inspection covers four diagonal views and overhead, with motion observed from
front-left and rear-right views. Seven geometry/motion regression checks pass.
This is an illustrative command sweep, not closed-loop carton placement.

The new complete shell/geometry inventory also reproduced a scene-opening error:
REAL points initialized with JSON `0` reached the strict ladder editor as a long.
Normalize that numeric token to double at the scene-project boundary. The catalog
test now uses the plant's actual scalar-reading behavior; it failed before the
fix and all 142 tests pass afterward. All 77 shell scenes now inventory without
that error. The current inventory flags candidates in 43 scenes and does not
grant visual approval. Powder-mixer placement is now repaired; tank shell sizing
honors the authored diameter/height, and an original static open chute replaces
the incorrectly labeled roller-shutter. Its inherited door approval is removed.
Five-view native reinspection verifies the bounded static layout. Radar feedback
now accounts for parent scale, and Reset projects its restored feedback.
Thirty-eight focused geometry checks, 19 plant checks and 71 authored scene cases pass;
six scenes have no authored cases. Three family-selection regression cases pass.

Parcel-sorter startup and native exercise-editor opening now work with REAL
`route_position=0`. Its table/belt layout, carton support, optical heights and indexed paths
are repaired. Five native static views plus portal/table details were inspected;
plant preview Run/Stop/Reset and a three-route completion were observed. Normal
shell Run opens a blank editor with NO CONTROLLER LOADED; no reference controller
is supplied for this scene. The declared plant preview does not pass that workflow. Current native static coverage is 14/77, with 63 pending; inspections include failures.
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
Workstation Call, Dual Confirmation and Service Marker have clear spacing/supports but generic
START plates for other input functions; their labels still need correction.
Global help validation also fails on Count Display's inherited door metadata.
Mixer process behavior and full catalog runtime acceptance remain unverified.

Restore tag before this pass: `codex/multi-angle-review-baseline-20261004` at
`2c3de4b`. The software evidence below remains valid within its stated scope;
the prior final checkpoint is historical, not the current visual acceptance.

Scope: the entire canonical PLC interface and RungProof application. Demo 5
is one reproduction example, not the acceptance boundary. The review and repair
pass covers startup, scene/controller ownership, editor/persistence, workspace
authoring, external IPC, Python interface and retained legacy tools. The current
matrix below separates verified repairs from remaining product capabilities;
older checkpoints preserve the evidence and status at that time.

Checkout: `Siemens-PLC-PC-Interface`, branch `agent/add-config-foundation`.
Restore tag: `codex/whole-app-review-baseline-20261003` at `c4cda6b`.
The user's older dirty canonical checkout has not been located or modified.
No changes have been pushed. No plant connection has been attempted.

## Evidence and fixes

| Finding | Cause and correction | Evidence |
| --- | --- | --- |
| Windows launcher cannot find .NET | Missing path separator produced `dotnetdotnet.exe`. Corrected executable path and added a missing-runtime message. | Executed the actual `.cmd` launcher; clean build and native RungProof window observed. |
| Scene action buttons stop working during scans | Runtime refresh destroyed every button between mouse-down and mouse-up. Construct them on scene attachment; refresh values separately. | Reproduced and retested using Windows Computer Use on the native Godot window. Gantry-home, pallet-valid, and carton-present now toggle while scanning. App verifier checks button identity across 90 scans. |
| Run advances scans while the toolbar and footer say Stopped | Status read plant motion instead of selected controller execution. Read the virtual snapshot in simulator mode. | Native Run and Stop now show the correct state. |
| Simulator labeled External PLC while disconnected | Status selected the client class rather than the execution mode. Read the selected mode. | Native PLC health now identifies local runtime, no echo, connection disabled. |
| Demo 5 commands persist after a permissive drops | Conditional calls skip the blocks that clear prior memory. Scan permissive-producing blocks each cycle. | Regression reproduced failure before fix. Native lost-home click now removes vacuum and gantry commands. |
| Demo 5 counts unavailable cartons and repeatedly increments a completed layer | Dwell ignored permissives; layer arithmetic executed every scan while completion stayed true. Gate dwell with pick permissive and count completion rising edges. | Two controller regressions passed after fix. |
| Opening a saved ladder for another scene replaces it with a demo | Restored the saved document before scene attachment installed the starter template. Attach the scene first, then restore saved work. | App-shell regression preserves a custom network label after scene change and reopening, including the loaded controller program. Native same-scene save also verified. |
| 31 unresolved accessory errors despite existing mappings | Type-level migration metadata predates accessory configuration. Validate configured catalog IDs and retain missing-ID errors. | App shell now reports one informational ready diagnostic, 77 scenes, 294 assets. This does not grant production or visual approval. |
| Normal conveyor Start is overwritten by the next scan | Sidebar and 3D actions wrote an output directly. Both now use one controller route, with authored momentary command bindings and matching loaded output bindings. | Native Windows Start produced `conveyor_run=True`, speed 1.05 m/s, and carton motion. Rendered picking/scan regression passes. |
| Scene rules compete with the selected controller | Fallback fake-PLC rules executed on feedback changes. Suppress them while a controller owns the output image. | Regression verifies feedback changes preserve the controller output and that fallback rules still work after returning to local scene execution. |
| E-stop leaves controller running or permits automatic restart | Route simulated E-stop through the active controller Stop and block Run while its scene permissive is latched. Reset clears controller state without starting. | Native E-stop, blocked Run, and Reset inspected; rendered regression also requires a fresh Start after Reset and Run. |
| Pending momentary Start fires after Stop/Run | Session Stop retained an unscanned pulse. Cancel pending pulses and partial elapsed scan time on Stop. | Controller regression; 139 tests pass. |
| External and virtual controllers can publish competing outputs | Mode change unloads the virtual session; external physics takes an exclusive branch. External Run no longer invokes fake-PLC logic. Local Stop/Reset/PLC-owned scene actions are blocked in external mode. | Offline regression checks mode exclusivity and preserves an injected external output image. Native external selection blocks local Start without connecting hardware. |
| Event History never records events | Replace placeholder with bounded, scrollable action and controller-transition history. | Native Run and accepted/blocked Start events displayed. |
| Split view obscures the scene and camera frames covered areas | Use the visible scene aperture for framing, projection offsets, picking, and resize updates; hide information rails in split. | Rendered camera/picking regressions and native minimum/default/maximized windows inspected. |
| Points disappear in standalone editor; collapse does not reclaim editor space | Share a bounded scrollable point dock across operator/editor/split views and move editor bounds with its collapse state. Align point columns with the split divider. | Split layout regressions at 1200x675 and 1600x900; native collapse and expand inspected. |
| Narrow editor hides title/status, menus, and instruction access | Responsive toolbar, clipped tab titles, scrollable vendor menus, compact drawers, and an operational instruction browser. Preserve drawer choices after layout updates. | Native title/status/browser and rendered editor/drawer regressions passed. Narrow editor and point lists require scrolling. |
| Split Save opens the workspace dialog | Treat split as a ladder editing view for Save/Load. | Native Save opens the ladder-project dialog; cancelled without writing. |
| Point headings and values wrap after maximizing | Theme font changes leave stale BBCode table column measurements. Reparse the table only when its font size changes. | Native 1200x675 to maximized and back inspected: headings, BOOL, and conveyor_run remain on one line. |
| A missing bridge reply freezes UI/physics indefinitely | Async serialized JSON exchange with deadline/cancellation, continuous bounded stderr drain, and process teardown on a bad reply. Poll completions on the Godot main thread. | 13 process/client/contract tests include hung reads, stderr flooding, malformed/EOF replies, cancellation, fresh-process recovery, and stale session rejection. No PLC transport. |
| Mismatched profile can still Connect; approval survives a selection change | Enforce declared scene/profile and typed PC/PLC mapping; clear approval on scene/profile/source changes. Revalidate before Connect and bind backend connection to the verified descriptor from the same configuration load. | App-shell guard regression; two new fake Python regressions reject changed IP/slot/cadence before transport creation. |
| Partial or wrongly typed external image changes some scene points | Require the complete configured PLC point scope and validate all ownership/types/ranges before committing any point. | Pure contract tests and rendered scene-control regression require typed and atomic rejection. |
| Every physics frame issues PLC I/O and can queue stale work | Use profile cycleMs as the minimum request interval and allow only one pending exchange. Discard late results after source/scene changes. | Source review and single-pending/session cancellation tests. This is frame-limited scheduling, not a measured real-time 20 ms guarantee. |
| External health placeholders conceal actual readback | Display the guarded result's cycle health, heartbeat reason/echo/age and required readiness status. Reject malformed health metadata. Keep unavailable labels while disconnected. | Fake healthy/fault/status-type regressions; native disconnected health inspected. No live readiness proof. |
| Read-only test competes with an active session | Require a disconnected session before opening the separate diagnostic transport. | Guarded UI source review. |
| Settings buttons fall below the native window | Bound the autowrapped explanation width before initial layout and keep profile details at a scrollable fixed height. | Native 1200x675 settings and profile mismatch inspected; rendered bounds verifier passes. |

## Review matrix

| Area | Current evidence | Remaining acceptance / capabilities |
| --- | --- | --- |
| Launch/import/toolchain | Fresh tracked-source copy reproduced missing restore; repaired launcher restores/builds/imports and opens a working native window. Missing Godot/.NET/console stop with exact paths | Portable tools require setup; no standalone export preset/installer supplied |
| All scene data | All 77 catalog entries load; 71 have declared cases and pass; six have none. Rerun logs in `.tools/plant-scene-review` | Visual controls and runtime coverage; many declared cases cover only initial state |
| Authored demos | All five compile; 142 controller tests pass. Native demos 1-4 exercised; Demo 5 four-pick completion, mixed instructions, FB/FC/DB views, gantry command motion, Stop and Reset inspected | Broader scene runtime coverage; Demo 5 remains a manual-feedback command visualization |
| Operator controls | Native Run/Stop, normal conveyor Start/E-stop/Reset, action inputs and history; complete runtime/health rails now scroll at 1200x675 and 1600x900 | E-stop/reset across other applicable scenes |
| Conveyor/pusher/tank plant execution | Pusher repeated transfers, stroke/sensor feedback, Stop and Reset; native tank fill/drain, level/analog feedback, Stop hold and Reset through File/Open. Plant regression passes 19 checks; model matches eight Python traces / 83 snapshots | Other scene runtime coverage |
| Ladder editor | Native drag insertion/Undo, block browsing, Save/Open, invalid drafts, retained execution, multi-scene close guards, watch controls, tag edit/deletion guards, interface validation/Undo and Instruction Help verified; rendered interaction verifier passed | Crash/power-loss recovery; broader instruction/application acceptance |
| Scene/workspace authoring | Native placement, numeric transform, Undo/Redo, authored mapping, Save/Open and guards verified. Cyclic hierarchy formerly hung validation; now rejected promptly while preserving the current native workspace | Complete runtime behavior for all authored asset/mapping combinations |
| Layout/camera | Split regressions and native resize/points/browser/scrollable rails/forms inspected at 1200x675 and 1600x900; bounded dropdowns and readable tag/block forms | Broader scene visual acceptance |
| External execution boundary | 16 offline bridge/contract tests; 16 fake Python tests; fake full-app exchange/playback regression and native Run/Stop/Reset; profile guards, exclusive source, atomic output | Two supplied profiles only; file editing while disconnected, renewed verification and manual Connect; live commissioning/cadence unverified |
| Python canonical interface / legacy tools | 129 root tests, 16 fake live/diagnostic tests, 69 selected legacy Python tests, 28 Node tests and vendor metadata test pass. Reviewed existing heartbeat/transport patches and repaired stale portable hash manifest | Retained Qt GUI/installer not executed. 31 migrated accessory scenes explicitly unsupported by the legacy renderer |
| Shutdown/resource lifecycle | Orphan Studio block selector repaired; rendered checks/native launch-close complete; 16 offline connection lifecycle/contract tests pass, including hung process and stale-session recovery | Longer endurance/resource testing |

## Specific open issues

- Unsaved ladder drafts/history survive scene changes; New/Open and close
  now guard unsaved work. Crash/power-loss recovery remains unimplemented.
- Non-demo labs open as blank exercises with matching typed scene tags. One
  catalog I/O type is unsupported by the offline controller and is reported.
  Complete lab reference programs and full workflow coverage are not supplied.
- External playback/readiness now follows the existing native/reference
  binding; offline full-app and native controls verified. Automatic reconnect
  and an in-dialog endpoint/mapping editor are absent. No live communication
  has been verified.
- Demo 5 commands indicators and gantry XYZ motion. Feedback is manually set;
  it does not perform closed-loop carton placement. FB interfaces/DB views are
  declarations with shared tags, not independently instantiated PLC blocks.
- Workspace placements/groups/links now compare with a saved baseline and are
  protected on scene changes, Load, cross-scene ladder Open and close. Failed or
  cancelled Save prevents replacement. Crash/power-loss recovery remains open.

## Initial checkpoint results (historical)

- .NET build: zero warnings and errors.
- Controller unit/behavior suite: 139 passed, zero failed, no transport created.
- Canonical Python interface: 129 passed. Fake live/diagnostic suites: 16 passed.
- All 77 catalog files load; 71 have declared cases and pass; six have none.
- Godot app shell, cross-scene persistence, numeric scene I/O, stable operator
  controls, rendered ladder editor, and rendered workspace verifiers passed.
- Headless workspace gizmo failures were retested with a rendered viewport.
  Its remaining mapping assertion expected False after Run; corrected the
  fixture to require True after Run and False after Stop, and reran successfully.
- Native Windows screenshots inspected for launcher startup, Demo 5 Run/Stop,
  input changes, lost-permissive response, Save, add-network, Undo/Redo, normal
  conveyor Start failure, standalone editor, and unusable split view.

## Controller routing checkpoint

Restore tag `codex/controller-routing-baseline-20261003` preserves the prior
checkpoint. The current build has zero warnings/errors, 139 passing controller
tests, and passing rendered scene-control, virtual-controller UI, numeric-I/O,
and app-shell regressions. No PLC connection was attempted. The scene-control
regression includes a synthetic external output image; it is ownership proof,
not a PLC communication or hardware test. Shutdown resource leaks remain open.

Native Windows evidence covers normal Start/motion, E-stop/blocked Run/Reset,
source selection, rejected external local Start, and displayed event history.
Unmapped commands report rejection rather than silently forcing outputs. The
external command interface, transport readiness/cadence, and commissioning
requirements still need review. Next work is split/editor layout and framing,
then the remaining external bridge and whole-program workflows.

## Layout checkpoint

Restore tag `codex/layout-review-baseline-20261003` at `5f18105` preserves the
controller routing checkpoint. Build is clean. Split bounds/camera/columns,
point collapse, standalone points, and drawer-state regressions pass at
1200x675 and 1600x900. Rendered ladder editor, scene controls, workspace,
camera input, and app-shell regressions also pass. Native Windows inspection
covers minimum/default/maximized split views, resize reflow in both directions,
the instruction drawer, and the ladder Save dialog. This completes these layout
repairs, not whole-program acceptance. External transport and resource leaks
remain under review; no plant connection was attempted.

## External bridge checkpoint - 2026-10-04

Restore tag `codex/external-review-baseline-20261003` at `22e2dbb` precedes
these changes. Build is clean, controller tests pass 139/139, connection tests
pass 13/13, canonical Python tests pass 129/129, and fake live/diagnostic tests
pass 16/16. App-shell/profile guard, rendered scene-control/atomic image, and
rendered settings bounds regressions pass. Native inspection proves local
profile validation, mismatch display and usable controls at 1200x675; Connect
and the read-only hardware test were not invoked. Runtime scheduling uses a
minimum profile interval with one outstanding request; real cadence/readiness
remain unverified. Shutdown rendering/resource leaks remain open.

Run the new offline suites from `rungproof-next/`:

```powershell
.\.tools\dotnet\dotnet.exe run --project tests/Connections/RungProof.Next.Connections.Tests.csproj -- ..\build\.venv-rungproof\Scripts\python.exe
# Set DOTNET_ROOT and PATH as documented before launching Godot.
.\.tools\godot\Godot_v4.7.2-stable_mono_win64\Godot_v4.7.2-stable_mono_win64_console.exe --path . --resolution 1200x675 -- --verify-external-dialog --shell-scene=scene-1-conveyor-stop
```

Next work remains unsaved project/scene transitions, all demo native workflows,
external playback/reference semantics, and the rest of the review matrix.

## Scenario draft checkpoint - 2026-10-04

Restore tag `codex/project-persistence-baseline-20261004` at `49c5019`
preserves the external bridge checkpoint. Native Windows use reproduced loss
of an unsaved network and Undo history after Demo 3 -> Demo 1 -> Demo 3.
Scene loading reinstalled the authored template on every attachment. Each
scene now retains its exact in-memory draft, saved baseline/path, and separate
Undo/Redo history; selecting the current scene also preserves its project.
Cached drafts never have user bindings overwritten by template alignment.
This retains work during scenario navigation; it is not crash recovery or
automatic disk persistence. Explicit Save remains necessary before closing.

The app-shell regression failed before the fix and passes afterward, including
invalid draft contents, dirty state/path, isolation, Undo, Redo across another
round trip, and same-scene selection. Build has zero warnings/errors and the
rendered editor interaction regression passes. Native Windows inspection
confirms the third network, dirty marker, and Undo/Redo after the round trip.
The unrelated conveyor template assigned to non-demo labs and their Run path
remain under review, as do shutdown resource leaks and the rest of the matrix.

## Native demo / valid-event checkpoint - 2026-10-04

Restore tag `codex/lab-execution-baseline-20261004` at `a7d455d` precedes
these changes. Demo 4 counted invalid detections without type-valid or
count-request, so enabling permissives later could validate an old count.
The counter now sees a raw pallet-detection rising edge qualified by both
permissives. Regression failed before the fix (expected 0, actual 5) and now
passes for each missing-permissive combination, held detection, five valid
events, and loss of type-valid. Controller suite passes 139/139, build has
zero warnings/errors, and app-shell/draft regressions pass.

Native Windows checks cover Demo 1's lamp off through two rising edges and on
at three, Stop output removal and Reset; Demo 2's initial delay, subsequent
lamp activation and removal on request loss; Demo 3's package motion after
Start and stop at photoeye position 0.5; and corrected Demo 4's ignored invalid
event, output off through four valid events/on at five, and removal when the
type permissive drops. These are bounded user workflow checks, not complete
scene visual or hardware acceptance. Demo 4's shutter partly obscures its
equipment; broader visual and block-structure review remains open.

## Lab authoring / bounded drawers checkpoint - 2026-10-04

Restore tag `codex/lab-project-baseline-20261004` at `6ee9328` precedes
these changes. Non-demo scenes incorrectly opened the conveyor ladder and
could run hidden scene rules instead of the user's selected controller.
They now open blank exercise projects with PC-owned inputs and PLC-owned
outputs mapped to their actual BOOL/INT/DINT/REAL points. Unsupported types
are reported rather than coerced. The conveyor starter and five authored
demos retain their programs. Empty exercise Run and Verify + Load report
EDIT001; scene feedback alone cannot fabricate a PLC output without logic.

The exercise factory regression checks all 77 scenes, including owner/type
binding consistency and one reported unsupported type. Controller suite is
140/140; build has zero warnings/errors. App-shell/draft and rendered editor
interaction regressions pass. Native Lab 2.1 testing covers empty Run feedback,
adding a network/contact with the correct lamp coil, Run/scan monitoring,
input true/lamp on, input false/lamp off, Stop, and Save through the file
dialog. Saved JSON contains the matching scene ID, tags, contact, and coil;
the native tab title reflects its filename and clears the dirty marker.

Native use also exposed project/footer and diagnostics overlap under points.
Tag/block forms and inspector pages now scroll within their docks; the palette
compacts by height. A strengthened fresh-editor regression first failed with
all drawers open and now passes at 1200x675 and 1600x900 in both vendor views.
Native 1600x900 inspection confirms usable footer, diagnostics, and routine.
This checkpoint does not complete the review matrix or prove physical PLC I/O.

## Draft validation / loaded controller checkpoint - 2026-10-04

Restore tag `codex/validation-state-baseline-20261004` at `1e5b22b`
precedes this fix. Native loading of a readable draft with an undeclared
contact retained the good runtime in Main but erased its shell program and
snapshot, falsely displaying Stopped/program not running. Validation now
retains the loaded program/snapshot, reports draft errors in the editor's
Error List, and suppresses monitoring of the mismatched edited ladder.
Toolbar/footer execution and scans continue to reflect the loaded controller.
Programmatic control refresh no longer emits a spurious user-edit warning.

The rendered persistence regression now starts with a valid running program
and requires its identity, running snapshot/scan, cycle status, cleared stale
monitoring, and draft errors after invalid Open. It passes alongside the
complete rendered editor interaction and app-shell/draft regressions; build
is clean. Native Windows testing confirms cross-scene Open from Demo 1 to the
saved Lab 2.1 project, Run, invalid draft Open, retained advancing scans,
and correct lamp response from the previous good program. Unsaved replacement
and exit prompts, resource cleanup, and remaining review areas stay open.

## Unsaved replacement / close checkpoint - 2026-10-04

Restore tag `codex/unsaved-work-baseline-20261004` at `433454f` precedes
this fix. New/Open require Save, Discard, or Cancel for the current dirty
ladder; close checks the current and all cached scene drafts. Cancel is the
default focus. Save prompts for each queued project and blocks the pending
action until every write succeeds. Saving cached drafts never attaches their
scene or controller. Cancelling a later Save keeps earlier saves and leaves
the remaining drafts protected. Writes complete in a temporary file before
replacing an existing project, avoiding truncation during a failed write.

Build is clean. App-shell regression verifies all-scene detection, Cancel,
failed Save preventing continuation, waiting for all saves, matching saved
contents/source IDs, and Discard. Rendered editor regression verifies the
New guard's Cancel and Discard branches. Native Windows checks cover close
Cancel, two-scene detection, sequential Save dialogs, and cancelling the
second Save; the next close lists only the remaining cached draft. Saving
that final draft produced the correct scene JSON and the review process exited.
Crash recovery is outside this repair and remains absent.

## Shutdown ownership checkpoint - 2026-10-04

Restore tag `codex/shutdown-review-baseline-20261004` at `aaf2f8d`
precedes this fix. After pending scene frees settled, orphan diagnostics
identified an unparented Studio `BlockTypeSelector` and its popup subtree.
It retained the viewport, canvas, themes, fonts, and textures reported at exit.
The hidden Studio selector is now owned by its workbench, as in TIA. Before
the fix the diagnostic run listed 14 stray nodes and shutdown leaks; afterward
it lists none and exits without RID/ObjectDB leak reports. Rendered editor and
1200x675 split regressions also pass and exit without those reports. Normal
batch-file startup and native window close were inspected; the process exits.

Build has zero warnings/errors; controller suite passes 140/140 and offline
connection/process suite 13/13. Save-failure feedback hides its file dialog
before showing the error guard, preventing competing exclusive windows.
Unsaved-dialog text is bounded and abbreviates long scene lists, with Cancel
focused by default. Longer native authoring and the rest of the matrix remain
under review. No physical PLC connection was attempted.

For settled orphan diagnostics, append `--trace-orphans` to `--verify-app-shell`.
Inspect its output for `Stray Node`, `leaked`, or `RID allocations`.

## External playback checkpoint - 2026-10-04

Restore tag `codex/external-playback-baseline-20261004` at `4157d6b`
precedes this fix. The full-app offline bridge reproduced movement immediately
after Connect, before Run. Main advanced plant physics on every connected frame,
the equipment controllers independently animated, and the PLC readiness bits
were not used to gate the returned output image. Run/Stop/Reset had incorrectly
been treated as PLC commands rather than plant playback controls.

Readiness now matches `prototype/src/livePlcBinding.js` and the legacy native
runtime: healthy exchange, simulation enabled, communication OK, and no PLC
timeout. Connect, Stop, Reset, readiness loss, and disconnect leave playback
paused; recovery never resumes automatically. Connected exchange continues
while paused. Reset restores the plant without replacing its last PLC command
image. Unready output images are not applied. Equipment physics is frozen with
the plant; no PLC RUN/STOP/reset command or output write was introduced.
Momentary PC feedback remains set until an accepted exchange samples it, then
clears independently of plant playback. Scene changes also cancel pending
connections so a late connect cannot attach to another scene.

The offline full-app regression passes connection without motion, Run motion,
Stop holding package/equipment while cycles continue, paused Reset, readiness
loss and output rejection, blocked Run, recovery requiring new Run, disconnect,
and sampled pulse handling. The connection suite passes 16/16, including all
eight PLC status-bit combinations, unhealthy/incomplete readback and new-session
behavior. Controller suite remains 140/140; build has zero warnings/errors.
Rendered scene-control and app-shell/orphan regressions pass without leaks.
The headless scene-control ray-pick check requires a rendered viewport and was
rerun there successfully; headless popup placement is not layout evidence.

Native Windows mouse tests exercised the offline connected scene's Run, Stop,
and Reset. Screenshots showed motion, frozen playback, advancing exchange
counts and retained PLC output. External source/playing/paused/readiness/cycle
labels now report actual state; the footer no longer says LOCAL ONLY during
external mode. REAL values use six significant figures for display without
changing the runtime values. Final native error log is empty and the process
exits on close. No physical PLC adapter or network was used by the fixture.

Run `--verify-external-playback` for the offline regression. Add
`--keep-playback-review-open` to inspect its fake connected scene with native
controls; this flag only applies to that verifier and never selects real PLC
transport. Logs are under `rungproof-next/.tools/external-playback-*` and
`native-external-playback-*`.

## Continuous plant execution checkpoint - 2026-10-04

Restore tag `codex/scene-motion-baseline-20261004` at `3bff1d9` precedes
this fix. The full-app execution test reproduced Scene 2's package/photoeye,
pusher stroke/limits, and transfer count remaining unchanged under actual
ladder scans. The `conveyorPusher` runtime had no update implementation. Tank
outputs likewise failed to move the level because a separate local Run flag
was never set by the selected ladder controller.

The conveyor/photoeye/pusher plant now follows the existing canonical Python
components and native reload policy. Physics produces PC-owned feedback from
the commanded motion; it never writes PLC-owned commands or executes hidden
PLC logic. Transfer requires a package at the photoeye crossing the declared
stroke threshold. Reload waits for the delay and retracted limit. Photoeye
sweep/hold handles crossing between steps, discharge counts once, and the
package is hidden after discharge. Selected-controller execution now gates
plant/equipment playback; Stop holds the plant, and Reset restores its model.
Tank motion uses the selected playback state instead of the unused local flag.

`--verify-plant-motion` passes actual ladder scan feedback, repeated pusher
transfers, a Stop during partial stroke, Reset, the tank's declared 7 percent/s
fill and 4.5 percent/s drain, 4-20 mA feedback, high/low limits, saturation,
Stop and Reset. The pure model matches eight independent canonical Python
traces (83 snapshots), including swept photoeye, hold decay, partial stroke,
off-station extension, and counted discharge. The stored trace records its
source SHA-256; tests reject a stale source. Invalid elapsed time is rejected.
Run the suite with `dotnet run --project tests/Plant/RungProof.Next.Plant.Tests.csproj`.

Build is clean; 140 controller tests, numeric I/O, rendered scene controls,
app-shell/orphan checks, and external playback regression pass. All 77 scenes
were rerun: 71 have passing declared cases, and these six have no cases:
conveyor-cell, equipment-gallery, scene-1-conveyor-stop,
scene-2-conveyor-pusher, tank-high-low, tank-radar. Loading them is not motion
acceptance. The new motion checks cover previously untested execution paths.

Native Windows inspection of the new pusher/tank visuals and normal file
loading is pending: a Windows update overlay currently blocks native input.
The normal launcher was opened, but the tool cannot target the system overlay.
No visual acceptance is claimed for this checkpoint. Review fixtures are
generated under `.tools/plant-review-scene2.rpproj.json` and
`.tools/plant-review-tank.rpproj.json` for subsequent native File/Open testing.
The review goal remains active and no PLC connection was attempted.

## Workspace write checkpoint - 2026-10-04

Restore tag `codex/workspace-review-baseline-20261004` at `84714d7`
precedes this fix. Workspace saves previously wrote over the destination
directly. They now finish a temporary file in the destination directory and
replace the saved workspace only after that write completes, for both absolute
and Godot user paths. The rendered workspace regression passes its existing
group, hierarchy, mapping, transform, Undo/Redo and Save/Load assertions.
A Windows exclusive-reader failure check also passes: the original saved JSON
survives failed replacement, the temporary file is removed, and retry succeeds.
Build is clean; log: `.tools/workspace-atomic-final.log`.

Remaining work: preserve/protect unsaved workspace changes at scene replacement,
workspace Load and close, and compare Undo state against the saved document.
Keep cross-scene ladder Open synchronous until attachment is complete; inserting
an asynchronous guard only in Main's SceneRequested callback would restore the
ladder into the old scene before attachment and reintroduce the earlier bug.
Native inspection remains pending behind the Windows update overlay.

## Workspace baseline checkpoint - 2026-10-04

Restore tag `codex/workspace-drafts-baseline-20261004` at `d4394c9`
precedes this fix. The rendered workspace regression reproduced UNSAVED
remaining set after Undo returned to the empty baseline. Dirty-state updates
now compare the current workspace document against its baseline from scene
attachment, successful Save or successful Load. Undo/Redo therefore report the
actual state; a failed Save never advances the baseline. This also avoids
marking a workspace dirty for scene controls whose values are not stored in
workspace files.

Build and the complete rendered workspace regression pass, including edits,
Undo to the original baseline, Redo, Save of a nonempty workspace, another
edit, Undo to that saved baseline, and Redo. The atomic replacement test still
passes. Logs: `.tools/workspace-dirty-before.log` and
`.tools/workspace-dirty-final.log`. Native manual inspection remains pending.
Next repair: scene replacement, workspace Load and close must consume this
accurate dirty state without breaking cross-scene ladder attachment ordering.

## Workspace replacement checkpoint - 2026-10-04

Restore tag `codex/workspace-guards-baseline-20261004` at `ca9af4b`
precedes this fix. Unsaved workspace edits now require Save, Discard, or Cancel
before scene replacement, workspace Open/Load, cross-scene ladder Open, and
window close. Save cancellation/failure retains the current document and blocks
continuation; successful Save resumes the pending operation. Discard authorizes
only that operation without falsely marking the current workspace saved. Close
then checks current/cached ladder drafts. Cross-scene ladder Open queues the
whole open and preserves attach-before-restore ordering. Scenario selection
tracks the actual active scene when replacement is queued or loaded from a file.

Build, rendered workspace replacement/dirty/atomic-write regression, and rendered
ladder editor regression pass. The injected denied replacement intentionally
logs WORKSPACE_SAVE_FAILED; it verifies preservation and successful retry.
Logs: `.tools/workspace-guards-final.log`, `.tools/workspace-guards-ladder.log`.
Native Windows launch and File/Open loaded the pusher and tank review projects.
Pusher package advance, extended cylinder/transfer, repeated cycles, Stop hold,
and Reset were inspected; tank fill, 42-percent/10.72-mA reset state, full-level
20-mA feedback, indicators and Stop hold were inspected. This is offline visual
simulation evidence, not live-machine or physical geometry acceptance.

Native asset search/selection/placement, Undo/Redo header state, close Cancel,
scene-change Save, and saved workspace File/Open round trip were also inspected.
The bounded guard dialog defaults to Cancel. The own review file is
`.tools/native-workspace-guard-20261004.rungproof.json`; it contains one sensor
placement in tank-level. The Windows overlay has cleared. Remaining visual
issues found here: the operator rail clips runtime/navigation on the tank, and
Undo to an empty workspace leaves a stale gizmo/selection inspector. Next fixes
will address those observed issues. Whole-program review goal remains active.

## Operator rail and Undo selection checkpoint - 2026-10-04

Restore tag `codex/operator-review-baseline-20261004` at `dc8f54d`
precedes these fixes. The operator and PLC-health rails now scroll their whole
content; runtime, equipment and health text fit their content, while the bounded
event history keeps its own scrolling. This prevents long descriptions/action
lists from reducing runtime and health text to a few clipped pixels. Native
1600x900 and 1200x675 inspection confirmed runtime details and both navigation
buttons can be reached; the narrow window also exposes the complete PLC-health
summary by scrolling. The Engineering button was exercised from the scrolled
operator rail.

Undo to an empty workspace now detaches its transform gizmo and replaces stale
placement inspector text with the current scene summary. The prior failure was
reproduced in `.tools/workspace-selection-before.log`; the corrected rendered
workspace test and native place/Undo workflow both confirm it. Scenario list
selection also tracks the actual loaded scene after file Open or guarded changes.

Build, workspace replacement/dirty/write/transform tests, app-shell/orphan and
split-view tests pass. Controller suite remains 140/140; the full-app controller
UI verifier passes its stable actions, stop/reset, monitor and force assertions.
Native sessions closed normally with no ERROR or leak reports. Logs include
`.tools/operator-workspace-final.log`, `.tools/operator-shell-final.log`,
`.tools/operator-split-final.log`, `.tools/operator-native-final.log`, and
`.tools/operator-native-narrow-final.log`. Whole-program review remains active;
remaining editor interactions, demo presentation/sequence boundaries, external
profiles, installation/export and legacy-path conflicts still need review.

## Editor browsing and contrast checkpoint - 2026-10-04

Restore tag `codex/editor-review-baseline-20261004` at `aca9e3f` precedes
these fixes. Selecting another block previously marked the project unsaved and
caused an unnecessary close prompt. Dirty comparison now excludes navigation
while saved files still retain the selected block. Real network edits and
cached drafts still require Save/Discard/Cancel. The controller suite passes
141/141, including every Demo 5 block, saved navigation and actual edits.

Native drag insertion at an FB wire and Undo were exercised. FB, FC and DB
pages were inspected; selecting/hovering rows now keeps readable text and
backgrounds. The shared selection styles cover project, instruction, interface,
tag, watch, validation and search browsers. The interface summary stays bounded
and scrollable, and explicitly identifies declarations/shared project tags.
Offline parameter passing and per-instance FB storage remain unimplemented;
the UI must not imply those declarations execute as real Siemens interfaces.

Build (zero warnings/errors), rendered ladder interaction and split/layout
checks pass. Logs: `.tools/editor-review-controller.log`,
`.tools/editor-review-rendered.log`, `.tools/editor-review-split.log`, and
`.tools/editor-review-native.log`. Native clean block browsing closes without a
false save prompt. Whole-program review remains active.

## Authored demo sequence and first Run checkpoint - 2026-10-04

Restore tag `codex/demo-sequence-review-baseline-20261004` at `5cc5dff`
precedes these fixes. Native testing found that setting scene inputs before the
first Run lost them when loading the controller reset the plant. Initial Run
now preserves current feedback; explicit Reset and explicit program loading
retain their reset behavior. Native inputs-before-Run and the rendered plant
regression both confirm the correction.

Demo 4's advertised block program previously had only its main block and an
unused timer. Its existing qualified counter and immediate completion output
now execute in a counter FB and validation FC, called each scan. Existing
invalid-event and threshold behavior still passes.

Demo 5 now demonstrates comparisons, a meaningful parallel actuator-status
branch and two populated DB declaration views in addition to its two FBs,
two FCs, timer, counter and arithmetic. Its completed four-pick layer removes
pick commands and cannot accept a fifth pick until Reset. Held carton feedback
counts once; completed-layer arithmetic increments once. Native four-carton
input sequence showed layer_complete=True and both commands=False; native
FB comparison monitoring and DB declarations were inspected. The watch dock
can be resized; its per-scan row recreation needs further review.

The XYZ gantry now follows gantry_cycle while playback runs, holds on Stop or
loss of command, and resets its authored pose. The three delivered sibling KIN
nodes move together; Z travel stays within the solid-rod/carriage overlap.
The shutter-shaped coordinate-sensor substitute in this scene was replaced
by a sensor pair and overlapping equipment was spaced to expose the gantry.
The scene/help now state the actual manual-feedback/command-visualization
boundary: this is not a closed-loop carton placement model or real FB/DB
instance execution. Other generic accessory substitutions remain under review.

Build is clean; controller suite passes 142/142; app-shell, cached-draft/unsaved
guards, profile guards and settled orphan checks pass; plant regression passes
19 checks. Native first Run, gantry motion, Stop hold, Reset pose, four-pick
completion, watch resizing and comparison/DB views were inspected. Logs:
`.tools/demo-sequence-controller-final.log`, `.tools/demo-sequence-shell-final.log`,
`.tools/demo-sequence-plant-final.log`, and
`.tools/demo-sequence-native-acceptance.log`. Goal remains active.

## Watch stability and saved metadata checkpoint - 2026-10-04

Restore tag `codex/watch-review-baseline-20261004` at `bd99654` precedes
these fixes. Every scan recreated watch rows and symbol-menu items, losing
selection and disrupting Remove or an open picker. Controls now retain identity
until symbols or membership change; scans update values in place. The rendered
regression failed before the change and now passes selection/value checks.

Watch edits also left the unsaved marker and toolbar Undo stale. Both editor
views now refresh saved-metadata state without invalidating the executing
controller. The regression verifies Clear/Undo, both titles and retained
monitoring. Native Windows Remove and Clear updated the marker and enabled
Undo; toolbar Undo in TIA and Studio 5000 restored the clean baseline while
scans continued. Earlier native testing also retained an open picker across
scans and added a symbol successfully. Native sessions closed cleanly.

Build has zero warnings/errors; rendered ladder interaction passes. Logs:
`.tools/watch-stability-before.log`, `.tools/watch-stability-final.log`,
`.tools/watch-native-final.log`, `.tools/watch-controls-native-final.log`.
Whole-program review remains active.

## Fresh-source startup checkpoint - 2026-10-04

Restore tag `codex/startup-review-baseline-20261004` at `218bbc1` precedes
this fix. An isolated copy of all tracked Next files, without `.godot` or
NuGet object files, reproduced launcher failure NETSDK1004. The launcher used
`--no-restore` and also omitted asset import. It now restores during build,
then invokes the matching Godot console's headless import before opening the
native player. Failure stops startup; missing Godot, .NET and console paths
were individually checked and returned exit code 1.

The source copy reused only the pinned portable tools through a junction; it
did not copy generated caches or alter the canonical import cache. Its build
had zero warnings/errors, imported 900 resources, and rendered the actual
Windows conveyor scene. Normal Run and the operator Start produced conveyor
motion and photoeye feedback; native close completed. App-shell and cached-draft
guards pass in the copy. Headless popup positioning produces expected display
errors in guard-dialog checks; the native player has no such startup errors.
Evidence: `rungproof/build/cold-start-review-20261004/launch-review.log` and
`cold-shell-review.log`. The isolated review copy is ignored, not a release.

Setup and README now describe the actual launcher, current catalog and guarded
bridge. No export preset/standalone installer exists; offline source execution
is the supported entry point. External mode needs the parent Python bridge and
profiles. These packaging gaps are recorded rather than claimed verified.

## Editor mutation boundary checkpoint - 2026-10-04

Restore tag `codex/editor-mutation-review-baseline-20261004` at `ad8ec7e`
precedes these fixes. A first timer Reset created its timer tag before recording
history, so Undo left an unwanted tag. History now precedes both mutations.
Invalid initial values and duplicate interface parameters previously recorded
an empty Undo entry and invalidated the loaded monitor. They now reject before
edit state changes. The rendered regression reproduced all three failures,
then passed exact timer-Reset Undo, retained rejected-edit monitoring and a
single Undo of an accepted parameter after duplicate rejection.

Native Demo 4 main/FB/FC monitoring was inspected. The declaration form rejected
an invalid BOOL while retaining live highlights, accepted a valid parameter,
rejected its duplicate and restored the clean/monitored document with one
toolbar Undo. Native timer Reset and Undo restored the original monitored rung
and clean title. Session closed cleanly. Build has zero warnings/errors and
rendered ladder interaction passes; logs `.tools/editor-mutation-before.log`,
`.tools/editor-mutation-final.log`, `.tools/editor-mutation-native-final.log`.
Native form inspection found weak label contrast and fields requiring excessive
dock width; this is the next layout repair. An invalid review CLI scene ID also
revealed startup left half initialized instead of rejecting/falling back.

## Native editor form checkpoint - 2026-10-04

Restore tag `codex/editor-form-review-baseline-20261004` at `9ae608f` precedes
these fixes. Native tag/object pages inherited a gray tab surface with dark
labels, and horizontal command/parameter rows clipped controls at default
dock width. A light tab surface now matches the tree; flow containers wrap
block/task/tag commands and declaration fields. Symbol binding text clips
inside its dropdown, and the vendor-boundary note has readable dark text.
Successful declaration insertion replaces any prior form-error message.

Native 1600x900 and minimum 1200x675 forms were inspected. All declaration
fields and commands fit the default dock with vertical scrolling. Native
rename/initial BOOL edit applied, deleting the referenced tag was blocked,
and toolbar Undo restored its original name/value and clean title. Build is
clean, rendered ladder interaction passes, and native sessions close cleanly.
Logs `.tools/editor-form-final.log`, `.tools/editor-form-native.log`,
`.tools/editor-form-native-narrow.log`. No live PLC action was taken.

## Invalid startup scene checkpoint - 2026-10-04

Restore tag `codex/startup-input-review-baseline-20261004` at `3a99bd2`
precedes this fix. An unknown `--shell-scene` threw during `_Ready`, leaving a
half-built native shell on Loading project. Startup now verifies the ID against
the catalog, loads the default on a stale/invalid argument and reports the
reason in status/Event History. The invalid-ID app-shell regression passes;
native launch rendered the default scene with the recovery event and functional
menus/editor. Build is clean and native close succeeds. Logs:
`.tools/startup-invalid-scene-final.log`, `.tools/startup-recovery-native.log`.
Native Instruction Help testing then exposed a separate hidden-dock issue;
its menu changed tab content without revealing the dock.

## Instruction Help checkpoint - 2026-10-04

Restore tag `codex/help-review-baseline-20261004` at `10bf159` precedes this
fix. Instruction Help changed the selected tab while its dock remained hidden.
All explicit Help-open paths now use the shared dock-opening function. The
rendered regression first failed with a collapsed dock, then passed for the
button and menu paths. Native View > Instruction Help opened the dock; selecting
TON and scrolling exposed its parameters, scan behavior and offline boundary.
Build is clean and the native session closes cleanly. Logs:
`.tools/help-dock-before.log`, `.tools/help-dock-final.log`,
`.tools/help-dock-native.log`.

## Workspace file and native authoring checkpoint - 2026-10-04

Restore tag `codex/workspace-file-review-baseline-20261004` at `07a8302`
precedes these fixes. A malformed descendant listed before a cyclic parent
pair caused validation to loop forever. Validation now tracks every ancestor
and rejects any repeat. The regression stalled at the cyclic hierarchy before
the fix, then rejected it promptly and passed the complete workspace verifier.
Native File > Open rejected the cyclic file with a parent-cycle message and
retained the current sensor placement and mapping; the window remained usable.

Native sensor placement, numeric X edit, Undo/Redo, authored-only mapping,
Save on close and Open restored the exact transform and mapping. Long dropdown
labels had pushed the Connections form past the right edge; clipped text now
keeps selectors and commands inside the dock, inspected in the native window.
Build and rendered HUD/workspace checks pass; native close is clean. Logs:
`.tools/workspace-cycle-before.log`, `.tools/workspace-cycle-final.log`,
`.tools/workspace-native-final.log`, `.tools/workspace-file-native.log`.

Root and application READMEs now direct current Windows users to the Godot
launcher and label the retained Qt pilot explicitly. External settings select
the two supplied profiles; endpoint/mapping changes require disconnected file
editing and renewed verification. Automatic reconnect and an in-dialog profile
editor are absent. Existing fake reconnect/stale-session tests pass; live
cadence and commissioning remain unverified.

## Legacy migration and final regression checkpoint - 2026-10-04

Restore tag `codex/legacy-manifest-review-baseline-20261004` at `4cbef9a`
precedes these repairs. Vendor verification rejected four existing heartbeat/
runtime/update-loop/transport patches; its older hashes also depended on CRLF
checkout bytes. The patches were compared with the canonical interface and
existing exact-heartbeat/timeout regressions passed. No adapter implementation
was changed. The manifest now hashes canonical LF bytes; a new fixture proves
both LF/CRLF acceptance and rejection of code changes or inventory drift.

Legacy scene tests still assumed a 32-scene catalog. All 77 current entries are
now classified: 46 are compatible with the retained schema; 31 catalog accessory
scenes explicitly reject because that renderer has no implementation. Node
ownership checks exercise all 39 compatible labs and assert rejection of those
31 scenes. A fresh checkout's absent, generated saved-scenes directory is
treated as empty; other I/O errors still fail. This preserves strict validation
instead of suggesting unsupported assets can run in the old renderer.

Native File/Open loaded the separate tank drain ladder. Run lowered level and
analog feedback together (42 / 10.72 to 40.11 / 10.4176, eventually 0 / 4).
Stop closed the valve and held a nonempty level at 41.01 / 10.5616 across later
observations. Reset restored 42 / 10.72, false outputs and stopped scan zero.
The visible sight level moved consistently; native close was clean. Evidence:
`.tools/tank-drain-native-final.log` and the inspected native Windows frames.

Final automated results:

- Controller 142 passed; offline connection/contract tests 16 passed.
- Plant reference: eight cases, 83 matching snapshots; plant motion 19 checks.
- Canonical Python 129 passed; fake live/read-only Python 16 passed.
- Selected legacy Python 69 passed; Node 28 passed; vendor metadata one passed.
- Scene cases: 71 passed, zero failed; all 77 load, six have no declared cases.
- Rendered app-shell, ladder interaction, split, scene controls, offline external
  playback and plant motion all pass against the final application code.
- No rendered error/leak reports; app-shell's deliberately absent last-workspace
  fixture reports its expected handled warning.

Logs are under `rungproof-next/.tools`: `final-controller.log`,
`final-connections.log`, `final-plant-reference.log`, `final-root-python.log`,
`final-fake-python.log`, `final-legacy-python.log`, `final-legacy-node.log`,
`final-vendor-metadata.log`, `final-scene-contracts.log` and
`review-final-{app-shell,ladder-editor,split-view,scene-controls,external-playback,plant-motion}.log`.
These results complete the bounded review/repair pass, not release acceptance
or implementation of every capability listed in the current review matrix.

The final normal `.cmd` launch restored/built with zero warnings/errors,
imported assets without error and opened the native Windows application.
Scenario > Scenario Browser selected Demo 5; toggling carton-at-pick, gantry-home
and pallet-position-valid before Run retained those inputs and produced both
vacuum and gantry commands. Stop cleared outputs; Reset restored its initial
pose/inputs and stopped scan zero. The normal app was left open at this reset
Demo 5 state. Launcher log: `.tools/review-final-normal-launch.log`.

## Verification boundary

Native mouse/keyboard interaction proves only the inspected Windows workflows.
Headless declared scene cases prove only the stated cases, not full user
acceptance. Fake adapters and offline programs never prove live PLC behavior.
Live commissioning remains subject to the repository's approved CPU/profile,
exact write scope, network authorization, and direct machine observation.

Drive-alarm scene: three incorrectly inherited models replaced by original supported training props, stale reviews/references archived or removed, operator face labels corrected and five native views inspected. Close review caught and repaired a mast outside its base and hidden keypad buttons. It remains a Boolean exercise with static text legends; no fieldbus/string parsing or supplied controller. Normal Run was retested and still opens NO CONTROLLER LOADED. Seven added checks cover floor, separate equipment, mast support, identity, plates and symbolic alarm true/reset projection. Current evidence is drive-alarm-*.log; 38 focused geometry, 19 plant, rendered controls and 71 authored cases pass. Goal active; 68 native scene inspections remain.
