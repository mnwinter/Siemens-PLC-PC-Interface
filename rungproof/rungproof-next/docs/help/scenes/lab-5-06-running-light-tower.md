# Lab 5.6 - Running-Light Tower help

Scene ID: `lab-5-06-running-light-tower`  
Migrated source: `prototype/scenes/lab-5-06-running-light-tower.plcscene`  
Scene contract: `prototype/scenes/lab-5-06-running-light-tower.plcscene`

## Purpose

A pulse-driven sequence walks a signal through a multi-level tower.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `tower_enable` | `BOOL` | **PC** | `False` |
| `step_pulse` | `BOOL` | **PC** | `False` |
| `tower_step_active` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle tower enable` | `toggle` | `tower_enable` |
| `Toggle step pulse` | `toggle` | `step_pulse` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `tower_enable` | `switch_0` | `switch` |
| `step_pulse` | `switch_2` | `switch` |
| `tower_step_active` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Running-Light Tower switch |
| `indicator_1` | `indicator` | Running-Light Tower indicator |
| `switch_2` | `switch` | Running-Light Tower operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A pulse-driven sequence walks a signal through a multi-level tower.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Each step advances in order and reset returns the tower to its first state.
