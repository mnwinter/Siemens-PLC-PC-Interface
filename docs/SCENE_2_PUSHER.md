# Scene 2: conveyor with single-solenoid pusher

Scene 2 builds on the proven conveyor/photoeye scene by adding one
PLC-controlled pusher. The PLC must stop a product at the photoeye, extend the
pusher, wait for the extended limit, remove the extend command, and wait for
the retracted limit before restarting the conveyor.

This is a beginner logic-training scene. It is a visual simulator, not a
machine-safety model.

## Project-copy rule

Create one standalone TIA project per scene:

1. Open the completed `Scene 1 - Conveyor Stop` project.
2. Use **Project > Save as**.
3. Save the copy as `Scene 2 - Conveyor Pusher`.
4. Make the DB14 and ladder changes below only in the Scene 2 copy.

Do not add Scene 2 tags to the Scene 1 project. Do not create DB15 merely to
preserve the old DB14 layout. Each saved TIA project contains only the logic
and DB14 members required by that scene. The previous project is the restore
point and the starting template for the next scene.

The repository keeps each PC scene JSON file separately. It does not contain
or modify the TIA project archive.

## Process sequence

The intended cycle is:

1. Pusher retracted and no part at the photoeye: conveyor runs.
2. Product blocks `Part_At_Pusher`: conveyor stops.
3. PLC sets and latches `Pusher_Extend`.
4. Simulator extends the pusher and transfers the product.
5. `Pusher_Extended` becomes true: PLC resets `Pusher_Extend`.
6. Simulator retracts the pusher.
7. `Pusher_Retracted` becomes true: conveyor can run again.

The simulated pusher is single-solenoid/spring-return:

- `Pusher_Extend = true` drives it toward extended.
- `Pusher_Extend = false` drives it toward retracted.

## Scene 2 DB14 contract

Disable **optimized block access** for DB14. Replace the Scene 1
scene-specific members with this layout; retain the heartbeat and watchdog
status members at their existing offsets.

| Offset | DB14 member | Type | Writer | Safe value |
|---:|---|---|---|---|
| `0.0` | `Part_At_Pusher` | `Bool` | PC simulator | `false` |
| `0.1` | `Pusher_Extended` | `Bool` | PC simulator | `false` |
| `0.2` | `Pusher_Retracted` | `Bool` | PC simulator | `true` |
| `1.0` | `Conveyor_Run` | `Bool` | PLC | n/a |
| `1.1` | `Pusher_Extend` | `Bool` | PLC | n/a |
| `2.0` | `PC_Heartbeat` | `DInt` | PC simulator | `0` |
| `6.0` | `PLC_Heartbeat_Echo` | `DInt` | PLC | n/a |
| `10.0` | `Simulation_Enable` | `Bool` | Operator/PLC | n/a |
| `10.1` | `Simulation_Comm_OK` | `Bool` | PLC watchdog | n/a |
| `10.2` | `Simulation_Timeout` | `Bool` | PLC watchdog | n/a |

The PC writes only `DB14.DBX0.0`, `DB14.DBX0.1`, `DB14.DBX0.2`, and
`DB14.DBD2`. It never writes the PLC commands, watchdog results, physical
inputs/outputs, or CPU operating state.

## Reuse the Scene 1 watchdog

Keep the existing `Simulation_Watchdog` FB and instance DB copied from
Scene 1. Call it unconditionally from OB1 with:

```text
Simulation_Enable   := DB14.Simulation_Enable
PC_Heartbeat        := DB14.PC_Heartbeat
Watchdog_Time       := T#2s
PLC_Heartbeat_Echo  => DB14.PLC_Heartbeat_Echo
Simulation_Comm_OK  => DB14.Simulation_Comm_OK
Simulation_Timeout  => DB14.Simulation_Timeout
```

Do not put the watchdog call behind `Simulation_Enable`. The FB needs to run
every PLC scan so it can detect heartbeat progress, time out, and recover.

## Scene 2 ladder logic

Use the network order below. The last write to `Pusher_Extend` intentionally
wins if set and reset conditions ever occur during the same scan.

### Network 1: latch pusher extension

```text
Simulation_Comm_OK  Part_At_Pusher  Pusher_Retracted
-------| |---------------| |--------------| |---------(S) Pusher_Extend
```

### Network 2: reset extension at the limit or on communication loss

Two parallel branches drive the reset coil:

```text
Pusher_Extended
-------| |-------------------------------------------(R) Pusher_Extend

NOT Simulation_Comm_OK
-------|/|-------------------------------------------(R) Pusher_Extend
```

In LAD, place the two conditions in parallel on one reset rung or use two
reset networks after the set network. The communication-loss reset is
required; do not rely only on the PC application to clear the command.

### Network 3: conveyor permissive

```text
Simulation_Comm_OK  Pusher_Retracted  Part_At_Pusher  Pusher_Extend
-------| |---------------| |--------------|/|-------------|/|----( ) Conveyor_Run
```

This keeps the conveyor stopped while:

- communication is unhealthy;
- a part is at the pusher;
- the pusher extend command is latched; or
- the pusher has not fully retracted.

Do not map these simulated commands directly to hazardous physical outputs.
They belong in the scene-specific simulation path.

## PC scene files

Scene 2 uses:

```text
examples\scene-2-db14-pusher-interface.json
examples\scene-2-conveyor-pusher.json
```

Validate them without connecting:

```powershell
py -3 -m siemens_plc_pc_interface scene-validate `
    .\examples\scene-2-db14-pusher-interface.json `
    .\examples\scene-2-conveyor-pusher.json
```

Expected:

```text
SCENE_VALID: True
PLC_CONNECTION_ATTEMPTED: False
```

## Live graphical test

After compiling and downloading the Scene 2 TIA project:

1. Open a watch table containing all ten DB14 members.
2. Confirm `Pusher_Extended = false` and `Pusher_Retracted = true` after the
   simulator connects.
3. Set `Simulation_Enable = true`.
4. Start the graphical scene with the guarded live command.
5. Watch one complete conveyor-stop-push-retract sequence.
6. Stop the viewer.
7. Require `SAFE_STATE_WRITE: PASS`.
8. Set `Simulation_Enable = false`.

From a source checkout:

```powershell
py -3 -m siemens_plc_pc_interface scene-visualize `
    .\examples\scene-2-db14-pusher-interface.json `
    .\examples\scene-2-conveyor-pusher.json `
    --execute `
    --write-safe-state-on-exit
```

## Expected result

- Loop health reaches `HEALTHY`.
- `Simulation_Comm_OK` becomes true and `Simulation_Timeout` becomes false.
- Conveyor runs until `Part_At_Pusher` becomes true.
- Conveyor stops and `Pusher_Extend` latches true.
- The graphical pusher extends and the product leaves the photoeye.
- `Pusher_Extended` becomes true.
- `Pusher_Extend` resets false.
- The pusher retracts and `Pusher_Retracted` becomes true.
- Conveyor returns to its ready/running state.

## First failure checks

| Symptom | First check |
|---|---|
| Conveyor never starts | Verify `Simulation_Enable`, `Simulation_Comm_OK`, and `Pusher_Retracted` are true |
| Product stops but pusher never moves | Verify the set rung makes `Pusher_Extend` true |
| Pusher reaches extended but stays there | Verify `Pusher_Extended` resets `Pusher_Extend` |
| Conveyor starts during a push | Verify the conveyor rung includes both normally-closed `Part_At_Pusher` and `Pusher_Extend`, plus `Pusher_Retracted` |
| Limits appear backwards | Confirm DB14 offsets `0.1` and `0.2`, and confirm retracted safe value is true |
| Viewer remains `STARTING` | Verify `PLC_Heartbeat_Echo` changes and the watchdog call is unconditional |
| Viewer shows a timeout | Check TCP 102/network path, DB14 access, heartbeat offsets, and watchdog call |

Scene 2 runtime behavior is covered by offline automated tests. Record the
live TIA/VM result in `PROJECT_INFORMATION.md` only after the sequence is
observed on the target PLC.
