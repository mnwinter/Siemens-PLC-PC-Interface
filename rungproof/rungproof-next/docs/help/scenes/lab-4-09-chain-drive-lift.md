# Lab 4.9 - Chain-Drive Lift help

Scene ID: `lab-4-09-chain-drive-lift`  
Migrated source: `prototype/scenes/lab-4-09-chain-drive-lift.plcscene`  
Scene contract: `prototype/scenes/lab-4-09-chain-drive-lift.plcscene`

## Purpose

A chain-driven transfer moves a box only when the lift is at a valid home position.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `box_present` | `BOOL` | **PC** | `False` |
| `lift_home` | `BOOL` | **PC** | `False` |
| `destination_clear` | `BOOL` | **PC** | `False` |
| `chain_run` | `BOOL` | **PLC** | `False` |
| `lift_enable` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle box present` | `toggle` | `box_present` |
| `Toggle lift home` | `toggle` | `lift_home` |
| `Toggle destination clear` | `toggle` | `destination_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `box_present` | `switch_8` | `switch` |
| `lift_home` | `switch_9` | `switch` |
| `destination_clear` | `switch_10` | `switch` |
| `chain_run` | `indicator_3` | `indicator` |
| `lift_enable` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Chain-Drive Lift conveyor |
| `liftTable_1` | `liftTable` | Chain-Drive Lift lift Table |
| `box_2` | `box` | Chain-Drive Lift box |
| `indicator_3` | `indicator` | Chain-Drive Lift indicator |
| `training_accessory_4` | `trainingAccessory` | Chain-Drive Lift - chain conveyor |
| `training_accessory_5` | `trainingAccessory` | Chain-Drive Lift - chain hoist/vertical lift |
| `training_accessory_6` | `trainingAccessory` | Chain-Drive Lift - lift limit switches |
| `training_accessory_7` | `trainingAccessory` | Chain-Drive Lift - mechanical stop |
| `switch_8` | `switch` | Chain-Drive Lift operator input |
| `switch_9` | `switch` | Chain-Drive Lift operator input |
| `switch_10` | `switch` | Chain-Drive Lift operator input |
| `indicator_11` | `indicator` | Chain-Drive Lift output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A chain-driven transfer moves a box only when the lift is at a valid home position.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The chain and lift are enabled only with a box present, valid home, and clear destination.
