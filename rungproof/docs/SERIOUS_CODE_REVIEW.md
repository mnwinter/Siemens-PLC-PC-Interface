# Serious code and architecture review

Reviewed 2026-07-30. Scope: application top down, repository wide, with
independent architecture exploration and regression verification.

## Executive result

The application had a sound controls-safety model and useful deterministic
tests, but it was not release-ready. The review and release-verification pass
found thirteen concrete code, product, development, and packaging defects. The
repair pass keeps the working plant behavior and adds deep modules at the real
seams: scene contract, equipment catalog, scene session, scene-load
coordination, local API authorization, and reproducible packaging.

## Findings and disposition

| Priority | Finding | Disposition |
|---|---|---|
| P1 | Scene-controlled text reached `innerHTML` unescaped | Fixed with shared encoding, symbolic IDs, CSP, and malicious-markup tests |
| P1 | Asset config could request unbounded geometry allocations | Fixed with typed per-equipment config, limits, equipment cap, and aggregate complexity budget |
| P1 | Runtime references and point writes were validated after load | Fixed with eager semantic validation |
| P1 | Failed construction destroyed the working scene | Fixed with transactional staging and swap |
| P1 | Read-only PLC watchdog state generated false hard failures | Fixed: absent writer health is a warning; partial connects always attempt disconnect |
| P2 | Concurrent loads allowed an older request to replace a newer selection | Fixed with abort plus monotonic load generation |
| P2 | App exit, heartbeat, and scene save lacked the PLC route's origin guard | Fixed with same-origin checks plus an application-instance capability token on every POST |
| P2 | Source server exposed the repository root | Fixed with explicit static roots, traversal rejection, profile blocking, CSP, and HTTP tests |
| P2 | Browser and server accepted different saved-scene contracts | Fixed with a versioned Draft 2020-12 schema, semantic adapters, and shared parity fixtures |
| P2 | Package build read a dirty adjacent repository and ambient tool versions | Fixed with pinned upstream source, documented local read-only patch, locked toolchain, provenance, and build-version output |
| P2 | Root Python test discovery failed | Fixed by making `tools` a package and supporting module/script imports |
| P1 | Frozen EXE omitted the local PLC diagnostics module and never opened its server port | Fixed with an explicit PyInstaller tools path and hidden import; proved by the black-box EXE smoke test |
| P2 | Package smoke/app-window scripts evaluated `$PSScriptRoot` too early in parameter defaults | Fixed by resolving default artifact paths after parameter binding |
| Release blocker | Repository has no initial commit; all files are untracked | Not mutated. Establishing the first source-control baseline requires an explicit ownership/commit decision |

## Architectural assessment

### Deep Scene Contract module

The old contract was **shallow**: validation details leaked through the loader,
factory, simulation runtime, editor, and Python save handler. The new
versioned **module** has an **interface** that returns only bounded,
semantically executable scenes. Its **implementation** owns equipment limits,
point types, runtime references, and persistence rules.

The JavaScript and Python validators are **adapters** at a real cross-language
**seam**. This creates **leverage** for every caller and improves **locality**:
a contract change now has one documented version and parity tests.

### Deep Equipment Catalog module

The editor catalog and player type list previously duplicated supported
equipment. The catalog now owns type identity, authoring defaults,
capabilities, and configuration bounds. The validator and editor consume that
same **interface**, and a regression test proves that 3D builders expose the
same set. This adds **depth** without inventing a plugin system.

### Transactional Scene Session module

Scene construction order, rollback, and disposal now live behind one scene
session **interface**. Its **implementation** stages the complete asset graph,
runtime, and alarm manager. Only a valid session is swapped into the player.
That is a high-value lifecycle **seam**, not a pass-through wrapper.

### Scene Load Coordinator

Cancellation and newest-request-wins behavior now have one small **module**.
The **interface** is deep enough to guarantee commit ownership while hiding
abort and generation details from callers.

### Renderer-neutral plant runtime

This remains the next architectural gate before live scene binding. The current
`createSimulation(scene, registry)` external interface is already reasonably
deep, so mechanically splitting the large file would add shallow modules. The
next justified step is a deterministic plant-state implementation with a
Three.js adapter and an in-memory test adapter. Do not add a hypothetical live
PLC adapter before the offline plant adapter exists independently.

## Deliberately rejected work

- No ECS or physics engine.
- No broad UI framework rewrite.
- No plugin architecture.
- No live PLC scene writes.
- No editor promotion into the packaged product.
- No generalized storage-adapter hierarchy with only one storage requirement.
- No unapproved initial Git commit.

## Upstream reuse decisions

- Three.js r179 remains the proven renderer already vendored with hashes.
- JSON Schema Draft 2020-12 and Python `jsonschema` provide the server contract
  instead of a custom schema language.
- The Siemens PLC/PC interface is pinned from its existing repository at commit
  `754fcfb88192f2a932bd7df70feea0d08088ab97`; only the audited read-only
  diagnostic method is added locally.
- PyInstaller, python-snap7, jsonschema, and transitive build dependencies are
  locked rather than replaced with custom packaging code.
- Three.js `TransformControls` is a good future editor control, but it does not
  solve a reviewed release defect and is not added in this pass.

## Verification contract

Use:

```powershell
py -3 -m pip install -r requirements-build.txt
powershell -NoProfile -ExecutionPolicy Bypass -File tools\run_checks.ps1 fast
powershell -NoProfile -ExecutionPolicy Bypass -File tools\run_checks.ps1 full
powershell -NoProfile -ExecutionPolicy Bypass -File tools\run_checks.ps1 release -EnableRealPlc
```

`release` builds `build\RungProof-VM\RungProof.exe`, creates
`build\RungProof-VM.zip`, and runs the packaged native self-test and window
smoke test.

Final release evidence on 2026-07-30:

- 14 Node tests passed;
- 13 Python tests passed;
- 25 training scenes and 50 acceptance cases passed;
- 32 scene tag contracts, 173 runtime points, and 120 external interface tags
  passed;
- packaged HTTP, authorization, static-root, scene-save, and PLC-profile checks
  passed;
- the packaged app opened one dedicated window and exited with zero residual
  RungProof or app-window processes;
- PyInstaller analysis contained no reference to the adjacent Siemens
  repository.

## Native direct-runtime review - 2026-07-30

The packaged browser/server architecture above is now superseded for the
Scene 2 product slice. The current executable is a native PySide6/Qt 3D
application. Its one in-process PLC worker directly owns the pinned
`Snap7Transport`; the renderer only reads immutable snapshots. No HTTP server,
JSON transport, browser engine, WebView, or render-frame-driven PLC exchange is
in the live path.

The retained module calls are deliberate software boundaries, not runtime
transport stages:

```text
ConveyorPusher -> SimulationUpdateLoop -> InterfaceRuntime -> Snap7Transport
```

All four execute synchronously in the same PLC worker thread. Network exchange
and the configured 20 ms cadence dominate the response time; these typed
function calls do not add another process, queue, serialization step, or
scheduler.

### Independent native review findings

| Priority | Finding | Disposition |
|---|---|---|
| P1 | Readiness or heartbeat recovery could resume playback without a new operator Run | Fixed; every readiness loss latches playback stopped |
| P1 | A late cycle could trigger catch-up exchange bursts | Fixed; missed slots are skipped |
| P1 | One-folder smoke test copied only the EXE | Fixed; the complete Qt package is copied and verified |
| P1 | Window close could hide the UI before a blocking PLC operation returned | Fixed; the window remains visible in closing state until the worker exits |
| P2 | A Qt 3D startup exception could leave the PLC worker alive | Fixed; the viewport is constructed before the PLC session |
| P2 | Profile validation allowed extra/remapped live tags | Fixed; exact DB14 ownership is enforced |
| P1 | A transient S7 error recreated the plant and silently reset position/time | Fixed; only the failed transport/runtime is replaced and the plant state is preserved |
| P2 | Profile inversion and timing could change the reviewed behavior | Fixed; version, endpoint, 20 ms cycle, 2000 ms transport timeout, 1000 ms heartbeat, symbols, safe values, point group, and non-inverted mappings are exact |

The re-review also suggested that the release lane skipped native Qt lifecycle
tests. Current `tools/run_checks.ps1` already executes those tests with the
locked build environment after packaging; system-Python skips are therefore
not the release result.

### Safety and lifecycle contract

- Connect is explicit and authorizes only the displayed DB14 scope.
- Stop and Reset never disconnect the real PLC.
- Explicit Disconnect and application exit close the S7 session.
- Transport failure reconnects automatically but never restarts playback.
- Enable, communication, timeout, or heartbeat loss stops playback and requires
  a fresh Run after recovery.
- Reconnect preserves conveyor, package, pusher, sensor, and scene-time state;
  only operator Reset clears the plant.
- Overruns skip missed 20 ms slots rather than generating a burst.

This is a focused native Scene 2 vertical slice. The other scenes and complete
legacy equipment catalog have not yet been ported to the native renderer.
Physical PLC/TIA validation is still required; automated tests deliberately do
not contact `10.70.9.201`.

### Final verification

- Independent final verdict: no remaining P0-P2 findings.
- Focused native runtime and Qt suite: 20 passed.
- Release lane: 25 Node tests passed; 42 Python tests passed with 6
  PySide6-only skips; all 6 skipped Qt tests then passed in the locked build
  environment.
- Package smoke: native entrypoint, exact Scene 2 target/write scope, no PLC
  connection attempt, no browser engine, and no HTTP server.
- Window smoke: one package process, zero listening ports, zero new browser
  processes, and clean exit.
- Final ZIP SHA-256:
  `E4C4B48BF9D9A270979AC693297941F445E9133F835F968360637B846217035A`.

## Native A/B/C UI re-review - 2026-07-30

The polished native UI was reviewed after all three browser-era workspaces
were restored as Qt layouts:

- A - Operator console;
- B - Immersive floor;
- C - Engineering split.

The review verified that every layout reuses the same `NativePlcSession`,
Qt 3D viewport, actions, panels, and snapshot stream. Triggering the actual
A/B/C actions produced zero Connect, Disconnect, Run, Stop, or Reset calls.
The view controller performs presentation-only widget reparenting and does not
enter the PLC or plant-runtime path.

Visual verification found View A's reparented live-point panel was added to the
grid while still hidden. The panel is now explicitly shown, and the regression
test checks visibility in A, B, and C. Disabled-state selectors were also made
more specific than the green/amber action selectors so disconnected Run and
Stop controls cannot appear enabled.

The final independent UI verdict was clean with no P0-P2 findings. The packaged
A/B/C screenshots were inspected, the native package contains no browser/HTTP
runtime assets, and physical PLC validation remains deliberately outstanding.

## VM-safe renderer and Test PLC re-review - 2026-07-30

| Priority | Finding | Disposition |
|---|---|---|
| P1 | Live Connect could enter during the first read-only diagnostic refresh interval | Fixed at the `_connect` command seam; diagnostic-active and non-disconnected states return without creating the persistent writer |
| P2 | Packaged renderer/Test PLC claims were hardcoded | Fixed; self-test constructs the default renderer and observes native-child state and diagnostic availability |
| P2 | Package analysis scan could silently pass without current manifests | Fixed; smoke requires one current `Analysis-*.toc` and scans both analysis content and the copied package |
| P2 | Listener comparison occurred only after self-test exit | Fixed; the live self-test PID is monitored with a bounded 30-second proof window |
| P2 | Native window entrypoint remains a large module | Recorded debt; decomposition is required before feature/protocol/diagnostic expansion, but does not block this focused correction |

The independent re-review found no remaining blocking runtime finding. Focused
native Qt/read-only diagnostic tests passed 19/19. The final packaged smoke
observed `software-qwidget`, no native child window, the read-only diagnostic,
no browser/server runtime, no listener, no PLC connection attempt, and the
exact Scene 2 DB14 write scope.
