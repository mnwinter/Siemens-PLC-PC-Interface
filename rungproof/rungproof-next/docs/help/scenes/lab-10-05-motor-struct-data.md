# Lab 10.5 - Motor STRUCT Data help

Scene ID: `lab-10-05-motor-struct-data`  
Migrated source: `prototype/scenes/lab-10-05-motor-struct-data.plcscene`  
Scene contract: `prototype/scenes/lab-10-05-motor-struct-data.plcscene`

## Purpose

A structured motor record combines command, power, temperature, and alarm fields for one motor.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `motor_record_valid` | `BOOL` | **PC** | `False` |
| `temperature_valid` | `BOOL` | **PC** | `False` |
| `alarm_clear` | `BOOL` | **PC** | `False` |
| `motor_enable` | `BOOL` | **PLC** | `False` |
| `record_ready` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle motor record valid` | `toggle` | `motor_record_valid` |
| `Toggle temperature valid` | `toggle` | `temperature_valid` |
| `Toggle alarm clear` | `toggle` | `alarm_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `motor_record_valid` | `switch_6` | `switch` |
| `temperature_valid` | `switch_7` | `switch` |
| `alarm_clear` | `switch_8` | `switch` |
| `motor_enable` | `indicator_2` | `indicator` |
| `record_ready` | `indicator_9` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Motor STRUCT Data motor |
| `machine_1` | `machine` | Motor STRUCT Data machine |
| `indicator_2` | `indicator` | Motor STRUCT Data indicator |
| `training_accessory_3` | `trainingAccessory` | Motor STRUCT Data - motor diagnostic faceplate |
| `training_accessory_4` | `trainingAccessory` | Motor STRUCT Data - temperature display |
| `training_accessory_5` | `trainingAccessory` | Motor STRUCT Data - structured-data monitor |
| `switch_6` | `switch` | Motor STRUCT Data operator input |
| `switch_7` | `switch` | Motor STRUCT Data operator input |
| `switch_8` | `switch` | Motor STRUCT Data operator input |
| `indicator_9` | `indicator` | Motor STRUCT Data output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A structured motor record combines command, power, temperature, and alarm fields for one motor.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The motor record is accepted only when its required fields are valid and alarms are clear.
