# Lab 6.7 - Luggage Weight Sort help

Scene ID: `lab-6-07-luggage-weight-sort`  
Migrated source: `prototype/scenes/lab-6-07-luggage-weight-sort.plcscene`  
Scene contract: `res://scenes/migrated/lab-6-07-luggage-weight-sort.scene.json`

## Purpose

Symbolic luggage routing logic exercise. The WEIGHT readout is static; numeric weight measurement is not modeled.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `bag_present` | `BOOL` | **PC** | `False` |
| `weight_valid` | `BOOL` | **PC** | `False` |
| `class_selected` | `BOOL` | **PC** | `False` |
| `weigh_cycle` | `BOOL` | **PLC** | `False` |
| `class_result` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle bag present` | `toggle` | `bag_present` |
| `Toggle weight valid` | `toggle` | `weight_valid` |
| `Toggle class selected` | `toggle` | `class_selected` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `bag_present` | `switch_8` | `switch` |
| `weight_valid` | `switch_9` | `switch` |
| `class_selected` | `switch_10` | `switch` |
| `weigh_cycle` | `indicator_3` | `indicator` |
| `class_result` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Luggage Weight Sort conveyor |
| `box_1` | `box` | Luggage Weight Sort box |
| `machine_2` | `machine` | Luggage Weight Sort machine |
| `indicator_3` | `indicator` | Luggage Weight Sort indicator |
| `training_accessory_4` | `trainingAccessory` | Luggage Weight Sort - scale/load-cell platform |
| `training_accessory_5` | `trainingAccessory` | Luggage Weight Sort - luggage load |
| `training_accessory_6` | `trainingAccessory` | Luggage Weight Sort - weight display |
| `training_accessory_7` | `trainingAccessory` | Luggage Weight Sort - reject diverter |
| `switch_8` | `switch` | Luggage Weight Sort operator input |
| `switch_9` | `switch` | Luggage Weight Sort operator input |
| `switch_10` | `switch` | Luggage Weight Sort operator input |
| `indicator_11` | `indicator` | Luggage Weight Sort output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Symbolic luggage routing logic exercise. The WEIGHT readout is static; numeric weight measurement is not modeled.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A valid bag produces one category result and increments only its class counter.
- The readout says NO LIVE VALUE and is not bound to a numeric point.