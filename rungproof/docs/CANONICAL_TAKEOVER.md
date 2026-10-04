# Canonical repository takeover - 2026-10-03

## Repository and preservation

- Canonical remote: https://github.com/mnwinter/Siemens-PLC-PC-Interface.git
- Branch: `agent/add-config-foundation`.
- Migration baseline: `72a82d401f4b8f0a3613ede94d51e3345163dcb1`.
- Application source: `rungproof/`; Godot application: `rungproof/rungproof-next/`.
- Retired-source removal reported by the handoff:
  `95883a322132c049de5db688ce027cbc71dc8e6c` (not independently verified).
- This review used a new, initially clean checkout. The pre-existing dirty
  destination checkout described in the handoff was not located or modified.
  Its changes are not present in this checkout and must be inspected before
  any later integration. No old-repository development was performed.
- Local restore tag: `codex/takeover-baseline-20261003`, verified against the
  migration commit. Do not reset or overwrite the separate dirty checkout.

Read root `AGENTS.md`, `PROJECT_INFORMATION.md`, `README.md`, then the corresponding
RungProof documents, `CONTEXT.md`, and `docs/AI_HANDOFF.md`. Some historical
documents describe the older Qt application, not the current Godot bridge.

## Fresh-checkout corrections

1. Removed an eager Snap7 client import from read-only diagnostics. Profile
   validation and injected fake-transport tests now work without Snap7; the
   established transport still loads Snap7 when constructing a real client.
2. Disabled automatic Blender-source imports. Runtime models use the committed
   delivery/collision GLBs. Blender source remains available for asset authoring.
3. Bounded the block-interface summary, which initially measured over 1,000 px
   tall and expanded the entire editor into Local Model Points.
4. Made the instruction palette horizontally scrollable, exposed the compact
   project-dock handle, and initially collapsed internal diagnostics in split
   view. This keeps the ladder pane above the shared points dock.
5. Added split-view capture selection and corrected the persistence verifier's
   missing output-directory assumption. Layout verification waits for rendered
   container updates after switching views.
6. Ellipsized long toolbar scenario titles to retain status visibility and added
   cell spacing to the aligned local point tables.

## Reproducible setup

The ignored portable tools are Godot 4.7.2 .NET and .NET SDK 10.0.401. See
`rungproof-next/docs/DEVELOPMENT_SETUP.md`. From `rungproof-next/`, with the
pinned executables installed:

```powershell
$env:DOTNET_ROOT = "$PWD\.tools\dotnet"
$env:PATH = "$env:DOTNET_ROOT;$env:PATH"
& .tools/dotnet/dotnet.exe build RungProof.Next.csproj
& .tools/godot/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe --headless --editor --path . --import
& .tools/dotnet/dotnet.exe run --project tests/RungProof.Next.VirtualController.Tests.csproj
```

Godot uses `rungproof/build/.venv-rungproof/Scripts/python.exe` for its bridge,
falling back to `py -3`. Create that environment using your Python executable
and install `python-snap7==3.1.0` for real transport availability. Installed
dependencies and a valid profile are not live PLC proof.

## Verified in this checkout

- C# build: zero warnings, zero errors.
- Virtual-controller tests: 135 passed, 0 failed; real transport not constructed,
  real PLC connection not attempted. The older handoff's count of 137 does not
  match the migrated suite.
- Root Python interface suite: 129 tests passed using offline transports.
- RungProof live-session/read-only diagnostic suite: 14 tests passed, both with
  and without Snap7 installed.
- App-shell verifier: 77 scenes, three groups, five demos, 294 assets; all five
  authored demo programs compiled; default PLC state disconnected.
- Virtual-controller application verifier: photoeye, blocked restart, forced
  output safe stop, reset, and monitor checks passed.
- Rendered Godot verifiers: ladder editing/persistence/drag/drop/dock controls,
  1600x900 window density, split-pane bounds, and Start/E-stop/Reset passed.
- Offline bridge `describe`/`close`: Scene 2 descriptor and exact DB14 scopes
  returned through the actual Python process. These commands do not connect.
- Actual GL compatibility-renderer captures inspected for Demo 5, including
  the points table and ladder pane. These are rendered application checks,
  not physical mouse interaction or complete UI acceptance.
- Godot still reports RID/ObjectDB resource leaks at shutdown.

## Open acceptance gates - do not claim complete

The supplied product requirements remain authoritative. Existing implementations
and passing menu tests do not by themselves close those requirements.

### External PLC execution

- No live PLC connection/read/write was performed in this review. Obtain the
  actual approved CPU/VM context, inspect the dirty destination work, and verify
  the exact profile/write scope with the operator before commissioning.
- `Main._PhysicsProcess` calls synchronous bridge exchange on the Godot thread,
  without honoring the configured exchange period through an independent worker.
  `Send` also waits for a JSON response without a bounded IPC timeout.
- The source selector does not fully isolate virtual-controller advancement
  from external exchange. `RunActiveController` calls local `RunDefault` in
  external mode; scene rules/sequences can assign PLC-owned scene points.
  Resolve this through the existing plant/session architecture, preserving
  external PLC authority rather than adding simulator interlocks.
- Connect currently depends on UI profile checks; enforce active-scene/profile
  compatibility and authorization invalidation at the actual connect boundary.
- External settings display a descriptor; comprehensive editable configuration,
  readiness/handshake results, and runtime timing still need acceptance.

### UI and demos

- Split pane bounds now pass at 1600x900, but the scene is cramped between its
  information rails and its camera composition is not centered in the exposed
  scene aperture. Do not equate the bounds verifier with a usable split view.
- The rendered 1200x675 split check fails: the ladder pane exceeds the window
  and overlaps the points dock. Verify drawer reopening, instruction
  reachability, and true mouse dragging after resolving this minimum layout.
- Standalone ladder view still needs its own Local Model Points/layout review.
- Demo 5 compiles and displays FB/FC/DB structure; complete animated mixed-logic
  execution and all demo start/stop/reset paths remain to be exercised.
- The scene E-stop test passes its symbolic stop/reset behavior. This does not
  establish safety-rated behavior or validate the external PLC's program.

Keep `docs/AI_HANDOFF.md` for broader architecture history and this document
for migration-specific evidence and unresolved gates.
