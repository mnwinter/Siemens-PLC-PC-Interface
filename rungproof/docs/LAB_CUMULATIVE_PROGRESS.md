# Cumulative Lab Progression

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
