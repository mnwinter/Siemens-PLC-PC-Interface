# Multi-angle scene review - 2026-10-04

Status: **active**. The prior software review did not establish multi-angle
visual acceptance. Fourteen scenes have five-view native static inspections; 63 remain pending.
Demo 5, Powder Batch Mixer, Parcel Size Sorter, Conveyor Inspection Cell,
the Equipment Gallery and Drive Alarm-Code String have repaired layouts.
The sorter operator Run still lacks a controller; three simple panels have clear spacing but incorrect START plates. Other scenes
remain pending unless their row explicitly records observation. Inspection coverage
includes failed scenes; it is not a count of accepted scenes.

## Acceptance method

Use the native Windows Godot application and the opt-in `--visual-scene-review`
bar. Inspect front-right, front-left, rear-left, rear-right and overhead views.
Use close views where occlusion hides a support, workpiece or moving attachment.
Check workpiece support, post/beam clearance, equipment identity, floor contact
and relevant motion extremes. Run/Stop/Reset and permissive transitions require
separate behavior evidence. A camera log is evidence of navigation, not a
substitute for inspecting its screenshot. Do not silently pass obscured details.

The bounds inventory uses actual imported visible meshes after world transforms,
not catalog dimensions. Its column counts intersecting mesh AABBs between
separate equipment, with more than 5 mm overlap on each axis. Curved/rotated
meshes and intentional connections can create false positives. Zero candidates
also does not prove proper support, equipment identity, or moving clearance.
43 of 77 scenes have positive counts after the mixer, tank and conveyor sizing repairs.
Every row requires native inspection.

## Repairs and open findings

- Demo 5: pallet now centered between four posts on the base slab; carton rests
  inside the conveyor deck footprint; robot clears the shortened conveyor;
  coordinate-sensor foot clears the separate gripper model. The gantry tool now
  follows its Z axis through the XYZ sweep, Stop and Reset. All seven focused
  geometry checks pass. Native static five-view inspection is complete. Motion
  was observed from front-left and rear-right, including Stop/Reset. No real
  carton transfer or automatic home/pick feedback is implemented.
  Conveyor width/deck sizing is now honored by the shared composer, with model
  sizing isolated from equipment scale. Demo 5 explicitly retains its reviewed
  1.055 m deck height; its five static views were rechecked after this change.
  Other conveyor scenes still need native support/clearance checks.
- Powder Batch Mixer: the intersecting tanks and motor/hopper interference are
  repaired. Tank diameter/height now size the actual cylindrical shell (2.6 m /
  2.5 m here), with equipment scale applied separately. A copied roller-shutter
  previously labeled as a powder chute is replaced by an original static open
  channel; its inherited door approval/reference is removed and the old review
  is archived. The builder checks that cross-support corners stay below the
  channel. Family registration rejects zero/tied matches and preserves existing
  authored packages. Native five-view reinspection covers spacing, floor contact
  and channel clearance, including close/overhead views where rear tanks occlude
  details. The scene remains a symbolic batch exercise, with manual feedback and
  PLC-driven indicators; no actual powder transfer, weighing, mixer process or
  supplied batch reference ladder is proven.
- Tank resizing exposed radar feedback that ignored parent scale. It now uses
  the world-space liquid surface, and Reset projects the restored tank feedback.
  The focused scaled-radar case passes; other tank scenes still need native review.
- Workstation Call, Dual Confirmation and Service Marker inspections find clear supports/spacing
  but generic START plates on call/confirmation buttons. This shared label issue
  remains open. Global help validation also fails at Count Display's inherited
  door-axis metadata (`KIN_bottom_bar`); do not regenerate help to legitimize that
  identity without checking its actual model.
- Whole-shell startup: the inventory reproduced REAL initial `0` arriving as a
  long in the editor. The catalog test previously decoded it as double instead
  of following the plant reader. The test now reproduces the actual boundary
  and failed before normalization in `SceneLadderProject`. All 142 tests pass
  after the fix, and the shell inventory completes for all 77 scenes.
- Parcel Size Sorter: repaired the overlapping tables/belts and cartons. Two
  fixture-free flat table variants, five conveyors (including a new bridge),
  grounded feet and common 1.055 m surfaces provide the declared three-way path.
  Indexing uses 0/45/90 degrees with explicit dwell; cartons yaw with the index.
  The sweep found a header collision and Reset leaving carton rotations behind.
  Both are repaired. Close native views then found the lowest beam below the
  belt; configured optical heights now position housings/lenses/beams together
  at 1.30/1.65/2.05 m, above the belt and between the three carton top heights.
  Five full-scene static views and five final portal detail views were inspected,
  with the secondary table junction inspected overhead and from front-right.
  Native plant motion was observed from front-left and rear-right. Stop held
  after two routes; Reset restored initial poses; the second pass completed
  count=3/cycle_complete=true with cartons on distinct takeaways, then Reset.
  The 46 s sampled geometry check uses bottom contact samples and a center-support
  hull plus oriented mesh boxes to screen solid interference. It does not prove
  friction, dynamics, stability, throughput, triangulated collision or real sensor
  response. Queue holding and feedback remain scripted in this plant preview.
  Normal shell Run was also tried: it opens a blank editor with NO CONTROLLER
  LOADED. No supplied sorter reference ladder exists. That operator workflow
  remains open; the explicitly labeled plant preview does not pass it.

- Conveyor Inspection Cell: cartons were 90 mm above the now-correct belt;
  they now rest at its 0.9 m deck. Photoeye feet are grounded and stand span is
  2.6 m, clearing the conveyor frame and pull-cord hardware. The shared photoeye
  composer translates complete stands instead of stretching heads/cables, and
  uses the actual authored 0.92 m post height when raising the optical axis.
  The beam now follows photoeye_blocked. Five final native views include close
  support/clearance views and a complete overhead footprint. Normal shell Run,
  machine Start, moving front-left/rear-right views, Stop hold and Reset were
  inspected. Simulated E-stop set estop_ok=false/conveyor_run=false and stopped;
  Run was blocked until explicit reset, and reset required a new machine Start.
  This is simplified position feedback and teleporting recirculation, not a
  physical return conveyor, optical sensing or safety verification. Remaining
  cable AABB flags are screening candidates; solid-part oriented boxes are clear.
- Equipment Gallery: two fitting-origin sensor models extended below the floor,
  the transmitter crossed a pipe flange, and pipe/valve supports floated. The
  instruments now have opt-in illustrative display stands and clear probe tips;
  the transmitter is separated from the pipe. Existing pipe/valve supports are
  grounded; unused pipe sizing claims were removed. Five final native views and
  close transmitter/fork views show the repaired static layout. Normal Run opens
  a blank editor with NO CONTROLLER LOADED. The animation workflow remains open;
  no preview or static checks count as passing it.

## Evidence

Local ignored logs under `rungproof-next/.tools/`:
`scene-geometry-before.log`, `scene-static-clearance-before.log`,
`scene-geometry-final.log`, `multi-angle-native-review.log`,
`multi-angle-native-final.log`, `scene-real-initial-before.log`,
`scene-real-initial-after.log`, `all-scene-geometry-inventory.log`,
`multi-angle-native-parcel.log`, `geometry-review-shell-final.log`.
Build: zero warnings/errors. Controller: 142 pass / 0 fail. Existing plant:
19 checks pass. Thirty-eight focused geometry checks pass (seven Demo 5, four mixer,
nine parcel, six inspection conveyor, four gallery, seven drive alarm, one scaled radar); all 71 authored scene cases pass, with six scenes having none.
Three family-selection regression cases pass. Current mixer evidence:
`mixer-build.log`, `powder-chute-build.log`, `mixer-import.log`,
`mixer-geometry-final.log`, `mixer-plant-regression.log`,
`mixer-scene-contracts.log`, `mixer-native-final.log`,
`all-scene-geometry-mixer-final.log`. Global help validation remains failed at
the unrelated Count Display metadata/document mismatch. These counts do not
approve the rest of the catalog. Restore tag:
`codex/multi-angle-review-baseline-20261004` at `2c3de4b`.

Parcel follow-up evidence: `parcel-geometry.log`, `parcel-plant-regression.log`,
`parcel-scene-contracts.log`, `parcel-inventory-final.log`,
`parcel-native-final-shell.log`, `parcel-native-plant.log` and
`demo5-conveyor-native.log`. CLI preview rejects missing scene IDs and app-shell
combinations before creating a scene/transport. Native screenshots were inspected
in this session; navigation logs alone do not constitute visual acceptance.

Current conveyor/gallery evidence: `catalog-conveyor-before-clearance.log`,
`catalog-gallery-build.log`, `catalog-gallery-geometry.log`,
`catalog-native-final.log`, `catalog-inventory-final.log`,
`catalog-plant-regression.log`, `catalog-rendered-scene-controls.log` and
`catalog-scene-contracts.log`. Build has zero warnings/errors; 31 geometry and
19 plant checks pass, as do 71 declared scene cases. The GUI input verifier
failed when incorrectly invoked headless; its rendered invocation passes all
checks, including actual viewport input and button feedback. Native screenshots
were separately inspected. The user's pre-existing Demo 1 window was preserved;
the isolated review window closed cleanly.

- Drive Alarm-Code String: native baseline five-view inspection found a
  guarding panel labeled VFD, a roller shutter labeled fieldbus display, a servo
  amplifier labeled status indicator, equipment intersections and a panel below
  the floor. These are source-package identity failures. The fieldbus GLB's
  SHUTTER/KIN nodes conflict with its current parking-display recognition record;
  fresh native import confirms the mismatch. Moving the copies apart was insufficient.
  Original grounded training props now replace all three. Inherited reviews and
  unrelated pictures are archived, generic-basis/industrial references removed,
  stale shutter kinematics removed, and quality remains candidate/unapproved.
  Native detail inspection caught the VFD mast outside its base and hidden keypad
  buttons; both are repaired. Final full-scene FR/FL/RL/RR/T views and close VFD
  front/rear/overhead checks show bounded support/clearance. MESSAGE VALID,
  CODE FOUND and RESET plates were inspected closely. Optional faceLabel retains
  default plates in scenes that do not configure it; prior three-panel label
  findings remain open. The status lens now binds drive_alarm_active; symbolic
  image true/reset projection passes. Display legends are static, not received
  alarm text. Scene/help explicitly state Boolean inputs and no fieldbus/string
  parsing implementation. Normal shell Run was retested after repair: empty
  editor, NO CONTROLLER LOADED. No supplied reference ladder; that workflow and
  actual string processing remain open. The original wall-VFD family builder
  also hides its keypad keys; only this training package is corrected here.

- Labs 10.2 through 10.6: native FR/FL/RL/RR/T baseline views were inspected in
  the full shell, and normal Run was clicked separately in each scene. All five
  open the empty editor with NO CONTROLLER LOADED. Their five-point Boolean
  contracts do not implement the named weight/class/enum/struct/array concepts.
  These observations are failures/open work, not lesson acceptance.
  - Chicken Label Print: conveyor intersects the CNC cabinet; carton is on the
    floor instead of the belt. The checkweigher is a roller shutter, food-product
    load is a pneumatic pusher, and formatted-label display is a tote labeler.
    No weight data, label-text formatting or printing process is implemented.
  - Vision Package Sorter: a close front-right carton view confirms it is under
    the belt, among its frame/end hardware. Class-result display is a photoeye;
    four-lane diverter is a selector switch. There are two disconnected parallel
    belts and a fixture table, not four connected destination lanes. Five BOOL
    points contain no class/destination value or routing controller.
  - Motor Operating-State Enum: supports/spacing are clear. Three generic START
    plates incorrectly identified Start, Stop and Fault inputs, and motor_running
    was bound only to the lamp, leaving the actual shaft stationary. Corrected
    START REQUEST/STOP REQUEST/FAULT ACTIVE plates and green/red/amber buttons
    were inspected closely; final FR/FL/RL/RR/T views were repeated. The existing
    symbolic motor_running output now drives the shaft as well as the lamp.
    Four regression checks cover plates, actual shaft true/false behavior and
    Reset. The plate and shaft checks failed before repair and pass afterward.
    This is output-image projection evidence, not native controller execution;
    no enum-valued point/named state or reference controller is supplied. Normal
    Run after repair still opens an empty editor. Scene/help now state that scope.
  - Motor STRUCT Data: diagnostic faceplate and structured-data monitor are
    roller shutters; temperature display is an RTD probe. Shutter posts and
    nearby equipment overlap. The contract has BOOL validity/enable points,
    not a structured motor record or numeric temperature.
  - Ten-Motor Array Startup: only five actual motors; the claimed ten-motor
    lineup and group-status panel are overlapping roller shutters. Sequence
    display is a three-button box. No per-motor array commands or staggered
    startup timing exist in the five-BOOL contract.

## Catalog coverage

FR/FL/RL/RR/T = front-right / front-left / rear-left / rear-right / top.
Pending means not inspected in this new pass. Previous single-view pictures,
initial-state cases, inherited asset reviews and catalog `mapped` status do not
count as this scene's multi-angle or runtime acceptance.

| # | Scene | Bounds candidates | Native static views | Current result |
| --- | --- | ---: | --- | --- |
| 1 | `conveyor-cell` | 11 | FR/FL/RL/RR/T | Repaired support/sensor clearance; normal offline Run/Start/Stop/Reset and E-stop inspected |
| 2 | `equipment-gallery` | 0 | FR/FL/RL/RR/T | Repaired floor/display support; normal Run opens blank editor, animation workflow open |
| 3 | `lab-10-01-drive-alarm-code-string` | 0 | FR/FL/RL/RR/T | Repaired prop identity, spacing and supports; normal Run opens blank editor; string processing absent |
| 4 | `lab-10-02-chicken-label-print` | 144 | FR/FL/RL/RR/T | FAIL: wrong checkweigher/load/display models, CNC/belt intersection, unsupported carton, empty editor on Run |
| 5 | `lab-10-03-vision-package-sorter` | 32 | FR/FL/RL/RR/T + carton FR | FAIL: carton under belt, wrong display/diverter models, no four-lane path, empty editor on Run |
| 6 | `lab-10-04-motor-enum-state` | 0 | FR/FL/RL/RR/T + three plate details; repeated after repair | Repaired plates and symbolic shaft binding; enum state/controller absent, normal Run opens empty editor |
| 7 | `lab-10-05-motor-struct-data` | 67 | FR/FL/RL/RR/T | FAIL: shutter copies instead of displays, interference, no STRUCT data, empty editor on Run |
| 8 | `lab-10-06-ten-motor-array-startup` | 260 | FR/FL/RL/RR/T | FAIL: five motors and overlapping shutter copies, no array/timed startup, empty editor on Run |
| 9 | `lab-11-06-wastewater-collection` | 222 | Pending | Pending |
| 10 | `lab-11-07-multi-conveyor-pallet-route` | 892 | Pending | Pending |
| 11 | `lab-11-11-service-elevator` | 63 | Pending | Pending |
| 12 | `lab-11-12-mobile-traffic-lights` | 21 | Pending | Pending |
| 13 | `lab-11-13-xy-palletizing` | 0 | FR/FL/RL/RR/T | Repaired; bounded static/motion checks pass |
| 14 | `lab-11-19-powder-batch-mixer` | 0 | FR/FL/RL/RR/T | Repaired static layout/chute; process behavior unverified |
| 15 | `lab-2-01-workstation-call` | 0 | FR/FL/RL/RR/T | Clear supports/spacing; generic START plate needs correction; runtime pending |
| 16 | `lab-2-02-dual-confirmation` | 0 | FR/FL/RL/RR/T | Clear three-component footprint/supports; generic START plates need correction; runtime pending |
| 17 | `lab-2-03-service-marker-inhibit` | 0 | FR/FL/RL/RR/T | Clear button/beacon footprint/supports; incorrect START plate; runtime pending |
| 18 | `lab-2-04-two-station-call` | 0 | Pending | Pending |
| 19 | `lab-2-05-bay-light-selector` | 0 | Pending | Pending |
| 20 | `lab-2-06-ready-attention` | 0 | Pending | Pending |
| 21 | `lab-2-07-dual-contact-permissive` | 0 | Pending | Pending |
| 22 | `lab-2-08-inspection-vote` | 0 | Pending | Pending |
| 23 | `lab-2-09-maintenance-beacon` | 0 | Pending | Pending |
| 24 | `lab-2-10-dust-collector-seal-in` | 0 | Pending | Pending |
| 25 | `lab-2-11-inbound-tote-stop` | 15 | Pending | Pending |
| 26 | `lab-2-12-assembly-lift` | 0 | Pending | Pending |
| 27 | `lab-2-13-coolant-jug-fill` | 53 | Pending | Pending |
| 28 | `lab-2-14-sump-pump` | 41 | Pending | Pending |
| 29 | `lab-2-15-fume-extractor` | 0 | Pending | Pending |
| 30 | `lab-2-16-safe-drill` | 24 | Pending | Pending |
| 31 | `lab-2-17-pallet-robot` | 23 | Pending | Pending |
| 32 | `lab-2-18-pallet-pickup` | 29 | Pending | Pending |
| 33 | `lab-2-19-service-door` | 54 | Pending | Pending |
| 34 | `lab-2-20-bottle-shuttle` | 39 | Pending | Pending |
| 35 | `lab-2-21-tote-finishing` | 29 | Pending | Pending |
| 36 | `lab-2-22-dual-spindle` | 2 | Pending | Pending |
| 37 | `lab-2-23-parcel-sorter` | 174 | FR/FL/RL/RR/T | Repaired static/declared plant path; normal Run lacks controller |
| 38 | `lab-2-24-robot-cnc` | 29 | Pending | Pending |
| 39 | `lab-2-25-inspection-toggle` | 0 | Pending | Pending |
| 40 | `lab-3-01-guarded-pallet-transfer` | 20 | Pending | Pending |
| 41 | `lab-3-02-robot-cell-safe-restart` | 42 | Pending | Pending |
| 42 | `lab-4-01-press-count-lamp` | 0 | Pending | Pending |
| 43 | `lab-4-02-counter-reset-lamp` | 0 | Pending | Pending |
| 44 | `lab-4-03-repeat-cycle-counter` | 0 | Pending | Pending |
| 45 | `lab-4-04-sequence-light-tower` | 0 | Pending | Pending |
| 46 | `lab-4-05-dual-input-count-window` | 0 | Pending | Pending |
| 47 | `lab-4-06-multi-press-confirmation` | 0 | Pending | Pending |
| 48 | `lab-4-07-parking-garage-entry` | 20 | Pending | Pending |
| 49 | `lab-4-08-package-grouping` | 118 | Pending | Pending |
| 50 | `lab-4-09-chain-drive-lift` | 145 | Pending | Pending |
| 51 | `lab-4-10-cookie-packaging` | 196 | Pending | Pending |
| 52 | `lab-4-11-barrel-fill-station` | 143 | Pending | Pending |
| 53 | `lab-4-12-cable-cut-length` | 21 | Pending | Pending |
| 54 | `lab-5-01-delayed-lamp` | 0 | Pending | Pending |
| 55 | `lab-5-02-timed-lamp-off` | 0 | Pending | Pending |
| 56 | `lab-5-03-rotary-flasher` | 0 | Pending | Pending |
| 57 | `lab-5-04-alternating-lamps` | 0 | Pending | Pending |
| 58 | `lab-5-05-variable-flash-rate` | 0 | Pending | Pending |
| 59 | `lab-5-06-running-light-tower` | 0 | Pending | Pending |
| 60 | `lab-5-07-pedestrian-crossing` | 26 | Pending | Pending |
| 61 | `lab-5-08-drawbridge-control` | 43 | Pending | Pending |
| 62 | `lab-5-09-bag-indexing-conveyor` | 37 | Pending | Pending |
| 63 | `lab-5-10-coating-line` | 97 | Pending | Pending |
| 64 | `lab-6-07-luggage-weight-sort` | 110 | Pending | Pending |
| 65 | `lab-6-08-hand-dryer` | 634 | Pending | Pending |
| 66 | `lab-9-01-sum-function` | 0 | Pending | Pending |
| 67 | `lab-9-02-product-function` | 0 | Pending | Pending |
| 68 | `lab-9-03-sum-and-counter-function` | 0 | Pending | Pending |
| 69 | `lab-9-04-function-selector` | 0 | Pending | Pending |
| 70 | `lab-9-10-box-volume` | 46 | Pending | Pending |
| 71 | `lab-9-11-pallet-counting` | 86 | Pending | Pending |
| 72 | `lab-9-12-ev-charging-manager` | 95 | Pending | Pending |
| 73 | `scene-1-conveyor-stop` | 34 | Pending | Pending |
| 74 | `scene-2-conveyor-pusher` | 88 | Pending | Pending |
| 75 | `tank-high-low` | 60 | Pending | Pending |
| 76 | `tank-level` | 52 | Pending | Pending |
| 77 | `tank-radar` | 80 | Pending | Pending |

Drive-alarm follow-up evidence: `.tools/drive-alarm-{props-build,build,import,geometry,inventory,scene-contracts,rendered-controls,plant-regression}.log`, `catalog-next-shell-native.log` (baseline), `drive-alarm-native-supported.log` (support and plates), and `drive-alarm-native-final-complete.log` (final five views, keypad detail, failed normal Run). Build zero warnings/errors; 38 focused geometry, 19 plant, rendered scene controls and 71 authored cases pass. These do not approve uninspected scenes, missing controllers, string functionality or hardware.

Catalog scenes 4-8 follow-up evidence: `.tools/catalog-scenes-4-8-native.log` records native navigation; screenshots were individually inspected. Normal Run was observed separately for all five. `.tools/motor-state-{red-build,red-geometry,build,geometry,scene-contracts,native-final}.log` records the failing projection checks, repaired 42-check pass, 71 authored-case pass and final native camera/plate review. Logs do not replace visual observation or supply a controller. Goal active: 63 inspections remain, and recorded failures require repair.
