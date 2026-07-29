# Typed simulation update loop

The simulation update loop is the deterministic boundary between a future
scene/process model and the proven PLC runtime. It is implemented and tested
offline. It does not change DB14, the Snap7 transport, ownership rules, cycle
order, shutdown policy, or the PLC watchdog.

## Cycle order

Each call to `SimulationUpdateLoop.step()` performs these operations:

1. Validate and encode the supplied PC-owned scene point values.
2. Stage only conversions that produced a writable raw value.
3. Run one existing `InterfaceRuntime.cycle()`.
4. Decode every PLC-owned point from the values read during that cycle.
5. Combine point quality and heartbeat state into one loop health value.
6. Emit one JSON-lines record when a logger is configured.

The underlying PLC cycle remains:

1. read all configured PLC-owned tags;
2. evaluate the previously written heartbeat echo;
3. write dirty non-heartbeat PC-owned tags;
4. write the new PC heartbeat last.

That order is the live-proven behavior. The PLC echo is expected to be one
count behind the new heartbeat generated at the end of the current cycle.

## Stateful PC points

`pc_point_values` is a partial update, not a required complete image. If a
scene omits a PC-owned point during a later cycle, the last accepted point
value remains staged in the runtime.

At startup, every PC-owned point begins with the scene-facing interpretation
of its backing tag's validated `safe_value`.

Range behavior remains point-specific:

- `clamp`: stage the bounded raw value and report a warning;
- `fault`: do not stage a new raw value, retain the previous accepted value,
  and report an error containing `PLC write skipped`.

Unknown points, PLC-owned points supplied as inputs, and values of the wrong
type are programming errors. They raise before the PLC cycle instead of being
silently ignored.

## Loop health

| Health | Meaning |
|---|---|
| `starting` | Waiting for the first PLC heartbeat echo and no point issue exists |
| `healthy` | Heartbeat is progressing and every point has good quality |
| `degraded` | Heartbeat is usable, but at least one point was clamped |
| `fault` | Heartbeat stalled or at least one point has fault quality |

Priority is `fault`, `degraded`, `starting`, then `healthy`. A range error is
therefore visible even during initial heartbeat acquisition.

The loop health is diagnostic state. It does not replace the PLC-side
`Simulation_Comm_OK`, `Simulation_Timeout`, permissives, interlocks, or safety
logic.

## Result model

`UpdateResult` contains:

- the existing raw `CycleResult`;
- overall `LoopHealth`;
- the complete accepted PC point image, including any current rejected
  attempt;
- the complete PLC point image decoded from the current read;
- zero or more `PointDiagnostic` records.

Each point sample includes:

- scene-facing value;
- raw PLC value;
- point quality;
- engineering unit;
- backing tag name.

A PLC-owned analog value outside its configured point range preserves the bad
raw value while setting the engineering value to `null`. This makes the
actual PLC data available for troubleshooting without presenting a bad
engineering value as usable.

## JSON-lines logging

`JsonLinesUpdateLogger` accepts any text stream and writes one compact JSON
object per completed cycle. It does not choose a file path or manage log
rotation; those policies belong to the future application host.

Example composition:

```python
import time

from siemens_plc_pc_interface import (
    JsonLinesUpdateLogger,
    SimulationUpdateLoop,
)
from siemens_plc_pc_interface.runtime import InterfaceRuntime


def run_one_scene_cycle(
    runtime: InterfaceRuntime,
    log_stream,
    scene_inputs: dict[str, bool | int | float],
):
    """
    The caller owns runtime connection, explicit write authorization,
    cycle timing, shutdown, and the PLC-side Simulation_Enable command.
    """
    loop = SimulationUpdateLoop(
        runtime,
        logger=JsonLinesUpdateLogger(log_stream),
    )
    return loop.step(time.monotonic(), scene_inputs)
```

The JSON record contains:

```json
{
  "cycle": 2,
  "health": "healthy",
  "heartbeat": {
    "healthy": true,
    "reason": "echo_progressing",
    "last_echo": 1,
    "age_ms": 0
  },
  "pc_points": {},
  "plc_points": {},
  "diagnostics": []
}
```

Point dictionaries contain the configured point names and their current
sample data. The actual line is compact and key-sorted for predictable log
processing.

## Safety boundary

The update loop does not:

- connect automatically;
- authorize PLC writes;
- write physical `%I` or `%Q`;
- write PLC-owned tags;
- write the operator-controlled simulation enable;
- issue CPU RUN, STOP, reset, download, or hardware commands;
- replace the PLC watchdog or safe mapping.

Any future executable or scene host that can connect and write must retain an
explicit authorization equivalent to the current CLI `--execute` gate and
must print its exact configured DB write scope before connecting.

## Offline verification

The unit tests use an in-memory fake transport. They prove:

- startup and first-echo state;
- healthy point exchange;
- clamp/write/degraded behavior;
- fault/no-write behavior;
- bad PLC raw-value diagnostics;
- point ownership rejection;
- retained PC scene values;
- JSON-lines structure;
- heartbeat-stall faulting.

No PLC connection is attempted by these tests. The typed DB100 example remains
proposed architecture and must not be run with `--execute` until a matching
PLC DB and watchdog have been commissioned.

The first consumer of this result model is documented in
[Reusable simulation components](COMPONENTS.md).
