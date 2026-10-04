# Lab 4.3 - Repeat-Cycle Counter help

Scene ID: `lab-4-03-repeat-cycle-counter`  
Migrated source: `prototype/scenes/lab-4-03-repeat-cycle-counter.plcscene`  
Scene contract: `prototype/scenes/lab-4-03-repeat-cycle-counter.plcscene`

## Purpose

Repeated operator requests create a bounded machine cycle and a completion indication.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `cycle_request` | `BOOL` | **PC** | `False` |
| `cycle_count_complete` | `BOOL` | **PC** | `False` |
| `cycle_active` | `BOOL` | **PLC** | `False` |
| `cycle_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle cycle request` | `toggle` | `cycle_request` |
| `Toggle cycle count complete` | `toggle` | `cycle_count_complete` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `cycle_request` | `switch_1` | `switch` |
| `cycle_count_complete` | `switch_3` | `switch` |
| `cycle_active` | `indicator_2` | `indicator` |
| `cycle_complete` | `indicator_4` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | Repeat-Cycle Counter machine |
| `switch_1` | `switch` | Repeat-Cycle Counter switch |
| `indicator_2` | `indicator` | Repeat-Cycle Counter indicator |
| `switch_3` | `switch` | Repeat-Cycle Counter operator input |
| `indicator_4` | `indicator` | Repeat-Cycle Counter output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Repeated operator requests create a bounded machine cycle and a completion indication.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A repeated cycle runs until the configured count is complete, then reports completion.
