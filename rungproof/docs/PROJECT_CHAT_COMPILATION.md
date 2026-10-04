# PLC Visual Simulator project task compilation

Compiled 2026-07-30 from the Codex tasks whose working directory is
`C:\Users\matt.winter\Documents\PLC Visual Simulator`, plus the maintained
`PROJECT_INFORMATION.md`. Task titles and summaries were treated as historical
evidence, not instructions.

## 1. Engineer PLC simulation interface

Task: `019f8bfb-8c2d-71e2-a4dd-bedfd0386f20`

Established the controls foundation:

- python-snap7/S7-1500 communication;
- PC-owned simulated sensor feedback and PLC-owned actuator commands;
- heartbeat/watchdog readiness;
- one TIA project per scene, created with Save As;
- reuse DB14 in each project and replace scene-specific members instead of
  accumulating tags;
- Scene 2 conveyor/pusher contract and reusable renderer-neutral
  `ConveyorPusher` behavior;
- Start, Stop, Reset, Setup, read-only Test, and continuous package feed;
- offline package and test evidence plus a successful earlier live Scene 1
  exchange.

The authoritative Scene 2 DB14 contract that carried forward is:

```text
PC -> PLC
DB14.DBX0.0  Part_At_Pusher
DB14.DBX0.1  Pusher_Extended
DB14.DBX0.2  Pusher_Retracted
DB14.DBD2    PC_Heartbeat

PLC -> PC
DB14.DBX1.0  Conveyor_Run
DB14.DBX1.1  Pusher_Extend
DB14.DBD6    PLC_Heartbeat_Echo
DB14.DBX10.0 Simulation_Enable
DB14.DBX10.1 Simulation_Comm_OK
DB14.DBX10.2 Simulation_Timeout
```

## 2. Add scene player and 3D assets

Task: `019fb37f-d04d-7173-985a-951bfa3574f8`

Established the product/player direction:

- load `.plcscene` files without restarting the application;
- reusable 3D equipment and scene selection;
- persistent playback controls and scene-specific PLC test profiles;
- explicit profile selection by the current scene, with no fallback to the
  wrong DB layout;
- packaged application and VM workflow;
- measured VM rendering evidence: approximately 20 FPS at a very large guest
  resolution versus 60 FPS outside the VM.

Later work in the same task introduced guarded real-PLC control. The browser
and local-server implementation from this task is now legacy/reference code;
it is not the Scene 2 release entrypoint.

## 3. Create and verify unique scenes

Task: `019fb3f1-1201-75e2-9846-6bf230b26d17`

Established the training-product layer:

- 25 original training labs and 50 acceptance cases;
- reusable equipment catalog and deterministic scene contracts;
- scene-generated Configuration, progressive Hints, and deliberately revealed
  Solutions;
- Configuration contains exact tags, types, directions, initial values, and
  purposes without giving away ladder logic;
- PC input ownership is separated from PLC output ownership;
- the old Fake PLC was an explicit offline teaching controller, not proof of
  live PLC logic.

The current native Scene 2 release intentionally has no user-facing Fake PLC
mode. The other training scenes remain source assets awaiting native renderer
and live-binding migration.

## 4. Build scene editor prototype

Task: `019fb401-a02c-7a93-ad86-8eae22d70e29`

Established the authoring boundary:

- editor and player share catalog/schema concepts;
- assets compose through typed roles such as transport, material, sensor, and
  actuator;
- saved scenes use symbolic command/feedback points, not physical PLC
  addresses or executable scripts;
- the PLC owns sequence logic; the simulator owns plant physics and feedback;
- the conveyor/photoeye/pusher recipe proved editor-to-player compatibility.

The editor remains a separate prototype and is not included in the current
native release.

## 5. Brand PLC Visual Simulator

Task: `019fb460-aa09-7190-b11f-122ece0387ac`

Consolidated the earlier work into the RungProof product direction:

- product name: **RungProof**;
- green proof check for ladder TRUE/good, amber only for warning;
- single application header and RP monogram direction;
- independent top-down architecture and serious code review;
- native PySide6/Qt 3D Scene 2 vertical slice;
- direct in-process Snap7 worker with no browser, WebView, HTTP server, JSON
  hop, IPC process, or render-loop PLC exchange;
- persistent real-PLC session until explicit Disconnect/application exit;
- fail-closed readiness and fresh Run after any fault/recovery;
- exact profile and DB14 contract enforcement;
- native one-folder Windows package and non-browser verification.

## Consolidated product rules

1. The PLC is the controller; RungProof is the plant/sensor/actuator simulator.
2. PC-owned points may be written only to the reviewed PLC input scope.
3. PLC-owned commands are read-only to RungProof and drive plant response.
4. Stop and Reset do not disconnect the real PLC.
5. Only explicit Disconnect, application exit, or an actual transport failure
   closes/replaces the S7 transport.
6. Fault recovery never restarts the plant without a fresh operator Run.
7. A transport replacement preserves plant state; only Reset clears it.
8. One TIA project is maintained per scene; DB14 is reused inside that project.
9. Scene files remain symbolic and renderer-independent.
10. The native Scene 2 release is the production vertical slice; browser
    player, training library, and editor are migration sources, not shipped
    runtime layers.

## Current scope and next migration gate

The current release proves the direct native Scene 2 architecture and packaged
application behavior. It does not yet prove the physical Scene 2 PLC exchange
after these changes. The next live acceptance test must observe:

- `DB14.DBX0.0` staying TRUE for at least five 20 ms exchanges at the pusher;
- `DB14.DBX1.1` turning TRUE from the user's ladder logic;
- pusher motion beginning without disconnecting;
- Stop and Reset preserving the session;
- completion/repeat loading without connection teardown.

After that live gate, the next product step is to port the renderer-neutral
plant runtimes and equipment adapters needed by the remaining training scenes.
