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
| Original 20 ms PLC exchange | Live functional test passed |
| Batched DB14 transport and throttled reporting | Live tested |
| 20/15/10/5 ms optimized rate sweep | Live tested; 20 ms passed |
| Conveyor scene against the real PLC | Live functional proof passed |

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
- `examples/conveyor-scene-fast.json` uses the same model with a 5 ms fixed
  physics step so 20, 15, 10, and 5 ms exchanges all align exactly.

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

The optimized runtime does not perform one S7 read per PLC tag. It reads the
five PLC-owned DB14 values with one contiguous DB read and performs the normal
heartbeat update with one DB write. A changing Boolean sensor still uses a
read/modify/write of byte 0 so PLC-owned `DB14.DBX0.1` is preserved. Periodic
console output defaults to every 25 cycles; health changes, component state
changes, cycle 1, and the final cycle are always printed.

### First live timing result

The first packaged 250-exchange test passed the functional heartbeat and
safe-state checks on 2026-07-29:

```text
HEARTBEAT_PROOF: PASS
SAFE_STATE_WRITE: PASS
TIMING: cycles=250 overruns=24 resyncs=2 average_ms=9.261 maximum_ms=14.780 p99_ms=13.332
```

The product reached the photoeye and stopped as designed. The transaction
durations remained below 15 ms, but the scheduler still missed 24 configured
20 ms deadlines and resynchronized twice. This result proves function, not a
hard real-time 20 ms guarantee. That package used individual tag operations
and printed a full JSON record every cycle. The optimized rate-sweep build
changes both sources of overhead, but its timing still requires a live test.

### Finding the fastest reliable rate

Use the optimized 5 ms physics profile and test one exchange period at a time:

| Order | Period | Cycles | Approximate duration |
|---:|---:|---:|---:|
| 1 | 20 ms | 250 | 5 s |
| 2 | 15 ms | 334 | 5 s |
| 3 | 10 ms | 500 | 5 s |
| 4 | 5 ms | 1000 | 5 s |

For each run require:

- `HEARTBEAT_PROOF: PASS`;
- `SAFE_STATE_WRITE: PASS`;
- zero `resyncs`;
- `p99_ms` and `maximum_ms` below the requested period;
- zero or rare overruns.

Stop descending when a rate fails those checks. The preceding rate is the
short-test candidate, not yet a hard real-time guarantee. Repeat that candidate
for a longer soak before using it as the project default. TIA online monitoring
and VM/host load should remain consistent between tests.

### Optimized live rate-sweep result

The optimized package was tested on 2026-07-29 from the Windows Server 2019 VM
against the real CPU 1512SP-1 PN:

| Period | Cycles | Overruns | Resyncs | Average | Maximum | p99 | Result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 20 ms | 250 | 0 | 0 | 3.701 ms | 9.660 ms | 6.758 ms | Pass |
| 15 ms | 334 | 5 | 3 | 3.482 ms | 50.055 ms | 7.835 ms | Fail |
| 10 ms | 500 | 32 | 7 | 4.304 ms | 56.674 ms | 18.209 ms | Fail |
| 5 ms | 1000 | 136 | 1 | 3.175 ms | 12.617 ms | 6.412 ms | Fail |

Every run retained `HEARTBEAT_PROOF: PASS` and `SAFE_STATE_WRITE: PASS`.
However, average duration is not sufficient for selecting the exchange rate.
The 15, 10, and 5 ms runs missed deadlines or resynchronized because of
Windows/VM long-tail scheduling delays. The 20 ms rate was the fastest
short-test candidate and was selected for the longer soak shown below.

The subsequent 30,000-cycle 20 ms soak reported:

```text
TIMING: cycles=30000 overruns=23 resyncs=7 average_ms=3.573 maximum_ms=13.012 p99_ms=5.913
HEARTBEAT_PROOF: PASS
SAFE_STATE_WRITE: PASS
```

The PLC exchange workload remained below 20 ms at p99 and maximum, but Windows
missed 23 deadlines and resynchronized seven times during the approximately
ten-minute run. The heartbeat remained healthy. Because this application is a
visual PLC logic simulator rather than a deterministic machine controller,
20 ms is accepted as the supported best-effort exchange rate with PLC
watchdog protection. `Simulation_Enable` was enabled near cycle 2,867 rather
than before cycle 1.

The current command files report the functional runtime exit code. A timing
failure can therefore still display exit code zero; judge these builds by the
printed timing criteria until timing acceptance is incorporated into the
process exit status.

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

## Controlled rate-sweep commands

The package supplies one guarded command per rate. From source, the equivalent
20 ms command is:

```powershell
$env:PYTHONPATH = "src"
py -3 -m siemens_plc_pc_interface scene-run `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene-fast.json `
    --cycle-ms 20 `
    --report-every 25 `
    --execute `
    --cycles 250 `
    --write-safe-state-on-exit
```

Repeat with these pairs:

```text
--cycle-ms 15 --cycles 334
--cycle-ms 10 --cycles 500
--cycle-ms 5  --cycles 1000
```

Do not run the rates simultaneously. Each command opens its own S7 session and
writes only `DB14.DBX0.0` and `DB14.DBD2`.

## Failure symptoms

| Symptom | First check |
|---|---|
| Conveyor never starts but heartbeat is healthy | Confirm the proof echo rung was replaced with `Comm_OK AND NOT photoeye` |
| `SCENE_INVALID` | Read the exact field/ownership message; validation occurs before connection |
| First cycle is `starting` | Normal; the PLC echo acknowledges the preceding heartbeat |
| Persistent `fault` or `Simulation_Timeout = true` | Check heartbeat echo progression and DB14 watchdog call |
| Frequent timing overruns or any resync | Stop the sweep; use the preceding slower rate and repeat it longer |
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
