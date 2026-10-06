# Lab 2.24 - Robot CNC Tending Cell help

Scene ID: `lab-2-24-robot-cnc`  
Migrated source: `prototype/scenes/lab-2-24-robot-cnc.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-24-robot-cnc.scene.json`

## Purpose

The offline reference transfers one blank from infeed into the CNC enclosure
using the actual six robot joints and gripper, waits for a machining timer,
and places the same part on outfeed. It opens both sliding doors and retracts
the tool for transfer, then parks the robot before closing access for machining.

## Current installation and verification

The 400 x 140 x 252 mm billet rests on the 0.9 m conveyor deck. The robot stands
on the CNC's front access side. A bearing shoe connects the fixed vise base to
the billet's machining bottom at Y=1.66 m. The duplicate coupon is removed.
Staged waypoints lift stock clear of each belt, carry it along the machine
front, enter above the vise and lower it onto that support. Only gripped stock
follows the tool; release leaves it seated. Moving door rollers remain on their
extended supported track, and the coolant line clears the handling route.

The focused `--audit-robot-cnc` passes 23 checks over 45 seconds: actual attachment
and finger contact, belt/vise bearing, door/tool clearance at both aperture
crossings, machining reference state, sampled clearance, completion and
Stop/Reset/restart behavior. These sampled geometric checks do not prove robot
self-collision clearance, full swept volume or mechanical performance.
Pickup, readiness and machining completion still use timed reference states.
Normal selected-controller operation, feedback-driven door/clamp interlocks
and cutting/material removal remain unverified.

Native Windows home, held grip, held loaded entry and completed outfeed were
inspected from four diagonal views and Top. Front views supplement rear/roof
occlusion; held release showed stock remaining on its support. Stop retained a
loaded pose and blocked restart until Reset. A full subsequent reference cycle
completed. Held Step advances this joint adapter and explicit access motions,
but autonomous spindle animation stays frozen. Phase boundaries discard leftover
step time; do not use step counts as elapsed-time acceptance.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `infeed_run` | `BOOL` | **PLC** | `False` |
| `outfeed_run` | `BOOL` | **PLC** | `False` |
| `blank_at_pickup` | `BOOL` | **PC** | `False` |
| `robot_run` | `BOOL` | **PLC** | `False` |
| `cnc_ready` | `BOOL` | **PC** | `True` |
| `cnc_run` | `BOOL` | **PLC** | `False` |
| `machining_complete` | `BOOL` | **PC** | `False` |
| `status_color` | `STRING` | **SIM** | `amber` |
| `cycle_complete` | `BOOL` | **SIM** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start robot/CNC cycle` | `start` | `cnc-cycle` |
| `Stop cell safely` | `stop` | `` |
| `Reset CNC cell` | `reset` | `` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `infeed_run` | `cnc_infeed` | `running` |
| `outfeed_run` | `cnc_outfeed` | `running` |
| `blank_at_pickup` | `cnc_infeed_sensor` | `photoeye` |
| `robot_run` | `cnc_robot` | `running` |
| `cnc_run` | `cnc_machine` | `running` |
| `status_color` | `cnc_cell_status` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `cnc_infeed` | `conveyor` | CNC infeed conveyor |
| `cnc_outfeed` | `conveyor` | CNC outfeed conveyor |
| `cnc_workpiece` | `box` | Machining blank |
| `cnc_robot` | `robotArm` | CNC tending robot |
| `cnc_machine` | `machine` | CNC machining center |
| `cnc_infeed_sensor` | `photoeye` | Blank pickup sensor |
| `cnc_cell_start` | `switch` | Start CNC tending |
| `cnc_cell_status` | `indicator` | CNC cell status |

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `infeed_run` | `False` |
| `outfeed_run` | `False` |
| `robot_run` | `False` |
| `cnc_run` | `False` |
| `status_color` | `red` |

## Machine guide

The sequence below describes the tending reference. Its completion is timed;
normal controller and feedback-driven process acceptance remain open.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.
- The PLC is ready to command infeed_run, outfeed_run, robot_run, cnc_run.

### Normal sequence

- infeed blank
- pickup
- machining
- machine complete
- unload
- outfeed
- ready

### Expected observations

- Preview action moves the actual robot and attached stock through open access.
- Stock stays on the bearing shoe after release; the robot parks and doors close
  before `cnc_run` becomes true. The tool is retracted again before unloading.
- Stock is released onto outfeed and remains visible at the completed endpoint.
- Stop removes commands and holds the current pose. Restart requires Reset after
  interruption or completion. Reset restores stock, joints, doors and tool home.
- These observations prove reference presentation only; they do not establish
  actual clamping, sensed machining completion or PLC interlock operation.
