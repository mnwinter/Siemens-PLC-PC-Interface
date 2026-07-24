# DB14 simulation interface

## Data block requirements

Create `DB_SimulationProof` as DB14 with optimized block access disabled.
The validated layout is:

| Offset | Symbol | Type | Direction |
|---|---|---|---|
| `0.0` | `PC_To_PLC` | `Bool` | PC to PLC |
| `0.1` | `PLC_To_PC` | `Bool` | PLC to PC |
| `2.0` | `PC_Heartbeat` | `DInt` | PC to PLC |
| `6.0` | `PLC_Heartbeat_Echo` | `DInt` | PLC to PC |

The resulting absolute addresses are:

```text
DB14.DBX0.0  PC_To_PLC
DB14.DBX0.1  PLC_To_PC
DB14.DBD2    PC_Heartbeat
DB14.DBD6    PLC_Heartbeat_Echo
```

## PLC proof logic

The PLC proof requires two operations called cyclically:

```text
PLC_To_PC := PC_To_PLC
PLC_Heartbeat_Echo := PC_Heartbeat
```

In LAD, use a normally open `PC_To_PLC` contact driving the `PLC_To_PC` coil,
and a `MOVE` from `PC_Heartbeat` to `PLC_Heartbeat_Echo`.

## Ownership rule

- The PC writes only `PC_To_PLC` and `PC_Heartbeat`.
- The PLC writes only `PLC_To_PC` and `PLC_Heartbeat_Echo`.
- Neither side should write the other side's fields.

This separation avoids two writers fighting over the same memory.

## Diagnostic sequence

The guarded round-trip test:

1. Reads and stores the original PC-owned values.
2. Writes `true` and `24072401`.
3. Verifies both PLC echoes.
4. Writes `false` and `24072402`.
5. Verifies both PLC echoes.
6. Restores and verifies the original PC-owned values.

The `--hold-seconds 5` option keeps each state visible in a monitoring TIA
watch table.

## Production expansion

Do not expand this proof by directly writing `%I` or `%Q`. Add separately
owned fields to a dedicated simulation DB, validate their types and offsets,
and map them through PLC logic with normal permissives and interlocks.
