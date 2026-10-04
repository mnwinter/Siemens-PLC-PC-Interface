# Lab 11.13 - XY Palletizing Cell help

Scene ID: `lab-11-13-xy-palletizing`  
Migrated source: `prototype/scenes/lab-11-13-xy-palletizing.plcscene`  
Scene contract: `prototype/scenes/lab-11-13-xy-palletizing.plcscene`

## Purpose

A gantry places cartons at indexed pallet positions and reports a full-layer condition.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `carton_at_pick` | `BOOL` | **PC** | `False` |
| `gantry_home` | `BOOL` | **PC** | `False` |
| `pallet_position_valid` | `BOOL` | **PC** | `False` |
| `vacuum_pick` | `BOOL` | **PLC** | `False` |
| `gantry_cycle` | `BOOL` | **PLC** | `False` |
| `layer_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle carton at pick` | `toggle` | `carton_at_pick` |
| `Toggle gantry home` | `toggle` | `gantry_home` |
| `Toggle pallet position valid` | `toggle` | `pallet_position_valid` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `carton_at_pick` | `switch_9` | `switch` |
| `gantry_home` | `switch_10` | `switch` |
| `pallet_position_valid` | `switch_11` | `switch` |
| `vacuum_pick` | `indicator_3` | `indicator` |
| `gantry_cycle` | `indicator_12` | `indicator` |
| `layer_complete` | `indicator_13` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `robotArm_0` | `robotArm` | XY Palletizing Cell robot Arm |
| `conveyor_1` | `conveyor` | XY Palletizing Cell conveyor |
| `box_2` | `box` | XY Palletizing Cell box |
| `indicator_3` | `indicator` | XY Palletizing Cell indicator |
| `training_accessory_4` | `trainingAccessory` | XY Palletizing Cell - XY gantry |
| `training_accessory_5` | `trainingAccessory` | XY Palletizing Cell - vacuum gripper |
| `training_accessory_6` | `trainingAccessory` | XY Palletizing Cell - pallet magazine |
| `training_accessory_7` | `trainingAccessory` | XY Palletizing Cell - carton load |
| `training_accessory_8` | `trainingAccessory` | XY Palletizing Cell - coordinate sensors |
| `switch_9` | `switch` | XY Palletizing Cell operator input |
| `switch_10` | `switch` | XY Palletizing Cell operator input |
| `switch_11` | `switch` | XY Palletizing Cell operator input |
| `indicator_12` | `indicator` | XY Palletizing Cell output indication |
| `indicator_13` | `indicator` | XY Palletizing Cell output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A gantry places cartons at indexed pallet positions and reports a full-layer condition.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A carton is picked only at home and placed only at a valid pallet position.
