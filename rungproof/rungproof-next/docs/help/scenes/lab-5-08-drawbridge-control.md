# Lab 5.8 - Drawbridge Control help

Scene ID: `lab-5-08-drawbridge-control`  
Migrated source: `prototype/scenes/lab-5-08-drawbridge-control.plcscene`  
Scene contract: `prototype/scenes/lab-5-08-drawbridge-control.plcscene`

## Purpose

A bridge raises only after traffic is stopped and the bridge returns to its home limit before reopening traffic.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `traffic_stopped` | `BOOL` | **PC** | `False` |
| `bridge_request` | `BOOL` | **PC** | `False` |
| `bridge_home` | `BOOL` | **PC** | `False` |
| `bridge_raise` | `BOOL` | **PLC** | `False` |
| `traffic_release` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle traffic stopped` | `toggle` | `traffic_stopped` |
| `Toggle bridge request` | `toggle` | `bridge_request` |
| `Toggle bridge home` | `toggle` | `bridge_home` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `traffic_stopped` | `switch_2` | `switch` |
| `bridge_request` | `switch_6` | `switch` |
| `bridge_home` | `switch_7` | `switch` |
| `bridge_raise` | `indicator_1` | `indicator` |
| `traffic_release` | `indicator_8` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `liftTable_0` | `liftTable` | Drawbridge Control lift Table |
| `indicator_1` | `indicator` | Drawbridge Control indicator |
| `switch_2` | `switch` | Drawbridge Control switch |
| `training_accessory_3` | `trainingAccessory` | Drawbridge Control - drawbridge deck |
| `training_accessory_4` | `trainingAccessory` | Drawbridge Control - road barrier |
| `training_accessory_5` | `trainingAccessory` | Drawbridge Control - bridge limit switches |
| `switch_6` | `switch` | Drawbridge Control operator input |
| `switch_7` | `switch` | Drawbridge Control operator input |
| `indicator_8` | `indicator` | Drawbridge Control output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A bridge raises only after traffic is stopped and the bridge returns to its home limit before reopening traffic.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Bridge motion and traffic release are mutually interlocked.
