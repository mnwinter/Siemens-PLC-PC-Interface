## Pallet robot normal-editor native cycle - 2026-10-06

Windows window 3342534, build 561feda: opened the eight-tag QA project through Project > Open, used Online > Verify + load offline (1 block, 1 task, 3 rungs, 8 tags), returned to the scene and clicked Run. At scan 28 both robot_run and conveyor_run were false and the robot remained home. Start pallet unload was accepted at scan 285 and robot_run became true.

Native sampled views: FR first attachment/carry at scan 602, FL first carried load 610, RL receiver approach 935, first receiver placement count=1 at 1250 and RR withdrawal 1263. RR second carried load 1520 and Top second carry/receiver footprints 1557. At Top 1988, count=2, both totes remained in separate receiver pockets, the robot was parked, robot_run=false and conveyor_run=true; FR 2030 showed outbound travel. FR 2372 and FL 2394 showed the empty pallet retained on the outbound conveyor, both commands false. Top 3048 confirmed both receiver loads retained and the pallet fully on the outbound deck. Scrolled input image at 3341 showed cycle_complete=true and robot_at_park=true.

Stop robot cell at scan 3619 halted the controller with both commands false. Reset pallet cell restored scan 0, both totes and pallet at initial poses, receiver empty, cycle_complete=false, robot_at_park=true, commands false. No output force or physical PLC was used. This closes the reproduced missing native Start binding and verifies a complete normal loaded-ladder cycle at sampled phases. It does not inspect every continuous frame: second descent/contact and intermediate park return frames were missed, and mid-carry Stop/Reset and repeated-cycle coverage remain required. Row 31 stays open for those visual/runtime gaps and full-solid contact proof.

## Pallet robot start-path repair - 2026-10-06

Explicit operator.start PC BOOL and controllerStartBinding now connect the Start action to a loaded ladder input. Opt-in controllerSequenceCommand=robot_run starts the plant routine once per Reset when controller playback and the command are active. Sequence presets preserve PLC-owned outputs in this opt-in mode, preventing reference steps from overwriting the loaded controller image. Existing standalone reference sequence remains available. QA ladder now latches robot_run from the Start request and removes it after both placements and completed park.

Build: zero warnings/errors. Focused Godot command-boundary verifier passes, including no routine start before command and command-triggered motion with preserved outputs. Controller tests: zero failures. Updated eight-tag QA fixture validation passes with zero binding issues. Evidence: .tools/pallet-robot-start-build.log, pallet-robot-start-check.log, pallet-robot-start-tests.log, pallet-robot-start-project.log. These checks do not prove the native normal-editor Start button or full loaded-ladder transfer. Restart the native app with this build and repeat that workflow; row 31 remains FAIL/open.

## Pallet robot native controller blocker - 2026-10-06

Native Windows session 45504/window 2497778: opened aaa-pallet-robot-native-qa.rpproj.json through the normal editor, used Online > Verify + load offline, and observed verification complete: 1 block, 1 task, 3 rungs, 7 tags. Run advanced the controller scan and asserted robot_run=true while conveyor_run=false, placed_count=0. Clicking Start pallet unload was rejected with 'this scene action has no command binding in the loaded ladder program'. Robot remained at home; no native transfer or release was verified.

Cause located in Main.TryExecuteSelectedControllerAction: start actions require an explicitly authored controllerStartBinding to a BOOL input. This scene's start-robot action has no such binding or start input; its reference sequence is only started through the direct runtime path used in the bounded verifier. The previously passing command-boundary checks therefore do not prove a working normal UI workflow. Repair must connect a real operator request and controller command to reference-cycle entry without forcing outputs or silently bypassing loaded ladder logic. Row 31 remains FAIL/open.

## Pallet-robot PLC interface and outbound command gate - 2026-10-06

Row 31 inspection found placed_count and cycle_complete internal SIM ownership, preventing controller input bindings, and no completed-park feedback. These two existing point names now have PC ownership; added PC BOOL robot_at_park, derived from the actual robot adapter after a completed park solve (not early proximity). Authored sequences, routes, loads and default blank exercise are preserved. The outbound translate motion now explicitly requires conveyor_run; while false, sequence elapsed time and pose hold. Configured command gates validate declared PLC BOOL ownership. No PLC output is manufactured by feedback projection.

New --verify-pallet-robot-controller focused real Godot command-boundary verifier: reset feedback readable; reference transfers both containers and returns to park; switched to controller-owned clock/output image; withheld conveyor command holds; command moves; withdrawal holds; resume completes at X 5.2. All six checks PASS. This uses actual plant nodes and symbolic output commits, not a compiled/loaded ladder or native operator proof. Build zero warnings/errors, 145 controller tests and app-shell verification PASS. Evidence: .tools/pallet-robot-controller-boundary.log, pallet-robot-feedback-build.log, pallet-robot-feedback-tests.log, pallet-robot-feedback-app-shell.log.

Next required: load a ladder reference using the new feedback through the normal Windows editor, inspect intermediate transfers from multiple angles, and exercise Stop/Reset. Latest native pallet-robot inspection predates these interface changes. Overall row 31 remains FAIL/open; rated mechanics, complete solid contact and physical controls are unverified.

## Sump level-switch mounting repair - 2026-10-06

Row 28 now opts into tankSwitchMounts with sump_tank/low_float/high_float and .20/.78 modeled thresholds. Existing six point names, action ownership and level-cycle definition are preserved. The actual sensor models are tuning forks, now labeled explicitly. Both fittings mount on the clear positive-X side; probes point into the vessel, heads remain outside, and sockets seat the process seals. Socket endpoints are transformed through the tank's inverse transform, correcting the rotated-tank mounting bug. Existing positive-Z tank installations remain unchanged. Added --verify-tank-switch-mounts focused entry point and expanded the existing mount verifier to the sump, including above-floor and ladder/sight-glass clearance checks.

Build passed with zero warnings/errors. All 24 focused checks across three tank scenes passed; 145 controller tests and app-shell verification passed (77 scenes/5 demos/295 assets). Native Windows final session 22372/window 2949318: explicitly selected FR/FL/RL/RR/Top and inspected the final layout, then low_float focus FR showed the seated fitting/head clear of the shell exterior. The opaque shell hides internal tips; their placement is bounded geometry-verifier evidence, not native visibility. Whole-equipment broad bounds still flag intentional sensor penetration and pipe/flange junctions; no all-solid collision certification is claimed. Evidence: .tools/sump-switch-build.log, sump-switch-mount-check.log, sump-switch-controller-tests.log, sump-switch-app-shell.log.

Remaining FAIL: vertical closed vessel still substitutes for the described sump, tuning forks still substitute for float devices, full controller-owned level cycle and complete native motion not yet verified. This repair resolves the buried low probe and mounting/ladder/sight-glass conflicts, not overall scene acceptance.

## Mobile-traffic static layout repair - 2026-10-06

Row 12 now reuses the repaired crosswalk_road_module horizontal roadway and two traffic_signal_head models. Existing indicator_0/1 identities and road_a_green/road_b_green bindings are preserved, with three unchanged manual input points/actions and readable READY/A CLEAR/B CLEAR station labels. Removed two unbound single-amber-beacon props falsely named mobile head and synchronization link. The named synchronization-link requirement remains open; no working link is substituted or claimed. Heads sit at +/-3.3 X, +/-3.8 Z, Y .15 on opposite shoulders and face their respective X approaches. Stations at X 6 are clear of the road, whose delivered X bounds are +/-5; measured station half-width .22 gives .78 m clearance. Delivered head foot starts Y 0, matching shoulder top .15 after placement.

Native Windows session 73638/window 6363868: reloaded through Previous/Next and inspected FR/FL/RL/RR/Top, no visible independent equipment overlap. All 145 virtual-controller tests and app-shell verifier passed (77 scenes/5 demos/295 assets). These do not prove traffic sequencing. The scene still lacks portable bases, synchronization-link representation/behavior, independently commandable red/amber channels, all-red intervals, traffic motion and actual automatic clear feedback. Scene remains FAIL for overall acceptance. Description now distinguishes manual feedback and PLC-owned green commands. Evidence: .tools/mobile-traffic-delivered-bounds.log, mobile-traffic-controller-tests.log, mobile-traffic-app-shell.log.

## Native Reset and service-elevator placement - 2026-10-06

Updated native Windows build fbebf61, session 73638/window 6363868: opened saved .tools/multizone-native-qa.rpproj.json through Logic Editor, verified and loaded 1 block/1 task/3 rungs/6 tags. Run then Zone 1 Clear showed input/output True and green indication at scan 278. Direct Reset returned stopped scan 0, visible Zone 1/2 inputs and outputs False, indication inactive. Native screenshot scope does not prove drum angle/UV restoration; the committed real Godot regression verifies those internals. Middle conveyor handoffs additionally inspected close from front-right and rear-left.

Service elevator row 11: measured actual delivered GLB vertices, moved shutter to [-3.3,0,-1.6] and separated/grounded cabinet props. Measured static shutter/lift Z gap is 0.175 m; right cabinet/door X gap is 1.32 m; cabinet bottoms at floor. Reloaded through Previous/Next and inspected FR/FL/RL/RR/Top in native Windows app. This is a placement repair, not an elevator implementation: bucket elevator still substitutes for car/shaft, cabinets still substitute for call station/position sensor, two-landings geometry and full-motion controller behavior remain unresolved. Evidence: .tools/service-elevator-delivered-bounds.log and .tools/service-elevator-placement-check.log. Scene stays FAIL.

## Conveyor Reset regression - 2026-10-06

Reset now calls ConveyorController.ResetPlantTravel after clearing its run command. The real Godot plant verifier first applies nonzero conveyor travel and confirms speed, drum transform, and belt UV changed, then verifies Reset restores zero speed/travel and the home transform immediately. Both checks and the complete plant-motion verifier passed. Virtual controller suite: 145 passed, 0 failed. Updated native Windows build launched and startup inspected; native running-to-reset visual confirmation remains pending. No PLC transport used. Whole-program and catalog acceptance remain open.

## Multi-conveyor native QA command lifecycle (2026-10-06)

Owned session 35484/window 3933478. Loaded multizone-native-qa.rpproj.json by
Logic Editor > Project > Open project, selected .tools folder with Return,
selected actual fixture icon and Open. Online > Verify + load offline reports
1 block, 1 task, 3 networks/rungs, 6 tags. Returned to scene and Run.
Zone 1 clear true -> zone 1 run true while visible zone 2 remained false;
zone 1 loss -> false. Zone 2 independently true then false on clear loss.
Zone 3 enabled alone; scrolled output panel shows outputs [false,false,true].
Stop changes outputs to [false,false,false], state STOPPED. Reset scan 0,
outputs false, visible zone 1/2 inputs false. Zone 3 input reset not exposed.

These prove native project-load/compile/operator command lifecycle for the
isolated QA fixture. Captures do not establish actual shaft/belt animation,
all-on Stop, source-edge sequencing, common-stop behavior or pallet motion.
Scene remains FAIL/open for those missing route functions. No PLC connected.
Current app remains stopped at Reset with QA project loaded and first handoff
focused FL; next verify actual drive visuals and remaining second seam detail.

## Multi-conveyor close details and drive QA preparation (2026-10-06)

Native session 35484/window 3933478 current final geometry: focused receiving
roller Top and FL inspected, showing narrowed transfer deck and grounded posts.
Focused first-handoff photoeye FL inspected, exposing level belt-to-belt deck,
post and foot, separated photoeye stand/cable and adjoining belt noses. No
obvious solid intersection in these views; this does not prove pallet bearing
or intermediate motion. Second handoff close detail still pending.

Created ignored .tools/multizone-native-qa.rpproj.json from established project
schema: three independent assignment rungs, each zone_clear -> corresponding
zone_run. Six BOOL tags, all initially false, 20 ms scan. This is drive binding
QA only, not the lesson's common-stop/edge/handoff-state control reference.
Offline validation PASS zero issues, .tools/multizone-native-qa-validation.log.
Next load through native Logic Editor > Project > Open project, Verify + load
offline, then observe each motor/belt and indicator independently plus Stop
and Reset. Native QA fixture not loaded yet; runtime results remain unproven.

## Multi-conveyor corrected installation native checkpoint (2026-10-06)

Widened four photoeye stand spans from 2.05 to 3.2 m and raised optical centers
to 1.23 m for the 1.053 m carrying deck. Existing factory translates actual
heads/posts/feet/cables, rather than scaling housings. Original frame/bracket
and cable broad overlap candidates now absent in startup geometry report.
Corrected decks also have no separate-equipment broad AABB candidates.
This is an envelope screen, not complete within-equipment solid clearance.

Owned session 35484/window 3933478, final endpoint DLL and current JSON:
normal-shell startup notice dismissed; full-scene FR(initial), FL, RL, RR,
Top inspected. Separate grounded photoeye stands, three level handoff decks,
and inline receiving roller visible. Final spans [-3.5395832,-3.260417],
[3.260417,3.5395832], [10.060417,10.337], widths 1.4/1.4/1.02, top 1.0529999.
Broad views do not replace close details or actual pallet runner traversal.
Scene still lacks pallet/travel and common-stop I/O; loaded-controller drive
motion, beam/load intersections and retained route states remain unverified.
Previous build/tests passed; current C# build passed after deck correction.

## Multi-conveyor handoff clearance follow-up (2026-10-06)

Camera bar absence was launch configuration, not a product defect: omitted
--visual-scene-review. Restarted owned normal shell with that inspection flag,
session 87103/window 5768742; startup notice dismissed. Full-scene Top now
visually inspected: three separate belts, three transfer decks, inline roller.
Runtime report identifies belt/deck AABB candidates at original 35 mm drum
endpoint clearances and photoeye cable/bracket mounting candidates.

Corrected handoff endpoints to clear full delivered belt envelopes by 5 mm,
and end before the first roller envelope by 5 mm. This removes intentional
plate penetration of the curved belt wrap; actual runner support across these
clearances still needs sampled traversal. Build zero warnings/errors. Native
window still uses preceding endpoint DLL: final corrected deck angles and
geometry checks pending. Photoeye solid/cable candidates require diagnosis.
Do not count current overhead image as final corrected-deck verification.

## Multi-conveyor supported handoffs implementation (2026-10-06)

Added opt-in multiConveyorHandoffs installation and SceneComposer.MultiConveyor.cs.
Three 16 mm carrying decks with two grounded posts/feet each span measured
outgoing drive drum center +35 mm to incoming tail drum center -35 mm, or
receiving first roller center -35 mm. Height agreement within 1 mm and transfer
span .1..1 m are checked at composition; widths use minimum receiving surface.
Actual native composition prints spans [-3.5854168,-3.2145834],
[3.2145834,3.5854168], [10.014584,10.345], top=1.0529999; widths 1.4/1.4/1.02.
No pallet motion or feedback is generated by these parts.

Build zero warnings/errors. Owned prior window closed; new native session
10170/window 1842402 launched with --shell-scene to select this normal-shell
scene at startup. Startup notice dismissed; initial front-right render inspected.
The camera review toolbar is absent in this startup-selected state, so the
attempted historical Top coordinate did not change view. Do not count it as
Top inspection. Recover camera UI / normal navigation before final close
handoff and five-angle acceptance. Deck/post solid clearance, pallet bearing
and actual handoff traversal remain unverified; scene remains FAIL/open.

## Multi-conveyor delivered roller alignment (2026-10-06)

Imported actual delivered training pallet roller GLB into Blender and measured
transformed mesh vertices using ignored .tools/measure-multizone-roller.py.
Roller 30 top=1.093000054 m, all six foot bottoms=.039999999 m; first/last
roller X extent is approximately +/-1.958 m, frame ends +/-2.025 m. Grounding
by Y=-.04 gives carrying top 1.053 m. Updated three belt deckHeight values to
1.053 and roller equipment center to [12.3,-.04,0]. No asset was regenerated.

Native normal Previous/Next reload, session 16751/window 3277368: front-right
shows roller receiving zone inline after third belt and common height visually.
This is placement evidence, not continuous pallet support: belt inter-zone gaps
remain, as does roughly .292 m to the first roller outer edge from nominal belt
end. Add measured supported bridges before claiming a working pallet route.
Pallet and actual load travel remain absent; photoeye beam heights/clearances
must be revisited for the higher deck. Full five-angle final installation
inspection and native loaded-controller motor test remain open.

## Multi-conveyor sensor and output-binding repair (2026-10-06)

Replaced scene-local training_accessory_7 vibration surrogate with existing
through-beam photoeye type at zone 1/2 boundary X=-3.4, Z=0. Existing three
photoeyes moved onto belt centerlines (-8.5, 1.7, 10.2 X). Manual zone-clear
inputs remain explicitly manual; photoeyes do not fabricate feedback yet.
Added running point bindings from zone_1_run/2_run/3_run to conveyor_0/1/2,
retaining original indicator bindings. Operator labels now identify each zone.
No default ladder program or authored demo was added.

Normal Windows Previous/Next reload, owned session 16751/window 3277368,
updated front-right visually inspected. Belt/photoeye installation is visible;
roller zone still disconnected. Existing 145 controller tests PASS/0 FAIL;
app-shell PASS 77 scenes/5 demos/295 assets; no PLC connection attempted.
These checks do not prove native loaded-controller drive motion, sensor solids
clearance, transfer continuity or a pallet route. Full repair remains open.
Builder source identifies roller bearing top at 1.093 m and foot bottom .040 m,
so a grounded roller's carrying top is 1.053 m; current .9 m belt installation
will need matching elevation or an explicit transition. Inspect actual meshes
before finalizing this source-derived measurement.

## Multi-conveyor overlap first repair (2026-10-06)

Native session 16751/window 3277368, current scene 10. Front-right and Top
confirm original three 6.5 m belts superimposed (centers only 2.2 m apart).
Changed only belt center X positions to -6.8, 0, +6.8 m. This separates their
carrying decks with nominal 0.3 m end gaps. Normal Previous/Next navigation
reloads JSON; updated native front-right inspection confirms separated belts.
App-shell verifier PASS: 77 scenes, 5 demos, 295 assets, disconnected.

This is deliberately an unfinished installation repair. Handoff bridges,
photoeye relocation/mounting, roller-zone inline connection, delivered roller
bearing height and missing pallet need measurement and repair. Candidate
catalog confirms zone_handoff_sensor maps to sensing.condition.vibration.v1,
so it is a wrong sensor identity. Current booleanPanel projects outputs only
to indicators, not the conveyor motors; no common-stop input or actual pallet
route model exists. Keep scene FAIL/open. No motion acceptance established.

## Wastewater pump native visual checkpoint (2026-10-06)

Owned session 16751/window 3277368, focused pump_3 Top and front-right views.
At source-high false, pump command false; all other QA permissives retained true.
Front-right shows pump suction/discharge connections, base and guarded coupling.
Restoring source-high made pump command true. Exposed rear rotor orientation
changed between running captures (scan 3886 and 4188); after Stop at scan 4498,
output false and rear rotor orientation unchanged on the following capture.
This establishes bounded visible rear rotor motion/stop, not internal coupling
or impeller motion, speed fidelity, hydraulic flow or swept-volume clearance.
No guard was removed. Native runtime left stopped, manually toggled inputs
retained true. Final full-scene five-angle evidence is recorded above.

## Wastewater final-build angles and valve motion (2026-10-06)

Owned native session 16751/window 3277368, final 0cd70ad build. Full-scene
front-right and Top were inspected in the preceding operator checkpoint;
front-left, rear-left and rear-right now inspected too. All four tanks are
visibly separated; probe remains roof-mounted; front views expose collector
connections and floor supports. Rear vessels occlude much of the collector.
No complete internal pipe bore or hydraulic validation is implied.

Focused valve rear-right view shows supported installation and readable
TO TREATMENT label. Focused Top shows pointer perpendicular to bore at reset,
parallel to bore with all three QA permissives true, perpendicular after
outlet-clear loss, parallel on restore, perpendicular after source-high loss.
Both commands clear on each of these losses. Treatment-ready loss was tested
in the previous checkpoint. Thus all three individual permissive losses have
native command evidence. Pointer quarter-turn endpoints verified visually;
continuous intermediate travel, shaft animation and hydraulic behavior remain
unverified. Focused Top intentionally crops surrounding piping/indicators.

## Wastewater native operator checkpoint (2026-10-06)

Final build 0cd70ad, owned Windows session 16751/window 3277368. Loaded ignored
wastewater-native-qa.rpproj.json using Logic Editor > Project > Open project,
selected the actual file-list item, then Online > Verify + load offline.
Verification UI reported 1 block, 1 task, 2 networks/rungs, 5 tags loaded.
Bottom Load is a workspace picker, not the ladder project picker.

Native Run: initially both output commands false; source high alone false;
source high plus treatment ready false; adding outlet clear made both true.
Removing treatment ready made both false; restoring it made both true.
Stop cleared both commands while preserving visible manual feedback. Reset
returned stopped scan 0, visible source/treatment inputs false and both outputs
false. No physical PLC was connected. This is QA-fixture BOOL behavior, not
liquid transfer, measured analog feedback, all-permissive-loss coverage, or
confirmed shaft/valve animation. Those checks remain pending.

Final full-scene Top camera inspected: four tank roofs and collector/discharge
route fit below the toolbar; separate tank footprints are visible. Front-right
final build also inspected. Focused station readability and full five-angle
final-build inspection remain pending; overall goal remains active.

# Multi-angle scene review - 2026-10-04

## Wastewater native controller QA preparation (2026-10-06)

Created ignored .tools/wastewater-native-qa.rpproj.json from existing project
schema, two assignment rungs each requiring source_level_high AND treatment_ready
AND outlet_clear. Both outputs are false initially. QA-only fixture does not
change exercise defaults or the five authored demos. Offline --mcp-project
validation PASS, zero compiler/I/O issues, log
.tools/wastewater-native-qa-verify.log. This proves readability/compilation/scene
bindings, not scan behavior or operator acceptance.

Owned session 78708 closed normally exit 0. Restarted final camera/labels build
normal Windows shell, live exec session 16751 at initial Conveyor Inspection
Cell startup notice. Next: select current returned window, dismiss notice, load
QA project using normal Load/file dialog, Verify + load offline if required, Run
and toggle manual inputs. Observe pump/valve ON/OFF, individual permissive loss,
Stop and Reset. Also recheck final overhead camera and station text.

## Wastewater piping native checkpoint (2026-10-06)

Owned current piping build session 78708/window 10880540, normal shell startup
and Scenario menu -> Lab 11.6. FR/FL/RL/RR/Top full-scene native views inspected,
stopped and disconnected. Front-left and Top clearly show four outlet branches,
common collector, pump and raised valve/discharge connection; rear views show
valve feet on floor. Pneumatic prop is absent. No physical or full component
clearance acceptance is inferred from these views or the endpoint checks.

Top exposed the large tank guardrail behind inspection toolbar. Added this
scene to the existing opt-in 1.30 overhead review fit; that final camera change
requires restart and native Top recheck. Updated scene description to connected
visual piping while explicitly stating no liquid-transfer/analog measurement
simulation; gave the three manual input stations distinct face labels. These
final label changes also need native focused readability review.

Final current build zero warnings/errors; focused 18 checks PASS; controller
tests 145 PASS/0 FAIL; app-shell PASS 77 scenes/5 demos/295 assets. Checkpoint
preserves piping geometry and tests. Native loaded-controller pump/valve motion,
flange/tee bore/diameter continuity and all-component clearance remain open.
Window 10880540 still uses the prior camera/label DLL. Scene remains FAIL/open.

## Wastewater joint/support verification WIP (2026-10-06)

Expanded focused assertions to compare actual mesh endpoint-ring centers
against four delivered tank outlet faces, pump suction, pump discharge, valve
inlet and treatment outlet. All port centers agree within 1 mm. This is center
continuity, not matched flange diameters, bore union or pressure compatibility.

Support assertion first failed: both PIPE_foot_L/R bottoms were 0.25 m above
floor after lowering by only the raised valve offset. Corrected to the actual
minimum delivered foot bottom, retaining ground anchors and extending posts.
Now all six feet (four header/two valve) rest on floor within 1 mm. Current
focused verifier has 18 checks, all True, exit 0. Build zero warnings/errors.
Log .tools/wastewater-piping-focused.log. Post/foot contact and full component
clearance still need stronger verification/native inspection.

Closed owned native session 53628 normally, exit 0. Started current piping
build normal Windows shell, live exec session 78708, initial Conveyor Inspection
Cell startup notice. Select returned current window via sky.list_windows then
dismiss notice and choose Wastewater through Scenario menu; native piping
inspection remains pending. Changes remain uncommitted WIP.

## Wastewater connected process geometry WIP (2026-10-06)

Replaced training_accessory_8 pneumatic asset with a scene-local collector
installation in SceneComposer.Wastewater.cs. Uses delivered tank outlet flange,
pump suction/discharge flange and valve bore endpoint transforms before the
scene enters the tree. Four vessel outlet branches feed a common header; pump
rotated 180 degrees faces its +X suction toward the header. Pump discharge
rises through a 450 mm elbow to a Z-oriented valve and explicit TO TREATMENT
boundary. Header feet/posts added; raised valve feet/anchors lowered to floor
and existing shoe posts extended. Other scenes do not opt into this assembly.

Build zero warnings/errors. Focused --verify-wastewater-installation ten checks
PASS, exit 0; .tools/wastewater-piping-focused.log. 145 tests PASS/0 FAIL; app
shell PASS 77 scenes/5 demos/295 assets. Added assertion confirms process route
meshes replace the pneumatic prop, NOT hydraulic or all-joint proof. Further
endpoint/tee continuity, support contact, bends, component clearance and actual
Windows views are pending. Branch-to-header visual tees do not establish a
verified watertight boolean-unioned bore or flow model.

Native session 53628/window 6095772 has the preceding DLL. Restart is required
before native inspection of the new piping. Keep scene FAIL/open. Changes
remain uncommitted WIP pending stronger geometry and native verification.

## Wastewater current-build native offset inspection (2026-10-06)

Started current aa5cbf0 build through normal Windows shell, owned exec session
53628, window 6095772. Dismissed startup notice and selected Wastewater through
the actual Scenario menu. Full-scene FR and focused tank_0 FR/FL/RL/RR/Top
inspected after current-DLL restart. The inward probe fitting remains connected
to roof/socket; central manway is visually clear. Top shows the inward movement.
Focused framing can crop other equipment behind UI; this is not full-scene
framing acceptance. Hollow rail clearance is supported by the separate nine
focused assertions, not by claiming ring AABBs are empty.

Local runtime stopped and PLC disconnected throughout. OFF valve pointer
quarter-turn is visible in nearby views; native ON transition and pump animation
under authored/loaded controller remain untested. Scene remains FAIL/open for
process piping, wrong pneumatic manifold and native driven process workflow.
Current native window remains open for next repair/inspection.

## Wastewater focused clearance verification (2026-10-06)

Prior valve-only full audit session 3943 completed exit 0 / geometry PASS.
Current build --verify-wastewater-installation runs the same nine assertions
as the full verifier without replaying unrelated lesson workflows. All nine
PASS, exit 0; log .tools/wastewater-clearance-focused.log. Build zero warnings
and errors, 145 tests PASS/0 FAIL, app-shell PASS 77 scenes/5 demos/295 assets.

The initial OBB-only rail check failed because RAIL_mid/top are whole hollow
torus meshes whose boxes fill the empty center. The current check requires
all probe mesh vertices to fit within the actual ring inner radial profile
with 10 mm allowance; posts/manway retain OBB checks. Height-separated pairs
are screened first. This is a bounded static clearance check, not swept,
physical, structural or instrument calibration acceptance. The inward roof
offsets remain scene-specific and defaults remain unchanged in other lessons.

Current native window 12518294 still has an older DLL. Fresh restart and
native post-offset inspection remain pending, as does controller-driven
valve/pump motion. Process piping and pneumatic manifold replacement remain
open. Earlier WIP notes are historical checkpoints, not current acceptance.

## Wastewater rail-clearance correction WIP (2026-10-06)

Closing native session 2907 revealed its actual BOUNDS_CANDIDATE output:
tank_0/training_accessory_7 count=16, example RAIL_mid/PROBE_insulator. The
previous rendered views and socket-only checks did not establish guardrail
clearance. Added scene opt-in roof offsets +0.55 X/-0.55 Z instead of the
full-size default +0.35/-0.85, retaining default offsets for other tank lessons.
Added a specific probe-versus-RAIL/manway OBB bounds assertion. Build passes
zero warnings/errors after adding the missing LINQ import. New mounting offset
and clearance assertion still require verifier and fresh native inspection.

Old native window 5774044 closed normally, session 2907 exit 0. Restarted
normal shell is window 12518294 (Conveyor Inspection Cell). It launched before
the offset-source rebuild and therefore needs another restart before the
new offset implementation can be visually verified. Full geometry session 3943
is still live for the previous valve-only build; do not attribute its result to
this newer rail-clearance fix. All five changed files remain uncommitted WIP.

## Wastewater valve projection WIP (2026-10-06)

Added actual valve_4 position binding for outlet_valve_open and a scene-local
wastewaterOutlet installation. Authored zero pointer parallels the process bore
(OPEN); inverted input maps false to quarter-turn CLOSED, true to authored OPEN.
Autonomous valve travel is disabled only for this installation. Existing other
valve lessons remain unchanged. This is command position projection, not valve
feedback, actuator transit-time simulation or hydraulic flow proof.

Build zero warnings/errors, 145 tests PASS/0 FAIL. App-shell/full geometry checks
launched with .tools/wastewater-valve-shell.log and
.tools/wastewater-valve-geometry.log. Added two focused assertions for false/true
valve geometry. Results and native app restart/inspection are pending. Current
native window 5774044 still uses prior DLL: do not claim this new factory has
been visually inspected. Piping and pneumatic manifold replacement remain open.

## Wastewater probe and pump projection WIP (2026-10-06)

Converted training_accessory_7 to the real analog levelSensor factory and opted
into roofAnalogProbe, with tank_0/transmitterId installation references. Existing
measured roof/socket/flange and liquid-zero/tip sizing now places the probe on
tank_0 instead of standing unmounted on the floor. Retained manually toggled
source_level_high; no analog acquisition or calibration is established.
Added transfer_pump_run running binding to actual pump_3, retaining its light.
Valve projection and correct process manifold/piping remain unresolved.

Normal Windows Previous/Next navigation reloaded the scene. Actual full-scene FR
and focused tank_0 FR/Top show the roof-mounted probe and clear central manway.
Focused Top partly approaches toolbar; complete rail/attachment clearance and
FR/FL/RL/RR/Top focused post-change views are now inspected. The roof socket
shows contact with the process flange and roof, clear of the central manway;
rail crossing in projected views is not swept or physical clearance proof. Native controller-driven pump
animation not tested in this checkpoint.

Build zero warnings/errors; 145 controller tests PASS/0 FAIL; app shell PASS
77 scenes/5 demos/295 assets. Six new geometry assertions check socket/roof/flange,
tip/liquid zero and rod attachment, separate shells, pump running true/false and
unchanged manual feedback. Full --verify-scene-geometry exec session 59906 completed exit 0. Log
.tools/wastewater-probe-geometry.log ends SCENE_GEOMETRY_VERIFY PASS bounds
screen only; no mechanical or live acceptance. All six new wastewater assertions
are True. Checkpoint commit f965e77 preserves the repair. Scene acceptance
remains open for process piping, valve projection and native controller motion.

## Wastewater spacing repair checkpoint (2026-10-06)

Changed only scene placement and its displayed scope description. The four
vessels now occupy X=-6,-2,2,6 m, Z=0, rather than intersecting shells.
Pump, valve, transmitter prop, pneumatic prop and operator stations occupy
separate front rows. Native normal Previous/Next navigation reloaded the JSON;
FR/FL/RL/RR/Top all inspected afterward in window 5774044, stopped, controller
unloaded and PLC disconnected. Tank shells and exterior ladders now show
visible gaps. Top confirms separate tank footprints; the larger fourth tank
approaches the focus toolbar and needs later framing review with its installation.

Build: zero warnings/errors. Controller tests: 145 PASS / 0 FAIL. App shell:
PASS 77 scenes / 5 authored demos / 295 assets. Logs are
.tools/wastewater-spacing-tests.log and .tools/wastewater-spacing-shell.log.
These checks do not prove process behavior or eliminate all component-level
collisions. This partial repair does NOT accept the scene: unmounted probe,
incorrect pneumatic manifold, disconnected process ports and missing actual
pump/valve output projection remain open. Existing FAIL matrix row remains.

## Wastewater native diagnosis checkpoint (2026-10-06)

Re-inspected current lab-11-06-wastewater-collection in the normal Windows shell,
window 5774044, catalog 9/77, stopped with no controller loaded and PLC disconnected.
Actual front-right, front-left, rear-left, rear-right and top views were inspected.
Top confirms intersecting cylindrical tanks and fourth oversized tank; front/rear
views confirm an unmounted transmitter, disconnected process equipment and the
pneumatic manifold. This is a failing pre-repair checkpoint, not acceptance.

Authoritative scene/source evidence:
- tank_0/1/2 shell diameters are 2.6 m, centers X=-3.3/-1.1/1.1 m: adjacent
  center distance 2.2 m produces 0.4 m shell penetration before attachments.
- collection_tank_bank independent_recognition identifies a single generic
  vertical-3000x5000 tank; CreateTrainingAccessory bypasses CreateTankAsset
  config sizing, explaining the oversized fourth vessel in the native view.
- level_transmitters identifies one flange-mounted insertion-probe transmitter,
  not a mounted multi-tank sensing system.
- pipe_manifold identifies a seven-station pneumatic solenoid manifold, not
  wastewater process piping. Moving this prop cannot repair the process route.
- pointBindings transfer_pump_run/outlet_valve_open target indicator_5/13 only;
  the actual pump_3 and valve_4 have no output bindings. No native driven
  pump/valve or liquid-transfer result is established.

Next repair must space the actual vessel/attachment envelopes, remove redundant
misidentified props, mount the insertion probe using measured roof/flange bounds,
and connect real process ports. Existing tankPiping uses a fixed 4.6 m inlet and
full-size tank dimensions, so it cannot be applied unchanged to these 2.5 m
shells. Preserve symbolic BOOL ownership and distinguish manual level feedback
from any later process model. Retest actual native geometry after the repair.

## Ten-motor array scene equipment repair - 2026-10-06

Normal Windows session 2907 before FR/Top confirmed only five motors with two overlapping roller-shutter accessories and a parking-display prop. Source review files identify both lineup/status assets as roller shutters and sequence-display asset as a parking sign; those catalog identities remain unchanged and receive no new approval. Removed only scene's fake lineup accessory, added five actual motors, and arranged ten declared motor models in two separated rows (2.6 m column spacing, 2.5 m row spacing). Replaced status/sequence props with supported count-display housings, explicit GROUP STATUS / START SEQUENCE and NO DATA. Moved display/operator/indicator row to Z=5.5 m; distinct operator face labels preserved original three input actions. Added retained motor_array_run BOOL projection to all ten motors. Description/purpose now disclose absent per-motor array values and staggered timing; group projection is not staggered startup.

Build zero warnings/errors; 145 controller tests PASS/0 FAIL; --verify-app-shell PASS (77 scenes/5 demos/295 assets). Eight new geometry checks currently pass: ten actual motor models, zero separate-equipment AABB candidates, two true display identities, two grounded attached supports, all ten responding to explicit group True and all ten stopped by False. Full --verify-scene-geometry session 1103 completed exit 0 / SCENE_GEOMETRY_VERIFY PASS (bounds screen only; no mechanical or live acceptance). Logs .tools/motor-array-tests.log, .tools/motor-array-shell.log, .tools/motor-array-geometry.log.

Reloaded authored JSON through normal Previous/Next in existing native session 2907, keeping the same production scene composer and binding implementation. Repaired scene inspected FR/FL/RL/RR/Top at 1602x932: all ten motors distinct, row/display/operator spacing clear, full overhead equipment below toolbar/above I/O. Focused training_accessory_7 and training_accessory_8 front-right show readable NO DATA readouts and supported bases/masts. Native controller-driven rotation, timing, alarm response and per-motor array execution remain open; no default lesson controller added. Whole-program goal active.

## Motor STRUCT display identity and interference repair - 2026-10-06

Native normal-shell before views showed roller shutters instead of the three declared diagnostic displays, obscuring the motor/machine. Owned window close log identified motor shaft versus machine side panel and display-versus-indicator/display interference. Replaced only this scene's three misleading accessory references with actual count-display housings configured with explicit MOTOR RECORD / TEMPERATURE / STRUCT DATA and NO DATA text. Reusable mislabeled source assets remain unchanged and are not approved as displays. Shifted motor X from -3.3 to -3.8 m to clear machine side panel; retained other equipment and input/output ownership. Added missing motor_enable -> motor running projection and distinct operator face labels. Description and purpose now explicitly state BOOL validity exercise, absent STRUCT record/power/temperature measurements and need for authored/loaded logic.

Build zero warnings/errors; 145 controller tests PASS; --verify-app-shell PASS (77 scenes, 5 demos, 295 assets). --verify-scene-geometry completed exit 0 / PASS, including nine new motor-record assertions: zero separate-equipment AABB candidates, three real display identities without shutter/fabricated values, grounded attached base/mast/housing for each, explicit enable run and removed-enable stop. Logs .tools/motor-record-tests.log, .tools/motor-record-shell.log, .tools/motor-record-geometry.log. This proves bounded symbolic projection and static screens, not motor mechanical coupling or STRUCT execution.

Rebuilt real Windows normal shell session 13591 and selected scene through Scenario menu. Inspected FR/FL/RL/RR/Top: actual supported displays, separated motor/machine and controls, no new visible interferences. Focused training_accessory_3 front-right shows MOTOR RECORD / NO DATA readable. Full-scene Top initially clipped machine behind review bar; extended existing opt-in overhead camera allowance only to this scene. Rebuilt session 2907 and native Top at 1602x932 shows all equipment below toolbar and above I/O. Final app-shell verifier PASS (.tools/motor-record-final-shell.log). Normal Run still opens unloaded blank exercise editor; no default controller introduced. Temperature/STRUCT focused readability and normal loaded-controller workflow remain open. Whole-program goal remains active.

## Demo 5 native completed-layer retention and Reset - 2026-10-06

Fourth return home observed at 113.70 s/5685: placed 4, home True, cycle False, vacuum False, all stock retained. Held at 118.84 s/5942. Normal Load next carton action was rejected with explicit message requiring home, empty pickup and layer space, and Reset after four cartons or fault; count 4 and empty pickup remained unchanged. Completed layer inspected front right, front left and overhead. With bridge returned home, overhead clearly showed four separate carton footprints within pallet perimeter and pallet separated from gantry posts. This overhead result differs from the earlier carry views obscured by the bridge.

Pressed normal Reset: local runtime stopped, scan/time zero, placed 0, home True, vacuum/cycle False. Overhead empty pallet and front-right supported initial pickup carton were visible. Native session 77702 is now stopped and held at Reset, front right/gantry focus. This completes the observed four-carton operator sequence, full-layer load rejection and Reset checkpoints. First-carton continuous carry/release and continuous return trajectories remain sampled rather than every-frame inspected; broader scene/runtime acceptance remains open. No PLC connection or write.

## Demo 5 fourth native carton placement - 2026-10-06

Third return-home observed at 78.16 s/scan 3908, placed 3, home True, cycle False and vacuum False. Held again at 84.22 s/4211. Loaded fourth carton onto supported pickup table and pressed Start through normal operator actions. Held .5 s scans showed approach/contact at 84.72/85.22, vacuum True/carton_at_pick False at 85.72 s/4286, lift clear at 86.22 s/4311, then carry at 86.72-89.72 s. Inspected carry from rear right and opposing front right; inspected later alignment/descent from front left and front right. Some front-left carton detail is obscured by shadows/nameplate, so front-right observation was used for late descent.

Continued held steps through 93.22 s/4661: fourth carton descended into the remaining pallet position, count 4 and vacuum False at 92.72 s/4636, then tool withdrew above retained stock. No newly visible geometric intersection in these sampled native poses. Released clock for return at 93.22; immediate capture 93.50 s/4675. Fourth return-home, extra-load rejection and Reset still pending. This adds native route waypoints, not every-frame or swept collision certification. Whole-program acceptance remains incomplete and goal active.

## Demo 5 second and third native carton routes - 2026-10-06

Continued normal Windows Demo 5 session 77702, training_accessory_4 focus, actual authored controller running with PLC disconnected. Second carton: Load and Start at held elapsed 26.22 s/scan 1311. Observed approach/contact/vacuum attachment/lift in .5 s steps; vacuum True and carton_at_pick False at 27.72 s/1386. Carry inspected from rear right, front left, front right and overhead at 29.22 s/1461. Rear right/front right show carried carton above the retained first carton and empty pickup table. Front left is partly post-occluded; overhead bridge obscures the carried carton. Continued .5 s held captures through 34.72 s/1736: descent, placed count 2 at 34.22 s/1711, vacuum False at 34.72 s/1736 and visible withdrawal gap. Opposing front-right/front-left views show both cartons retained on the pallet with the tool withdrawing. Released return; home True/cycle False/vacuum False at 40.10 s/2005, held again at 44.38 s/2219, placed 2 retained.

Third carton: native Load then Start at held 44.38 s/2219. Held .5 s steps show approach/contact at 44.88/45.38, vacuum attachment at 45.88 s/2294, lift clear of table at 46.38 s/2319. Front-left/front-right/rear-right observations show carry into the distinct third pallet position, above existing stock, at 46.88-48.88 s. Rear-right descent at 49.38/49.88 and opposing front-left descent through 51.88 s/2594 show arrival at pallet; placed 3 and vacuum False at 51.88. Rear right has partial stock occlusion of the third carton; front left shows its foreground placement. Released return clock at 51.88; immediate capture 52.40 s/2620 shows withdrawn tool and retained stock. Third return-home and fourth carton remain to be checked. No newly visible intersection in these observed waypoints; this is native waypoint evidence, not every-frame/swept collision or physical certification.

## Demo 5 first native carton pickup and return checkpoints - 2026-10-06

Continued the rebuilt normal Demo 5 operator shell (session 77702). Focused training_accessory_4. Held ticks at .50,1.00,1.50,2.00 s showed tool approach, vacuum True/carton_at_pick False and carton lifting clear of the supported pickup table. Inspected pickup/attached state from front right and front left. Released the native clock at 2.00 s; immediate capture was 2.48 s. Next held capture was 8.80 s/scan 440, placed 1, home False, vacuum False, gantry_cycle True: first carton visibly on the pallet and tool withdrawn above it. Rear right clearly shows supported carton inside pallet footprint. Rear left is partly occluded by the nearby robot; overhead is obscured by the gantry bridge, so neither alone proves carton footprint clearance.

Released return clock; rear-right capture at 16.60 s/scan 830 showed home True, placed 1, gantry_cycle False and vacuum False. Held again at 26.22 s/scan 1311 and observed unchanged retained first carton with tool at home. This verifies these native first-carton checkpoints and retention. Horizontal carry and exact release passed between continuous captures and still require finer held inspection; cartons 2-4 and their intermediate native views remain open. Do not describe the first carton as every-frame or full multi-angle motion certification. Existing audit still has failures=0 with 2,576 executed samples.

Next native state: Demo 5, training_accessory_4 focus, rear right, held clock, running controller, home True, placed 1, pickup empty. Load next carton then Start, and use held .5 s steps to inspect horizontal carry. No physical PLC transport.

## Demo 5 first-scan operator Start repaired and verified - 2026-10-06

Explicit BOOL operator pulses now establish a released baseline only for previously unobserved edge contacts referencing that declared input. Existing edge memory, startup held inputs and forces retain their prior semantics. Session PulseInput uses this for deliberate presses; normal scene pulse actions establish the same baseline when the controller is running and the scene point was false. No scan, output, elapsed time or plant motion is executed by this preparation. Stop continues to discard unscanned commands.

Added a focused test for first-scan pulse firing once, held-high startup suppression, force preservation and Stop cancellation, plus two Demo 5 integration assertions using the normal operator action before any warm-up scan. Build zero warnings/errors; 145 controller tests PASS/0 FAIL; --audit-palletizer --visual-scene-review failures=0 across 2,576 route samples and zero static candidates; --verify-app-shell PASS (77 scenes/5 demos). Logs: .tools/demo5-first-pulse-tests.log, .tools/demo5-first-pulse-audit.log, .tools/demo5-first-pulse-shell.log.

Rebuilt and opened the real Windows shell, selected Demo 5 through Scenario menu, held the clock before Run, pressed Run at scan 0, pressed Start once, then Step 0.5 s. At scan 25/time .50 s, home False and gantry_cycle True, with visible tool approach: the prior lost-first-Start case is corrected. Native session 77702 remains held there, Full scene/front right. This verifies startup behavior; remaining multi-angle pickup/carry/placement/home and four-carton native acceptance are still open. Goal remains active.

## Demo 5 native startup ordering issue reproduced - 2026-10-06

Opened Demo 5 through normal Scenario menu in Windows, focused training_accessory_4. Home/front-right view shows the empty pallet clear of the front gantry post. Held the offline plant clock, pressed Run (scan 0), then Start / resume one carton (accepted in event history), then Step 0.5 s. At scan 25 / elapsed .50 s, home remained True, gantry_cycle False, placed 0 and no visible movement. Pressed Start again and Step 0.5 s: scan 50 / elapsed 1.00 s, home False and gantry_cycle True; tool approached the carton. Front-right and front-left observations recorded this moving approach.

The deterministic --audit-palletizer --visual-scene-review command completed with failures=0, 2,576 route samples and zero static candidates (.tools/demo5-resumed-audit.log). Its workflow warms the controller with .1 s before Start; this does not cover the newly observed Run-at-scan-zero/Start ordering. VirtualControllerRuntime edge contacts initialize their first sampled input as the baseline, suppressing that first edge. Pending momentary operator Start before the initial baseline is therefore a specific unresolved workflow case; do not change global edge semantics without examining existing tests. Next action: reproduce in a focused automated regression and repair the operator pulse/startup sequencing, then continue native pickup/placement/return inspections. Native window session 57157 remains held at scan 50, elapsed 1.00 s with zero placements. Full native motion acceptance remains incomplete.

## Sorter operator button interference corrected - 2026-10-06

Focused native before views (overhead/front left) placed switch_11 against lane 4's services. Added a 1 mm AABB plus oriented-box screen for all three operator switches against all four receiving conveyors. Before repair this reported switch_11 enclosure/junction-box overlap of approximately 198x137x116 mm and additional pedestal/foot/cable intersections; focused command exited 1. Shifted only switch_11 from X 4.2 m to 3.6 m, retaining Y 0 and Z 4.7, its action and authored style. After repair the focused command exits 0 and operator controls are clear under the bounded screen. Logs: .tools/sorter-operator-before.log and .tools/sorter-operator-after.log.

Reloaded via normal Windows shell Previous/Next navigation. Focused diagonal and overhead views now show a visible gap between button housing/pedestal and lane 4 junction box/frame. This proves observed static separation, not every-frame collision or mechanical certification. Build zero warnings/errors; controller tests 144 PASS/0 FAIL; app-shell verification PASS for 77 scenes. Remaining sorter class feedback, driven carton routing and normal-controller motion acceptance are unresolved. Native window remains active in session 57157.

## Sorter overhead framing verified in Windows - 2026-10-06

Extended the existing opt-in near-vertical full-scene framing allowance to Vision Package Sorter. No equipment poses or normal camera defaults changed. Native rebuilt operator-shell overhead view at 1602x932 now displays the entire infeed, all four outgoing lane ends and controls between the review toolbar and I/O panel. Focused front-left inspection of outgoing bridge 4 also shows separation between its support and the table drive motor. These observations are static; automatic carton routing remains unwired.

Verification: build zero warnings/errors, VirtualController tests 144 PASS/0 FAIL, --verify-app-shell PASS for 77 scenes/5 demos/295 assets. Native instance is active (exec session 57157). Next: resolve switch_11/destination_lane_4 overlap candidate in a focused view and actual bounds; continue runtime gaps. A direct --scene-id invocation opens standalone preview even with --app-shell; native acceptance above used normal shell navigation instead.

## Sorter support clearance and resumed native review - 2026-10-06

User explicitly returned screen control. Moved lane 4's inner bridge support pair from local X -1.55 m to -1.65 m to remove the measured table-drive-motor intersection. Added outgoing bridge peer checks and lane-frame belt/drum/platter profile checks. Build: zero warnings/errors; focused carton static route command exited 0, with outgoing clearance/profile checks and 12,300 outgoing footprint samples passing. This is bounded offline geometry evidence, not mechanical approval.

Launched the actual Windows app with --app-shell --visual-scene-review and navigated to catalog scene 5 (Vision Package Sorter). Inspected front right, front left, rear left, rear right and overhead at the full-scene setting. Four separate receiving conveyors and supported table handoffs are visible. The overhead camera clips an upper lane end: camera framing remains unresolved. Full-scene views are insufficient to certify the small motor/support clearance visually; a focused close view remains required. Scene description still claims vision-based package routing, but the actual five-point boolean-panel simulation has no driven class selection/carton routing. Runtime completion remains failed/unverified. No physical PLC connection or writes.

Sorter four-outgoing-handoff checkpoint (2026-10-06; native review OPEN):
Four scene-specific curved handoffs now join the parcel table to its four
receiving conveyors. Actual lane-local bearing starts are -1.9627335..-1.9627337
m from each conveyor center; rounded noses start at -2.0033336. Handoffs use
these measured edges, matching the circular platter, deck Y=0.9 and four
support legs each. The old cabinet mapped as a diverter is removed; scene
and catalog now contain 20 equipment items. All 21 sorter checks pass in
.tools/sorter-outgoing-handoff.log: 12,300 sampled full-footprint support
points cover four outgoing paths to retained receiver positions, alongside
the existing 2,225 infeed/table samples. All 71 scene contracts pass/0 fail
in .tools/sorter-outgoing-handoff-contracts.log. These are static planar
support samples, not observed motion or complete outgoing 3D collision proof.
Outgoing bridge peer/mating screens, driven table index/carton transfer,
class feedback and latest native static/full-motion camera review remain OPEN.


Vision sorter four-receiver checkpoint (2026-10-06; native review OPEN):
The single destination-bank surrogate is replaced in this scene by four
actual conveyor installations, each 4 m long / 0.9 m wide / deck Y=0.9.
Their axes fan at -67.5/-22.5/+22.5/+67.5 degrees with inner nominal tips
2.6 m from the table center. This spacing is for separate receiving equipment;
table-to-lane bridges are not yet present. Two deck-count/level checks failed
before repair and pass afterward. All four complete delivered conveyor
assemblies clear each other at the 1 mm OBB screen. All 19 sorter checks pass
in .tools/sorter-lane-separation.log; all scene contracts pass 71/0 in
.tools/sorter-four-lanes-contracts.log. Scene/catalog equipment count is 17.
Outgoing handoffs, cabinet-diverter replacement, class feedback, actual PLC
routing and latest native static/full-motion camera review remain OPEN.


Vision sorter infeed bridge checkpoint (2026-10-06; native review OPEN):
A scene-specific four-leg steel handoff bridge now connects the infeed to
the circular parcel platter at deck Y=0.9. Its 64-segment curved nose follows
the platter edge. The first bearing-plane footprint check failed at the
rounded belt nose; the actual near-level bearing edge is X=-0.11055827,
66 mm behind the belt bounding edge. The revised leading transition uses
a quadratic thin underside over that nose and starts at the measured edge.
Ten current sorter geometry/identity checks pass, including 2,225 sampled
footprint points across infeed/bridge/platter (.tools/sorter-bridge-final.log).
Build succeeds and all 71 scene contracts pass/0 fail in
.tools/sorter-bridge-contracts.log. This proves sampled planar support, not
full 3D nose/frame self-collision or every-frame/native visual acceptance.
The scene has 14 equipment items. Four outgoing receiving lanes, cabinet
diverter replacement, class feedback and controller-owned transfer remain
OPEN, together with native static/moving multi-angle inspection.


Vision sorter parcel-table repair checkpoint (2026-10-06; native review OPEN):
The scene now opts into the existing parcelTransfer table variant, omitting
visible machining fixtures/raised index markers and matching the platter to
the actual 0.9 m infeed deck. Explicit radius 1.28 preserves its previously
delivered 2.56 m diameter; the old config radius 1.2 was ignored by the
machining-table mapping. Both fixture/deck checks failed before and pass after
repair (.tools/sorter-parcel-table-after.log); all seven current sorter support/
identity checks pass. Its initial-state contract passes separately. The
2.0645833 m horizontal gap, cabinet diverter surrogate, single destination
belt at Y=1.055, class feedback and native static/motion review remain OPEN.
The parcel variant provides a position-controlled adapter; controller-owned
indexing/routing has not yet been connected or verified in this lesson.


Sorter display support regression checkpoint (2026-10-06; native review OPEN):
Five actual scene checks pass for display mesh identity, grounded base with
attached mast/housing, explicit CLASS / NO RESULT text with hidden stale COUNT
legend, carton bearing-plane contact and full supported footprint. Evidence:
.tools/sorter-display-support.log. Full scene contracts pass 71/0 in
.tools/sorter-display-contracts.log; app shell passes 77 scenes / 5 demos / 295
assets while DISCONNECTED in .tools/sorter-display-shell.log. Source contract
checks and text-node inspection do not prove rendered readability or sorting.
The diverter still uses a cabinet surrogate; connected four-lane routing,
class feedback and latest native five-angle inspection remain OPEN.


Vision sorter display identity checkpoint (2026-10-06; native review OPEN):
Actual GLB node inventory confirms the former class-display package contains
photoeye receiver/transmitter parts; the supposed four-lane diverter contains
cabinet parts. VISION_SORTER_ASSET_IDENTITY.json preserves that inventory;
tools/audit_vision_sorter_asset_identity.py regenerates it. The scene now reuses
the existing count-display housing through an opt-in staticText rendering mode,
with CLASS / NO RESULT instead of an invented class value. Its actual display
mesh identity check failed before and passes after repair; the carton support
checks also pass (.tools/sorter-display-after.log). Build succeeds. Current
class feedback, diverter identity/connected lanes, and native readability/
five-angle review remain OPEN. This does not certify the reusable display asset.


Vision sorter support checkpoint (2026-10-06; native review OPEN):
The current source carton was confirmed below the actual belt: bottom Y=0
against belt top Y=0.9. Changing only box_1 position Y to 0.9 repairs contact
while preserving its existing footprint and scene behavior. Two actual Godot
mesh checks verify bearing-plane contact within 1 mm and full belt footprint;
the contact check failed before and passes after repair. The existing carton
static-route/photoeye verifier also passes (.tools/vision-sorter-support-after.log).
The sorter authored initial-safe-state contract passes separately; it does not
prove sorting. Display/diverter identity, connected four-lane routing and
latest native five-angle scene inspection remain OPEN.


Coverage inventory checkpoint (2026-10-06):
The canonical 77-row matrix records FR/FL/RL/RR/Top for all 77 scenes. Older
chronological statements of 18/59 or 30/47 are historical checkpoint counts,
not current totals. This does NOT certify current geometry or runtime: twelve
rows retain explicit FAIL text, and at least four scenes have changed since
their last native review (tote finishing, guarded transfer, EV charging, radar).
SCENE_NATIVE_REVIEW_QUEUE.json extracts every row and labels acceptance as
NOT_CERTIFIED_BY_THIS_INVENTORY. tools/audit_native_review_queue.py regenerates
it; failure labels include unresolved runtime findings and must be examined
before calling them current visual failures. Current source confirms the
Vision Package Sorter carton remains at Y=0 beside a conveyor deck at Y=0.9,
so the historical carton-under-belt finding still needs repair and rendered
verification. Native control remains stopped after Escape; no new native
acceptance is claimed.


Axial cap motion checkpoint (2026-10-06; native review OPEN):
The tote finishing adapter now has a measured axial stroke, release to the
tote-parented cap, retraction, and five PC cap feedback points. Concurrent
travel is explicitly inhibited while the chuck is extended, preserving the
raw PLC request and publishing a separate PC inhibition. Fifty-three focused
checks pass in .tools/cap-motion-screen.log, including actual mesh screens
through the sampled axial cycle and capped discharge. The hollow neck/cap
exception requires measured radial clearance and the inner roof above the rim;
it is not a blanket collision exclusion. Full scene contracts pass 71/0 in
.tools/cap-motion-contracts.log. Fifteen pure cap-model checks also pass.
Native static/moving multi-angle inspection is still OPEN after Escape stop.
Seated rotation/thread/torque/seal behavior, every-frame swept-volume proof,
labeling, inspection and complete PLC station sequencing remain unverified.


Held-cap regression checkpoint (2026-10-06; native review OPEN):
Commit d06fcaf reuses the finishing tote's exported hollow cap at matching
installation scale, seats its roof against the chuck lower face, and raises
the held assembly together by 100 mm to clear the indexing neck. Forty focused
checks pass in .tools/capper-cap-raised.log; the two new held-shape/pose checks
failed before repair. Full scene contracts pass 71/0 in
.tools/capper-held-contracts.log. App shell passes 77 scenes / 5 demos / 295
assets with connection DISCONNECTED in .tools/capper-held-shell.log. These
headless checks do not add native visual acceptance. Axial motion, oriented
cap seating, release, capped discharge, labeling and inspection remain OPEN.


Tote cap geometry checkpoint (2026-10-06; native review OPEN):
The finishing candidate now has a hollow cap underside. Actual exported GLB
rays verify its inner roof seats at the neck rim within floating-point tolerance,
with nominal 5 mm radial clearance and a 20 mm roof above the rim. Four cap-fit
checks and five aperture checks pass. The underside asset render was inspected;
this is not native Windows scene acceptance or a thread, gasket or seal design.
The taller candidate uses a scene-configured 140 mm nozzle stroke, preserving
bore engagement. Build and 38 focused Start/travel/fill/geometry checks pass;
71 scene contracts pass with zero failures (.tools/tote-cap-cup-contracts.log).
Cap application, labeling, inspection and the full PLC station sequence remain
open, together with native static and moving multi-angle scene checks.


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


Scene 65 hand-dryer native/reference repair (2026-10-06, current checkpoint):
Completed the connected eight-item enclosure/fan/heater/sensor/hand layout and
PLC-owned live countdown. Three original replacement assets remain unapproved
candidates; archived copied-family reviews confer no approval. Hands are a
separate actor; hand presence comes from finite sensor-segment/actual hand mesh
intersection. Removed the fake manual timer-result input and unsupported machine.
Grounded enclosure supports carry the retained quarter-scale fan; heater rails
bear on two enclosure brackets. Inserted hands clear fixed equipment in the
focused bounds/OBB screen. Heat/air effects show eligible commands only.

Original illustrative ten-second reference: 19 focused offline checks PASS,
including timer/countdown boundaries, Stop/Run, cancellation/rearming/Reset,
malformed heat inhibition without rewriting the PLC image, actual sensor pose,
heater bracket bearing and inserted-hand clearance. It is generated only by
--audit-hand-dryer into .tools/plant-review-hand-dryer.rpproj.json, opened explicitly
via File menu. Five demos and blank default exercises remain intact.
Native active FR/FL/RL/RR/Top, physical input, completion, continuous held-hand
state and Reset verified. Display precision repaired and re-inspected: scan 500
shows 0.02 seconds with commands active; scan 501 shows 0.00 and both off.
Native withdrawal sampled at scan 502 rearms; reinsertion reaches 7.52 remaining
at scan 627. Mid-cycle Stop clears outputs/readout and heat/air effects; Run's
first accepted scan 628 restores a fresh 10.00-second nonretentive interval.
Final bracket revision rendered again. All owned preview windows closed normally,
exit zero. No appliance, thermal, protective-function or physical acceptance.
Build zero warnings/errors; controller conformance 144 PASS; scene contracts
71 PASS; help validates 294 assets/77 scenes; native controls and app shell PASS.
Full geometry/workflow regression: 987 checks PASS; this bounds/workflow screen
does not establish physical or mechanical acceptance.
Evidence .tools/hand-dryer-{audit,native-final,native-precision,native-brackets,
contracts-final,geometry-final,conformance,controls,shell}.log. A prior contract
attempt omitted pinned DOTNET_ROOT/PATH and was cancelled; only final run counts.

Scene 64 luggage-sort refreshed baseline (2026-10-06, next repair):
Native FR/FL/RL/RR/Top show a CNC obstructing the conveyor end and a disconnected
scale/diverter. The luggage_load accessory is byte-identical to an electrical
contactor/overload starter; the scale/load-cell platform is only a bare shear-beam
load cell. Keep the relevant powered swing-arm diverter and original honest
static weight readout, integrating them into the actual transport/weigh route.
Source purpose is numeric weighing/classification; training acceptance requires
one category result and incrementing only its class counter. Current booleanPanel
instead exposes manual bag_present/weight_valid/class_selected, lamp-only
weigh_cycle/class_result, no numeric weight/category/counters or process travel.
Normal Run opens the blank unauthored editor with NO CONTROLLER LOADED; expected
for an exercise and not process verification. Repair the true luggage/scale
identities and connected supported flow, add actual sensor and weight feedback,
and explicitly opened original PLC classification/counting reference. Do not
narrow source intent to symbolic lamps. Baseline closed normally, exit zero;
.tools/luggage-native-before.log. Scene 64 remains FAIL/open.

Scene 65 hand-dryer repair progress (2026-10-06, superseded snapshot):
Replaced copied shutters/container with original grounded dryer enclosure/outlet,
open heater rack, and sensor/hand station. Added fan and heater mounting brackets;
retained the delivered axial fan at quarter scale in an explicit mounted variant.
Archived invalid inherited reviews; all three replacements remain unapproved.
Removed the unsupported procedural machine and manual timer-result switch.
Eight equipment items and six symbolic points now separate raw hands_inserted,
mesh/segment-derived hands_present, diagnostic heater_inhibited, and PLC-owned
blower_run, heater_enable, remaining_seconds. Heat/air material effects indicate
eligible commands only; they are not measured temperature or airflow.

Original ten-second illustrative PLC reference is generated by --audit-hand-dryer
into ignored .tools/plant-review-hand-dryer.rpproj.json and opened explicitly.
It is not a default exercise or sixth demo. Focused audit: 13 PASS, including
500 eligible ticks at 20 ms, countdown, Stop/Run nonretentive restart, cancellation,
held-hand restart prevention, reinsertion, Reset. Build zero warnings/errors;
controller conformance 144 PASS; help validates 294 assets/77 scenes.

Native Windows: opened the reference via File menu, ran it, operated the rendered
physical input button, held accepted clock, inspected active FR/FL/RL/RR/Top.
At scan 250: 5.02 s remaining (display F1 rounds to 5.0), fan/heater indications on.
At scan 500: 0.02 remaining (display rounds to 0.0); scan 501 removes both outputs,
heat appearance and air command. Continuous held-hand run stayed off through
scan 1553; native Reset restores withdrawn hands, zero remaining and scan zero.
Top framing now shows complete rear fan. Closed normally with process exit zero.
Native mid-cycle Stop/reinsertion and finer readout precision still need review;
full geometry/contract regression and malformed-output probes remain pending.
Scene 65 remains open until those checks and current changes are checkpointed.
Evidence .tools/hand-dryer-{assets,import,audit,native-final,conformance}.log.

Scene 65 timed hand-dryer baseline (2026-10-06, historical before repair):
Repeated native FR/FL/RL/RR/Top and normal Run after the Scene 63 checkpoint.
Both air_outlet and heating_element are byte-identical full industrial roller
shutters; hand_presence_sensor is a 20-litre dispensing container. These three
accessory IDs occur only in this scene. Their inherited recognition passes
identify the copied families and do not validate the declared lesson identities.
Two substituted shutter models dominate/overlap the view, hiding the disconnected
fan and housing. Main machine is a procedural unsupported housing, rather than a
connected dryer assembly. The original PROGRESS / NO LIVE VALUE asset is honest
but static and disconnected; preserve its replacement identity while adding an
explicit numeric interface, rather than restoring an invalid inherited model.

Source prototype purpose: hand presence starts a blower/heater cycle with visible
remaining time. The current migration narrowed that to manual hands_present and
manual dryer_timer_active; booleanPanel has four BOOL points, two lamp-only
outputs, no actual blower/heater bindings, and no numeric countdown. Normal Run
opened the blank unauthored editor with NO CONTROLLER LOADED, as expected; it did
not prove a working timed process. Repair actual connected dryer/nozzle/heater/
sensor/hand layout, remove manual timer-result input, and supply an explicitly
opened original timed PLC reference with readable remaining-time output. Preserve
five demos and blank default exercises. No physical appliance/heater/airflow
acceptance is implied. Baseline window closed normally, exit zero; evidence
.tools/hand-dryer-native-before.log. Scene 65 remains FAIL/open.

Scene 63 coating-line repair (2026-10-06, preceding checkpoint):
Replaced the electrical-cabinet/motor-starter/roller-shutter copies with an
original open-ended spray tunnel, flat workpiece fixture and hollow exhaust duct
with a centred damper vane and fan stand. Removed the CNC from the carrying belt.
Retained the relevant spray-gun and axial-fan assets in explicit mounted variants;
presentation pedestals are hidden only in this installation. Roof mounting and
service routes connect the gun; exhaust duct reaches the retained fan inlet.
Three replaced assets remain unapproved candidates. Archived copied recognition
and renders do not approve their replacements. No airflow, coating quality,
liquid/powder classification, physical interlock or mechanical acceptance claim.

Fourteen actual items / thirteen typed symbolic points. Whole catalog remains
77 scenes, 294 runtime assets, exactly five authored demos, 609 actual equipment
items. Refreshed the previously stale aggregate equipment counts from all current
scene definitions. Default coating exercise remains blank. PC owns actual finite
STATION/EXIT beam feedback from WORKPIECE_BODY triangles, position/speed, raw
momentary START, manual maintained SPRAY READY/VENT READY and three diagnostics.
PLC owns index_run, spray_enable and vent_run. No manual station-result toggle.

The single-clock coating plant drives supported load travel, belt animation,
fan rotation, instantaneous illustrative damper position and eligible spray cone
from accepted symbolic output images. Motion/spray conflict or missing readiness
holds the plant with diagnostics while preserving the PLC command image. Missed
EXIT clamps X to supported bounds instead of deleting the part or fabricating
completion. Spray requires the positioned body, both manual readiness inputs,
vent command and no indexing. Manual readiness does not prove measured airflow.

-- --audit-coating passes 23 focused checks. Eight hundred ten sampled workflow
observations include stopped-clock probes; a separate uninterrupted cycle uses
574 accepted scans with exactly 100 spray ticks and 50 purge ticks at 20 ms.
The original reference uses ten editable PLC rungs: fresh START with readiness,
index to actual STATION, stopped two-second spray with ventilation, one-second
post-spray purge, discharge to actual EXIT, then wait for Reset. Reference is
created only under ignored .tools/plant-review-coating-line.rpproj.json for an
explicit normal File Open. Readiness alone cannot replay rejected START. Stop
freezes position/phase and timer snapshot, clearing commands; Run resumes the
retained phase with a fresh nonretentive interval after cleared commands. Reset
restores X=-2, raw inputs false, commands dark and zero scan. Older projects need
the revised Scene 63 roles. External/physical PLC behavior has not been tested.

Native Windows: normal File Open / Return to Scene, actual 3D readiness selectors
and START accepted. Held scan225 / 4.50 s / X=0.01 had STATION true, index false,
spray/vent true; FR/FL/RL/RR/Top inspected. At 6.50 s spray was false, ventilation
remained true with the part stationary. At 11.50 s EXIT true / X=2.23 retained
the supported part with all commands off. Final models re-inspected five angles
at home and continuous-cycle EXIT, including corrected overhead framing: fan
clears review toolbar. Normal continuous playback reached supported EXIT and
held through later scans; native Stop held scan7526 / X=2.23. Reset and missing
readiness were verified by the deterministic audit; no native Reset claim.
Both owned previews are now absent; first exited normally with code zero, second
process/handle was absent after the user update, so its exit code is unavailable.
Logs: .tools/coating-{assets,build,import,audit,geometry-final,conformance,contracts,
help,controls,shell}.log and coating-native-{final,camera-final}.log.

Final regression: build zero warnings/errors; 968/968 rendered geometry/workflow
checks pass. Controller conformance 144/144, scene contracts 71/71, help 294 assets
/ 77 scenes, rendered scene controls, review-overlay input, external-image and
headless app shell pass. App-shell probe reports the expected WORKSPACE_LOAD_FAILED
warning when no saved workspace exists. No physical PLC transport constructed or
connection attempted by conformance. Deterministic probes do not constitute solid
collision, airflow, coating quality or external-PLC commissioning acceptance.

Whole-program goal ACTIVE and incomplete. Continue with remaining matrix failures,
including luggage weighing/reject layout, hand dryer, EV charging and radar piping.

Historical Scene 63 baseline (before the repair above):
Repeated FR/FL/RL/RR/Top in the Windows shell. CNC enclosure occupies the belt;
coating-enclosure asset is an electrical cabinet, workpiece asset a motor starter,
and damper asset a roller shutter. Spray gun has a relevant identity but sits
unmounted away from the conveyor. Scene uses booleanPanel; its three outputs
bind only lamps, and workpiece_at_station is manually toggled. Normal Run opened
the blank editor with no controller loaded, as expected for an unauthored exercise.
No timed coating/index/discharge reference exists yet. Source description is a
spray-coating line, not an immersion bath. All four accessory IDs are used only
by this scene. Preserve the valid spray-gun asset; repair wrong identities,
connect the supported workpiece route and ventilation/spray installation, then
implement actual position feedback and an explicitly opened timed reference.
Baseline window closed normally; .tools/coating-native-before.log. Scene 63 is
still FAIL/open; no new geometry or process implementation has been accepted.

Previous Scene 62 bag indexing repair (2026-10-06):
Replaced the copied pneumatic pusher/carton with an original filled sack, flat
bearing underside, tapered body, sealed ends and BAG label. Removed duplicate
pusher/drive/control substitutes. Eight actual items and ten symbolic points;
whole-catalog equipment total 609. Catalog remains 77 scenes / 294 runtime assets,
with exactly five authored demos and default exercises blank.

ENTRY and EXIT now span the carrying belt at 1.1 m and derive feedback from a
finite optical segment intersecting delivered BAG_BODY triangles. EXIT X=1.7 m,
front stand Z=1.3 m and rear stand Z=-1.75 m clear the integral control station
and cable route. Static installation screen: two enclosing-bound candidates,
zero unresolved after cable-triangle/local-bound refinement. This is a sampled
geometry screen, not solid collision or physical installation acceptance.

PC owns actual entry/exit, position/speed, raw momentary START, manual maintained
PAUSE BLOCKED/CLEAR, and motion_inhibited/travel_limited diagnostics. PLC owns
run enable and reverse direction separately; both true is valid permitted return.
Single green/amber lamps project those commands. Removed fake sensor toggles.
Bag and conveyor travel share accepted scan time; no separate conveyor callback.
Illustrative 0.5 m/s kinematics and supported X bounds -2.6..2.6 m. A malformed
reverse without CLEAR holds motion while exposing the command image; missed EXIT
clamps supported travel and reports travel_limited without rewriting PLC outputs
or fabricating completion. Update older projects for revised Scene 62 point roles.

-- --audit-bag-index passes 30 focused checks / 1203 accepted samples. It creates
only ignored .tools/plant-review-bag-index.rpproj.json for explicit File Open.
Six original reference rungs: fresh START at ENTRY runs forward; actual EXIT
stops into pause; manual CLEAR plus a fresh START runs reverse; actual ENTRY
stops into idle. Travel-phase START and blocked-pause START are discarded.
CLEAR alone does not initiate return; losing CLEAR holds the retained return.
Stop retains phase/pose but clears output commands and pending pulses; Run
resumes the retained leg with its permissive. Reset restores supported X=-2,
raw inputs false, outputs dark and zero scan. Sack remains unapproved candidate;
old pusher recognition/renders are archived under
review/historical_invalid_identity_20261006 and do not approve this replacement.
No flexible-body, material, hardware or commissioning claim.

Native Windows: default blank exercise observed; explicit File Open / Return to
Scene; actual 3D START and PAUSE CLEAR selector accepted. Final installation
FR/FL/RL/RR/Top inspected at forward X=-1, EXIT X=1.28, reverse X=0.28; bag stayed
supported and visible. Missing CLEAR / CLEAR alone held EXIT. Fresh START lit
both run/reverse lamps and moved back. Losing CLEAR held X=0.28 for two stepped
seconds with run false / reverse true. Stop cleared both outputs; Run with CLEAR
resumed reverse to ENTRY X=-1.58. Stop also froze scan100 / X=-1 with hold released.
Reset restored X=-2 / zero scan / outputs off. After final framing adjustment,
Top home and continuous returned ENTRY inspected; rear sensor head clears review
bar, BAG label readable. Normal continuous outbound reached EXIT X=1.28 and return
reached ENTRY X=-1.58 with both outputs off. Native previews exited normally.

Build zero warnings/errors; conformance 144/0; final contracts 71/0 with 77
positive catalog metadata probes; help 294 assets / 77 scenes valid.
Rendered geometry/workflow 945/945 PASS (including 30 bag workflow/installation
and five new selector-alignment checks). Rendered scene controls, review-overlay
input, external-image and virtual-controller UI PASS; headless app shell PASS
(77 scenes, five demos, 294 assets). All verification processes exited normally;
no regression errors. App-shell Load Last Workspace emitted the expected
WORKSPACE_LOAD_FAILED warning because no saved workspace existed. No PLC connection.
Logs: .tools/bag-index-{geometry,controls,controller-ui,app-shell,contracts-final,
help-final}.log. Conformance evidence: .tools/bag-index-conformance.log.

Whole-program goal ACTIVE and incomplete. Next: Scene 63 Coating Line, then hand
dryer, EV manager and remaining review-matrix/process failures.

Scene 61 drawbridge repair (2026-10-06, previous checkpoint):
Replaced copied scissor/table, guard and shutter geometry with an original hinged
4 m bridge deck, two supported 4.8 m road barriers, and a shaft-connected cam /
HOME and RAISED roller switches. Grounded approaches/piers, landing seats, channel
and approach rails are visible. Barrier arms clear the fixed rails. Eight scene
items, fifteen symbolic points; actual whole-catalog equipment total is 613.
Historical prototype, blank exercises and exactly five authored demos remain.

PC owns raw maintained CLOSE/OPEN request and manual NO/YES STOPPED acknowledgement.
STOPPED is not a traffic detector. Actual deck/barrier angles derive HOME, RAISED,
CLOSED and OPEN feedback; removed the fake manual HOME toggle. PLC owns both bridge
directions, both barrier directions and red/green commands. Invalid commands remain
visible; conflicting/impossible motion asserts PC motion_inhibited and blocks the
affected motion. Amber traffic lenses stay dark because no amber command exists.
Update older Scene 61 projects for the new point roles and outputs.

-- --audit-drawbridge passes 35 focused checks and generates only the ignored
.tools/plant-review-drawbridge.rpproj.json for explicit File Open. Six reference
rungs close barriers before raising, require manual STOPPED, lower before opening
barriers, and release green only after HOME and OPEN limits. Original illustrative
travel times: gates 2 s, deck 4 s to 70 degrees. Limits and cam follow the rendered
angles every accepted 20 ms scan. This is symbolic/offline kinematics, not traffic
control, structural/load analysis, physics collision or commissioning evidence.
Three assets remain unapproved candidates; old unrelated recognition/render
evidence is retained under review/historical_invalid_identity_20261006 and does
not approve the replacement geometry.

Native Windows: explicit File Open and Return to Scene; physical request and
STOPPED selectors; missing STOPPED held deck home with closed barriers. Deck at
35 degrees after 2 s and 70 degrees after 4 s accumulated motion; losing STOPPED
held 35 degrees. FR/FL/RL/RR/Top inspected at home/closed, mid-travel and raised.
Focused cam contact and separate green HOME / amber RAISED lenses inspected at
both endpoints; both off mid-travel. Shaft connection and plate/pier clearance
inspected from front/rear. Stop cleared outputs and froze actual pose and scan
clock with review hold off; Run resumed lowering. Normal continuous opening and
return reached raised/closed/red, then HOME/open/green. Reset restored zero scan,
home/closed, raw requests false and outputs off. Camera fits complete motion;
final top-view framing verification and rendered regression results follow below.

Focused audit 35/35 PASS, build zero warnings/errors, conformance 144/0, contracts
71/0 (77 positive catalog metadata probes), help 294 assets/77 scenes valid.
Final native top view inspected at home with barriers both down and fully raised
at scan 594 / 11.88 s; raised tips clear the clock/toolbar after the framing fix.
Rendered geometry/workflow 910/910 PASS; controls, review-overlay input,
external-image, virtual-controller UI and app-shell regressions PASS. Native
preview and all verification processes exited normally. No PLC connection.

Whole-program goal ACTIVE and incomplete. Next: Scene 62 Bag Indexing Conveyor,
then coating bath, hand dryer, EV manager and remaining matrix/process issues.

Scene 60 pedestrian-crossing repair (2026-10-06, previous checkpoint):
Replaced three wrong copied assets: horizontal 10 x 6 m road with two raised
sidewalks and nine crosswalk marks; red/amber/green vehicle heads; orange-hand /
white-walking-person pedestrian heads. Two opposing heads of each kind stand on
the sidewalks. Request button is supported; manual PATH BLOCK/CLEAR selector is
separate on the floor. Seven scene items, eight symbolic points; whole catalog
actual equipment total 614. Three older counter-lesson catalog counts/types were
also synchronized with their actual scene files. Contract verification now rejects
stale equipment counts/types, including duplicate types (77 positive/3 negative
metadata probes). Historical prototype, blank exercises and five demos remain.

CROSS is a momentary PC raw request; clear_to_finish is manual raw PATH feedback,
not an automatic detector. sequence_running is now PLC status, removing its fake
operator toggle. Added vehicle_amber/vehicle_ready/pedestrian_stop commands;
vehicle_stop now drives red, WALK drives white symbols. Update older projects.
Renderer exposes independently commanded channels even if user ladder conflicts.
An unbound reference_running PLC output detects Stop and prevents retained WALK
from being republished directly on Run. No live PLC transport is constructed.

-- --audit-pedestrian-crossing runs 30 checks and generates the ignored twenty-rung
.tools/plant-review-pedestrian-crossing.rpproj.json for explicit File Open. It
starts red/hand for 3 s; waits for PATH CLEAR, then idle green/hand. A fresh idle
request with CLEAR selects amber 1 s, all-red 0.5 s, WALK 2 s, steady hand/red
clearance 3 s. Green waits for PATH CLEAR. Blocked/active requests are discarded;
held request produces one cycle. Source supplies no presets: these are original
illustrative training choices. The simplified reference omits a flashing-hand
change interval, traffic/people motion and road engineering; no compliance claim.
Signal appearance uses FHWA Chapter 4E visual reference only:
https://mutcd.fhwa.dot.gov/htm/2009r1r2/part4/part4e.htm
Old enclosure/beacon recognition evidence is retained in each asset's
review/historical_invalid_identity_20261006 and invalid for new geometry. Assets
remain candidates with independent approval pending; no OEM/certification claim.

Native Windows: File Open/Return to Scene worked. Held Run scan zero, startup
red/hand at 1. Physical PATH CLEAR, idle green at 151; physical CROSS entered amber
at 152, all-red at 202, white WALK at 227. FR/FL/RL/RR/Top inspected during WALK;
front/rear faces, sidewalk support, separate mast/control footprints and stop
lines are visible. Focused WALK and hand/red faces inspected. PATH BLOCK during
WALK: hand/red at 327, still held at 502 after clearance expired. Focused PATH /
BLOCK / CLEAR legend and pointer were readable; physical CLEAR released idle at
503. Second request reached WALK at 603; Stop cleared commands and retained phase
3; Run's first scan 604 selected startup phase 5. Normal continuous clock returned
to idle at 1486; another request was amber at 1859 and completed idle green at
3632. Reset stopped at zero with all eight points false. Owned reviewer closed
normally (exit zero). These are sampled native observations, not every-frame or
mechanical/hardware proof. Overhead visors obscure faces in top view as expected;
close focus may place upper housings behind the existing QA overlay.

Verification: build zero warnings/errors, focused 30/30, rendered geometry and
workflow 865/865, controller conformance 144/144, scene contracts 71/71. Rendered
scene controls/overlay/external image and virtual-controller UI pass. Help
294 assets/77 scenes; shell 77 scenes/294 assets/five demos/28 diagnostics pass.
Ignored evidence: .tools/crossing-*.log. Whole-program goal remains active.
Next: Scene 61 Drawbridge Control, then the remaining review-matrix failures.

Scene 59 running-light-tower repair (2026-10-06, previous checkpoint):
Replaced the fake held-input pushbutton with an actual ENABLE OFF/RUN selector.
STEP now supplies a momentary PC-owned pulse, consumed on one accepted scan.
Replaced obsolete single green-only tower_step_active with independent PLC-owned
BOOL tower_red/tower_amber/tower_green channels. All three imported lenses render
independently, including conflicting commands. Update older projects to the new
outputs. Three grounded separated equipment items remain; equipment instances
615, scenes 77, assets 294 and authored demos five. Historical prototype, default
empty exercise editor and validated real transport remain unchanged.

-- --audit-running-tower runs 29 offline controller/scene checks and writes
ignored .tools/plant-review-running-light-tower.rpproj.json. Open this seven-rung
original reference explicitly through File -> Open Ladder Agent Project. It uses
PLC rising-edge sampling, DINT phase increment/wrap and three exclusive color
coils. Source specifies manual pulse-driven steps, without timing or wrap detail;
green-to-red wrap is a declared original training choice, not source parity.
First enabled scan selects red and discards simultaneous Step. Subsequent fresh
edges select amber, green, red. No idle advance. One accepted low scan rearms an
edge; unsampled repeated clicks coalesce. OFF clears phase/commands next scan.
Stop clears color commands/pending Step, retaining ENABLE/phase. Run restores
retained color and establishes a fresh edge baseline without startup advance.
Reset clears requests/phase, returns OFF and leaves stopped scan zero.

Native Windows: normal File Open, Return to Scene, held Run scan zero. Physical
ENABLE selected red at scan 2; physical STEP selected amber at 4 and green at 6.
Three unsampled physical STEP clicks coalesced, selecting red at 8. Idle through
33 stayed red. Pending STEP then Stop at 33 cleared input/all lenses; Run at 35
restored red without advancing. Physical OFF cleared at 36; disabled STEP was
consumed without commands at 38; re-enable selected red at 39. FR/FL/RL/RR/Top
inspected, plus readable ENABLE/OFF/RUN and STEP close views. Top confirms layout;
the tower cap naturally hides lateral lenses overhead. All three color lenses
are distinguishable in side views; no intersections or floating bases observed.
Continuous playback: amber at 653 remained amber at 1001; next physical STEP
green at 1418; physical OFF cleared at 1818. Reset stopped scan zero with all
five points false. Owned reviewer closed normally, exit zero. These are sampled
native observations, not every-frame, mechanical, hardware or PLC parity proof.

Verification: build zero warnings/errors, focused 29/29, rendered geometry/
workflow 830/830, scene contracts 71/71, controller conformance 144/144. Rendered
scene controls, overlay input, external image and virtual-controller UI pass.
Shell 77 scenes/294 assets/five demos/28 diagnostics; help and diff whitespace
checks pass. Ignored evidence: .tools/running-tower-*.log. Whole-program goal
remains active. Next: Scene 60 Pedestrian Crossing, then remaining matrix issues.

Scenes 57/58 flashing-lesson repair (2026-10-06, previous checkpoint):
Scene 57 has one maintained ENABLE OFF/RUN selector and separate amber A / green
B lamps. Removed alternate_phase and its fake PC phase button: PC supplies raw
alternate_enable; PLC owns timing and both outputs. Old projects must move phase
into PLC memory. Scene 58 retains all three original raw BOOL requests through
actual ENABLE/FAST/SLOW selectors, followed by a single green lamp in a grounded
row. Both/neither rate selections inhibit the explicit reference without priority.
Equipment instances total 615; 77 scenes, 294 assets and five authored demos.
Historical source, default empty exercises and real transport remain unchanged.

-- --audit-flash-pair executes 49 controller/scene checks, generating ignored
.tools/plant-review-alternating-lamps.rpproj.json (five rungs) and
.tools/plant-review-variable-flash-rate.rpproj.json (nine rungs). Open explicitly
through File -> Open Ladder Agent Project. Half-periods 0.5 s for alternation,
0.2 s FAST and 0.5 s SLOW are original training choices, absent from the source.
Timers precede phase/output coils, avoiding one extra scan per transition.
OFF/invalid selection clears lamps, phase and timers next accepted scan.
Alternation starts A; variable rate starts OFF. Direct valid rate change wholly
between accepted scans retains phase and starts the new full interval; separate
accepted changes can pass through invalid selection and reset phase. Stop clears
outputs/nonretentive timers but retains requests/PLC phase. Run resumes that phase
with a fresh interval. Reset clears all state and leaves stopped scan zero.

Native Windows references opened through File. Scene 57: physical ENABLE;
A at scan 1/24, B at 25, A at 50, B at 75. Stop at 75 dark; Run 99 B true /
ET 0.48 s, 100 A true / B ET 0.50 s. OFF cleared at 101. Continuous A at 111,
B at 341; physical OFF cleared both lamps; Reset stopped zero. FR/FL/RL/RR and
readable ENABLE/OFF/RUN focus inspected. Initial diagonal Top put an end selector
under the QA toolbar; aligned overhead azimuth rebuilt and visually verified with
all three items clearly visible. These QA camera changes do not move equipment.

Scene 58: physical ENABLE/FAST; dark 9, green 10/19, dark 20, green 30. Physical
SLOW while FAST selected made a pending conflict at held 30; accepted 31 dark.
FAST OFF left SLOW: 55 dark after 24 new scans, 56 green, 81 dark, 106 green.
Stop 106 dark; Run 130 green, 131 dark. SLOW OFF remained dark through 156 NO RATE.
Five full-scene angles inspected at held 10; focused FAST/SLOW labels/detents
readable. Normal I/O scrollbar exposes all three raw inputs. Continuous SLOW:
dark 166, lit 491; ENABLE OFF cleared lamp with SLOW retained. Continuous FAST:
dark 2306/3370/3828, lit 4431. Reset all three raw inputs/lamp false and stopped
scan zero. Owned native windows closed normally, exit zero. These are snapshots
and accepted-scan observations, not frame-by-frame or real-controller parity.

Verification: build zero warnings/errors; focused 49/49, geometry/workflow 788/788,
scene contracts 71/71 and controller conformance 144/144. Rendered scene controls,
review-overlay/external-image and virtual-controller UI pass. Shell 77 scenes /
294 assets / five demos / 28 diagnostics; help 294 assets / 77 scenes and diff
whitespace check pass. First geometry attempt exposed a verifier-only single
selector assumption; every configured dial now matches its equipment/raw input,
preserving all five alignment/reset checks per selector. Reset checks actual
pointer restoration, rather than fixed OFF label text. Logs: ignored
.tools/flash-pair-*.log, alternating-lamps-native.log, alternating-top-native.log
and variable-flash-rate-native.log.

Whole-program goal remains active. Next: Scene 59 Running Light Tower, then
remaining operational/installation issues recorded in this review matrix.
This checkpoint does not establish every scene's mechanical or hardware acceptance.

Scene 56 rotary-flasher repair (2026-10-06, previous checkpoint):
replaced the mislabeled pushbutton with an actual maintained MODE OFF/FLASH
selector. Removed the manual flash_tick input/button: PC now supplies only
raw flash_mode_selected, while PLC owns timing/phase/flash_lamp. The unused
tower tiers stay dark. Two separated grounded equipment items and two points
remain. Equipment instances total 616; catalogs still contain 77 scenes,
294 assets and exactly five authored demos. Historical prototype is unchanged.

-- --audit-rotary-flasher runs 22 checks and writes ignored explicit reference
.tools/plant-review-rotary-flasher.rpproj.json. Four rungs use two TONs followed
by a phase coil and lamp coil. A 0.5 s half-period is an original offline
training choice absent from the source. Both TONs evaluate before the phase
coil, so each phase lasts 25 accepted 20 ms scans without accumulating an
extra transition scan. Default exercises remain empty; open the reference
through File. Old projects must replace manually supplied flash_tick with
PLC timers/phase. No runtime transport or timer-engine change was made.

OFF clears phase, timers and lamp on the next accepted scan. Stop freezes scan
and clears lamp/nonretentive timers while retaining selector and PLC phase.
Run with FLASH retained resumes that phase with a fresh full half-period.
Application Reset clears selector/phase/timers/lamp and leaves stopped scan zero.
This is an offline reference behavior, not a live-controller restart guarantee.

Native Windows: explicit reference opened through File -> Open Ladder Agent
Project. Run held scan zero, physical selector FLASH accepted. Scan 24 / 0.48 s
was dark; scan 25 / 0.50 s visibly lit green. FR/FL/RL/RR/Top were inspected at
held scan 25. The equipment-focus FR view showed MODE/OFF/FLASH readable with
the pointer aimed at FLASH. Full-scene scan 50 / 1.00 s was dark and scan 75 /
1.50 s lit. Stop at 75 cleared both ET values/lamp and disabled stepping. Run
held 75; scan 99 showed ON ET 0.48 s/lamp true, and 100 showed 0.50 s/lamp false.
Releasing Hold showed normal playback dark at scan 103 / OFF ET 0.06 s, still
dark at 521 / OFF ET 0.42 s and lit at 843 / ON ET 0.36 s. Physical OFF during
continuous playback cleared both timers/input/lamp. Reset restored stopped
zero; normal close exited zero. Overhead naturally hides the front labels and
most lens faces; diagonals and equipment focus cover those surfaces.

Verification: build zero warnings/errors; focused 22/22 and expanded geometry
727/727 (22 workflow plus five selector checks); 71 scene contracts pass;
rendered scene controls/review overlay/external-image regression passes;
app shell 77 scenes/294 assets/five demos/28 diagnostics; help 294 assets/77
scenes and git diff --check pass. The first contract invocation omitted the
pinned DOTNET_ROOT/PATH and was cancelled; rerunning with the configured
runtime completed all 71. Logs are ignored .tools/rotary-flasher-*.log.
Controller conformance 144/144 was verified in the preceding timer checkpoint.
These checks do not establish every scene's operational or hardware acceptance.

Whole-program goal remains active. Next: Scene 57 Alternating Lamps and Scene
58 Variable Flash Rate, then remaining installations recorded in the matrix.

Scenes 54/55 timer-lesson repair (2026-10-06, previous checkpoint):
Demo 2 retains its actual authored two-second TON program. Scene 54 now has a
maintained REQUEST OFF/ON selector with correct imported pointer/tick geometry
and readable white face/detent labels. Only raw timer_request is PC-owned;
delayed_lamp follows the PLC result. Scene 55 now has one momentary START,
consumed by one accepted scan; removed time_active was a manually precomputed
timer result. Only PLC timed_lamp drives its green tier; unused tiers stay dark.
Both scenes retain their grounded separated installation and two I/O points.

The new -- --audit-timer-lessons executes 33 actual controller/scene checks.
It tests the real authored Demo 2 and writes an ignored, explicitly opened
.tools/plant-review-timed-lamp-off.rpproj.json: two rungs with a three-second TP.
Three seconds is an original offline training choice absent from the source.
No extra authored demo or automatic solution loading was added. Old Scene 55
projects must replace time_active with raw START and PLC timer output. Five
authored demos, 77 scenes and 294 runtime assets remain; current equipment
instances total 617 after removing the fake time switch. Historical prototype
files are unchanged. Generic selectors retain numeric labels unless configured.

Native Windows evidence, final assembly: Scene 54 FR/FL/RL/RR/Top were inspected
and close FR REQUEST/OFF/ON labels were readable. Actual physical selector and
held scans showed the existing TON off at scan 99 / ET 1.98 s, on at 100 / 2.00 s.
Stop at scan 50 / ET 1.00 s cleared ET/lamp, retained ON and disabled stepping.
Run plus 100 fresh scans switched the lamp on at scan 150. Physical OFF at 150
cleared input immediately and lamp/ET at accepted scan 151. Reset restored
OFF, stopped scan zero and no lamp. Scene 54 continuous playback was not
remeasured in this checkpoint; the exact-boundary evidence uses held scans.

Scene 55's explicit reference was opened through normal File -> Open Ladder
Agent Project. Physical START at held scan zero gave lamp true, input consumed
and ET 0.02 s at scan 1. FR/FL/RL/RR/Top were inspected in that state. A second
press during the interval did not restart ET: scan 77 showed 1.54 s. The lamp
was on at 149 / ET 2.98 s and off at 150 / 3.00 s. A fresh START then ran another
interval; Stop at scan 200 / ET 1.00 s cleared lamp/ET, and Run plus 100 scans
left the lamp off at scan 300. Normal continuous playback then visibly lit the
green lamp (ET 0.64 s) and subsequently cleared it with raw START false; it did
not repeat. Reset left stopped scan zero and both points false. Both final
native sessions exited zero after normal close. Timing is accepted offline
scan time, not a wall-clock performance guarantee or live-controller proof.

Verification: build zero warnings/errors; final focused timer audit 33/33;
broad geometry/workflow 700/700, including five additional selector checks;
71 migrated scene contracts; 144 deterministic controller tests; rendered
scene-control, review-overlay input and virtual-controller UI regressions;
shell 77 scenes/294 assets/five demos and 28 diagnostics; help 294 assets/77
scenes and git diff --check pass. The 700 sweep preceded only the cosmetic
REQUEST font/contrast adjustment; final native inspection and the focused
audit covered that final label. Logs are ignored .tools/timer-lessons-*.log,
.tools/timer-delayed-final-native-2.log and .tools/timer-pulse-final-native.log.
These bounded checks do not establish every scene's operational acceptance.

The whole-program goal remains active. Next: Scene 56 Rotary Flasher, then the
remaining timer/sequence and process installations identified in the matrix.

Scene 49 package-grouping repair (2026-10-06, previous checkpoint):
replaced the disconnected belt/roller/pallet and substitute stop/sensor layout
with two original scoped Blender/glTF assemblies: a continuously supported
powered roller line/receiver and a guided retracting stop. Three real cartons,
two actual optical stations, an inline operator row and a separate GROUP display
form the installation. Capacity three, 0.4 m/s travel and one-second stop stroke
are declared offline training choices; no OEM or source-exact timing is claimed.
Prescribed accumulation excludes slip, contact forces and collision dynamics.

Accepted local controller/plant scans own every carton, gate, rod and roller
pose. Raw PC feedback comes from actual beam crossings and positions; PLC CTU
owns the count and PLC BOOL outputs own feed/release. The release latch requires
count three plus actual accumulation. The gate clears the cartons before travel;
a connected receiving surface supports the whole transferred group. All three
cartons remain visible after actual completion. Enable/path loss holds motion;
Stop freezes scan and plant while clearing the PLC output/readout image. Run
restores retained CTU/release memory; Reset empties the finite batch and stops.

Reproduce with -- --audit-package-grouping: 27 checks / 3,847 sampled poses pass.
The audit writes ignored .tools/plant-review-package-grouping.rpproj.json, a
seven-rung reference opened explicitly via File -> Open Ladder Agent Project.
Default exercise editors remain empty and exactly five authored demos remain.
Old Scene 49 projects must replace manual group_count_reached with raw actual
feedback and PLC-owned DINT group_count, using the current scene help. Historical
prototype files are unchanged. This replaces Scene 49's former two static carton
support checks with full three-carton route/count/Stop/Reset coverage.

Native Windows evidence: the explicit QA reference was opened through File,
then Run, Enable, Clear and Load. Held scan 75 / 1.50 s counted the first actual
beam crossing; FR/FL/RL/RR/Top were inspected. Stop at 75 disabled stepping and
held the carton; one Run scan republished count one without another edge.
The first/second cartons accumulated at 18.02/34.02 s with counts one/two.
At scan 2375 / 47.50 s three retained cartons waited behind the stop at 40%;
all five views were inspected. At scan 2450 / 49.00 s the raised stop cleared
the crossing group; all five views were inspected. Stop/Run held and resumed
that crossing. Ordinary continuous playback completed the group, then held
scan 3093 / 61.86 s showed count three, done true and the returned stop at zero.
The retained receiver group was inspected from all five views; close front
GROUP 3 was readable. Fourth Load was blocked with the idle-feed/free-position/
Reset explanation. Reset returned empty/stopped/scan zero. The physical 3D LOAD
button accepted a fresh carton; a final Reset left the scene stopped. The Top
view partly crops the far infeed behind the review HUD; diagonal views resolve
that area. Native package-grouping-final-native exited zero.

Verification: build zero warnings/errors; 144 controller tests; 662 shared
geometry/workflow checks; 71 scene contracts; shell 77 scenes / 294 assets /
five demos; help 294 / 77; virtual-controller UI and rendered scene-control/
review-overlay regression all pass. Rotating-cylinder support checks use actual
mesh vertices, avoiding inflated rotated bounding-box contact reports. These
are sampled offline geometry and reference-controller results, not swept-solid,
hardware safety, roller mechanics or live PLC commissioning acceptance.
Whole-program goal remains active. Scenes 50-53 already have scoped repairs;
next gaps are Scene 54 selector labeling and Scenes 55-59 raw timer/control
behavior. Shared substitute assets elsewhere remain unresolved.

Scene 48 parking-entry repair (2026-10-06, previous checkpoint):
replaced the motor-starter vehicle and substitute barrier/wall with four
original scene-scoped Blender/glTF models: supported parking pad, wheeled
vehicle, barrier cabinet and hinged boom. Two vehicles use separate marked
bays. Five operator buttons are inline outside the approach route; sensor feet,
barrier, count-display support and available lamp are separated.

The original offline plant has two spaces, a prescribed 1 m/s route and a
one-second 90-degree boom stroke. These are declared training assumptions,
not manufacturer dimensions, source-exact ladder logic or vehicle physics.
The actual accepted controller/plant clock owns all movement. PLC-owned BOOL
commands drive the boom/vehicle; PC feedback comes from actual positions,
beam crossings, fully parked arrivals and fully completed departures. PLC
CTUs and subtraction own occupancy; the PC does not precompute the count.
The occupied-passage boom guard is an offline collision constraint, not a
validated barrier safety function. Static wheels do not model steering/traction.

Reproduce with -- --audit-parking-entry: 27 focused checks and 6,366 sampled
poses pass, including four-wheel pad contact, full route support, moving boom /
sensor / other-car clearance, permissive loss, partial motion Stop/resume,
repeat arrival/departure counts, reentry, explicit removal and stopped Reset.
The audit writes ignored .tools/plant-review-parking-entry.rpproj.json; open
this six-rung QA project explicitly through File -> Open Ladder Agent Project.
It never auto-loads: default exercise editors remain empty and there are still
exactly five authored demos. Old Scene 48 projects need the new raw BOOL
feedback, typed barrier position and PLC DINT occupancy bindings from help.
Historical prototype files remain unchanged; migrated JSON/help are current.

Native Windows operator evidence: held scan 200 / 4.00 s showed a waiting
vehicle and boom 60%, count zero; FR/FL/RL/RR/Top inspected. Stop froze both
pose and scan; Run resumed. At scan 425 / 8.50 s the actual raised boom cleared
the crossing vehicle; all five angles inspected. At 14.50 s the turning car
remained supported; at scan 900 / 18.00 s it was parked and retained, count one.
Ordinary continuous Run parked the second car, count two; full bays were
inspected from all five angles and close front OCCUPANCY 2 was readable.
Stop cleared the PLC output/readout image to zero while both cars and CTU
memory remained; one accepted Run scan republished two without a new edge.
This zero is a cleared output image, not an empty physical lot.

Exit at scan 3743 / 74.86 s showed the raised boom, crossing vehicle and
remaining parked vehicle, count two; all five angles inspected. At scan 4193 /
83.86 s departure completed, count one, and the outbound car stayed visible.
Explicit REMOVE cleared only that car, leaving count one and the other bay
occupied. The second exit completed at scan 5093 / 101.86 s, count zero, with
the departed car retained. Application Reset emptied the lot and stopped at
scan zero. Native log parking-entry-final-native exited zero.

The final inline control arrangement was re-inspected in native FR/FL/RL/RR/
Top. Rebuilt UI showed Approach immediately after ENTER at held scan zero;
two 18-second cycles gave count two at scan 1800. Third ENTER retained both
cars and displayed the specific free-bay/EXIT explanation, replacing misleading
Reset advice. Reset returned empty/stopped/scan zero; final-native-2 exited zero.

Verification: build zero warnings/errors; 144 controller tests; 637 shared
geometry/workflow checks with the review overlay; final scoped parking checks;
71 scene contracts; shell 77 scenes / 294 assets / five demos; help 294 / 77;
virtual-controller UI and rendered scene-control/overlay regression all pass.
The scene-control verifier requires rendering: its headless pointer run failed,
then the rendered invocation passed. The final scoped audit and scene contracts
cover the later control-row move. Catalog aggregate equipment totals were
refreshed from all 77 actual scene definitions (618); stale totals had also
predated this repair. No real PLC transport or hardware acceptance occurred.
Reusable substitute vehicle/road/barrier catalog assets in other scenes remain
unresolved. Whole-program goal remains active; next Scene 49 box stop/release
has disconnected stop/sensor/receiver geometry and no accepted motion cycle.

Scenes 46/47 button-counter repair (2026-10-06, previous checkpoint):
replaced PC precomputed channel-ready/pattern-ok toggles with raw one-accepted-scan
A/B presses and RESET. Added correctly labeled A/B/RESET physical buttons and
two PLC-owned DINT accumulated-count readouts; all six props sit in a separate
inline row. PLC ladder owns both CTUs and comparisons. The existing pulse
interface coalesces clicks before the same accepted scan; it does not queue
every rapid click or model a hardware high-speed counter.

The prototype contracts specify no presets, order or timing. The explicitly
opened original offline reference for Scene 46 uses inclusive A=2..3/B=3..4
numeric count windows; Scene 47 uses exact A=2/B=3 count comparison. Both permit
either press order and impose no elapsed-time window. These are declared
training choices, not source-exact solutions or ordered-pattern validation.
Old projects must replace removed ready/pattern_ok inputs and bind the new
raw BOOL inputs plus PLC DINT count outputs. Historical prototype files remain
unchanged; current migrated JSON/help are the runtime contract.

Reproduce with -- --audit-button-counters. This runs 46 focused checks and writes
ignored .tools/plant-review-dual-count.rpproj.json and
.tools/plant-review-multi-press.rpproj.json. Each seven-rung reference has two
CTUs, two priority resets, comparison output and two count MOVs. These remain
explicit QA projects, never auto-loaded solutions; the catalog still has five
authored demos and an empty default exercise editor.

Native Windows: File -> Open Ladder Agent Project -> Return to Scene -> Run.
Scene 46 sidebar presses counted A=1,2 and B=1,2,3; A=2/B=3 gave green. Full-scene
FR/FL/RL/RR/Top inspected with six separated feet and no stand intersections.
Close front A display view showed readable A=2/B=3. A=3/B=4 remained green;
Stop cleared both displayed output counts to zero at scan 6206, Run republished
3/4 without new presses. A=4 removed green. Sidebar RESET cleared both; a new
B press showed one and the physical 3D RESET button cleared it. Application
Reset returned stopped scan zero. Native dual-count-final log exited zero.

Scene 47 used physical 3D A twice and B three times, giving A=2/B=3 and green.
Full FR/FL/RL/RR/Top inspected with all six feet clear. Close front count view
showed readable 2/3; nearby B housing is cropped by the right pane in this
focused view, while its digits remain readable and full-scene views show its
complete footprint. Stop at scan 6221 cleared both readouts/green; Run restored
2/3. Extra B gave 2/4 and removed confirmation. Physical 3D RESET cleared both;
new A showed one, and application Reset cleared it and stopped at scan zero.
Native multi-press-final log exited zero. Rear views hide front-facing digits;
overhead establishes spacing rather than readout readability. No motion model
is needed for these operator counter panels.

Build zero warnings/errors; 46 focused workflow checks, 613/613 geometry/workflow
with overlay (605 without), 144/144 controller conformance, rendered scene
controls/overlay/external typed-image PASS, shell 77 scenes/294 assets/five demos
PASS, authored contracts 71/71 and help 77/294 PASS. Logs: .tools/button-counter-*
plus dual-count-final-native and multi-press-final-native. Tests use offline
transport only. Whole-program goal remains active; next Scene 48 parking entry
still has substituted static props and no demonstrated occupancy/barrier route.

Scene 44 repeat-cycle repair (2026-10-06, previous checkpoint):
replaced the manual PC count-complete toggle with machine enable plus actual
home/busy/cycle_done/head-position feedback. A scoped CNC dry-stroke model owns
the complete connected Z head and spindle on accepted plant ticks. PLC ladder
owns the batch latch, CTU and displayed count. The default editor remains empty.
Ignored .tools/plant-review-repeat-cycle.rpproj.json is an explicitly opened,
five-rung QA reference, not a sixth demo. Its three-cycle preset, 100 mm feed,
1 s feed, 0.5 s dwell and 1 s return are documented training choices; the
prototype supplies no corresponding OEM specification. Old projects must replace
removed cycle_count_complete and bind the new typed contract.

Moving-route checks exposed motor/roof, spindle/door/bearing and coolant/truck
conflicts. Raised the scoped enclosure roof/panels by 100 mm, deepened its front
bay by 350 mm, moved the complete closed-door/track/header assembly, removed an
internal decorative solid backdrop, rerouted coolant beside the guide trucks
and installed a stock-bearing shoe. Shared delivery assets are unchanged.
Controls/readouts sit in a separate front row; the selector plate says ENABLE.

Native Windows: normal File -> Open Ladder Agent Project -> Return to Scene ->
Run, Enable, Start Batch. Held scan 25 showed half feed/head 50%/count 0; Stop
kept pose/scan and disabled Step; Run resumed. Inspected focused FR/FL/RL/RR/Top
at scan 25 half feed, scan 50 work endpoint and scan 100 half return. Actual return
at 125 produced Done True/count 0; scan 126 acknowledged and counted one. Second
return at 251 counted two at 252; scan 402 showed home/count three/batch complete.
Completion full-scene FR/FL/RL/RR/Top inspected. Top initially hid the roof edge
under the overlay; two wheel detents exposed all six footprints. Rear-left still
occludes near stands; front views and overhead supply their placement evidence.
Closed rear/roof panels obscure internal motion and glazing limits detail.
Focused COUNT readout showed 3 and green completion; ordinary continuous playback
also completed three and retained idle. Stop clears display/output image to zero
while retaining CTU memory; one resumed scan republishes three without motion.
Application Reset restored disabled home, stopped scan zero and count zero.
Native .tools/repeat-cycle-final-native.log exited zero.

Native Hold exposed a stale QA count label immediately after Stop: snapshot
publication preceded output projection, with no later callback while held.
Refresh now follows snapshot output projection. Rebuilt native File/Open workflow
repeated the batch at held scan 400: Stop immediately showed count 0 at scan 400,
home unchanged and completion lamp off. Native overlay-final log exited zero.

Final build zero warnings/errors; 23 focused checks pass, including 618 executed
route samples, missing Enable, permissive loss/fresh Start, held high command,
actual completion edge/CTU agreement, Stop/Run, Reset and clock ownership.
Geometry/workflow 567/567 with overlay, controller 144/144, rendered scene
controls/overlay/external typed image PASS, shell 77 scenes/294 assets/five demos
PASS, authored contracts 71/71, help 77/294 PASS, prior unchanged plant-motion
85/85 PASS. Logs: .tools/repeat-cycle-final-*, committed-geometry, rendered-controls,
motion and contracts. Offline prescribed motion/bounds evidence only; no live PLC,
material removal, dynamics or commissioning acceptance. Whole-program goal remains
active. Next matrix gaps include Scenes 46/47 counter lessons and Scene 48 barrier.

Scene 44 repeat-cycle baseline (2026-10-06, historical; superseded above): normal
native Windows operator shell opened the unchanged lab-4-03-repeat-cycle-counter.
Both sidebar actions latch PC cycle_request/cycle_count_complete true while Stopped;
PLC cycle_active/cycle_complete remain false. Normal Run opens the intentionally
empty editor with NO CONTROLLER LOADED. Returned to Scene and inspected FR/FL/RL/RR/Top.
The CNC is a static generic prop: the scene has only switch/indicator bindings, no
machine command, motion, completion sensor, plant model or counter. The two manual
switches inherit generic START plates. Front-left hides the near request station
behind the CNC panel; rear-left hides the near completion beacon behind the enclosure.
Top shows separate footprints; this baseline does not establish any running cycle.
Native exited 0; .tools/repeat-cycle-counter-baseline-native.log. No Scene 44 source
changes made. The original prototype has the same incomplete four-point contract;
it does not supply a count preset, machine cycle or motion timing. Preserve the
empty training editor and distinguish a chosen, documented offline reference from
a source-derived machine specification. Repair the completion feedback/command
path and exercise the bounded count with an explicit QA controller, including
Stop/Run, Reset, held inputs, missing permissives and actual native moving poses.
The whole-program goal remains active; last repair commit is 222211f.

Scene 43 counter/reset repair and catalog preflight (2026-10-06, current checkpoint):
replaced the PC-computed count_reached toggle with raw pulse_received; reset_pressed
is now a one-scan momentary action. Corrected physical plates COUNT/RESET and
reset button color. PLC CTU/RES owns the counter and lamp; the default editor
remains empty. The verifier writes ignored .tools/plant-review-counter-reset.rpproj.json
(preset three, matching Demo 1); no sixth demo or automatic solution is added.
Older controller projects must replace the removed count_reached input.

Found and repaired an unscanned local action surviving Stop: pending scene pulse
points are cleared on local shell and standalone Stop, so Run cannot replay an
old COUNT/RESET. Held inputs are retained. External playback bypasses this cleanup.
Eleven controller/action regressions cover three distinct presses, idle retention,
reset/recount, coincident count/reset priority, Stop/Run retention, discarding both
pending pulses and application Reset. These timing cases are deterministic evidence.

Final native Windows operator workflow: normal File -> Open Ladder Agent Project,
Return to Scene and Run. First/second COUNT kept the lamp off (scans 1101/1614);
physical third COUNT lit the green tier at 2406, with pulse_received already false.
Wide FR 3273, FL 3638, RL 3970, RR 4353 and Top 4754 inspected while lamp remained
on during idle scans. All three stands are grounded and separate. Rear angles hide
faceplates; close FR crops the outer reset foot, so wide angles supplied full feet.
Physical RESET at 5873 cleared lamp/input while Running; fresh one/two/three presses
re-established completion. Stop at 7459 cleared lamp; Run at 7499 restored retained
completion. Application Reset restored stopped scan 0 and all three points false.
Exact accumulated values were verified deterministically, not read in native watch.
Native exited 0; .tools/counter-reset-final-native.log records this workflow.

Catalog preflight exposed two stale assumptions and one actual layout defect.
Photoeye validation now matches the compositor's finite height minimum 0.3 m;
the chain lift's 3.2 m receiving sensor must not fail an arbitrary 2.5 m ceiling.
Inclined photoeyes are checked at the product's cross-belt path using both lens
heights and stand locations. Rotated/scaled roots fail this bounded authored-envelope
check rather than receiving an unsupported claim. Six Python regressions cover
actual upper/inclined installations, invalid elevations and missed product/belt.
Existing native/world-space chain-lift and carton audits remain the geometric basis.

Scene 68 (not 66), sum-and-counter: moved indicator_5 from (3.3,0,-1.2) to
(5.5,0,0), beside its peer rather than behind it. Two authored coordinates changed;
I/O/reference behavior is retained. Native FR/FL/RL/RR/Top inspected all nine props;
front readouts are small but separate, rear cables/feet clear. Default Top cropped
the outer control under the toolbar; four mouse-wheel zoom-out detents exposed all
nine footprints. Camera auto-fit at Top remains a separate usability gap. Native
exited 0; .tools/sum-counter-indicator-{baseline,final}-native.log. Existing eleven
sum/counter integration/clearance checks also pass against this final placement.

Verification: final build 0 warnings/errors; geometry/workflow 544/544 with inspection
overlay (539/539 without); controller 144/144; plant motion 85/85 including 2,576
Demo 5 route samples; rendered controls/overlay/external-image PASS; shell 77 scenes,
294 assets/five demos PASS; authored contracts 71/71; help 77/294 PASS; six new Python
tests PASS; diff whitespace PASS. Logs use .tools/counter-reset-final-*, with final
layout geometry in .tools/counter-reset-final-layout-geometry.log. These are bounded
offline/runtime checks, not physical PLC transport or commissioning evidence.
Goal remains active. Next unresolved lesson is Scene 44 repeat-cycle counter;
review its precomputed completion/manual input and actual native operator workflow.

Scene 43 counter/reset baseline (2026-10-06, historical; superseded above):
normal native Windows operator shell (`--shell-scene=lab-4-02-counter-reset-lamp`,
not standalone `--scene-id`) confirmed the precomputed `count_reached` toggle
and persistent `reset_pressed` toggle. Both actions latched true while stopped;
`counter_lamp` stayed false. Normal Run opened the empty ladder editor with
NO CONTROLLER LOADED. Both rendered button plates say START instead of identifying
count/reset. No counting workflow is currently established. Window exited code 0;
log `.tools/counter-reset-baseline-shell-native.log`. The accidentally selected
standalone preview was closed without running it and is not operator evidence.

Next scoped repair: replace the precomputed result input with raw count pulses,
make reset momentary, correct button labels and training/help point ownership,
then exercise a real CTU/reset controller through actions, accepted scans and
output projection, including coincident count/reset, Stop/Run and Reset. Keep
the default lab editor empty; an explicit ignored QA project can demonstrate
operation without inventing a sixth authored demo or automatically solving the
exercise. Derive the reference preset from Demo 1's three-pulse example and
label it as the reference value. Inspect final native rendering/workflow before
calling the repair complete. No Scene 43 source changes made yet.

Scene 74 held transfer inspection (2026-10-06, current checkpoint): added
scoped offline Hold, Step 0.1 s (five existing 20 ms scans) and Step 20 ms
(one actual scan), with time/stroke/count readout. The controller/plant path
remains single-clock; held native callbacks cannot advance a second time.
Stop disables both steps. Reset preserves the hold and restores initial state;
release restores original process modes. Other existing clock increments
remain unchanged. Eight clock regressions pass; full plant motion is now 85/85,
including the existing Demo 5 routes and 2,576 executed route samples. Build
has zero warnings/errors. Shell PASS (77 scenes / 294 assets / five demos),
rendered controls/overlay PASS and help validation 77/294 PASS. Logs:
`.tools/carton-clock-{shell,rendered-controls}.log`. No scene geometry, shared delivery assets or DB14
contract changed in this checkpoint.

Native 1602x932 final code: normal File -> Open Ladder Agent Project loaded
`.tools/plant-review-scene2.rpproj.json`; Return to Scene, Hold and normal Run.
Ten coarse presses advanced exactly 50 scans / 1.00 s. Fine presses held
scan 58 / 1.16 s / 53.3% extension; 63 / 1.26 s / 86.7% actual release /
count 1; 65 / 1.30 s / full extension; 72 / 1.44 s / 53.3% retraction.
Each of these four poses was individually inspected in FR/FL/RL/RR/Top close
full-scene views. Plate contact and connected yoke remain visible on extension;
carton stays supported on the table at transfer/full extension and stays put
while the plate retracts. Rear views hide the low sensor; close views crop
outer equipment ends/feet. These observations cover the central transfer,
not every frame or a complete collision sweep.

At scan 62 the rounded label reads 80.0% with count 0; the unchanged canonical
strict floating-point threshold crosses on scan 63. Stop at 72 cleared both
commands and held pose; clicks on both disabled step buttons kept scan 72.
Run while held stayed at 72; eight fine scans returned home at 80 / 1.60 s
with the carton still on the table (RR/Top). It remained there through scan
180 / 3.60 s and recycled to infeed at scan 188 / 3.76 s, the canonical
next-load boundary. Reset restored staged carton, empty receiver, commands
false, count 0 and stopped scan 0. Release plus normal Run restored real-time
scan 38 / 0.76 s with visible infeed motion. Native exited normally, code 0.
Evidence: `.tools/carton-review-clock-native.log` and
`.tools/carton-review-clock-motion.log`; screenshots inspected through the
Windows Computer Use skill, without saving duplicate captures.

The generated three-rung file remains ignored QA evidence, not a shipped
solution. Arbitrary command sequences, physical force/pressure/gravity and
commissioning remain unverified. The whole-program goal stays active; continue
with other recorded gaps, starting with Scene 43's precomputed counter/reset
feedback and actual operator workflow. The preceding continuous-playback gap
for intermediate native poses is resolved by this bounded held-pose pass.

Scene 74 native continuous playback checkpoint (2026-10-06): normal
File -> Open Ladder Agent Project loaded the generated offline reference
`.tools/plant-review-scene2.rpproj.json` (three rungs with limit-triggered
retraction, not the older held-solenoid endpoint fixture). Return to Scene and
normal Run drove repeated transfers. Native 1602x932 snapshots inspected FR
scan 38 (infeed), FL 578 (infeed), RL 2055 (received), RR 2549 (received),
Top 3466 (received) and FR 6150 (received). Received carton visibly bears on
the table and stays visible after plate return. Stop at 6557 removed both
commands and retained carton; FL reinspection held the same scan/received pose.
Reset restored staged infeed, empty receiver, commands false and stopped scan 0.
Owned native window exited code 0. Evidence: .tools/carton-transfer-continuous-native.log.

This is snapshot coverage during ordinary repeated playback, not every-frame
or phase-by-phase full-stroke acceptance. Fast extension/retraction phases
need closer native review; arbitrary command sequences and physical transfer
remain open. The generated review file is ignored QA evidence, not a shipped
authored solution. Default exercises remain empty. Next step: expose a scoped
single-clock native Hold/small-step inspector for Scene 74, validate its exact
scan increment and Stop/Reset behavior, then inspect intermediate stroke and
80-percent release poses from multiple views. Other whole-program gaps remain;
do not mark the goal complete after these two scenes.

Demo 5 supported four-carton repair (2026-10-06, current checkpoint):
replaced the autonomous illustrative sweep with one fixed kinematic plant driven
by the normal 20 ms ladder clock. A receiving/pick table joins the narrower
conveyor at Y=1.055 within gantry reach. Cartons attach at pickup, travel with
the tool, release onto four pallet slots and remain visible. Home, pickup,
placement, attachment, completion, progress and inventory come from plant state;
manual home/carton toggles are removed. START / LOAD / PALLET labels match actions.
Four actual placement/home returns drive CTU and layer completion. Demo-menu
and saved Demo 5 documents match; two FBs, two FCs, two declaration DBs, TON,
CTU, comparison, edge and math coverage remain. DB14/shared delivery assets unchanged.

Completion is retained across Load until the next accepted cycle. Regressions
exercise operator Load with and without fresh Start in the exact one-scan gap
before CTU sees home-return feedback. Stop discards unscanned Start, freezes
pose/inventory and clears commands; Run alone holds, fresh Start resumes.
Rejected Load now shows home/empty-station/layer requirements in native status
and event history instead of failing silently.

Final deterministic evidence: build 0 warnings/errors; controller 144/144;
focused palletizer 58/58 including review clock; 2,576 actual 20 ms route samples;
0 coarse static bounds candidates; general geometry/workflow 528/528; plant
motion 77/77; shell 77 scenes / 294 assets / 5 demos PASS; help 77/294 valid.
Moving bridge/carriage/rod/tool are checked against posts, other equipment and
visible placed stock; carton bounds against fixed solids, pallet bearing,
tool contact and telescopic-rod/carriage bearing are sampled through four routes.
These are selected sampled bounds and prescribed kinematics, not full swept
volume, collision response, force, vacuum-pressure, gravity/drop, automatic
conveyor feeding, physical PLC, commissioning or safety acceptance.

Native first pass (1602x932, .tools/palletizer-native.log): normal Run/Start and
three Load/Start actions completed four cartons, home true, commands false and
layer_complete true. Inspected first release in all FR/FL/RL/RR/Top views,
attached second carton in FL/FR, and retained four-carton layer in all five views.
Stop during attached transfer cleared commands; Run plus 25 scans held pose;
fresh Start resumed and release retained both cartons. Reset restored one pickup
carton, empty pallet and stopped scan 0. Rear-left robot partially occludes the
gantry; other views resolve contact/clearance. Overhead bridge partly hides one
carton in some phases. Native screenshots were individually inspected; no
claim of every-frame multi-angle capture. This pass preceded completion-latch
and blocked-Load status fixes; final code was separately retested below.

Final native code pass (.tools/palletizer-native-final.log): Run alone held;
Start plus three Load/Start actions completed four actual transfers. Home/placed
snapshots: 1 at scan 1745/34.90 s, 2 at 4295/85.90 s, 3 at 7040/140.80 s,
4 at 9642/192.84 s. Layer completion true observed at 10099/201.98 s.
Final layer inspected Top 9642, FR 10443, FL 10894, RL 11285, RR 11757;
RL robot partially occludes contact. Duplicate and fifth Load displayed the
rejection reason without changing stock. Reset restored home/preloaded carton,
empty pallet, all outputs false and stopped scan 0. Native exited code 0.

The whole-program goal remains active. Next recorded gap is Scene 74 continuous
native stroke review; other catalog process/model/controller gaps remain.
Older Demo 5 baseline below records superseded behavior and historical evidence.

Demo 5 normal realtime baseline (2026-10-06, superseded pre-repair checkpoint):
launched the native Windows operator application at 1602x932 with review cameras
but Hold OFF. Enabled the three existing manual permissives, then normal Run
loaded the authored Demo 5 program. Running snapshots were inspected in FR
(scan 43 / 0.86 s / 58.7% stroke), FL (823 / 16.46 s / 99.5%), RL
(1771 / 35.42 s / 34.6%), RR (2226 / 44.52 s / 25.0%) and Top
(2730 / 54.60 s / 31.3%). The pallet is inside the support posts; the orange
tool follows the gantry axes. Rear-left robot occludes the gantry/carton;
front/rear-right and overhead resolve those areas. These are snapshots during
continuous playback, not an every-frame recording or complete swept-volume
acceptance.

The deeper functional finding remains open: the carton stays on the conveyor,
the pallet stays empty and gantry_home remains manually true while the tool
is away. The cycle is an illustrative XYZ sweep; its timer/counter does not
observe an actual completed placement. This is stated in the current scene
help and does not become a physical palletizer by passing ladder tests.
Clearing carton input removed both commands. Three further separate carton
presentations, each held past 750 ms, reached layer_complete. At scan 5630 /
112.60 s both actuator commands were off; the I/O pane confirmed retained
layer_complete True at scan 7229 / 144.58 s. Reset cleared outputs and manual
inputs, restored the pose and stopped at scan 0. Native console exited normally
with code 0. Log: `.tools/demo5-continuous-native.log` (ignored local evidence).

Next unresolved Demo 5 work: a supported carton route within the gantry's
reachable envelope, attached pickup/carry/release poses, observed home and
placement feedback, and a reference whose counter advances from that feedback.
Preserve the integrated FB/FC/timer/counter lesson and PC/PLC ownership.
Do not count the current timed manual-input cycle as a pallet-placement pass.
The whole-program goal remains active; other catalog runtime gaps also remain.

Scene 53 cable-cut repair (2026-10-06, completed repair checkpoint): replaced the
payoff shutter, dancer/cutter trays and unrelated machine with a connected
scene-local reel, passive guide/encoder/feed rolls, slotted-anvil cutter and
grounded receiving table. There are 11 equipment items and 15 symbolic points.
The delivered length display opts into F2 measured feedback. Manual feedback
switches become one Start. One finite clock feeds 3 m at prescribed 0.3 m/s,
cuts, returns the knife home and retains the piece. Available stock finishes
at 7 m from 10 m, excluding the 5.5 m already threaded upstream route. Reel
motion uses a constant 0.35 m effective pitch radius. PC owns feedback; PLC
owns commands/authorization. The saved six-rung 20 ms Cable_Measured_Cut_Cycle
opens through File -> Open Ladder Agent Project. Default empty ladder stays
an exercise. DB14 and shared delivered geometry are unchanged. No tension,
slip, sag, layering, elasticity, cutting force or collision physics is modeled.

Focused audit: 31/31 pass, 581 executed 20 ms cycle samples, zero coarse static
bounds candidates. Corrected the counter to exclude its final loop-condition
evaluation. Checks cover piece dimensions/support, selected knife clearance,
measured inventory, F2 readout, reel/encoder/blade projections, interlocks,
retained completion, Stop/Run/fresh Start during feed/downstroke/return, Reset,
invalid cut commands, clock partitioning and held native steps. Intentional
knife/cable cutting, rod/actuator interfaces and the narrow slot are excluded
from selected clearance screens. These are sampled bounds and prescribed
kinematics, not solid-contact, swept-volume or physical process acceptance.

Native Windows at 1602x932 loaded the saved reference through its File dialog.
Initial, 0.60 m feed at held 2.5 s, partial blade at 11 s / 0.63 stroke and
completed 3 m / home at 13.5 s were inspected in FR/FL/RL/RR/Top. Wide overhead
resolves close-view cropping. FR receiving end is behind right HUD; FL reel
behind left HUD; RL reel behind right HUD. Alternate views resolve these.
Focused cutter Top/RR were also inspected at completion; header/blade obscure
the small cutting-plane gap, whose 60 mm position is numerically checked.
Rear labels are reversed; display backs are plain housing. Run plus 25 scans
held initial state. Stop at 11 s cleared commands and held 0.63 stroke; Run
plus 25 scans held it; fresh Start resumed. At 12 s return was stopped at
0.75 stroke; Run plus scans held it; fresh Start completed return. Completed
Start plus scans could not repeat the cut. Reset restored empty receiver,
zero length, home blade and stopped scan 0. Normal realtime FL focused playback
showed 0.24 m at scan 399 / 7.98 s and retained 3.00 m / home / commands off
at scan 1205 / 24.10 s (Start around 7.2 s). I/O confirmed 3 m measured, 7 m
remaining and no fault at scan 2053. The brief realtime knife stroke was not
captured frame by frame. Native console exited normally with code 0.

Build: zero warnings/errors. Controller tests: 144 pass, 0 fail. Shared
geometry: 487 checks; motion: 32 checks. Shell (77 scenes), help, Scene 53
initial contract and shared numeric workflow pass. Scene 52 regression: 29/29.
Whole-program goal remains active: Demo 5 continuous motion and other
runtime/installation gaps remain open.

Scene 52 barrel-fill repair (2026-10-06, previous checkpoint): replaced the
motor-starter barrel and disconnected dosing/filler props with an open-top
barrel, elevated 200 L cutaway source, connected valve/meter/nozzle and grounded
supports. The scene has 11 equipment items and 15 symbolic points. One finite
plant clock indexes the barrel, transfers 150 L at a prescribed 20 L/s, then
parks the filled barrel on the conveyor. Source plus barrel remains 200 L.
PC owns observed volumes/positions; PLC owns commands and authorization.
The editable seven-rung 20 ms Barrel_Metered_Fill_Cycle reference opens through
File -> Open Ladder Agent Project. Default empty ladder stays an exercise.
Shared deliveries and DB14 remain unchanged. Mechanical indexing and constant
flow are assumptions; hydraulics, slosh, slip, replenishment and collision
physics are excluded.

Final focused audit: 29/29 pass, 1,344 actual-controller 20 ms samples.
Checks cover support/visible bounds, actual optical rays/rendered beams,
rendered liquid volumes and stream endpoint, mating pipe end rings, finite
inventory, completed restart rejection, Stop/Run/fresh Start during infeed,
fill, discharge and occupied outfeed, Reset, invalid fill diagnostics,
external pause and held native steps. One coarse cable/post bounds candidate
remains; actual cable triangle bounds clear the axis-aligned valve/portal
parts. These screens are not solid-contact or swept-volume acceptance.

Native Windows at 1602x932 loaded the reference through the normal File route.
The first repaired build's initial and 53.2 L filling states were inspected
in FR/FL/RL/RR/Top. This revealed floating-point text spilling off the meter.
Added optional numericDisplay formats G/F0/F1/F2/F3; this scene uses F1.
The final build showed readable 53.2 L in FL at held 14 s. Stop closed the
valve/stream and retained volume; Run plus 100 scans held it; fresh Start
continued to 93.2 L at 18 s. At 22 s, 150 L discharged with 50 L remaining.
At 30 s, Stop/Run/100 scans held the occupied outfeed; fresh Start parked it
at 34 s with both outputs off. Completion was inspected in FR/FL/RL/RR/Top,
plus wide Top to resolve cropping. Rear-left source occludes the parked barrel;
rear-right/front views resolve it. Back sides of 3D labels appear reversed.
Completed Start plus scans held the batch. Reset restored an empty barrel,
200 L source and stopped scan 0. A normal realtime run showed initial FL,
filled discharge FL at scan 1379 / 27.58 s and retained completion FL at scan
2082 / 41.64 s (Start around 8 s). Intermediate realtime frames were not all
inspected. Native console session exited normally with code 0.

Final build has zero warnings/errors. Controller tests: 144 pass, 0 fail.
Shared geometry: 487 checks; shared motion: 32 checks. Shell (77 scenes),
help and Scene 52 contract pass. After the display edit, the focused 29-check
audit, shared numeric workflow and Scene 51's 24-check regression pass.
At the Scene 52 checkpoint, Scene 53 cable-cut substitutions and Demo 5
continuous motion remained open; the newer Scene 53 checkpoint above supersedes
that cable-cut finding.

Scene 51 cookie-packaging repair (2026-10-05, previous checkpoint): replaced
an overlapping CNC, floor-level packaged-meat prop and pneumatic-pusher counter
with scene-local cookie trays, a grounded ring-jaw sealer and numeric displays.
There are 14 equipment items, 13 symbolic points and one momentary Start.
Six trays stay supported on the 9 m conveyor. A single prescribed plant clock
indexes each cookie, observes its actual beam crossing, lowers/holds/raises
the jaws, reveals its package and retains all six at the outfeed. PC owns
observed counts/positions; PLC owns commands/authorization. The saved six-rung
20 ms Cookie_Packaging_Batch reference opens through File -> Open Ladder Agent
Project. Default empty ladder remains an exercise. Shared deliveries and DB14
are unchanged. Mechanical indexing is assumed; heat, film mechanics, slip,
replenishment and collision dynamics are excluded.

Final focused audit: 24/24 pass with 1,252 actual-controller 20 ms cycle samples.
Checks cover support/visible load bounds, actual beam/rendered visibility,
exactly six counts/seals, retained completion, Stop/Run/fresh Start during feed
and partial head travel, Reset, empty sealing, conflict diagnostics, external
pause and held native steps. Three coarse static bounds candidates remain;
curved-cable triangle bounds clear the axis-aligned sealer parts. These are
sampled bounds and prescribed kinematics, not solid-contact, swept-volume or
physical process acceptance.

Final native Windows application at 1602x932 loaded the reference through its
File menu. Initial, jaws-down, first sealed and completed states were inspected
in FR/FL/RL/RR/Top views. Top obscures food/head beneath the portal header;
close views can crop belt ends/control bases. Front/rear views resolve those
occlusions. Stop at held 6 s cleared commands; Run plus scans held the pose;
fresh Start resumed. Reset restored six unwrapped trays, zero counts and
stopped scans. With hold released, a normal real-time run showed initial travel
in FL, count 3/sealed 2 in FL, count 5/sealed 5 in RR and completion at scan
1916 / 38.32 s in RR (Start around 10.94 s). Another Start left package poses
and counts held through scan 2809 / 56.18 s. These are inspected snapshots,
not every-frame five-angle coverage. Owned native console session exited 0.

Final build: zero warnings/errors. Controller tests: 144 pass, 0 fail. Shared
motion: 32 checks; catalog geometry: 487 checks. Shell (77 scenes), help,
Scene 51 contract, virtual-controller UI and Scene 50's 36-check regression
pass. Whole-program goal stays active. Next open installation is Scene 52
barrel transfer; Demo 5 and other documented continuous-motion/runtime gaps
remain open.

Scene 50 carton-cycle repair (2026-10-05, previous checkpoint): the carton now
loads from the chain infeed, crosses a supported lower bridge, rises on the
powered carrying deck, crosses the upper bridge to the receiving belt, stops
at its plate, and remains there while the empty carriage returns HOME. The
scene has 16 equipment items, 16 symbolic points and one momentary Start.
The opt-in single-carton plant owns position feedback, with separate upper
entry-beam and occupied-zone feedback; PLC commands retain PLC ownership.
One clock projects load, carriage, chains and belt travel. Shared deliveries
and DB14 remain unchanged. The retained saved reference filename now contains
Chain_Lift_Carton_Cycle, a seven-rung 20 ms editable offline sequence. Default
generated ladder remains an exercise; use File -> Open Ladder Agent Project.

A strengthened audit selected the actual CARTON_BODY by mesh volume instead
of import order (which selected a barcode), and exposed a real shaft conflict.
Moved the upper shaft/sprockets/gearbox to Y=3.95, above the carton's upper
body envelope, and derived chain-loop length from that shared center height.
Recessed the supporting deck below its belt to remove coplanar face flicker.
Seated the receiver's raised splice witness flush. Rotating curved meshes use
transformed surface-vertex bounds before the oriented-box screen, preventing
rotating bounding cubes from falsely growing into a resting carton.

Final focused audit: 36/36 pass, 2,897 cycle samples at 10 ms; all four route
legs, bearing-contact envelopes, carton visibility/selected obstacle clearance,
actual optical centerlines/rendered beams, endpoint feedback, completion,
occupied-receiver restart rejection, Stop/Run/fresh Start in every leg, exact
chain/drum Reset, conflicting-command diagnostics and held-clock QA checks.
Carriage screen covers 211 heights, excluding intended guide/chain/limit
interfaces. Bounds screens are not swept-volume, solid-contact, load-rating,
falling-load, slip, flexible-chain or full self-collision acceptance.

Final native Windows build opened the saved reference through the normal File
route and was visually inspected at 1602x932. Held actual 20 ms controller
steps produced lower-bridge crossing (6 s), mid-rise (10 s, 43.5%), upper
shaft approach (20 s), upper-bridge crossing (22 s), and empty return (30 s,
73.5%) in FR/FL/RL/RR/Top views. Stop at 43.5% cleared commands; Run plus
2 s of scans held that pose; fresh Start resumed. The upper entry beam hid
while crossed and returned after the carton passed, while receiver CLEAR
stayed false. At 34 s the empty lift reached HOME with the carton retained;
Reset restored the infeed carton and stopped scans. Some close Top views
crop the stop/carton behind QA controls; front/rear-right views show them.
These are inspected controller-driven snapshots, not every-frame five-angle
native coverage. After Reset, released the hold and ran a normal real-time
cycle: initial travel and the completed HOME/retained-carton endpoint were
observed in RR, at scan 2261 / simulated 45.22 s (Start around 10.28 s).
Intermediate real-time frames were not individually inspected. The owned
native process closed normally and its console session exited 0.

Final build: zero warnings/errors. Controller tests: 144 pass, 0 fail; native
controller UI regression passes without PLC transport. Geometry: 487 pass;
shared plant-motion/QA scope: 32 pass; shell: 77 scenes/3 groups/5 demos/294
assets; scene contract: 16 points/1 action/16 rendered/0 deferred; help passes.
Logs: rungproof-next/.tools/chain-lift-cycle-{build,audit,controller-tests,
controller,geometry,motion-regression,shell,contract,help,clearance-native}.log.

Whole-program goal ACTIVE and incomplete. Continue the remaining findings,
including Scene 51's incorrect cookie/CNC belt installation and load placement;
Demo 5 and Scene 74 continuous native multi-angle acceptance also remain open.
No live PLC connection or hardware acceptance is claimed.

Scene 50 installation repair (2026-10-05, previous checkpoint): replaced the
overlapping conveyor/scissor-table installation and incorrect mill/scissor/
E-stop accessories with a scene-local guided chain lift, separate chain
infeed, two transfer bridges, frame-mounted endpoint switches, an upper
receiving belt and floor-mounted end stop. The staged carton bears on the
yellow deck; two crossmembers connect the deck to the moving side beams.
Shared catalog deliveries and DB14 remain unchanged. The scene now declares
14 equipment items, 6 symbolic points and 4 actions. Chain/lift PLC commands
reach actual drive adapters, with the carton following actual carriage height.
Chain links/sprockets follow that position; the infeed animates its upper run.

The editable chain-lift-installation-reference.rpproj.json is an installation
test using three explicitly manual permissives and a momentary Start. Normal
20 ms offline scans reject missing permissives and stale Start, drive the
supported load on fresh Start, hold on Stop, require fresh Start after Run,
clear the seal on destination loss, and restore initial state on global Reset.
It is not the final continuous carton-transfer program.

Native Windows home and upper endpoint snapshots were inspected FR/FL/RL/RR/
Top, with the source example opened through File -> Open Ladder Agent Project.
Normal operator checks exercised rejected Start, fresh Start, upper Stop,
Run/fresh-Start behavior, destination loss/recovery and Reset. A partial raised
snapshot was seen; mid-stroke Stop was verified in the focused headless audit.
Final deck crossmember correction was rechecked in native focused FR/RL home
and raised views. These are inspected snapshots, not every-frame native stroke
acceptance. Some rear views occlude the upper receiving surface. PLC remained
disconnected; both own repaired/final native QA processes exited 0.

All 28 --audit-chain-lift-installation checks pass, including deck bearing,
fixed switch bracket/endpoint roller contact, carton support and selected
obstacle clearance at 211 height samples (10 mm), actual controller sequencing,
drive Stop/Reset and restoring every feed sprocket without another command.
Guides, chain links and intended limit contacts are excluded from the sampled
clearance check; this is not continuous swept-volume or self-collision proof.
Static candidate count fell from 145 to 3 intended switch/post interfaces.
Final build has zero warnings/errors. Controller regression: 144 pass;
geometry regression: 487 pass; shell: 77 scenes/294 assets; Scene 50 contract:
6 points/4 actions/14 rendered/0 deferred. Help validation passes. Broad
regressions preceded the final crossmember and feed-sprocket Reset corrections;
final build/focused audit cover them, and final native inspection covers deck
support geometry. Logs: rungproof-next/.tools/chain-lift-{build,audit,controller,
geometry,shell,contract,repaired-native,final-native}.log.

OPEN: carton starts on the lift; horizontal loading/discharge, automatic
position/load feedback, receiving-belt motion and lowering/return are not yet
implemented. Manual HOME can remain asserted while raised. Infeed animation
is an upper-run visual model, not flexible-chain physics. Next implement a
supported continuous carton route and real simulator feedback, then inspect
full native motion from all five angles and continue the remaining catalog.
Goal active; whole-program review remains incomplete.

Sequence tower repair (2026-10-05, previous): Scene 45 now installs four
separate red/amber/green/blue tiers and a separate completion beacon. The
scene-local assembly extends the delivered three-tier model by its 235 mm
pitch and raises the cap/sounder. Independent indicatorChannel bindings show
each PLC BOOL, including conflicting simultaneous commands; existing exclusive
indicator behavior and shared catalog models are preserved. Legacy request
names/action IDs remain, but Start and Step are momentary pulses. Four new
symbolic PLC outputs supply the colors; DB14 is unchanged.

The editable sequence-light-tower-reference.rpproj.json implements red ->
amber -> green -> blue -> off on separate Step edges. Repeated Start while
active and Step before Start/after completion are discarded. Stop clears
active/completion/color commands; Run or Step cannot resume the old state.
Fresh Start resets the retained count. Global Reset clears points/count and
stops scans. Completion seals only after an active sequence finishes, so a
retained count cannot relight it after Stop.

Native Windows baseline reproduced the three-tier/two-green-binding conflict.
Repaired geometry was inspected FR/FL/RL/RR/Top; no unintended placement
intersection was seen. Rear views occlude some operator/completion details.
Final lamp brightness was reduced after close-up inspection revealed washed
out colors. Final FR close/full views distinguish all four energized tiers.
The final saved example was opened through File -> Open Ladder Agent Project
in the normal operator shell. Actual offline scans exercised the complete
color cycle, repeated Start, completion/extra Step, Stop after completion and
mid-cycle, Run/Step rejection, fresh Start and global Reset. PLC disconnected
throughout. Own native QA process closed and exited 0. These are inspected
snapshots and operator interactions, not an every-frame motion review.

All 30 --audit-sequence-tower checks pass: saved example equality, actual
20 ms symbolic controller scans, pulses/idle/Stop/Reset behavior, four lens
identities/pitch/cap clearance/floor position and independent-channel material
projection. Final build: zero warnings/errors. The existing regression run
passes 144 controller tests and 487 geometry checks; app shell has 77 scenes /
294 assets, Scene 45 contract has 8 points / 2 actions / 5 rendered / 0 deferred.
Help validation passes. Broad checks preceded the final lamp-brightness and
reference completion-seal corrections; final build/focused audit and native
operator checks cover those final changes. Logs: rungproof-next/.tools/
sequence-tower-{build,audit,controller,geometry,shell,contract,final-color-native}.log.

The CNC is explicitly static; the sounder is uncommanded. This is an offline
symbolic exercise, with no live PLC, wiring or physical acceptance claim.
Goal active; whole-program review remains incomplete. Next address the
Scene 50 lift-conveyor placement/receiving-surface failures and continue the
remaining catalog process and continuous-motion checks.

Scene 50 follow-up baseline (2026-10-05, open): the normal Windows
operator shell reproduced the same conveyor/lift overlap in FR/FL/RL/RR/Top
and FR close-up. The close/top views crop parts of the long installation;
rear views expose the separate floor carton. The nominal chain-hoist accessory
is a vertical knee milling machine (also identified in its local review file);
the limit-switch accessory renders another complete scissor table. The scene
contract binds chain_run and lift_enable only to indicator lamps, so it has no
commanded chain/lift/carton transfer. Baseline log confirms 145 enclosing-bound
candidates, including 131 conveyor/table candidates and a platform/platform
intersection. No Scene 50 repair or motion acceptance is claimed. Own baseline
window closed, process exit 0, PLC disconnected. Next replace the incorrect
scene-specific equipment identities, establish an aligned supported carton
route, and bind actual motion/feedback without silently enforcing PLC logic.
Log: rungproof-next/.tools/chain-lift-baseline-native.log.

Robot restart repair (2026-10-05, previous): Scene 41 now separates the
robot from the static CNC inside a four-sided welded-wire fence with an
outward-opening gate. The coded sensor stays on the latch post; its actuator
and bearing bracket move with the actual gate. A controller cabinet replaces
the unrelated pallet-fork prop. These installations are scene-local opt-ins.
The gate feedback, robot enable and momentary requests drive real scene adapters.
The legacy reset_complete name is retained, but its action is now a pulse.
The new motion_request pulse provides a separate Start; Reset authorizes the
cell without starting the robot. Existing DB14 and shared assets are unchanged.

Native Windows baseline reproduced the robot wrist inside the CNC enclosure
and the incorrect fence/cabinet identities. The first repaired gate endpoints
looked clear, but its intermediate swing hit the gate-feedback station. Moving
the operator stations to Z=5.2 clears that full swing; the actuator bracket was
widened to bear on the leaf frame. Static repaired installation and the final
running robot were inspected FR/FL/RL/RR/Top, with additional gate/interlock
details. These are inspected snapshots, not a continuous every-frame review.

The final saved, editable robot-cell-restart-reference.rpproj.json was opened
through File -> Open Ladder Agent Project in the normal Windows operator shell.
Actual offline scans rejected Start before Reset, lit Cell Ready without motion
on Reset, then enabled motion on separate Start. Gate/ready loss cleared both
outputs; restoration alone did not restart. Stop held pose; Run and Start alone
could not reuse authorization. Fresh Reset plus Start resumed motion; global
Reset restored home/open gate/false points/stopped scans. PLC stayed disconnected.

All 35 --audit-robot-restart checks pass: saved reference equality, actual
symbolic controller sequencing, actuator mounting, 800 robot samples at 10 ms
covering the complete base-axis cycle, and 91 gate angles through 90 degrees.
The contact screens exclude the intended hinges and interlock mounting contacts.
Build: zero warnings/errors. Controller: 144 tests. Existing geometry: 487
checks. Scene 41 contract: 6 points/4 actions/12 rendered/0 deferred. App shell:
77 scenes/294 assets. Help validation passes. Logs: rungproof-next/.tools/
robot-restart-{build,audit,controller,geometry,contract,shell,operator-final-native}.log.
The own native QA process closed and exited 0.

This is an offline symbolic reset/start exercise. The robot performs a generic
base-axis sweep, not CNC tending; the CNC remains static. The E-stop prop has no
declared action or circuit. No continuous swept-volume, robot self-collision,
physical safety function, wiring, mechanical rating or live acceptance is proven.
Goal active: continue the remaining catalog placement/process failures; the
whole-program review is not complete. Next inspect the remaining sequence and
transfer scenes, including Scene 45's four-color/three-tier beacon conflict.

Robot CNC transfer repair (2026-10-05, previous): Scene 38's reference now
uses the actual six robot joints and tool attachment for both transfers.
The 400 x 140 x 252 mm billet remains between the fingers while lifted,
carried through a staged front corridor, seated on the existing bearing shoe,
released, regripped and delivered to outfeed. A CNC-specific grip datum,
orientation, joint seed and park pose leave existing tote defaults unchanged.
Sliding door assemblies and the retracting nose/tool stack use explicit access
position. The robot parks before access closes and the machining timer starts.
The doors' rollers bear on an extended, supported top track throughout travel.
Vise bolts, the coolant nozzle/service hose and the rear backdrop were moved
clear of the stock/finger route. Changes are opt-in to the CNC tending scene.

The separate `--audit-robot-cnc` passes all 23 checks, exit 0: actual tool/load
attachment and two-finger contact, belt/vise footprint bearing, both aperture
crossings with open doors/retracted tool, closed access/tool down with ungripped
stopped robot during machining, door track bearing, completion and Stop/Reset/
restart rejection. It advances 22500 two-ms runtime/adapter ticks (45 s),
including 2250 twenty-ms load/robot-versus-other-equipment clearance samples.
The contact screens use bounds/OBB and cable triangle bounds with allowances;
they do not establish continuous swept volume, robot self-collision clearance,
mechanical ratings or physical interlock operation.

Native Windows: home, held grip, held loaded entry above the vise and completed
outfeed each inspected FR/FL/RL/RR/Top. Held infeed, opening, approach, lift,
front-corridor travel, lowering, release and withdrawal were also inspected.
Front views show supported released stock; rear enclosure walls and the roof
occlude some details. Held outfeed delivery was inspected FR/FL/Top. Stop held
the loaded outfeed approach and removed commands; restart was rejected until
Reset. A subsequent uninterrupted reference cycle completed; completed restart
was rejected and Reset restored home. These are inspected snapshots, not a
continuous recording or every-frame review. This joint adapter and explicit
access motions advance with held Step; autonomous spindle animation remains
frozen. Phase-boundary remainder is discarded, so step counts do not prove time.

Build clean; geometry 487 checks, controller 144 tests, Scene 38 contract,
app shell (77 scenes/294 assets) and help validation PASS. Logs under
`rungproof-next/.tools/robot-cnc-transfer-{build,audit,geometry,controller,
contract,shell,native-resumed}.log`. The own QA process exited 0 and closed.
The user had closed the earlier windows during the break; none was restored.
Goal active. Normal selected-controller operation, feedback-driven door/clamp/
process interlocks, material removal, full robot sweep and live proof remain
open. Next: continue the remaining catalog placement and process failures.

Robot CNC installation checkpoint (2026-10-05, previous): Scene 38 now carries
one 400 x 140 x 252 mm billet on the 0.9 m belt instead of transporting an entire
vise. The robot is on the front access side (Z=.6) of the grounded CNC
(Z=-2.6). Moving the enclosure back clears conveyor drives. The wider pickup
sensor stands clear of conveyor structure and its beam is at Y=.97. A bearing
shoe connects the existing vise base to the billet's machining bottom Y=1.66;
the delivered jaw-face span is filled. The stock target is X=0, Z=-1.985.
The opt-in composer moves the actual delivered stock mesh into the addressable
load root, leaving the vise fixed and removing the duplicate coupon.

The separate `--audit-robot-cnc` remains RED: 11/14 checks pass, exit 1 without
exception. Home installation, infeed/outfeed footprint support, station bearing,
timed completion and load Reset pass. Detached gripper contact, moving clearance
and closed-door transfer fail. It advances 4000 two-ms runtime/adapter ticks and
screens 800 load-clearance samples. Concrete pairs include door glazing/stiles,
vise jaws/bolts, bearing shoe and coolant nozzle. Bounds/contact screens are
diagnostics, not full swept-volume or mechanical acceptance.

Native Windows: repaired home and outfeed inspected FR/FL/RL/RR/Top; stock-focused
home Top/FR; held pickup FR/FL; machining FL and machine-focused FL/FR. The roof,
doors and robot occlude parts of the vise. Released remaining preview completed;
Reset restored the billet to infeed. No held unload, continuous-video/all-frame
robot sweep or normal selected-controller proof claimed. Held generic preview
Step advances only the sequence; autonomous robot/spindle adapters remain
frozen. Phase-boundary time remainder is also discarded. Do not treat held
screenshots as a complete robot motion test.

Build clean; geometry 487, controller 144, scene contract and app shell
(77 scenes/294 assets) PASS. Help validation PASS. Logs:
`rungproof-next/.tools/robot-cnc-{layout-audit,layout-build-final,layout-geometry,
layout-controller,layout-contract,layout-shell,native-layout}.log`.
Own QA exited 0 and closed; user's Conveyor Pusher window restored/preserved.
Goal active. Next: attach the billet to actual robot joints, open the enclosure
for transfer and route above the vise before seating. Door/robot/clamp
interlocks, feedback-driven process, controller flow and cutting remain open.

Dual Spindle installation repair (2026-10-05, previous): Scene 36 now uses
opt-in head, bed and slide installations. Both axes lie over one shared steel
plate; duplicate drill coupons/tables are removed. The fixture sits at Y=1.45
on a grounded four-leg bed covering its full 2.2 m transfer. Both spindles feed
330 mm, entering stock by 25 mm while retaining quill/bearing overlap; their
retracted tips clear the slide plate. The fixture follows actual carriage
position, maintaining contact and matching travel without a second clock.

The focused `--audit-dual-spindle` now passes 18 checks: shared stock, grounded
connected supports, separate-equipment clearance, 3000 two-ms support/feed/
feedback/contact ticks and 600 ten-ms moving-clearance samples, completion,
Stop/Reset and rejected active/completed/interrupted restart. Fixture and slide
travel both measure 2.2 m. Build clean; geometry 487, controller tests 144 and
scene contract PASS. The focused diagnostic remains separate from the broader
geometry suite. Bounds/contact screens do not establish mechanical ratings.
Final app-shell and help validation PASS (77 scenes, 294 assets). The own QA
process exited 0; its window is closed and the user's carton window restored.

Native Windows: home, full feed, held intermediate transfer (~41.7%) and full
endpoint each inspected FR/FL/RL/RR/Top. Near-end transfer (~83.3%) inspected Top;
stepped retraction restored both home flags before transfer. Completed Start
was rejected without pose change. Stop at 29.4118% feed removed both run commands;
a further held 0.5 s step retained pose/feedback, and Start was rejected until
Reset. Reset restored all homes. Rear columns and overhead heads occlude some
stock; front views supplement them. No continuous-video/all-frame proof claimed.
Logs: `.tools/dual-spindle-repair-{audit-final,geometry,controller,contract}.log`
and `.tools/dual-spindle-native-repaired.log`.

Still open: normal selected-controller feed/transfer/Start binding, independent
retraction behavior, cutting/material removal and dynamics; reference completion
is timed. Generic preview step-boundary delta remainder is not conserved, so held
step counts are not elapsed-time acceptance. Whole goal stays active; preserve
the user's Conveyor Pusher window. Next: repair the remaining catalog placement
failures, including Scene 38 robot/CNC access/support, or normal controller flow.

Dual Spindle failure reproduction (2026-10-05, previous): Scene 36 home and
reported-complete endpoint were inspected in Windows FR/FL/RL/RR/Top. Held
0.5 s drilling was inspected Top/FR; released preview and Reset were exercised.
Endpoint fixture remains visibly unsupported and detached from the slide;
rear views occlude parts of the stock and are supplemental to front/Top.
No held intermediate transfer or continuous-video proof is claimed.

New `--audit-dual-spindle` measures the actual delivered stock, bit axes,
bearing-contact candidates and 3000 two-ms preview/adapter ticks. Seven failures:
both axes miss shared stock, duplicate coupons remain, fixture lacks home and
route bearing contact, both axial feeds remain zero, slide does not contact
fixture, and 3.2 m fixture travel differs from 2.2 m actual slide travel.
Timed completion/Reset pass; the cell remains FAIL/open. Audit exits 1 without
exception. Clean build, shell and help pass. Logs `.tools/dual-spindle-*.log`.
Next repair must supply a mounted shared fixture/feed/transfer path; no geometry
or controller repair is claimed. Goal active.

Tote Finishing installation checkpoint (2026-10-05, previous): Scene 35's
station supports are clear of the belt/conveyor, the tote contacts the belt,
and the full footprint remains supported at discharge. Grounded columns and
connected overhead heads are checked; moving nozzle tip/chuck/optic are attached.
The opt-in composer uses existing delivered station meshes; masters remain unchanged.

Windows observations: initial FR/FL/RL/RR/Top; two intermediate approach Top
views; held fill FR/FL/RL/RR plus filler-focused RR and Top; released remaining
preview; discharge Top/FR/FL/RL/RR; Reset back to infeed. Close focus crops some
separate equipment and is supplemental. No held cap/label/inspection pose or
continuous video was captured. Native normal Run opened the empty editor and
Start reported no controller loaded; the preview did not replace that controller.

Twelve new geometry/reference checks cover station/conveyor clearance, 245
route positions, bearing/mount connections and 5000 two-ms preview ticks.
487 geometry/workflow checks and 144 controller tests pass; build, scene
contract and 77-scene/294-asset shell pass. Logs `.tools/tote-finishing-*.log`.
Functional acceptance remains FAIL/open: capped fill/volume, cap stroke,
label application, scripted inspection feedback, controller-driven transport/
Start binding, preview restart/resume, dynamics and live PLC. Goal remains active.

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


Status: **active**. The prior software review did not establish multi-angle
visual acceptance. All 77 scenes have initial five-view native static inspections.
Demo 5, Powder Batch Mixer, Parcel Size Sorter, Conveyor Inspection Cell,
the Equipment Gallery, Drive Alarm-Code String and Chicken Label Print have repaired static layouts.
The sorter operator Run still lacks a controller; eight simple panels now have corrected function plates and clear spacing. Other scenes
remain pending unless their row explicitly records observation. Inspection coverage
includes failed scenes; it is not a count of accepted scenes.

## Acceptance method

Bottle Shuttle placement (2026-10-05, previous): Scene 34's imported body
bottom was Y=1.0629166 m above the 0.9 m belt, a 162.9 mm gap. Root Y is now
0.8270833333 m, placing the actual body bottom at 0.9 m. The authored X=-3..3
route stays inside the flat drum-axis span and belt width in 121 samples.
Both sensor stand spans increased from 2.05 to 3.2 m, clearing conveyor
feet, brackets, bracing, connectors and cable bounds at a 5 mm overlap screen.
Grounded feet and clearance from Start/status equipment pass. A front-left
occlusion makes the Start station and sensor appear to occupy the same place;
measured bounds distinguish that occlusion from an intersection. Placement
was retained. Lens-to-lens rays cross actual body triangles only at the
corresponding endpoint; this does not prove continuous runtime feedback.

The bottle's long overlapping legend was split into PROCESS FLUID above the
blue band and white 1 L within it. Imported text bounds fit their regions.
Source/delivery, four numbered renders, hero/blind/scale/wireframe previews
and thumbnail were rebuilt using the filter for this asset only. Collision
export is unchanged. New local renders do not refresh independent recognition.
Five of the original six placement checks failed before repair; two additional
checks cover endpoint optics and neighboring controls. All eight now pass
within 442 total. Build zero warnings/errors, controller 143, shell 77/294,
scene contract and help pass. Logs `.tools/bottle-shuttle-{red-build,
red-geometry,model,build,import,geometry,neighbor-red-build,neighbor-red,
controller,contract,shell,final-native}.log`; neighbor-red is a passing probe,
not a reproduced failure. These are bounded geometry screens, not mechanical
contact, bottle stability, capacity or commissioning proof.

Native final home and held right endpoint inspected FR/FL/RL/RR/Top, plus
home bottle-focused Top/FL/FR for label and seating. Rear views hide the front
label; Top cannot prove vertical bearing. Held outward half-second steps,
mid-route Stop/held advance/Run, real-time return and Reset were exercised.
The timed reference exposes failures: Start clears left feedback while the
bottle is still at the beam; Stop holds pose but Run restarts the route clock,
so its first half-second repeats the pre-Stop pose instead of advancing.
Source StartSequence resets step index/time and translate uses fixed from/to.
Six metres in 2.5 s also implies 2.4 m/s, conflicting with the 0.75 m/s
conveyor setting. Normal loaded-controller round trip remains unverified.
These findings stay FAIL/open; next work is continuous command/feedback and
Stop/resume integration, not accepting the existing timed preview. Goal active.

Shipping strap routing (2026-10-05, previous checkpoint): six disconnected thick bars
were replaced by two closed 35 mm wide, 1.2 mm thick bands derived from the
actual evaluated upper-frame/case section, including labels and barcodes.
The convex hull bridges recessed faces. Returns pass beneath the upper
stringers inside the fork openings, instead of beneath runners on the belt.
Lowest world height is 1.0288 m, 128.8 mm above the 0.9 m belt. Source/delivery,
four model renders and thumbnail were rebuilt. The passive collision envelope
is geometrically unchanged; export renamed its autogenerated mesh only.

Four added checks failed before repair and now pass within 434 total. They
check two bands, welded edge closure/Euler characteristic, underside/belt
height and triangle vertex/midpoint/centroid samples against convex authored
load parts. This is not exhaustive solid intersection or restraint proof.
Build has zero warnings/errors; controller 143, shell 77/294, scene contract
and help validation pass. Logs `.tools/shipping-strap-{red-geometry,model,
import,geometry,build,controller,shell,contract-final,native-final}.log`.

Native focused home and pickup FR/FL/RL/RR/Top plus a camera-only Pallet
underside view were inspected. The low view shows entry and partial return
inside the fork opening; wood/other load surfaces obscure the full underside,
and the upper cases are intentionally cropped. Rear-right pickup has a
stacklight occlusion; other diagonals resolve the load. Top resolves the
upper routes, not underside clearance. Unheld automatic travel reached
pickup with feedback true/100%, conveyor false and cycle complete. Reset
returned zero/clear home. Focus requires an angle-button recenter after motion.
The underside button is confined to Scene 32's opt-in standalone QA preview.
Normal loaded-controller lesson, full mechanical/dynamic acceptance and fresh
independent recognition remain open. Whole review goal remains active.

Shipping load bearing contacts (2026-10-05, previous checkpoint): the actual imported
Scene 32 load had a 40 mm stringer-to-deck gap, a 22.5 mm lower-case-to-deck
gap, and blocks penetrating the lower boards. The source builder now derives
each bearing plane from its neighboring board. Runner and deck datums remain
unchanged; local bearing heights are bottom-board top 0.0725 m, block top
0.1675 m, stringer top 0.2125 m and deck top/lower-case bottom 0.2475 m.
All nine blocks, three stringers, seven deck boards and four lower cases
have bounded contact checks. Thin 0.2 mm sealing tape is seated on the lower
cases; upper cases bear on it instead of intersecting the former 12 mm strip.
Source .blend, delivered .glb, four model renders and thumbnail were rebuilt.
Only Scene 32 directly composes this base asset; separately copied training
assets have not been silently replaced or accepted.

All five new checks failed before repair; 430 geometry checks now pass,
alongside clean build, controller 143, shell 77/294, both scene contracts and
help validation. Logs `.tools/shipping-load-contact-{red-build,red-geometry,
model,import,geometry,controller,shell,contract,native}.log`.
Native home and completed pickup each inspected at shipping_pallet focus
FR/FL/RL/RR/Top. Unheld automatic travel reached pickup with feedback true
and conveyor command false; endpoint X=2.5626 m remains unchanged. Rear-right
pickup obscures the near lower corner behind the stacklight; other angles
resolve the load. Top confirms footprint but cannot prove vertical contact.
Reset returned feedback to zero/clear and restored the supported home pose;
the opt-in focus camera required an angle-button recenter after the reset.
The standalone preview is not the normal loaded-controller lesson. Strap
side/underside routing and full solid-contact/mechanical acceptance remain
open; older hero/scale/wireframe/blind recognition evidence is historical for
the previous model. Goal active.

Shipping pallet reference motion (2026-10-05, previous checkpoint): Scene 32 now uses a
bounded opt-in reference instead of fixed-start timed translations. AUTO Run
and MANUAL Jog require their respective modes; four jogs advance from the
current pose to 25/50/75/100%, and another start at pickup is rejected. Stop
holds position and feedback, Run resumes without teleporting, and mode loss
stops on the next simulation tick. Continuous position and pickup feedback
come from travel and the actual case triangles crossed by the lens-to-lens ray.
The old X=3.1 m endpoint puts the beam in a case-column gap. The first case
crossing is X=2.5626 m: 6.1626 m travel at 0.75 m/s, about 8.217 s from home;
each quarter jog is about 1.54065 m / 2.0542 s. The conveyor's nominal speed
is configured to match; acceleration/slip dynamics are not established.

Native `.tools/pallet-pickup-motion-native.log`: four complete MANUAL jogs,
Run blocked in MANUAL, fifth jog blocked at pickup, and 50%/100% poses inspected
FR/FL/RL/RR/Top. The runners remain on the belt; rear-right pickup is partly
obscured by the stacklight, resolved by the other views. Rebuilt preview
`.tools/pallet-pickup-motion-hud-native.log`: held Run, half-second advance,
Stop/held advance/Run/resumed advance, mode loss, Reset and unheld automatic
completion. Full-precision feedback remains stored; six significant digits and
reserved text height keep preview controls readable and stationary. These
observations are not continuous five-angle coverage of every intermediate pose.

Build has zero warnings/errors; geometry 425 checks, controller 143, shell
77 scenes/294 assets and both declared scene contracts pass. Evidence:
`.tools/pallet-pickup-motion-{geometry-final,controller,contract-v2}.log` and
`.tools/pallet-pickup-motion-hud-{build,shell}.log`. The reference rejects
selected-controller playback and does not replace its command image or motion.
Normal loaded-controller lesson, internal case/deck seating and full mechanical
acceptance remain FAIL/open. Whole review goal remains active.

Shipping pallet installation (2026-10-05, previous checkpoint): Scene 32's pallet runners
were 127.5 mm above the belt and extended 7 mm past the flat drum-axis span.
Root Y=0.8625 m seats all three imported bottom boards at belt Y=0.9 m;
starting X=-3.6 m provides 193 mm flat-span margin. The automatic reference
still ends at X=3.1 m. Manual first-jog endpoint is now X=-1.925 m, exactly
25% of the updated 6.7 m route. Photoeye stand span changes from 2.05 to
3.6 m; its hardware/cable enclosing bounds now clear the conveyor, and both
feet remain on the floor. Five new checks pass within 411 geometry checks,
including actual automatic reference transforms sampled every 10 ms.

Native `.tools/pallet-pickup-native-final.log`: repaired home, held 1.5 s
mid-travel and completed pickup each inspected FR/FL/RL/RR/Top. Stop removed
the conveyor command and advancing the held clock retained the pose; Reset
restored the supported start. An unheld automatic run reached pickup and
stopped. Rear-right pickup obscures part of the load behind the stacklight;
other angles resolve its footprint. This is an offline plant preview, not
the normal loaded-controller lesson or continuous five-angle observation.
Build clean, controller 143, shell 77/294 and both declared contracts pass.
Evidence: `.tools/pallet-pickup-{build,geometry,controller,shell,contract}.log`.
Final endpoint assertion and all 411 checks pass again in
`.tools/pallet-pickup-geometry-final.log`.

At that previous checkpoint, Scene 32 remained FAIL/open for runtime correctness: native Jog after automatic
completion is accepted while AUTO remains true, jumps the pallet back to the
authored start, and retains pickup_sensor=true away from the beam. Position
feedback is only assigned at timed endpoints; reference speed and configured
conveyor speed differ. Repair bounded incremental jog, restart continuity,
mode permissives and actual position/optical feedback next. Internal case/deck
seating and complete mechanical acceptance are not established. Goal active.

Pallet robot handling (2026-10-05, current): Scene 31 now uses the imported
six-joint hierarchy and tool attachment rather than an independent base
oscillator plus disconnected tote translations. The grounded pedestal and
raised receiver keep the installation within reach. Both face 180 degrees;
the receiver backstop faces away from the approaching wrist. Bay centers are
X=2.07/0.93 m, Z=2.15 m, with roller tops at 1.195 m. The first carry passes
in front of the cell before crossing right; approach/return routes use the
staging side to stay inside the catalog base-axis +/-170 degree range.
Both carry bottoms remain at 2.1 m. The route stays in front of the 2.48 m
backstop; that carrying height does not clear the whole backstop.

The wrist-mounted jaws/fasteners and connected guide rods follow the tool.
Forearm cable strain reliefs follow the forearm before wrist roll, with short
brackets on the opposite face. The receiver nameplate is mounted on the
backstop instead of projecting into the wrist descent. Earlier iterations
failed on tote/cable, tote/elbow and wrist/nameplate intersections or base-axis
reach. These were repaired; no joint limit was relaxed to force completion.
The checker also needed nonrecursive operand normalization and actual
triangle/box plus capped-cylinder refinement for curved mesh candidates.
Moving bounds are refreshed once per 10 ms sample, preserving all candidate
checks without repeating transform calls for every equipment pair.

Final geometry v24: 406 checks PASS, including 29 pallet-cell checks. The same
41.446-second reference is sampled at 10 ms for actual joint/load sweeps,
tool attachment, roller landing before count, supported empty-pallet release,
Stop/Reset and rejection of an unreachable target. Restart after a stopped or
completed reference requires Reset, preventing reuse of authored pickup
coordinates against an already moved tote. Malformed robot payloads stop the
reference. Build zero warnings/errors, controller 143, shell 77/294, plant
motion 32, scene reference contract and help validation pass.

Final native Windows PLANT PREVIEW: first lifted tote and completed two-bay
landing each inspected in FR/FL/RL/RR/Top (10 pose/view observations). FR/FL
and RL expose the opposed jaw contact; RR hides part of the grip behind the
arm. Front views hide the landed tote bottoms behind the backstop; rear views
and Top expose both separate bays and the backstop nameplate. Stop held the
lifted tote after releasing the review clock; Run before Reset remained
blocked without moving it. Reset restored both staged totes, pallet, count
zero and parked joints. An unheld reference completed with two placed totes,
empty pallet fully outbound, commands off and cycle_complete true. A visible
Reset instruction was added to the preview controls and inspected separately.
Complete controller-driven robot operation, continuous native
inspection of every intermediate frame, manufacturer limits other than the
catalog base range, robot self-collision, cable bend radius and physical
gripping/load capacity remain unproven. Scene 31 remains FAIL/open overall;
this is an offline reference repair. Logs: .tools/pallet-robot-handling-*.log.
Goal remains active.

Pallet receiver landing (2026-10-05, previous checkpoint): reproduced the old Scene 31
reference reporting two placements with both totes outside the receiver. New
actual-reference checks failed landing, count/landing agreement and path
clearance. Measured bay centers are X=3.03/4.17 m, Z=2.4 m; roller tops are
395 mm. Lift/carry/lower phases now land tote bottoms on those rollers before
incrementing placed_count. Carry bottoms are at 2.1 m, clearing the second
staged tote as well as the conveyor and receiver. A first 1.8 m carry repair
failed the load/load sweep and was corrected. Staged tote roots rose 4.3049 mm
to remove deck penetration; pallet nail heads are seated flush. These are
scene-specific installation/reference changes, with no point ownership change.

The reference now takes about 30.23 seconds; its contract allows 31 seconds.
Four additional geometry checks pass (396 total): flush nail heads, actual
roller landing, placement-count agreement and both load meshes clear through
the reference at 10 ms samples. Existing empty-pallet support/release checks
still pass. Build zero warnings/errors, controller 143, shell 77/294, plant
motion 32, scene reference contract and help validation pass.

Final native Windows PLANT PREVIEW (no PLC controller): held second-carry pose
and completed two-bay landing each inspected in FR/FL/RL/RR/Top (10 views).
Stop removed commands and held the carried pose after releasing the review
clock; Reset restored both staged totes/pallet and count zero. An unheld full
reference completed with two seated totes, empty pallet on the outbound belt,
both commands off and cycle_complete true. Backstop hides most landed load
details in rear views; front views and Top expose the separate bays. The held
carry views visibly show that the robot does not grip/reach the tote. Actual
robot/load attachment, autonomous robot sweep, controller-driven transfer and
continuous native review of every intermediate frame remain open. The 10 ms
screen advances authored reference transforms, not the native robot's separate
autonomous clock. Scene 31 remains FAIL/open overall.
Logs: .tools/pallet-landing-*.log. Goal remains active.

Demo 5 repeatable motion inspection (2026-10-05, previous checkpoint): the opt-in native
review toolbar now provides Hold offline gantry clock and Step 0.5 s. Hold
freezes the controller and autonomous equipment clocks; Step executes the
existing input/ladder/output path and gantry motion in 25 authored 20 ms ticks.
It requires normal Run and the actual manual permissives. It is scoped to this
illustrative gantry, not a general plant step. Editor, scene and source changes
release the hold; the clock controls are hidden outside Demo 5's offline scene.

Native Windows inspection covered seven held phases at 0, 0.5, 1, 1.5, 2, 2.5
and 3 seconds (stroke 0, 25, 75, 100, 75, 25, 0 percent), each in FR/FL/RL/RR/Top:
35 pose/view observations across the outward and return sweep. No pallet/post
intersection or detached tool appeared. RL robot and RR near-post occlusions
hide parts of the rod/tool; Top hides the rod beneath the carriage/bridge.
FR/FL cover those regions. Gantry focus crops unrelated equipment edges.
Release resumed scans; native Stop held scan/pose and Reset restored home/zero.
Editor return and disconnected External PLC/Built-in mode changes were checked
in the final build; hold was released and toolbar visibility was correct.

Build passes with zero warnings/errors; controller 143, shell 77 scenes/294
assets, plant motion 32 and geometry 392 checks pass. The rendered input test
also passes the clock-toolbar click-through guard. Native reviewers exited zero.
Logs: .tools/gantry-clock-*.log. These are sampled native poses plus the existing
20 ms geometry sweep, not continuous all-frame observation. Actual carton
pickup/transport, automatic home feedback and complete catalog motion remain
open. Goal remains active.

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

Carton plate contact (2026-10-05, latest): the plate trailed the load by
629.73 mm throughout extension. Scene 74 now configures that much plate
extension on a rigid two-arm yoke seated in the carriage crossmember and plate.
The grounded cylinder/frame and 1.35 m stroke are unchanged. Front bolts and
lettering are recessed to prevent load penetration. No canonical timing,
feedback, counts, ownership or production reference program changed.

The actual-ladder contact check failed before the fix and now passes throughout
repeated transfers (24 plant-motion checks total). Five added geometry checks
pass: real station acquisition, both yoke connections, plate/load contact,
moving equipment/load solid clearance, and carrying-surface coverage across
151 samples at 2 ms. All 385 geometry checks, clean build, 143 controller tests,
77-scene shell and help coverage pass. Cable clearance uses transformed triangle
bounds rather than empty enclosing space. Logs: `.tools/carton-contact-*.log`.

Native Windows normal Open/Verify + Load/Run used the existing ignored
held-solenoid QA fixture. Home FR, received/full-extension FR/FL/RL/RR/Top,
close pusher Top/RL, Stop and Reset (home close Top/RL, scan zero) inspected.
Top exposes both yoke arms and plate/load contact; rear views partly hide the
carton/table bottom and close views crop the surrounding installation.
The full stroke has sampled geometric evidence, not continuous five-angle
native observation. Reviewer exited zero. Direct launch initially omitted
bundled DOTNET_ROOT; corrected launch succeeds. A helper reset recovered stale
window IDs; no model acceptance was based on failed capture.
Scene 74 remains FAIL/open for optical feedback geometry (received carton can
still cross the beam after canonical feedback clears) and residual static
cable candidates. Current home enclosing-bound candidates total ten; moving
solids pass the new sweep. Earlier plate-gap findings are historical. Full
physical mechanism, receiver accumulation and live PLC acceptance are unproven.

Carton retention (2026-10-05, latest): Scene 74 keeps its released carton
visible after the canonical 80% stroke threshold, continues the remaining
visual stroke, and holds the load on the 900 mm receiving table during
retraction. The single rendered carton is recycled only at the canonical
reload boundary; Reset restores its staged pose. Plant timing, counts,
feedback and point ownership are unchanged. Receiver accumulation is not
implemented. Earlier disappearing-carton notes below are historical.

Four new actual-ladder checks pass: visibility at transfer, full footprint
and bottom contact on the receiver at full stroke, no backward drag during
retraction, reload recycling and Reset (23 plant-motion checks total).
Canonical Python parity passes eight cases/83 snapshots. Build has zero
warnings/errors; 143 controller tests, 77-scene shell and all 380 geometry
checks pass. Evidence: `.tools/carton-retention-*.log`.

Native Windows normal Open/Verify + Load offline/Run used an ignored two-rung
QA project that holds the solenoid after transfer; the production program was
not changed. Received/full-extension FR/FL/RL/RR/Top were inspected. The load
is visible on the table, with lower contact partly hidden in the rear views.
Stop cleared commands and retained the load; Reset restored home/infeed at
scan zero. The owned reviewer exited zero. Automatic retraction/reload is
covered by actual-ladder scans, not continuous native five-angle observation.
Scene 74 remains FAIL/open: the plate trails the carton, optical geometry
does not establish feedback parity, and residual cable candidates remain.
No complete physical transfer or live PLC acceptance is claimed.

Pallet outbound support (2026-10-05, latest): Scene 31 now has a 4 m outbound
conveyor at X=5.4 m, sharing the staging belt's 900 mm carrying height. A
425 mm steel deck on a centered 200 mm bearer, two posts and grounded feet
bridges the belts. The deck leaves 70/35 mm gaps from the flat tangent points;
the deeper bearer stays outside the curved wraps. Raised visual splice
witnesses are flush on both belts. The existing conveyor_run command drives
both conveyors; no PLC points or transport were added. The standalone
reference release now travels 8 m to X=5.2 over 12.307692 s, finishing fully
within the outbound flat carrying surface. Catalog equipment totals and help
were updated (604 instances, 11 in this scene).
An all-catalog metadata audit also repaired stale per-scene counts for the
parcel sorter and carton pusher, plus the pusher's missing receiver type.
All 77 scene counts/type lists and aggregate totals now match their JSON.

Ten new checks pass (380 geometry/workflow checks total): shared deck height,
connected grounded supports, equipment clearance, flush splice witnesses,
all three runner contacts and complete pallet clearance throughout the actual
reference at 10 ms samples, final landing, shared command/completion stop and
Reset. Runner support is a geometric witness requiring at least 100 mm of
longitudinal contact per runner across the three carrying surfaces; this is
not a zero-gap deck, load rating, slip or acceleration proof. Belt/drum/cable
clearance screens transformed triangle bounds where enclosing boxes contain
empty space. Build has zero warnings/errors; 143 virtual-controller tests,
77-scene shell, offline plant motion, scene contract and 294-asset/77-scene
help validation pass. Evidence: `.tools/pallet-outbound-*.log`.

Native Windows standalone PLANT PREVIEW (no PLC controller): staged and final
poses inspected in FR/FL/RL/RR/Top; running reference completed with the
empty pallet on the receiving belt and both conveyor commands off. A held
post-bridge release pose was inspected in Top/RR and bridge-focused Top/RL/RR;
bridge-focused FR is blocked by the receiver backstop, RR partly by the status
light, RL partly by the robot base, and surrounding geometry is cropped.
Reset restored the staged pallet/containers and initial point values. Exact
crossing poses were sampled by the verifier; they were not continuously
observed from five native angles. Scene 31 remains FAIL/open: container paths
miss receiver bays, robot attachment/reach and complete physical transfer are
unproven. The normal controller-owned shell does not execute this standalone
timed reference automatically. Earlier outbound-support findings below are
historical; their remaining robot-transfer findings still apply.

Pallet-cell installation (2026-10-05, latest): Scene 31's pallet and both
containers were lowered together by 80 mm. All three bottom runners now meet
the measured 900 mm belt surface, and both containers retain their deck contact.
The receiver moved laterally from Z=1.2 to Z=2.4 m, clearing its backstop and
base from the conveyor. Sensor spacing increased from 2.05 to 2.50 m to clear
the conveyor braces. A composer bug was also repaired: imported cables have
zero object origins, so TX/RX names now determine stand-side translation;
pigtails stretch vertically from their fixed M12 endpoints to raised heads.
Five new installation checks pass, with 370 geometry/workflow checks total.
The carton pusher's cable clearance uses actual transformed triangle bounds
because the curved tail's enclosing box overlaps empty space by a bracket.
Native Windows FR/FL/RL/RR/Top and focused sensor Top/FL/RR were inspected;
normal Reset retained the corrected seating. Build has zero warnings/errors;
the scene's existing reference contract and 77-scene shell verifier pass.
This closes the measured static pallet, receiver and sensor installation
findings, not the complete robot-transfer finding. The authored container
targets still miss the receiver bays, there is no proven robot attachment,
and the empty-pallet release extends beyond the current belt support. Scene
31 remains FAIL/open. Logs: `.tools/pallet-robot-{red,pigtail-red,geometry,
build,contract,shell,native}.log`. PLC remained disconnected.
The affected carton scene also received a fresh Windows regression: normal
File Open of `.tools/pusher-rod-review.rpproj.json`, Verify + Load offline,
focused home FR/Top, Run to full extension (feedback TRUE at scan 22), extended
Top/FR, Stop (command FALSE, pose held), and Reset (home, feedback FALSE, scan
zero). This deliberately commands an empty pusher stroke; it is not a carton
transfer test. Evidence: `.tools/pallet-robot-pusher-native.log`. Both owned
review windows exited zero, with no native errors; the shell verifier retains
its existing missing-workspace warning.
The final offline rerun also passes all 143 controller tests and 19 plant-motion
checks; no real PLC transport was constructed or contacted. Help coverage
validation passes for 294 assets and 77 scenes.

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

Pusher installation continuation (2026-10-05, superseding the rod-only layout
findings below): Scene 74 now honors its 1.38 m center height with grounded
barrel, guide-bearing and air-manifold supports. Rigid longer guide tails
stay engaged throughout 101 samples; outboard guides clear the cylinder caps,
their brackets retain the wider crossmember, and four plate bolts follow
motion. Relocated photoeye and optional carton-centre projection datum preserve
beam/body overlap while clearing moving members. Ten added checks pass (310
total), build is clean, app-shell and plant execution/reference checks pass.
Native home and full extension each received FR/FL/RL/RR/Top inspection, plus
close pusher Top/RR. Extended clevis and both guide engagements are visible.
Normal Open/Verify/Run used the endpoint fixture: conveyor OFF, photoeye FALSE,
carton seated at infeed. Stop held pose/scan 4688; Reset restored home/False/0.
PLC disconnected, owned window exit zero. Scene remains FAIL/open: no receiver,
unverified plate/carton contact timing, disappearing transferred carton and
seven residual cable broad-phase candidates. See WHOLE_PROGRAM_REVIEW.md for
exact source/runtime scope and logs; no full supported transfer accepted.

Control feedback continuation (2026-10-05): numeric readout clicks no longer
translate fixed stands. Repeated modeled-button presses retain their original
home instead of accumulating travel. The seven-check composed Box Volume suite
fails before and passes after the fix; rendered control verification and clean build
pass. Native wide FR/FL and close FL inspection with repeated L/W/H readout
clicks showed fixed housings/masts/bases and values 850/720/720. Three actual
length-valid cap clicks toggled True with a stationary mount. Reset returned
four zero readouts and shown flags False; PLC disconnected, empty exercise,
owned window exit zero. This bounded pass adds input/feedback evidence, not
new five-angle or loaded calculation acceptance.

Pusher continuation (2026-10-05): Scene 74 rod motion now stretches along the
imported asset's parent X, using its delivered 960 mm length. The gland end
stays fixed, the free end follows the clevis and transverse diameter stays
90 mm throughout 101 samples at each of two world orientations. Off-station
extension/retraction no longer drags the infeed carton sideways. Native normal
Project > Open / Verify + load / Run used an ignored one-network endpoint
fixture (conveyor OFF, pusher held extended, photoeye FALSE). Final FR/FL/RL/RR/
Top individually confirmed the carton stays seated; pusher-focused Top/RR
showed the rod at the gland, while the conveyor obscures the clevis. Stop held
pose/scan 4466 and Reset restored home/output FALSE/scan zero. PLC disconnected,
owned review window exit zero. Build and 300 scene/workflow checks pass, as do
19 plant execution checks, eight Python traces / 83 snapshots and app-shell.
At that earlier rod-only checkpoint the scene was FAIL/open: low plate, photoeye support interference, unresolved
guide-shaft engagement, absent receiver and disappearing transferred carton.
The endpoint review does not prove a supported transfer or mechanical approval.

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
| 5 | `lab-10-03-vision-package-sorter` | 32 | FR/FL/RL/RR/T + carton FR | Carton support source repaired: bottom now contacts delivered belt at Y=0.9, full footprint supported; failing-before/passing-after mesh checks. Latest native review pending. Display source now reuses supported count-display housing with CLASS / NO RESULT text; native readability pending. Four level receiving belts and supported outgoing handoffs now modeled; cabinet surrogate removed. Historical FAIL requires fresh native review; class feedback and driven routing absent; empty exercise editor on Run |
| 6 | `lab-10-04-motor-enum-state` | 0 | FR/FL/RL/RR/T + three plate details; repeated after repair | Repaired plates and symbolic shaft binding; enum state/controller absent, normal Run opens empty editor |
| 7 | `lab-10-05-motor-struct-data` | 0 | FR/FL/RL/RR/T; supported display focus; corrected Top repeated | Display identity/support/spacing and motor command projection repaired; 9 checks PASS, native five-angle reinspection. FAIL/open: no STRUCT record or power/temperature data; normal Run opens blank exercise editor; complete loaded-controller workflow unverified |
| 8 | `lab-10-06-ten-motor-array-startup` | 0 | FR/FL/RL/RR/T + both supported-display readable details | Ten actual motors and display/control spacing repaired; 8 focused checks pass, native five-angle reinspection. FAIL/open: no per-motor array/staggered timing; native loaded-controller workflow unverified |
| 9 | `lab-11-06-wastewater-collection` | 222 (historical; predates repair) | Final repaired FR/FL/RL/RR/T + valve/pump details | Tank spacing, roof probe mounting, measured collector/discharge pipes and grounded supports repaired; 18 focused checks pass. Native QA project load/Run, each permissive loss, Stop/Reset and valve endpoints inspected. FAIL/open: no fluid/analog process model or full continuous-motion proof; default exercise unloaded. |
| 10 | `lab-11-07-multi-conveyor-pallet-route` | 892 (historical); final separate-equipment screen 0 | Final repaired FR/FL/RL/RR/T + receiver/first seam/middle belt details | Three separated belts, level supported handoffs, inline grounded receiver and actual handoff photoeye repaired. Native independent zone commands, loss, Stop/Reset checked with QA program; actual conveyor Reset internals verified. FAIL/open: missing pallet travel, common-stop/edge control, automatic beam feedback and bearing traversal; receiver static. |
| 11 | `lab-11-11-service-elevator` | 63 (historical; predates placement repair) | Final placement FR/FL/RL/RR/T | Shutter/lift separated by measured 0.175 m; cabinet/landing-door overlaps and cabinet grounding repaired and natively re-inspected. FAIL/open: bucket elevator instead of car/shaft, cabinets instead of call station/position sensor, two-landings geometry and full-motion controller workflow absent/unverified. |
| 12 | `lab-11-12-mobile-traffic-lights` | 21 (historical; predates model replacement) | Final repaired FR/FL/RL/RR/T | Horizontal road and two opposing three-color heads replace wall/beacon proxies; stations clear of roadway. Existing green bindings preserved; 145 controller tests/app shell pass. FAIL/open: portable bases, synchronization link, red/amber command timing, vehicle motion and automatic clear feedback; default exercise unloaded. |
| 13 | `lab-11-13-xy-palletizing` | 0 | Native pickup/release/attached transfer; retained layer FR/FL/RL/RR/Top | Supported reachable pick table; four carried/released retained cartons; actual home/completion/inventory; native normal Run/Start/Load, attached Stop/Run/fresh Start and Reset. 58 focused checks / 2576 route samples; moving-peer and bearing screens pass. Partial RL robot/Top bridge occlusion resolved by other views. Fixed symbolic kinematics; forces/automatic feed/safety/full swept-volume unverified |
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
| 28 | `lab-2-14-sump-pump` | 41 (historical); current intentional probe/junction bounds candidates remain | Final mount FR/FL/RL/RR/T + low-fitting FR close; earlier pump details | Joined pipes, aligned valve/spool and grounded supports repaired. Low/high switches now seated at actual modeled thresholds on clear side, above floor and clear of ladder/sight glass; 24 three-scene mount checks pass, native re-inspected. FAIL/open: closed vertical vessel instead of sump, tuning forks instead of floats, full controller-owned level cycle and complete native motion unverified. |
| 29 | `lab-2-15-fume-extractor` | 0 | FR/FL/RL/RR/T static and running 35%; close plate; speed states; native preview Stop/Run/Off/Reset | LIGHT REQUEST, speed binding and preview Stop repaired; six-blade transform checks pass. Open: beacon substitutes light, hood/duct absent, normal Run unloaded; reference preview is not controller lesson acceptance |
| 30 | `lab-2-16-safe-drill` | 24 original / 0 repaired | Native repaired FR/FL/RL/RR/T; stock FR close; normal 3D hand/cycle controls; held feed/bottom four close sides; Stop/Reset/restart; unheld completion | Fixture/feed and honest Stop-hold semantics repaired; normal cycle blocks without controller. Top stock view occluded by head; guard/two-hand safety behavior is not modeled |
| 31 | `lab-2-17-pallet-robot` | 23 historic; broad home candidates are not solid interference | Final modeled pickup and completed landing FR/FL/RL/RR/T; Stop/Reset/restart guard; earlier staged/bridge/sensor views | Imported robot/tool attachment, grounded installation, routes and roller landing repaired; 29 pallet-cell checks PASS within 406 total. Reference sampled at 10 ms; both totes land before count/release, empty pallet fully outbound. FAIL/open: complete normal controller-driven transfer, continuous intermediate native views and physical/rated handling unproven |
| 32 | `lab-2-18-pallet-pickup` | 0 at repaired home | Rebuilt load home/pickup focused FR/FL/RL/RR/T; prior 50% views, four jogs/fifth blocked, Stop/resume/mode loss/Reset; unheld auto | Pallet/case bearing planes, closed strap route, belt support, sensor mounting and bounded reference repaired; 434 checks pass. Home/pickup underside views added. FAIL/open: normal controller lesson and complete solid-contact/mechanical acceptance |
| 33 | `lab-2-19-service-door` | 54 original / 0 repaired | Repaired native FR/FL/RL/RR/T; operator FR close; held opening/Stop/reverse; real-time endpoints; open five views; Reset | Layout/plates and reference reversal/position feedback repaired; raw NC signal displays explicit. Physical limit/cable behavior, compressed slat geometry and loaded-controller operation unaccepted |
| 34 | `lab-2-20-bottle-shuttle` | 39 historic | Repaired home/right endpoint five views; reference completed left and held post-reversal right FR/FL/RL/RR/T; normal controller held outward/completed-left five views, operator project load/Start/Stop/Run/Reset; rebuilt pause amber and return Run=-1 | INT direction contract and editable reference repair normal offline round trip. Eight placement, thirteen reference and twenty controller integration/contract checks pass within 475. Open: first contact not captured as held native frame, continuous native motion coverage, dynamic stability, external profile/live acceptance |
| 35 | `lab-2-21-tote-finishing` | 0 after cable-surface screen | Initial/discharge native FR/FL/RL/RR/T; held fill four sides and filler Top/RR close; released preview/Reset; normal Run/Start | Placement/reference repaired: grounded outside-belt stations, seated tote, supported discharge and attached tools. Missing Start binding and controller-clocked tote travel repaired; 38 Start/travel/normalized-fill/standalone geometry checks pass. Six new PC position/station-window/exit points; Stop/command withdrawal retain load and Reset reloads it. OPEN: latest native command/travel review. New open-fill candidate has exported cavity/aperture and separate initially hidden cap; five mesh ray checks pass, and top/four corner asset renders inspected. Bounded normalized fill and effective stream are connected; moving/off-station/capped/misaligned commands inhibited. Litre/flow calibration and cap application remain unverified. Label application, inspection and complete PLC station sequencing remain open; no complete finishing model |
| 36 | `lab-2-22-dual-spindle` | Repaired separate-equipment screen clear | Repaired native home/full feed/intermediate transfer/endpoint FR/FL/RL/RR/T; near-end Top; stopped partial feed/restart rejection/Reset | Placement/reference repaired: one shared stock, grounded supporting bed, 330 mm axial feeds with reference home flags, contacted matching 2.2 m slide/fixture travel; 18 focused checks PASS. Open: normal controller feed/transfer/Start binding, independent retraction, material removal/dynamics and continuous native motion; completion remains timed |
| 37 | `lab-2-23-parcel-sorter` | 174 | FR/FL/RL/RR/T | Repaired static/declared plant path; normal Run lacks controller |
| 38 | `lab-2-24-robot-cnc` | Reference transfer repaired; 23 checks pass | Home/grip/loaded entry/outfeed FR/FL/RL/RR/T; held route and seated release; held outfeed FR/FL/T; native Stop/restart rejection/Reset; uninterrupted completion | Actual joints/tool carry stock through open access onto supported vise and outfeed. Sampled other-equipment clearance passes; self-collision/full sweep, feedback interlocks, normal controller and cutting remain open. |
| 39 | `lab-2-25-inspection-toggle` | 0 | Native FR/FL/RL/RR/T; repaired plate FR close; real editor create/load/Run/pulse/Stop/Reset | TOGGLE plate repaired, clear stands. Loaded one-network SET test lights beacon; discarded test is not odd/even lesson acceptance |
| 40 | `lab-3-01-guarded-pallet-transfer` | 20 (historic) | Native FR/FL/RL/RR/T; final carton top/FR close; earlier guard toggle/Reset | Carton support repaired and re-inspected. Latest offline layout moves both sensors and the curtain onto the carrying route and replaces the foot-switch surrogate with the mesh swing gate beside the belt. Build/help, thirty-three focused mesh/drive/travel/offline ladder-reference checks, initial-state contract, controller regression and app shell pass. Dedicated nine-point runtime retains the carton at the supported exit after crossing both optical routes; Stop/command withdrawal retain pose and Reset reloads infeed. Current carton-runtime full geometry and all 71 scene contracts pass. Offline normal PLC scan-driven transfer is verified with the explicit review program; fresh native views and protective behavior remain unverified. |
| 41 | `lab-3-02-robot-cell-safe-restart` | 1 | FR/FL/RL/RR/T static and commanded sweep; gate/interlock details; final normal operator workflow | Repaired robot/CNC clearance, complete fence/gate, mounted moving actuator and cabinet identity; 35 focused checks plus native offline Reset/Start/permissive-loss/Stop/Run/Reset pass. Remaining bounds pair is intended sensor mounting. Generic robot sweep/static CNC/E-stop reference only; physical/live proof open |
| 42 | `lab-4-01-press-count-lamp` | 0 | Native FR/FL/RL/RR/T; final FR close PULSE; normal Run, rail/3D pulses, Stop/Run/Reset | Pulse/plate repaired. Three presses light authored CTU lamp, Stop removes output, Run retains count, Reset clears; five integration checks pass |
| 43 | `lab-4-02-counter-reset-lamp` | 0 | Native FR/FL/RL/RR/T; normal project Open/Run; physical COUNT/RESET; Stop/Run/application Reset | Raw momentary pulse/reset, corrected plates; explicit three-count CTU reference native lamp off after 1/2 and on after 3. Reset clears; restart retains count; pending pulses discarded. Eleven exact workflow checks pass. Empty exercise editor remains intentional; hardware/external behavior unverified |
| 44 | `lab-4-03-repeat-cycle-counter` | 0 (historical) | Native focused FR/FL/RL/RR/T at half feed, work endpoint and half return; full completion five views; normal File/Open/Run; held Stop/Run/Reset; continuous batch; focused COUNT 3; rebuilt held Stop label | Actual scoped CNC dry stroke with connected head/spindle and PLC CTU preset three. 23 checks, 618 sampled route poses; repaired roof, front bay, coolant and stock support. Count 1/2/3 observed; no early/idle fourth count. Default editor stays empty. Rear panels obscure internal motion/near stands; Top needs wheel adjustment. Offline prescribed motion and sampled bounds only; OEM dynamics/material removal/live PLC acceptance open |
| 45 | `lab-4-04-sequence-light-tower` | 0 | Repaired FR/FL/RL/RR/T geometry; final FR close/full four colors; normal Open/Start/Step/Stop/Run/Reset | Four physical tiers, independent color bindings, momentary requests and editable offline reference repaired. Native complete cycle/restart/reset inspected; 30 focused checks PASS. Rear details partly occluded. CNC static, sounder uncommanded; live/physical acceptance open |
| 46 | `lab-4-05-dual-input-count-window` | 0 | Native FR/FL/RL/RR/T | Raw A/B/reset, PLC count readouts; explicit numeric-window reference and native File/Open/Run/Stop/reset verified. Six stand footprints clear; no elapsed-time window |
| 47 | `lab-4-06-multi-press-confirmation` | 0 | Native FR/FL/RL/RR/T | Raw A/B/reset, PLC count readouts; explicit exact-count reference and physical 3D button workflow verified. Six stands clear; order unrestricted, no timed-pattern claim |
| 48 | `lab-4-07-parking-garage-entry` | 20 (historical baseline) | Native FR/FL/RL/RR/Top at partial boom, crossing, parked/full and exit; final inline layout five views | Original supported two-bay installation and actual hinged boom; explicit PLC reference counts actual arrivals/departures; retained cars, full-bay guard, Stop/resume and Reset exercised; 27 checks / 6,366 poses pass. Offline reference only; reusable substitute assets elsewhere unresolved |
| 49 | `lab-4-08-package-grouping` | 118 (historical baseline) | Native FR/FL/RL/RR/Top at actual entry, partial stop, crossing and retained completion; close GROUP 3; physical LOAD; Stop/Run/Reset | Original supported roller line/receiver and guided stop; explicit PLC reference counts real incoming beams and releases three retained cartons; 27 checks / 3,847 poses pass. Top infeed HUD cropping resolved by diagonal views. Offline prescribed accumulation; swept-solid/roller mechanics/hardware safety and reusable assets elsewhere unaccepted |
| 50 | `lab-4-09-chain-drive-lift` | 3 intended mounts | Native lower bridge/mid-rise/shaft approach/upper bridge/empty return FR/FL/RL/RR/T; Stop/fresh Start/completed HOME/Reset | Supported complete single-carton route and automatic feedback repaired; 36 focused checks pass with 2,897 samples. OPEN every-frame five-angle native coverage, swept-volume/self-collision and broader physical/process acceptance |
| 51 | `lab-4-10-cookie-packaging` | 3 coarse; cable triangles clear sealer | Native initial/down/first-sealed/complete FR/FL/RL/RR/T; real-time FL/RR | Repaired finite six-cookie cycle: 24 focused checks, 1,252 samples; support/count/seal/retention/Stop/resume/Reset. Top header occludes food; snapshots and bounds only. Physical process acceptance open |
| 52 | `lab-4-11-barrel-fill-station` | 1 coarse; cable triangle bounds clear post | Native initial/fill FR/FL/RL/RR/T; final completion FR/FL/RL/RR/T and wide Top; realtime FL | Repaired finite 150 L fill/retained barrel cycle: 29 focused checks, 1,344 samples; inventory/support/optics/Stop/resume/Reset. Meter formatted F1. Rear-left occlusion and Top cropping resolved by other views; snapshots and bounds only. Physical process acceptance open |
| 53 | `lab-4-12-cable-cut-length` | 0 coarse static candidates | Native initial/feed/partial blade/completed FR/FL/RL/RR/T; wide overhead and cutter focus; normal File/reference/Run/Start; Stop/Run/fresh Start/Reset | Connected reel/rolls/knife/receiver, measured F2 length and 3 m retained cut. 31 focused checks, 581 executed 20 ms samples. Realtime FL initial/feed/completed inspected; brief knife transient not frame-by-frame. Close HUD cropping/header occlusion resolved by other views; small 60 mm gap numerically checked. Prescribed no-slip kinematics and selected bounds only; no solid/swept/physical acceptance |
| 54 | `lab-5-01-delayed-lamp` | 0 | Final native FR/FL/RL/RR/T; readable close selector; physical OFF/ON; held exact TON boundary; Stop/Run/Reset | Existing authored Demo 2 off at ET 1.98 s/on at 2.00 s; Stop resets TON but retains ON; Run requires fresh full delay; OFF clears next scan; final continuous interval not remeasured |
| 55 | `lab-5-02-timed-lamp-off` | 0 | Final native FR/FL/RL/RR/T; physical START; explicitly opened QA reference; exact TP boundary, Stop/Run/Reset, continuous playback | One accepted-scan raw START; PLC TP owns lamp; original reference preset 3 s; active presses ignored; on at 2.98 s/off at 3.00 s; fresh START after expiry; Stop cancels, Run alone does not fire; empty exercise default |
| 56 | `lab-5-03-rotary-flasher` | 0 | Final native FR/FL/RL/RR/T; readable MODE/OFF/FLASH focus; physical selector; held boundaries; Stop/Run/Reset; continuous playback | Raw maintained mode replaces manual flash_tick; explicit original PLC reference 0.5 s half-period, on at 25/off at 50/on at 75 scans; Stop clears lamp/timers, Run retains phase with fresh half-period; OFF clears next scan; empty default exercise |
| 57 | `lab-5-04-alternating-lamps` | 0 | Final native FR/FL/RL/RR/T; readable ENABLE focus; physical OFF/RUN; held boundaries; Stop/Run/Reset; continuous playback | Raw enable replaces fake PC phase; explicit PLC reference alternates amber A/green B every 25 scans; exactly one lamp per enabled scan; Run resumes retained phase with fresh interval; Reset zero/stopped; empty default exercise |
| 58 | `lab-5-05-variable-flash-rate` | 0 | Final native FR/FL/RL/RR/T; readable FAST/SLOW focus; physical three selectors; held boundaries; conflict/no-rate; Stop/Run/Reset; both rates continuous playback | Three raw maintained requests; explicit PLC reference FAST 10 scans/SLOW 25 per half-period; both/neither selections inhibit/clear timing; direct valid rate change retains phase only without accepted intermediate invalid scan; Reset all selectors OFF; empty default exercise |
| 59 | `lab-5-06-running-light-tower` | 0 | Final native FR/FL/RL/RR/T; readable ENABLE and STEP focus; physical controls; explicit reference Open; held and continuous playback; Stop/Run/Reset | Three PLC color channels replace single green-only output; raw ENABLE maintained selector and momentary STEP; explicit original reference red -> amber -> green -> red, no idle advance; disabled/pending-stop pulses discarded; Run restores retained color; Reset OFF/stopped zero; default exercise empty; independent asset/hardware acceptance remains open |
| 60 | `lab-5-07-pedestrian-crossing` | 26 historic; intended road support excluded from separation check | Repaired native FR/FL/RL/RR/T; signal and PATH focus; continuous cycle | Repaired horizontal road/sidewalks, two opposing vehicle and pedestrian heads, independent channels, momentary request, PLC-owned timed reference and startup restart. 30 offline checks pass. Declared simplified timings; no traffic/people motion or public-road compliance; independent asset approval open |
| 61 | `lab-5-08-drawbridge-control` | 43 historical; 2 current shaft/limit-mount contact candidates | Repaired native home/35/70-degree FR/FL/RL/RR/T; focused cam/endpoints and physical selectors; final Top barriers down/90 degrees; continuous cycle and Stop/Run/Reset | Reviewed / bounded: actual hinged deck and two supported barriers; angle-derived limits, moving cam, independent red/green, no false manual HOME. 35 focused checks PASS. Explicit six-rung reference, default exercise blank. Candidate shaft/mount contact intentional; sampled rail bounds and native views only, no solid collision/road/hardware acceptance |
| 62 | `lab-5-09-bag-indexing-conveyor` | 37 historic; 2 current cable enclosing-bound candidates, both excluded by triangle screen | Final installation native FR/FL/RL/RR/T at forward/EXIT/reverse; physical START/CLEAR; continuous cycle; final Top home/returned ENTRY | Reviewed / bounded: original supported sack, actual optical entry/exit and single-clock travel; explicit six-rung reference, manual CLEAR + fresh START return, Stop/Run/Reset. 30 focused checks / 1203 samples pass. Default exercise blank; independent asset approval, flexible-body physics and hardware acceptance open |
| 63 | `lab-5-10-coating-line` | historic 97; sampled load clearance passes | Native home/station/EXIT FR/FL/RL/RR/T; physical controls, timed steps, continuous discharge and Stop | Connected original tunnel/load/duct; retained mounted gun/fan; actual optical feedback and explicit timed PLC reference. 23 checks; 574 healthy scans, 100 spray / 50 purge ticks. Candidate assets and sampled installation only; airflow/coating/physical acceptance unverified |
| 64 | `lab-6-07-luggage-weight-sort` | 110 | Native scale and reject transfer FR/FL/RL/RR/T; normal/reject retained exits, Stop/Run/Reset and 3D controls | REPAIRED bounded layout/reference: suitcase, four-cell deck, retained diverter with direct-drive installation, receiving bridge/outfeed; 41 focused checks PASS. Numeric fixture weighing and one count/category verified offline; native reject cycle verified. Candidate approval/contact dynamics/calibration remain open |
| 65 | `lab-6-08-hand-dryer` | 634 historic; heater bearing and inserted-hand OBB screens PASS | Active native FR/FL/RL/RR/Top; physical input, precise final tick, completion, continuous held-hands, second cycle, Stop/Run, Reset | Connected original dryer/sensor/hand/heater assembly and PLC countdown repaired; 19 offline checks PASS. Source defaults remain blank; explicit reference required. Candidate/physical approval remains open. |
| 66 | `lab-9-01-sum-function` | 0 | Native FR/FL/RL/RR/T; close front; 3D A/B clicks; actual reference Open/Run/Stop/Reset | Two PC DINT inputs and live SUM result; 2+5=7 observed. Seven grounded, clear props. Global-tag reference FB supplied; exercise remains opt-in; FB parameter/instance semantics and independent asset approval open |
| 67 | `lab-9-02-product-function` | 0 | Native FR/FL/RL/RR/T; close front; actual reference Open/Run/Stop/Reset; validity loss; all five 3D inputs after shared-picker repair | Two PC DINT factors and live PRODUCT; 2*5=10 observed. Seven grounded, clear props. Shared-picker follow-up correctly targets all five controls and Reset clears them. Global-tag FB reference opt-in; FB parameter/instance semantics and independent asset approval open |
| 68 | `lab-9-03-sum-and-counter-function` | 0 (historical) | Native FR/FL/RL/RR/T; close operand/result views; actual 3D operand clicks; Project Open/Verify + Load; Run/Stop/Reset | CNC removed; typed DINT operands/sum/count and live readouts added. Opt-in reference displays 2+5=7 and one held completion count, Stop zeros image, Run republishes retained count, Reset clears. Eleven integration/clearance checks pass. 2026-10-06: indicator peers moved inline; final native five angles and full top wheel-zoom inspected; eleven existing integration/clearance checks pass. Default top framing crops an outer control. Open: independent reusable-asset approval; manual call-complete feedback; exercise requires authored/explicit reference logic |
| 69 | `lab-9-04-function-selector` | 0 (historical) | Final native FR/FL/RL/RR/Top, close FL; actual six 3D inputs; Project Open, Run, invalid choice, Stop/Reset | Live DINT A/B/choice/RESULT and opt-in FB routing to SUM/PRODUCT; observed 7/10 and invalid 99 clears validity. Native picking conflict repaired by moving readouts behind buttons; supports and separate-equipment clearance pass. Open: source-selector parity and FB instance/parameter semantics unverified; QA close/top cropping documented |
| 70 | `lab-9-10-box-volume` | 46 (historical) | Updated native FR/FL/RL/RR/Top and close FL; all six 3D inputs; actual reference Open/Verify + Load/Run; invalid value/flag; Stop/Reset | Static supported fixture/carton and four live DINT readouts; observed 850*720*720=440640000 mm3 and maximum 1000000000. Missing validity/zero dimensions invalidate retained result. Readouts grounded/clear; 17 new checks pass. Open: automatic acquisition, source parity, FB instance/parameter semantics and independent asset approval; close-view cropping documented |
| 71 | `lab-9-11-pallet-counting` | 86 | Native FR/FL/RL/RR/T | Carton/fixture/readout geometry repaired and five views/details inspected. Live DINT count/readout FR/FL and invalid/five-edge/held/permissive/Stop/Run/Reset native checks pass. Optical classification/pallet travel/CNC integration open |
| 72 | `lab-9-12-ev-charging-manager` | 95 | Native FR/FL/RL/RR/T | Geometry repaired with original two-bay EV layout; native FR/FL/RL/RR/T inspected. OPEN: 45 geometry/offline adapter/PLC reference checks PASS; two-bay allocation, meter events and PLC kWh provided. Latest controls, vehicle visibility, readouts and native runtime review pending after Escape stop |
| 73 | `scene-1-conveyor-stop` | 34 | Native FR/FL/RL/RR/T | Carton belt contact/load-end footprint repaired; native five wide/Top/FL close and Demo 3 Run/Start/photoeye/Stop/Reset rechecked; full clearance open |
| 74 | `scene-2-conveyor-pusher` | 88 initial; 9 current home enclosing-bound candidates, all excluded by cable triangle screen | Native final staged/received FR/FL/RL/RR/T; close pusher RR/Top; normal Open/Verify/Run/Stop/Reset; earlier receiver Top/FR | Receiving surface, retention, plate contact, reference optical path and static stand/base installation repaired. RX stand Z=-1.55; pusher X=-0.4/Z=-2.4; connected yoke extension 879.73 mm. Geometry 392 and motion 25 PASS. Cable screen uses 5 mm broad candidates and 1 mm world allowance. Native held-solenoid endpoint fixture; lower sensor hidden in rear views, close Top crops carton edges. Normal three-rung reference continuous playback inspected FR/FL/RL/RR/Top, with received retention, Stop and Reset. Held final scan 58 extending, 63 actual release, 65 full, 72 retracting: each FR/FL/RL/RR/Top; Stop/disabled steps, home retention, canonical reload, Reset/release confirmed. Clock regressions 8/8; motion 85/85. Open: arbitrary output sequences and physical transfer |
| 75 | `tank-high-low` | 60 initial; probe/piping/valve-specific screens pass | Native FR/FL/RL/RR/T; valve Top/FL close; normal offline QA Run/Stop/Reset | Probe/piping/valve installations repaired; 365 checks PASS. QA ladder cycle and pointer commands verified. FAIL/open: opaque vessel and broader operator/process acceptance |
| 76 | `tank-level` | 52 initial; probe/analog/piping/valve-specific screens pass | Native FR/FL/RL/RR/T; valve Top/FL close; normal offline QA Run/Stop/Reset | Installations repaired; QA drain pointer and reset 42% / 10.72 mA observed. 365 checks PASS. FAIL/open: opaque vessel and broader operator/process acceptance |
| 77 | `tank-radar` | 80 | Native FR/FL/RL/RR/T; repaired radar five focus views | Radar flange/head mounting and antenna-to-surface distance/beam repaired (sampled checks); 35% native range 3.10036. OPEN: piping/grounded drain valve and explicit inspection view added; 24 focused checks PASS. 32 focused geometry/offline PLC reference checks PASS; new geometry/view/operator requests and full native cycle review pending; no physical acceptance |

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

Vision sorter receiving-geometry measurements (2026-10-06; repair OPEN):
.tools/sorter-receiving-measurement.log records actual Godot transformed
meshes: infeed ends at X=-0.0445833 and top Y=0.9; rotary platter starts
at X=2.02 and top Y=0.93, leaving a 2.0645833 m unsupported horizontal gap
and 30 mm deck mismatch. The destination bank contains one KIN_belt_surface,
not four lanes; its top is Y=1.055 and Z range 3.3..3.9. Source table still
uses the machining-fixture master, not the existing parcelTransfer variant.
The next repair must provide a flat parcel table and connected, level receiving
paths with full footprint support, remove the cabinet diverter surrogate,
and check frames/controls/supports before native multi-angle inspection.
Existing support/display checks pass but do not validate this missing route.

Sorter bridge peer/drum screen checkpoint (2026-10-06; native review OPEN):
The 1 mm bounding/OBB screen found one candidate: the new deck against
KIN_drive_drum (enclosing overlap roughly 54 x 20 x 1400 mm). Every bridge
triangle XY projection was then clipped against the convex hull of actual
transformed drum vertices with a declared 1 mm interior allowance. No
projected penetration remains in the current pose. A 50 mm deliberately
lowered-deck negative control is detected; the deck is restored in finally.
This is a bounded conservative drum-profile screen, not arbitrary exclusion
or complete 3D collision proof. Other bridge/peer equipment screens pass.
The deck/belt-surface and deck/platter mating interfaces remain explicitly
excluded from this peer screen and need separate contact/collision review.
All 12 sorter checks pass, including the retained 2,225 support samples
(.tools/sorter-drum-screen-final.log); build succeeds. Native views and four
outgoing lanes/controller transfer remain OPEN.

Sorter bridge mating-profile checkpoint (2026-10-06; native review OPEN):
The previously excluded belt-surface/platter interfaces now have separate
profile tests. Every actual bridge triangle is projected and clipped against
the transformed obstacle vertex hull: XY for rounded belt/drum and XZ for
platter, with a declared 1 mm interior allowance and depth-range rejection.
Current belt, drum and platter profiles clear. Lowering the deck 50 mm is
detected against belt/drum; shifting the nose 50 mm into the platter is
detected. Each negative control restores the original transform in finally.
All 16 sorter checks pass, preserving 2,225 footprint support samples, in
.tools/sorter-mating-screen-final.log; build succeeds. These are conservative
profile/OBB screens, not general concave-mesh, swept-volume, fabrication or
native visual proof. Four outgoing lanes, correct routing/diverter mechanics,
class feedback and fresh static/full-motion camera inspection remain OPEN.
