# Lab 2.22 - Dual-Spindle Plate Cell help

Scene ID: `lab-2-22-dual-spindle`  
Migrated source: `prototype/scenes/lab-2-22-dual-spindle.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-22-dual-spindle.scene.json`

## Purpose

Two drill heads process a clamped plate in parallel, retract independently, and release a transfer slide only after both are home.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `drill_a_run` | `BOOL` | **PLC** | `False` |
| `drill_b_run` | `BOOL` | **PLC** | `False` |
| `drill_a_home` | `BOOL` | **PC** | `True` |
| `drill_b_home` | `BOOL` | **PC** | `True` |
| `transfer_extend` | `BOOL` | **PLC** | `False` |
| `status_color` | `STRING` | **SIM** | `amber` |
| `cycle_complete` | `BOOL` | **SIM** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start dual-spindle cycle` | `start` | `dual-cycle` |
| `Stop both spindles` | `stop` | `` |
| `Reset plate cell` | `reset` | `` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `drill_a_run` | `drill_a` | `running` |
| `drill_b_run` | `drill_b` | `running` |
| `transfer_extend` | `plate_transfer` | `position` |
| `status_color` | `dual_drill_status` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `drill_a` | `drillPress` | Pilot drill spindle |
| `drill_b` | `drillPress` | Countersink spindle |
| `metal_plate` | `box` | Clamped metal plate |
| `plate_transfer` | `pusher` | Plate transfer slide |
| `dual_drill_start` | `switch` | Start dual-spindle cycle |
| `dual_drill_status` | `indicator` | Dual-spindle status |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `drill_a_run` | `False` |
| `drill_b_run` | `False` |
| `transfer_extend` | `False` |
| `status_color` | `red` |

## Machine guide

Two drill heads process a clamped plate in parallel, retract independently, and release a transfer slide only after both are home.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.
- The PLC is ready to command drill_a_run, drill_b_run, transfer_extend.

### Normal sequence

- parallel drilling
- spindle dwell
- retracting
- both home
- transfer plate
- complete

### Expected observations

- Transfer begins only after both spindles are home; all motion commands finish off.
