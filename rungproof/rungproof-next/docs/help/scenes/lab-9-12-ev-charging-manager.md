# Lab 9.12 - EV Charging Manager help

Scene ID: `lab-9-12-ev-charging-manager`  
Migrated source: `prototype/scenes/lab-9-12-ev-charging-manager.plcscene`  
Scene contract: `prototype/scenes/lab-9-12-ev-charging-manager.plcscene`

## Purpose

A shared controller allocates charging permission and accumulates energy pulse events for occupied bays.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `bay_occupied` | `BOOL` | **PC** | `False` |
| `customer_authorized` | `BOOL` | **PC** | `False` |
| `charger_ready` | `BOOL` | **PC** | `False` |
| `charge_enable` | `BOOL` | **PLC** | `False` |
| `energy_session_active` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle bay occupied` | `toggle` | `bay_occupied` |
| `Toggle customer authorized` | `toggle` | `customer_authorized` |
| `Toggle charger ready` | `toggle` | `charger_ready` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `bay_occupied` | `switch_1` | `switch` |
| `customer_authorized` | `switch_8` | `switch` |
| `charger_ready` | `switch_9` | `switch` |
| `charge_enable` | `indicator_2` | `indicator` |
| `energy_session_active` | `indicator_10` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | EV Charging Manager machine |
| `switch_1` | `switch` | EV Charging Manager switch |
| `indicator_2` | `indicator` | EV Charging Manager indicator |
| `training_accessory_3` | `trainingAccessory` | EV Charging Manager - EV/charger bay |
| `training_accessory_4` | `trainingAccessory` | EV Charging Manager - connector latch |
| `training_accessory_5` | `trainingAccessory` | EV Charging Manager - energy meter |
| `training_accessory_6` | `trainingAccessory` | EV Charging Manager - pulse-output meter |
| `training_accessory_7` | `trainingAccessory` | EV Charging Manager - authorization reader |
| `switch_8` | `switch` | EV Charging Manager operator input |
| `switch_9` | `switch` | EV Charging Manager operator input |
| `indicator_10` | `indicator` | EV Charging Manager output indication |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

## Machine guide

A shared controller allocates charging permission and accumulates energy pulse events for occupied bays.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- Charging is enabled only for an occupied, authorized, ready bay.
