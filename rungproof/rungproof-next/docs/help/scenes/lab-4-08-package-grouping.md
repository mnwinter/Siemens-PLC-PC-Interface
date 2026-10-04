# Lab 4.8 - Package Grouping Station help

Scene ID: `lab-4-08-package-grouping`  
Migrated source: `prototype/scenes/lab-4-08-package-grouping.plcscene`  
Scene contract: `prototype/scenes/lab-4-08-package-grouping.plcscene`

## Purpose

A conveyor groups a fixed number of cartons before releasing the group to the next station.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `package_detected` | `BOOL` | **PC** | `False` |
| `group_count_reached` | `BOOL` | **PC** | `False` |
| `release_clear` | `BOOL` | **PC** | `False` |
| `group_conveyor_run` | `BOOL` | **PLC** | `False` |
| `group_release` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle package detected` | `toggle` | `package_detected` |
| `Toggle group count reached` | `toggle` | `group_count_reached` |
| `Toggle release clear` | `toggle` | `release_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `package_detected` | `switch_8` | `switch` |
| `group_count_reached` | `switch_9` | `switch` |
| `release_clear` | `switch_10` | `switch` |
| `group_conveyor_run` | `indicator_3` | `indicator` |
| `group_release` | `indicator_11` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `conveyor_0` | `conveyor` | Package Grouping Station conveyor |
| `box_1` | `box` | Package Grouping Station box |
| `photoeye_2` | `photoeye` | Package Grouping Station photoeye |
| `indicator_3` | `indicator` | Package Grouping Station indicator |
| `training_accessory_4` | `trainingAccessory` | Package Grouping Station - powered roller conveyor |
| `training_accessory_5` | `trainingAccessory` | Package Grouping Station - package spacing sensor |
| `training_accessory_6` | `trainingAccessory` | Package Grouping Station - pallet receiver |
| `training_accessory_7` | `trainingAccessory` | Package Grouping Station - guided group stop |
| `switch_8` | `switch` | Package Grouping Station operator input |
| `switch_9` | `switch` | Package Grouping Station operator input |
| `switch_10` | `switch` | Package Grouping Station operator input |
| `indicator_11` | `indicator` | Package Grouping Station output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A conveyor groups a fixed number of cartons before releasing the group to the next station.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The release command occurs only after the target group count and downstream clear signal.
