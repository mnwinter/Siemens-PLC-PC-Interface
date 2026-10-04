# Whole program review - 2026-10-03

Scope: the entire canonical PLC interface and RungProof application. Demo 5
is one reproduction example, not the acceptance boundary. Goal remains active.

Checkout: `Siemens-PLC-PC-Interface`, branch `agent/add-config-foundation`.
Restore tag: `codex/whole-app-review-baseline-20261003` at `c4cda6b`.
The user's older dirty canonical checkout has not been located or modified.
No changes have been pushed. No plant connection has been attempted.

## Evidence and fixes

| Finding | Cause and correction | Evidence |
| --- | --- | --- |
| Windows launcher cannot find .NET | Missing path separator produced `dotnetdotnet.exe`. Corrected executable path and added a missing-runtime message. | Executed the actual `.cmd` launcher; clean build and native RungProof window observed. |
| Scene action buttons stop working during scans | Runtime refresh destroyed every button between mouse-down and mouse-up. Construct them on scene attachment; refresh values separately. | Reproduced and retested using Windows Computer Use on the native Godot window. Gantry-home, pallet-valid, and carton-present now toggle while scanning. App verifier checks button identity across 90 scans. |
| Run advances scans while the toolbar and footer say Stopped | Status read plant motion instead of selected controller execution. Read the virtual snapshot in simulator mode. | Native Run and Stop now show the correct state. |
| Simulator labeled External PLC while disconnected | Status selected the client class rather than the execution mode. Read the selected mode. | Native PLC health now identifies local runtime, no echo, connection disabled. |
| Demo 5 commands persist after a permissive drops | Conditional calls skip the blocks that clear prior memory. Scan permissive-producing blocks each cycle. | Regression reproduced failure before fix. Native lost-home click now removes vacuum and gantry commands. |
| Demo 5 counts unavailable cartons and repeatedly increments a completed layer | Dwell ignored permissives; layer arithmetic executed every scan while completion stayed true. Gate dwell with pick permissive and count completion rising edges. | Two controller regressions passed after fix. |
| Opening a saved ladder for another scene replaces it with a demo | Restored the saved document before scene attachment installed the starter template. Attach the scene first, then restore saved work. | App-shell regression preserves a custom network label after scene change and reopening, including the loaded controller program. Native same-scene save also verified. |
| 31 unresolved accessory errors despite existing mappings | Type-level migration metadata predates accessory configuration. Validate configured catalog IDs and retain missing-ID errors. | App shell now reports one informational ready diagnostic, 77 scenes, 294 assets. This does not grant production or visual approval. |

## Review matrix

| Area | Current evidence | Remaining work |
| --- | --- | --- |
| Launch/import/toolchain | Pinned Godot/.NET start; native window opened; build clean | Fresh install/export and missing-dependency recovery |
| All scene data | All 77 catalog entries load and pass their declared cases; logs in `.tools/scene-review` | Visual controls and unsupported runtime types; many declared cases cover only initial state |
| Authored demos | All five compile; behavior tests for demos 1-4 and two Demo 5 regressions; 138 controller tests pass | Native interaction for demos 1-4; all FB/FC/DB views, animation/bindings, repeated run/reset |
| Operator controls | Demo 5 inputs, Run, Stop, command removal retested with real mouse input | E-stop/reset across applicable scenes; action event history; visible runtime summary clipping |
| Ladder editor | Native add-network, Undo, Redo, and Save verified; rendered interaction verifier passed; cross-scene load regression passed | Native cross-scene load, drag insertion, tags, block interfaces, watch, validation failure, help |
| Scene/workspace authoring | Rendered workspace verifier passed, including mapping Run and Stop | Native asset placement, mappings, selection, undo, save/load, malformed files |
| Layout/camera | Default 1600x900 inspected; maximized view inspected | Split and narrow window failures; usable aperture; point tables in standalone editor; drawers retain state; readable tree; camera framing |
| External execution boundary | Existing fake Python suites and process descriptor check | Exclusive execution ownership, IPC timeout/worker, profile cadence, scene/profile matching, stale authorization, readiness feedback, type validation |
| Python canonical interface / legacy tools | Earlier 129 root tests and 14 fake live/diagnostic tests passed | Source review for conflicts and rerun after any relevant change |
| Shutdown/resource lifecycle | RID and ObjectDB leak reports observed | Trace and fix owned UI/resource cleanup; verify process/bridge termination |

## Specific open issues

- Event History is a static label; it records no user actions or transitions.
- Native Conveyor Inspection Cell reproduction: Run starts ladder scans; then
  clicking Start / Stop Inspection Conveyor leaves `conveyor_run` False. The
  scene action writes a PLC-owned output and the next scan overwrites it.
  Operator commands must enter the selected controller's input image; both
  sidebar and 3D controls need the same route. Recheck E-stop/reset at that seam.
- Standalone Logic Editor hides Local Model Points. Split layout can overflow
  at 1200x675 and hides most of the scene between information rails.
- Split scene viewport calculation includes opaque UI areas; the camera frames
  the entire viewport rather than its actual visible aperture.
- Dock layout updates reapply visibility defaults, undoing user choices.
- Switching scenes does not yet prove preservation of unsaved user ladder work.
- Main advances external and virtual sessions in the same physics callback.
  External Run calls local scene logic, so PLC authority needs explicit audit.
- External bridge JSON reads block the UI thread indefinitely on a missing
  response, with redirected stderr not consumed. Profile cadence is ignored.
- External connect lacks an enforced matching scene/profile boundary; scope
  approval is not invalidated when selection changes.
- Demo 5 currently commands output indicators; complete palletizing motion and
  reusable FB interface/instance behavior require further verification.

## Checkpoint results

- .NET build: zero warnings and errors.
- Controller unit/behavior suite: 138 passed, zero failed, no transport created.
- Canonical Python interface: 129 passed. Fake live/diagnostic suites: 14 passed.
- Declared scene contracts: 77 scene files passed their stated cases.
- Godot app shell, cross-scene persistence, numeric scene I/O, stable operator
  controls, rendered ladder editor, and rendered workspace verifiers passed.
- Headless workspace gizmo failures were retested with a rendered viewport.
  Its remaining mapping assertion expected False after Run; corrected the
  fixture to require True after Run and False after Stop, and reran successfully.
- Native Windows screenshots inspected for launcher startup, Demo 5 Run/Stop,
  input changes, lost-permissive response, Save, add-network, Undo/Redo, normal
  conveyor Start failure, standalone editor, and unusable split view.

Next work: reproduce and fix controller action routing, then audit execution
source ownership and repair split/editor layouts with native interaction proof.

## Verification boundary

Native mouse/keyboard interaction proves only the inspected Windows workflows.
Headless declared scene cases prove only the stated cases, not full user
acceptance. Fake adapters and offline programs never prove live PLC behavior.
Live commissioning remains subject to the repository's approved CPU/profile,
exact write scope, network authorization, and direct machine observation.
