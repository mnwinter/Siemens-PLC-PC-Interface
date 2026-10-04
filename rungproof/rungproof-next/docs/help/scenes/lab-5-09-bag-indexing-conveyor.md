# Lab 5.9 - Bag Indexing Conveyor help

Scene ID: `lab-5-09-bag-indexing-conveyor`  
Migrated source: `prototype/scenes/lab-5-09-bag-indexing-conveyor.plcscene`  
Scene contract: `prototype/scenes/lab-5-09-bag-indexing-conveyor.plcscene`

## Purpose

A bag is indexed between two sensors, paused for operator action, and restarted from a known direction.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `bag_at_entry` | `BOOL` | **PC** | `False` |
| `bag_at_exit` | `BOOL` | **PC** | `False` |
| `pause_clear` | `BOOL` | **PC** | `False` |
| `conveyor_run` | `BOOL` | **PLC** | `False` |
| `conveyor_reverse` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle bag at entry` | `toggle` | `bag_at_entry` |
| `Toggle bag at exit` | `toggle` | `bag_at_exit` |
| `Toggle pause clear` | `toggle` | `pause_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `bag_at_entry` | `switch_4` | `switch` |
| `bag_at_exit` | `switch_8` | `switch` |
| `pause_clear` | `switch_9` | `switch` |
| `conveyor_run` | `indicator_10` | `indicator` |
| `conveyor_reverse` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Bag Indexing Conveyor conveyor |
| `box_1` | `box` | Bag Indexing Conveyor box |
| `photoeye_2` | `photoeye` | Bag Indexing Conveyor photoeye |
| `photoeye_3` | `photoeye` | Bag Indexing Conveyor photoeye |
| `switch_4` | `switch` | Bag Indexing Conveyor switch |
| `training_accessory_5` | `trainingAccessory` | Bag Indexing Conveyor - bag product load |
| `training_accessory_6` | `trainingAccessory` | Bag Indexing Conveyor - reversible drive |
| `training_accessory_7` | `trainingAccessory` | Bag Indexing Conveyor - manual pause station |
| `switch_8` | `switch` | Bag Indexing Conveyor operator input |
| `switch_9` | `switch` | Bag Indexing Conveyor operator input |
| `indicator_10` | `indicator` | Bag Indexing Conveyor output indication |
| `indicator_11` | `indicator` | Bag Indexing Conveyor output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A bag is indexed between two sensors, paused for operator action, and restarted from a known direction.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The bag stops at the requested station and reverse motion is permitted only after pause_clear.
