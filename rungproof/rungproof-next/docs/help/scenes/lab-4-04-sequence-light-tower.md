# Lab 4.4 - Sequence Light Tower help

Scene ID: `lab-4-04-sequence-light-tower`  
Migrated source: `prototype/scenes/lab-4-04-sequence-light-tower.plcscene`  
Scene contract: `res://scenes/migrated/lab-4-04-sequence-light-tower.scene.json`

## Purpose

A four-color tower advances **red -> amber -> green -> blue -> off** on
separate momentary Step requests. The sequence tower has four physical lens
tiers; the separate single green beacon indicates completion. The CNC is
static process equipment, not an actuator in this indication exercise.

## Expected I/O to operate this scene

These are symbolic scene points, not PLC hardware addresses. PC-owned requests
are sampled by the selected controller. PLC-owned commands are projected onto
the tower; the scene does not create its own output sequence.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `sequence_start` | `BOOL` | **PC** | `False` |
| `sequence_step_due` | `BOOL` | **PC** | `False` |
| `tower_active` | `BOOL` | **PLC** | `False` |
| `sequence_complete` | `BOOL` | **PLC** | `False` |
| `tower_red` | `BOOL` | **PLC** | `False` |
| `tower_amber` | `BOOL` | **PLC** | `False` |
| `tower_green` | `BOOL` | **PLC** | `False` |
| `tower_blue` | `BOOL` | **PLC** | `False` |

The legacy `sequence_step_due` name now represents a momentary operator Step
request; it is not timer-complete feedback. `tower_active` is sequence status,
not a substitute for the four individual color commands. Existing two-output
programs still bind, but cannot produce the full four-color sequence.

## Operator actions

| Action | Type | Bound point |
| --- | --- | --- |
| `Press sequence Start (momentary)` | `pulse` | `sequence_start` |
| `Press sequence Step (momentary)` | `pulse` | `sequence_step_due` |

Action IDs `toggle-sequence_start` and `toggle-sequence_step_due` remain for
existing references; their behavior is now momentary. Each accepted click
appears high for a controller scan, then clears.

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `sequence_start` | `switch_1` | `switch` |
| `sequence_step_due` | `switch_3` | `switch` |
| `tower_red` | `indicator_2` | `indicatorChannel` (red) |
| `tower_amber` | `indicator_2` | `indicatorChannel` (amber) |
| `tower_green` | `indicator_2` | `indicatorChannel` (green) |
| `tower_blue` | `indicator_2` | `indicatorChannel` (blue) |
| `sequence_complete` | `indicator_4` | `indicator` (green) |

`indicatorChannel` changes only the named lens. Simultaneous commands light
simultaneous tiers so incorrect controller outputs remain visible. The normal
exclusive `indicator` behavior used by other scenes remains unchanged.

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `machine_0` | `machine` | Static process equipment |
| `switch_1` | `switch` | Momentary sequence Start |
| `indicator_2` | `indicator` | Four-color sequence tower |
| `switch_3` | `switch` | Momentary sequence Step |
| `indicator_4` | `indicator` | Sequence complete status |

## Run the offline reference

1. Select this scenario in Built-in Simulator mode. Use **File -> Open Ladder
   Agent Project...** to open
   `programs/examples/sequence-light-tower-reference.rpproj.json`.
2. Return to the scene and press the bottom **Run** button to start scans.
   All tower tiers must remain off. Step before Start has no effect.
3. Press the scene **Start** request. Red lights and `tower_active` becomes true.
4. Press **Step** four separate times: amber, green, blue, then all tower tiers
   off. The separate completion beacon lights after the fourth Step. Idle
   scans do not advance; Start during an active sequence is ignored.
5. Extra Step presses after completion have no effect. A fresh Start clears
   completion and begins again at red.
6. Bottom **Stop** removes all commands. **Run** alone or Step cannot resume
   the old color; a fresh Start resets the sequence to red.
7. Bottom **Reset** clears the counter, both requests, all commands and lenses,
   and leaves controller scans stopped.

The default lab template remains an exercise and does not automatically load
this reference. If no lamps respond, first verify that this reference is
loaded and the scan number is increasing, then press the scene Start request.
If a Step skips colors, inspect rising-edge handling and the counter value.

## Machine guide

The reference samples Start and Step edges before state permissives, accepts
Start only when inactive, clears the old counter, and counts active Step
requests to a preset of four. Four comparisons decode one color per active
state. Completion is separate status, so "tower off" means all four sequence
tiers off; the completion beacon remains on until a new Start, Stop or Reset.

## Stop and safety boundary

`--audit-sequence-tower` checks four physical tiers, initial/off and independent
lamp materials, saved reference equality, actual offline scans, one advance per
press, idle holding, request rejection, completion and Stop/Run/Reset behavior.
It does not prove physical wiring, PLC watchdog behavior, buzzer operation,
machine motion or live-PLC acceptance. The sounder geometry has no command in
this lesson. No hardware address or validated DB14 member is changed.
