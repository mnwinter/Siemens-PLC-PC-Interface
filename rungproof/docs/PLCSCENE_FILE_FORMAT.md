# PLC Scene file format

## Identity

| Property | Value |
|---|---|
| Extension | `.plcscene` |
| Encoding | UTF-8 |
| Representation | JSON |
| File type field | `"fileType": "plc-visual-scene"` |
| Current schema | `"version": 1` |
| MIME type | `application/vnd.plc-visual-simulator.scene+json` |

The custom extension makes scene files recognizable without introducing a
binary or proprietary serialization. Standard JSON tools can still inspect
and version-control the document.

## Save behavior

The **Save** button validates and normalizes the current scene, then writes:

```text
prototype/saved-scenes/<scene-id>.plcscene
```

The saved entry immediately appears in the scene library selector. Saving the
same scene ID again replaces that saved-library copy. Built-in scenes under
`prototype/scenes` are never overwritten.

Saved-library files are user/runtime data and are ignored by Git.

## Load behavior

- Select a **Saved — ...** item to reload a library scene.
- Click **Load** to open a portable `.plcscene` from another folder.
- Legacy `.json` scene documents are accepted during the prototype.
- Validation completes before the current scene is replaced.

## What is persisted

- scene ID, name, description, and camera;
- equipment type, stable ID, label, transform, and validated configuration;
- simulation type, physical parameters, equipment references, and symbolic
  point names;
- optional `plcTestProfile` local filename reference for the scene's external
  read-only diagnostic profile;
- optional declarative `alarmRules` that evaluate symbolic scene points;
- optional training hints and a separately revealed functional reference
  solution.

## What is not persisted

- current animation position or elapsed time;
- live mock tag values, timers, counters, or transient fault state;
- the player's current Run/Stop state, selected Loop mode, or completed-loop
  count;
- active, acknowledged, or cleared alarm instances and alarm history;
- PLC connection details, IP addresses, DB offsets, rack/slot, `%I`, or `%Q`;
- write authorization, credentials, or executable scripts.

PLC bindings remain a separate guarded interface contract. Loading a scene file
does not authorize a PLC connection or write. If `plcTestProfile` is present,
the player automatically loads only that exact validated external profile when
Test PLC is opened. Missing, invalid, or unavailable references fail closed
without selecting a substitute profile.

## Scene learning guides

The player derives **Configuration** from `simulation.points`; it is not stored
as a second editable tag list. Only external `PC` and `PLC` points are shown.
`SIM` points and PLC points marked `role: "memory"` are excluded because they
are not part of the simulator/PLC interface.

Every non-`static` scene must declare every runtime-visible point. Validation
rejects missing arrays, duplicate names, unsupported data types/owners, and
initial values that do not match the point type. Saved and editor-generated
scenes use the same contract as built-in scenes.

An optional `training` object may provide:

```json
{
  "training": {
    "hints": [
      "First progressive hint",
      "Second progressive hint"
    ],
    "solution": {
      "summary": "Reference behavior explanation",
      "steps": ["Functional reference step"],
      "acceptance": "Expected result"
    }
  }
}
```

Hints and the reference solution are validated and persisted with the scene,
but neither changes runtime control behavior.

Training scenes may also provide cumulative setup metadata and a machine
operation guide:

```json
{
  "training": {
    "sequenceNumber": 10,
    "inheritsFrom": "lab-2-09-maintenance-beacon",
    "foundation": "common-plc-watchdog-foundation",
    "retainedTags": ["PC_Heartbeat", "Simulation_Comm_OK"],
    "addedTags": ["motor_run"],
    "changedTags": [],
    "previousAcceptance": ["lab-2-09-maintenance-beacon"],
    "machineGuide": {
      "purpose": "What the machine does.",
      "startConditions": ["What must be ready."],
      "normalSequence": ["What happens in order."],
      "stopBehavior": ["What a stop does."],
      "faultBehavior": ["How missing or wrong signals appear."],
      "expectedObservations": ["What the student must verify."]
    }
  }
}
```

`inheritsFrom` and the tag-delta fields describe cumulative lab progression.
Independent practice scenes omit them or reference the common foundation.
The machine guide explains physical/process behavior and is intentionally not
a ladder-logic solution.

## Local server boundary

The prototype server listens on `127.0.0.1` and accepts scene saves up to
2 MiB. It sanitizes the scene ID before forming a file name and writes only
inside `prototype/saved-scenes`.
