# Lab 4.6 - Multi-Press Confirmation help

Scene ID: `lab-4-06-multi-press-confirmation`  
Migrated source: `prototype/scenes/lab-4-06-multi-press-confirmation.plcscene`  
Scene contract: `prototype/scenes/lab-4-06-multi-press-confirmation.plcscene`

## Purpose

A paired-button confirmation exercise requires the requested press pattern before enabling the result.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `button_a_pattern_ok` | `BOOL` | **PC** | `False` |
| `button_b_pattern_ok` | `BOOL` | **PC** | `False` |
| `confirmation_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle button a pattern ok` | `toggle` | `button_a_pattern_ok` |
| `Toggle button b pattern ok` | `toggle` | `button_b_pattern_ok` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `button_a_pattern_ok` | `switch_0` | `switch` |
| `button_b_pattern_ok` | `switch_1` | `switch` |
| `confirmation_valid` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Multi-Press Confirmation switch |
| `switch_1` | `switch` | Multi-Press Confirmation switch |
| `indicator_2` | `indicator` | Multi-Press Confirmation indicator |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A paired-button confirmation exercise requires the requested press pattern before enabling the result.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The confirmation is valid only when both independent press patterns are valid.
