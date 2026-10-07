# Tote-finishing fill-port finding - 2026-10-06

## Confirmed geometry issue

Scene `lab-2-21-tote-finishing` maps `finishing_tote` to `loads.ibc.1000l.v1`. Its delivered GLB includes a closed `IBC_fill_cap` and a solid `IBC_tank` roof beneath it. This prevents a credible open-port filling sequence even if a volume counter were added.

Imported the actual delivery file `assets/factory_kit/ibc_tote/delivery/ibc_tote.glb` into Blender and ray-cast down the fill centre independently against both meshes. Blender Z-up results:

| Mesh | Centre ray hit | Hit Z (m) | Delivered vertices |
| --- | --- | --- | --- |
| IBC_fill_cap | true | 1.559999943 | 644 |
| IBC_tank | true | 1.490000010 | 384 |

The source Blend independently produces the same two hit heights. Evidence logs are `.tools/tote-delivery-port-inspection.log` and `.tools/tote-fill-port-inspection.log`; JSON captures are beside them. These are mesh inspections, not native Windows visual acceptance.

## Required repair and verification

Create a scene-specific open-fill tote installation with an actual roof aperture and inner cavity. Retain a separate cap for later application; preserve the existing generic closed IBC used elsewhere. Any derived catalog candidate must receive its own review status rather than inherit the source asset's approval. Verify the exported aperture and cap interface from multiple views, recheck belt support and station clearance, then connect a bounded fill quantity and station-presence checks to the existing PLC valve command. Filling, cap/label application and inspection remain unimplemented.

## Repair checkpoint

The scene now selects loads.ibc.open-finishing.v1, an unapproved derived candidate with actual cavity and aperture. Its original generic basis is unchanged. Exported ray evidence is saved at assets/material_flow/tote_finishing_open_ibc/review/exported_aperture_checks.json: centre hits the cavity floor at Z 0.11 m, the surrounding roof still hits at Z 1.49 m, the bore is open and the rim/cap remain solid. The cap is separately retained in delivery and hidden by the initial finishing installation. The top and four corner open-port Blender views were inspected, and 25 focused scene checks pass with bore-aware nozzle clearance. Native scene inspection, bounded fill quantity and cap application remain pending.

## Hollow cap and normalized fill checkpoint

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

## Capper application gap - OPEN

The current delivered installation places the neck rim at world Y 2.232912 m,
and the retained CAP_UNDER_CHUCK lower face at Y 2.385000 m: a 0.152088 m
vertical separation. These bounds come from .tools/tote-cap-cup-audit.log and
are captured in review/capper_application_gap.json beside the candidate asset.
SceneComposer.ToteFinishing.cs still supplies ContinuousRotation only. This
is a confirmed missing axial application motion, not a successful capping step.
The 152 mm separation is not a prescribed actuator stroke: the held cap and
tote cap differ in dimensions, and the seating plane, chuck retention, extension,
release and return must be resolved before setting travel. Use the repaired
hollow cap geometry consistently, measure the seat/chuck interface, then screen
the full axial stroke and retained capped tote route. Native views remain open.

## Held-cap geometry repair checkpoint

The capper now reuses the actual exported hollow tote cap mesh at the same
installation scale. Its roof contacts the chuck lower face without axial
overlap. The held chuck/body/ring/cap assembly is raised together by 100 mm
to clear the passing neck; the generic capper master is unchanged. Two focused
checks failed before the repair and pass afterward. The first repaired pose
failed route clearance; the raised pose passes all 40 focused checks, including
244 route intervals and the 5,000-tick preview (.tools/capper-cap-raised.log).
This repairs the held shape and indexing clearance only. Axial application,
release, retained capped travel and native multi-angle acceptance remain OPEN.
The prior 152 mm finding records the earlier geometry and is superseded by
the repaired held pose; it must not be used as the new actuator stroke.

## Installed cap rotation repair

An analytic check of the old horizontal installation scales (X 0.81545,
Z 0.59840) found a 27.394 mm negative envelope clearance after a 90-degree
cap turn. The finishing installation now opts into preserving circular neck
and cap geometry, using the larger common horizontal scale while preserving
their centers and vertical seating geometry. The held cap uses the same scale.
Forty focused actual-scene checks still pass (.tools/circular-cap-audit.log),
including bore engagement, fill inhibition and full supported preview route.
The reproducible nominal envelope check is tools/modeling/verify_installed_tote_cap_rotation.py.
This is not a thread/seal fit, swept triangle proof or native acceptance.
Axial application and the latest native multi-angle review remain OPEN.

## Composed-mesh radial regression

Two actual Godot mesh checks now verify equal horizontal neck/cap dimensions
and delivered cap lower-wall radial clearance at home and a quarter-turn,
with 2 mm minimum margin relative to the neck outer vertices. All 42 focused
checks pass in .tools/installed-cap-audit.log; build succeeds. These checks
inspect installed vertices/transforms, strengthening the earlier nominal
calculation. They do not prove thread engagement, sealing or axial application.
Native Windows multi-angle inspection remains OPEN after the prior Escape
stop; permission to resume computer control has been requested.

## Axial model checkpoint - adapter pending

ToteCapPlantModel.cs adds an isolated renderer-neutral illustrative cycle:
home, lowering, seated dwell, release and retraction. Accepted ticks are at
most 20 ms. Command/eligibility loss before release retracts without setting
Applied; an applied cap survives command withdrawal and Stop. Pause holds the
stroke and Reset clears the applied state. A continuously asserted command
cannot apply repeatedly. Durations are constructor inputs, not hardware claims.
Fifteen focused model checks pass (.tools/tote-cap-model-tests.log); the main
application builds with zero warnings/errors (.tools/tote-cap-model-build.log).
The model is NOT connected to scene meshes or PC feedback yet. The remaining
adapter must derive the stroke from actual seating geometry, move the chuck
assembly, exchange held/retained cap visibility at release, project feedback,
and check full stroke/capped discharge before native multi-angle acceptance.

## Axial adapter checkpoint - full motion acceptance OPEN

The external-clock adapter now derives axial stroke from delivered held and
seated cap top heights, moves the spindle/chuck assembly, hides the held cap
and reveals the tote-parented cap at modeled release, then retracts. Five
PC-owned points report extension, applied, busy, inhibited and home. Eligibility
requires actual completed normalized fill, stopped conveyor, open tote and
actual neck vertices within the held cap lower-wall bore with 1 mm margin.
Eight new scene tests pass; all 50 focused checks pass in
.tools/tote-cap-integration.log. Model tests remain 15 PASS. Stop retains partial
stroke; withdrawal before application retracts without release; Reset restores
the open tote. An applied cap remains visible at the retained exit. The older
standalone preview is preserved. Full axial stroke/capped-route collision
screening and native static/motion views remain OPEN. The external-clock
adapter currently projects axial motion only: rotating seated dwell/thread
engagement, torque and sealing are not proved. Concurrent conveyor commands
during an extended chuck still require explicit conflict testing; no protective
hardware behavior is claimed. Labeling and inspection remain unfinished.

## Concurrent travel/cap conflict repair

An actual adapter regression failed: conveyor_run moved the tote while the
cap chuck was extended, and the next cap attempt missed alignment. The
simulator now inhibits effective tote/belt travel while cap extension is
nonzero, retains the raw PLC command and publishes PC tote_transfer_inhibited.
The conflicting request makes cap eligibility false, so the held cap retracts
without release. Travel can resume when the chuck is home. This is an authored
simulation interlock, not evidence of protective hardware or a rated safety
function. The failing regression passes after repair; all 51 focused checks
pass in .tools/cap-conflict-after.log. Full stroke collision screening,
latest capped-route geometry and native multi-angle inspection remain OPEN.

## Sampled axial and capped-discharge clearance checkpoint

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
