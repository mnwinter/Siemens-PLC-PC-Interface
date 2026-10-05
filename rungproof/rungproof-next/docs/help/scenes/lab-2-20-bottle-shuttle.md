# Lab 2.20 - Bottle Shuttle Conveyor help

Scene ID: `lab-2-20-bottle-shuttle`  
Migrated source: `prototype/scenes/lab-2-20-bottle-shuttle.plcscene`  
Scene contract: `res://scenes/migrated/lab-2-20-bottle-shuttle.scene.json`

## Purpose

A reusable bottle travels to a right-hand sensor, reverses, returns to the left sensor, and stops.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `motor_run` | `BOOL` | **PLC** | `False` |
| `motor_direction` | `INT` | **PLC** | `0` |
| `left_sensor_active` | `BOOL` | **PC** | `True` |
| `right_sensor_active` | `BOOL` | **PC** | `False` |
| `status_color` | `STRING` | **SIM** | `amber` |
| `cycle_complete` | `BOOL` | **SIM** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Start bottle shuttle` | `start` | `round-trip` |
| `Stop shuttle` | `stop` | `` |
| `Reset bottle` | `reset` | `` |

## Equipment bindings

| Symbolic point | Equipment | Mode |
| --- | --- | --- |
| `motor_run` | `shuttle_conveyor` | `running` |
| `left_sensor_active` | `left_sensor` | `photoeye` |
| `right_sensor_active` | `right_sensor` | `photoeye` |
| `status_color` | `shuttle_status` | `indicator` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `shuttle_conveyor` | `conveyor` | Bottle shuttle conveyor |
| `shuttle_bottle` | `box` | Reusable process bottle |
| `left_sensor` | `photoeye` | Left end sensor |
| `right_sensor` | `photoeye` | Right end sensor |
| `shuttle_start` | `switch` | Start shuttle |
| `shuttle_status` | `indicator` | Shuttle status |

## Stop and safety boundary

The bottle body is seated at belt Y=0.9 m, with root Y=0.8270833333 m.
Both photoeye pairs have 3.2 m stand spans and grounded feet, clear of the
conveyor and neighboring control bounds. The PROCESS FLUID name and 1 L
capacity occupy separate label regions. Eight geometry checks include 121
route support samples and actual body-triangle endpoint rays; native home
and right endpoint were inspected from five angles.

The standalone preview now moves at the configured 0.75 m/s and drives
belt/drum animation from the same travel. Start preserves actual left feedback;
both sensors follow lens-to-lens intersections with the bottle body triangles.
The reference reverses at the right first-contact X=2.7688888321 m and stops
at the left first-contact X=-2.7688888321 m. Stop holds pose and leg; Run
resumes that leg. Reset returns X=-3 m. A fresh round trip takes about
15.08 simulated seconds. Reversal is instantaneous; no acceleration, slip
or bottle stability model is proven.

To inspect this reference, launch Godot with `-- --scene-id=lab-2-20-bottle-shuttle
--visual-plant-review`. It starts stopped and explicitly has no PLC controller.
Run, Stop and Reset work in that preview; Hold preview clock and Step 0.5 s
allow pose inspection. Expect 0.375 m travel per outward held half-second,
except a step containing a reversal or completion. Native Windows testing
covered both-leg Stop/resume, outward stepping, real-time completion and
five views of completed left and held right-side return poses.

Normal Built-in Simulator operation uses an editable reference project:
`programs/examples/02-bottle-shuttle-reference.rpproj.json`. Open Logic Editor,
choose Project → Open project and select that file. Opening it selects this
scene, verifies its I/O, and loads a stopped controller. Return to Scene, press
Run, then Start bottle shuttle. Run alone does not start a new machine cycle.
Stop shuttle (or bottom Stop) pauses playback and clears output commands;
Run resumes the retained outward/return step. Reset bottle resets both the
plant and controller memory, stops playback, and requires Run followed by Start.
After completion the controller continues scanning but the motor is stopped;
another Start begins at the completed pose without teleporting to home.

`motor_direction` changed from the legacy STRING to INT: **-1 = left,
0 = stopped, +1 = right**. Update previously authored symbolic bindings to
that type/encoding. No PLC profile or physical address mapping is supplied.
The controller owns reversal and stopping; the plant publishes actual optical
feedback each accepted scan and waits for the next scan's commands. At a
20 ms scan and 0.75 m/s, up to 15 mm travel separates first contact from the
next command. The eight-network reference stores a numeric travel step, not
fixed timers for the sensors. Its separate `operator.stop` input cancels the
cycle; playback Stop retains it. That input is available to authored logic,
and is not the same command as the scene's Stop shuttle action.

The plant is bounded to X=-3..3 m. A missed sensor cannot move the bottle off
the carrying belt: it holds at the route limit and reports red SIM status,
without changing the PLC-owned commands or claiming completion. Invalid
direction codes hold motion and also report red; 0 holds motion. Actual belt
travel and bottle travel use the same clock. Playback pause shows amber.
`cycle_complete` is a SIM observation of a right detection followed by a
stopped return at the left sensor; it is not a PLC acknowledgment or output.

The normal offline controller-to-plant round trip, both-leg Stop/Run, Reset,
repeat Start, sensor scan ordering and command ownership have deterministic
checks. Windows project opening and operator playback were also exercised.
Selecting a controller still blocks the standalone reference. These checks
do not establish external PLC profile compatibility or live commissioning.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `motor_run` | `False` |
| `motor_direction` | `0` |
| `status_color` | `red` |

## Machine guide

A reusable bottle travels to a right-hand sensor, reverses, returns to the left sensor, and stops.

### Start conditions

- The common PLC/watchdog foundation is healthy.
- All required simulator inputs are at their documented initial state.
- The PLC is ready to command motor_run, motor_direction.

### Normal sequence

- travel right
- right detected
- travel left
- left detected

### Expected observations

- Right sensor reverses travel; left sensor stops the completed round trip.
