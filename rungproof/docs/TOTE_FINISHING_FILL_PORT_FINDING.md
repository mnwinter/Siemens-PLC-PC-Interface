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
