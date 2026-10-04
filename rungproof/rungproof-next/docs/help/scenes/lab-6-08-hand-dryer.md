# Lab 6.8 - Timed Hand-Dryer help

Scene ID: `lab-6-08-hand-dryer`  
Migrated source: `prototype/scenes/lab-6-08-hand-dryer.plcscene`  
Scene contract: `prototype/scenes/lab-6-08-hand-dryer.plcscene`

## Purpose

Hand presence starts a blower and heater cycle with a visible remaining-time indication.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `hands_present` | `BOOL` | **PC** | `False` |
| `dryer_timer_active` | `BOOL` | **PC** | `False` |
| `blower_run` | `BOOL` | **PLC** | `False` |
| `heater_enable` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle hands present` | `toggle` | `hands_present` |
| `Toggle dryer timer active` | `toggle` | `dryer_timer_active` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `hands_present` | `switch_7` | `switch` |
| `dryer_timer_active` | `switch_8` | `switch` |
| `blower_run` | `indicator_2` | `indicator` |
| `heater_enable` | `indicator_9` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `fan_0` | `fan` | Timed Hand-Dryer fan |
| `machine_1` | `machine` | Timed Hand-Dryer machine |
| `indicator_2` | `indicator` | Timed Hand-Dryer indicator |
| `training_accessory_3` | `trainingAccessory` | Timed Hand-Dryer - hand-presence sensor |
| `training_accessory_4` | `trainingAccessory` | Timed Hand-Dryer - air outlet |
| `training_accessory_5` | `trainingAccessory` | Timed Hand-Dryer - heating element |
| `training_accessory_6` | `trainingAccessory` | Timed Hand-Dryer - progress display |
| `switch_7` | `switch` | Timed Hand-Dryer operator input |
| `switch_8` | `switch` | Timed Hand-Dryer operator input |
| `indicator_9` | `indicator` | Timed Hand-Dryer output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Hand presence starts a blower and heater cycle with a visible remaining-time indication.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The blower and heater run only during a valid hand-drying interval.
