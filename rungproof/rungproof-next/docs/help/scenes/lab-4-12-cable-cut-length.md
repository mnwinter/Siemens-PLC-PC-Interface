# Lab 4.12 - Cable Cut-Length Cell help

Scene ID: `lab-4-12-cable-cut-length`  
Migrated source: `prototype/scenes/lab-4-12-cable-cut-length.plcscene`  
Scene contract: `prototype/scenes/lab-4-12-cable-cut-length.plcscene`

## Purpose

An encoder-measured cable length drives a cut request and a home-position interlock.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `cable_present` | `BOOL` | **PC** | `False` |
| `length_reached` | `BOOL` | **PC** | `False` |
| `cutter_home` | `BOOL` | **PC** | `False` |
| `feed_run` | `BOOL` | **PLC** | `False` |
| `cutter_fire` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle cable present` | `toggle` | `cable_present` |
| `Toggle length reached` | `toggle` | `length_reached` |
| `Toggle cutter home` | `toggle` | `cutter_home` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `cable_present` | `switch_9` | `switch` |
| `length_reached` | `switch_10` | `switch` |
| `cutter_home` | `switch_11` | `switch` |
| `feed_run` | `indicator_3` | `indicator` |
| `cutter_fire` | `indicator_12` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Cable Cut-Length Cell motor |
| `machine_1` | `machine` | Cable Cut-Length Cell machine |
| `photoeye_2` | `photoeye` | Cable Cut-Length Cell photoeye |
| `indicator_3` | `indicator` | Cable Cut-Length Cell indicator |
| `training_accessory_4` | `trainingAccessory` | Cable Cut-Length Cell - payoff reel |
| `training_accessory_5` | `trainingAccessory` | Cable Cut-Length Cell - cable dancer |
| `training_accessory_6` | `trainingAccessory` | Cable Cut-Length Cell - length encoder |
| `training_accessory_7` | `trainingAccessory` | Cable Cut-Length Cell - cable cutter |
| `training_accessory_8` | `trainingAccessory` | Cable Cut-Length Cell - cut-length display |
| `switch_9` | `switch` | Cable Cut-Length Cell operator input |
| `switch_10` | `switch` | Cable Cut-Length Cell operator input |
| `switch_11` | `switch` | Cable Cut-Length Cell operator input |
| `indicator_12` | `indicator` | Cable Cut-Length Cell output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

An encoder-measured cable length drives a cut request and a home-position interlock.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The cutter fires only at the target length and returns to home before the next cycle.
