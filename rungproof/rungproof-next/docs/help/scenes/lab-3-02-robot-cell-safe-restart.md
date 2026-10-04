# Lab 3.2 - Robot Cell Safe Restart help

Scene ID: `lab-3-02-robot-cell-safe-restart`  
Migrated source: `prototype/scenes/lab-3-02-robot-cell-safe-restart.plcscene`  
Scene contract: `prototype/scenes/lab-3-02-robot-cell-safe-restart.plcscene`

## Purpose

A robot cell requires a closed gate, reset edge, and ready status before motion may be requested.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `gate_closed` | `BOOL` | **PC** | `False` |
| `reset_complete` | `BOOL` | **PC** | `False` |
| `robot_ready` | `BOOL` | **PC** | `False` |
| `robot_enable` | `BOOL` | **PLC** | `False` |
| `cell_ready` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle gate closed` | `toggle` | `gate_closed` |
| `Toggle reset complete` | `toggle` | `reset_complete` |
| `Toggle robot ready` | `toggle` | `robot_ready` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `gate_closed` | `switch_2` | `switch` |
| `reset_complete` | `switch_8` | `switch` |
| `robot_ready` | `switch_9` | `switch` |
| `robot_enable` | `indicator_3` | `indicator` |
| `cell_ready` | `indicator_10` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `robotArm_0` | `robotArm` | Robot Cell Safe Restart robot Arm |
| `machine_1` | `machine` | Robot Cell Safe Restart machine |
| `switch_2` | `switch` | Robot Cell Safe Restart switch |
| `indicator_3` | `indicator` | Robot Cell Safe Restart indicator |
| `training_accessory_4` | `trainingAccessory` | Robot Cell Safe Restart - machine-guarding fence |
| `training_accessory_5` | `trainingAccessory` | Robot Cell Safe Restart - coded safety gate switch |
| `training_accessory_6` | `trainingAccessory` | Robot Cell Safe Restart - emergency-stop station |
| `training_accessory_7` | `trainingAccessory` | Robot Cell Safe Restart - robot controller/status panel |
| `switch_8` | `switch` | Robot Cell Safe Restart operator input |
| `switch_9` | `switch` | Robot Cell Safe Restart operator input |
| `indicator_10` | `indicator` | Robot Cell Safe Restart output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A robot cell requires a closed gate, reset edge, and ready status before motion may be requested.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A restart request cannot enable motion until the gate is closed and the robot is ready.
