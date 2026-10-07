# Lab 10.5 - Motor STRUCT Data help

Scene ID: `lab-10-05-motor-struct-data`  
Migrated source: `prototype/scenes/lab-10-05-motor-struct-data.plcscene`  
Scene contract: `prototype/scenes/lab-10-05-motor-struct-data.plcscene`

## Purpose

The current scene is a BOOL-based motor validity exercise. It does not supply a STRUCT-valued motor record, power measurement, or temperature measurement. The scene title identifies the intended lesson; the missing structured-data interface remains an open implementation defect.

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
| `motor_enable` | `motor_0` | `running` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Motor commanded by motor_enable |
| `machine_1` | `machine` | Motor STRUCT Data machine |
| `indicator_2` | `indicator` | Motor STRUCT Data indicator |
| `training_accessory_3` | `trainingAccessory` | Motor Record display - no live value |
| `training_accessory_4` | `trainingAccessory` | Temperature display - no live value |
| `training_accessory_5` | `trainingAccessory` | Struct Data display - no live value |
| `switch_6` | `switch` | Motor STRUCT Data operator input |
| `switch_7` | `switch` | Motor STRUCT Data operator input |
| `switch_8` | `switch` | Motor STRUCT Data operator input |
| `indicator_9` | `indicator` | Motor STRUCT Data output indication |

## Current operating workflow

Author or load controller logic before Run. Require motor_record_valid, temperature_valid, and alarm_clear for the documented validity condition; the controller owns motor_enable and record_ready. Verify that losing each permissive removes the commands, and that Stop and Reset clear them. These BOOLs do not represent measured temperature or a decoded STRUCT. The three displays currently show NO DATA and have no live measurement binding.

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

The current scene is a BOOL-based motor validity exercise. It does not supply a STRUCT-valued motor record, power measurement, or temperature measurement. The scene title identifies the intended lesson; the missing structured-data interface remains an open implementation defect.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The motor record is accepted only when its required fields are valid and alarms are clear.
