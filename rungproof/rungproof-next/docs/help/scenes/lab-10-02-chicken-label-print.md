# Lab 10.2 - Chicken Label Print help

Scene ID: `lab-10-02-chicken-label-print`  
Migrated source: `prototype/scenes/lab-10-02-chicken-label-print.plcscene`  
Scene contract: `prototype/scenes/lab-10-02-chicken-label-print.plcscene`

## Purpose

A weighed product receives a formatted label after the weight and printer-ready signals are valid.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `product_weighed` | `BOOL` | **PC** | `False` |
| `printer_ready` | `BOOL` | **PC** | `False` |
| `label_data_valid` | `BOOL` | **PC** | `False` |
| `print_request` | `BOOL` | **PLC** | `False` |
| `label_applied` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle product weighed` | `toggle` | `product_weighed` |
| `Toggle printer ready` | `toggle` | `printer_ready` |
| `Toggle label data valid` | `toggle` | `label_data_valid` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `product_weighed` | `switch_8` | `switch` |
| `printer_ready` | `switch_9` | `switch` |
| `label_data_valid` | `switch_10` | `switch` |
| `print_request` | `indicator_3` | `indicator` |
| `label_applied` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Chicken Label Print conveyor |
| `machine_1` | `machine` | Chicken Label Print machine |
| `box_2` | `box` | Chicken Label Print box |
| `indicator_3` | `indicator` | Chicken Label Print indicator |
| `training_accessory_4` | `trainingAccessory` | Chicken Label Print - food product load |
| `training_accessory_5` | `trainingAccessory` | Chicken Label Print - checkweigher |
| `training_accessory_6` | `trainingAccessory` | Chicken Label Print - label printer |
| `training_accessory_7` | `trainingAccessory` | Chicken Label Print - formatted label display |
| `switch_8` | `switch` | Chicken Label Print operator input |
| `switch_9` | `switch` | Chicken Label Print operator input |
| `switch_10` | `switch` | Chicken Label Print operator input |
| `indicator_11` | `indicator` | Chicken Label Print output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A weighed product receives a formatted label after the weight and printer-ready signals are valid.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A label request is issued only when the product data and printer are ready.
