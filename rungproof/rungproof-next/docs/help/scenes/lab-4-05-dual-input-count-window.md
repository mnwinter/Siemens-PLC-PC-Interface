# Lab 4.5 - Dual-Input Count Window help

Scene ID: `lab-4-05-dual-input-count-window`  
Migrated source: `prototype/scenes/lab-4-05-dual-input-count-window.plcscene`  
Scene contract: `prototype/scenes/lab-4-05-dual-input-count-window.plcscene`

## Purpose

Two independent inputs must meet separate count conditions before a station indication is enabled.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `channel_a_ready` | `BOOL` | **PC** | `False` |
| `channel_b_ready` | `BOOL` | **PC** | `False` |
| `window_ready` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle channel a ready` | `toggle` | `channel_a_ready` |
| `Toggle channel b ready` | `toggle` | `channel_b_ready` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `channel_a_ready` | `switch_0` | `switch` |
| `channel_b_ready` | `switch_1` | `switch` |
| `window_ready` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Dual-Input Count Window switch |
| `switch_1` | `switch` | Dual-Input Count Window switch |
| `indicator_2` | `indicator` | Dual-Input Count Window indicator |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Two independent inputs must meet separate count conditions before a station indication is enabled.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The ready indication is on only when both count conditions are satisfied.
