# Conveyor Pusher help

Scene ID: `scene-2-conveyor-pusher`  
Migrated source: `prototype/scenes/scene-2-conveyor-pusher.plcscene`  
Scene contract: `res://scenes/migrated/scene-2-conveyor-pusher.scene.json`

## Purpose

The established production sequence: run to the photoeye, stop, extend the single-solenoid pusher, transfer the package, retract, and admit the next package.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `part_at_pusher` | `BOOL` | **PC** | `False` |
| `pusher_extended` | `BOOL` | **PC** | `False` |
| `pusher_retracted` | `BOOL` | **PC** | `True` |
| `conveyor_running` | `BOOL` | **PLC** | `False` |
| `pusher_extend` | `BOOL` | **PLC** | `False` |
| `pusher_position` | `REAL` | **SIM** | `0` |
| `component_state` | `STRING` | **SIM** | `stopped_loaded` |
| `parts_completed` | `DINT` | **SIM** | `0` |

## Operator actions

No operator action contract is declared.

## Equipment bindings

No point-to-equipment bindings are declared.

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `scene2_conveyor` | `conveyor` | Scene 2 conveyor |
| `scene2_product` | `box` | Scene 2 package |
| `scene2_photoeye` | `photoeye` | Part-at-pusher photoeye |
| `scene2_pusher` | `pusher` | Single-solenoid spring-return pusher |
| `scene2_receiver` | `containerReceiver` | Flat carton receiving table |
| `scene2_station` | `switch` | Scene Start / Stop |
| `scene2_stacklight` | `indicator` | Scene 2 status light |

## Stop and safety boundary

The composed pusher uses its configured 1.38 m centre height, grounded mounts,
outboard guided shafts and moving plate fasteners. A rigid two-arm yoke extends
the plate 629.73 mm from the carriage to contact the carton; the cylinder frame
and 1.35 m stroke stay in place. Front bolts and lettering are recessed to
avoid penetrating the load. The pusher is offset along the conveyor to clear
the inclined photoeye path. Its heads face each other at 1.047 m and 2.405 m
heights; the optional visual carton-centre datum positions the body across the
beam at first detection without changing the symbolic plant model.

The flat receiving table meets the belt edge at the same 900 mm top height.
Its supports clear the conveyor bracing, and the receiver-side photoeye stand
is beyond the table. The canonical plant releases the infeed carton at 80%
stroke. The renderer keeps that carton visible, continues it to the table at
full stroke, and holds it during retraction. The same single rendered carton
returns to the infeed when the plant admits its next load; this does not model
a queue of received cartons. Reset restores the staged carton.

Plate contact, connected yoke travel, support and solid clearance have sampled
geometry checks and actual-ladder contact checks. Native Windows inspection
covers the received endpoint in five views, close top/rear-left and Stop/Reset.
The inclined beam clears above the received carton. Continuous lens-to-lens
geometry agrees with feedback through reference ladder cycles; fine stroke
sampling allows a 2 mm grazing boundary at the canonical 80% release. Head
aim, grounded supports and cable connections also pass geometric checks.
Residual static cable candidates and complete physical transfer remain open.
These checks do not establish a rated mechanism or safety function.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.
