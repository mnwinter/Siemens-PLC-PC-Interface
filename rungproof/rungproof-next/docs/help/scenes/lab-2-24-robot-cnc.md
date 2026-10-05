# Lab 2.24 - Robot CNC Tending Cell help

Scene ID: `lab-2-24-robot-cnc`  
Migrated source: `prototype/scenes/lab-2-24-robot-cnc.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-24-robot-cnc.scene.json`

## Purpose

The intended process transfers a blank from an infeed conveyor into a CNC enclosure, waits for machining, and places the part on an outfeed conveyor. The current timed reference does not implement an attached robot transfer or door interlocks.

## Current installation and unresolved transfer

The single 400 x 140 x 252 mm billet rests on the 0.9 m conveyor deck. The
robot is installed on the CNC's front access side. At the machining target,
a bearing shoe connects the existing vise base to the billet's Y=1.66 m
bottom; its footprint fills the space between the delivered jaw faces.
The machine vise remains fixed and the duplicate coupon has been removed.

The focused `--audit-robot-cnc` currently passes 11 of 14 checks and exits 1.
Three failures remain: the stock is detached from the gripper during transfer,
the straight transfer penetrates machine parts, and it passes through closed
doors. Pickup/readiness/completion feedback is still timed. These failures
must be repaired before accepting the intended process; normal controller
operation, clamping and cutting/material removal are unverified.

Native Windows home and outfeed positions were inspected from four diagonal
views and Top, plus held pickup and front machine detail views. Doors, the
roof and robot obscure parts of the vise. The diagnostic measures bearing
contact separately. Held preview Step advances the sequence but freezes the
generic robot/spindle animation; release the clock to observe that motion.

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

The sequence below describes the intended tending process. The current timed
preview has the transfer failures documented above and is not process acceptance.

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

- The timed preview sets `cnc_run` while `robot_run` is false, then sends the
  billet to outfeed. These point values alone do not prove robot withdrawal,
  door closure, clamping or machining completion.
