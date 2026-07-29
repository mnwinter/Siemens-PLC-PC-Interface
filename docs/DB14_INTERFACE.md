# DB14 simulation interface

## Data block requirements

Create `DB_SimulationProof` as DB14 with optimized block access disabled.
The validated layout is:

| Absolute address | Symbol | Type | Owner |
|---|---|---|---|
| `DB14.DBX0.0` | `PC_To_PLC` | `Bool` | PC writes |
| `DB14.DBX0.1` | `PLC_To_PC` | `Bool` | PLC writes |
| `DB14.DBD2` | `PC_Heartbeat` | `DInt` | PC writes |
| `DB14.DBD6` | `PLC_Heartbeat_Echo` | `DInt` | PLC writes |
| `DB14.DBX10.0` | `Simulation_Enable` | `Bool` | Operator/PLC writes |
| `DB14.DBX10.1` | `Simulation_Comm_OK` | `Bool` | PLC writes |
| `DB14.DBX10.2` | `Simulation_Timeout` | `Bool` | PLC writes |

The PC runtime reads the final three fields but does not write them.
`Simulation_Enable` is an operator-controlled mode request. It is deliberately
not a remote PC command because communications must not enable their own
authority.

## PLC watchdog

The proven PLC implementation uses `Simulation_Watchdog [FB3]` with a
single-instance DB, `Simulation_Watchdog_DB [DB5]`.

Interface:

| Section | Name | Type |
|---|---|---|
| Input | `Simulation_Enable` | `Bool` |
| Input | `PC_Heartbeat` | `DInt` |
| Input | `Watchdog_Time` | `Time` |
| Output | `PLC_Heartbeat_Echo` | `DInt` |
| Output | `Simulation_Comm_OK` | `Bool` |
| Output | `Simulation_Timeout` | `Bool` |
| Static | `Last_Heartbeat` | `DInt` |
| Static | `Heartbeat_Seen` | `Bool` |
| Static | `Heartbeat_Timer` | `TON_TIME` |
| Temp | `Heartbeat_Changed` | `Bool` |

The implementation performs these operations in order:

1. Compare `PC_Heartbeat <> Last_Heartbeat`.
2. On a change, store the new heartbeat in `Last_Heartbeat`.
3. On a change, copy the heartbeat to `PLC_Heartbeat_Echo`.
4. On a change, set `Heartbeat_Seen`.
5. Run a `TON` while a heartbeat has been seen but is no longer changing.
6. Set `Simulation_Comm_OK` only while simulation is enabled, a heartbeat has
   been seen, and the timer is not done.
7. Set `Simulation_Timeout` while simulation is enabled and communication is
   not OK.

The proven watchdog time is `T#2s`.

## Safe PLC mapping

The proof Boolean feedback is gated by the PLC watchdog:

```text
PLC_To_PC := Simulation_Comm_OK AND PC_To_PLC
```

For a larger simulation, apply the same principle to every simulated input:
the PLC mapping layer must select a safe or physical source when
`Simulation_Comm_OK` is false. Do not rely on a final PC write during cable
loss; that write may never reach the PLC.

## Ownership rule

- The PC writes only `PC_To_PLC` and `PC_Heartbeat`.
- The PLC writes `PLC_To_PC`, `PLC_Heartbeat_Echo`,
  `Simulation_Comm_OK`, and `Simulation_Timeout`.
- The operator/PLC controls `Simulation_Enable`; the PC only reads it.
- Neither side writes fields owned by the other side.

This separation avoids competing writers and makes the failure behavior
deterministic.

### Adjacent Boolean limitation

The validated proof places the PC-owned `DBX0.0` and PLC-owned `DBX0.1` in the
same byte. A client Boolean write can require a byte read/modify/write. The PC
runtime therefore writes `PC_To_PLC` only when its value changes rather than
rewriting it every cycle.

For a larger production mapping, group PC-owned and PLC-owned Boolean fields
in separate bytes. That removes cross-owner byte-level races and enables
efficient grouped transfers.

## Proven failure behavior

On 2026-07-24, the real CPU 1512SP-1 PN passed these live checks:

1. With simulation enabled and no progressing heartbeat,
   `Simulation_Comm_OK = false` and `Simulation_Timeout = true`.
2. Changing `PC_Heartbeat` to `1` produced
   `PLC_Heartbeat_Echo = 1`.
3. After the heartbeat stopped for two seconds, the PLC returned to
   `Simulation_Comm_OK = false` and `Simulation_Timeout = true`.
4. With `PC_To_PLC = true` during that timeout, `PLC_To_PC` remained false.

This proves the PLC-side timeout and output gate.

On 2026-07-29, the packaged continuous PC runtime also passed the live
hardware test. With simulation enabled and the heartbeat progressing,
`Simulation_Comm_OK` and the gated `PLC_To_PC` became true. When the runtime
stopped, the safe values were written successfully and the PLC returned to
`Simulation_Comm_OK = false`, `Simulation_Timeout = true`, and
`PLC_To_PC = false`.

The echo normally trails the newly generated heartbeat by one count because
the runtime reads PLC-owned values before writing the next PC-owned
heartbeat.

## Production expansion

Do not expand this interface by directly writing `%I` or `%Q`. Add separately
owned fields to a dedicated simulation DB, validate their types and offsets,
and map them through PLC logic with normal permissives, interlocks, and
machine-safe fallback behavior.
