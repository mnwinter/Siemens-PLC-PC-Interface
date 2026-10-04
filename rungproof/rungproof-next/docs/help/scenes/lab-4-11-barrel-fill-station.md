# Lab 4.11 - Barrel Fill Station help

Scene ID: `lab-4-11-barrel-fill-station`  
Migrated source: `prototype/scenes/lab-4-11-barrel-fill-station.plcscene`  
Scene contract: `prototype/scenes/lab-4-11-barrel-fill-station.plcscene`

## Purpose

A moving container stops at a fill point and resumes only after the fill-complete feedback is present.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `barrel_at_fill` | `BOOL` | **PC** | `False` |
| `fill_complete` | `BOOL` | **PC** | `False` |
| `downstream_clear` | `BOOL` | **PC** | `False` |
| `infeed_run` | `BOOL` | **PLC** | `False` |
| `fill_valve_open` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle barrel at fill` | `toggle` | `barrel_at_fill` |
| `Toggle fill complete` | `toggle` | `fill_complete` |
| `Toggle downstream clear` | `toggle` | `downstream_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `barrel_at_fill` | `switch_8` | `switch` |
| `fill_complete` | `switch_9` | `switch` |
| `downstream_clear` | `switch_10` | `switch` |
| `infeed_run` | `indicator_4` | `indicator` |
| `fill_valve_open` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Barrel Fill Station conveyor |
| `tank_1` | `tank` | Barrel Fill Station tank |
| `valve_2` | `valve` | Barrel Fill Station valve |
| `photoeye_3` | `photoeye` | Barrel Fill Station photoeye |
| `indicator_4` | `indicator` | Barrel Fill Station indicator |
| `training_accessory_5` | `trainingAccessory` | Barrel Fill Station - barrel/container load |
| `training_accessory_6` | `trainingAccessory` | Barrel Fill Station - flow meter |
| `training_accessory_7` | `trainingAccessory` | Barrel Fill Station - fill nozzle |
| `switch_8` | `switch` | Barrel Fill Station operator input |
| `switch_9` | `switch` | Barrel Fill Station operator input |
| `switch_10` | `switch` | Barrel Fill Station operator input |
| `indicator_11` | `indicator` | Barrel Fill Station output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A moving container stops at a fill point and resumes only after the fill-complete feedback is present.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The valve opens only at the fill position and the conveyor resumes after completion.
