# Lab 5.5 - Variable Flash Rate help

Scene ID: `lab-5-05-variable-flash-rate`  
Migrated source: `prototype/scenes/lab-5-05-variable-flash-rate.plcscene`  
Scene contract: `prototype/scenes/lab-5-05-variable-flash-rate.plcscene`

## Purpose

Two operator inputs select a faster or slower flashing rate while a lamp is active.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `flash_enable` | `BOOL` | **PC** | `False` |
| `fast_rate_selected` | `BOOL` | **PC** | `False` |
| `slow_rate_selected` | `BOOL` | **PC** | `False` |
| `rate_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle flash enable` | `toggle` | `flash_enable` |
| `Toggle fast rate selected` | `toggle` | `fast_rate_selected` |
| `Toggle slow rate selected` | `toggle` | `slow_rate_selected` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `flash_enable` | `switch_0` | `switch` |
| `fast_rate_selected` | `switch_1` | `switch` |
| `slow_rate_selected` | `switch_3` | `switch` |
| `rate_lamp` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Variable Flash Rate switch |
| `switch_1` | `switch` | Variable Flash Rate switch |
| `indicator_2` | `indicator` | Variable Flash Rate indicator |
| `switch_3` | `switch` | Variable Flash Rate operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Two operator inputs select a faster or slower flashing rate while a lamp is active.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The lamp uses exactly one selected rate and turns off when flash_enable is removed.
