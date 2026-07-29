# First scene: conveyor and photoeye

The first runnable scene is a deterministic, headless conveyor simulation. It
loads one product at the infeed, reads a PLC-owned conveyor run command, moves
the product at a fixed speed, and writes one simulated photoeye to the PLC.

This is the first runtime scene, not yet a graphical scene editor.

## Proven versus new

| Item | Status |
|---|---|
| CPU 1512SP-1 PN connection and DB14 read/write | Live proven |
| DB14 heartbeat and PLC watchdog | Live proven |
| DB14 addresses and ownership | Unchanged |
| Scene validation, fixed-step engine, and scheduler | Offline tested |
| 10 ms physics step | Offline tested |
| 20 ms PLC exchange | Configured and offline tested; not yet live proven |
| Conveyor scene against the real PLC | Requires commissioning test |

The scene does not write physical `%I` or `%Q`, CPU state, the operator
enable, or any PLC-owned field.

## Required PLC logic

The original DB14 proof rung was:

```text
PLC_To_PC := Simulation_Comm_OK AND PC_To_PLC
```

That rung is useful for a communication echo proof, but it is not valid
conveyor control. In the first scene:

- `PC_To_PLC` is the simulated photoeye;
- `PLC_To_PC` is the PLC conveyor run command.

If the proof echo rung is left unchanged, an initially clear photoeye produces
a false run command and the conveyor never starts.

For this first stop-at-photoeye sequence, replace only that proof rung with:

```text
PLC_To_PC := Simulation_Comm_OK AND NOT PC_To_PLC
```

Equivalent LAD:

```text
|----[ Simulation_Comm_OK ]----[/ PC_To_PLC ]----( PLC_To_PC )----|
```

This causes the PLC to command the conveyor while communication is healthy
and the photoeye is clear. The simulated product moves to the photoeye; the PC
sets `PC_To_PLC`; the PLC removes `PLC_To_PC`; and the product stops at the
sensor.

Do not use this proof sequence as production machine logic. Real permissives,
mode selection, safety, faults, and reset behavior remain PLC responsibilities.

## Files

The PLC interface and scene are deliberately separate:

- `examples/db14-conveyor-interface.json` contains IP, DB14 addresses, types,
  ownership, heartbeat, and typed point names.
- `examples/conveyor-scene.json` contains only simulation components,
  physical parameters, point bindings, and scheduled scene events.

The scene file has no PLC IP or DB address.

## Timing

The first configuration uses:

| Setting | Value |
|---|---:|
| Fixed physics step | 10 ms |
| PLC exchange period | 20 ms |
| Physics steps per PLC exchange | 2 |
| PLC heartbeat timeout | 1000 ms |
| PLC watchdog time | 2 s |
| Simulated photoeye minimum on-time | 100 ms |

The PC exchange is not synchronized to the PLC scan. A 20 ms PC period means
the external S7 client attempts one exchange every 20 ms; it does not force
the PLC to use a 20 ms scan. The scheduler reports average, maximum, p99, and
deadline-overrun counts so the rate can be judged from measured behavior.

Do not reduce the PC exchange to 10 ms until the 20 ms run has zero or rare
overruns on the target VM. The current transport performs typed tag operations
individually, so network and Snap7 overhead can be materially longer than the
PLC program scan.

## Offline validation

From the repository:

```powershell
$env:PYTHONPATH = "src"
py -3 -m siemens_plc_pc_interface scene-validate `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene.json
```

Expected:

```text
SCENE_VALID: True
PLC_EXCHANGE_MS: 20
PHYSICS_STEP_MS: 10
PHYSICS_STEPS_PER_EXCHANGE: 2
COMPONENTS: 1
PLC_CONNECTION_ATTEMPTED: False
```

Preview the guarded live command:

```powershell
py -3 -m siemens_plc_pc_interface scene-run `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene.json `
    --cycles 250
```

This also does not connect. It prints the exact write scope and exits with code
2 because `--execute` was intentionally omitted.

## Live commissioning sequence

Before running:

1. Put the equipment in an approved safe test state.
2. Confirm DB14 remains standard/non-optimized and its offsets match the
   interface file.
3. Compile and download the revised first-scene PLC command rung.
4. Confirm the watchdog FB is still called unconditionally.
5. Open the DB14 watch table.
6. Set `Simulation_Enable = true` in TIA Portal.

Run 250 exchanges, approximately five seconds:

```powershell
$env:PYTHONPATH = "src"
py -3 -m siemens_plc_pc_interface scene-run `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene.json `
    --execute `
    --cycles 250 `
    --write-safe-state-on-exit
```

Expected progression:

1. Cycle 1 reports `starting`; the heartbeat has not been echoed yet.
2. A later cycle reports `healthy` and `PLC_To_PC = true`.
3. The conveyor position increases by approximately `0.01 m` per 20 ms
   exchange while running.
4. Near a `0.5 m` leading-edge position, `PC_To_PLC` becomes true.
5. The PLC sets `PLC_To_PC` false and the product stops over the photoeye.
6. The command ends with `HEARTBEAT_PROOF: PASS`.
7. Timing reports the 20 ms exchange workload.
8. Cleanup reports `SAFE_STATE_WRITE: PASS`.

After the test, set `Simulation_Enable = false`.

## Failure symptoms

| Symptom | First check |
|---|---|
| Conveyor never starts but heartbeat is healthy | Confirm the proof echo rung was replaced with `Comm_OK AND NOT photoeye` |
| `SCENE_INVALID` | Read the exact field/ownership message; validation occurs before connection |
| First cycle is `starting` | Normal; the PLC echo acknowledges the preceding heartbeat |
| Persistent `fault` or `Simulation_Timeout = true` | Check heartbeat echo progression and DB14 watchdog call |
| Frequent timing overruns | Keep 20 ms or increase it; do not force 10 ms |
| Product stops at photoeye | Expected first-scene behavior |
| Photoeye never changes | Confirm the product position advances and DB14.DBX0.0 is not forced |
| `PLC_To_PC` remains false | Check `Simulation_Enable`, `Simulation_Comm_OK`, and the revised rung |

## Scene JSON contract

The first schema allowlists only:

- component type `conveyor_photoeye`;
- event actions `load_object` and `reset_scene`;
- digital PLC-to-PC `run_command` bindings;
- digital PC-to-PLC `photoeye` bindings.

Component IDs must be unique. A PC-owned sensor point can have only one scene
writer. Event times must align to the fixed physics step. The PLC exchange
period must be an exact multiple of the physics step.

Arbitrary Python class names or actions are rejected.
