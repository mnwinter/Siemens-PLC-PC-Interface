# Lab 2.17 - Twin-Container Pallet Cell help

Scene ID: `lab-2-17-pallet-robot`  
Migrated source: `prototype/scenes/lab-2-17-pallet-robot.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-17-pallet-robot.scene.json`

## Purpose

A robot transfers two process containers from a staged pallet, then releases the empty pallet to the outbound conveyor.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `pallet_ready` | `BOOL` | **PC** | `True` |
| `robot_run` | `BOOL` | **PLC** | `False` |
| `conveyor_run` | `BOOL` | **PLC** | `False` |
| `placed_count` | `DINT` | **SIM** | `0` |
| `cell_color` | `STRING` | **SIM** | `amber` |
| `cycle_complete` | `BOOL` | **SIM** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start pallet unload` | `start` | `unload-cycle` |
| `Stop robot cell` | `stop` | `` |
| `Reset pallet cell` | `reset` | `` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `pallet_ready` | `pallet_ready_sensor` | `photoeye` |
| `robot_run` | `pallet_robot` | `running` |
| `conveyor_run` | `robot_pallet_conveyor` | `running` |
| `conveyor_run` | `robot_pallet_outbound` | `running` |
| `cell_color` | `robot_cell_status` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `robot_pallet_conveyor` | `conveyor` | Pallet staging conveyor |
| `robot_pallet_outbound` | `conveyor` | Empty pallet outbound conveyor |
| `robot_pallet_transfer_bridge` | `trainingAccessory` | Grounded pallet transfer bridge |
| `robot_pallet` | `box` | Staging pallet |
| `container_a` | `box` | Process container A |
| `container_b` | `box` | Process container B |
| `pallet_robot` | `robotArm` | Pallet unloading robot |
| `process_receiver` | `containerReceiver` | Container process receiver |
| `pallet_ready_sensor` | `photoeye` | Pallet ready sensor |
| `robot_cycle_start` | `switch` | Start robot cycle |
| `robot_cell_status` | `indicator` | Robot cell status |

## Stop and safety boundary

The staging pallet's bottom runners meet the 900 mm belt surface. Both
containers are seated on its deck, the receiver is clear of the conveyor,
and the photoeye stands and connected pigtails clear the conveyor braces.
The outbound conveyor shares the 900 mm carrying height, with a grounded
425 mm bridge deck between the belts. The 70/35 mm gaps at the flat belt
tangent points are narrower than each pallet runner. The standalone reference
release covers 8 m at 0.65 m/s and finishes with the whole pallet on the
outbound flat belt. Both conveyors use the existing `conveyor_run` command.
This geometric installation does not establish a complete robot transfer:
the reference container paths still miss the receiver bays and robot/load
attachment is unproven. Timed reference motion is separate from the normal
controller-owned shell and does not prove acceleration, slip or load capacity.
The reference contract verifies sequence point values, not physical handling.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `robot_run` | `False` |
| `conveyor_run` | `False` |
| `cell_color` | `red` |

## Machine guide

A robot transfers two process containers from a staged pallet, then releases the empty pallet to the outbound conveyor.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.
- The PLC is ready to command robot_run, conveyor_run.

### Normal sequence

- pick first
- place first
- pick second
- place second
- release pallet
- ready

### Expected observations

- Exactly two containers are placed before the pallet conveyor releases.
