# Lab 11.13 - XY Palletizing Cell help

Scene ID: `lab-11-13-xy-palletizing`  
Migrated source: `prototype/scenes/lab-11-13-xy-palletizing.plcscene`  
Scene contract: `res://scenes/migrated/lab-11-13-xy-palletizing.scene.json`

## Purpose

Demo 5 transfers four cartons from a supported pickup table to four separate
positions on the white pallet. Its ladder has two FBs, two FCs, two DB declaration
views, a 750 ms pickup timer, a placement counter, comparisons and arithmetic.
DB/interface members are declarations; project tags hold runtime values.

Run enables the offline controller. Start commands one carton transfer. The
first carton is preloaded; Load stages each subsequent carton at the home
station. That action is blocked while occupied, moving, faulted, or complete.

## Expected I/O to operate this scene

All points are symbolic. PC owns plant feedback and operator requests; PLC owns
actuator commands. No physical I/O addresses or PLC connection are required.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `carton_at_pick` | `BOOL` | **PC** | `True` |
| `gantry_home` | `BOOL` | **PC** | `True` |
| `pallet_position_valid` | `BOOL` | **PC** | `True` |
| `vacuum_pick` | `BOOL` | **PLC** | `False` |
| `gantry_cycle` | `BOOL` | **PLC** | `False` |
| `layer_complete` | `BOOL` | **PLC** | `False` |
| `start_command` | `BOOL` | **PC** | `False` |
| `at_pickup` | `BOOL` | **PC** | `False` |
| `at_place` | `BOOL` | **PC** | `False` |
| `carton_attached` | `BOOL` | **PC** | `False` |
| `pick_complete` | `BOOL` | **PC** | `False` |
| `cycle_in_progress` | `BOOL` | **PC** | `False` |
| `palletizer_fault` | `BOOL` | **PC** | `False` |
| `placed_cartons` | `DINT` | **PC** | `0` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start / resume one carton` | `pulse` | `start_command` |
| `Load next carton at pickup` | `palletizerLoad` | `` |
| `Toggle pallet permissive` | `toggle` | `pallet_position_valid` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `pallet_position_valid` | `switch_11` | `switch` |
| `vacuum_pick` | `indicator_3` | `indicator` |
| `gantry_cycle` | `indicator_12` | `indicator` |
| `layer_complete` | `indicator_13` | `indicator` |
| `start_command` | `switch_9` | `switch` |

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
| `training_accessory_8` | `trainingAccessory` | Conveyor-to-gantry pickup table |
| `switch_9` | `switch` | XY Palletizing Cell operator input |
| `switch_10` | `switch` | XY Palletizing Cell operator input |
| `switch_11` | `switch` | XY Palletizing Cell operator input |
| `indicator_12` | `indicator` | XY Palletizing Cell output indication |
| `indicator_13` | `indicator` | XY Palletizing Cell output indication |

## Normal sequence

1. Run, then Start. The gantry lowers to the preloaded carton.
2. At the pickup contact, the ladder waits 750 ms before enabling vacuum.
3. The attached carton follows the raised tool to its assigned pallet slot.
4. At the supported placement height, the ladder releases vacuum. The carton
   remains on the pallet while the gantry lifts and returns home.
5. `pick_complete` remains latched until the next accepted cycle so Load cannot
   erase completion between scans. It counts placement and home return. Load then
   Start cartons 2-4. After the fourth return, `layer_complete` stays on and the
   four cartons remain visible. Reset restores one pickup carton and an empty pallet.

`gantry_home`, `at_pickup`, `at_place`, `carton_attached`, `pick_complete`,
`cycle_in_progress` and `placed_cartons` come from the plant state. They are
not manually fabricated switch inputs. Pallet-valid remains an operator
permissive, not a measured pallet alignment sensor.

## Stop and fault behavior

Stop freezes the offline pose and attachment, preserves placed cartons, and
clears commands. Run alone holds; a fresh Start resumes the held transfer.
Loss of pallet-valid removes commands. Restoring it also requires Start.
Vacuum loss during a commanded carry latches `palletizer_fault`; Reset clears it.

Pause retains attachment as an offline kinematic policy. This model does not
simulate vacuum pressure, gravity/drop, force, deforming cartons, collision
response, automatic conveyor feeding, or a safety function. The surrounding
robot, separate vacuum-gripper exhibit and loaded-pallet exhibit are static.

## Visual review controls

`--visual-scene-review` adds Hold offline plant clock and Step 0.5 s. Each step
runs 25 actual 20 ms scans through input, ladder, output and plant integration.
The review controls share the plant clock; no second gantry sweep runs.
