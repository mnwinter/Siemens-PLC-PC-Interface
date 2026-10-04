# Prototype acceptance results

Date: 2026-07-30

## Static checks

```powershell
$node = "C:\Users\matt.winter\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
& $node --check prototype\src\sceneLoader.js
& $node --check prototype\src\sceneGuides.js
& $node --check prototype\src\assetFactory.js
& $node --check prototype\src\simulations.js
& $node --check prototype\src\alarmManager.js
& $node --check prototype\src\plcProfiles.js
& $node --check prototype\src\player.js
& $node --check tools\build_training_scenes.mjs
& $node --check tools\verify_training_scenes.mjs
& $node tools\build_training_scenes.mjs
& $node tools\verify_training_scenes.mjs
& $node tools\test_control_ownership.mjs
& $node tools\test_machine_stop_loop.mjs
& $node tools\test_alarm_manager.mjs
& $node tools\test_scene_tag_contract.mjs
& $node tools\test_scene_plc_profile.mjs
py -3 -m py_compile tools\serve_player.py
py -3 tools\test_plc_diagnostics.py
```

Result: pass.

Scene JSON parse result:

```text
JSON_OK conveyor-cell.json: 7 assets
JSON_OK equipment-gallery.json: 21 assets
JSON_OK scene-1-conveyor-stop.plcscene: 5 assets
JSON_OK scene-2-conveyor-pusher.plcscene: 6 assets
JSON_OK tank-high-low.json: 9 assets
JSON_OK tank-level.json: 10 assets
JSON_OK tank-radar.json: 8 assets
```

Training library result:

```text
TRAINING_SCENES_VALID: 25
TRAINING_CASES_PASS: 50
SCENE_GUIDES_VALID: 25
REUSABLE_TYPES_COVERED: 8
LIBRARY_SCENES_VALID: 32
PLC_CONNECTION_ATTEMPTED: FALSE
CONTROL_SOURCE_DEFAULT: disconnected
DISCONNECTED_INPUT_ACCEPTED: PASS
DISCONNECTED_PLC_OUTPUTS_SAFE: PASS
FAKE_PLC_REFERENCE_LOGIC: PASS
FAKE_PLC_WRONG_OUTPUT_RESPONSE: PASS
TRUE_REFERENCE_OUTPUT_FAILS_SAFE: PASS
SEQUENCE_CONTROLLER_GATE: PASS
ALL_LABS_DISCONNECTED_SAFE: 25
SCENE_1_SYSTEM_STOP: PASS
SCENE_1_BLOCKED_RESTART: PASS
SCENE_1_LOOP_RESET_RESTART: PASS
OPERATOR_STOP_LOOP_INHIBIT: PASS
EXPLICIT_SEQUENCE_SYSTEM_STOP: PASS
SEQUENCE_COMPLETION_LOOP: PASS
GLOBAL_RUN_PERMISSIVES: PASS
PLC_CONNECTION_ATTEMPTED: FALSE
SYSTEM_STOP_ALARM: PASS
LOCAL_ACKNOWLEDGEMENT: PASS
CLEARED_HISTORY_RETAINED: PASS
START_BLOCKED_WARNING: PASS
DECLARATIVE_POINT_FAULT: PASS
ACTIVE_ALARM_NOT_CLEARED: PASS
INTERLOCK_FAULT: PASS
PROGRAM_COMPLETE_NOT_ALARM: PASS
PLC_CONNECTION_ATTEMPTED: FALSE
SCENE_1_PROFILE_AUTO_SELECTED: PASS
SCENE_2_PROFILE_AUTO_SELECTED: PASS
UNCONFIGURED_SCENE_FAILS_CLOSED: PASS
INVALID_REFERENCED_PROFILE_REJECTED: PASS
BUILTIN_SCENE_PROFILE_REFERENCES: PASS
UNSAFE_PROFILE_REFERENCE_REJECTED: PASS
```

All-scene tag-contract result:

```text
SCENE_TAG_CONTRACTS_VALID: 32
DECLARED_RUNTIME_POINTS: 173
EXTERNAL_INTERFACE_TAGS: 120
PLC_CONNECTION_ATTEMPTED: FALSE
```

## Browser checks

Tested at 1280 x 720 in the in-app Chromium browser.

| Check | Result |
|---|---|
| Conveyor scene renders | Pass |
| Prior Scene 1 stops at 0.50 m with photoeye true | Pass |
| Prior Scene 2 stop/push/transfer/retract sequence | Pass |
| Prior Scene 2 repeat package loading | Pass |
| `.plcscene` Save creates a file in the local library | Pass |
| Saved scene appears in selector and reloads | Pass |
| Portable `.plcscene` file picker load | Pass |
| Conveyor Run changes mock command and speed | Pass |
| Photoeye changes to blocked at carton crossing | Pass |
| Tank scene loads without page restart | Pass |
| Initial 42% maps to 10.72 mA | Pass |
| 100% maps to 20.00 mA and high switch true | Pass |
| 17.62% maps to 6.82 mA and low switch true | Pass |
| High/low tank 75% high-switch threshold | Pass |
| High/low tank 25% low-switch threshold | Pass |
| Radar tank initial 35% maps to 2.75 m and 9.60 mA | Pass |
| Radar tank rise to 51.10% maps to 1.99 m and 12.18 mA | Pass |
| Original combined tank still loads after optional-instrument refactor | Pass |
| Equipment gallery loads 21 assets | Pass |
| Training scenes 2.01-2.25 all load through the scene selector | Pass (25/25) |
| Training scenes have a live WebGL canvas and no load error overlay | Pass (25/25) |
| Training scenes contain validated progressive hints and reference solutions | Pass (25/25) |
| Runtime tags match declared name/type/owner/unit | Pass (32/32 built-ins) |
| Configuration tags match the scene point name/type/owner/initial value | Pass (32/32 built-ins) |
| Configuration excludes `SIM` points and PLC `role: "memory"` points | Pass (32/32 built-ins) |
| Configuration dialog opens with expected I/O rows or intentional empty state | Pass (32/32 built-ins) |
| Scene Editor conveyor-pusher export has a complete typed point contract | Pass |
| Saved Scene 1 and editor fixtures have complete typed point contracts | Pass (2/2) |
| Hint dialog reveals Hint 1, then Hint 2 only after request | Pass (25/25) |
| Solution shows warning, then reveals nonempty reference steps | Pass (25/25) |
| Packaged EXE opens Configuration, Hint, and guarded Solution for every lab | Pass (25/25) |
| Scene 2.01 direct-follow lamp | Pass |
| Scene 2.02 AND logic, all four input combinations | Pass |
| Scene 2.03 inverted-input logic | Pass |
| Scene 2.04 OR logic, all four input combinations | Pass |
| Disconnected exercise input changes while PLC output remains safe | Pass |
| Run is rejected while disconnected (`PLC WAIT` / `NO PLC`) | Pass |
| Fake PLC must be explicitly enabled | Pass |
| Forced wrong result `bay_a=TRUE`, `bay_b=FALSE` lights only bay A | Pass |
| Scene change disables Fake PLC and returns outputs safe | Pass |
| Brighter indicator emissive/glow/point-light treatment | Pass |
| Ergonomic lift reaches top limit with both motion outputs off | Pass |
| Robot/CNC machining excludes robot motion | Pass |
| Robot/CNC completes with robot and CNC outputs off | Pass |
| Local scene-file chooser loads valid JSON | Pass |
| Equipment click opens inspector | Pass |
| Layout variants A, B, C render | Pass |
| Browser warning/error log | Empty |

Additional visual/mechanical checks:

| Check | Result |
|---|---|
| Conveyor rollers use physical rotation pivots | Pass |
| Motor and pump couplings use shaft-axis pivots | Pass |
| Pump casing remains stationary | Pass |
| Motor and pump green run indicators visible | Pass |
| Industrial fan guard, blades, motor, stand, and run lamp render | Pass |
| Flanged process pipe with flow arrow/support is identifiable | Pass |
| 3D conveyor start/stop station operates | Pass |
| 3D tank pump and drain stations operate | Pass |
| 3D gallery start button operates | Pass |
| 3D emergency stop latches, blocks Run, and resets | Pass |

## PLC Scene Player shell checks

| Check | Result |
|---|---|
| File, View, Playback, PLC, and Help menus render | Pass |
| Persistent playback HUD renders in A, B, and C | Pass |
| View menu switches A/B/C | Pass |
| Selected Scene 2 survives A-to-B-to-C View changes | Pass |
| Previous/next media controls are absent | Pass |
| HUD Run/Stop updates the simulation and displayed state | Pass |
| Operator Stop holds elapsed/process state | Pass |
| Reset returns elapsed time and process state to initial values | Pass |
| Scene 1 sensor condition enters `SYSTEM STOP` | Pass |
| System stop leaves photoeye true and conveyor output false | Pass |
| Start is rejected while the Scene 1 stop photoeye remains blocked | Pass |
| Rejected Start holds package position at 0.51 m | Pass |
| Loop displays `LOOP RESET` and returns to `RUNNING` | Pass |
| Loop count advances after automatic reset/start | Pass |
| Operator Stop remains stopped with Loop selected | Pass |
| Sequence global Run checks the declared Start permissives | Pass |
| Faults & Alarms opens as a modal popup | Pass |
| Scene 1 system stop raises one active alarm | Pass |
| Popup shows scene ID, code, severity, state, source, and first check | Pass |
| Local acknowledgement leaves the active alarm condition present | Pass |
| Reset moves the alarm to cleared history | Pass |
| Clear history cannot remove an active alarm | Pass |
| Blocked restart raises a `START BLOCKED` warning | Pass |
| Loading another scene opens a separate empty alarm session | Pass |
| Popup states its no-real-PLC-write boundary | Pass |
| PLC menu exposes Test PLC | Pass |
| Player controls expose Test PLC in A, B, and C | Pass |
| Scene 1 Test PLC auto-loads only its assigned seven-tag profile | Pass |
| Scene 2 Test PLC auto-loads only its assigned ten-tag pusher profile | Pass |
| Auto-loaded profile control is locked to one option | Pass |
| Scene without `plcTestProfile` has no Run button or fallback | Pass |
| Unsafe or invalid profile reference | Rejected before connection |
| PLC profile endpoint reports two valid profiles and no write endpoint | Pass |
| Cross-site PLC-test POST without the read-only header | Rejected (HTTP 403) |
| Invalid PLC profile POST | Rejected before connection (HTTP 400) |
| Offline diagnostic tests | 4 passed |
| Real PLC connection during acceptance | Not attempted |
| Help > Player controls dialog | Pass |
| Missing built-in scene files are omitted from the playable library | Pass |
| One WebGL canvas per view | Pass |
| Horizontal page overflow | None |

## Standalone EXE checks

Built with:

```powershell
.\tools\build_vm_exe.ps1
```

Tested with:

```powershell
.\tools\smoke_test_vm_exe.ps1
```

Result:

```text
EXE_SMOKE_TEST: PASS
PLAYER_HTTP: 200
THREE_HTTP: 200
SCENE_GUIDES_HTTP: 200
ALARM_MANAGER_HTTP: 200
PLC_PROFILE_RESOLVER_HTTP: 200
SCENE_1_HTTP: 200
SCENE_2_HTTP: 200
SCENE_PROFILE_REFERENCES: PASS
TRAINING_SCENE_HTTP: 200
BASIC_TRAINING_SCENE_HTTP: 200
BASIC_TRAINING_GUIDE: PASS
PLC_PROFILES_HTTP: 200
PLC_PROFILE_COUNT: 2
PLC_UNAUTHORIZED_POST: 403
PLC_INVALID_PROFILE_POST: 400
SAVE_HTTP: 200
```

The save check also proved that the packaged application stores persistent
`.plcscene` files in `saved-scenes` beside the EXE. No installed Python, npm,
CDN, internet service, or PLC connection is required by the packaged runtime.
This was a local package test; launch on the actual VM is still outstanding.

Dedicated-window package test:

```text
PACKAGED_APP_WINDOW: PASS
PLAYER_HTTP: 200
APP_WINDOW_PROCESS_COUNT: 1
SINGLE_HEADER_LIVE_PLC_GUIDE_ALARM_SOURCE: PASS
EXIT_RESPONSE_OK: True
PACKAGE_PROCESS_COUNT: 0
APP_PROCESS_COUNT: 0
```

This proves one Microsoft Edge application-mode window with no normal browser
tab required, plus clean shutdown of both the installed rendering engine and
the hidden packaged server. Google Chrome application mode is the fallback
when Edge is unavailable. An installed Edge or Chrome engine is required; it
is intentionally reused instead of bundling another complete browser.

Current package:

```text
RungProof-VM.zip
SHA-256: b69db4d0a1fc629425a79680f48ef1daa7e346ba83f8b88bb3da4ab5b0e5a96c
```

## PLC status

```text
PLC_CONNECTION_ATTEMPTED: FALSE
PLC_TEST_WRITE_ATTEMPTED: FALSE
LIVE_SCENE_PLC_EXCHANGE_ENABLED: TRUE — GUARDED/EXPLICIT
REAL_PLC_COMMISSIONED: FALSE
```

This is an offline visual/architecture and read-only-diagnostic proof, not a
live controls proof.

## Guarded real PLC binding and single-header acceptance — 2026-07-30

| Check | Result |
|---|---|
| One RungProof product header contains brand and File/View/Playback/PLC/Help | Pass |
| Separate duplicate web menu strip removed | Pass |
| Connect Real PLC is presented before Offline Fake PLC | Pass |
| Scene 2 dialog shows 3 feedback points and 2 PLC command points | Pass |
| Scene 2 dialog shows exact 4-write and 6-read DB14 scope | Pass |
| Final Connect control disabled until exact-scope confirmation | Pass |
| Browser-cycle requests send only PC-owned scene points | Pass |
| `part_at_pusher` FALSE-to-TRUE reaches the configured `DB14.DBX0.0` transport write | Pass (fake transport) |
| PLC outputs apply only through declared simulation controller points | Pass |
| Starting/disabled/Comm-not-OK/timeout cycles do not apply PLC commands | Pass |
| Healthy-to-not-ready transition clears previously applied PLC commands | Pass |
| Missing required live PLC status BOOL | Pass; profile/readiness fail closed |
| Stale or faulted cycle cannot apply returned PLC commands | Pass |
| Explicit Disconnect, scene change, exit, mismatch, fault, and timeout close/invalidate live session | Pass |
| Stop holds the visual scene while preserving the intentional real-PLC session | Pass (source regression) |
| Reset resets the visual model while preserving the intentional real-PLC session | Pass (source regression) |
| Run controls remain disabled while the live session is STARTING/not ready | Pass (source regression) |
| Scene 1/2 local 3D toggles cannot bypass live PLC ownership | Pass |
| Missing guarded-write marker rejected | Pass (HTTP 403) |
| Modified authorized write scope rejected before transport creation | Pass (HTTP 409) |
| Full source verification | Pass (25 Node, 22 Python) |
| Training and interface contracts | Pass (25 scenes, 50 cases, 32 tag contracts) |
| Browser warning/error log | Empty |
| Real PLC connection during automated acceptance | Not attempted |

```text
LIVE_SCENE_2_PLC_OUTPUTS: PASS
LIVE_SCENE_2_PC_OWNERSHIP: PASS
LIVE_SCENE_1_PLC_OUTPUTS: PASS
PLC_CONNECTION_ATTEMPTED: FALSE
```

The live adapter is now present, but actual TIA/PLC commissioning remains a
separate required test. A passing fake-transport or packaged smoke test does
not prove CPU settings, DB14 layout, heartbeat echo, watchdog ladder behavior,
or the physical network path.
