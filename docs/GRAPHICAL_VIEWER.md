# Graphical conveyor viewer

The graphical runtime is a visual layer over the deterministic scene engine.
It is intended for watching PLC logic drive simulated equipment, not for hard
real-time control. The original Scene 1 conveyor/photoeye remains supported;
Scene 2 adds a pusher overlay and extended/retracted indication without
creating a second runtime.

Here, deterministic means the component model advances in fixed simulation
steps and preserves exchange order. It does not mean Windows, Snap7, or the
Ethernet link has hard real-time timing. For this visual simulator, the
live-proven best-effort 20 ms exchange is the supported default.

## Data flow

```text
PLC DB14 <-> Snap7 worker <-> SceneEngine -> latest SceneCycleReport -> Tkinter
```

Only the worker thread accesses Snap7 or advances physics. Tkinter reads the
latest completed report and draws it. A delayed GUI frame cannot change the
simulation state or PLC exchange order.

## Current display

The window shows:

- conveyor motor running/stopped;
- one product and its position;
- photoeye clear/blocked;
- pusher position and extended/retracted state when the scene contains a
  pusher;
- component state and completed count;
- scene time and exchange duration;
- update-loop health and heartbeat echo;
- `Simulation_Enable`;
- `Simulation_Comm_OK`;
- `Simulation_Timeout`;
- recent p99 transaction time.

The component layout and PLC point bindings still come from JSON. This is a
runtime viewer, not yet a drag-and-drop scene editor.

## Offline preview

This command validates both JSON files and prints the write scope. It does not
connect or open the viewer:

```powershell
py -3 -m siemens_plc_pc_interface scene-visualize `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene-fast.json
```

Expected:

```text
PLC_EXCHANGE_MS: 20
WRITE_SCOPE: pc_to_plc=DB14.DBX0.0:BOOL, pc_heartbeat=DB14.DBD2:DINT
VIEW: GRAPHICAL CONVEYOR AND PHOTOEYE
PLC_CONNECTION_ATTEMPTED: False
```

## Live start

Before starting, verify the DB14 watch table, the unconditional watchdog FB
call, the stop-at-photoeye PLC rung, and `Simulation_Enable = true`.

```powershell
py -3 -m siemens_plc_pc_interface scene-visualize `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene-fast.json `
    --execute `
    --write-safe-state-on-exit
```

Do not add `--cycle-ms` for normal visual use. The configured and live-proven
best-effort 20 ms exchange is the supported default.

## Standalone VM package

From a development checkout with the development requirements installed:

```powershell
.\tools\build_graphical_viewer_package.ps1
```

This creates:

```text
build\SiemensPlcPcInterface-GraphicalViewer-VM.zip
```

The ZIP includes the standalone EXE, both validated JSON files, setup
documentation, SHA-256 hashes, an offline validation command, and a guarded
live launch command. On the VM, extract the complete ZIP before running either
command; do not run the EXE from inside the compressed folder.

## Stop behavior

Click **Stop simulator** or close the window. The viewer:

1. signals the scene worker to stop;
2. allows the current PLC exchange to finish;
3. attempts configured safe values when
   `--write-safe-state-on-exit` was supplied;
4. disconnects Snap7;
5. closes the graphical window.

If communication is already lost, a PC-side safe write is not guaranteed.
Verify that the PLC watchdog sets `Simulation_Comm_OK = false`,
`Simulation_Timeout = true`, and gates the simulated command false.

## First live acceptance test

Require all of these:

- the graphical window opens on the Windows Server 2019 VM;
- loop health reaches `HEALTHY`;
- the displayed DB14 status matches the TIA watch table;
- the motor runs while the photoeye is clear;
- the product moves and stops when the photoeye blocks;
- closing the window returns the DB14 PC-owned fields to false/zero when the
  best-effort safe-state option is used;
- the terminal reports `SAFE_STATE_WRITE: PASS`.

## Failure symptoms

| Symptom | First check |
|---|---|
| No window | Confirm the packaged build contains Tcl/Tk and check the terminal error |
| `STARTING` never becomes `HEALTHY` | Confirm `PLC_Heartbeat_Echo` is progressing |
| Motor never runs | Check `Simulation_Enable`, `Simulation_Comm_OK`, and `PLC_To_PC` |
| Product does not move while motor says RUN | Confirm the scene worker has not reported an exception |
| Photoeye differs from TIA | Check `DB14.DBX0.0` is not forced and compare the latest completed exchange |
| Window is visually choppy | Check VM/host load; display refresh is not the PLC exchange |
