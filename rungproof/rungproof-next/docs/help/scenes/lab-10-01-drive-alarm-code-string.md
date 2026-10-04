# Lab 10.1 - Drive Alarm-Code String help

Scene ID: `lab-10-01-drive-alarm-code-string`  
Migrated source: `prototype/scenes/lab-10-01-drive-alarm-code-string.plcscene`  
Scene contract: `prototype/scenes/lab-10-01-drive-alarm-code-string.plcscene`

## Purpose

A drive alarm string is received, searched for a selected code, and converted into a PLC alarm result.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `drive_alarm_string_valid` | `BOOL` | **PC** | `False` |
| `alarm_code_found` | `BOOL` | **PC** | `False` |
| `alarm_reset` | `BOOL` | **PC** | `False` |
| `drive_alarm_active` | `BOOL` | **PLC** | `False` |
| `alarm_match_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle drive alarm string valid` | `toggle` | `drive_alarm_string_valid` |
| `Toggle alarm code found` | `toggle` | `alarm_code_found` |
| `Toggle alarm reset` | `toggle` | `alarm_reset` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `drive_alarm_string_valid` | `switch_6` | `switch` |
| `alarm_code_found` | `switch_7` | `switch` |
| `alarm_reset` | `switch_8` | `switch` |
| `drive_alarm_active` | `indicator_2` | `indicator` |
| `alarm_match_valid` | `indicator_9` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Drive Alarm-Code String motor |
| `machine_1` | `machine` | Drive Alarm-Code String machine |
| `indicator_2` | `indicator` | Drive Alarm-Code String indicator |
| `training_accessory_3` | `trainingAccessory` | Drive Alarm-Code String - VFD diagnostic panel |
| `training_accessory_4` | `trainingAccessory` | Drive Alarm-Code String - fieldbus alarm-string display |
| `training_accessory_5` | `trainingAccessory` | Drive Alarm-Code String - drive status indicator |
| `switch_6` | `switch` | Drive Alarm-Code String operator input |
| `switch_7` | `switch` | Drive Alarm-Code String operator input |
| `switch_8` | `switch` | Drive Alarm-Code String operator input |
| `indicator_9` | `indicator` | Drive Alarm-Code String output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A drive alarm string is received, searched for a selected code, and converted into a PLC alarm result.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The alarm result is active only for a valid drive message containing the selected code.
