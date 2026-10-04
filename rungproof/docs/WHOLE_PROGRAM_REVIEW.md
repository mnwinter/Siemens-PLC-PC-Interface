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
| Normal conveyor Start is overwritten by the next scan | Sidebar and 3D actions wrote an output directly. Both now use one controller route, with authored momentary command bindings and matching loaded output bindings. | Native Windows Start produced `conveyor_run=True`, speed 1.05 m/s, and carton motion. Rendered picking/scan regression passes. |
| Scene rules compete with the selected controller | Fallback fake-PLC rules executed on feedback changes. Suppress them while a controller owns the output image. | Regression verifies feedback changes preserve the controller output and that fallback rules still work after returning to local scene execution. |
| E-stop leaves controller running or permits automatic restart | Route simulated E-stop through the active controller Stop and block Run while its scene permissive is latched. Reset clears controller state without starting. | Native E-stop, blocked Run, and Reset inspected; rendered regression also requires a fresh Start after Reset and Run. |
| Pending momentary Start fires after Stop/Run | Session Stop retained an unscanned pulse. Cancel pending pulses and partial elapsed scan time on Stop. | Controller regression; 139 tests pass. |
| External and virtual controllers can publish competing outputs | Mode change unloads the virtual session; external physics takes an exclusive branch. External Run no longer invokes fake-PLC logic. Local Stop/Reset/PLC-owned scene actions are blocked in external mode. | Offline regression checks mode exclusivity and preserves an injected external output image. Native external selection blocks local Start without connecting hardware. |
| Event History never records events | Replace placeholder with bounded, scrollable action and controller-transition history. | Native Run and accepted/blocked Start events displayed. |
| Split view obscures the scene and camera frames covered areas | Use the visible scene aperture for framing, projection offsets, picking, and resize updates; hide information rails in split. | Rendered camera/picking regressions and native minimum/default/maximized windows inspected. |
| Points disappear in standalone editor; collapse does not reclaim editor space | Share a bounded scrollable point dock across operator/editor/split views and move editor bounds with its collapse state. Align point columns with the split divider. | Split layout regressions at 1200x675 and 1600x900; native collapse and expand inspected. |
| Narrow editor hides title/status, menus, and instruction access | Responsive toolbar, clipped tab titles, scrollable vendor menus, compact drawers, and an operational instruction browser. Preserve drawer choices after layout updates. | Native title/status/browser and rendered editor/drawer regressions passed. Narrow editor and point lists require scrolling. |
| Split Save opens the workspace dialog | Treat split as a ladder editing view for Save/Load. | Native Save opens the ladder-project dialog; cancelled without writing. |
| Point headings and values wrap after maximizing | Theme font changes leave stale BBCode table column measurements. Reparse the table only when its font size changes. | Native 1200x675 to maximized and back inspected: headings, BOOL, and conveyor_run remain on one line. |

## Review matrix

| Area | Current evidence | Remaining work |
| --- | --- | --- |
| Launch/import/toolchain | Pinned Godot/.NET start; native window opened; build clean | Fresh install/export and missing-dependency recovery |
| All scene data | All 77 catalog entries load and pass their declared cases; logs in `.tools/scene-review` | Visual controls and unsupported runtime types; many declared cases cover only initial state |
| Authored demos | All five compile; behavior tests for demos 1-4 and two Demo 5 regressions; 139 controller tests pass | Native interaction for demos 1-4; all FB/FC/DB views, animation/bindings, repeated run/reset |
| Operator controls | Demo 5 inputs, Run, Stop, command removal and normal conveyor Start/E-stop/Reset retested with real mouse input; event history displayed | E-stop/reset across other applicable scenes; visible runtime summary clipping |
| Ladder editor | Native add-network, Undo, Redo, and Save verified; rendered interaction verifier passed; cross-scene load regression passed | Native cross-scene load, drag insertion, tags, block interfaces, watch, validation failure, help |
| Scene/workspace authoring | Rendered workspace verifier passed, including mapping Run and Stop | Native asset placement, mappings, selection, undo, save/load, malformed files |
| Layout/camera | Split 1200x675 and 1600x900 regressions; native minimum/default/maximized views, points collapse, browser, and resize reflow inspected | Remaining native block/tag/edit flows and runtime summary clipping; broader scene visual acceptance |
| External execution boundary | Fake Python suites, process descriptor check, exclusive mode and synthetic output ownership regressions | IPC timeout/worker, profile cadence, scene/profile matching, stale authorization, readiness feedback, type validation |
| Python canonical interface / legacy tools | Earlier 129 root tests and 14 fake live/diagnostic tests passed | Source review for conflicts and rerun after any relevant change |
| Shutdown/resource lifecycle | RID and ObjectDB leak reports observed | Trace and fix owned UI/resource cleanup; verify process/bridge termination |

## Specific open issues

- Switching scenes does not yet prove preservation of unsaved user ladder work.
- External bridge JSON reads block the UI thread indefinitely on a missing
  response, with redirected stderr not consumed. Profile cadence is ignored.
- External connect lacks an enforced matching scene/profile boundary; scope
  approval is not invalidated when selection changes.
- Demo 5 currently commands output indicators; complete palletizing motion and
  reusable FB interface/instance behavior require further verification.

## Checkpoint results

- .NET build: zero warnings and errors.
- Controller unit/behavior suite: 139 passed, zero failed, no transport created.
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

## Controller routing checkpoint

Restore tag `codex/controller-routing-baseline-20261003` preserves the prior
checkpoint. The current build has zero warnings/errors, 139 passing controller
tests, and passing rendered scene-control, virtual-controller UI, numeric-I/O,
and app-shell regressions. No PLC connection was attempted. The scene-control
regression includes a synthetic external output image; it is ownership proof,
not a PLC communication or hardware test. Shutdown resource leaks remain open.

Native Windows evidence covers normal Start/motion, E-stop/blocked Run/Reset,
source selection, rejected external local Start, and displayed event history.
Unmapped commands report rejection rather than silently forcing outputs. The
external command interface, transport readiness/cadence, and commissioning
requirements still need review. Next work is split/editor layout and framing,
then the remaining external bridge and whole-program workflows.

## Layout checkpoint

Restore tag `codex/layout-review-baseline-20261003` at `5f18105` preserves the
controller routing checkpoint. Build is clean. Split bounds/camera/columns,
point collapse, standalone points, and drawer-state regressions pass at
1200x675 and 1600x900. Rendered ladder editor, scene controls, workspace,
camera input, and app-shell regressions also pass. Native Windows inspection
covers minimum/default/maximized split views, resize reflow in both directions,
the instruction drawer, and the ladder Save dialog. This completes these layout
repairs, not whole-program acceptance. External transport and resource leaks
remain under review; no plant connection was attempted.

## Verification boundary

Native mouse/keyboard interaction proves only the inspected Windows workflows.
Headless declared scene cases prove only the stated cases, not full user
acceptance. Fake adapters and offline programs never prove live PLC behavior.
Live commissioning remains subject to the repository's approved CPU/profile,
exact write scope, network authorization, and direct machine observation.
