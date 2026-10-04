# RungProof / PLC Visual Simulator AI handoff

This document is the versioned project-memory handoff for a new AI agent or
developer starting from a fresh branch. It records the durable context that
would otherwise be trapped in a local Codex session. It intentionally excludes
machine-local Codex databases, credentials, screenshots from private chats, and
temporary runtime state.

## Product intent

Visual review reopened (2026-10-04): the user reported a pallet intersecting a
Demo 5 gantry post. The previous final checkpoint did not inspect every scene
from multiple angles. The active goal now requires catalog-wide native visual
coverage and repair; do not mark it complete after Demo 5. Use
`MULTI_ANGLE_SCENE_REVIEW.md` as the coverage ledger. Demo 5 placement and attached
gripper motion are corrected and inspected from five angles; seven focused
geometry checks pass. REAL scene initial JSON integer tokens now normalize at
the scene-project boundary; the previously mismatched catalog test reproduces
the production reader and all 142 tests pass. The complete 77-scene shell bounds
inventory now flags 44 scenes for interpretation. Powder-mixer placement and
tank shell sizing are repaired; an original static open chute replaces the
copied roller-shutter, and inherited door evidence is archived/removed from
current approval. Its five-view native reinspection verifies bounded static
clearance, not a powder-flow process. Scaled radar feedback and Reset projection
are corrected. Thirty-one focused geometry, 19 plant, three family-selection and
71 authored scene-case checks pass (six scenes have no authored cases).
Parcel-sorter geometry is repaired: flat indexed tables, supported bridge and
takeaway paths, common deck elevations, raised header and configured optical
heights. Five static views plus final portal/table details were inspected. Native
declared plant preview Run/Stop/Reset and count=3 completion were observed from
front-left/rear-right; this is scripted geometry, not contact dynamics or sensor
validation. Normal shell Run opens the blank editor with NO CONTROLLER LOADED;
no supplied sorter reference controller exists. Do not count preview as operator
Run acceptance. Shared conveyor width/deck sizing now works; Demo 5 static
five-view regression passes, and the inspection conveyor is now reviewed; other conveyor scenes still need native review. Eight scenes inspected; 69 pending.
Conveyor inspection now has supported cartons, grounded/photoeye stands clear
of frame/pull-cord hardware, and correctly projected beam feedback. Five native
views plus normal offline Run/Start/Stop/Reset and simulated E-stop/restart gating
were inspected. Feedback/recirculation remain simplified, not physical sensing.
Gallery probes are supported on illustrative stands; pipe/valve supports are
grounded and the transmitter clears the pipe. Five static native views and
instrument details were inspected. Gallery normal Run opens a blank editor with
NO CONTROLLER LOADED: its animation workflow remains open. Current evidence is
catalog-*.log under rungproof-next/.tools; 31 geometry, 19 plant, rendered scene
controls and 71 scene cases pass. Do not use headless GUI-input checks as evidence.
Workstation Call, Dual Confirmation and Service Marker have clear supports/spacing but incorrect
generic START plates. Global help validation fails at Count Display's inherited
door-axis metadata; investigate actual identity before refreshing that help.
Candidate AABB flags and scene loading are never visual acceptance. Restore tag
`codex/multi-angle-review-baseline-20261004` preserves `2c3de4b`. No hardware or
push. Continue the remaining ledger and asset/placement repairs.

Whole-program review final checkpoint (2026-10-04): Windows startup, all five
authored demos, controller ownership, editor/history/persistence, native
workspace authoring and malformed-file rejection were inspected and repaired.
Native tank fill/drain, analog feedback, Stop hold and Reset are verified.
Final suites pass: 142 controller, 16 connection, 129 canonical Python,
16 fake Python, 69 selected legacy Python and 28 Node tests; eight plant traces
match 83 snapshots. All 77 scenes load; 71 have passing declared cases and six
have none. Rendered app-shell/editor/split/controls/playback/plant checks pass.
The vendor manifest now matches the reviewed existing adapter patches and
normalizes Windows line endings while rejecting other changes. The legacy
renderer rejects 31 Godot-only accessory scenes explicitly.

Use the current matrix in `WHOLE_PROGRAM_REVIEW.md`; older checkpoint statuses
below are historical. Remaining capabilities include crash recovery, full lab
reference programs, actual FB instances/closed-loop pallet placement, automatic
reconnect/profile editing UI and a standalone installer. Full visual/runtime
acceptance of every scene and live PLC commissioning remain unverified. No
hardware connection or push was performed.

Editor completion checkpoint (2026-10-04): timer Reset records its tag creation
inside Undo; rejected interface edits retain history/monitoring. Native tag and
block forms now wrap at minimum/default window sizes with readable labels.
Unknown startup scene IDs recover to the default and report the reason.
Instruction Help now reveals its dock through the shared open path; native TON
documentation and scrolling inspected. Build and rendered ladder regression
pass. Whole-program review remains active; see the current review matrix.

Fresh-source startup checkpoint (2026-10-04): the launcher now restores NuGet
packages and imports assets before native startup. A tracked-source copy with
no generated caches reproduced NETSDK1004 before the fix, then built/imported
and ran the conveyor through normal Windows controls. Missing Godot/.NET/console
checks stop with exact paths. Portable tool setup remains required, and there
is no standalone export preset/installer. Review copy and logs are ignored at
`build/cold-start-review-20261004`; its `.tools` is a junction to the pinned
tools, so do not recursively delete through that junction. Goal remains active.

Current checkpoint (2026-10-04, watch review): controller suite 142/142;
plant regression 19 checks; rendered ladder interaction passes. Native Demo 5
first Run preserves preconfigured inputs, its four-pick layer stops commands,
and command-driven XYZ motion holds on Stop and resets. Demo 4 now calls its
counter FB and validation FC. Demo 5 has two FBs, two FCs, two populated DB
declaration views, timer/counter/comparison/math/parallel logic. It remains a
manual-feedback visualization; DB interfaces are declarations/shared tags.
Watch rows/pickers retain identity across scans; Remove/Clear update both
editor titles and toolbar Undo without dropping runtime monitoring. Native
Remove/Clear/Undo in TIA and Studio 5000 passed; sessions closed cleanly.
The Windows overlay mentioned in older checkpoints below is gone, and native
pusher/tank, authoring and watch workflows have since been inspected. See
`WHOLE_PROGRAM_REVIEW.md` for current matrix and evidence. Goal remains active;
fresh install/export and remaining native flows are still under review.

Latest local review checkpoint (2026-10-04): scene navigation retains each
ladder draft, saved baseline/path, and Undo/Redo; Demo 4 counts only valid
pallet-detection edges. Labs now open blank exercises with their own typed
scene bindings; empty Run reports missing logic and hidden scene rules cannot
compete with the selected controller. Fresh editor drawers fit at 1200x675 and
1600x900. Native demo 1-4 and Lab 2.1 author/run workflows were exercised. See
`WHOLE_PROGRAM_REVIEW.md` for regression and Windows evidence. Drafts remain
in memory; Save is required before exit. Rejected drafts now retain the loaded
controller's truthful state and show editor errors without stale monitoring.
New/Open and window close now guard unsaved current/cached drafts with Save,
Discard, or Cancel; failed writes cannot authorize continuation. Complete
lab/reference coverage, crash recovery,
remaining native workflows, broader external profile coverage, and longer sessions
still require work. The whole-program review is active; no live PLC acceptance
or complete product acceptance has been established.

The shutdown leak was traced to an unparented hidden Studio block selector.
Both vendor workbenches now own that control and its popup. Settled orphan,
rendered editor, and split tests exit without resource leak reports. Current
controller tests pass 140/140 and offline connection/process/playback tests 16/16.
External Connect no longer runs plant playback. Run requires the existing
reference readiness policy; Stop/Reset hold playback while exchange continues.
Readiness recovery requires a new Run. Full-app fake exchange and native
Run/Stop/Reset were verified without a PLC adapter or network. External source,
playback and cycle labels now report actual state; REAL display is bounded.

Latest plant checkpoint: Scene 2 lacked a conveyor/pusher physics implementation,
and tank motion depended on a local Run flag not set by ladder execution. The
ported canonical conveyor/pusher model now produces feedback and repeated
transfers from real offline ladder scans; tank fill/drain and analog/limit
feedback run from selected-controller playback. Stop holds the plant. Pure
model comparison passes eight Python traces / 83 snapshots; the full-app
`--verify-plant-motion` regression passes. All 77 scene files load, 71 with
declared cases pass, and six have no declared cases. Native pusher/tank 3D and
File/Open inspection are still pending because a Windows update overlay
blocks native input. Generated native review projects are under
`rungproof-next/.tools/plant-review-*.rpproj.json`. Keep the goal active.

Workspace save now completes a temporary file before replacing the destination;
Windows failed-replacement preservation/cleanup/retry and the rendered workspace
regression pass. Unsaved placements/groups/links still need scene/Load/close
guards and saved-baseline comparison for Undo. Preserve synchronous scene
attachment during ladder Open; a deferred Main SceneRequested callback alone
would reopen that prior corruption bug. See the workspace write checkpoint.

Saved-baseline comparison for workspace dirty state is now implemented.
Rendered tests reproduce the former Undo-to-baseline false UNSAVED state and
verify original and nonempty saved baselines with Edit/Undo/Redo/Save. Scene,
workspace Load and close protection is still pending. The current tree's
`Main.WorkspaceVerification.cs` also tests failed atomic replacement.

Workspace replacement guards are now implemented and tested for scene changes,
workspace Load, cross-scene ladder Open, and close. Save cancellation/failure
blocks replacement; Discard does not falsely save; queued ladder opens still
attach the scene before restoring the project. Rendered workspace/editor tests
pass. Native launch, pusher/tank File/Open and motion, placement, Undo/Redo,
close Cancel, scene-change Save and workspace Open were inspected after the
Windows overlay cleared. Native inspection found clipped operator runtime and
navigation on the tank, and stale gizmo/selection after Undo to empty; these
remain to be repaired. Prior pending-overlay statements above describe earlier
checkpoints, not current availability. No PLC connection was attempted.

Operator and PLC-health rails now scroll complete content; native 1600x900 and
1200x675 inspection confirmed readable runtime/health and reachable navigation.
Undo to empty now removes the gizmo and stale placement inspector. Rendered
workspace, app-shell/orphan, split and controller UI checks pass; controller
suite is 140/140. Native windows closed normally without error/leak reports.
Next review areas are remaining editor workflows, Demo 4/5 presentation and
complete sequence boundaries, external profiles, install/export and legacy
conflicts. The goal is active; prior pending-rail statements are historical.

Latest editor checkpoint: block navigation no longer marks a project dirty or
prompts on clean close; save files still preserve the active block. The
controller suite passes 141/141. Native FB/FC/DB browsing and drag insertion/Undo
were exercised. All editor Tree browsers now use readable selected/hovered
states; interface summaries are bounded and explicitly identify declarations
and shared project tags. Offline calls do not implement parameter passing or
per-instance FB storage. Build, rendered ladder interaction and split tests
pass. See the editor browsing checkpoint in `WHOLE_PROGRAM_REVIEW.md`; keep the
goal active for remaining editor, demo sequence, external and install review.

Latest authored demo checkpoint: first Run preserves operator-established scene
feedback instead of resetting it during initial controller load. Demo 4 now
executes its qualified counter in an FB and validation in an FC; its unused
timer was removed without changing completion behavior. Demo 5 includes
comparisons, a parallel actuator-status branch and two populated DB declaration
views. A completed four-pick layer stops pick commands and requires Reset.
Its three delivered XYZ nodes now animate from gantry_cycle and hold on Stop
or command loss; Reset restores them. The coordinate-sensor shutter substitute
was replaced in this scene by a sensor pair. The scene/help explicitly retain
manual feedback and identify the motion as a command visualization, not a
closed-loop placement model. Build, 142 controller tests, app-shell/guard/orphan
checks and 19 plant checks pass. Native first Run, motion, Stop/Reset, four-pick
completion and block views were inspected. Next review: watch-table row
stability under scans, remaining native editor workflows, external profiles,
install/export and generic accessory substitutions. The goal stays active.

RungProof is a Windows PLC visual simulator and training environment. A user
selects a scenario, sees the 3D machine, edits ladder logic in a TIA Portal or
Studio 5000 styled workbench, runs a deterministic built-in controller, and
observes typed symbolic scene I/O. The longer-term product also supports an
authorized external PLC session using the existing guarded Siemens runtime.

The user expects the product to feel like an industrial engineering tool:

- Scenario, Logic Editor, and split-view navigation are quick and reliable.
- The complete operator scene is on the left and the ladder editor is on the
  right in split mode, with a draggable divider and local-model point tables
  remaining visible below.
- Side drawers never overlap the top toolbar or local-model points panel.
- Ladder symbols can be dragged onto visible rung insertion boxes and edited,
  moved, deleted, and added like the target vendor workflows.
- PLC source selection is explicit: built-in Simulator or External PLC.
- External PLC settings show the complete profile, connection, mapping, status,
  readiness, and test results instead of a generic disconnected badge.

## Two application generations

### Legacy/native live-PLC path

The existing guarded live path is under `rungproof/` in the canonical repository
and is the source of truth for real PLC behavior. Paths in the list below are
relative to `rungproof/`:

- `tools/rungproof_native.py` — native Qt application and operator controls;
- `tools/native_runtime.py` — plant/runtime/session lifecycle;
- `tools/plc_live.py` — guarded S7 session and typed exchange;
- `tools/plc_diagnostics.py` — read-only diagnostic path;
- `prototype/src/livePlcBinding.js` — browser/reference binding semantics;
- `prototype/src/player.js` — reference UI flow for Connect Real PLC;
- `prototype/plc-profiles/*.json` — validated scene/profile contracts;
- `vendor/siemens-plc-pc-interface/` — pinned S7 interface implementation.

The live session has separate states for connection, playback, and readiness.
It performs typed cycles, writes only the configured PC-to-PLC scope, reads only
the configured PLC-to-PC scope and status bits, and relies on the PLC watchdog
for safe output handling when cycles stop. Stop and Reset do not intentionally
disconnect the session.

The live path is launched by `RUN-3D-PLAYER.cmd`. The normal release/build
switch that exposes real writes is documented in `rungproof/README.md` and build
scripts. Do not silently enable real writes in an offline test build.

### RungProof Next

`rungproof-next/` is the Godot 4.7.2 .NET application launched by
`rungproof-next/RUN-RUNGPROOF-NEXT.cmd`. It currently provides:

- real 3D scene rendering with reviewed assets;
- scenario browser grouped as User Created, Labs, and exactly five authored
  Demos;
- TIA Portal and Studio 5000 styled ladder editor;
- editable contacts, coils, branches, timers, counters, comparisons, math,
  program-control blocks, tags, watch tables, block/interface lifecycle, and
  save/load of `.rpproj.json` projects;
- deterministic virtual controller and symbolic scene-I/O mapping;
- operator/logic split view, cycle/scan display, diagnostics, local model point
  tables, and training asset help.

The ladder workbench follows the TIA-style ownership model: the left project
dock contains separate Project tree, PLC tags, and Blocks / tasks tabs. The
editor's instruction palette remains the insertion surface, while the old
right-side Instructions / PLC tags / Blocks / Search / Help rail is hidden from
the visible layout. Search and instruction help remain available through their
internal commands without consuming editor width.

The five authored demos now load paired ladder documents when their scenario is
selected. Demo 5 is intentionally the more complex `Lab 11.13 - XY Palletizing
Cell`, not another conveyor view; its ladder contains the OB entry routine,
multiple FBs, multiple FCs, and a DB with visible interfaces and calls. The
app-shell verifier compiles every authored demo document and checks the active
Demo 5 bindings/FB-FC structure.

Its C# connection seam is `src/Connections/GuardedRuntimeClient.cs`. The Next
shell now starts `tools/plc_bridge.py` only when an operator uses the External
PLC settings, and that bridge delegates to the existing `tools/plc_live.py`
controller. The scene/profile contract is retained in the scene's optional
`plcTestProfile` field. Built-in Simulator remains the default source.

The 2026-10-04 whole-program review moved JSON bridge exchanges into bounded
async work through `ProcessBridgeChannel`. `Main._Process` polls completed
requests so UI, connection events and scene commits stay on Godot's main
thread. One request may be outstanding. Scene/source changes cancel pending
work and invalidate approval; a late reply cannot become another scene's
image. Profile cycleMs is currently a minimum frame-driven interval, not a
real-time timing guarantee. The bridge passes the verified descriptor into
`LivePlcController.connect` to reject changed configuration before creating
transport. Typed symbolic scope validation is in `ExternalSceneContract`.
Settings details scroll without stretching the dialog beyond the viewport.
See `WHOLE_PROGRAM_REVIEW.md` for current verified boundaries and open work.

## External PLC feature requirements

The implemented PLC menu provides the following without changing the existing
simulator behavior:

1. **Execution source**
   - Built-in Simulator: uses the virtual controller and local symbolic model.
   - External PLC: scene exchange delegates to the existing guarded live
     session. Next currently blocks local Stop/Reset and unmapped PLC-owned
     actions. Complete playback/command equivalence with the legacy UI remains
     under review; it must not be represented as commissioned or complete.
   - The selected source is visible in the toolbar, operator console, and PLC
     inspector.

2. **External PLC settings**
   - scene/profile selection;
   - CPU family/protocol as supported by the existing adapter;
   - IP/host, rack, slot, cycle, connection timeout, heartbeat timeout;
   - exact PC-to-PLC write scope and PLC-to-PC read scope;
   - typed scene-point mapping and required readiness/status bits;
   - explicit connect/disconnect controls and current session identity/health.

3. **Connection verification**
   - local profile/schema validation;
   - endpoint and transport availability;
   - authorized connection and exact write-scope confirmation;
   - protocol handshake and typed readback;
   - required `simulation_enable`, `simulation_comm_ok`, and
     `simulation_timeout` readiness checks;
   - scene/profile identity and point type/direction validation;
   - watchdog/cycle health and reconnect behavior;
   - read-only diagnostics that prove zero writes when the user selects a test.

4. **Testing**
   - use the existing in-memory transport adapter for automated live-path tests;
   - never contact the plant from CI, headless app verification, or simulator
     tests;
   - keep one explicit operator-run authorization step for a real connection;
   - test disconnect, timeout, stale session, scene change, malformed profile,
     invalid scope, missing status tags, and type mismatch;
   - prove simulator mode still runs when no PLC is available.

## Important prior user feedback

These are not optional polish items; they are recurring acceptance criteria:

- Do not report “complete” until the interaction has been exercised, not just
  compiled or inspected.
- The initial scene must run and animate; RUNNING text without green ladder
  state or animation is a defect.
- E-stop is a physical/momentary safety input, not a latched ordinary command.
  Reset/restart behavior must be explicit and testable.
- Green ladder state, cycle clock, elapsed timer values, and scene animation must
  agree with the same execution source.
- Scene/Event History drawers must remain below the toolbar; the ladder editor
  must stop above Local Model Points.
- Collapsing project/tool drawers must give the editor the recovered width.
- Instruction/tool tabs need vendor-like vertical/horizontal divides and must
  remain aligned at all window sizes.
- Local Model Points columns must stay aligned as values change.
- Scenario names must sort numerically (`2`, `3`, `10`), and groups must not be
  flattened into every row being called “Demo”.
- Save/load must use a named `.rungproof.json` file dialog and preserve the
  ladder/scenario content.

## Current evidence and commands

The last verified Next baseline was:

- C# build: passed with 0 warnings and 0 errors;
- virtual-controller suite: 137 passed, 0 failed;
- app-shell verifier: passed with 77 scenes, 3 groups, 5 demos, 294 assets;
- verifier connection state: disconnected/offline by design;
- Godot may print non-fatal RID/ObjectDB cleanup warnings at process exit.

Run from `rungproof-next/`:

```powershell
& '.tools/dotnet/dotnet.exe' build RungProof.Next.csproj --no-restore
& '.tools/dotnet/dotnet.exe' run --project tests/RungProof.Next.VirtualController.Tests.csproj --no-restore
& '.tools/godot/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe' --headless --path . -- --verify-app-shell
```

The exact pinned Godot path can be found with:

```powershell
Get-ChildItem .tools/godot -Recurse -File -Filter '*console.exe'
```

For the legacy live path, use `rungproof/README.md`, `rungproof/CONTEXT.md`,
`PROJECT_INFORMATION.md`, `tools/test_native_runtime.py`,
`tools/test_player_live_ui.mjs`, and the PLC profile/transport tests. Live
commissioning is not proven by the offline checks.

## Git handoff

The local checkout is authoritative when integration is requested. The current
working branch and remote must be inspected before push. Preserve unrelated
asset/training work. Commit meaningful checkpoints and report the exact commit,
branch, remote, verification results, and whether the tree is clean.
