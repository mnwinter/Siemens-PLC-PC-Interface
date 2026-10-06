# Lab 3.2 - Robot Cell Safe Restart help

Scene ID: `lab-3-02-robot-cell-safe-restart`  
Migrated source: `prototype/scenes/lab-3-02-robot-cell-safe-restart.plcscene`  
Scene contract: `res://scenes/migrated/lab-3-02-robot-cell-safe-restart.scene.json`

## Purpose

A robot cell requires a closed gate, reset edge, and ready status before motion may be requested.

The installed robot and static CNC are separated inside a four-sided wire-mesh
fence. The access leaf pivots outward; the coded actuator travels with that
leaf while the sensor stays on the latch post. GATE, RESET, READY and START
stations are outside the gate's complete swing area. The controller cabinet
replaces the unrelated pallet-fork prop in this scene only.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `gate_closed` | `BOOL` | **PC** | `False` |
| `reset_complete` | `BOOL` | **PC** | `False` |
| `robot_ready` | `BOOL` | **PC** | `False` |
| `motion_request` | `BOOL` | **PC** | `False` |
| `robot_enable` | `BOOL` | **PLC** | `False` |
| `cell_ready` | `BOOL` | **PLC** | `False` |

`reset_complete` retains its legacy symbolic name for existing projects. It is
now a momentary reset **request**, not latched proof of a completed safety
reset. `motion_request` is a separate momentary Start request. The PC never
writes `robot_enable` or `cell_ready`; the selected controller owns them.

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Toggle gate closed` | `toggle` | `gate_closed` |
| `Press reset (momentary)` | `pulse` | `reset_complete` |
| `Toggle robot ready` | `toggle` | `robot_ready` |
| `Press Start motion (momentary)` | `pulse` | `motion_request` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `gate_closed` | `switch_2` | `switch` |
| `reset_complete` | `switch_8` | `switch` |
| `robot_ready` | `switch_9` | `switch` |
| `robot_enable` | `indicator_3` | `indicator` |
| `cell_ready` | `indicator_10` | `indicator` |
| `robot_enable` | `robotArm_0` | `running` |
| `gate_closed` | `training_accessory_4` | `switch` (true = closed) |
| `motion_request` | `motion_request_station` | `switch` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `robotArm_0` | `robotArm` | Robot enable sweep |
| `machine_1` | `machine` | Enclosed CNC - static process equipment |
| `switch_2` | `switch` | Gate closed feedback |
| `indicator_3` | `indicator` | Robot enable command |
| `training_accessory_4` | `trainingAccessory` | Robot cell fence and hinged access gate |
| `training_accessory_5` | `trainingAccessory` | Gate sensor and moving coded actuator |
| `training_accessory_6` | `trainingAccessory` | Emergency-stop station - visual reference only |
| `training_accessory_7` | `trainingAccessory` | Robot controller cabinet |
| `switch_8` | `switch` | Momentary reset request |
| `switch_9` | `switch` | Robot ready feedback |
| `indicator_10` | `indicator` | Cell ready command |
| `motion_request_station` | `switch` | Separate robot motion Start request |

## Run the offline reference

1. Select this scenario in Built-in Simulator mode.
2. Use **File -> Open Ladder Agent Project...** and open
   `programs/examples/robot-cell-restart-reference.rpproj.json`. The file-open
   flow verifies and loads the editable ladder; its source scene is this lab.
3. Press the bottom **Run** button to start controller scans. Close the gate and
   set Robot Ready. Robot Enable and Cell Ready must remain false.
4. Press **Reset (momentary)**. Cell Ready becomes true; the robot stays stopped.
5. Press **Start motion (momentary)**. Robot Enable becomes true and the actual
   base-axis adapter sweeps through +/-55 degrees. The green command beacon
   follows the same output. This is illustrative motion, not a CNC transfer.
6. Open the gate or remove Robot Ready. Both outputs drop and the robot holds
   its current pose. Restoring the input alone cannot restart it: use a fresh
   Reset followed by a separate Start.
7. Bottom Stop drops the outputs and holds the robot. Run resumes scans but
   requires Reset and Start again. Bottom Reset restores the initial robot
   pose, open gate, false points, and stopped controller.

The scene's default lab template remains an exercise, so Run without a loaded
program does not supply the reference behavior. Standalone plant preview also
does not own a PLC program. If the robot remains still, first check that this
reference is loaded, scans are running, both permissives are true, and Reset
then Start have been pressed. Cell Ready alone is authorization, not motion.

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

The emergency-stop station is a visual reference prop with no declared E-stop
point or action. This reference tests symbolic reset/start sequencing only.
Gate feedback snaps between the authored endpoints; the geometric diagnostic
samples intermediate angles independently. No physical safety-rated circuit,
stopping distance, guard height/distance, wiring, robot program or access-door
interlock is validated here. The static CNC does not cut material in this lab.

`--audit-robot-restart` checks the saved reference with actual offline ladder
scans, reset/start edge rejection, permissive loss, Stop/Run/Reset, actuator
mounting, the full robot sweep (800 samples at 10 ms), and the 90-degree gate
swing (91 samples). Those are sampled geometry and simulator checks, not
continuous swept-volume or physical acceptance.

## Machine guide

A robot cell requires a closed gate, reset edge, and ready status before motion may be requested.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.

### Normal sequence

- Apply the requested input condition.
- Verify only the documented PLC outputs respond.

### Expected observations

- A restart request cannot enable motion until the gate is closed and the robot is ready.
