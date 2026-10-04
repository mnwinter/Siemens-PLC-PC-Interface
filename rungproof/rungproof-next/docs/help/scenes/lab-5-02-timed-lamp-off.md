# Lab 5.2 - Timed Lamp-Off help

Scene ID: `lab-5-02-timed-lamp-off`  
Migrated source: `prototype/scenes/lab-5-02-timed-lamp-off.plcscene`  
Scene contract: `prototype/scenes/lab-5-02-timed-lamp-off.plcscene`

## Purpose

A pushbutton starts a fixed on-time and the lamp drops out when the interval expires.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `start_pulse` | `BOOL` | **PC** | `False` |
| `time_active` | `BOOL` | **PC** | `False` |
| `timed_lamp` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle start pulse` | `toggle` | `start_pulse` |
| `Toggle time active` | `toggle` | `time_active` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `start_pulse` | `switch_0` | `switch` |
| `time_active` | `switch_2` | `switch` |
| `timed_lamp` | `indicator_1` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Timed Lamp-Off switch |
| `indicator_1` | `indicator` | Timed Lamp-Off indicator |
| `switch_2` | `switch` | Timed Lamp-Off operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A pushbutton starts a fixed on-time and the lamp drops out when the interval expires.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The lamp is on only during the active timing window.
