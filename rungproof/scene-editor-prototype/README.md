# Scene Editor prototype

## Question this proof answers

Can a user pick reusable Scene Player assets, place and configure them, and
compose a working machine without embedding arbitrary JavaScript, PLC
addresses, or controller logic in the scene file?

This is intentionally a separate, disposable authoring module. It reuses the
current `AssetFactory` and version-1 `.plcscene` validator, but it is not bundled
into the Scene Player EXE.

## Run

From the repository root:

```powershell
.\RUN-SCENE-EDITOR.cmd
```

The launcher starts the existing local-only server and opens the editor in a
dedicated Chromium app window. The editor does not expose a PLC connection or
PLC-memory write path.

## Current vertical slice

- browse all 21 current catalog asset types;
- click an asset to place the real reusable 3D model;
- orbit, zoom, pan, and select equipment in the viewport;
- edit stable ID, label, position, rotation, and type configuration;
- undo, redo, delete, start a new scene, and load a working starter;
- bind compatible assets to a typed conveyor/photoeye/pusher behavior recipe;
- see the symbolic PLC-command and PC-feedback contract;
- open supported `.plcscene` files;
- save directly to the Scene Player saved library or download a portable file.

The first behavior recipe compiles to the existing player-compatible
`conveyorPusher` simulation. Unsupported runtime types are rejected on open so
the editor cannot silently erase behavior it does not understand.

The compiled file includes the complete `simulation.points` declaration: three
PC feedback points, two PLC command points, and three simulator-only diagnostic
points. The player derives both its live tag metadata and Configuration popup
from that declaration.

## Architecture decision under test

Individual 3D assets do not call each other and do not execute PLC logic.

```text
PLC-owned symbolic commands
            |
            v
typed plant behavior recipe
  transport + material + sensor + actuator
            |
            v
PC-owned simulated feedback
```

The editor uses typed roles and capabilities to prevent invalid compositions.
For example, the conveyor-pusher recipe requires a conveyor for transport, a
box as movable material, a photoeye as the presence sensor, and a pusher as the
linear actuator. A stack light is optional.

This is the smallest useful route toward a Factory I/O-style system: the PLC
controls the scene; the simulator models plant response and returns inputs.

## Prototype limits

- no drag handles or transform gizmos yet; transforms use numeric fields;
- no collision or general physics engine;
- no generic renderer-neutral component runtime yet;
- only `static` and `conveyorPusher` authoring recipes are supported;
- the current player `conveyorPusher` runtime still combines plant response
  with an offline demonstration sequence and must be split before live PLC use;
- type-specific configuration is editable JSON and is not yet generated from a
  production catalog schema;
- no PLC connection, physical addresses, credentials, or write authorization.

## When this proof is complete

Record the decision in `NOTES.md`, then either delete this module or promote the
validated model/compiler into a production editor. Do not leave the prototype
as an accidental second application architecture.
