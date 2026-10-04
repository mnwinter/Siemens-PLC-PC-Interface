# Lab 11.13 - XY Palletizing Cell help

Scene ID: `lab-11-13-xy-palletizing`  
Migrated source: `prototype/scenes/lab-11-13-xy-palletizing.plcscene`  
Scene contract: `res://scenes/migrated/lab-11-13-xy-palletizing.scene.json`

## Purpose

Symbolic palletizing cell: manual carton/home/pallet permissives drive XY gantry
command motion and a four-pick layer count. Reset starts a new layer. The XYZ
sweep illustrates the command; it does not place cartons or generate position
or pick-complete feedback.

The white pallet is centered inside the four gantry posts and rests on the base
slab. The carton rests on the 1.055 m conveyor deck; the carrying belt is 1.4 m wide. The orange tool follows the X/Y/Z
command offsets with its Z axis; Stop holds that attached pose and Reset
restores it. The separate vacuum-gripper model remains an illustrative accessory.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `carton_at_pick` | `BOOL` | **PC** | `False` |
| `gantry_home` | `BOOL` | **PC** | `False` |
| `pallet_position_valid` | `BOOL` | **PC** | `False` |
| `vacuum_pick` | `BOOL` | **PLC** | `False` |
| `gantry_cycle` | `BOOL` | **PLC** | `False` |
| `layer_complete` | `BOOL` | **PLC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle carton at pick` | `toggle` | `carton_at_pick` |
| `Toggle gantry home` | `toggle` | `gantry_home` |
| `Toggle pallet position valid` | `toggle` | `pallet_position_valid` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `carton_at_pick` | `switch_9` | `switch` |
| `gantry_home` | `switch_10` | `switch` |
| `pallet_position_valid` | `switch_11` | `switch` |
| `vacuum_pick` | `indicator_3` | `indicator` |
| `gantry_cycle` | `indicator_12` | `indicator` |
| `gantry_cycle` | `training_accessory_4` | `running` (XYZ command sweep) |
| `layer_complete` | `indicator_13` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `robotArm_0` | `robotArm` | XY Palletizing Cell robot Arm |
| `conveyor_1` | `conveyor` | XY Palletizing Cell conveyor |
| `box_2` | `box` | XY Palletizing Cell box |
| `indicator_3` | `indicator` | XY Palletizing Cell indicator |
| `training_accessory_4` | `trainingAccessory` | XY Palletizing Cell - XY gantry |
| `training_accessory_5` | `trainingAccessory` | XY Palletizing Cell - vacuum gripper |
| `training_accessory_6` | `trainingAccessory` | XY Palletizing Cell - pallet magazine |
| `training_accessory_7` | `trainingAccessory` | XY Palletizing Cell - carton load |
| `training_accessory_8` | `trainingAccessory` | Manual coordinate-permissive sensor pair |
| `switch_9` | `switch` | XY Palletizing Cell operator input |
| `switch_10` | `switch` | XY Palletizing Cell operator input |
| `switch_11` | `switch` | XY Palletizing Cell operator input |
| `indicator_12` | `indicator` | XY Palletizing Cell output indication |
| `indicator_13` | `indicator` | XY Palletizing Cell output indication |

## Stop and safety boundary

Stop freezes playback. Loss of a pick permissive removes gantry and vacuum
commands on the next offline scan. Reset restores the pose, inputs and counters
without running. This scene has no authored E-stop input; it does not prove a
safety function, a real E-stop circuit, watchdog, or live commissioning.

## Machine guide

Demo 5 uses two FBs, two FCs, two DB declaration views, a 750-ms timer, a
four-pick counter, comparisons, arithmetic and a parallel actuator-status
branch. DB/interface fields are declarations; runtime values use project tags.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Run, enable gantry-home and pallet-position-valid, then present a carton.
- Hold carton-present for at least 750 ms to count one pick. Clear it before
  presenting the next carton. A held carton counts once.
- After four picks, layer-complete stays on and pick commands stop. Reset
  clears the completed layer and requires a new Run.

### Expected observations

- XYZ nodes move only while gantry-cycle is commanded and playback is running.
- Stop or loss of a pick permissive holds the command pose; Reset restores it.
- The manually supplied home permissive does not track the illustrated pose.
