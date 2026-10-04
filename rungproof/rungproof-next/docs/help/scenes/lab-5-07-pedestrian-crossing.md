# Lab 5.7 - Pedestrian Crossing help

Scene ID: `lab-5-07-pedestrian-crossing`  
Migrated source: `prototype/scenes/lab-5-07-pedestrian-crossing.plcscene`  
Scene contract: `prototype/scenes/lab-5-07-pedestrian-crossing.plcscene`

## Purpose

A request starts a timed crossing sequence that coordinates vehicle and pedestrian indications.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `crossing_request` | `BOOL` | **PC** | `False` |
| `sequence_running` | `BOOL` | **PC** | `False` |
| `clear_to_finish` | `BOOL` | **PC** | `False` |
| `vehicle_stop` | `BOOL` | **PLC** | `False` |
| `pedestrian_walk` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle crossing request` | `toggle` | `crossing_request` |
| `Toggle sequence running` | `toggle` | `sequence_running` |
| `Toggle clear to finish` | `toggle` | `clear_to_finish` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `crossing_request` | `switch_2` | `switch` |
| `sequence_running` | `switch_6` | `switch` |
| `clear_to_finish` | `switch_7` | `switch` |
| `vehicle_stop` | `indicator_0` | `indicator` |
| `pedestrian_walk` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `indicator_0` | `indicator` | Pedestrian Crossing indicator |
| `indicator_1` | `indicator` | Pedestrian Crossing indicator |
| `switch_2` | `switch` | Pedestrian Crossing switch |
| `training_accessory_3` | `trainingAccessory` | Pedestrian Crossing - traffic signal head |
| `training_accessory_4` | `trainingAccessory` | Pedestrian Crossing - pedestrian signal head |
| `training_accessory_5` | `trainingAccessory` | Pedestrian Crossing - crosswalk/road module |
| `switch_6` | `switch` | Pedestrian Crossing operator input |
| `switch_7` | `switch` | Pedestrian Crossing operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A request starts a timed crossing sequence that coordinates vehicle and pedestrian indications.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A crossing request stops vehicle traffic before enabling the pedestrian indication, then returns to idle.
