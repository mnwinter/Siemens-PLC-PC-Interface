# Reusable simulation components

Reusable components are deterministic offline process models that sit above
the typed simulation update loop. They model equipment behavior; they do not
connect to a PLC, authorize writes, change DB addresses, or replace PLC
permissives, interlocks, watchdogs, and safety logic.

The first component is a single-object conveyor with one photoeye. The second
builds on that same conveyor model with a single-solenoid pusher and two
simulated limit switches.

## Conveyor/photoeye assumptions

`ConveyorPhotoeye` is intentionally small:

- motion is one-dimensional and forward only;
- conveyor speed is constant while the run command is true;
- one object can be on the conveyor at a time;
- the object is represented by its leading edge and configured length;
- one photoeye is positioned along the conveyor;
- product loading and scene reset are host/operator simulation actions;
- the PLC supplies the run command through a PLC-owned typed point;
- the component supplies the photoeye through a PC-owned typed point.

This is process simulation, not a motor, drive, or safety model. Acceleration,
slip, accumulation, jams, multiple products, reverse motion, and collision
physics are outside the first component.

## Physical configuration

```python
from siemens_plc_pc_interface import (
    ConveyorPhotoeye,
    ConveyorPhotoeyeConfig,
)

conveyor = ConveyorPhotoeye(
    ConveyorPhotoeyeConfig(
        length_m=1.0,
        speed_m_per_s=0.5,
        object_length_m=0.2,
        photoeye_position_m=0.5,
        minimum_photoeye_on_s=0.1,
    )
)
```

Validation rejects:

- zero, negative, nonnumeric, or nonfinite lengths and speeds;
- an object longer than the conveyor;
- a photoeye outside the conveyor;
- a negative minimum photoeye on-time.

## Commands and states

Each `step()` receives:

- `run_command`: move the conveyor at configured speed;
- `reset_scene`: dominant scene reset that clears the object, photoeye hold,
  discharge event, and completion counter.

Explicit states are:

| State | Meaning |
|---|---|
| `reset` | Scene reset is applied; motor command is suppressed |
| `stopped_empty` | No product and run command is false |
| `running_empty` | No product and run command is true |
| `stopped_loaded` | Product present and run command is false |
| `running_loaded` | Product present and run command is true |

The snapshot also reports:

- motor running;
- object present;
- object leading-edge position in metres;
- photoeye blocked;
- one-cycle object discharged event;
- completed-object count.

## Product movement and discharge

`load_object()` places a single product with its leading edge at the infeed.
Loading a second product before the first leaves raises `ComponentError`
instead of creating an undefined overlap.

While running:

```text
new leading edge = old leading edge + speed * elapsed time
```

The object is discharged once its trailing edge reaches the configured
conveyor length. The object is then removed, `object_discharged` is true for
one update, and `completed_count` increments.

Negative, nonfinite, or invalid elapsed time is rejected. A zero-time step is
allowed for deterministic state evaluation without motion.

## Photoeye timing

The physical photoeye is blocked while its configured position lies between
the object's trailing and leading edges.

A simulation update can move the complete object across a narrow sensor
between two sample times. The component detects that swept crossing and holds
the simulated photoeye for `minimum_photoeye_on_s`. Set this value to at least
the interface cycle time when the PLC must observe one complete true update.

The default is `0.1` seconds. The first live-scene configuration uses a 20 ms
PLC exchange, so the default holds the sensor across several exchanges. This
is a simulation pulse-stretching feature, not a claim about a real sensor's
hardware response time.

## Typed point binding

`ConveyorPointBinding` maps the component to existing typed points without
duplicating raw PLC addresses:

```python
from siemens_plc_pc_interface import ConveyorPointBinding

binding = ConveyorPointBinding(
    run_command_point="conveyor_running",
    photoeye_point="simulated_photoeye",
)
```

The binding:

- reads `conveyor_running` from `UpdateResult.plc_point_samples`;
- requires a good Boolean sample;
- allows run during `healthy` or `degraded` loop health;
- forces run false during `starting`, `fault`, or bad command quality;
- converts the component snapshot to
  `{"simulated_photoeye": photoeye_blocked}` for the next update.

`degraded` remains usable because the update loop assigns that state to a
clamped point while heartbeat communication is still progressing. A loop
`fault` is fail-safe and suppresses the run command even if the last PLC
sample was true.

## Integration order

The component consumes the command from the previous completed PLC update and
publishes its sensor into the next update:

```python
from siemens_plc_pc_interface import ConveyorInputs

# Startup before the first healthy PLC result.
inputs = ConveyorInputs(run_command=False)

# Each deterministic host cycle:
snapshot = conveyor.step(dt_s, inputs)
result = update_loop.step(
    now,
    binding.pc_point_values(snapshot),
)
inputs = binding.inputs_from_update(result)
```

This creates an intentional one-update command/response delay, similar to
separate PLC and simulation scans. `SceneEngine` now owns fixed `dt_s`,
component ordering, point exchange, and product/reset events. `SceneRunner`
owns real-time deadlines and bounded timing statistics. See
[`FIRST_SCENE.md`](FIRST_SCENE.md).

## Reset behavior

`reset_scene` is a simulation reset, not a PLC fault-reset or safety reset.
It immediately:

- suppresses motor running even if `run_command` is true;
- removes the simulated product;
- clears the photoeye and its minimum-on hold;
- clears the discharge event;
- resets the completed count.

PLC-controlled machine reset behavior should remain in the PLC program and
should be exposed as a separate mapped command only when its intended
simulation behavior is defined.

## Conveyor/pusher component

`ConveyorPusher` reuses the complete `ConveyorPhotoeye` model and adds:

- one PLC-owned extend command;
- deterministic time-based extension and retraction;
- one PC-owned extended limit;
- one PC-owned retracted limit;
- product transfer when the extending pusher crosses its configured transfer
  position;
- an explicit one-cycle `object_transferred` event;
- fail-safe suppression of both PLC commands when loop health or point
  quality is bad.

The actuator is intentionally modeled as a single-solenoid, spring-return
pusher. Removing the extend command causes retraction; there is no separate
retract command.

```python
from siemens_plc_pc_interface import (
    ConveyorPhotoeyeConfig,
    ConveyorPusher,
    ConveyorPusherConfig,
)

pusher = ConveyorPusher(
    ConveyorPusherConfig(
        conveyor=ConveyorPhotoeyeConfig(
            length_m=1.0,
            speed_m_per_s=0.5,
            object_length_m=0.2,
            photoeye_position_m=0.5,
            minimum_photoeye_on_s=0.1,
        ),
        pusher_stroke_time_s=0.3,
        transfer_position_fraction=0.8,
    )
)
```

`ConveyorPusherPointBinding` uses five distinct digital points:

| Point role | Direction |
|---|---|
| Conveyor run command | PLC to PC |
| Pusher extend command | PLC to PC |
| Part-at-pusher photoeye | PC to PLC |
| Pusher extended limit | PC to PLC |
| Pusher retracted limit | PC to PLC |

The binding requires all five points to use the same interface group. The
scene validator prevents two components from writing the same PC-owned point.
See [`SCENE_2_PUSHER.md`](SCENE_2_PUSHER.md) for the standalone Scene 2 TIA
project, DB14 layout, ladder sequence, and live test.

## Safety boundary

The component layer does not:

- import or call Snap7;
- know the PLC IP, rack, slot, DB number, or absolute address;
- write physical `%I` or `%Q`;
- write any PLC-owned point;
- issue CPU commands;
- bypass the update loop's ownership and heartbeat diagnostics.

All current component proof is offline with unit tests. No claim is made that
the conveyor physics or typed DB100 example has been tested on PLC hardware.
