# Lab 2.18 - Shipping Pallet Accumulation help

Scene ID: `lab-2-18-pallet-pickup`  
Migrated source: `prototype/scenes/lab-2-18-pallet-pickup.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-18-pallet-pickup.scene.json`

## Purpose

Automatic mode advances a loaded shipping pallet to the pickup photoeye; a separate jog sequence demonstrates manual positioning.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `auto_mode` | `BOOL` | **PC** | `True` |
| `conveyor_run` | `BOOL` | **PLC** | `False` |
| `pickup_sensor` | `BOOL` | **PC** | `False` |
| `pallet_position` | `REAL` | **SIM** | `0` |
| `status_color` | `STRING` | **SIM** | `amber` |
| `cycle_complete` | `BOOL` | **SIM** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle auto mode` | `togglePoint` | `auto_mode` |
| `Start automatic travel` | `start` | `automatic` |
| `Jog pallet one increment` | `start` | `manual` |
| `Stop conveyor` | `stop` | `` |
| `Reset pallet` | `reset` | `` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `auto_mode` | `pickup_mode` | `selector` |
| `conveyor_run` | `pickup_conveyor` | `running` |
| `pickup_sensor` | `pickup_end_sensor` | `photoeye` |
| `status_color` | `pickup_status` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `pickup_conveyor` | `conveyor` | Shipping pallet conveyor |
| `shipping_pallet` | `palletLoad` | Loaded shipping pallet |
| `pickup_end_sensor` | `photoeye` | Forklift pickup sensor |
| `pickup_mode` | `rotarySwitch` | Auto / manual selector |
| `auto_start` | `switch` | Automatic start |
| `manual_jog` | `switch` | Manual jog |
| `pickup_status` | `indicator` | Pickup conveyor status |

## Stop and safety boundary

The shipping pallet's three bottom boards sit on the 900 mm belt, fully
inside its flat carrying span throughout the automatic reference. Its root
starts at X=-3.6 m, Y=0.8625 m and ends at X=3.1 m. The first manual reference
moves to X=-1.925 m (25% of this route). The photoeye stands are 3.6 m apart,
grounded and clear of the conveyor hardware/cable bounds.

These placements were inspected in native Windows home, held mid-travel and
pickup views from five angles, with Stop/Reset. Geometry samples the automatic
route every 10 ms. The reference still has unresolved control behavior: Jog
is accepted in AUTO and repeats from the fixed start, pickup feedback is
timed and can remain true after jogging away, and configured/reference speeds
disagree. Reset before a single reference run avoids the repeated-start jump;
this workaround does not establish lesson acceptance or fix the runtime.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `conveyor_run` | `False` |
| `status_color` | `red` |

## Machine guide

Automatic mode advances a loaded shipping pallet to the pickup photoeye; a separate jog sequence demonstrates manual positioning.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.
- The PLC is ready to command conveyor_run.

### Normal sequence

- automatic travel
- pickup position

### Expected observations

- Auto stops at the pickup sensor; manual jog moves only one bounded increment.
