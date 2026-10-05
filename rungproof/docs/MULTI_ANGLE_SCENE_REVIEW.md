# Multi-angle scene review - 2026-10-04

Status: **active**. The prior software review did not establish multi-angle
visual acceptance. Thirty scenes have five-view native static inspections; 47 remain pending.
Demo 5, Powder Batch Mixer, Parcel Size Sorter, Conveyor Inspection Cell,
the Equipment Gallery, Drive Alarm-Code String and Chicken Label Print have repaired static layouts.
The sorter operator Run still lacks a controller; eight simple panels now have corrected function plates and clear spacing. Other scenes
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
42 of 77 scenes have positive counts in the selector follow-up inventory.
Every row requires native inspection.

## Repairs and open findings

- Sump Dewatering Pump (scene 28): native FR initial / FL / RL / RR / T views
  and close overhead/FL discharge views inspected. **FAIL/open:** the pump has
  no connected suction/discharge route; the elevated spool/valve assembly
  interferes with the tank ladder/cage and lacks grounded pipe support. The
  valve runs vertically beneath a horizontal spool rather than an established
  inline discharge connection. The actual low sensor bounds extend to Y=-0.175;
  its probe is below the floor. Source maps the two named floats to tuning-fork
  switches, and their tank process fittings are not established. The closed
  vertical vessel also does not establish the described sump installation.
  The 41 AABB candidates are a screening count, not 41 proven solid collisions.
  Normal Run opens the unloaded editor. The pump-hysteresis contract passes in
  the standalone reference runtime; that does not prove installed flow, real
  sensor behavior, native level extremes or controller execution. Keep this
  failed until actual ports, probe elevations, routing/support and full level
  motion are repaired and inspected. Evidence: sump-native.log and
  sump-fume-sump-contract.log under rungproof-next/.tools, current native
  screenshot observations and the imported bounds inventory.
- Weld Fume Extractor (scene 29): native FR/FL/RL/RR/T views show separated,
  grounded equipment without an observed cross-equipment solid intersection.
  Initial AABB inventory is zero, which alone is not acceptance. The light
  request station incorrectly read START; config faceLabel now reads LIGHT
  REQUEST. Fresh native FR/FL close views show the text on its plate without
  overlap. Native Advance Fan Speed moves the pointer and input value through
  0 -> 1 -> 2 -> 3 -> 0; fan_run remains false with no controller loaded. A
  native light request toggles the PC input while the PLC output stays false.
  Normal Run still opens EDIT INVALID / NO CONTROLLER LOADED. Five standalone
  contract cases cover all four speeds, exactly one speed flag, independent
  light toggling and return to off. Existing boolean-panel output reset prevents
  accumulated flags; no runtime rule rewrite was needed. The speed percent has
  no rendered point binding, so actual variable fan animation remains open.
  Inspection light is a single-tier beacon; extraction hood/duct and actual
  illumination are not modeled. Guard recognition is not physical safety proof.
  Thus spacing/label/input-pointer observations are bounded; complete extractor
  identity, speed response, controller outputs and Stop/Reset motion remain open.
  Evidence: sump-native.log, fume-label-native.log and fume-contract.log under
  rungproof-next/.tools, plus inspected native screenshots. Both isolated review
  windows exited cleanly; user Demo 1 remains open. Fresh build has zero warnings/
  errors; all 95 existing geometry checks and 142 controller tests pass. Shell
  verifies 77 scenes/294 assets with the same four headless invalid-position
  errors and no-saved-workspace warning. These checks do not cover sump piping
  acceptance. Coverage is now 30/77 inspected, 47 pending, including failures.
- Coolant Jug installation follow-up (earlier checkpoint): the capped jug, unsupported belt height
  and fixed fill solids in its lane are repaired with an opt-in scene adapter.
  The actual imported jug bottom was 129.3 mm above the belt; its new origin
  puts the bottom at Y=0.9000003. The exit origin is X=3.5, keeping its full
  footprint on the eight-metre belt. The photoeye stands straddle the conveyor.
  Both filler posts are grounded outside the belt and joined to a portal beam;
  the nozzle sits over the uncapped annular mouth. Its tip and visual stream
  follow the nozzle, and the stream is visible only when the valve is open.
  The reusable standalone asset and other jug instances retain their defaults.
  Native catalog FR/FL/RL/RR/T initial views were inspected, plus all five held
  filling views in explicit no-controller plant QA. A close FL view shows the
  open neck and centered stream. Close overhead is occluded by the dosing head
  and is not acceptance of the hidden mouth. Four separate 0.5-second runtime
  steps reach filling; hold keeps that pose stable through camera changes.
  Holding disables runtime/equipment processing; stepping advances sequence
  bindings, not independent pump rotation or conveyor texture animation.
  Resuming real-time processing reaches the supported exit with fill_percent=100,
  valve/skid off and cycle_complete=true. Reset restores the initial supported
  jug. A fresh real-time Run was inspected during indexing and at completion;
  Stop was clicked after completion, so mid-cycle Stop remains deterministic
  evidence only. Normal catalog Run still opens EDIT INVALID / NO CONTROLLER
  LOADED. The introduction's claim that Run controls the scene is misleading
  for this unloaded controller state and remains a workflow finding.
  Ten new checks cover actual support, annular mouth, solid clearances, grounded
  frame connections, 320 travel samples, fill alignment, attached tip/stream and
  Stop/Reset. Original scene configuration reproduces failed checks; all 95
  geometry checks now pass. Build: zero warnings/errors; one fill contract case,
  19 plant-motion checks, 142 controller tests and rendered overlay/control checks
  pass. Shell verifies 77 scenes/294 assets but retains four headless invalid
  window-position errors and the expected no-saved-workspace warning. Clearing
  imported ownership before reparenting removes new attachment-owner warnings.
  Current initial AABB inventory is 13 candidates (formerly 53), in the conveyor /
  sensor pair; solid OBB checks exclude optical beam/cables. This is screening,
  not physical collision proof. The external skid-to-reservoir service pipe is
  still absent; the internal reservoir-to-valve path was repositioned. Structural
  ratings, hollow body/fluid volume, real optical sensing and PLC-controlled
  execution are unverified. Scene acceptance remains open on those documented
  visual/workflow omissions. Logs coolant-install-*-final.log,
  coolant-install-native-held.log and coolant-install-shell-native.log under
  rungproof-next/.tools record this checkpoint; screenshots were inspected in
  the native review session. Both isolated reviewers exited cleanly; user Demo 1
  remains open. Coverage stays 28/77 inspected, 49 pending, including failures.
- Historical pre-repair Coolant Jug inspection (scene 27): native FR/FL/RL/RR/T and
  close overhead/FL fill-unit views. **Visual acceptance FAIL/open:** the jug
  retains its red cap, while fixed fill-assembly solids occupy its indexing
  lane on the belt. A usable nozzle-to-open-jug fill path and supported clear
  travel are not established. The source maps coolant_jug to the jerry-can asset
  and toteFiller to the volumetric tote filling station; that standalone station
  needs a scene integration review rather than treating its recognition as a
  validated conveyor installation. The 53 AABB candidates remain a screening
  count, not 53 proven collisions. Imported cap/nozzle, belt/support and sensor
  bounds need measurement before the repair. Normal Run opens the blank editor
  with EDIT INVALID / NO CONTROLLER LOADED. No filling sequence, high-probe
  behavior, transfer endpoint or motion clearance is accepted. Evidence:
  coolant-jug-native.log in rungproof-next/.tools plus native screenshot
  observations in the review session. Isolated window closed cleanly; user
  Demo 1 preserved. Coverage 28/77 inspected, 49 pending, including failed scenes.
- Assembly Lift hydraulic follow-up: the stationary rod/clevis failure recorded
  below is repaired. The driven lower-front arm now carries its clevis, pin and
  drive lug. The fixed-length barrel pivots at its base pin; only the rod's
  longitudinal mesh axis extends between the gland and moving clevis. Imported
  mesh dimensions determine lengths, retaining rod/barrel diameters. Binding
  checks require the delivered nodes and common parent coordinate system; an
  incompatible asset logs a warning instead of applying the wrong transform.
  Four additional checks use actual mesh-cap centres and the authored arm mount
  through 240 raise/lower samples, plus hydraulic Stop/Reset transforms. Two
  attachment/contact checks reproduce failures before repair; all 85 geometry
  checks now pass. Fresh build has zero warnings/errors, both Assembly Lift
  contract cases and all 19 plant-motion checks pass. Current native Windows
  inspection covers all five angles, a closer lift view, FL/RR raising/lowering
  and endpoints, FR raised attachment and Reset. The FL raised view exposes
  the connected cylinder/rod/clevis chain; rear views occlude parts of it and
  are not independent acceptance of those hidden details. Native Stop was
  clicked after the top endpoint; mid-cycle hold remains deterministic evidence.
  Evidence: hydraulic-before.log, hydraulic-final.log, hydraulic-final-build.log,
  hydraulic-contract.log, hydraulic-plant-motion.log and hydraulic-native.log in
  rungproof-next/.tools. The current master still has exposed arms; historical
  bellows recognition is not current guarding or independent approval. Normal
  controller-owned lesson execution and the four other shared lift scenes still
  need their documented follow-up. Coverage stays 27/77, with 50 pending scenes.
  Isolated reviewer closed cleanly; user Demo 1 preserved. Goal remains active.
- Assembly Lift (scene 26) has native FR/FL/RL/RR/T inspections, close RAISE /
  LOWER plate views, and raise/lower movement and endpoints inspected from FL
  and RR. The fixture previously started at Y=0.82 beneath the actual imported
  deck top at Y=1.64. Its origin and sequence endpoints are now 1.64 / 3.84,
  retaining the existing 2.2 m travel. The minimumHeight metadata now matches
  the imported deck, but the composer still ignores that sizing setting; this
  change does not implement configurable lift height. Plates now identify both
  directions instead of displaying generic START labels.
  Six focused checks cover actual imported-mesh support initially and through
  both directions, 16 roller/washer attachments, full travel within the initial
  camera frustum, mid-cycle Stop, and supported Reset. Four attachment/support
  checks fail before repair; all 81 geometry checks pass after repair. Rollers
  and washers now follow their nearest authored pins while retaining their
  mounting offsets. Camera framing includes a conservative lift-travel envelope
  so a raised deck/fixture is visible without changing its pose. Shared lift
  motion/framing changes still require native follow-up in the Gallery, Service
  Elevator, Chain Drive Lift and Drawbridge scenes; their previous coverage
  does not establish acceptance of this revision.
  Standalone plant QA now exposes declared actions with a selector so Lower
  can be exercised as well as the default Raise. Its camera/action bars were
  repositioned and visually checked for readability and overlap. This control
  is restricted to the explicit no-controller QA mode. Normal shell Run still
  opens a blank exercise with EDIT INVALID / NO CONTROLLER LOADED. Native Stop
  was observed at the completed lower endpoint; only the deterministic check
  verifies mid-cycle Stop. Reset restores bottom_limit=true / top_limit=false.
  At this earlier checkpoint, full mechanism motion was **FAIL/open**: the hydraulic rod was still
  restored to its authored transform rather than following the driven arm.
  The old asset review describes an enclosed bellows skirt, whereas the current
  master/source and native scene expose the arms. That historical recognition
  result does not establish acceptance or guarding of the current revision.
  Fresh build: zero warnings/errors. Two scene-contract cases, 19 plant-motion
  checks, 142 controller tests and the 77-scene/294-asset shell verifier pass.
  The shell verifier also reports four invalid headless window-position errors;
  it is not a clean stderr run. Rendered Windows control checks pass both with
  and without the review overlay, including mouse input and external-image
  ownership. The headless control invocation fails its mouse-click checks;
  retain that failed log and use the rendered invocation for this verification.
  Evidence under rungproof-next/.tools: assembly-geometry-before.log,
  assembly-geometry-final.log, assembly-geometry-build.log,
  assembly-lift-final-native.log, assembly-lift-final-actions-native.log,
  assembly-final-contract.log, assembly-final-plant-motion.log,
  assembly-final-controller.log, assembly-final-shell.log,
  assembly-final-rendered-controls.log (headless failure),
  assembly-final-rendered-controls-window.log and
  assembly-final-overlay-controls-window.log. Isolated windows closed cleanly;
  the user's Demo 1 window was preserved. Goal remains active: 50 pending static
  inspections, this hydraulic attachment failure and previously recorded failures.
- Inspection Vote, Dust Collector and Inbound Tote Stop have final native
  FR/FL/RL/RR/T inspections, plus close function-plate and tote-support views.
  Vote plates now read VOTE A / VOTE B and the collector stop plate reads STOP.
  Actual 3D inputs and Reset were checked on both panels. Pending scan pulses
  remain queued until a controller consumes them; that is intentional runtime
  behavior, not a completed PLC scan. Collector equipment is a fan schematic,
  without a modeled dust hood/filter process. All three normal Run attempts
  open the blank exercise editor with NO CONTROLLER LOADED.
- Inbound Tote Stop exposed three imported-mesh failures: its bottom floated
  99.5 mm above the 0.9 m belt, photoeye solids intersected the conveyor frame,
  and its X=4 endpoint left part of the tote outside the belt. Tote origin Y is
  now 0.8905 (actual bottom 0.900012), photoeye span 3.8 m, and clearing ends
  at X=3.4. Six focused checks cover actual belt contact/full footprint, sensor
  solid clearance, grounded feet, mid-cycle Stop/Reset, a 300-sample full cycle,
  and scan-dwell alignment with the beam envelope. The three failing checks
  fail before repair and all 75 geometry checks pass after repair. Beam bounds
  do not prove optical detection through the hollow tote or barcode reading.
  Seven broad AABB cable/frame candidates remain (previously 15); excluding
  cable bounds, imported solid OBB checks pass. This is not physical routing proof.
  Native plant-preview movement and completion were inspected from FL and RR;
  the completed footprint was inspected overhead, and Reset restores the input
  position. Native Stop was clicked after completion and holds the endpoint;
  mid-cycle Stop is covered by the deterministic check, not that UI observation.
  The preview explicitly has no PLC controller. Fresh build: zero warnings/errors.
  Three scene contracts (six cases) pass. Evidence under rungproof-next/.tools:
  inbound-geometry-before.log, inbound-geometry-final.log,
  inbound-geometry-build.log, catalog-scenes-22-28-native.log,
  inbound-native-motion-final.log, and the lab-2-08-inspection-vote,
  lab-2-10-dust-collector-seal-in and lab-2-11-inbound-tote-stop final-contract logs.
  The catalog log filename does not establish inspection of scenes 26-28.
  Isolated reviewers closed cleanly; the user's Demo 1 window was preserved.
  Goal remains active: 51 static inspections and recorded failures remain open.
- Two Station Call, Bay Light Selector, Ready/Attention, Dual Contact Permissive
  and Maintenance Beacon have final native FR/FL/RL/RR/T inspections. Their
  supports contact the floor and separate equipment remains clear in these views.
  Close views cover five new function plates: NORTH CALL, SOUTH CALL, ATTENTION,
  RESET NO and TEST NC. The two call actions independently change PC-owned inputs;
  actual 3D request/reset/NC controls were clicked on Ready/Attention and Dual
  Contact Permissive. Reset restores their input defaults. Ready/Attention's
  request is currently a persistent toggle despite its spring-return description;
  mouse hold/release and physical contact behavior are not accepted by these checks.
  Bay lights are single-tier post indicators; actual bay lighting is not modeled.
- Bay Light Selector exposed three fixed dial marks for a two-position input,
  and handle motion around Y swung it away from the front face. The delivered
  master has three marks and a Z-axis pivot, contradicting its old four-position
  approval. Composed variants now show only their configured 2-4 detents, with
  numbers outside the rim, ticks contacting the actual plate, and Z-axis handle
  projection. initialPosition is honored. Native Bay Light Selector clicks show
  0/1 and Reset to 0; Maintenance Beacon clicks show 0/1/2/3, wrap to 0, and Reset
  from 1 to 0. All numbers remain readable in final close views. This establishes
  symbolic dial projection, not beacon output logic or a lockout function.
  The unchanged master was moved from production to candidates, quality flags
  cleared, and its stale recognition/review archived. No fresh independent asset
  recognition is claimed. Master re-authoring, approval/help reconciliation,
  and fresh native checks of Gallery, Fume Extractor and Pallet Pickup variants
  remain open after the shared selector change.
- Normal Run was separately clicked on all five newly inspected lessons and
  opens the blank exercise editor with NO CONTROLLER LOADED. PC input clicks do
  not drive PLC-owned outputs without a program. These are static/input checks;
  the lesson output sequences and user-authored ladder workflow remain unaccepted.
  The user's Demo 1 window was preserved; isolated reviewers closed cleanly.
  Fresh build has zero warnings/errors. All 69 geometry checks pass, including
  20 selector checks of imported ticks, pointer alignment/plane and Reset across
  four bound selector lessons. Count/alignment/plane checks failed before repair.
  Plant checks (19), authored scene cases (71), virtual-controller tests (142),
  shell verification (77 scenes, 294 assets, disconnected) and normal rendered
  controls pass. Final geometry/build and native dial views include the last
  tick/legend placement; behavior suites preceded that geometry-only adjustment.
  Evidence under rungproof-next/.tools: selector-geometry-before.log,
  selector-final--verify-scene-geometry.log, selector-final--verify-plant-motion.log,
  selector-scene-contracts.log, selector-virtual-controller.log,
  selector--verify-app-shell.log, selector-rendered-controls.log,
  selector-inventory.log, catalog-panels-18-21-native.log,
  selector-native-complete.log and selector-four-position-native.log.
  Logs record navigation; screenshots were inspected separately. Goal remains active.
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
- Workstation Call, Dual Confirmation and Service Marker originally had generic
  START plates on call/confirmation/inhibit buttons. Their four plates now read
  MATERIAL CALL, OPERATOR OK, QUALITY OK and INHIBIT using the existing opt-in
  faceLabel support. Five final native views and all four close plate views were
  inspected. Their existing scene-contract cases pass. Normal Run was tried on
  each and opens an empty editor with NO CONTROLLER LOADED. The source confirms
  these labs intentionally start as tag-only exercises requiring user networks;
  label repair does not supply a reference controller or prove running behavior.
  Global help validation also fails at Count Display's inherited
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
  - Chicken Label Print: those baseline model/support failures are now repaired.
    The wrong shutter/pusher/tote-labeler packages were replaced, the unrelated
    CNC removed, and the tray/carton are supported. Final five views plus
    focused supports, printer paper, display and all three plates were inspected.
    Normal Run still opens the empty editor. No actual weight data, label-text
    formatting, printing or reference controller is implemented.
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

Scenes 9-12 follow-up: all four were opened in the native Windows shell and
inspected from all five angles. Wastewater's three 2.6 m tanks are only 2.2 m
apart; the additional collection-bank prop is a single large tank overlapping
the row. The level transmitter is an unmounted probe/body, not mounted feedback
from the three tanks. Its GLB contains PROBE_sensing_rod/process-flange nodes;
this is a mounting/scene-integration failure, not proof of a different instrument.
The claimed pipe manifold is a seven-station pneumatic assembly, confirmed by
native appearance and MAIN_AIR_SUPPLY / DIN_PLUG / EXHAUST_MUFFLER nodes.

The pallet-route close overhead/front-right views confirm belt/frame/end-roller
interference between three conveyors on one centerline. The roller zone is
beside them without a connected handoff. No pallet equipment exists. The handoff
sensor GLB contains VIB_label / PILLOW_BLOCK / MACHINE_shaft rather than a pallet
detection assembly. Service Elevator's rear views expose shutter/platform
interference; BUCKET_* nodes confirm the shaft prop is a continuous bucket
elevator. ENCLOSURE_body/FLOOR_plinth nodes confirm the position-sensor prop is
a cabinet. Traffic Lights' top/rear views confirm a vertical window panel, no
roadway, and two single amber beacon props. Each normal Run was tried separately
and opens an empty editor. These observations fail acceptance; bounds counts
alone neither locate every issue nor establish physical feasibility.

Evidence: .tools/catalog-scenes-9-12-native.log and
catalog-scenes-9-12-source.log. The three corrected simple panels were rechecked
in .tools/call-panel-native-final.log, including five views per scene, all four
plate close views and three separately observed Run failures. Their existing
contracts pass in lab-2-01-workstation-call-plate-contract.log,
lab-2-02-dual-confirmation-plate-contract.log and
lab-2-03-service-marker-inhibit-plate-contract.log. These rule-contract checks
do not supply the missing user ladder. Coverage is 18 inspected / 59 pending;
earlier counts below describe their earlier checkpoints. Goal active.

FR/FL/RL/RR/T = front-right / front-left / rear-left / rear-right / top.
Pending means not inspected in this new pass. Previous single-view pictures,
initial-state cases, inherited asset reviews and catalog `mapped` status do not
count as this scene's multi-angle or runtime acceptance.

| # | Scene | Bounds candidates | Native static views | Current result |
| --- | --- | ---: | --- | --- |
| 1 | `conveyor-cell` | 11 | FR/FL/RL/RR/T | Repaired support/sensor clearance; normal offline Run/Start/Stop/Reset and E-stop inspected |
| 2 | `equipment-gallery` | 0 | FR/FL/RL/RR/T | Repaired floor/display support; normal Run opens blank editor, animation workflow open |
| 3 | `lab-10-01-drive-alarm-code-string` | 0 | FR/FL/RL/RR/T | Repaired prop identity, spacing and supports; normal Run opens blank editor; string processing absent |
| 4 | `lab-10-02-chicken-label-print` | 0 | FR/FL/RL/RR/T + support/printer/display/plate details; repeated after repair | Repaired static identity/support/spacing; actual weighing/formatting/printing/controller absent; normal Run opens empty editor |
| 5 | `lab-10-03-vision-package-sorter` | 32 | FR/FL/RL/RR/T + carton FR | FAIL: carton under belt, wrong display/diverter models, no four-lane path, empty editor on Run |
| 6 | `lab-10-04-motor-enum-state` | 0 | FR/FL/RL/RR/T + three plate details; repeated after repair | Repaired plates and symbolic shaft binding; enum state/controller absent, normal Run opens empty editor |
| 7 | `lab-10-05-motor-struct-data` | 67 | FR/FL/RL/RR/T | FAIL: shutter copies instead of displays, interference, no STRUCT data, empty editor on Run |
| 8 | `lab-10-06-ten-motor-array-startup` | 260 | FR/FL/RL/RR/T | FAIL: five motors and overlapping shutter copies, no array/timed startup, empty editor on Run |
| 9 | `lab-11-06-wastewater-collection` | 222 | FR/FL/RL/RR/T + transmitter T/FR | FAIL: overlapping tanks, unmounted probe, pneumatic manifold instead of process piping; empty editor on Run |
| 10 | `lab-11-07-multi-conveyor-pallet-route` | 892 | FR/FL/RL/RR/T + conveyor T/FR | FAIL: three superimposed belts, disconnected roller zone, vibration/bearing prop instead of handoff sensor, no pallet; empty editor on Run |
| 11 | `lab-11-11-service-elevator` | 63 | FR/FL/RL/RR/T | FAIL: shutter intersects scissor platform, bucket elevator instead of car/shaft, cabinets instead of call station/position sensor; empty editor on Run |
| 12 | `lab-11-12-mobile-traffic-lights` | 21 | FR/FL/RL/RR/T | FAIL: vertical guard/window wall instead of roadway, single amber beacons instead of traffic head/link; empty editor on Run |
| 13 | `lab-11-13-xy-palletizing` | 0 | FR/FL/RL/RR/T | Repaired; bounded static/motion checks pass |
| 14 | `lab-11-19-powder-batch-mixer` | 0 | FR/FL/RL/RR/T | Repaired static layout/chute; process behavior unverified |
| 15 | `lab-2-01-workstation-call` | 0 | FR/FL/RL/RR/T + plate detail; repeated after repair | Clear supports/spacing; MATERIAL CALL plate repaired; normal Run opens empty exercise editor |
| 16 | `lab-2-02-dual-confirmation` | 0 | FR/FL/RL/RR/T + two plate details; repeated after repair | Clear supports/spacing; OPERATOR OK / QUALITY OK plates repaired; normal Run opens empty exercise editor |
| 17 | `lab-2-03-service-marker-inhibit` | 0 | FR/FL/RL/RR/T + plate detail; repeated after repair | Clear supports/spacing; INHIBIT plate repaired; normal Run opens empty exercise editor |
| 18 | `lab-2-04-two-station-call` | 0 | FR/FL/RL/RR/T + close plates | Static clear; NORTH/SOUTH CALL repaired. Independent PC actions/Reset checked; Run empty controller. |
| 19 | `lab-2-05-bay-light-selector` | 0 | FR/FL/RL/RR/T + close dial | Static clear; 2-position dial/axis repaired; native 0/1/Reset. Post indicators only; Run empty controller. |
| 20 | `lab-2-06-ready-attention` | 0 | FR/FL/RL/RR/T + close plate | Static clear; ATTENTION repaired; 3D request/Reset checked. Persistent toggle vs spring-return description open; Run empty controller. |
| 21 | `lab-2-07-dual-contact-permissive` | 0 | FR/FL/RL/RR/T + close plates | Static clear; RESET NO/TEST NC repaired; 3D PC inputs/Reset checked. No physical contact proof; Run empty controller. |
| 22 | `lab-2-08-inspection-vote` | 0 | FR/FL/RL/RR/T + close plates | Static clear; VOTE A/B repaired; 3D PC inputs/Reset checked. No conflict output sequence accepted; Run empty controller. |
| 23 | `lab-2-09-maintenance-beacon` | 0 | FR/FL/RL/RR/T + close dial | Static clear; 4-position dial/axis repaired; native 0-3/wrap/Reset. No beacon sequence or lockout proof; Run empty controller. |
| 24 | `lab-2-10-dust-collector-seal-in` | 0 | FR/FL/RL/RR/T + close STOP | Static clear; STOP repaired; 3D PC requests/Reset checked. Fan schematic only; Run empty controller. |
| 25 | `lab-2-11-inbound-tote-stop` | 7 | FR/FL/RL/RR/T + close tote; FL/RR motion endpoints | Tote support, sensor clearance and cycle endpoint repaired; six focused checks pass. Native completion/Reset and endpoint Stop checked; Run empty controller. Cable AABB candidates remain. |
| 26 | `lab-2-12-assembly-lift` | 0 | FR/FL/RL/RR/T + close plates/lift + FL/RR motion | Fixture support, rollers/washers, travel framing and hydraulic attachment repaired; historical bellows approval stale; blank editor on normal Run; shared scenes need follow-up |
| 27 | `lab-2-13-coolant-jug-fill` | 13 | Catalog FR/FL/RL/RR/T; QA five held filling views + close FL mouth; real-time indexing/exit, Reset | Lane/support/nozzle repaired; sampled sweep clear. Open: external service pipe absent, Run blank controller editor; native Stop endpoint-only |
| 28 | `lab-2-14-sump-pump` | 41 | FR initial/FL/RL/RR/T + close overhead/FL discharge | FAIL: disconnected pump, elevated unsupported/intersecting piping, buried low probe; float fitting/identity open; normal Run unloaded |
| 29 | `lab-2-15-fume-extractor` | 0 | FR/FL/RL/RR/T; repaired close plate; native selector 0-1-2-3-0 | Spacing/input pointer checked, LIGHT REQUEST repaired. Open: beacon substitutes light, hood/duct absent, speed animation unbound, Run unloaded; five reference contract cases pass |
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
| 51 | `lab-4-10-cookie-packaging` | 146 | Pending | Pending |
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
