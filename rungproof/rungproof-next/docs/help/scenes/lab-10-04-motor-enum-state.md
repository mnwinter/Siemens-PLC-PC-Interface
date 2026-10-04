# Lab 10.4 - Motor Operating-State Enum help

Scene ID: `lab-10-04-motor-enum-state`  
Migrated source: `prototype/scenes/lab-10-04-motor-enum-state.plcscene`  
Scene contract: `prototype/scenes/lab-10-04-motor-enum-state.plcscene`

## Purpose

A motor state machine exposes one named operating state at a time and rejects conflicting commands.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `start_request` | `BOOL` | **PC** | `False` |
| `stop_request` | `BOOL` | **PC** | `False` |
| `fault_active` | `BOOL` | **PC** | `False` |
| `motor_running` | `BOOL` | **PLC** | `False` |
| `state_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle start request` | `toggle` | `start_request` |
| `Toggle stop request` | `toggle` | `stop_request` |
| `Toggle fault active` | `toggle` | `fault_active` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `start_request` | `switch_1` | `switch` |
| `stop_request` | `switch_3` | `switch` |
| `fault_active` | `switch_4` | `switch` |
| `motor_running` | `indicator_2` | `indicator` |
| `state_valid` | `indicator_5` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Motor Operating-State Enum motor |
| `switch_1` | `switch` | Motor Operating-State Enum switch |
| `indicator_2` | `indicator` | Motor Operating-State Enum indicator |
| `switch_3` | `switch` | Motor Operating-State Enum operator input |
| `switch_4` | `switch` | Motor Operating-State Enum operator input |
| `indicator_5` | `indicator` | Motor Operating-State Enum output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A motor state machine exposes one named operating state at a time and rejects conflicting commands.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A fault or stop request dominates start and leaves the motor in a safe stopped state.
