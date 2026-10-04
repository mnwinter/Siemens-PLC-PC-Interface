# Lab 10.6 - Ten-Motor Array Startup help

Scene ID: `lab-10-06-ten-motor-array-startup`  
Migrated source: `prototype/scenes/lab-10-06-ten-motor-array-startup.plcscene`  
Scene contract: `prototype/scenes/lab-10-06-ten-motor-array-startup.plcscene`

## Purpose

An array-based startup sequence starts ten motors with a staggered delay and stops the group on alarm.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `group_start_request` | `BOOL` | **PC** | `False` |
| `all_motors_ready` | `BOOL` | **PC** | `False` |
| `group_alarm_clear` | `BOOL` | **PC** | `False` |
| `motor_array_run` | `BOOL` | **PLC** | `False` |
| `startup_sequence_active` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle group start request` | `toggle` | `group_start_request` |
| `Toggle all motors ready` | `toggle` | `all_motors_ready` |
| `Toggle group alarm clear` | `toggle` | `group_alarm_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `group_start_request` | `switch_9` | `switch` |
| `all_motors_ready` | `switch_10` | `switch` |
| `group_alarm_clear` | `switch_11` | `switch` |
| `motor_array_run` | `indicator_5` | `indicator` |
| `startup_sequence_active` | `indicator_12` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Ten-Motor Array Startup motor |
| `motor_1` | `motor` | Ten-Motor Array Startup motor |
| `motor_2` | `motor` | Ten-Motor Array Startup motor |
| `motor_3` | `motor` | Ten-Motor Array Startup motor |
| `motor_4` | `motor` | Ten-Motor Array Startup motor |
| `indicator_5` | `indicator` | Ten-Motor Array Startup indicator |
| `training_accessory_6` | `trainingAccessory` | Ten-Motor Array Startup - ten-motor lineup asset |
| `training_accessory_7` | `trainingAccessory` | Ten-Motor Array Startup - group motor status panel |
| `training_accessory_8` | `trainingAccessory` | Ten-Motor Array Startup - staggered-start sequence display |
| `switch_9` | `switch` | Ten-Motor Array Startup operator input |
| `switch_10` | `switch` | Ten-Motor Array Startup operator input |
| `switch_11` | `switch` | Ten-Motor Array Startup operator input |
| `indicator_12` | `indicator` | Ten-Motor Array Startup output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

An array-based startup sequence starts ten motors with a staggered delay and stops the group on alarm.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The array starts in order with a delay between motors and stops safely on a group alarm.
