# Lab 9.10 - Box Volume Calculation help

Scene ID: `lab-9-10-box-volume`  
Migrated source: `prototype/scenes/lab-9-10-box-volume.plcscene`  
Scene contract: `prototype/scenes/lab-9-10-box-volume.plcscene`

## Purpose

Three measured dimensions are accepted before a box-volume result is released to the next step.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `length_valid` | `BOOL` | **PC** | `False` |
| `width_valid` | `BOOL` | **PC** | `False` |
| `height_valid` | `BOOL` | **PC** | `False` |
| `volume_result_valid` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle length valid` | `toggle` | `length_valid` |
| `Toggle width valid` | `toggle` | `width_valid` |
| `Toggle height valid` | `toggle` | `height_valid` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `length_valid` | `switch_5` | `switch` |
| `width_valid` | `switch_6` | `switch` |
| `height_valid` | `switch_7` | `switch` |
| `volume_result_valid` | `indicator_2` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `box_0` | `box` | Box Volume Calculation box |
| `machine_1` | `machine` | Box Volume Calculation machine |
| `indicator_2` | `indicator` | Box Volume Calculation indicator |
| `training_accessory_3` | `trainingAccessory` | Box Volume Calculation - dimension sensors |
| `training_accessory_4` | `trainingAccessory` | Box Volume Calculation - numeric measurement display |
| `switch_5` | `switch` | Box Volume Calculation operator input |
| `switch_6` | `switch` | Box Volume Calculation operator input |
| `switch_7` | `switch` | Box Volume Calculation operator input |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Three measured dimensions are accepted before a box-volume result is released to the next step.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Volume result-valid is asserted only when all three dimensions are valid.
