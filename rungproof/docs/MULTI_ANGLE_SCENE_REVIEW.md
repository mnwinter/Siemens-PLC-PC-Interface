# Multi-angle scene review - 2026-10-04

Status: **active**. The prior software review did not establish multi-angle
visual acceptance. All 77 scenes have initial five-view native static inspections.
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
- Catalog completion checkpoint (2026-10-04): scenes 66-77 each inspected in
  native FR/FL/RL/RR/T. This completes initial static coverage, including failures;
  it does not complete repairs, motion sweeps or whole-program acceptance.
  Sum/Product/Function Selector show CNC, shaft-support and shutter substitutes;
  their Boolean-only contracts have no numeric operands/results or function-choice
  value. Sum/Counter has no numeric result/count contract. Box Volume has two
  shutters and no numeric dimensions/volume binding. EV Charging has disconnected
  fluid props/shutters, no vehicle/charging route or energy-pulse/accumulation
  contract. These outputs bind to lamps rather than the claimed process.
  Pallet Counting's carton is buried; the declared type sensor appears as a
  white pallet beneath a shutter post, and its count display is a shutter.
  Conveyor Stop/Pusher have apparent carton support gaps; measurement/runtime
  projection still needs repair. Pusher has no receiving support, and sensor/head
  clearance requires a full motion check. Tank scenes share disconnected pump
  and elevated inlet piping, external long probes and opaque vessels. Radar's
  promised instrument/cone is not identifiable in the five wide views; focused
  geometry inspection is required. No tank fill/drain motion is accepted.
  Evidence: bag-carton-native-final.log and scene JSON; navigation logs do not
  replace the individually inspected screenshots.
- Pallet Counting (71 / authored Demo 4): normal Run loads the batch-counter
  program. Native rail type-valid/count-request permissives plus five separate
  detection rising edges leave the lamp off for edges 1-4 and light it at 5.
  Clearing type-valid removes the output; restoring it restores the output.
  Stop removes output with visible inputs retained; Run restores output from
  the retained batch; Reset returns stopped scan zero and visible inputs/output
  false. Source preset is five. Internal numeric watch, 3D button operation,
  pallet motion and displayed numeric count were not accepted.
- Conveyor Stop (73 / authored Demo 3): normal Run loads the authored program.
  Rail Start sets conveyor-running; carton advances to the photoeye, feedback
  becomes true and conveyor output becomes false. Subsequent native FR view
  confirms the held carton. Stop preserves the held feedback; Reset clears
  feedback/output, returns position zero and restores the carton to the load
  end. No mid-travel Stop, full clearance sweep or physical PLC proof.
- Radar Tank (77): declared Run and inlet actions both report that no ladder
  controller is loaded. Normal Run opens the empty editor, NO CONTROLLER LOADED.
  The scene description's immediate run/fill instructions do not match startup.
  Other scenes 66-70, 72, 74-76 had no action/Run/Stop/Reset acceptance added.

- Scenes 60-65 (2026-10-04): each inspected in native FR/FL/RL/RR/T.
  Pedestrian Crossing has a vertical window/guard panel instead of a road,
  amber beacons instead of traffic/pedestrian heads, and vehicle_stop binds to
  a green indicator. Drawbridge has a scissor table, vertical guard and shutter;
  bridge_raise/traffic_release bind only to lamps, with no bridge-deck motion.
  Bag Indexing's carton was below the belt (top/FR close). Its origin is now
  Y=0.9 m, matching the measured carrying surface; both support/solid-clearance
  checks fail before and pass after. Rebuilt normal native startup, five wide
  views and top/FR close views confirm the repair. The product is still a carton
  rather than a bag; sensors are outside the belt and conveyor outputs only
  lamps. Coating Line's CNC occupies the conveyor, with a shutter and disconnected
  fan/spray props rather than a continuous coating/ventilation route. Luggage
  Sort's carton is buried, with a shutter display and disconnected weighing/
  rejecting layout; its Boolean-only contract has no measured weight or numeric
  class. Hand-Dryer shows multiple overlapping shutters and disconnected fan,
  panel and bottle props rather than a dryer; no remaining-time point or display
  binding exists. All six use manually toggled PC feedback and lamp-only PLC
  output bindings. No actions, loaded ladder, Run/Stop/Reset, machine motion or
  complete lesson behavior was accepted for these six scenes.
  Evidence: catalog-51-native.log (60-62 baseline), bag-carton-native-final.log
  (62 repaired and 63-65), scene JSON, bag-carton-{red-build,red-geometry,build,
  geometry,contract}.log. Build zero warnings/errors; all 151 geometry/reference
  checks and Bag Indexing's initial-state contract pass. This is static support
  acceptance only. Required controller suite: 142 pass, zero fail, no real PLC
  transport/connection. App shell passes for 77 scenes/294 assets but retains
  four known headless invalid-window-position errors and missing-workspace
  warning (bag-carton-{controller,shell}.log); stderr is not clean.
  Goal active; 12 static inspections and recorded repairs remain.

- Scenes 51-59 (2026-10-04): each inspected in native FR/FL/RL/RR/T.
  Cookie Packaging's CNC occupies the belt, and its food product is a packaged
  meat tray below the indexing conveyor (top/FR close), with no cookie stream.
  Barrel Fill's tank occupies the conveyor; its declared barrel is visibly a
  MOTOR STARTER (top/FR close). Valve/flow-meter/nozzle assemblies do not form
  a connected barrel-filling route. Cable Cut has two roller shutters instead
  of reel/dancer equipment and no continuous cable/encoder/cutter arrangement.
  These three scenes' outputs bind only to green beacons; actual machine,
  measured count/length, transfer and filling behavior remains unaccepted.
  Timed/flash panels have clear grounded stands in five views, but START plates
  are ambiguous. Timed Lamp-Off's start_pulse is a persistent toggle and
  time_active is precomputed PC input. Rotary Flasher has pushbuttons instead
  of the promised rotary selector, and manually toggled flash_tick. Alternating
  Lamps uses a PC alternate_phase toggle; timer alternation/exclusivity was not
  exercised. Variable Flash Rate's fast/slow inputs can both be selected by
  separate toggles; precedence/timing remains unverified. Running-Light Tower
  has one green-only output, unable to walk independent tower levels; its
  step_pulse is persistent. No loaded controller/actions were tested for
  51-53 or 55-59. Evidence: catalog-51-native.log and scene source bindings.
- Delayed Lamp (54 / authored Demo 2): five native wide views show clear stands.
  Normal Run starts the authored two-network 2-second TON document. Rail
  request toggle gives PC=true/output=false initially; subsequent native view
  shows output=true and green beacon. Actual 3D button clears request/output.
  Reapplied request yields green; normal Stop removes output while request
  remains true, Reset clears both points and returns stopped scan zero.
  Source confirms the preset; screenshots establish before/after behavior,
  not a precisely measured two-second interval. Its selector description
  mismatches the pushbutton model/START plate. Evidence: catalog-51-native.log,
  AuthoredDemoLadderPrograms.cs and individually inspected native screenshots.
  Full catalog and repairs remain; goal active.
- Scenes 43-50 (2026-10-04): each has inspected native FR/FL/RL/RR/T views.
  Counter/reset and pattern panels have clear static stand spacing, but their
  persistent toggles expose precomputed count/pattern conditions rather than
  raw counting/press events. No loaded controller or Run/Stop/Reset workflow was
  exercised for these eight scenes. Their START plates remain ambiguous.
  Repeat Cycle's CNC has no machine-output binding. Sequence Light Tower
  promises four colors but has three-tier beacons and two green-only bindings.
  Parking Entry's declared vehicle is visibly a MOTOR STARTER (FR close), with
  two shutters and a wall panel; barrier_open binds only to a beacon, without
  barrier/shutter motion or numeric occupancy feedback. Package Grouping's
  carton was below its belt (top/FR close); Chain Lift has overlapping lift/
  conveyor equipment, two scissor tables instead of the declared vertical hoist,
  a floor carton and an isolated palletized-load accessory. Chain/lift outputs
  bind only to beacons. Complete transfer, sensor feedback and motion remain open.
  Baseline evidence: press-count-fixed-native.log, scene JSON bindings and
  individually inspected native screenshots. Bounds counts in the table remain
  the earlier inventory; they have not been regenerated for these repairs.
- Guarded Transfer (40) and Package Grouping (49) carton support repair:
  box_1 Y changes from 0 to 0.9 m, matching the actual transformed belt top.
  Four new mesh checks fail before repair and pass after: carrying-footprint/
  surface contact and separate-equipment solid clearance for each carton.
  All 149 geometry/reference checks pass, build has zero warnings/errors, both
  initial-state contracts pass. Rebuilt native normal-shell instances inspected
  from all five wide angles and carton top/FR close views for both scenes.
  Cartons now visibly rest on the belts. This placement repair does not accept
  transfer motion, counter grouping, protective-function behavior or the other
  misplaced accessories. Evidence: transfer-carton-{red-build,red-geometry,
  build,geometry,guard-contract,group-contract,guard-native,group-native}.log.
  Full catalog goal remains active.
- Press-Count Lamp / Demo 1 (scene 42): native five static views show clear,
  grounded stands. Normal Run starts the authored two-network CTU program.
  Original control toggles rather than pulses: three native clicks leave the
  input true and threshold_lamp false (two rising edges). The existing action
  ID/binding is retained, but type is pulse, label is Pulse count button and
  plate PULSE. Guide now states the three-count starter preset and distinguishes
  Stop retaining count from Reset clearing it. Five new integration checks use
  the scene action, actual authored ladder, mapper and scan session together;
  four fail before repair, all pass after. Fresh native Run, two rail pulses
  (lamp off), third 3D press (lamp green, input released), Stop (off), Run (green
  from retained count), Reset (both points false, scan zero) and FR close plate
  inspected. Stands' geometry is unchanged; five views are from the original
  layout, with a fresh final close view after label repair. All 145 geometry/
  reference checks and 142 controller tests pass, no live transport constructed;
  build zero warnings/errors. Press-count initial-state contract and inspection
  toggle's two reference contracts pass. Shell verifies 77 scenes/294 assets but
  retains four headless position errors and missing-workspace warning. The new
  startup guidance is readable in the actual native window. Evidence:
  catalog-42-native.log (original), press-count-fixed-native.log (final),
  press-count-{red-build,red-geometry,build,geometry,controller,contract}.log,
  inspection-toggle-{build,contract,shell}.log. Goal active.
- Scenes 38-41 and native editor workflow (2026-10-04): all four have native
  FR/FL/RL/RR/T inspections. Robot CNC Tending's robot approaches the closed rear
  of the enclosure; loading reach, workpiece attachment and door/chuck transfer
  remain unverified. Normal Start blocks without a controller. Inspection Light
  Toggle's separated stands are clear; its START plate is now TOGGLE, confirmed
  in a fresh native FR close view. Basic Logic opens an empty exercise. Through
  the real editor UI, added one NO toggle_button_pressed contact and a SET coil
  for inspection_light_on, verified/loaded offline, returned to scene, ran and
  pulsed the input: the rendered beacon lit. Normal Stop extinguished it; Reset
  restored all three false points and scan zero. This temporary network was
  discarded through the unsaved-work prompt; it does not implement or validate
  the odd/even toggle lesson. A stopped pulse remains queued until an accepted
  scan; that alone is not a stuck-button defect. Startup guidance now explicitly
  explains empty exercises and Online > Verify + load offline before Run.
  Guarded Pallet Transfer's carton is buried beneath the belt (native top/FR
  close); its sensors and light-curtain/gate props sit outside the conveyor route.
  Guard input toggle and Reset worked; full transfer and protective behavior are
  unverified. Robot Cell Safe Restart's robot occupies the CNC envelope; its wall
  prop does not form a cell perimeter. Persistent reset_complete toggle is not a
  spring-return reset request, and outputs bind only to beacons, not robot motion.
  Native toggle persistence/Reset checked; edge/restart/motion behavior remains
  unaccepted. Historical bounds counts are screening evidence, not solid proof.
  Evidence: catalog-34-native.log (38/39 and temporary editor test),
  catalog-39-final-native.log (fresh label and 40/41). Screenshots individually
  inspected; logs alone do not establish acceptance. Goal active.
- Service Door Shutter (scene 33): original five views and close button views
  confirm the close enclosure overlaps its guide, the green beacon occupies
  the curtain, and all three plates read START. Controls now stand 1 m forward
  of the shutter plane, with OPEN/STOP/CLOSE plates; both signal stands sit
  beyond the right-hand equipment envelope. Fresh normal native five views
  and operator FR close view inspected. The indicators explicitly show raw NC
  signals, not reached-limit lamps; the description no longer claims cable
  monitoring. Original rendered Close blocks without a ladder controller.
  Standalone motion review also reproduced stale 100% position during travel
  and a Close reversal that initially opens farther. Opt-in fromCurrent motion
  now captures the actual adapter input pose at each step; sequencePositionOnly
  prevents a second autonomous travel source. Reference-only positionFeedback
  updates a declared SIM REAL and PC BOOL NC inputs, refusing PLC-owned targets
  and skipping controller/external clocks. Fresh native preview shows opening
  to 60% closed, Stop holding across another reference second, Close starting
  at that pose and moving to 68%, resumed real-time closing to 100%, unheld
  opening to 0%, five open-endpoint views and Reset back to 100%. Eleven new
  checks cover layout/floor/plates, 101 curtain poses, raw polarity, no autonomous
  creep, intermediate feedback, Stop, both reversal directions and open endpoint.
  The compressed slat animation remains illustrative; continuous animation,
  physical limit/cable faults and loaded-controller door operation are unaccepted.
  Build has zero warnings/errors; all 140 geometry/reference checks, two door
  contracts, 142 controller tests, 19 motion checks, rendered controls and shell
  pass. Geometry has no warnings/errors; shell retains four headless position
  errors and its missing-workspace warning. Local evidence: service-door-native.log,
  service-door-plant-native.log (reproduction), service-door-fixed-plant-native.log,
  service-door-{build,geometry,contract,controller,motion,controls,shell}.log.
- Shipping Pallet Accumulation (scene 32): native five views plus sensor top/FR/RL
  close views inspected. Pallet support and sensor/conveyor support intersections
  remain open; 29 bounds candidates require solid/contact measurement. Native
  Toggle auto changes auto_mode true to false; Jog blocks without a controller.
  Full accumulation/jog/Stop/Reset motion remains unverified.
- Bottle Shuttle Conveyor (scene 34): native five views and bottle top/FR close
  inspected. Bottle label text overlaps and extends past its panel; bottle/belt
  contact and both sensor/conveyor attachments still need measurement. The 39
  bounds candidates are screening findings. Normal Start blocks without a ladder
  controller; full round trip, reversal, Stop and Reset remain unverified.
- Chemical Tote Finishing Line (scene 35): native five views and filler top/FR
  close inspected. Station columns occupy the belt corridor; its 29 candidates
  include conveyor/filler (7), capper (5), labeler (5), vision (12). Tote support,
  nozzle/cap alignment and full transfer through all stations remain unverified.
  Normal Start blocks without a ladder controller. FAIL/open.
- Dual-Spindle Plate Cell (scene 36): native five views and metal plate top/FR
  close inspected. The shared plate is offset from both spindle axes and below
  their separate yellow vise coupons; fixture/slide support also needs measurement.
  Two candidates concern drill_a base/transfer frame. Both adapters remain rotation
  only, so actual dual feed/retraction and transfer are unaccepted. Normal Start
  blocks without a controller. FAIL/open. Native scenes 34-36 evidence is in
  catalog-34-native.log; scenes 32-33 original review in catalog-32-native.log.
  Coverage is 37/77 inspected, 40 pending, including failed scenes.

- Drill fixture/feed follow-up: the opt-in fixtureDrill installation uses the
  delivery's single yellow stock mesh in the separate workpiece equipment root,
  at its measured vise center; the second buried fixture is gone. Its bit was
  originally at Y=1.610 inside stock spanning Y=1.585..1.695. Raising the spindle
  home 235 mm gives 150 mm clearance; a 245 mm downstroke ends at Y=1.600 inside
  the coupon with 15 mm remaining above its bottom. SpindleFeed retains axial
  feed when rotating and retains rotation when a position setpoint changes.
  Run alone rotates without automatic feed; the head/guard/table/vise stay fixed.
  Twelve added geometry/reference checks cover single stock ownership, placement,
  home clearance, 101 rotating feed poses, bit/chuck travel, quill/bearing overlap,
  fixture clearance, reset, bottom feedback, stopped pose and restart blocking.
  Generic Stop intentionally holds its current pose; the misleading Stop and
  retract label now reads Stop spindle and hold, and the guide states that
  behavior. Start now also requires drill_at_top, preventing bottom restart from
  asserting top feedback on an unmoved spindle. Simulator Reset restores home.
  Fresh normal native FR/FL/RL/RR/T and stock FR close views inspected. Actual
  3D left/right hand buttons change the corresponding PC points; the 3D cycle
  button reports no ladder controller loaded and leaves drill_run false. Normal
  controller lesson execution remains unaccepted. Standalone QA shows home,
  intermediate downstroke and bottom in four close side views; top stock focus
  is occluded by the head. Stop holds bottom across two stepped reference seconds,
  Run stays blocked there, and Reset visibly restores home. A subsequent reference
  cycle retracts through an intermediate pose, then resumes in real time to
  top/complete; a separate wholly unheld cycle also completes. Held poses do not
  constitute continuous animation evidence. No material removal, safety-rated
  two-hand, guard feedback or simultaneous/continuous-hold model is established;
  the lesson hint explicitly identifies its requests as latched demonstration inputs.
  Build 0 warnings/errors; 129 geometry/reference checks, four drill contracts,
  19 plant-motion checks, 142 controller tests, rendered controls and shell pass.
  Geometry log has no warnings/errors; shell retains four headless position errors
  and the existing missing-workspace warning. Evidence in rungproof-next/.tools:
  drill-datum.log (original actual mesh bounds), drill-feed-native.log,
  drill-feed-plant-native.log and drill-feed-{build,geometry,contract,controller,
  motion,controls,shell}.log. Both owned reviewers exit 0; user Demo 1 remains open.
- Twin-Container Pallet Cell (scene 31): fresh normal native five views and
  receiver-focused top/FR views show the receiver backstop crossing the belt end.
  The pallet visibly appears raised off its belt; its contact datum needs measurement.
  Its 23 candidates include 13 conveyor/receiver and six conveyor/photoeye pairs;
  these remain screening findings, with sensor/brace close inspection outstanding.
  Normal Run opens NO CONTROLLER LOADED. Full robot/container transfer, receiver
  seating and outbound pallet travel remain unverified. This scene is FAIL/open.
  Coverage is now 32/77 inspected, 45 pending including failures.

- Earlier drill inspection and permissive checkpoint:
- Fixture-Safe Drill Station (scene 30): normal Windows FR/FL/RL/RR/T
  static views and workpiece-focused top/FR close views inspected. **FAIL/open:**
  the mapped press already owns a yellow coupon in its vise; the scene's
  separate `drill_workpiece` is another scaled clamped-plate fixture underneath
  the table, with 24 original AABB candidates (screening, not solid proof).
  Native held preview reaches `drill_at_bottom=true` without visible axial
  spindle travel. The adapter is ContinuousRotation, so SetPositionNormalized
  ignores the declared feed motion. Stop and retract removes `drill_run` and
  turns the light red but remains `drill_at_bottom=true`, `drill_at_top=false`
  after another two seconds of stepped reference time; no retraction exists
  in that action. Normal Run opens NO CONTROLLER LOADED. Both declared reference
  contract cases pass despite these visual/stop failures.
  Three generic START plates now read LEFT HAND, RIGHT HAND and DRILL CYCLE;
  fresh normal native close views verify all three fit their plates. The QA
  action bar now anchors at the viewport bottom because wrapped point values
  overlapped Run/Stop/Reset; native controls and upward-opening action popup
  are visible without that overlap.
  Exposing Run reproduced an additional bypass: RunDefault entered the default
  sequence directly with both hand requests false. It now dispatches the
  matching declared Start action, preserving its permissives and blocked
  message. An inventory of all 77 catalog entries finds 13 default sequences,
  each with exactly one matching Start action.
  Four new negative cases fail before the fix (both missing, either hand only,
  missing stock with both requests); all now pass. Valid reference completion
  and unconditional sump start also pass. Fresh native Run blocks with both
  missing and with left only, then starts with both set, reaches real-time
  reference completion and resets. These are standalone QA observations;
  they do not establish controller lesson execution or safety-rated two-hand
  behavior. Requests remain toggles, with no simultaneous/continuous-hold
  model established. One attempted rendered-button click in standalone QA
  did not change the input; normal rendered-button interaction remains open.
  Build 0 warnings/errors; 117 geometry/reference checks, two drill contracts,
  19 plant-motion checks, 142 controller tests and rendered controls pass.
  Shell passes with four existing headless position errors. Evidence under
  rungproof-next/.tools: safe-drill-native.log, safe-drill-plant-native.log,
  safe-drill-label-native.log, safe-drill-layout-native.log,
  drill-permissive-before.log, drill-permissive-final-native.log and
  drill-permissive-{build,geometry,controller,contract,motion,controls,shell}.log.
  All isolated drill reviewers exit 0; user Demo 1 preserved. Coverage now
  31/77 inspected, 46 pending including failures. Axial feed, single supported
  workpiece, stop semantics and guard/permissive feedback remain required.
- Sump piping follow-up: the opt-in scene installation now connects actual
  tank/pump flange faces with a suction offset and an upward discharge elbow,
  aligns the valve and instrumented spool horizontally, and grounds five pipe
  shoes with attached posts. The valve/spool clear the tank shell and ladder.
  Two broader 45-degree suction bends replaced an initially folded connector;
  a local curvature guard rejects tube radius exceeding the bend radius.
  The startup camera exposes the piping. Fresh normal Windows FR/FL/RL/RR/T
  wide views and pump-focused top/FL/RL/FR close views were inspected after
  the final bend correction. Joins and support contact are visible in the
  close views; occluded surfaces are not accepted from a single angle.
  Normal Run again opens NO CONTROLLER LOADED. Six new actual-mesh checks
  fail on the original scene placement and pass after repair. Build has
  zero warnings/errors; all 111 geometry checks, one sump reference contract,
  19 motion checks, 142 controller tests and rendered controls pass. Shell
  passes with four existing headless position errors. The isolated native
  reviewer exits 0 and user Demo 1 stays open. Evidence under
  rungproof-next/.tools: sump-piping-before.log, sump-piping-geometry.log,
  sump-piping-final-native.log and sump-piping-{build,controller,contract,
  motion,controls,shell}.log. **Still FAIL/open:** the closed vessel does not
  establish a sump, the named floats are tuning-fork switches with no proven
  process fittings, the low probe extends below the floor, and full native
  level motion/controller execution remains unverified. Annular visual joins
  do not establish an internal fluid passage, pressure rating or discharge
  destination. Coverage remains 30/77 inspected, 47 pending including failures.
- Fume speed / Stop follow-up: `fan_speed_percent` now binds to the rotor
  through opt-in `speedPercent`, clamped to 0..100% of the existing 720 rpm
  nominal animation. Unbound rotating assets keep their authored speed. The
  separate BOOL run command still gates motion. Actual six-blade world transforms
  reproduce failures at 35%, 65% and zero before repair; full nominal rotation
  already worked. All ten new checks now pass, including numeric limits, run
  false, paused controller clock, Reset and standalone Stop/Run. A single
  imported hub pivot correctly owns all blades and shaft; no asset rebuild.
  Native QA preview inspected running 35% from FR/FL/RL/RR/T, then 65%/100%
  and the matching single speed indication. Native Stop originally restarted
  the rotor immediately because reference rules reasserted its command. The
  standalone boolean-panel Stop latch now suppresses those rules until Run or
  Reset, projecting the declared initial output values while retaining inputs.
  Fresh native Stop holds the rotor/off outputs through a selector change;
  Run resumes at retained 65%; selector Off retains independent light; Reset
  restores initial inputs, rotor and indications. Selected-controller rules
  remain bypassed and output ownership is unchanged. These previews use the
  reference runtime, not an authored/loaded PLC program. Native snapshots do
  not measure rpm or prove blade/guard collision clearance through every frame.
  Hood/duct, actual inspection illumination and normal lesson execution remain
  open. Build 0 warnings/errors; 105 geometry checks, five fume contracts,
  19 plant-motion checks, 142 controller tests and rendered controls pass.
  Shell passes with its four existing headless position errors and expected
  missing-workspace warning. Evidence under rungproof-next/.tools:
  fume-speed-before.log, fume-stop-before.log, fume-speed-geometry.log,
  fume-speed-native.log, fume-speed-stop-native.log and fume-speed-*.log.
  Both isolated native previews exited 0; user Demo 1 stays open. Coverage
  remains 30/77 inspected, 47 pending, including failures. Sump remains FAIL.
- Original Sump Dewatering Pump finding (scene 28, piping follow-up above): native FR initial / FL / RL / RR / T views
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
  accumulated flags; no rule-content rewrite was needed. The initially missing
  rendered speed binding and preview Stop failure are repaired in the follow-up above.
  Inspection light is a single-tier beacon; extraction hood/duct and actual
  illumination are not modeled. Guard recognition is not physical safety proof.
  Thus spacing/label/input-pointer observations are bounded; complete extractor
  identity and normal lesson controller execution remain open. Reference preview
  speed projection and Stop/Reset now have the bounded follow-up evidence above.
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
| 13 | `lab-11-13-xy-palletizing` | 0 | FR/FL/RL/RR/T | Repaired; static five views and sampled all-moving-part sweep pass; native five motion views with occlusions recorded, Stop/Reset and three labeled 3D inputs checked. Actual carton transport/home feedback open |
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
| 28 | `lab-2-14-sump-pump` | 41 (original) | Final repaired FR/FL/RL/RR/T wide + top/FL/RL/FR pump close | Partial piping repair: joined measured ports, aligned valve/spool and grounded supports; still FAIL: buried low probe, float fitting/identity and sump vessel open; normal Run unloaded; full level motion pending |
| 29 | `lab-2-15-fume-extractor` | 0 | FR/FL/RL/RR/T static and running 35%; close plate; speed states; native preview Stop/Run/Off/Reset | LIGHT REQUEST, speed binding and preview Stop repaired; six-blade transform checks pass. Open: beacon substitutes light, hood/duct absent, normal Run unloaded; reference preview is not controller lesson acceptance |
| 30 | `lab-2-16-safe-drill` | 24 original / 0 repaired | Native repaired FR/FL/RL/RR/T; stock FR close; normal 3D hand/cycle controls; held feed/bottom four close sides; Stop/Reset/restart; unheld completion | Fixture/feed and honest Stop-hold semantics repaired; normal cycle blocks without controller. Top stock view occluded by head; guard/two-hand safety behavior is not modeled |
| 31 | `lab-2-17-pallet-robot` | 23 | Native FR/FL/RL/RR/T; receiver top/FR close; normal Run | FAIL/open: receiver backstop intersects conveyor; pallet appears raised off belt. Sensor/brace candidates and robot transfer/reach remain unresolved. Run unloaded |
| 32 | `lab-2-18-pallet-pickup` | 29 | Native FR/FL/RL/RR/T; sensor top/FR/RL close; auto toggle and jog | Open: pallet support and sensor/conveyor mounting need measurement; Jog blocks unloaded; full motion unverified |
| 33 | `lab-2-19-service-door` | 54 original / 0 repaired | Repaired native FR/FL/RL/RR/T; operator FR close; held opening/Stop/reverse; real-time endpoints; open five views; Reset | Layout/plates and reference reversal/position feedback repaired; raw NC signal displays explicit. Physical limit/cable behavior, compressed slat geometry and loaded-controller operation unaccepted |
| 34 | `lab-2-20-bottle-shuttle` | 39 | Native FR/FL/RL/RR/T; bottle top/FR close; Start | Open: overlapping bottle label text; contact and sensor mounts need measurement. Normal Start unloaded; round-trip motion unverified |
| 35 | `lab-2-21-tote-finishing` | 29 | Native FR/FL/RL/RR/T; filler top/FR close; Start | FAIL/open: station columns occupy belt corridor; tote support, station alignment and full transfer unverified. Start unloaded |
| 36 | `lab-2-22-dual-spindle` | 2 | Native FR/FL/RL/RR/T; plate top/FR close; Start | FAIL/open: plate offset below separate drill coupons, fixture/slide mounting unresolved; adapters rotation only. Start unloaded; feeds and transfer unverified |
| 37 | `lab-2-23-parcel-sorter` | 174 | FR/FL/RL/RR/T | Repaired static/declared plant path; normal Run lacks controller |
| 38 | `lab-2-24-robot-cnc` | 29 | Native FR/FL/RL/RR/T; Start | Open: robot behind closed CNC back; workpiece support, reach, door/chuck transfer unverified; Start unloaded |
| 39 | `lab-2-25-inspection-toggle` | 0 | Native FR/FL/RL/RR/T; repaired plate FR close; real editor create/load/Run/pulse/Stop/Reset | TOGGLE plate repaired, clear stands. Loaded one-network SET test lights beacon; discarded test is not odd/even lesson acceptance |
| 40 | `lab-3-01-guarded-pallet-transfer` | 20 (historic) | Native FR/FL/RL/RR/T; final carton top/FR close; earlier guard toggle/Reset | Carton support repaired and re-inspected. FAIL/open: sensors/curtain/gate outside conveyor route; transfer/protective behavior unverified |
| 41 | `lab-3-02-robot-cell-safe-restart` | 42 | Native FR/FL/RL/RR/T; persistent reset toggle/Reset | FAIL/open: robot occupies CNC; no cell perimeter; reset toggle vs edge request mismatch; only lamp output bindings, no robot-motion binding |
| 42 | `lab-4-01-press-count-lamp` | 0 | Native FR/FL/RL/RR/T; final FR close PULSE; normal Run, rail/3D pulses, Stop/Run/Reset | Pulse/plate repaired. Three presses light authored CTU lamp, Stop removes output, Run retains count, Reset clears; five integration checks pass |
| 43 | `lab-4-02-counter-reset-lamp` | 0 | Native FR/FL/RL/RR/T | Static stands clear. Precomputed count_reached and persistent reset toggle; actual counter/reset workflow unverified |
| 44 | `lab-4-03-repeat-cycle-counter` | 0 | Native FR/FL/RL/RR/T | Static spacing clear. Precomputed cycle_count_complete; outputs only lamps, CNC motion absent; bounded-cycle behavior unverified |
| 45 | `lab-4-04-sequence-light-tower` | 0 | Native FR/FL/RL/RR/T | FAIL/open: promised four-color sequence has three-tier beacons and two green-only bindings; behavior unverified |
| 46 | `lab-4-05-dual-input-count-window` | 0 | Native FR/FL/RL/RR/T | Static stands clear. Precomputed channel-ready toggles; raw counting/window workflow unverified |
| 47 | `lab-4-06-multi-press-confirmation` | 0 | Native FR/FL/RL/RR/T | Static stands clear. Precomputed pattern-ok toggles; raw press order/timing workflow unverified |
| 48 | `lab-4-07-parking-garage-entry` | 20 | Native FR/FL/RL/RR/T; replacement readout five focus views | Readout replaced/repositioned; five native focus views (RL obscured). FAIL/open: motor-starter vehicle, substitute barrier/wall, no occupancy numeric binding or barrier motion acceptance |
| 49 | `lab-4-08-package-grouping` | 118 (historic) | Native FR/FL/RL/RR/T; final carton top/FR close | Carton support repaired and re-inspected. FAIL/open: grouping/release outputs only lamps; separated receiver/stop/sensors and transfer behavior unverified |
| 50 | `lab-4-09-chain-drive-lift` | 145 | Native FR/FL/RL/RR/T | FAIL/open: conveyor/lifts overlap, floor carton, disconnected pallet load; hoist is scissor table; chain/lift outputs only lamps; motion unverified |
| 51 | `lab-4-10-cookie-packaging` | 146 | Native FR/FL/RL/RR/T; food top/FR close | FAIL/open: CNC occupies belt, packaged meat below indexing conveyor; lamp-only outputs, cookie count/transfer/packaging unverified |
| 52 | `lab-4-11-barrel-fill-station` | 143 | Native FR/FL/RL/RR/T; barrel top/FR close | FAIL/open: tank occupies conveyor, barrel is motor starter; disconnected fill route; lamp-only outputs, fill/transfer unverified |
| 53 | `lab-4-12-cable-cut-length` | 21 (prior inventory) | Native FR/FL/RL/RR/T; repaired readout five focus views; 3D inputs/Reset | Readout now grounded LENGTH / NO MEASUREMENT, front readable/Top clear; rear details blocked. CABLE/LENGTH/HOME plates and matching PC points verified. FAIL/open: payoff shutter, dancer/cutter trays, unbound encoder, no continuous cable measurement/cut route; outputs only lamps |
| 54 | `lab-5-01-delayed-lamp` | 0 | Native FR/FL/RL/RR/T; normal Run, rail/3D toggles, Stop/Reset | Authored TON initially off then green; 3D clears request, Stop removes output, Reset clears points/scan; exact native interval unmeasured; selector/plate mismatch open |
| 55 | `lab-5-02-timed-lamp-off` | 0 | Native FR/FL/RL/RR/T | Static spacing clear; persistent start_pulse, precomputed time_active, ambiguous START plates; timer behavior unverified |
| 56 | `lab-5-03-rotary-flasher` | 0 | Native FR/FL/RL/RR/T | Static spacing clear; pushbutton instead of rotary selector, manual flash_tick; flashing/off behavior unverified |
| 57 | `lab-5-04-alternating-lamps` | 0 | Native FR/FL/RL/RR/T | Static spacing clear; PC phase toggle; timer alternation/exclusivity unverified |
| 58 | `lab-5-05-variable-flash-rate` | 0 | Native FR/FL/RL/RR/T | Static spacing clear; independent fast/slow toggles, simultaneous selection/timing unverified |
| 59 | `lab-5-06-running-light-tower` | 0 | Native FR/FL/RL/RR/T | FAIL/open: single green-only output cannot walk tower levels; persistent step_pulse; behavior unverified |
| 60 | `lab-5-07-pedestrian-crossing` | 26 | Native FR/FL/RL/RR/T | FAIL/open: vertical wall instead of road, amber beacons instead of signal heads; vehicle_stop green binding; timed crossing unverified |
| 61 | `lab-5-08-drawbridge-control` | 43 | Native FR/FL/RL/RR/T | FAIL/open: scissor table, guard and shutter instead of bridge route; only lamp outputs, no bridge motion |
| 62 | `lab-5-09-bag-indexing-conveyor` | 37 (historic) | Repaired native FR/FL/RL/RR/T; carton top/FR close | Carton belt support repaired. FAIL/open: carton/bag identity, outside sensors, only lamp outputs; indexing/reversal unverified |
| 63 | `lab-5-10-coating-line` | 97 | Native FR/FL/RL/RR/T | FAIL/open: CNC occupies belt, disconnected coating/spray/ventilation props; only lamp outputs, process unverified |
| 64 | `lab-6-07-luggage-weight-sort` | 110 | Native FR/FL/RL/RR/T; replacement readout five focus views | Carton support repaired earlier; WEIGHT readout replaced and five focus views inspected (RL obscured, RR partly obscured). FAIL/open: disconnected weighing/rejecting layout; no numeric weight/class |
| 65 | `lab-6-08-hand-dryer` | 634 | Native FR/FL/RL/RR/T; replacement readout five focus views | PROGRESS readout replaced/repositioned; five focus views (FL text partly obscured, RL obscured). FAIL/open: substitute heating shutter and disconnected fan/panel/bottle; no remaining-time numeric binding |
| 66 | `lab-9-01-sum-function` | 0 | Native FR/FL/RL/RR/T; close front; 3D A/B clicks; actual reference Open/Run/Stop/Reset | Two PC DINT inputs and live SUM result; 2+5=7 observed. Seven grounded, clear props. Global-tag reference FB supplied; exercise remains opt-in; FB parameter/instance semantics and independent asset approval open |
| 67 | `lab-9-02-product-function` | 0 | Native FR/FL/RL/RR/T; close front; actual reference Open/Run/Stop/Reset; validity loss | Two PC DINT factors and live PRODUCT; 2*5=10 observed. Seven grounded, clear props. Sidebar input proof; individual 3D clicks unverified here. Global-tag FB reference opt-in; FB parameter/instance semantics and independent asset approval open |
| 68 | `lab-9-03-sum-and-counter-function` | 0 (historical) | Native FR/FL/RL/RR/T; close operand/result views; actual 3D operand clicks; Project Open/Verify + Load; Run/Stop/Reset | CNC removed; typed DINT operands/sum/count and live readouts added. Opt-in reference displays 2+5=7 and one held completion count, Stop zeros image, Run republishes retained count, Reset clears. Eleven integration/clearance checks pass. Open: independent reusable-asset approval; manual call-complete feedback; exercise requires authored/explicit reference logic |
| 69 | `lab-9-04-function-selector` | 0 (historical) | Final native FR/FL/RL/RR/Top, close FL; actual six 3D inputs; Project Open, Run, invalid choice, Stop/Reset | Live DINT A/B/choice/RESULT and opt-in FB routing to SUM/PRODUCT; observed 7/10 and invalid 99 clears validity. Native picking conflict repaired by moving readouts behind buttons; supports and separate-equipment clearance pass. Open: source-selector parity and FB instance/parameter semantics unverified; QA close/top cropping documented |
| 70 | `lab-9-10-box-volume` | 46 (historical) | Native FR/FL/RL/RR/T; replacement fixture and readout five focus views each; actual 3D buttons/Reset | Static three-head fixture replaces shutter; carton supported on bench, CNC removed and rear readout view cleared. Seven geometry checks and LENGTH/WIDTH/HEIGHT manual inputs/Reset pass. Open: no numeric dimension acquisition, volume calculation or live MEASUREMENT value; independent asset approval pending |
| 71 | `lab-9-11-pallet-counting` | 86 | Native FR/FL/RL/RR/T | Carton/fixture/readout geometry repaired and five views/details inspected. Live DINT count/readout FR/FL and invalid/five-edge/held/permissive/Stop/Run/Reset native checks pass. Optical classification/pallet travel/CNC integration open |
| 72 | `lab-9-12-ev-charging-manager` | 95 | Native FR/FL/RL/RR/T | FAIL/open: shutters/fluid props instead of EV charging route; energy pulse/accumulation contract absent |
| 73 | `scene-1-conveyor-stop` | 34 | Native FR/FL/RL/RR/T | Carton belt contact/load-end footprint repaired; native five wide/Top/FL close and Demo 3 Run/Start/photoeye/Stop/Reset rechecked; full clearance open |
| 74 | `scene-2-conveyor-pusher` | 88 | Native FR/FL/RL/RR/T | Carton belt contact/load-end footprint repaired; native five wide/Top/FL close rechecked; no receiver, pusher/photoeye motion clearance unresolved |
| 75 | `tank-high-low` | 60 | Native FR/FL/RL/RR/T | Disconnected pump/elevated inlet, external probes, opaque tank; fill/drain behavior unverified |
| 76 | `tank-level` | 52 | Native FR/FL/RL/RR/T | Same disconnected piping/probe mounting; initial 42 percent / 10.72 mA visible, dynamics unverified |
| 77 | `tank-radar` | 80 | Native FR/FL/RL/RR/T; repaired radar five focus views | Radar flange/head mounting and antenna-to-surface distance/beam repaired (sampled checks); 35% native range 3.10036. FAIL/open: empty ladder Run, disconnected inlet/outlet/drain route, opaque internal beam; rear-left mount partly obscured |

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
