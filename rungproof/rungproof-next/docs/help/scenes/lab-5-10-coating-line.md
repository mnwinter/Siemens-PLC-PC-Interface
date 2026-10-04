# Lab 5.10 - Coating Line help

Scene ID: `lab-5-10-coating-line`  
Migrated source: `prototype/scenes/lab-5-10-coating-line.plcscene`  
Scene contract: `prototype/scenes/lab-5-10-coating-line.plcscene`

## Purpose

A workpiece is indexed into a coating enclosure, sprayed for a timed interval, and discharged after ventilation.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `workpiece_at_station` | `BOOL` | **PC** | `False` |
| `spray_ready` | `BOOL` | **PC** | `False` |
| `ventilation_ready` | `BOOL` | **PC** | `False` |
| `index_run` | `BOOL` | **PLC** | `False` |
| `spray_enable` | `BOOL` | **PLC** | `False` |
| `vent_run` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle workpiece at station` | `toggle` | `workpiece_at_station` |
| `Toggle spray ready` | `toggle` | `spray_ready` |
| `Toggle ventilation ready` | `toggle` | `ventilation_ready` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `workpiece_at_station` | `switch_9` | `switch` |
| `spray_ready` | `switch_10` | `switch` |
| `ventilation_ready` | `switch_11` | `switch` |
| `index_run` | `indicator_4` | `indicator` |
| `spray_enable` | `indicator_12` | `indicator` |
| `vent_run` | `indicator_13` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Coating Line conveyor |
| `machine_1` | `machine` | Coating Line machine |
| `fan_2` | `fan` | Coating Line fan |
| `photoeye_3` | `photoeye` | Coating Line photoeye |
| `indicator_4` | `indicator` | Coating Line indicator |
| `training_accessory_5` | `trainingAccessory` | Coating Line - coating enclosure |
| `training_accessory_6` | `trainingAccessory` | Coating Line - spray head |
| `training_accessory_7` | `trainingAccessory` | Coating Line - workpiece load |
| `training_accessory_8` | `trainingAccessory` | Coating Line - ventilation damper |
| `switch_9` | `switch` | Coating Line operator input |
| `switch_10` | `switch` | Coating Line operator input |
| `switch_11` | `switch` | Coating Line operator input |
| `indicator_12` | `indicator` | Coating Line output indication |
| `indicator_13` | `indicator` | Coating Line output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A workpiece is indexed into a coating enclosure, sprayed for a timed interval, and discharged after ventilation.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Spray is enabled only while the workpiece is positioned and ventilation is ready.
