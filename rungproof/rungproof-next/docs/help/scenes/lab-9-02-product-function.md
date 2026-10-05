# Lab 9.2 - Product Function Block help

Scene ID: `lab-9-02-product-function`  
Migrated source: `prototype/scenes/lab-9-02-product-function.plcscene`  
Scene contract: `res://scenes/migrated/lab-9-02-product-function.scene.json`

## Purpose

Symbolic product-function logic exercise. The RESULT readout is static; numeric operands and a product output are not modeled.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `factor_a_valid` | `BOOL` | **PC** | `False` |
| `factor_b_valid` | `BOOL` | **PC** | `False` |
| `calculate_request` | `BOOL` | **PC** | `False` |
| `product_result_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle factor a valid` | `toggle` | `factor_a_valid` |
| `Toggle factor b valid` | `toggle` | `factor_b_valid` |
| `Toggle calculate request` | `toggle` | `calculate_request` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `factor_a_valid` | `switch_1` | `switch` |
| `factor_b_valid` | `switch_5` | `switch` |
| `calculate_request` | `switch_6` | `switch` |
| `product_result_valid` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | Product Function Block machine |
| `switch_1` | `switch` | Product Function Block switch |
| `indicator_2` | `indicator` | Product Function Block indicator |
| `training_accessory_3` | `trainingAccessory` | Product Function Block - function-block calculation panel |
| `training_accessory_4` | `trainingAccessory` | Product Function Block - numeric result display |
| `switch_5` | `switch` | Product Function Block operator input |
| `switch_6` | `switch` | Product Function Block operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Symbolic product-function logic exercise. The RESULT readout is static; numeric operands and a product output are not modeled.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The product result becomes valid only after both factors and the request are valid.
- The readout says NO LIVE VALUE and is not bound to a numeric point.