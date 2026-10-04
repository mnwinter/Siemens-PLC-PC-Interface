# Lab 5.3 - Rotary Flasher help

Scene ID: `lab-5-03-rotary-flasher`  
Migrated source: `prototype/scenes/lab-5-03-rotary-flasher.plcscene`  
Scene contract: `prototype/scenes/lab-5-03-rotary-flasher.plcscene`

## Purpose

A mode selector enables a periodic lamp flasher with a clear off position.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `flash_mode_selected` | `BOOL` | **PC** | `False` |
| `flash_tick` | `BOOL` | **PC** | `False` |
| `flash_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle flash mode selected` | `toggle` | `flash_mode_selected` |
| `Toggle flash tick` | `toggle` | `flash_tick` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `flash_mode_selected` | `switch_0` | `switch` |
| `flash_tick` | `switch_2` | `switch` |
| `flash_lamp` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Rotary Flasher switch |
| `indicator_1` | `indicator` | Rotary Flasher indicator |
| `switch_2` | `switch` | Rotary Flasher operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A mode selector enables a periodic lamp flasher with a clear off position.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The lamp flashes only in the selected mode and is off when the selector is cleared.
