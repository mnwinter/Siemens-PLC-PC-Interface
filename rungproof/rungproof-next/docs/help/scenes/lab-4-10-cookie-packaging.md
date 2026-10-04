# Lab 4.10 - Cookie Packaging Cell help

Scene ID: `lab-4-10-cookie-packaging`  
Migrated source: `prototype/scenes/lab-4-10-cookie-packaging.plcscene`  
Scene contract: `prototype/scenes/lab-4-10-cookie-packaging.plcscene`

## Purpose

A product stream is counted, indexed, and presented to a packaging station.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `product_present` | `BOOL` | **PC** | `False` |
| `packaging_ready` | `BOOL` | **PC** | `False` |
| `batch_complete` | `BOOL` | **PC** | `False` |
| `infeed_run` | `BOOL` | **PLC** | `False` |
| `packaging_enable` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle product present` | `toggle` | `product_present` |
| `Toggle packaging ready` | `toggle` | `packaging_ready` |
| `Toggle batch complete` | `toggle` | `batch_complete` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `product_present` | `switch_8` | `switch` |
| `packaging_ready` | `switch_9` | `switch` |
| `batch_complete` | `switch_10` | `switch` |
| `infeed_run` | `indicator_3` | `indicator` |
| `packaging_enable` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Cookie Packaging Cell conveyor |
| `machine_1` | `machine` | Cookie Packaging Cell machine |
| `photoeye_2` | `photoeye` | Cookie Packaging Cell photoeye |
| `indicator_3` | `indicator` | Cookie Packaging Cell indicator |
| `training_accessory_4` | `trainingAccessory` | Cookie Packaging Cell - food product load |
| `training_accessory_5` | `trainingAccessory` | Cookie Packaging Cell - indexing conveyor |
| `training_accessory_6` | `trainingAccessory` | Cookie Packaging Cell - packaging machine |
| `training_accessory_7` | `trainingAccessory` | Cookie Packaging Cell - product counter |
| `switch_8` | `switch` | Cookie Packaging Cell operator input |
| `switch_9` | `switch` | Cookie Packaging Cell operator input |
| `switch_10` | `switch` | Cookie Packaging Cell operator input |
| `indicator_11` | `indicator` | Cookie Packaging Cell output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A product stream is counted, indexed, and presented to a packaging station.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Product advances only when packaging is ready and the current batch is not complete.
