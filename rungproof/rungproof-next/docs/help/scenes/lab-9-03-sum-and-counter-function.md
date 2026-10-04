# Lab 9.3 - Sum and Counter Function help

Scene ID: `lab-9-03-sum-and-counter-function`  
Migrated source: `prototype/scenes/lab-9-03-sum-and-counter-function.plcscene`  
Scene contract: `prototype/scenes/lab-9-03-sum-and-counter-function.plcscene`

## Purpose

A function calculates a result and increments an internal event count when the call completes.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `inputs_valid` | `BOOL` | **PC** | `False` |
| `calculate_request` | `BOOL` | **PC** | `False` |
| `call_complete` | `BOOL` | **PC** | `False` |
| `result_valid` | `BOOL` | **PLC** | `False` |
| `event_counted` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle inputs valid` | `toggle` | `inputs_valid` |
| `Toggle calculate request` | `toggle` | `calculate_request` |
| `Toggle call complete` | `toggle` | `call_complete` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `inputs_valid` | `switch_1` | `switch` |
| `calculate_request` | `switch_3` | `switch` |
| `call_complete` | `switch_4` | `switch` |
| `result_valid` | `indicator_2` | `indicator` |
| `event_counted` | `indicator_5` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | Sum and Counter Function machine |
| `switch_1` | `switch` | Sum and Counter Function switch |
| `indicator_2` | `indicator` | Sum and Counter Function indicator |
| `switch_3` | `switch` | Sum and Counter Function operator input |
| `switch_4` | `switch` | Sum and Counter Function operator input |
| `indicator_5` | `indicator` | Sum and Counter Function output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A function calculates a result and increments an internal event count when the call completes.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Each completed call produces one valid result and one counter event.
