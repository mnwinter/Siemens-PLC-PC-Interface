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
