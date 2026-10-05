# Lab 9.4 - Function Selector help

Scene ID: `lab-9-04-function-selector`  
Migrated source: `prototype/scenes/lab-9-04-function-selector.plcscene`  
Scene contract: `res://scenes/migrated/lab-9-04-function-selector.scene.json`

## Purpose

Symbolic function-selection logic exercise. The FUNCTION readout is static; numeric function selection and results are not modeled.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `operand_set_valid` | `BOOL` | **PC** | `False` |
| `function_select_valid` | `BOOL` | **PC** | `False` |
| `calculate_request` | `BOOL` | **PC** | `False` |
| `selected_result_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle operand set valid` | `toggle` | `operand_set_valid` |
| `Toggle function select valid` | `toggle` | `function_select_valid` |
| `Toggle calculate request` | `toggle` | `calculate_request` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `operand_set_valid` | `switch_0` | `switch` |
| `function_select_valid` | `switch_5` | `switch` |
| `calculate_request` | `switch_6` | `switch` |
| `selected_result_valid` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `switch_0` | `switch` | Function Selector switch |
| `machine_1` | `machine` | Function Selector machine |
| `indicator_2` | `indicator` | Function Selector indicator |
| `training_accessory_3` | `trainingAccessory` | Function Selector - function-block panel |
| `training_accessory_4` | `trainingAccessory` | Function Selector - numeric selector/display |
| `switch_5` | `switch` | Function Selector operator input |
| `switch_6` | `switch` | Function Selector operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Symbolic function-selection logic exercise. The FUNCTION readout is static; numeric function selection and results are not modeled.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Only the selected calculation path may assert selected_result_valid.
- The readout says NO LIVE VALUE and is not bound to a numeric point.