# Lab 4.2 - Counter Reset Lamp help

Scene ID: `lab-4-02-counter-reset-lamp`  
Migrated source: `prototype/scenes/lab-4-02-counter-reset-lamp.plcscene`  
Scene contract: `prototype/scenes/lab-4-02-counter-reset-lamp.plcscene`

## Purpose

A counter state controls a lamp and a reset input returns the station to a known state.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `count_reached` | `BOOL` | **PC** | `False` |
| `reset_pressed` | `BOOL` | **PC** | `False` |
| `counter_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle count reached` | `toggle` | `count_reached` |
| `Toggle reset pressed` | `toggle` | `reset_pressed` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `count_reached` | `switch_0` | `switch` |
| `reset_pressed` | `switch_2` | `switch` |
| `counter_lamp` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Counter Reset Lamp switch |
| `indicator_1` | `indicator` | Counter Reset Lamp indicator |
| `switch_2` | `switch` | Counter Reset Lamp operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A counter state controls a lamp and a reset input returns the station to a known state.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The lamp follows the count state and clears when reset is applied.
