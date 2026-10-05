# Lab 4.7 - Parking Garage Entry help

Scene ID: `lab-4-07-parking-garage-entry`  
Migrated source: `prototype/scenes/lab-4-07-parking-garage-entry.plcscene`  
Scene contract: `res://scenes/migrated/lab-4-07-parking-garage-entry.scene.json`

## Purpose

Manual entry, space-available and exit-clear inputs form a parking barrier logic exercise. The occupancy readout is static; vehicle tracking and an occupancy count are not modeled.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `entry_detected` | `BOOL` | **PC** | `False` |
| `space_available` | `BOOL` | **PC** | `False` |
| `exit_clear` | `BOOL` | **PC** | `False` |
| `barrier_open` | `BOOL` | **PLC** | `False` |
| `garage_available` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle entry detected` | `toggle` | `entry_detected` |
| `Toggle space available` | `toggle` | `space_available` |
| `Toggle exit clear` | `toggle` | `exit_clear` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `entry_detected` | `switch_7` | `switch` |
| `space_available` | `switch_8` | `switch` |
| `exit_clear` | `switch_9` | `switch` |
| `barrier_open` | `indicator_3` | `indicator` |
| `garage_available` | `indicator_10` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `rollerShutter_0` | `rollerShutter` | Parking Garage Entry roller Shutter |
| `photoeye_1` | `photoeye` | Parking Garage Entry photoeye |
| `photoeye_2` | `photoeye` | Parking Garage Entry photoeye |
| `indicator_3` | `indicator` | Parking Garage Entry indicator |
| `training_accessory_4` | `trainingAccessory` | Parking Garage Entry - vehicle/load asset |
| `training_accessory_5` | `trainingAccessory` | Parking Garage Entry - parking barrier arm |
| `training_accessory_6` | `trainingAccessory` | Parking Garage Entry - occupancy counter display |
| `switch_7` | `switch` | Parking Garage Entry operator input |
| `switch_8` | `switch` | Parking Garage Entry operator input |
| `switch_9` | `switch` | Parking Garage Entry operator input |
| `indicator_10` | `indicator` | Parking Garage Entry output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

Manual entry, space-available and exit-clear inputs form a parking barrier logic exercise. The occupancy readout is static; vehicle tracking and an occupancy count are not modeled.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- The barrier opens only when a vehicle is detected, a space is available, and the exit path is clear.
- The readout says NO LIVE VALUE and is not bound to a numeric point.