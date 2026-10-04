# Lab 4.4 - Sequence Light Tower help

Scene ID: `lab-4-04-sequence-light-tower`  
Migrated source: `prototype/scenes/lab-4-04-sequence-light-tower.plcscene`  
Scene contract: `prototype/scenes/lab-4-04-sequence-light-tower.plcscene`

## Purpose

A state sequence advances a four-color tower through a defined indication order.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `sequence_start` | `BOOL` | **PC** | `False` |
| `sequence_step_due` | `BOOL` | **PC** | `False` |
| `tower_active` | `BOOL` | **PLC** | `False` |
| `sequence_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle sequence start` | `toggle` | `sequence_start` |
| `Toggle sequence step due` | `toggle` | `sequence_step_due` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `sequence_start` | `switch_1` | `switch` |
| `sequence_step_due` | `switch_3` | `switch` |
| `tower_active` | `indicator_2` | `indicator` |
| `sequence_complete` | `indicator_4` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | Sequence Light Tower machine |
| `switch_1` | `switch` | Sequence Light Tower switch |
| `indicator_2` | `indicator` | Sequence Light Tower indicator |
| `switch_3` | `switch` | Sequence Light Tower operator input |
| `indicator_4` | `indicator` | Sequence Light Tower output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A state sequence advances a four-color tower through a defined indication order.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The tower advances in order and ends with every command off.
