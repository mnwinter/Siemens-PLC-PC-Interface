# Cumulative Lab Progression

## 2026-10-06 tote-finishing controller-clocked travel

A direct plant probe reproduced the next gap: four seconds of PLC conveyor_run left the tote stationary because all load translation existed only in the standalone sequence. Added a renderer-neutral ToteTransferPlantModel and an opted-in adapter for controller operation. Accepted ticks up to 20 ms now drive both belt and tote at prescribed 0.75 m/s; the general conveyor callback is disabled for that clock. Six PC points publish position, four installed station windows and retained exit arrival. Home and endpoint are checked against the delivered belt footprint. Command withdrawal and Stop hold position; Run continues the retained load; held Run cannot wrap or discard it at the exit; Reset reloads the infeed.

The explicit legacy preview remains available for its existing geometry checks. Twenty-four focused checks pass: twelve Start/commanded-travel checks and twelve delivered-mesh/standalone-preview checks. Final build passes with zero warnings/errors; the shared-helper guarded regression passes all 33 focused checks and all 71 scene contracts pass with zero failures. Fill volume, cap application, label application, inspection and complete PLC station sequencing remain open; no process completion is fabricated from tote arrival. Fresh native inspection remains pending after the Escape stop.


## 2026-10-06 tote-finishing Start binding repair

The 3D Start action was rejected even with a running compatible ladder because the scene omitted its explicit controllerStartBinding. A deterministic command probe reproduced the missing Start pulse twice. Adding `operator.start` fixes the action; five checks now prove Run alone does not pulse Start, the 3D action reaches the matching ladder input for one scan, Reset clears state and a stopped controller rejects Start. The twelve existing delivered-mesh/standalone-preview checks also pass, including 5,000 two-millisecond travel samples. Build and focused verification pass. This repairs command delivery only: normal controller-driven tote transport, capped fill/volume, cap application, label application, inspection and process restart/resume remain open. Latest native command and visual inspection remain pending after the Escape stop.


## 2026-10-06 guarded-transfer offline PLC reference

The explicit `--audit-guarded-layout` command now generates `.tools/plant-review-guarded-transfer.rpproj.json`, a compatible 20 ms ladder document. Its PLC evaluates the three manual permissives and removes transfer_run at supported exit completion. Thirty-three focused checks pass, including all eight input combinations, individual permissive losses during motion, normal scan-driven transfer across both optical routes, Stop/Run retention, completion without held-input restart and Reset. Build and app-shell validation pass (77 scenes, five demos, 294 assets, disconnected). Default exercise programs remain blank. Current carton-runtime full geometry exited 0 with no failed geometry checks; all 71 scene contracts passed with zero failures. The later reference audit is separately proved by 33 focused checks. Fresh native views and physical/protective acceptance remain pending.


## 2026-10-06 guarded-transfer retained carton runtime

Scene 40 now uses a dedicated `guardedTransfer` runtime with nine symbolic points. The carton starts fully supported at the infeed, travels at a prescribed 0.45 m/s only under the PLC transfer_run command, and clamps with its complete footprint 10 mm inside the delivered belt exit. It stays visible instead of wrapping or disappearing. PC feedback reports carton position, overlap with each installed optical route and retained completion; manual path-clear and guard fixtures remain separate. Belt and carton share accepted ticks up to 20 ms, with the ordinary conveyor physics callback disabled to avoid duplicate travel. Stop retains pose and zeros modeled speed; Reset restores home and completion.

Build, seventeen focused checks, initial-state scene contract, controller regression and help validation pass. The prior full geometry run exited 0 before this runtime change. Current-build full geometry is running in `.tools/guarded-plant-full-geometry.log`; its result is pending. Fresh Windows views, normal PLC-program-driven transfer, guard/curtain behavior and mechanical approval remain unverified.


## 2026-10-06 guarded-transfer drive-command repair

Scene 40's PLC `transfer_run` previously drove only a lamp. Added its `running` binding to the existing conveyor controller. The focused audit now passes ten checks: six delivered-mesh placement/support checks plus initial off, PLC on, command withdrawal and Reset for the drive command. Build, initial-state scene contract and help validation pass. A fresh corrected full geometry run is active in `.tools/guarded-current-full-geometry.log`; its terminal result is not yet known. The carton remains stationary, and manual guard/path fixtures do not prove protective detection or interlocking. Fresh native views remain pending after the Escape stop.


## 2026-10-06 guarded-transfer layout repair (native pending)

Scene 40 used a foot-switch surrogate for its access gate, with both photoeyes and the curtain outside the conveyor route. Replaced the scene gate mapping with the existing mesh swing gate at the access side, rotated the existing light-curtain pair across the belt, and placed both photoeyes within its X extent. Retained the supported home carton and the manual boolean fixture inputs. Added delivered-mesh checks for beam height/span and gate identity/clearance. Build, help validation, the focused six-check delivered-mesh audit and the scene initial-state contract pass. The first broad regression (before new checks) exited 0; the second exited 1 on the two superseded per-dash photoeye checks; it is not a pass. Current focused checks aggregate the dashed photoeye witness route correctly. New Windows multi-angle views remain pending after the native Escape stop. No carton transport, physical interlocking or safety-rated detection is claimed.


Radar REAL-feedback PLC reference checkpoint (2026-10-06, native review OPEN):
--audit-radar-layout explicitly generates ignored .tools/plant-review-radar.rpproj.json.
Default exercise remains blank. Local stations now publish PC-owned cycle_request
and manual_drain_request; PLC ladder owns pump/drain commands. The illustrative
reference fills to 80% REAL radar level and drains to 20%, retaining hysteresis
phase across Stop/Run. Manual drain request requires cycle enable and excludes
filling. Echo health remains idealized true; no echo-loss/noise process is proved.
Thirty-two geometry/inspection/PLC-reference checks PASS in
.tools/radar-reference-audit.log, including three drain/fill transitions with the
actual valve pointer, idealized current/level agreement, idle without request,
Stop holding surface/range/scan with closed pointer, retained-phase Run, request
removal, manual drain and Reset to 35% with requests cleared. Source exercises
are not silently filled. Full scene contracts 71 PASS/0 FAIL in
.tools/radar-reference-contracts.log; build zero warnings/errors, help 294/77 valid.
The piping/inspection geometry regression completed 1001 checks PASS in
.tools/radar-piping-geometry-regression.log. That broad run and the focused
reference together provide bounded offline evidence; neither proves native
appearance or hydraulic/physical behavior. New piping, inspection view, operator
request behavior and full native REAL-feedback cycle remain uninspected while
Windows input is stopped after physical Escape. Scene 77 and the full goal stay OPEN.

Radar tank piping/inspection checkpoint (2026-10-06, native review OPEN):
Scene 77 now opts into the existing tank-piping installation used by the other
tank lessons: measured pump discharge/inlet spool faces, diagonal tank nozzle,
explicit supply boundary/support, outlet flange and grounded full drain valve.
The valve's quarter-turn pointer binds to drain_valve_open; the first focused
run caught that missing binding and it was corrected. Existing radar roof/head
mounting, antenna/surface range datums and symbolic command ownership are retained.
--audit-radar-layout: 24 focused checks PASS in
.tools/radar-piping-inspection-audit.log: flange/route continuity, grounded/attached
pipe/valve supports, equipment clearances, pointer sweep/closed pose, sampled
radar fill/drain/range and Stop/Reset, plus presentation inspection state.
A SIM-only tank_inspection_view action ghosts shell/roof without removing meshes,
changing transforms or changing measured range; a second toggle restores authored
materials. It does not model a physical tank opening or any PLC command.
Nine equipment items; aggregate catalog count 621. Build zero warnings/errors;
help validates 294 assets/77 scenes. New piping, drain valve and transparent view
have NOT been visually inspected. Windows input remains stopped after physical
Escape. Radar REAL-threshold PLC reference/full native cycle remains unfinished.
Full current geometry regression is running in
.tools/radar-piping-geometry-regression.log. The preceding EV-reference geometry
run finished PASS (987 checks); it is not full verification of this radar change.
No hydraulic ratings, calibrated radar/echo quality or hardware acceptance claimed.
Scene 77 remains OPEN until native inspection and the controller review are done.

EV PLC reference/readout checkpoint (2026-10-06, native review OPEN):
--audit-ev-layout now explicitly generates ignored .tools/plant-review-ev.rpproj.json.
The blank default exercise and five-demo catalog are preserved. The reference
uses PLC ladder eligibility and allocation: 6 kW to one eligible bay or 3+3 kW
to two; these are illustrative policy choices, not charging hardware claims.
The plant reports independent energy pulses and a retained cumulative meter-event
ledger. PLC memory acknowledges ledger differences, accumulates each event once,
and publishes DINT event count plus REAL kWh. A Stop precisely after meter pulse
publication is tested: resume acknowledges that pending event once, with no lost
or duplicated pulse. Actual energy integration remains PC-owned, separate from
PLC accumulated count and displayed output.
Forty-five focused geometry/adapter/reference checks PASS in
.tools/ev-reference-final-audit.log, including two-bay sharing, readiness-loss
reallocation, independent counts/.001 kWh, both readout text values, eight 3D
action bindings, pulse-boundary Stop/Run and Reset. The installed meters opt into
explicit numeric displays; their reusable standalone assets keep NO LIVE VALUE.
Blocked EV actions now explain occupied/plug/command conditions instead of
suggesting Reset. Build zero warnings/errors; help 294/77 valid; app-shell PASS
with 77 scenes, exactly five demos, 294 assets and transport disconnected.
EV reference full geometry regression completed PASS, 987 checks (.tools/ev-reference-geometry-regression.log), before the subsequent radar repair.
NEW controls, empty/occupied vehicle visibility, numeric readout readability,
blocked message rendering and full two-bay native cycle have not been inspected.
Windows input remains stopped after physical Escape. Scene 72 remains OPEN;
o broad visual or electrical acceptance is claimed for this checkpoint.

EV contract follow-up (2026-10-06): controller regression 144 PASS/0 FAIL
(.tools/ev-controller-regression.log), no real PLC transport constructed or
attempted. Scene contract preflight found two operator controls stacked in depth;
all eight fixture buttons now form one X row at Z 4.1 with 1.8 m spacing. Full
scene contracts 71 PASS/0 FAIL in .tools/ev-contracts-connected.log. This proves
catalog/point preflight and authored verification cases, not the new scheduling
or pulse-counting ladder, which has not yet been supplied. New control-row
appearance remains unverified because Windows input was stopped with Escape.

EV offline plant/adapter checkpoint (2026-10-06, native runtime OPEN):
Added renderer-neutral two-bay energy fixture: PLC grants/allocations are retained
as commands; valid occupied/authorized/ready/connected bays receive allocated
power. Illustrative shared budget 6 kW, pulse scale .001 kWh; invalid or over-budget
allocation inhibits delivery rather than silently selecting a scheduling policy.
Energy and fractional pulse residue survive Pause; Reset clears them. The model
accepts ticks up to 20 ms and exposes one-scan pulses. Twenty-one pure model
checks PASS (.tools/ev-plant-model-tests.log), including 10-minute 1 kWh/1000 pulse
agreement, independent sharing, malformed commands and permissive loss.
The scene adapter derives connected feedback from visible installed plug/inlet
meshes, rejects insertion without a vehicle, rejects vehicle removal with plug
inserted, and rejects plug changes while a charge command/allocation is present.
Runtime has 29 symbolic points and eight fixture actions/20 equipment; aggregate
catalog count 620. Twenty-six geometry/adapter checks PASS in
.tools/ev-connected-adapter-audit.log; connected A-bay pulse and Stop/Run/Reset
proved offline. Corrected meter count representation to the editor's long-backed
DINT boundary. Static geometry checks include hidden empty-bay tire meshes.
Build zero warnings/errors; help validates 294 assets/77 scenes. New controls,
empty-bay visibility and pulse feedback have NOT been visually inspected; Windows
input remains stopped after physical Escape. Last close was interrupted, contrary
to the original closed-window wording (now corrected). PLC scheduling/counting
reference, live readout bindings and native runtime review remain unfinished.
The scene stays OPEN and no electrical, protocol or calibrated-energy claim is made.

EV geometry verification follow-up (2026-10-06):
--audit-ev-layout: 16 focused installation checks PASS, covering actual pad/tire
and charger bearing, plug/inlet engagement, cable/gland continuity, grounded
meter/reader bases and pulse-module mounting for both bays. A 12.5 mm gap behind
the pulse modules was corrected. Final current native FR/FL/RL/RR/Top repeated
in .tools/ev-native-pulse-mount-final.log. The close attempt was interrupted by
physical Escape; window closure was not confirmed and Windows input stopped. Build zero
warnings/errors, .tools/ev-focused-layout.log PASS; full scene geometry regression
in .tools/ev-geometry-regression.log PASS (987 checks). These are bounds/visual
checks, not electrical or mechanical approval. Updated five owned asset help
pages and Scene 72 help; help validates 294 assets/77 scenes. Two-bay permissions,
connector state, pulse generation and PLC energy accumulation remain OPEN.

Scene 72 original EV geometry checkpoint (2026-10-06, runtime OPEN):
Replaced five incorrectly cloned accessory types with original EV vehicle/charger,
connector latch, energy display, pulse module and authorization reader models.
Inherited recognition evidence is retained in each review/historical_invalid_identity_20261006
folder; candidate quality resets and corresponding industrial-register entries are
removed, so shutter/skid recognition is not inherited by the EV replacements.
Added two separated vehicle/charger bays, connected illustrated cable/plug/inlet
geometry, grounded charger pedestals and meter/reader supports. Removed unrelated
machine cabinet. Fifteen equipment items; aggregate catalog count 615. Initial
Windows inspection exposed tire/body overlap; real Boolean wheel-arch cutouts now
clear those envelopes. Final native FR/FL/RL/RR/Top inspected after rebuilding
and importing (.tools/ev-native-layout-final.log); owned preview closed normally.
The reusable energy readout says NO LIVE VALUE. Geometry is illustrative and
unapproved; no charging protocol, rating, wiring, energy calibration or physical
acceptance. Help validates 294 assets/77 scenes; no C# behavior changed this pass.
Shared allocation, independent bay feedback/controls, connector state, pulse and
numeric energy accumulation remain unfinished. Existing Boolean-panel behavior
and blank default ladder are preserved pending that connected-runtime repair.
Detailed connector/feet checks and full geometry regression still required.
Scene 72 remains FAIL/open for process behavior; this checkpoint replaces the
incorrect-prop baseline only. Whole-scene goal remains active.

Scene 72 EV charging refreshed native baseline (2026-10-06):
Opened the current scene in the normal Windows shell, dismissed the simulator
notice, and inspected FR/FL/RL/RR/Top. Three motorized shutters, a liquid
metering skid, an electric pump and a generic cabinet still replace the intended
charging installation. Source review confirms ev_charger_bay and connector_latch
visual_review.md identify roller shutters; energy_meter identifies a liquid skid.
These inherited recognition records cannot establish EV-component identity.
The booleanPanel contract has only bay_occupied/customer_authorized/charger_ready
feedback and charge_enable/energy_session_active commands. No connector feedback,
energy pulse, pulse scale, numeric accumulation or allocation contract exists.
Normal Run routes to the empty editor with no controller loaded, as expected for
an exercise; this is not evidence of a working charging sequence. Preserve that
blank default and create any reference only through an explicit review command.
Owned native window closed normally; .tools/ev-native-refresh.log. Scene remains
FAIL/open. Next repair must replace misidentified props with coherent vehicle,
charger/cable/connector/reader/meter geometry and supply a bounded offline energy
and permission contract before claiming process verification. No EV electrical
protocol, power delivery, calibration or installation certification is established.

Scene 64 luggage-sort connected reference/native checkpoint (2026-10-06):
The delivered suitcase now travels on an accepted 20 ms plant clock, with actual
finite suitcase-body beam feedback at entry, weighing station and both exits.
PC numeric weight is a latched illustrative fixture mass (12/22/32 kg), valid
only on the actual weighing deck with scale ready, weigh command and no travel.
The installed readout shows a dash when invalid; its reusable asset remains static
without this explicit binding. PLC owns motion, weighing, route, category and
three numeric class counters. Three modeled operator controls bind load-next,
scale-ready and fixture selection. Conflicting motion/weigh commands and changed
routes are inhibited while preserving the command image. Loads remain visible at
both exits; only explicit load-next or Reset relocates a completed actor.

Original reference generated explicitly by --audit-luggage-layout into ignored
.tools/plant-review-luggage.rpproj.json: 41 focused geometry/adapter/controller
checks PASS. All three masses produce one category and only its counter increment;
held exits cannot recount. Example dwell .5 s and 15/25 kg limits are illustrative.
Category/counts retained in PLC memory survive Stop; public numeric outputs clear
while stopped and restore on Run. No default exercise ladder is filled in.

Native File-menu reference opening, 12 kg weighing and normal exit demonstrated;
scale pose FR/FL/RL/RR/Top at scan 325. That first cycle exposed incorrect roller
animation axis. Corrected local-axis rotation and added actual transformed mesh
crown check (rotated box bounds are too conservative for round rollers).
Final-axis 32 kg reference: 32.00 kg at scan 325; class 3/counts 0/0/1 at scan 525,
X 1.80/Z -.21 reject transfer inspected FR/FL/RL/RR/Top. Stop holds scan 525 and
pose; first resumed scan 526 restores result/route/count without recounting.
At scan 576, X 2.30/Z -.93, visible bag crosses the receiving bridge. Scan 826
stops discharge at X 2.30/Z -2.76 with the bag retained on outfeed, inspected Top
and RR. Native Reset restores home and zero counters/scan. Final 3D fixture-mass
and scale-ready controls accepted; early 3D load request blocked. Result-available
lamp now follows numeric class_result instead of an unbound decorative state.
All owned native previews closed normally. Logs: .tools/luggage-final-audit.log,
.tools/luggage-native-axis-final.log and .tools/luggage-native-final-controls.log.
Build zero warnings/errors, controller 144 PASS, scene contracts 71 PASS, help
294 assets/77 scenes, app shell PASS with five demos and transport disconnected.
Final full geometry regression: 987 checks PASS in .tools/luggage-geometry-verified.log,
with no exception or failed check. Its historical box_1 support check now uses
the delivered suitcase. The regression also exposed a scene-transition read of
luggage fields after the runtime had changed; a runtime-type guard fixes that
exception. A weight-display base/sensor-foot overlap was corrected by moving
the readout to Z 1.6, with a focused clearance check and final native
FR/FL/RL/RR/Top inspection in .tools/luggage-native-display-clearance-final.log.
The early-load rejection message now explains the exit/commands-off condition
instead of suggesting Reset; native message inspection passed. Latest focused
proof: .tools/luggage-final-verified-audit.log, 41 checks PASS.
This is bounded prescribed geometry and offline behavior, not calibrated
weighing, rated drives or contact dynamics.
The full multi-scene goal remains open, including scenes 72/77 and other matrix gaps.


Scene 64 luggage-sort geometry checkpoint (2026-10-06, process still OPEN):
Replaced the electrical-starter copy with an original suitcase and the bare
load-cell copy with a grounded four-cell weighing platform. Archived inherited
family evidence; both replacements remain unapproved candidates. Removed CNC
and duplicate carton; joined the 0.90 m deck, retained rollers, side bridge and
reject outfeed. The installation parks the swing arm beside the normal lane on
an illustrative direct-drive bearing; disconnected presentation pneumatics are
omitted explicitly. This is not a rated/mechanically qualified drive assembly.

--audit-luggage-layout: nine checks PASS. Actual mesh bearing at home/scale and
reject end, four deck/cell contacts, common transfer plane and receiver joining
are checked. 301 normal and 452 reject prescribed poses pass visible-solid
bounds/OBB penetration screens. These manually posed routes do not establish
runtime movement, friction/contact dynamics or continuous structural support.
Native final parked layout inspected FR/FL/RL/RR/Top; overhead receiver no longer
clips under the toolbar. Owned previews closed normally with exit zero.
Build zero warnings/errors. Logs: .tools/luggage-layout-sweep.log and
.tools/luggage-native-gate-review.log. Five demos/default blank exercises retained.

The old five-BOOL panel is still the scene runtime. Numeric weight, one-result
classification, class counters, sensor-derived feedback, scan-clock transport,
Stop/Run/Reset and native moving-cycle review remain unfinished. Scene 64 stays
FAIL/open; this checkpoint does not supersede that requirement.


Lab 2.1 is the starting point for the PLC/watchdog foundation. Every later
lab retains that foundation and adds the next control concept. The simulator
scene files describe the required contract and acceptance behavior; the actual
TIA ladder blocks remain in the student's cumulative bench project.

## Progression groups

| Labs | Development focus | What remains from the previous lab |
|---|---|---|
| 2.1 | Watchdog, heartbeat, first input/output | Common `DB_SimulationProof`, watchdog, watch table |
| 2.2–2.4 | Series, inversion, parallel logic | Watchdog, project, prior troubleshooting method |
| 2.5–2.10 | Selectors, complementary outputs, permissives, memory, seal-in | Watchdog and prior project foundation; new tags are additive |
| 2.11–2.15 | Photoeyes, conveyors, tanks, pumps, analog/discrete feedback | Watchdog, prior blocks, and documented tag conventions |
| 2.16–2.20 | Guarded drilling, robot motion, limits, shutters, shuttle travel | Watchdog, prior blocks, and cumulative acceptance checks |
| 2.21–2.25 | Multi-station sequences, valves, CNC handshakes, sorting, toggle memory | Watchdog, prior blocks, all documented setup discipline |

## Rule for each new lab

1. Open the previous lab's TIA project copy.
2. Confirm the common watchdog and earlier acceptance checks still pass.
3. Add only the new symbols, networks, blocks, and equipment required by the
   new lab.
4. Do not rename or delete retained tags without recording a `changedTags`
   entry and reviewing every dependent rung.
5. Run the previous lab checks before running the new acceptance cases.
6. Save the project as the next cumulative lab revision.

## Simulator contract

The Setup view is the authoritative list of exact simulator point names. It
shows direction and type so a student can create matching PLC symbols or map
them in a verified external profile. The simulator follows PLC-owned outputs;
it does not synthesize missing ladder logic to make a lab pass.

## Current repository boundary

This repository does not contain the student's TIA Portal project or ladder
blocks. It now records the cumulative lineage, machine guide, tag delta, and
previous acceptance identity in every generated lab scene. Once TIA blocks are
exported, the cumulative project can be checked against those contracts.
