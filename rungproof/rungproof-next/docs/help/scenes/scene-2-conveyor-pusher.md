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
| `scene2_station` | `switch` | Scene Start / Stop |
| `scene2_stacklight` | `indicator` | Scene 2 status light |

## Stop and safety boundary

The composed pusher uses its configured 1.38 m centre height, grounded mounts,
outboard guided shafts and moving plate fasteners. The photoeye is offset
along the conveyor; the optional visual carton-centre datum positions its body
across the beam at first detection without changing the symbolic plant model.

This scene still lacks a receiving surface. Its canonical plant removes the
carton at the transfer threshold; the rendered path does not establish plate
contact or a fully supported physical transfer. These remain open review
findings even when the controller sequence and limit feedback pass.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.
