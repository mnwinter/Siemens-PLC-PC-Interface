# Lab 5.1 - Delayed Lamp help

Scene ID: `lab-5-01-delayed-lamp`  
Migrated source: `prototype/scenes/lab-5-01-delayed-lamp.plcscene`  
Scene contract: `prototype/scenes/lab-5-01-delayed-lamp.plcscene`

## Purpose

A selector request starts an on-delay before a station lamp is energized.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `timer_request` | `BOOL` | **PC** | `False` |
| `delay_complete` | `BOOL` | **PC** | `False` |
| `delayed_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle timer request` | `toggle` | `timer_request` |
| `Toggle delay complete` | `toggle` | `delay_complete` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `timer_request` | `switch_0` | `switch` |
| `delay_complete` | `switch_2` | `switch` |
| `delayed_lamp` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Delayed Lamp switch |
| `indicator_1` | `indicator` | Delayed Lamp indicator |
| `switch_2` | `switch` | Delayed Lamp operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A selector request starts an on-delay before a station lamp is energized.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The lamp remains off until delay_complete, then turns on while the request remains active.
