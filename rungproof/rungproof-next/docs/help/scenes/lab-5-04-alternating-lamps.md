# Lab 5.4 - Alternating Lamps help

Scene ID: `lab-5-04-alternating-lamps`  
Migrated source: `prototype/scenes/lab-5-04-alternating-lamps.plcscene`  
Scene contract: `prototype/scenes/lab-5-04-alternating-lamps.plcscene`

## Purpose

A running timer alternates two lamps so exactly one output is active at a time.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `alternate_enable` | `BOOL` | **PC** | `False` |
| `alternate_phase` | `BOOL` | **PC** | `False` |
| `lamp_a` | `BOOL` | **PLC** | `False` |
| `lamp_b` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle alternate enable` | `toggle` | `alternate_enable` |
| `Toggle alternate phase` | `toggle` | `alternate_phase` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `alternate_enable` | `switch_0` | `switch` |
| `alternate_phase` | `switch_3` | `switch` |
| `lamp_a` | `indicator_1` | `indicator` |
| `lamp_b` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Alternating Lamps switch |
| `indicator_1` | `indicator` | Alternating Lamps indicator |
| `indicator_2` | `indicator` | Alternating Lamps indicator |
| `switch_3` | `switch` | Alternating Lamps operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A running timer alternates two lamps so exactly one output is active at a time.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The two lamps alternate without overlapping and both turn off when disabled.
