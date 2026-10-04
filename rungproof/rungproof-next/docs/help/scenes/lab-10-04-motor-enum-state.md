# Lab 10.4 - Motor Operating-State Enum help

Scene ID: `lab-10-04-motor-enum-state`  
Migrated source: `prototype/scenes/lab-10-04-motor-enum-state.plcscene`  
Scene contract: `res://scenes/migrated/lab-10-04-motor-enum-state.scene.json`

## Purpose

Boolean inputs and motor/status outputs for an operating-state exercise. No enum-valued state or reference controller is supplied; author or load controller logic before Run.

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
| `motor_running` | `motor_0` | `running` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `motor_0` | `motor` | Motor commanded by motor_running |
| `switch_1` | `switch` | Start request |
| `indicator_2` | `indicator` | Motor running indication |
| `switch_3` | `switch` | Stop request |
| `switch_4` | `switch` | Simulated fault active |
| `indicator_5` | `indicator` | State-valid indication |

## Stop and safety boundary

Playback Stop freezes local motion. Controller logic owns removal of motor_running for stop or fault conditions; the scene does not write a PLC. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Boolean inputs and motor/status outputs for an operating-state exercise. No enum-valued state or reference controller is supplied; author or load controller logic before Run.

### Start conditions

- Author or load a valid offline controller for the five declared BOOL points.
- Keep stop_request and fault_active false before applying start_request.
- The common watchdog tags are retained lesson metadata, not verified live PLC communication in this shell.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- When supplied controller logic commands motor_running, the shaft graphic and running indicator follow that output.
- The state-valid indicator follows state_valid; no named enum state is displayed.
- Fault/stop priority must be implemented and verified in the supplied controller logic.
