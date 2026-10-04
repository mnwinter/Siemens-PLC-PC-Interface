# Lab 10.2 - Chicken Label Print help

Scene ID: `lab-10-02-chicken-label-print`  
Migrated source: `prototype/scenes/lab-10-02-chicken-label-print.plcscene`  
Scene contract: `res://scenes/migrated/lab-10-02-chicken-label-print.scene.json`

## Purpose

Boolean label-request exercise with supported food tray, weigh deck, printer and static label-preview props. No measured weight, text formatting, printing or reference controller is supplied.

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
| `conveyor_0` | `conveyor` | Input conveyor (static training layout) |
| `box_2` | `box` | Staged carton on input conveyor |
| `indicator_3` | `indicator` | Print request output |
| `training_accessory_4` | `trainingAccessory` | Chicken Label Print - food product load |
| `training_accessory_5` | `trainingAccessory` | Chicken Label Print - checkweigher |
| `training_accessory_6` | `trainingAccessory` | Chicken Label Print - label printer |
| `training_accessory_7` | `trainingAccessory` | Chicken Label Print - formatted label display |
| `switch_8` | `switch` | Toggle product weighed |
| `switch_9` | `switch` | Toggle printer ready |
| `switch_10` | `switch` | Toggle label data valid |
| `indicator_11` | `indicator` | Label-applied output |

## Stop and safety boundary

Playback Stop freezes local execution; the supplied controller logic owns removal of its output commands. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Boolean label-request exercise with supported food tray, weigh deck, printer and static label-preview props. No measured weight, text formatting, printing or reference controller is supplied.

### Start conditions

- Author or load a valid offline controller for the five declared BOOL points.
- Validity inputs begin false; the simulator shell has no live PLC transport.

### Normal sequence

- Toggle product_weighed, printer_ready and label_data_valid as manual symbolic inputs.
- Observe controller-owned print_request and label_applied indicators; static props do not execute a product-transfer or print cycle.

### Expected observations

- The five BOOL points represent manual validity inputs and controller-owned output indications. The weigh-deck DEMO readout, printer paper and label preview are static; no actual weight or label text is processed.
- A normal Run opens an empty editor until valid controller logic is supplied.