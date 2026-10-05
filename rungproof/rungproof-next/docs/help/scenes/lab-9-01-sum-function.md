# Lab 9.1 - Sum Function Block help

Scene ID: `lab-9-01-sum-function`  
Migrated source: `prototype/scenes/lab-9-01-sum-function.plcscene`  
Scene contract: `res://scenes/migrated/lab-9-01-sum-function.scene.json`

## Purpose

Manual sum validity exercise. The labeled buttons set Boolean inputs; numeric operands and results are not modeled. The RESULT readout has no live value.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `operand_a_valid` | `BOOL` | **PC** | `False` |
| `operand_b_valid` | `BOOL` | **PC** | `False` |
| `calculate_request` | `BOOL` | **PC** | `False` |
| `sum_result_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle operand a valid` | `toggle` | `operand_a_valid` |
| `Toggle operand b valid` | `toggle` | `operand_b_valid` |
| `Toggle calculate request` | `toggle` | `calculate_request` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `operand_a_valid` | `switch_1` | `switch` |
| `operand_b_valid` | `switch_5` | `switch` |
| `calculate_request` | `switch_6` | `switch` |
| `sum_result_valid` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_1` | `switch` | A VALID manual input |
| `indicator_2` | `indicator` | Sum Function Block indicator |
| `training_accessory_4` | `trainingAccessory` | Sum Function Block - numeric result display |
| `switch_5` | `switch` | B VALID manual input |
| `switch_6` | `switch` | CALCULATE manual input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Manual sum validity exercise. The labeled buttons set Boolean inputs; numeric operands and results are not modeled. The RESULT readout has no live value.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The result-valid indication occurs only when both operands are valid and a calculation is requested.
- The readout says NO LIVE VALUE and is not bound to a numeric point.