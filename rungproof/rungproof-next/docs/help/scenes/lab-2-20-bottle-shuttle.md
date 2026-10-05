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
| `motor_direction` | `STRING` | **PLC** | `stopped` |
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

Normal loaded-controller operation remains unresolved: `motor_direction` is
a legacy STRING command, while the current virtual and external controller
interfaces support BOOL/numeric outputs. Selecting a controller blocks the
standalone reference; it does not fabricate direction or overwrite commands.
Do not treat preview completion as normal controller or live-PLC acceptance.

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.

Declared simulation safe state:

| Point | Value |
| --- | --- |
| `motor_run` | `False` |
| `motor_direction` | `stopped` |
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
