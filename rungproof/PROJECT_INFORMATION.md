# Project information

## Native training-scene and Ladder integration repair (2026-10-02)

- The Godot catalog now exposes all 77 currently authored source scenes: 25
  Chapter 2 labs, 2 Chapter 3, 12 Chapter 4, 10 Chapter 5, 2 Chapter 6, 7
  Chapter 9, 6 Chapter 10, 6 Chapter 11, and 7 base/demo scenes.
- Chapters 7 and 8 are not hidden by the UI: no authored source contracts exist
  for them yet. Do not claim complete Chapters 3-11 until those lessons are
  specified, authored, rendered, and accepted.
- The migration tool preserves reviewed native divergence by default and can
  intentionally refresh individual repaired scenes with `--accept-scene`.
- Generated training layouts now stagger later equipment rows, declare valid
  photoeye beam centerlines, connect each scene control to its actual symbolic
  action, and prevent scene rules from writing PLC-owned lesson outputs. All 71
  scenes with verification cases pass the native contract runner.
- Lab 4.1 now exposes one pulse input and one PLC lamp output for a real CTU
  exercise. Lab 5.1 exposes one request input and one PLC lamp output for a real
  TON exercise. Independent round-two harnesses proved new project authoring,
  save/reset/reopen, binding validation, compile/load, scan execution, monitor
  state, scene I/O mapping, and safe reset for both lessons.
- Saved `.rpproj.json` documents retain their associated source scene ID; opening
  a project requests that scene before Verify + Load.
- Generic simulator lists now use explicit high-contrast selected-row styling
  and scene rows expose full-name/ID tooltips. The conveyor start station is
  rotated toward the default operator camera and the real-window control test
  locks that orientation contract.
- Current verification: build succeeds with zero warnings/errors, 134/134
  virtual-controller tests pass, 71/71 scene contracts pass, 77-scene app-shell
  verification passes, the counter/timer Ladder editor verifier passes, and
  2048x1152 HUD, one-to-one DPI, and scene-control checks pass. No physical PLC
  transport is constructed or contacted by these offline tests.

## Offline engineering end-to-end acceptance and symbolic I/O boundary (2026-10-02)

- Added `SceneIoImageMapper` as the single pure translation boundary between
  controller tag names and bound scene point names for BOOL, INT, DINT, and
  REAL images. `Main` now uses this mapper for every virtual-controller sample
  and commit path.
- The mapper has no physical-address resolution and no PLC transport
  dependency; the existing direction/type/ownership validator remains the
  pre-load gate.
- Added one coherent acceptance test covering authoring, editable-project
  save/open, binding validation, compilation, deterministic scan execution,
  scene input/output exchange, monitor publication, simulator-only forcing,
  safe Stop, and Reset force clearing.
- Current focused result: `VIRTUAL_CONTROLLER_TESTS_PASS 134`, zero failures,
  `REAL_PLC_TRANSPORT_CONSTRUCTED FALSE`, and
  `REAL_PLC_CONNECTION_ATTEMPTED FALSE`.
- Native verification after the mapper refactor passed virtual BOOL scene I/O,
  numeric DINT scene I/O, and the complete Ladder editor interaction verifier.
- The broader native integration rerun also passed the 2048x1152 HUD,
  workspace/gizmo, scene-control, camera-input, and one-to-one DPI checks;
  all 26 native scene contracts passed. Headless HUD/input attempts correctly
  failed at the synthetic 64x64 viewport and were not used as acceptance
  evidence; the documented real-window reruns are authoritative.
- The full objective now has direct source/test evidence for every named
  Ladder capability. Publication is still intentionally withheld because the
  shared repository contains thousands of pre-existing asset/training changes
  outside the PLC-editor scope; those must not be silently deleted or bundled
  into the Ladder checkpoint merely to make `git status` clean.

## Objective

Build **RungProof**, currently a PLC-led visual simulator for proving real
ladder logic on an isolated live bench PLC. TIA creates the ladder, the PLC
executes it, and RungProof supplies deterministic simulated plant feedback and
visualization. Offline control is deferred. The player must
stay open while scene definitions are loaded at runtime, provide normal
application menus and playback HUD controls, and use reusable
industrial-equipment assets. The validated equipment definitions must also be
reusable by a future user-facing drag/drop scene builder.

## Prototype boundary

This repository remains isolated. It does not modify the working
`C:\Users\matt.winter\Documents\Siemens-PLC-PC-Interface` repository.
Packaging uses a pinned source snapshot of that project at
`754fcfb88192f2a932bd7df70feea0d08088ab97`. RungProof exposes its existing
read-only diagnostic separately from an explicitly authorized guarded live
scene exchange.

The reference simulator's controls decisions remain authoritative:

- scene files contain process/equipment definitions, not PLC IP addresses;
- PLC-owned and PC-owned points remain separate;
- scene behavior does not bypass the guarded transport/runtime;
- PLC communication must fail safe;
- the existing PLC watchdog remains authoritative;
- no physical `%I` or `%Q` write path is permitted.

## Current architecture

```text
Dedicated desktop app window
    |
    +-- Single product header + playback HUD
    |       +-- File open/save
    |       +-- View A/B/C
    |       +-- Run / Stop / Reset playback
    |       +-- disconnected / explicit Fake PLC control source
    |       +-- explicit read-only Test PLC
    |       +-- explicit Connect Real PLC with exact scope confirmation
    |
    +-- Local scene loader + validation
    |       +-- built-in scene documents
    |       +-- local .plcscene / legacy JSON file chooser
    |       +-- local .plcscene saved-scene library
    |
    +-- Read-only PLC setup diagnostic
    |       +-- validated external plc-profiles
    |       +-- explicit connect / two reads / disconnect
    |       +-- test invokes no PLC transport write method
    |
    +-- Guarded live PLC adapter
    |       +-- one active scene/profile/session
    |       +-- exact PC-owned DB write-scope authorization
    |       +-- typed point conversion through pinned Siemens runtime
    |       +-- PLC-owned commands/status returned to the scene
    |       +-- browser-cycle timeout stops the PC heartbeat
    |       +-- PLC watchdog remains safe-state authority
    |
    +-- Reusable 3D asset factory
    |       +-- motor / conveyor / box / photoeye
    |       +-- switch / indicator / pump / fan / tank
    |       +-- level sensor / radar level sensor / pipe
    |       +-- rotary switch / lift table / valve / drill press
    |       +-- robot arm / roller shutter / rotary table / machine
    |
    +-- In-memory plant simulation
            +-- PLC outputs fail safe while controller disconnected
            +-- Fake PLC reference logic + deliberate output forcing
            +-- conveyor/photoeye behavior
            +-- prior Scene 1 conveyor-stop behavior
            +-- prior Scene 2 conveyor-pusher behavior
            +-- tank/pump/drain/level behavior
            +-- declarative Boolean-panel training behavior
            +-- declarative timed sequence training behavior
            +-- gallery animation
```

The player validates and stages the complete next scene, runtime, and alarm
session before replacing the active scene. A failed load disposes only staging
and retains the working view. The application window and renderer are not
restarted during a scene change, and only the newest concurrent load may
commit.

## Proven on 2026-07-30

Offline/static verification:

- all JavaScript modules passed Node syntax checks;
- the Python standard-library launcher compiled;
- all seven built-in scene documents parsed;
- current asset counts are 5 Scene 1, 6 Scene 2, 7 conveyor, 10 combined tank,
  9 high/low tank, 8 radar tank, and 13 gallery;
- the page loaded Three.js only from local vendored files.

Interactive browser verification at 1280 x 720:

- Variant A rendered the conveyor scene with no browser warning/error logs.
- Conveyor **Run** changed `conveyor_run` to true, speed to `1.05 m/s`, and
  `photoeye_blocked` changed true when a carton crossed the beam.
- Selecting the tank scene changed the load counter from 1 to 2 while the URL
  and page stayed unchanged, proving runtime scene replacement.
- Tank initial level was `42.00 %` and the linear transmitter was `10.72 mA`.
- With the inlet pump running, the tank reached `100.00 %`, the transmitter
  reached `20.00 mA`, and the high-level switch became true.
- After a fresh load with the drain open, the tank reached `17.62 %`, the
  transmitter reported `6.82 mA`, and the low-level switch became true.
- Loading `tank-level.json` through **Load** selected
  `Custom: tank-level.json` and replaced the scene without restarting.
- The equipment gallery loaded as the third scene and rendered all current
  assets.
- Clicking the conveyor selected `main_conveyor` and displayed its type,
  position, length, width, deck height, and belt color in the inspector.
- Variants A, B, and C all rendered at the test viewport with an active 3D
  canvas and no horizontal page overflow.

These results prove the local player concept and UI interaction only.

## Visual mechanics and interaction proof on 2026-07-30

The user-supplied screenshots identified a conveyor roller/drum that appeared
to rotate on the wrong axis and a plain black cylinder that could not be
identified visually.

Changes and evidence:

- rollers now rotate dedicated parent pivots around their physical cross-belt
  Z axis instead of changing an already-oriented roller mesh's Euler angles;
- motor and pump couplings now rotate dedicated pivots around their physical
  shaft X axis;
- the centrifugal pump casing no longer rotates;
- motor and pump models have both a top run lamp and an emissive green band
  around the motor body;
- the former black cylinder was the generic `pipe` asset and is now a flanged
  process pipe with a cyan flow arrow and optional floor support;
- a guarded, six-blade industrial ventilation fan with stand, motor, animated
  blade pivot, and run lamp was added;
- control faceplates and button caps are direct 3D hit targets;
- the conveyor's 3D start station started and stopped the conveyor;
- the tank's 3D pump station changed `inlet_pump_run` true and increased level;
- the tank's 3D drain station changed `drain_valve_open` true;
- the gallery's 3D green button started the motor, conveyor, pump, and fan;
- the gallery's red emergency stop latched all equipment off, blocked the
  regular Run command, and required a second click to reset;
- browser warning/error logs remained empty after these interactions.

Updated asset counts are 7 conveyor, 10 combined tank, 9 high/low tank,
8 radar tank, and 13 gallery.

## Tank variant proof on 2026-07-30

- `tank-high-low.json` is a discrete-only water-tank scene with independent
  low- and high-level switch assets.
- Starting at 50%, inlet operation crossed the 75% threshold and
  `high_level_switch` became true.
- After reset, drain operation reached 22.20%, crossed the 25% threshold, and
  `low_level_switch` became true.
- `tank-radar.json` is a radar-only water-tank scene with a top-mounted
  transmitter, visible measurement cone, target ring, and echo lamp.
- At 35.00% level, radar feedback was 2.75 m and 9.60 mA.
- After inlet operation reached 51.10%, distance decreased to 1.99 m and signal
  increased to 12.18 mA.
- The original combined tank scene still loaded with its existing 42.00%,
  10.72 mA, low-switch, and high-switch points.
- Browser warning/error logs remained empty.

These variants use the same reusable `tank`, `levelSensor`,
`radarLevelSensor`, `pump`, `pipe`, `switch`, and `indicator` factory types.
They are not one-off models.

## Prior Scene 1 and Scene 2 proof on 2026-07-30

The new player now contains separate `.plcscene` versions of the two
established scenes from `Siemens-PLC-PC-Interface`.

Scene 1:

- preserves the 1.0 m conveyor, 0.5 m/s speed, 0.2 m product, and 0.5 m
  photoeye position;
- preserves the symbolic `conveyor_running` PLC command and
  `simulated_photoeye` PC feedback;
- stopped at exactly 0.50 m with `simulated_photoeye = true`,
  `conveyor_running = false`, and component state `stopped_loaded`.

Scene 2:

- preserves the 1.0 m conveyor, 0.5 m/s speed, 0.2 m product, 0.5 m photoeye,
  0.3 s pusher stroke, 80% transfer point, and 2.5 s repeat loading;
- preserves the single-solenoid/spring-return behavior;
- preserves PC feedback `part_at_pusher`, `pusher_extended`, and
  `pusher_retracted`;
- preserves PLC commands `conveyor_running` and `pusher_extend`;
- visibly stopped, extended the pusher, transferred the package, retracted,
  restarted, and loaded later packages.

This is an offline 3D behavior reproduction. It does not replace the prior
live DB14 evidence or prove this new player against TIA/PLC communication.

## `.plcscene` persistence proof on 2026-07-30

- the formal file extension is `.plcscene`;
- files are UTF-8 JSON with `fileType: "plc-visual-scene"` and `version: 1`;
- Save writes a normalized scene document through the local-only server into
  `prototype/saved-scenes`;
- saved documents appear in the scene library selector and reload without a
  player restart;
- Load accepts portable `.plcscene` files and legacy `.json` files;
- a saved Scene 1 file parsed with five assets and `conveyorStop` simulation;
- files contain scene/equipment/symbolic behavior only, not PLC IP addresses,
  DB offsets, `%I`/`%Q` addresses, or executable scripts;
- runtime position, timers, live tag values, and current animation state are
  intentionally not persisted.

## Standalone Windows EXE proof on 2026-07-30

- PyInstaller 6.21.0 built a Windows x64 one-file executable from
  `tools/serve_player.py`;
- the `prototype` player/scenes and local `vendor` Three.js files are bundled
  inside the executable;
- the VM package contains the EXE, `README-VM.txt`, and a SHA-256 manifest;
- the package does not require Python, npm, a CDN, or internet access on the
  target VM;
- the actual packaged EXE was launched with an automatically selected local
  port and returned HTTP 200 for the player page, bundled Three.js, and the
  Scene 2 `.plcscene` file;
- the packaged EXE also returned HTTP 200 for the new basic
  `lab-2-01-workstation-call.plcscene` and the complex
  `lab-2-24-robot-cnc.plcscene`;
- the packaged EXE accepted a UTF-8 Scene 1 save, persisted it under
  `saved-scenes` beside the test EXE, and served the saved file back with HTTP
  200;
- the current package bundles Snap7 plus two editable `plc-profiles` beside the
  EXE; the package smoke test imported the diagnostic adapter and returned both
  profiles with HTTP 200;
- the smoke test confirmed the listening process belonged to the packaged EXE
  and stopped all test processes afterward;
- the current `RungProof-VM.zip` SHA-256 is
  `e39d180fcc521381a2494c930e24b250faeb394f42a4c85d8544c8fa9a17a035`;
- no PLC connection or write was attempted during package testing.

This proves the locally built Windows package. It has not yet been copied to
and launched on the actual VM.

## Exercise training library proof on 2026-07-30

The photographed exercises 2.1 through 2.25 were abstracted into 25 original
simulator challenges. The retained material is limited to control concepts,
I/O relationships, and sequence categories. Names, plant settings, point names,
layouts, equipment combinations, dimensions, timings, descriptions, and
acceptance cases were rewritten for this simulator.

Implementation:

- 25 generated `.plcscene` files are selectable in the persistent library;
- small lamp/selector exercises use the declarative `booleanPanel` runtime;
- exercises 2.1-2.4 cover direct-follow, AND, inverted-input, and OR logic with
  complete truth-table cases;
- machine cycles use the declarative `sequence` runtime with named steps,
  symbolic points, safe stop state, constrained motions, and optional start
  permissives;
- reference-logic verification explicitly enables Fake PLC; production scene
  loading still defaults to controller disconnected with PLC outputs safe;
- Boolean-panel evaluation resets declared output points before each rule while
  preserving PLC-owned latch/toggle memory;
- scene files contain no executable expressions or physical PLC addresses;
- eight new reusable asset types were added: rotary switch, lift table, valve,
  drill press, robot arm, roller shutter, rotary table, and enclosed machine;
- the equipment gallery now loads 21 shared factory assets;
- `docs/TRAINING_SCENE_CATALOG.md` records the source concept, material changes,
  symbolic I/O, acceptance criterion, and scene file for each adaptation.

Verification:

- all 25 training documents passed schema validation and asset construction;
- all 50 embedded deterministic acceptance cases passed;
- all 32 built-in library descriptors resolve to a valid scene with matching
  ID and constructible runtime;
- every training scene loaded through the actual browser scene selector with a
  live WebGL canvas, correct asset/tag counts, and no error overlay;
- exercises 2.1-2.4 passed their live direct, AND, inverted, and OR state checks;
- while disconnected, an exercise input changed but its PLC-owned lamp stayed
  safe until Fake PLC was explicitly enabled;
- the lift browser proof reached its top limit with both motion outputs off;
- the robot/CNC browser proof observed `cnc_run = TRUE` only while
  `robot_run = FALSE`, then completed with both outputs off;
- browser warning/error logs were empty;
- the rebuilt standalone EXE served packaged training scenes with
  HTTP 200 during the package smoke test;
- no PLC connection or write was attempted.

This proves offline scene behavior and browser rendering. It does not prove
student ladder solutions, TIA Portal projects, PLC timing, safety functions, or
live equipment commissioning.

## Scene learning-guide proof on 2026-07-30

The player now exposes **Configuration**, **Hint**, and **Solution** for the
active scene from both the scene card and the Help menu.

- Configuration is derived from the active scene's `simulation.points`; there
  is no second manually maintained tag list that can drift.
- Every required tag shows the exact simulator name, data type, direction,
  initial value, and a purpose derived from its equipment/action binding.
- `PC` ownership is displayed as **Simulator → PLC input** and `PLC` ownership
  is displayed as **PLC → Simulator output**.
- `SIM` points and PLC points marked `role: "memory"` are identified as
  internal and excluded from the external interface tag table.
- Configuration is explicitly labeled **I/O contract — not a ladder
  solution** and contains no reference rule or sequence answer.
- Hints reveal progressively and are tracked independently for each scene.
- Solution first presents an answer warning, then requires a second explicit
  click before showing a functional reference.
- All 25 labs passed guide-schema validation and configuration-to-point drift
  checks.
- Microsoft Edge browser automation opened Configuration, revealed two hints,
  and deliberately revealed the Solution for all 25 source labs with zero
  browser console errors.
- A second Microsoft Edge pass against the rebuilt packaged EXE opened
  Configuration, Hint, and the guarded Solution entry for all 25 labs with
  zero browser console errors.

The guide supplies the scene contract and training reference only. The
training labs still require a future guarded live point-binding adapter before
a student PLC can drive the scene.

## All-scene point-contract correction proof on 2026-07-30

The Configuration popup previously showed no simulator tags for Scene 1 even
though the live runtime exposed `conveyor_running`, `simulated_photoeye`, and
three internal diagnostic points.

Root cause:

- the 25 generated training labs declared `simulation.points`;
- the seven older/custom scenes instead hard-coded metadata inside `getTags()`;
- Scene 1 and Scene 2 also carried an incomplete `symbolicPoints` summary;
- Configuration correctly read only `simulation.points`, exposing the
  incomplete migration instead of inventing a second interface list.

Correction:

- all seven older/custom built-ins now declare every runtime-visible point;
- Scene 1 declares PLC output `conveyor_running`, PC input
  `simulated_photoeye`, and three `SIM` diagnostics;
- Scene 2, the inspection conveyor, all three tank variants, and the equipment
  gallery now use the same point-contract schema;
- custom runtimes supply changing values through the declaration, so tag name,
  type, owner, and unit have one authoritative source;
- non-static scene validation now rejects missing point arrays, duplicate
  names, invalid types/owners, and type-incompatible initial values;
- the Scene Editor and both saved-scene fixtures now export complete
  `simulation.points` contracts instead of `symbolicPoints`.

Verification:

```text
SCENE_TAG_CONTRACTS_VALID: 32
DECLARED_RUNTIME_POINTS: 173
EXTERNAL_INTERFACE_TAGS: 120
PLC_CONNECTION_ATTEMPTED: FALSE
```

The contract test constructs all 32 built-in runtimes, compares every live tag
against its declaration, compares every external declaration with
Configuration, verifies the editor export and saved scenes, and proves
duplicate names are rejected. An in-app Chromium pass opened Configuration for
all 32 built-ins with zero row-count mismatches. Scene 1 showed exactly
`conveyor_running` as **PLC to Simulator output** and
`simulated_photoeye` as **Simulator to PLC input**. The equipment gallery
correctly showed no external PLC tags and listed its five internal points.

## Controller-ownership correction proof on 2026-07-30

The training player no longer treats an exercise input as permission to
synthesize PLC outputs. The player now has three distinct controller-source
states in its runtime contract:

- `disconnected` is the default and forces PLC-owned points to type-appropriate
  safe values;
- `fake-plc` must be explicitly enabled for the built-in reference controller;
- `live-plc` is reserved for the future guarded point-binding adapter and is
  not exposed as a working UI mode.

Implementation and proof:

- all 25 labs were exercised while disconnected; every operator action left
  every PLC-owned point at `FALSE`, `0`, or the empty string as appropriate;
- the selector in Lab 2.05 changed from 0 to 1 while both lamp commands
  remained `FALSE`;
- Lab 2.06 proved that even a reference output whose Fake PLC initial value is
  `TRUE` remains `FALSE` while disconnected;
- enabling Fake PLC with the Lab 2.05 selector at position 1 produced the
  reference result `bay_a_command=TRUE` and `bay_b_command=TRUE`;
- forcing the deliberately incorrect Fake PLC combination
  `bay_a_command=TRUE`, `bay_b_command=FALSE` illuminated only bay A, proving
  that the renderer follows controller outputs rather than silently correcting
  them;
- changing scenes automatically returned the controller source to disconnected
  and removed all Fake PLC forces;
- Run is rejected while disconnected, with `PLC WAIT` / `NO PLC` shown in the
  player and HUD;
- the generator/verifier rejects operator actions that directly target a
  PLC-owned point; the dust-collector start/stop, fume-hood light request, and
  inspection-light toggle were split into PC-owned requests plus Fake PLC
  latch/output logic;
- indicator lenses now use a brighter emissive material, additive glow shell,
  and local point light; browser visual proof clearly distinguished the forced
  ON bay lamp from the forced OFF bay lamp;
- browser warning/error logs were empty after disconnected input, Fake PLC,
  wrong-output forcing, and scene-change tests.

This corrects the offline ownership model and provides a deterministic test
controller. It does not create a live PLC scene binding. A real student PLC
cannot drive these scenes until the guarded symbolic point-binding adapter is
implemented and commissioned.

## PLC Scene Player application-shell proof on 2026-07-30

- all three existing layouts remain supported and are available from the
  application View menu;
- changing View A/B/C preserves the selected scene ID and reloads that scene in
  the selected workspace;
- the File menu exposes `.plcscene` open/save operations;
- the Playback menu and persistent bottom HUD expose Run, Stop, and Reset;
- the PLC menu and Player controls expose the explicit read-only Test PLC
  diagnostic;
- operator Stop holds the current simulated process state, while Reset returns
  the scene to its defined initial state;
- scene selection stays in the scene-library selector; previous/next media-style
  controls are intentionally omitted because scenes are not a linear playlist;
- the HUD displays the current scene, playback state, elapsed simulation time,
  render FPS, and the offline/no-PLC-write status;
- the player explicitly reports that live simulations have no fixed duration
  or seek operation instead of presenting a nonfunctional media scrubber;
- Help provides the keyboard/mouse controls and the offline prototype boundary;
- missing built-in scene files are removed from the playable library at launch,
  preventing incomplete concurrent scene references from creating dead menu
  entries;
- A, B, and C each rendered with one WebGL canvas, no horizontal overflow, and
  the selected Scene 2 survived A-to-B-to-C View changes;
- HUD Run/Stop controls updated both the scene simulation and displayed player
  state.

## Machine-style stop and Loop proof on 2026-07-30

The player transport now acts as a machine command surface instead of a media
timeline:

- a normal sequence completion or declared logic stop enters `SYSTEM STOP`,
  clears the scene's safe-state outputs, and leaves process inputs in their
  physically reached state;
- Start calls the scene's permissive checks before any outputs are enabled;
- Scene 1 rejects Start while the package still blocks the stop photoeye, so a
  second Start cannot move through an active stop condition;
- Scene 2 keeps its photoeye transition as a valid pusher-cycle step instead of
  incorrectly treating every sensor as a global stop;
- operator Stop enters `OPERATOR STOP`, applies the scene safe state, and holds
  the scene until another explicit command;
- an emergency stop or other interlock enters `INTERLOCK STOP` and remains
  restart-inhibited until the interlock is reset;
- the **Loop scene** checkbox automatically performs Reset then Start only
  after a normal `SYSTEM STOP`;
- every automatic loop Start re-evaluates the same controller and process
  permissives as a manual Start. Loop never bypasses a blocked sensor;
- Loop never restarts an operator Stop or interlock stop. Automatically
  restarting either condition would be inaccurate machine behavior.

The deterministic machine-stop suite passed seven cases: Scene 1 system stop,
blocked restart, loop reset/restart, operator-stop loop inhibition, an explicit
sequence stop step, normal sequence-completion loop, and guarded global Run
permissives. Live Chromium proof showed `SYSTEM STOP` with
`simulated_photoeye=TRUE` and `conveyor_running=FALSE`; the blocked restart held
`object_position` at 0.51 m; Loop displayed `LOOP RESET` and returned to
`RUNNING`; and an operator Stop remained `OPERATOR STOP` after the loop delay.
No real PLC connection was attempted.

## Per-scene Faults & Alarms popup proof on 2026-07-30

Every loaded scene now owns a fresh in-memory alarm session. The alarm UI is a
modal popup opened from **View > Faults & alarms**, the Player controls button,
or **F8**; it does not consume a permanent workspace panel.

Alarm classification is machine-state aware:

- an unplanned `SYSTEM STOP` is an alarm;
- `START BLOCKED` is a warning;
- `INTERLOCK STOP` is a fault;
- normal operator Stop and normal program completion are not faults;
- optional validated `scene.alarmRules` can raise warning, alarm, or fault
  records from symbolic scene points;
- acknowledgement changes only the local displayed record and never clears the
  active condition;
- clearing history removes only cleared records and can never remove an active
  alarm;
- loading another scene creates a separate empty alarm session.

The popup shows active, unacknowledged, and history counts plus alarm code,
severity, state, source, raised/cleared times, message, and a specific first
check. It explicitly states that the window is for simulated scene alarms and
does not acknowledge, reset, or write an alarm in a real PLC.

Deterministic tests passed system-stop alarm creation, duplicate suppression,
local acknowledgement, cleared-history retention, blocked-start warning,
declarative point fault, active-alarm retention, interlock fault, and exclusion
of normal program completion. Live Chromium proof showed Scene 1 raise one
active `SYSTEM STOP` alarm with the photoeye true and conveyor output false;
acknowledgement left the alarm active; Reset moved it to cleared history; a
blocked restart raised `START BLOCKED`; and the equipment gallery opened its
own empty alarm session. Browser warning/error logs were empty. No real PLC
connection or write was attempted.

The packaged EXE now uses PyInstaller's no-console mode. On launch it:

1. starts a hidden local-only HTTP server on an available port;
2. prefers Microsoft Edge, with Google Chrome as fallback;
3. launches the installed Chromium engine with `--app`, a dedicated local
   profile, no tabs/address bar, and a 1440 x 900 starting window;
4. uses a page heartbeat and browser-process tracking to tie server lifetime to
   the application window;
5. closes the browser process and hidden server through File > Exit player.

The actual packaged EXE passed a host launch test: one Edge app-mode process
opened, the player returned HTTP 200, the menu/HUD/Test PLC source was present,
Exit returned success, and zero packaged EXE or app-window processes remained.
This has not yet been repeated inside the actual VMware guest.

## Read-only Test PLC restoration proof on 2026-07-30

The original Tk viewer's Test function was verified before porting it. It ran
only after the guarded runtime connected and:

- read every configured absolute DB address and data type;
- compared PC-owned readback with the latest runtime values;
- checked heartbeat progress and simulation status bits;
- produced corrective actions;
- did not itself toggle PLC commands or change CPU state.

The new player now exposes **PLC > Test PLC** and a **Test PLC** button in
Player controls. The new diagnostic deliberately stops short of pretending the
offline player is already the live runtime:

- interface profiles remain separate from `.plcscene` files under
  `plc-profiles`;
- Scene 1 explicitly references the validated seven-tag DB14 profile and
  Scene 2 explicitly references the validated ten-tag DB14 pusher profile;
- Test PLC resolves only the active scene's exact `plcTestProfile` filename;
- the automatically loaded selector is locked and shows the profile filename,
  IP, rack/slot, and configured tag count;
- a scene with no configured profile, or an invalid/unavailable reference,
  shows no Run button, selects no substitute, and attempts no connection;
- the operator must still press
  **Run read-only PLC test** before any S7 connection is attempted;
- the server reuses the established validated configuration model and
  `Snap7Transport`, connects, calls only `read_many_diagnostic` twice, and
  disconnects;
- no `InterfaceRuntime` is created and no `write` or `write_many` method is
  called;
- the report checks configured address/type access, available heartbeat
  movement, and `Simulation_Enable`, `Simulation_Comm_OK`, and
  `Simulation_Timeout` when those tags exist;
- PC-owned value comparison is reported as unavailable because scene playback
  is not yet the authorized live point-binding writer;
- the local PLC POST endpoint requires an explicit same-origin read-only header,
  rejects profile path traversal, and permits only one test at a time.

The prior player selected Scene 2 by a filename prefix and silently defaulted
every other scene to Scene 1. That was unsafe because unrelated scenes could
present valid-looking but incorrect DB14 parameters. The fallback has been
removed.

Four diagnostic-server tests still pass: valid profile discovery,
two-read/zero-write success, actionable connection failure, and path-escape
rejection. Six new scene-selection tests prove exact Scene 1/2 resolution,
fail-closed behavior, invalid-reference handling, built-in references, and
path rejection. Browser proof showed the exact locked profile for Scene 1 and
Scene 2, while Lab 2.01 showed no profile control or Run button. No connection
was attempted. The profile endpoint returned two valid profiles with
`writePathPresent: false`.

No request was sent to the configured real PLC during this proof. A live result
must still be recorded on the authorized VM/PLC before this diagnostic is
considered commissioned.

## VM rendering diagnosis on 2026-07-30

The user-recorded Scene 2 run was inspected before attributing its visible
stutter to the simulator:

- the recording is 3840 x 2088, 30 FPS, and 9.4 seconds long;
- the player's own on-screen `RENDER` value was 20 FPS inside the VM;
- during a 3.73-second conveyor movement interval, 98 of 112 recorded frames
  held the carton at effectively the same screen position and the visible
  movement arrived in jumps of roughly 11 to 26 pixels;
- the same Scene 2 player outside the VM reported 60 FPS in eight consecutive
  samples while running;
- the packaged EXE's local HTTP server is not in the per-frame render path
  after the assets and scene are loaded.

The active VMware configuration was also checked:

- `mks.enable3d = "TRUE"`;
- the log reports the Vulkan renderer and 3D support;
- graphics memory is configured as 1 GB;
- the VM is configured for up to 3840 x 2160 and two displays;
- the VM has two virtual CPUs and uses virtual hardware version 11.

The evidence therefore points to the VM graphics/display path, especially the
large 4K WebGL surface and possible screen-recording overhead. It does not
support blaming the EXE packaging or a missing VMware 3D-acceleration setting.
The first controlled proof should compare the on-screen `RENDER` value at
1920 x 1080 with recording stopped, then repeat with recording enabled. If the
rate rises toward 60 FPS at the lower resolution, the bottleneck is
resolution/fill-rate in the virtual graphics path. If it remains near 20 FPS,
inspect Chrome's `chrome://gpu` status inside the VM before changing simulator
rendering quality.

## Future scene builder direction

The authoring UI should consume the same validated equipment schema as the
player. Required production capabilities are:

1. equipment palette backed by stable catalog type IDs;
2. drag/drop placement with numeric position, rotation, scale, and snapping;
3. property inspector limited to each asset type's validated configuration;
4. symbolic behavior/point binding without physical PLC addresses in scenes;
5. save/load of versioned scene JSON;
6. undo/redo, copy/paste, duplicate IDs prevented, and schema migration;
7. preview in this persistent player before any guarded PLC binding is enabled.

## Separate Scene Editor proof on 2026-07-30

A separate throwaway authoring module now exists under
`scene-editor-prototype`. It is launched with `RUN-SCENE-EDITOR.cmd` and is not
bundled into the current Scene Player EXE.

Implemented proof:

- all 21 current equipment types appear in the asset library;
- clicking a library part places the same 3D model built by the player's
  existing `AssetFactory`;
- the viewport supports orbit, zoom, pan, and equipment selection;
- stable ID, label, position, rotation, and JSON configuration are editable;
- new, delete, undo, redo, open, download, and saved-player-library operations
  are present;
- the first typed behavior recipe requires compatible conveyor, product,
  photoeye, and pusher roles, with an optional indicator;
- missing a required role prevents compilation instead of producing a broken
  scene;
- unsupported simulation types are rejected on open instead of being silently
  converted to static scenes;
- the compiled file uses the existing `conveyorPusher` schema and carries a
  complete typed point declaration: PLC commands, PC feedback, and internal
  simulator diagnostics.

Browser evidence at 1440 x 900:

- the editor rendered one WebGL canvas with no horizontal overflow;
- the five-asset starter composition reported `COMPOSITION VALID`;
- adding a motor increased the model to six assets and numeric position editing
  changed its X position to 1.25 m;
- deleting the required pusher changed the status to
  `COMPOSITION INCOMPLETE`, blocked compilation, and identified the missing
  transfer-actuator role;
- Undo restored a valid `conveyorPusher` document;
- saving produced
  `prototype/saved-scenes/editor_conveyor_pusher.plcscene`;
- the saved file contained five assets, the expected eight-point typed
  contract, and no physical PLC-address pattern;
- the persistent Scene Player loaded that saved document in View C with one
  WebGL canvas;
- a 5.2-second run observed `conveyor_running`, `part_at_pusher`,
  `pusher_extend`, `pusher_extended`, and `pusher_retracted`, plus the expected
  stopped, running, pushing, retracting, and empty component states;
- editor and player browser warning/error logs remained empty.

Architecture conclusion:

- assets should declare capabilities and typed roles rather than directly call
  one another;
- scene files should describe the simulated plant and its symbolic point
  contract, while the real PLC remains the controller;
- the editor may compile friendly typed recipes into a stable runtime graph,
  but must not accept unrestricted scene scripts;
- deterministic runtime phases should eventually apply external commands,
  integrate actuators/material movement, sample sensors, then publish feedback;
- the current `conveyorPusher` runtime is suitable for offline compatibility
  proof but still combines plant response with a demonstration controller. It
  must be split before live PLC binding.

This proves the authoring and file-handoff concept. It does not yet prove a
general Factory I/O-style component runtime, collision/physics, transform
gizmos, production catalog-property validation, or live PLC operation.

## Screenshot-backed PLC diagnostic evidence — 2026-07-30

User-supplied screenshots now prove the packaged **Test PLC** path reached the
configured Scene 2 S7 endpoint at `10.70.9.201`, rack 0, slot 1, and read the
DB14 profile without writing:

- RungProof selected `scene-2-db14-pusher-interface.json` and returned
  individual status/heartbeat results, which are emitted only after the second
  configured tag read succeeds;
- TIA Portal showed `DB14.DBD2` `PC_Heartbeat = 0` and `DB14.DBD6`
  `PLC_Heartbeat_Echo = 0`;
- `DB14.DBX10.0` `Simulation_Enable = TRUE`,
  `DB14.DBX10.1` `Simulation_Comm_OK = FALSE`, and
  `DB14.DBX10.2` `Simulation_Timeout = TRUE`;
- the Scene 2 safe-state feedback matched the profile:
  `Part_At_Pusher = FALSE`, `Pusher_Extended = FALSE`, and
  `Pusher_Retracted = TRUE`;
- PLC commands were safe:
  `Conveyor_Run = FALSE` and `Pusher_Extend = FALSE`;
- RungProof correctly remained **Controller disconnected — outputs safe**.

The two communication warnings are expected for this test. The packaged
diagnostic has no PLC write method, so it cannot increment `PC_Heartbeat`.
Therefore the PLC cannot echo progress, set `Simulation_Comm_OK`, or clear
`Simulation_Timeout`. This is screenshot-backed read-access and DB-map proof,
not live scene binding. No independent packet capture was taken.

## Not proven

- No authorized guarded live Scene 2 point exchange has been commissioned.
  Snap7 is bundled only for the explicit read-only Test PLC path in the current
  packaged product.
- `PLC` and `PC` ownership labels are proposed point directions only; the
  current data is mock in-memory data.
- The tank's 4–20 mA value is an ideal linear engineering conversion:
  `4 mA + 16 mA * level_fraction`. It does not yet prove raw analog count
  mapping, module resolution, fault currents, or a specific Siemens analog
  module.
- The radar distance is an ideal geometric distance from the modeled horn to
  the modeled fluid surface. Echo quality, dead band, blanking distance, false
  targets, foam, dielectric effects, and a specific radar model are not yet
  simulated.
- The browser animation loop is not deterministic PLC logic or real-time
  control.
- The Scene 1/2 JavaScript reproduction uses the established parameters and
  sequence but is not yet the renderer-neutral production `SceneRuntime`.
- The clickable controls are in-memory mock interactions. They do not bypass
  or replace the future guarded PLC point-binding and authorization boundary.
- Collision, accumulation, jams, acceleration, valve travel, pump curves,
  pressure, flow, and detailed process dynamics are not modeled.
- The code-generated assets are functional visual placeholders, not imported
  CAD or final production art.

## Migration gates

Do not switch the working simulator to this architecture until all gates below
are complete:

1. Define and test the supported purpose of View A, B, and C; the user has
   explicitly chosen to retain all three layouts.
2. Define the production equipment-catalog schema shared by the player and
   future scene builder.
3. Promote the `.plcscene` schema from prototype version 1 only after migration,
   schema validation, and compatibility tests are defined.
4. Move the proven deterministic component/scene logic behind a renderer-neutral
   scene-runtime interface; do not make Three.js the process model.
5. Add a point-binding adapter that consumes validated symbolic point names and
   delegates all live scene exchange to the existing guarded runtime. The
   read-only Test PLC diagnostic is not that adapter.
6. Preserve explicit `--execute` or equivalent operator authorization and print
   exact write scope before connection.
7. On scene change while connected, pause process updates, project PC-owned safe
   values if explicitly configured, disconnect or rebind safely, validate the
   next scene/point contract, then resume. Never hot-swap incompatible PLC
   contracts blindly.
8. Re-run existing offline tests plus browser acceptance tests.
9. Commission against the VM/PLC using the current 20 ms proven exchange period
   and record live evidence before replacing the current viewer.

## Recommended next proof

Keep the VM 1920 x 1080/render-FPS check as the packaging proof. For the
Factory I/O-style direction, the next software proof is a renderer-neutral
plant runtime with deterministic command, motion, sensor, and feedback phases.
Move the conveyor/photoeye/pusher behavior behind that interface and prove the
same editor-generated scene through an offline mock controller. Only after the
plant/controller split passes should the guarded DB14 adapter be introduced.

## Productization and hardening update — 2026-07-30

Working product identity:

- name: **RungProof**;
- descriptor: **PLC Visual Simulator**;
- tagline: **Build the logic. Prove the machine.**

The name has only a preliminary collision scan. It does not have formal
trademark, company-name, domain, or legal clearance.

New authoritative records:

- `docs/PROJECT_CHAT_COMPILATION.md`
- `docs/PRODUCT_REVIEW_AND_ROADMAP.md`
- `docs/SERIOUS_CODE_REVIEW.md`
- `docs/brand/RUNGPROOF_BRAND_SYSTEM.md`

Hardening now present:

- shared HTML encoding and CSP for scene-controlled text;
- symbolic ID grammar;
- authoritative equipment catalog and per-type bounded configuration;
- 256-equipment and aggregate geometry-complexity limits;
- eager runtime reference, action, binding, sequence, alarm, and point-type
  validation;
- transactional scene staging and newest-request-wins load coordination;
- Draft 2020-12 persisted-scene schema with JavaScript/Python parity fixtures;
- same-origin plus per-instance capability authorization on every local POST;
- explicit static-resource roots instead of serving the repository;
- pinned Siemens-interface source and locked Python package toolchain;
- canonical `fast`, `full`, and `release` verification lanes in
  `tools/run_checks.ps1`.

The repository still has no initial Git commit and all files are untracked.
That release blocker was not mutated because establishing the first baseline
requires an explicit source-ownership and commit decision.

Final release proof on 2026-07-30:

- `tools/run_checks.ps1 release` passed from the locked build environment;
- 14 Node tests and 13 Python tests passed;
- all 25 training scenes, 50 acceptance cases, and 32 scene tag contracts
  passed;
- the rebuilt packaged HTTP surface, authorization boundaries, saved-scene
  path, static roots, and two read-only PLC profiles passed black-box tests;
- the final rebuilt EXE opened exactly one dedicated app window and its
  authorized exit left zero RungProof or Edge app-window processes;
- the PyInstaller analysis contained no path to the adjacent
  `Siemens-PLC-PC-Interface` repository;
- a packaged-only missing `plc_diagnostics` import and early
  `$PSScriptRoot` evaluation in the two package test harnesses were found
  during release verification, fixed, rebuilt, and reverified.

This is source and local packaged proof. The remaining Tier 0 evidence is a
1920 x 1080 run on the actual target VM plus the deliberately uncreated first
Git baseline. Live PLC/TIA behavior remains unproven.

## Guarded real-PLC scene binding restoration — 2026-07-30

The packaged player previously retained only the read-only setup diagnostic
when the browser scene player replaced the earlier direct runtime. Network and
DB read access were still present, but the continuous scene-to-PLC update loop
was not wired into the player. That omission is the specific reason Run
reported `Controller disconnected — Run cannot create PLC outputs`.

The player now has two deliberately separate PLC controls:

- **Read-only PLC Check** connects, reads configured tags twice, and
  disconnects without invoking any transport write method.
- **Connect Real PLC** loads only the active scene's assigned profile, displays
  the exact scene-point mapping plus every absolute DB read/write, requires an
  explicit scope checkbox, and starts one guarded live session.

Scene 2's authorized exchange is:

- scene feedback to PLC: `part_at_pusher → DB14.DBX0.0`,
  `pusher_extended → DB14.DBX0.1`, and
  `pusher_retracted → DB14.DBX0.2`;
- PC heartbeat: `pc_heartbeat → DB14.DBD2`;
- PLC commands to scene: `conveyor_running ← DB14.DBX1.0` and
  `pusher_extend ← DB14.DBX1.1`;
- status/heartbeat reads: `DB14.DBD6`, `DB14.DBX10.0`,
  `DB14.DBX10.1`, and `DB14.DBX10.2`.

The live session reuses the pinned Siemens interface runtime with
`PLC_WATCHDOG_ONLY` safe-state policy. Browser requests drive every PLC cycle,
so a stalled/closed browser stops the PC heartbeat instead of leaving an
independent background heartbeat falsely healthy. Stop holds the visual scene
and Reset resets the visual model without closing an intentional live session.
Explicit Disconnect, scene change, application exit, stale browser cycle,
scene mismatch, transport error, or heartbeat fault invalidates the session.
PLC command points are not applied to the scene until heartbeat health is
`HEALTHY`, `Simulation_Enable` is true, `Simulation_Comm_OK` is true, and
`Simulation_Timeout` is false.

Additional ownership protections:

- only `owner: PC` scene values are sent to the live adapter;
- only configured PLC-owned points pass through each simulation's public
  `setControllerPoint` interface;
- starting, disabled, communication-not-OK, timeout, faulted, or stale cycles
  do not apply PLC command values;
- Scene 1/2 local 3D run/stop toggles are disabled during live control so they
  cannot invoke Fake PLC logic or stop the visual plant while the heartbeat
  remains active;
- automated tests use an in-memory S7 transport and never contact
  `10.70.9.201`.

The duplicate web menu strip was removed. File, View, Playback, PLC, and Help
now live inside the single RungProof product header; the native Windows title
bar remains for window controls.

Current verification:

- release lane: 25 Node tests and 22 Python tests passed;
- final independent review found and corrected two fail-safe gaps: a
  healthy-to-not-ready transition now clears previously applied PLC commands,
  and profiles/readiness now fail closed unless all three required PLC status
  BOOLs are present with exact values;
- 25 training scenes, 50 acceptance cases, and 32 tag contracts passed;
- rendered Variant A at 1280 x 720 showed one application header, the real-PLC
  control before the offline Fake PLC control, and the complete Scene 2 scope;
- the Connect button remained disabled until the exact-scope checkbox was
  selected;
- browser warning/error log: empty;
- packaged guarded profile contract, live-binding source, static roots,
  authorization failures, and saved-scene persistence passed the EXE smoke
  test;
- the rebuilt EXE opened one dedicated app window with the single-header/live
  PLC source present, then exited with zero RungProof or Edge app-window
  processes;
- `PLC_CONNECTION_ATTEMPTED: FALSE`.

Rebuilt artifacts:

- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- ZIP SHA-256:
  `b69db4d0a1fc629425a79680f48ef1daa7e346ba83f8b88bb3da4ab5b0e5a96c`.

This proves the code, guarded ownership boundary, fake-transport behavior, and
rendered UI. It does not yet prove the actual TIA project, DB14 layout,
heartbeat echo, watchdog ladder, CPU protection settings, or physical network
exchange. Those remain live commissioning evidence.

## Brand check-color update — 2026-07-30

The RungProof verification check changed from amber (`#FFB000`) to proof green
(`#16A34A`). The green check now deliberately communicates a verified,
ladder-logic TRUE/good result. Amber remains reserved for warnings and
attention states. The canonical mark, application icon, brand system, and
green-check concept sheet were updated together.

Three additional candidate directions were generated and retained under
`docs/brand/logo-concepts`: an `RP` ladder monogram, a normally-open
ladder-contact/check mark, and a compact plant-cell/contact badge. They remain
exploratory raster sheets; none replaces the canonical SVG until selected and
redrawn as a deterministic vector.

## Real-PLC Stop/Reset recording diagnosis — 2026-07-30

Two user-supplied recordings provided direct evidence for the reported
disconnect and late-run behavior change:

- recording 1 showed a healthy real-PLC session through the Stop click, followed
  immediately by a disconnected badge and reset visual scene;
- recording 2 showed the same transition and the explicit toast
  `Operator stop — real PLC session disconnected; watchdog will take authority`;
- near the end of recording 2, the first Run click occurred while the new live
  session still reported `STARTING`, so it was rejected; a second click after
  readiness started the scene;
- at 47.0 seconds, the live-point table visibly showed
  `part_at_pusher = TRUE`; by 47.5 seconds the PLC-driven push had started and
  the point was FALSE again, so a slower TIA watch-table refresh could miss the
  short event even though the PLC scan received it;
- the final Stop click again switched the control source to disconnected and
  reset the visible package/pusher state, which was the apparent late behavior
  change.

Root cause:

- the player Stop and Reset command branches explicitly called
  `_disconnectLivePlc`;
- Run looked enabled during the brief live-session STARTING state even though
  the command handler correctly rejected a not-ready start.

Correction:

- Stop now holds the visual scene without closing the real-PLC transport;
- Reset now resets and stops the visual model without closing the transport;
- both messages explicitly state that the real PLC and heartbeat remain active;
- every Run entry point is disabled until the live session reports ready;
- explicit Disconnect and safety/lifecycle failures still invalidate the
  session.

The focused source regression suite passed four cases, including the new
Stop/Reset persistence and STARTING-state Run guards. The recordings are
physical-PLC evidence supplied by the user; this correction has not yet been
retested against the physical PLC from this development environment.

The guarded binding already selects only PC-owned scene points, maps
`part_at_pusher` to profile tag `simulated_photoeye`, and writes that tag to
`DB14.DBX0.0`. A transport-level regression now explicitly proves the
`FALSE → TRUE` transition reaches that configured write path. This is local
fake-transport proof of the software boundary, not a new physical packet
capture.

## Native root-level PLC architecture - 2026-07-30

The Scene 2 release application no longer uses the browser/server runtime. It
is now a native PySide6/Qt 3D application with one dedicated PLC worker in the
same process:

```text
ConveyorPusher -> SimulationUpdateLoop -> InterfaceRuntime -> Snap7Transport
```

The calls above are synchronous typed Python calls in one worker thread. There
is no HTTP listener, JSON serialization, WebView, JavaScript runtime, browser
heartbeat, IPC process, or render-loop PLC polling. The Qt renderer only reads
immutable plant/PLC snapshots and never owns the S7 connection.

The direct contract is fixed to the reviewed Scene 2 interface:

- S7-1500 at `10.70.9.201`, rack 0, slot 1;
- one 20 ms exchange cadence;
- DB14 PC writes: `DBX0.0`, `DBX0.1`, `DBX0.2`, and `DBD2`;
- DB14 PLC reads: `DBX1.0`, `DBX1.1`, `DBD6`, `DBX10.0`,
  `DBX10.1`, and `DBX10.2`;
- point mappings are non-inverted and all symbols, directions, safe values,
  heartbeat timing, and transport timing must exactly match the reviewed
  profile.

Stop and Reset preserve the live PLC session. A transport failure reconnects
automatically but latches playback stopped, so recovery requires a fresh
operator Run. Enable, communication, timeout, or heartbeat loss follows the
same fail-closed restart rule. A reconnect replaces only the failed
transport/runtime and preserves conveyor, package, pusher, sensor, and
scene-time state; only operator Reset clears the plant.

The native scheduler skips missed cycle slots rather than issuing catch-up
bursts. Post-connect Snap7 ping/send/receive operations are configured to the
reviewed 2000 ms limit, and the window remains visible in a closing state until
the non-daemon PLC worker has actually stopped.

The independent native review's eight P1/P2 findings were corrected and added
to regression coverage. The focused native suite has 20 passing tests in the
locked PySide6 environment, including real signal ownership, minimum
photoeye dwell, PLC-command-to-model response, Stop/Reset persistence,
readiness recovery, transport recovery, plant-state continuity, scheduler
overrun behavior, exact profile rejection, startup failure, and shutdown
lifecycle.

This is intentionally a Scene 2 native vertical slice, not yet a full port of
all legacy scenes/equipment. Automated verification uses an in-memory
transport and deliberately makes no connection attempt to `10.70.9.201`;
physical PLC/TIA validation remains required.

## Project task-history compilation - 2026-07-30

The available Codex tasks for this workspace were reviewed and consolidated in
`docs/PROJECT_CHAT_COMPILATION.md`. The compilation covers the original S7
interface, scene player/3D assets, 25-scene training library, scene editor
prototype, and current RungProof native-product task. It records the decisions
that remain authoritative and identifies browser-era components as migration
sources rather than shipped runtime layers.

## Final native release evidence - 2026-07-30

The final release lane passed after the adaptive high-DPI window correction:

- 25 Node source-contract tests passed;
- 39 system-Python tests passed with 3 PySide6-only tests skipped;
- those 3 native Qt lifecycle/high-DPI tests passed in the locked PySide6
  build environment;
- 17 focused native runtime/Qt tests passed together in that environment;
- 25 training scenes and 50 cases passed;
- 32 scene tag contracts, 173 runtime points, and 120 external interface tags
  passed;
- native package self-test reported browser engine false, HTTP server false,
  and PLC connection attempted false;
- native window test reported one package process, zero listening ports, zero
  new browser processes, and clean exit;
- packaged file scan found no QtWebEngine, browser-player, Three.js, or
  `serve_player` files;
- final visual inspection showed the single RP/green-check header, Scene 2
  controls, complete native Qt 3D viewport, live-point inspector, and PLC
  health panel fitting the available desktop.

Artifacts:

- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- ZIP SHA-256:
  `2765EDF6FF703372E89579C7DC9D24F6727CAABC7B5C1B132A82C8B2CFDFB360`.

The release did not contact the physical PLC. The next acceptance gate remains
an operator-authorized live Scene 2 test in TIA/DB14.

## Native A/B/C polished-view release - 2026-07-30

The native Scene 2 application now retains all three established workspace
views instead of replacing them with one layout:

- View A - Operator console uses a control rail, central 3D viewport,
  health/equipment rail, and bottom live-point strip;
- View B - Immersive floor gives the 3D viewport priority and places the
  operator/runtime tools in compact bordered edge cards;
- View C - Engineering split keeps controls and live points on the left,
  the 3D cell in the center, and runtime/health/equipment diagnostics on the
  right.

One product header and one persistent transport HUD are shared by all views.
The `View` menu, `Alt+1` / `Alt+2` / `Alt+3`, and `--view A|B|C` select the
layout. Switching only reparents shared Qt widgets: it reuses the exact same
`NativePlcSession`, Qt 3D viewport, command actions, and snapshot stream and
does not call Connect, Disconnect, Run, Stop, or Reset.

The browser prototype remained a local visual reference only. The native
palette, spacing, panel hierarchy, four-column point table, ownership colors,
RP/green-check tile, runtime cards, status treatment, and bottom HUD were
recreated in Qt. The Qt 3D cell now includes rollers, rails, feet, drive-motor
details, carton tape, photoeye housings and beam, pneumatic cylinder/rod/plate,
limit indicators, stack-light details, floor grid, and multiple light sources.
No browser was launched for implementation or verification.

Independent visual inspection found and corrected two release defects before
packaging: View A's point strip had remained hidden after reparenting, and
object-specific button colors made disabled Run/Stop controls look active.
The independent re-review then found no remaining P0-P2 UI regressions.

Current release proof:

- 25 Node tests passed;
- 42 system-Python tests passed with 6 PySide6-only tests skipped;
- all 6 native Qt layout/lifecycle tests passed in the locked build
  environment;
- the 20-test focused native runtime/Qt suite passed;
- 25 training scenes and 50 cases passed;
- packaged self-test reported browser engine false, HTTP server false, and PLC
  connection attempted false;
- packaged window test reported one process, zero listening ports, zero new
  browser processes, and clean shutdown;
- the package contained no QtWebEngine, `serve_player`, `player.html`, or
  Three.js files;
- all three packaged A/B/C layouts were captured and visually inspected.

Current artifacts:

- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- `build\native-rungproof-view-a.png`;
- `build\native-rungproof-view-b.png`;
- `build\native-rungproof-view-c.png`;
- ZIP SHA-256:
  `E4C4B48BF9D9A270979AC693297941F445E9133F835F968360637B846217035A`.

This artifact hash supersedes the earlier single-layout release hash. Automated
verification did not contact the physical PLC; the final acceptance gate is
still an operator-authorized Scene 2 test against TIA/DB14.

## VM-safe viewport and native Test PLC restoration - 2026-07-30

The VM screenshot showing a white viewport plus duplicated/stale View A/C
panels was traced to the Qt 3D `QWindow` hosted through
`QWidget.createWindowContainer`. That native-child composition path is not
reliable on the target VM/Remote Desktop graphics stack.

The packaged default is now `SoftwareScene2Viewport`, a pure
`QWidget`/`QPainter` renderer. It consumes the same immutable
`NativeSessionSnapshot`, preserves Views A/B/C, orbit/zoom controls, equipment
state, and the direct PLC worker, but creates no native child window. Qt 3D
remains an explicit `--renderer qt3d` workstation option.

The native application now restores **Test PLC - Read-only** in both Player
Controls and the PLC menu. It reuses `run_read_only_plc_test` through a bounded
background diagnostic:

```text
connect -> read configured DB14 tags twice -> disconnect
writes attempted -> 0
```

The diagnostic never uses the persistent `NativePlcSession`. A serious review
found and corrected a command-boundary race where a rapid Connect action could
start during the first diagnostic refresh interval. `_connect` now requires
the diagnostic to be inactive and the session to be exactly `DISCONNECTED`;
both buttons and both actions are disabled before the diagnostic worker starts.

The packaged self-test now constructs the actual default viewport and observes
its renderer id, `WA_NativeWindow` state, diagnostic availability, and loaded
browser/server modules. The smoke test monitors the live self-test process for
listeners, requires a current `Analysis-*.toc`, scans the copied package and
PyInstaller analysis for forbidden browser assets, and verifies the exact
Scene 2 DB14 write scope without contacting the PLC.

Final verification:

- 26 Node tests passed;
- 48 system-Python tests passed with 11 PySide6-only tests skipped;
- all 12 native Qt tests passed in the locked PySide6 environment;
- 19 focused native UI/read-only diagnostic tests passed;
- 25 training scenes, 50 cases, and 32 tag contracts passed;
- packaged renderer: `software-qwidget`;
- packaged native child window: `False`;
- packaged read-only Test PLC available: `True`;
- browser engine: `False`; HTTP server: `False`;
- PLC connection attempted during automated verification: `False`;
- native window: one process, zero listening ports, zero new browser processes,
  and clean exit.

Artifacts:

- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- ZIP SHA-256:
  `2AFF20948AA470BB2F707390EB56A92D5C690B07F8D61243B51659841ED0FA54`.

The independent re-review found no remaining blocking runtime issue. The large
native window module remains recorded P2 architecture debt; decomposition of
the optional Qt 3D adapter, view layout, and diagnostic UI is a required gate
before Scene 3, another PLC protocol, or additional diagnostic modes. It does
not block this focused VM/Test PLC correction because extracting it now would
increase release regression risk.

## Conveyor drive realism correction - 2026-07-30

The user-supplied conveyor screenshot exposed a mechanically implausible asset:
the conveyor motor sat on the floor beside the frame without a visible power
path to a roller.

The selected reference arrangement is a direct head drive. Scene 2 products
travel from negative X to positive X, so the positive-X roller is the
discharge/head roller. The corrected power path is:

```text
discharge roller -> guarded shaft/coupling -> bearing/flange
                 -> frame-mounted gearbox -> gearmotor
```

The drive roller, gearbox output, and motor output now share the cross-belt Z
axis. The assembly has a frame bracket and guarded coupling; the conveyor
motor no longer has floor feet or an unrelated floor position.

Primary manufacturer references:

- mk Technology Group's conveyor-drive guide identifies the standard head
  drive at the discharge end and its AF direct head drive as a motor fitted
  directly to the drive shaft:
  `https://www.mk-group.com/en/products/conveyor-technology/drives.html`;
- Dorner's 2200 end-drive page identifies the integral drive shaft, gearmotor,
  and drive-mount package:
  `https://www.dornerconveyors.com/products/2200-series/2200-modular-belt-conveyor-2/end-drive`;
- Dorner manual 851-256 shows the conveyor, mounting bracket, gearmotor,
  transmission, drive and driven pulleys, tensioner, and cover as one mounted
  system:
  `https://www.dornerconveyors.com/wp-content/uploads/2017/09/851-256j.pdf`;
- Interroll RollerDrive documents the motorized-roller alternative, which
  does not use an unrelated external floor motor:
  `https://www.interroll.com/products/rollerdrive`.

Implementation:

- the reusable Three.js conveyor factory now constructs the same connected
  end-drive assembly for every conveyor asset;
- conveyor animation rotates the end-drive shaft on the roller axis;
- the native Qt 3D Scene 2 geometry uses the same discharge-end centerline;
- the supported VM-safe software viewport visibly connects the discharge
  roller, guarded coupling, gearbox, bracket, and motor;
- `docs/ASSET_REALISM_GUIDE.md` now requires primary manufacturer references,
  an explicit selected topology, support/guarding review, and geometry tests
  for future equipment assets;
- `tools/test_conveyor_drive_geometry.mjs` and the native geometry contract
  fail if the drive components leave the discharge-roller centerline;
- the native PyInstaller build no longer copies the browser-era `vendor`
  directory. Required licenses are copied separately, and the Siemens runtime
  is collected through its explicit imports. This restored the established
  package boundary that excludes Three.js and browser assets.

Verification:

- the full source lane passed 26 Node tests and 48 Python tests with the 11
  PySide6-only cases skipped under system Python;
- all 12 locked PySide6 native Qt tests passed;
- all 25 training scenes and 50 deterministic cases passed;
- 32 scene tag contracts, 173 runtime points, and 120 external interface tags
  passed;
- the supported software-renderer preview was visually inspected at
  `build\conveyor-drive-software-preview.png`;
- the opt-in Qt 3D renderer could not be captured on this workstation because
  its graphics process exited before rendering; its component alignment is
  covered by the pure geometry contract instead;
- the packaged native smoke test reported browser engine false, HTTP server
  false, and PLC connection attempted false;
- the packaged window test reported one package process, zero listening ports,
  zero new browser processes, and clean exit;
- no forbidden QtWebEngine, `serve_player`, `player.html`, or Three.js files
  were present in the native package.

Current artifacts:

- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- ZIP SHA-256:
  `2AFF20948AA470BB2F707390EB56A92D5C690B07F8D61243B51659841ED0FA54`.

No physical PLC connection was attempted. This correction proves asset
topology, offline behavior, supported-renderer output, and packaged native
startup; it does not prove the opt-in Qt 3D renderer on every target GPU or VM.

## Isometric software-renderer regression correction - 2026-07-30

The first VM-safe `QWidget` fallback solved the Qt 3D native-child white-screen
failure, but it did so by flattening Scene 2 into a front-elevation schematic.
That was a visual regression from the previously approved isometric machine
model and is not an acceptable product direction.

Root cause:

- the old fallback drew directly in screen coordinates and had no world-space
  depth, camera projection, shaded faces, or painter-sorted 3D geometry;
- the release checks proved startup and VM compatibility but did not require
  projected depth or a visual comparison with the approved 3D scene;
- the frozen/offscreen Qt font database was empty, so canvas labels could fall
  back to missing-glyph boxes.

The packaged default remains VM-safe but is now a real isometric software 3D
renderer:

- equipment is defined in world-space box and cylinder primitives;
- an orthographic orbit camera projects those primitives and globally sorts
  shaded faces for raster rendering through `QPainter`;
- drag orbit and wheel zoom remain available without OpenGL or a native child
  window;
- rollers, rails, crossmembers, legs, feet, product, photoeye, pusher, and
  stacklight are separate depth-bearing components;
- the conveyor drive preserves the corrected direct head-drive topology:
  discharge roller, shaft, guarded coupling, bearing/flange, bracket-mounted
  gearbox, and motor all share the cross-belt Z axis;
- the installed Windows UI font is loaded explicitly at runtime so frozen and
  offscreen builds render readable overlay text without redistributing it.

Regression prevention:

- `tools\test_software_3d_geometry.py` requires the packaged software renderer
  to identify as `isometric-3d`, produce a non-flat projected conveyor deck,
  preserve the required machine components, and keep the drive assembly on the
  discharge-roller axis;
- the native self-test and packaged smoke test now require renderer id
  `isometric-3d` and `nativeChildWindow: false`;
- the supported-renderer frame is captured and visually compared before a
  release is accepted.

Final verification:

- 26 Node tests passed;
- 51 system-Python tests passed with 12 PySide6-only tests skipped;
- all 15 focused geometry/native Qt tests passed in the locked PySide6
  environment;
- all 25 training scenes and 50 deterministic cases passed;
- 32 scene tag contracts, 173 runtime points, and 120 external interface tags
  passed;
- the packaged smoke report identified renderer `isometric-3d`, native child
  window `False`, browser engine `False`, HTTP server `False`, and PLC
  connection attempted `False`;
- the packaged window test completed with one application process, no listener,
  no new browser process, and clean shutdown.

Current artifacts:

- `build\conveyor-drive-isometric-preview.png`;
- `build\RungProof-VM\RungProof.exe`;
- `build\RungProof-VM.zip`;
- ZIP SHA-256:
  `9C542C191CEE4F146F22A91A16E673ECD9C4C45FD3BC8F0C970655229D486D51`.

No physical PLC connection was attempted. Qt 3D remains an explicit optional
workstation renderer; the supported package path now preserves isometric
machine quality without relying on the native-child composition path that
failed on the VM.

## PLC test-environment clarification - 2026-07-30

The PLC currently has no physical field I/O connected. PLC communication and
scene-exchange testing are therefore acceptable when Matt transfers the build
to the VM that can reach the controls network. The present development machine
cannot communicate with that PLC because it is on a different network.

Accordingly, `PLC_CONNECTION_ATTEMPTED: FALSE` in local automated evidence means
**not reachable from this development environment**; it is not a prohibition
against VM-based PLC testing and should not be described as a field-I/O safety
restriction. PLC tests still require the existing explicit operator action so
offline automated checks cannot initiate a connection unexpectedly.

## Native asset approval library and control consolidation - 2026-07-30

The first native migration pass now rebuilds all 21 legacy equipment types as
independent, reviewable assets through the supported VM-safe isometric software
renderer. The approval register is
`docs\NATIVE_ASSET_APPROVAL_REGISTER.md`; it records the selected real-world
industrial topology and primary manufacturer reference for IDs A01 through A21.
All assets remain `PENDING` until Matt explicitly approves or requests revision.
No dependent legacy scene has been represented as recreated.

Review artifacts:

- individual cards: `build\asset-review\A01-motor.png` through
  `build\asset-review\A21-machine.png`;
- contact sheets: `build\asset-review\approval-sheet-01.png` through
  `approval-sheet-04.png`;
- the legacy source inventory contains 32 scene documents, each recorded as
  `WAITING FOR ASSET APPROVAL`.

The main-screen control duplication is removed:

- the persistent bottom HUD and Playback menu expose **Run**, **Stop**, and
  **Reset** only;
- **Test PLC - Read-only** exists under the PLC menu only.

Geometry support was extended with Euler rotation on renderer-neutral
primitives so angled machine members, robot links, scissor mechanisms, and
other non-axis-aligned components retain depth in the same software renderer.
The conveyor review asset preserves a bracket-mounted guarded gearmotor aligned
with the discharge roller rather than placing an unconnected motor on the
floor.

Verification:

- 35 focused asset, geometry, runtime, and locked-PySide native UI tests passed;
- the full source lane passed 26 Node tests and 57 Python tests
  (`13` PySide-only tests skipped under system Python);
- the full lane validated 25 training scenes, 50 deterministic cases, and all
  32 existing scene contracts;
- local automated checks reported `PLC_CONNECTION_ATTEMPTED: FALSE`.

The next gate is Matt's A01-A21 asset review. Native scene recreation begins
only after every asset required by that scene is approved.

## Native asset review round 1 correction - 2026-07-31

Matt rejected visible intersections and ambiguous equipment, with the explicit
acceptance rule that an asset is wrong if it reads like an M. C. Escher drawing.
This means coordinate clearance alone is insufficient: the supported renderer's
final occlusion and silhouette must remain physically coherent at the approval
camera angle.

Corrected assets:

- A01 motor: circumferential rings were replaced by axial cooling fins;
- A02 conveyor: roller barrels now clear both channel inner faces by at least
  0.24 world units, and assembled roller end caps hidden inside the channels
  are omitted so painter sorting cannot expose them through either rail;
- A08 fan: hollow tube/flange primitives expose six actual impeller blades;
- A10 tank: a full-height external ten-segment sight gauge shows six filled
  blue segments and four empty segments without large overlapping faces;
- A15 lift: the mechanism has positive clearance below the platform;
- A16 valve: a labeled transparent cutaway exposes the butterfly disc inside
  the wafer body and large-bore pipework;
- A17 drill press: the table clears the column, the quill/spindle/chuck/bit
  chain is non-overlapping, and the three feed handles extend outward from the
  head;
- A18 robot: shoulder, elbow, and wrist joints use new faceted sphere
  primitives; shortened links and cable covers terminate at the joints.

Renderer-neutral primitives now support hollow tubes, faceted spheres, and
optional cylinder end caps. These additions keep the same VM-safe QPainter
path and do not add OpenGL or a native child window.

Verification after the correction:

- all 48 focused locked-PySide asset, geometry, runtime, and native UI tests
  passed;
- the full source lane passed 26 Node tests and 70 Python tests
  (`13` PySide-only tests skipped under system Python);
- 25 training scenes, 50 deterministic cases, and all 32 legacy scene
  contracts remain valid;
- local verification reported `PLC_CONNECTION_ATTEMPTED: FALSE` because this
  machine cannot reach the PLC network.

The revised A01, A02, A08, A10, and A15-A18 cards are `PENDING` for Matt's
second visual review. The focused review sheets are
`build\asset-review\revision-01\approval-sheet-01.png` and
`approval-sheet-02.png`. No dependent scene migration has started.

## Rejected A02 same-layer painter-order correction - 2026-07-31

The first A02 correction fixed real geometry clearance and removed assembled
roller end caps, but it did not eliminate the visual contradiction. Cylinder
side polygons were still sorted independently by average camera depth, causing
successive roller barrels to alternate in front of and behind the back rail.
Matt correctly rejected this as an M. C. Escher result.

The VM-safe renderer now carries a renderer-neutral `render_layer` from each
primitive into its generated faces and uses one shared
`sort_faces_for_painter()` function in both asset-review cards and the native
Scene 2 viewport. The conveyor assembly contract is:

- layer 0: rollers and conveyor structure;
- layer 10: both side channels, which consistently mask all roller ends;
- layer 15 in Scene 2: the carton payload, preventing the back rail from
  visually cutting through the product;
- layer 20: the discharge-end shaft, coupling guard, bearing, bracket, gearbox,
  and motor, keeping the attached drive visible outside the channel.

Verification:

- the regenerated A02 card and full native Scene 2 preview were inspected at
  full resolution and no rail changes sides relative to the rollers;
- 51 focused locked-PySide asset, geometry, runtime, and native UI tests passed;
- the full source lane passed 26 Node tests and 73 Python tests
  (`13` PySide-only tests skipped under system Python);
- 25 training scenes, 50 deterministic cases, and all 32 existing scene
  contracts remain valid;
- local checks reported `PLC_CONNECTION_ATTEMPTED: FALSE`.

A02 remained `PENDING`. Matt subsequently rejected this correction because
drawing both rails after the rollers put the physically distant back rail in
front of the roller bed. The section above records the rejected intermediate
state and is superseded by the camera-aware correction below.

## A02 camera-aware rail-depth correction - 2026-07-31

The conveyor cannot use one fixed painter layer for both side channels. At any
camera angle, the back channel must be behind the roller bed and the front
channel must be in front. The shared `sort_faces_for_painter()` function now
identifies the two `side_rail_*` roles from their projected camera depth and
orders the assembly as:

1. far/back channel;
2. rollers, crossmembers, and payload;
3. near/front channel;
4. discharge-end shaft, coupling, bearing, bracket, gearbox, and motor.

The former static rail layer and static payload layer were removed. Regression
tests verify the physical relationship at yaw 8, 34, and 72 degrees, covering
the full supported drag-orbit range. Full-resolution A02 and native Scene 2
captures at those angles were inspected; the back rail remains behind the
rollers, the front rail remains in front, the carton remains between the
channels, and the attached end drive remains readable.

Verification:

- all 51 focused locked-PySide asset, geometry, runtime, and native UI tests
  passed;
- the full source lane passed 26 Node tests and 73 Python tests
  (`13` PySide-only tests skipped under system Python);
- 25 training scenes, 50 deterministic cases, and all 32 existing scene
  contracts remain valid;
- local checks reported `PLC_CONNECTION_ATTEMPTED: FALSE`.

A02 remains `PENDING` for Matt's explicit review. No dependent scene migration
has started.

## Native scene review batch S03-S06 - 2026-07-31

Matt directed creation of the next four scenes without waiting for another A02
approval response. The authoritative order comes from `BUILTIN_SCENES`
immediately after `scene-2-conveyor-pusher`:

1. S03 `conveyor-cell` - Conveyor Inspection Cell;
2. S04 `tank-level` - Tank Level / 4-20 mA;
3. S05 `tank-high-low` - Water Tank High/Low Switches;
4. S06 `tank-radar` - Water Tank Radar Level.

`tools\native_scene_library.py` now composes renderer-neutral native assets into
those four complete cells. `tools\native_scene_review.py` renders individual
approval cards and a four-scene contact sheet through the same VM-safe
QWidget/QPainter path used by the supported native renderer. It constructs no
PLC session and reports `PLC_CONNECTION_ATTEMPTED: FALSE`.

Scene details:

- S03 has a discharge-end-driven roller conveyor, three cartons, an opposed
  photoeye pair mounted outside both channels, an operator station, and a
  stacklight. Prefixed reusable conveyor instances now retain the camera-aware
  far-rail/rollers/near-rail ordering at yaw 8, 34, and 72 degrees.
- S04 has a connected centrifugal inlet pump, vertical riser and top header,
  outlet piping, process tank with a 42% four-segment sight indication, low and
  high point switches, and a distinct analog transmitter/display.
- S05 retains only discrete low/high sensing, shows a 50% five-segment sight
  indication, and has no analog or radar transmitter.
- S06 shows 35% level, a top-mounted radar transmitter, and a new tapered
  `frustum` measurement volume from antenna to liquid surface. The frustum
  replaces a rejected stepped-cylinder visualization that resembled piping.

Approval artifacts:

- `build\scene-review\S03-conveyor-cell.png`;
- `build\scene-review\S04-tank-level.png`;
- `build\scene-review\S05-tank-high-low.png`;
- `build\scene-review\S06-tank-radar.png`;
- `build\scene-review\scene-approval-sheet-01.png`.

Verification:

- all 59 focused locked-PySide scene, asset, geometry, runtime, and native UI
  tests passed;
- the full lane passed 26 Node tests and 81 Python tests
  (`13` PySide-only tests skipped under system Python);
- all 25 training scenes, 50 deterministic cases, and 32 source scene/tag
  contracts remain valid;
- local review generation reported `PLC_CONNECTION_ATTEMPTED: FALSE`.

S03-S06 are `PENDING` visual scene approval. They intentionally remain outside
the live native selector because no approved native PLC profile/runtime exists
for them; the application must fail closed rather than reuse Scene 2's DB14
mapping. Native behavior/profile migration follows visual approval.

## Common foundation and cumulative labs - 2026-08-04

The reusable PLC/watchdog foundation is documented in
`docs/PLC_BENCH_SETUP.md`. It preserves the reviewed heartbeat and simulation
status contract and separates common watchdog points from scene-specific
process points.

S03-S06 setup documents include exact bench-assignment names, direction,
machine operation, watch-table checks, and fault behavior. These scenes remain
independent process examples and do not borrow Scene 2 DB14 process mappings.

All 25 generated labs now contain machine guides and cumulative lineage:
sequence number, common foundation, inherited lab, retained tags, added tags,
changed tags, and previous acceptance identity. This is the simulator and
documentation contract for a cumulative student PLC project. The repository
still does not contain the student's TIA ladder blocks; those remain bench-side
until TIA V17 exports are supplied and reviewed.

## Launch-readiness planning baseline - 2026-08-05

The first recommended external launch is a controlled instructor/controls-lab
pilot, not a broad paid release or generic live-PLC product. The supported
surface is the native Windows application and Scene 2 vertical slice. S03-S06,
the 32 source scene contracts, and the Scene Editor remain review/prototype
surfaces until their separate native gates pass.

The dependency-ordered execution plan and objective exit gates are recorded in
`docs/LAUNCH_READINESS_PLAN.md`. The critical blockers are: inconsistent
version/product truth across current and legacy documents; pending Scene 2
visual and exact 1920x1080 VM acceptance; no named TIA V17/CPU import and bench
acceptance for the exposed DB14 write path; no remote/tagged release baseline;
unsigned distribution; incomplete Qt commercial-distribution review and
product legal/support documents; and no observed pilot evidence.

The current planning baseline is not a release acceptance result. On 2026-08-05
`tools/run_checks.ps1 fast` passed 26 Node tests and 90 Python tests with 15
expected PySide6-only skips under system Python and reported no PLC connection
attempt. The existing `RungProof-VM-v0.1.18.zip` hash is
`86B17222B884A7F6849255BCBB711F0F0B11391DD6EF65A06A57F1F781EF91C0`.
The final release must be rebuilt from a clean tagged commit and independently
pass source, package, visual, and applicable live-bench gates.

## Launch-readiness implementation - 2026-08-05

The launch scope is now enforced, not merely documented. `VERSION` defines
`0.2.0-pilot.1` across source/package metadata. The default pilot package has a
`PILOT-CAPABILITIES.json` manifest with `realPlcWritesEnabled: false`; the UI
hides and command-guards Connect Real PLC. A PLC-write-enabled build requires
an explicit switch. That internal candidate exists to perform the bench gate;
passing live evidence is still required before an external support claim.

Validated security corrections require the exact PC-owned point set each
cycle, require the PLC heartbeat echo to match the expected previous PC
heartbeat, bound scene files and repeat-load intervals, and reject non-loopback
Host values on the archived development server. Python build artifacts are
SHA-256 locked, the build environment is recreated and audited exactly, the
vendored Siemens-interface snapshot has a verified source manifest, and the
package carries a CycloneDX SBOM plus whole-package hashes.

Current local evidence:

- `full`: 28 Node tests and 103 Python tests passed, with 17 expected PySide
  skips under system Python; all training-scene/tag contracts passed;
- locked PySide environment: 19 of 19 native Qt tests passed;
- package integrity: 1,256 files passed;
- packaged self-test: correct version/renderer, PLC writes disabled, no browser,
  server, listener, or PLC connection attempt;
- window lifecycle: one process, zero listeners/browsers, clean Close;
- dated exact-lock `pip-audit`: no known vulnerabilities found.

The local candidate ZIP hash is
`c433b0a83a95bcd0cd0f405cd6768370c45eb7ab5980dae462d5c55fed990097`.
This is not a releasable artifact: the working tree is intentionally uncommitted
and therefore the clean release lane has not run. Remaining external gates are
recorded in `docs/RELEASE_CANDIDATE_RECORD_0.2.0-pilot.1.md` and the release
checklist. The formal security backend also remains incomplete because it
rejects the Windows-style paths generated by its own inventory preparation.

## PLC-led pilot scope correction - 2026-08-05

Matt clarified that he is the sole current tester and the present product goal
is testing real ladder logic against a reachable live bench PLC. The native
application is not expected to execute or emulate ladder logic. The prior
decision that a visual/read-only package could serve as the pilot was wrong:
without the guarded live DB14 exchange, the pilot cannot perform its core job.

The build remains fail-closed by default, but `-EnableRealPlc` now deliberately
creates the internal PLC test candidate without requiring the circular input
of a completed bench-acceptance record. The candidate still starts
disconnected and requires exact-scope operator authorization. Live TIA/CPU/DB14
results are then recorded as acceptance evidence before any external delivery
or compatibility claim. Offline reference-controller development is deferred.

The enabled package now includes an offline `BENCH-PREFLIGHT.ps1` that verifies
package integrity, the live capability manifest, the exact Scene 2 profile,
and records OS/target/file hashes without contacting the PLC. It generates a
machine-readable result template. `VALIDATE-BENCH-RESULT.ps1` rejects missing,
failed, or hash-mismatched TIA/live observations and creates a bound acceptance
record only after every required result is explicitly recorded as passing.

## No-Step product contract correction - 2026-08-05

Matt confirmed from the live VM build that RungProof does not use a Step
option. The supported playback surface is Run, Stop, and Reset only. Step is
not a pilot control and is not a bench-acceptance requirement. The stale
`stepPassed` template/validator requirement was removed. The internal legacy
hook remains unexposed so the executable already under live test does not need
to change mid-bench. The revised validator deliberately ignores a legacy
`stepPassed` field so an in-progress bench result created by the earlier
preflight does not need to falsify or recreate evidence.

## Disconnect telemetry truthfulness correction - 2026-08-05

Live bench testing found that explicit **Disconnect Real PLC** correctly ended
the session and the PLC watchdog correctly drove commands safe, but the native
UI retained the last connected health/status and PLC-owned command samples.
The defect was in two state-projection seams: non-connected session snapshots
retained cached PLC telemetry, and the point tables repainted only when the PLC
cycle number changed.

The runtime now invalidates heartbeat, PLC status, and PLC-owned command
samples immediately on `CLOSING` and throughout `DISCONNECTED`, `CONNECTING`,
and `RECONNECTING`; unavailable values render as `--`. The native window also
repaints on connection-state changes even when no new PLC cycle exists. Local
plant/SIM state remains available, and the guarded write scope, watchdog,
automatic reconnect, and fresh-Run requirement are unchanged.

Regression proof covers both the immediate Closing snapshot and a same-cycle
Connected-to-Disconnected Qt repaint. Source verification passed 114 Python
and 28 Node tests; the locked Qt suite passed 20 of 20. The rebuilt enabled
candidate passed native executable smoke, package integrity, and visible-window
lifecycle tests without attempting a PLC connection. Final `disconnectSafe`
acceptance still requires one focused live recheck of this corrected UI against
the TIA watch table; the existing copied bench evidence was not changed.

The retained baseline acceptance is tied to the earlier executable and cannot
be relabeled as proof of the corrected binary. The package now supports a
hash-bound delta qualification: `BENCH-PREFLIGHT.ps1` can bind a generated
`BENCH-DELTA-RESULT.json` to both the corrected preflight and unchanged
baseline acceptance, while `VALIDATE-BENCH-DELTA.ps1` verifies the full
baseline chain, required pilot.1-to-pilot.2 version pair, unchanged
profile/target, changed executable, every
affected live observation, and Matt's new approval. Automated evidence tests
cover complete acceptance, incomplete rejection, and profile-contract
rejection. A packaged offline proof generated the delta template from the
retained baseline and correctly rejected it while blank; no PLC connection was
attempted and the retained baseline files were not modified.

## Corrected candidate version identity - 2026-08-05

The telemetry-fixed executable must not share `0.2.0-pilot.1` with the accepted
baseline. The corrected candidate is therefore `0.2.0-pilot.2` across
`VERSION`, package metadata, UI/runtime version lookup, SBOM, folder, ZIP, and
candidate records. Pilot.1 remains an immutable accepted baseline whose notes
record the stale-telemetry blocker. The change-specific delta validator now
requires exactly a pilot.1 baseline and pilot.2 current preflight, in addition
to the unchanged profile and target contract and a changed executable hash.

The release lane now accepts an explicit `-EnableRealPlc` switch and forwards
it to both `build_vm_exe.ps1` and the enabled-capability executable smoke test.
This prevents a clean, green release run from silently qualifying the default
read-only package as the PLC-led pilot. The pilot release command is
`tools\run_checks.ps1 release -EnableRealPlc`; it remains intentionally blocked
until the intended 54-entry working tree is reviewed and committed.

## AAA shell refresh - 2026-08-07

The native shell now uses the canonical RungProof SVG mark in the window and
header, separates tools from scene selection, adds an explicit PLC boundary
help surface, and labels point direction as `SIMULATOR -> PLC` and
`PLC -> SIMULATOR`. Disconnected operation is presented as a local plant view
with PLC outputs not exchanged and physical PLC state not verified. A valid
photoeye detection uses amber rather than fault red. These are UI and renderer
presentation changes only; the guarded PLC contract and playback behavior are
unchanged.

The rollback point before this refresh is Git commit `28010d6` and tag
`pre-aaa-refresh-20260807`. Source capture evidence was generated in
`build/aaa-refresh-capture-2`; the locked native Qt suite passed 20/20 after
the refresh. The remaining AAA gap is authored industrial asset fidelity and
inspection interaction, which requires a separate visual asset/rendering pass
and must not be claimed complete from shell polish alone.

## Native static authoring review workspace - 2026-08-08

The source-mode Scene Editor now opens a bounded native Qt static authoring
workspace. It composes the 21 reusable native asset types, supports asset
selection and add/delete, edits position/yaw/uniform scale, and saves or
reopens validated symbolic `.plcscene` drafts. It intentionally excludes
simulation points, behavior recipes, PLC profiles, addresses, controller
fields, Run/Stop/Reset, and transport creation. The packaged EXE keeps the
editor disabled so the pilot remains a simulator/player.

The authoring contract is enforced by `tools/native_static_editor.py` and its
round-trip/rejection tests. Rendered evidence is in
`build/native-static-editor-desktop-r2.png` and
`build/native-static-editor-compact-r1.png`. The first hostile review found
palette overflow; the revised palette wraps labels and removes horizontal
scrolling. Remaining quality work must continue through the same render/review
loop; this slice is not a release or live-PLC acceptance claim.

The authoring viewport now also exposes stable semantic selection targets for
each placed asset. Selecting from either the draft list or the viewport keeps
the cyan callout, selection envelope, inspector row, and numeric transforms in
agreement. Delete requires explicit confirmation. Selected-state evidence is
`build/native-static-editor-selected-r2.png` and
`build/native-static-editor-selected-compact-r2.png`; hostile review found no
P0-P2 defects. This remains symbolic inspection only and creates no PLC
session.

The file-flow pass adds collision-aware staging for new assets, truthful
`UNSAVED DRAFT` source identity, retained draft IDs/paths, guarded New/Open/
Close/Delete transitions, and visible dirty-state messaging. The selected
file-flow evidence is `build/native-static-editor-fileflow-unsaved-r9.png`
and `build/native-static-editor-fileflow-compact-r9.png`. Hostile review found
no P0-P2 issues after the final copy and compact-row corrections. The source
lane passed 156 Python tests and 28 Node tests, and the locked native Qt suite
passed 31/31 after the delayed-list callback correction. This is still not a
live-PLC acceptance or whole-product completion claim.

The next authoring pass adds bounded in-session Undo/Redo history for
symbolic add, delete, transform, rename, new-draft, and reopen transitions.
The history path is covered by a dedicated locked-Qt test proving add -> undo
-> redo restoration, and rendered evidence is in
`build/native-static-editor-history-r1.png` and
`build/native-static-editor-history-compact-r1.png`. Hostile review found no
P0-P2 issues; the broader product remains in active AAA iteration.

The view-continuity pass persists bounded editor-only yaw, pitch, zoom, and
pixel-pan state in `editorView`. Save/Open now restore the inspection camera,
while orbit/zoom/pan changes participate in the existing unsaved-change guard.
The viewport and document validator share the same reachable camera bounds;
non-finite values, unknown keys, malformed state, and excessive pan are
rejected. Hostile review found and corrected the initial stale-dirty, range
mismatch, and non-finite-value defects. The source lane passed 160 Python and
28 Node tests; the locked native Qt suite passed 32/32, packaged smoke and
window lifecycle passed, and release evidence was collected under
`build/release-evidence/v0.2.0-pilot.2`. The hostile visual acceptance pass
also cleared saved/reopened desktop and compact captures in
`build/native-static-editor-view-persistence-saved-r3.png`,
`build/native-static-editor-view-persistence-reopened-r3.png`, and
`build/native-static-editor-view-persistence-compact-r3.png`. This is not
whole-product completion; the next loop continues native authoring depth and
industrial interaction fidelity.

The following authoring loop adds a `Duplicate` action that preserves the
selected asset's type, yaw, and uniform scale while choosing a collision-free
orthogonal staging slot and generating a unique symbolic id. Compact palette
labels now disable text elision so equipment identity remains inspectable at
narrow widths. The dedicated locked-Qt duplicate test passes, the source
contract tests pass, and the rebuilt package passed the 33-test locked native
Qt suite, package smoke, window lifecycle, and release-evidence collection.

The transform-authoring loop coalesces repeated numeric spinbox changes into
one Undo/Redo transaction, commits pending transforms before Save or other
destructive actions, and labels coordinates as symbolic scene units/degrees.
The compact palette now uses explicit engineering abbreviations with short
type codes while retaining full labels in tooltips and search matching. The
locked Qt suite passed 35/35, the full source lane passed 163 Python and 28
Node tests, hostile compact visual review found no P0-P3 issues, and the
rebuilt package passed smoke, window lifecycle, and release-evidence checks.

The next polish loop binds guarded Ctrl+Z/Ctrl+Y shortcuts to the native
authoring window while yielding to text-field editing. The locked native Qt
suite passed 36/36 after packaging; smoke, single-window lifecycle, and clean
release-evidence collection also passed for the resulting checkpoint.

The asset-identity loop adds a coalesced editable `ASSET LABEL` field. Full
labels stay in the draft list, inspector, and saved symbolic document, while
the viewport derives a concise overlay label to protect topology visibility.
The locked Qt suite passed 37/37, the full source lane passed 166 Python and
28 Node tests, hostile desktop/compact review found no P0-P3 issues, and the
rebuilt package passed smoke, single-window lifecycle, and release-evidence
collection.

The grid-snap loop adds explicit optional rounding for position, yaw, and
uniform scale, with visible `POS .25 / YAW 15° / SCALE .05` semantics. The
locked Qt suite passed 38/38 after packaging, the full source lane passed 168
Python and 28 Node tests, hostile desktop/compact review found no P0-P3
issues, and package smoke, single-window lifecycle, and release evidence all
passed.

The inspection workflow loop adds `Frame` for the selected asset. It computes
a bounded camera fit from the rendered inspection outline, centers the target,
preserves symbolic geometry, and correctly marks the persisted view dirty. The
locked Qt suite passed 39/39, the full source lane passed 169 Python and 28
Node tests, hostile desktop/compact review found no P0-P3 issues, and package
smoke, single-window lifecycle, and release-evidence collection passed.

The label edge-case pass restores the last valid asset label if an operator
clears the field before committing, preventing a transient blank inspector
from diverging from the saved/list identity. The rebuilt package again passed
the 37-test locked Qt suite, smoke, single-window lifecycle, and release
evidence collection.

The copy/paste authoring loop adds a symbolic draft-list context menu and
guarded Ctrl+C/Ctrl+V shortcuts. Pasted assets receive fresh collision-free
IDs, preserve authored type/yaw/scale, and remain behavior-free. The visible
`ASSET LIST COPY / PASTE` hint scopes keyboard behavior away from text fields.
The locked native Qt suite passed 40/40 after packaging, the full source lane
passed 170 Python and 28 Node tests, hostile desktop/compact review found no
P0-P3 issues, and package smoke, single-window lifecycle, and release evidence
collection passed.

The compact alarm-priority loop makes an active event auto-open the EVENTS
pane at the 960x520 breakpoint until the operator explicitly chooses another
tab. It adds a visible `ACTIVE ALARM Â· EVENTS PRIORITIZED` cue, preserves the
full alarm detail and acknowledgement actions, and uses compact-aware scene
scaling so the alarm-relevant equipment remains in frame. Focused native Qt
coverage passed 41/41 after packaging, the full source lane passed 171 Python
and 28 Node tests, hostile desktop/compact review found no P0-P3 issues, and
package smoke, single-window lifecycle, and release-evidence collection passed
for revision `892ba0e`.

The compact points inspection loop tightens the points-panel geometry so the
first three rows in each table remain fully visible at 960x520, and labels
additional diagnostics explicitly as `SCROLL FOR N MORE`. The rendered
desktop/compact review passed with no P0-P3 findings; the focused Qt
regression now covers the truthful compact overflow cue.

The alarm investigation loop keeps a selected asset's identity, type, source,
tag/value, and permissive context visible beside an active alarm on desktop.
The redundant console button yields that space only while inline alarm actions
are present; compact alarm priority and event actions remain unchanged. The
focused Qt suite and hostile desktop/compact review passed with no P0-P3
findings.

The compact alarm-source loop keeps a selected asset's identity, tag/value,
quality, and permissive state inside the active event card at 960x520. The
summary uses explicit labels and compact spacing so Acknowledge/Clear remain
fully visible; desktop retains the expanded source-asset card. Hostile
desktop/compact review passed with no P0-P3 findings.

The authoring handoff loop adds a symbolic `DRAFT GATE | VALID` state and a
read-only validated preview. Validation reuses the scene contract, rejects
invalid drafts, invalidates after edits, and keeps PLC transport/runtime
behavior disabled. The preview reports symbolic provenance and the saved
handoff boundary; hostile desktop/compact review passed after replacing
encoding-sensitive separators with ASCII delimiters.

The interactive Review Player loop replaces the screenshot-only preview with a
live VM-safe viewport handoff. It clones validated symbolic geometry, camera,
selection, and inspection targets without creating runtime behavior or a PLC
session. The handoff explicitly reports `VALIDATED UNSAVED DRAFT`, `PLC
DISABLED`, `NO TRANSPORT`, symbolic provenance, and no runtime behavior. The
compact breakpoint preserves draft identity/source state and the complete
select/orbit/pan/zoom legend, while fitting the equipment more prominently.
The locked native Qt suite passed 12/12 for this focused editor scope, and
hostile desktop/compact visual review passed with no P0-P3 findings on the
final r4 compact render.

The local training-scenario loop extends the validated handoff with a bounded
typed `reviewScenario`: READY, LOCAL CYCLE, and COMPLETE steps; BOOL review
points; and a local interlock alarm. `NativeDraftReviewRuntime` provides
deterministic Run/Stop/Reset plus Raise/Acknowledge/Clear behavior with no
wall-clock dependency, PLC profile, transport, or arbitrary execution.
Malformed scenarios fail closed before handoff. The player now exposes state,
step, point, and alarm diagnostics, changes the primary action to match legal
state transitions, and makes local outputs/alarm state visible in the
viewport. Desktop and compact hostile review passed with no P0-P2 findings;
the remaining badge wording polish was aligned before regression. The full
source lane passed 178 Python and 28 Node tests, including the new runtime
coverage.

The authoring-scope loop removes the hidden-default gap from the local review
scenario. Static Scene Authoring now exposes three bounded sequence labels and
the interlock ID/message in a clearly labeled `LOCAL REVIEW SCENARIO` section.
Those fields are included in the validated document, saved/opened with the
draft, and captured by symbolic undo/redo history. Compact inspector layout
keeps both authored asset identities visible, opens the alarm message at its
meaningful beginning with a full-value tooltip, and keeps the callout near the
selected asset without bisecting the equipment. Hostile desktop/compact review
passed with no P0-P3 findings.

## Product-truth and startup-lifecycle correction - 2026-09-10

A fresh program review found that the normal native product exposed Workspace
sign-in, package sync, and evidence-upload language even though the only
implementation is an in-memory deterministic fixture. The normal product now
hides the Workspace menu and badge and labels event evidence `LOCAL ONLY`.
The fixture remains reachable only through the explicit `--demo-workspace`
visual-QA capture path. No hosted service or upload capability is claimed.

The same review found a startup cleanup gap after the non-daemon
`NativePlcSession` was created but before the existing protected UI-build
block began. All fallible initialization after session creation is now inside
the cleanup guard; a regression injects workspace-client construction failure
and proves that the session closes.

The release lane now runs both `tools.test_native_qt` and
`tools.test_native_static_editor_qt` under the locked PySide6 environment.
The source launcher and README use `python -m tools.rungproof_native`, avoiding
the mixed package/direct-import failure exposed by the documented script path.

Verification on 2026-09-10:

- focused locked Qt/editor/release-metadata suite: 57 passed;
- full lane: 28 Node tests passed, 182 Python tests ran with 45 expected
  system-Python Qt skips, 25 training scenes and 50 cases passed;
- direct `RUN-3D-PLAYER.cmd --help` entry-point smoke passed;
- disconnected 1920x1080 Views A/B/C were rendered without a PLC connection;
  View A visibly contained no Workspace surface and used local-only evidence
  wording.

This is source and rendered-offline proof only. It does not complete the
pilot.2 live TIA/S7-1500/DB14 delta acceptance or authorize external release.

The PLC-enabled internal package was rebuilt on 2026-09-10 with
`tools\build_vm_exe.ps1 -EnableRealPlc`. Its first packaged self-test exposed
a PyInstaller 6.21 / Qt 6.11 dependency collision: PyInstaller placed the
versioned ICU 78 implementation at package-root `icuuc.dll`, shadowing the
Windows unversioned ICU compatibility API expected by `Qt6Core.dll`. The
result was `ImportError: DLL load failed while importing QtCore: The specified
procedure could not be found.` A fresh-copy differential probe passed when
only that conflicting DLL was removed. The build now removes it before package
hashing, with release-metadata regression coverage.

Final offline package evidence:

- PLC capability: `operator-authorized-live-bench`, enabled;
- exact write scope: `DB14.DBX0.0`, `DB14.DBX0.1`, `DB14.DBX0.2`, and
  `DB14.DBD2`;
- packaged self-test: pass, with no PLC connection attempt, browser engine,
  HTTP server, native child window, or listener;
- native application window: one process, clean exit, zero new browser
  processes, zero listening ports;
- locked native player/editor/release-metadata suite: 58 passed;
- package integrity: 1,305 files passed;
- versioned ZIP: `build/RungProof-VM-v0.2.0-pilot.2.zip`;
- ZIP SHA-256:
  `9D15C6EC82B33B865622AC7E5FC67726FCFA072AE638A5210D6F5F5B6510EE4D`.

This artifact is enabled for the controlled isolated bench but is not yet
pilot.2 live-accepted. It must still complete the hash-bound disconnect-
telemetry delta procedure against the exact supported TIA V17 Update 9,
CPU 1512SP-1 PN V2.9, standard DB14, and isolated no-field-I/O bench.

## Native enterprise asset-catalog expansion - 2026-09-16

The native renderer-neutral asset library expanded from 21 to 50 distinct
equipment types. The first 15 new builders cover an inline gearmotor, slider-bed
belt conveyor, twin-chain pallet conveyor, ISO pneumatic cylinder, parallel
gripper, pallet, tote, bulk hopper, storage silo, machine safety fence,
interlocked safety gate, safety light curtain, M18 proximity sensor, control
panel, and VFD cabinet. Each builder includes recognizable mechanical
topology, supports/mounting details, and equipment-specific fabrication cues.
The second tranche adds a rotary-screw compressor, air receiver, desiccant
dryer, hydraulic power unit, plate heat exchanger, mixer/agitator, platform
scale, barcode scanner, vision camera, pop-up transfer, conveyor turntable,
vertical lift, swing-arm diverter, and autonomous mobile robot.

`tools/native_asset_catalog.py` is now the canonical searchable catalog seam.
It provides categories, tags, reference metadata, and typed symbolic command,
feedback, unit, and interlock contracts for every renderable asset. Validation
requires one contract and one catalog item per asset, sequential approval IDs,
and rejects physical PLC address concepts in asset point names. The native
Asset Library inspector shows the new assets' category and control contract.

The VM-safe renderer quality floor increased from 14 to 24 radial segments for
cylinders, tubes, and frustums, and to 24 by 12 segments for spheres. All 50
asset cards and nine contact sheets rendered offline under
`build/asset-review-20260916-enterprise-50`; the generator reported
`PLC_CONNECTION_ATTEMPTED: FALSE`. The complete native regression discovery
lane passed 135 tests under the locked PySide6 environment.

This is a substantial catalog foundation, not a claim of feature parity with
Visual Components or Factory I/O. Remaining enterprise work includes
parametric geometry variants, authored animation/kinematic definitions,
runtime behavior adapters, LOD/material systems, editor palette integration,
and additional utilities, process, warehouse, mobile-robot, and sensor asset
families.

## Clean-sheet Godot successor started - 2026-09-16

The primitive/QPainter catalog was rejected as the long-term visual platform.
Increasing tessellation did not solve the exposed polygon-edge/faceted render
appearance, and catalog quantity without production-quality modeling was not
accepted. The native pilot remains intact as a controls/safety reference.

A separate `rungproof-next` program now establishes the clean-sheet product on
Godot 4.7.2 .NET, with Blender source models and glTF 2.0/PBR delivery assets.
The production catalog intentionally starts empty; no legacy primitive model is
grandfathered into it. The initial portfolio plan targets 850 production asset
families and at least 3,000 configured variants across facility, structures,
material handling, loads/packaging, robotics, machines, process, utilities,
sensors/inspection, controls/electrical, safety, and passive hardware.

The asset contract supports optional symbolic signals, connectors, kinematic
axes, collision geometry, LODs, thumbnails, and quality evidence. Passive
parts do not receive invented I/O. Admission requires context-free blind
recognition at 0.80 confidence plus topology, material, scale, and animation
review. Direct PLC transport remains outside the Godot process behind a
versioned local IPC seam and the existing guarded runtime principles.

The project now carries a workspace-local verified toolchain under its ignored
`.tools` folder: Godot 4.7.2 .NET, Blender 5.2.2 LTS, and .NET SDKs 8.0.425 and
10.0.401. Godot 4.7.2 requires the .NET 10 host. The clean-sheet C# project
builds with zero warnings/errors, imports glTF successfully, and passes a
headless runtime smoke test.

The first authored asset is a 600 mm x 6 m supported belt conveyor with channel
frame, adjustable legs, carry/return rollers, crowned head/tail drums,
pillow-block bearings, guarded gearmotor, junction box, and E-stop pull cord.
It has Blender source, glTF delivery, separate collision proxies, four review
renders, a thumbnail, typed symbolic controls, three connection points, and a
working ramped conveyor controller that bound 18 rotating nodes in Godot. It
remains in `candidates.catalog.json`, not production: independent blind review,
topology/material acceptance, and animation review are still open.

On 2026-09-17, full-resolution inspection rejected the initial conveyor
assembly. It mixed bulk-conveyor and unit-load geometry, used disconnected belt
slabs, placed safety hardware in the product envelope, and contained floating
guards/take-up/control details. The model was rebuilt as a coherent low-profile
slider-bed conveyor with a continuous wrapped belt, compact drums, stainless
bed, return rollers, connected screw take-ups, direct gearmotor, mounted safety
devices, pull-cord guides/anchor, fixed controls, cable tray/service loops, and
three braced supports. Seven full-resolution views are now required and a
Blender mechanical check prevents the known belt, cord, take-up, and missing-
view regressions. The asset still remains a candidate pending independent blind
review, texture maps, topology/scale evidence, and animated Godot captures.

The 2026-09-17 acceptance pass added authored belt base-color, roughness, and
normal maps with continuous path UVs; removed softbox reflections that appeared
as loose white geometry; and remounted the E-stop station on an unambiguous
below-frame drop bracket. The review set now contains seven inspection views,
stopped/running motion-witness frames, a banded one-meter scale reference, a
source-topology overlay, and a native 1600x900 Godot Vulkan capture. Runtime
visual inspection caught and corrected both excessive camera distance and an
incorrect Blender-Z-up to Godot-Y-up camera conversion. The generated source
passes mechanical assertions and Godot binds seven rotating nodes. Topology,
material, and scale flags are reviewed, but the asset remains quarantined:
independent context-free recognition and actual Godot belt-surface UV-motion
evidence are still open.

The animation gap was then closed in the same pass. `ConveyorController`
duplicates the imported belt material per conveyor instance and scrolls its U
offset from the ramp-limited actual belt travel while continuing to rotate the
two drums and five return rollers. A capture-only Godot carton witness is driven
by the same `ActualSpeedMps`; native stopped/running 1600x900 captures prove it
remains fixed with `RunCommand=false` and advances with the running command.
Godot reports seven rotating nodes and one belt material surface. Animation is
now reviewed; independent blind recognition remains the admission blocker.

## Second clean-sheet candidate - powered pallet roller conveyor - 2026-09-17

The next authored family is a 1000 mm clear-width by 4 m chain-driven pallet
roller conveyor. It contains 31 individually named 64-segment powered rollers,
roller shafts and sprockets, enclosed upper/lower chain runs, an under-slung
helical gearmotor/reducer and guarded drop drive, three braced/anchored support
stations, opposed photoeye/reflector, local E-stop, junction box, clamped cable
tray, and typed pallet-flow/three-phase connection points.

Fourteen full-resolution Blender/Godot views were manually inspected. The
quality loop replaced an unrecognizable motion slab with a modeled timber
pallet, added cable clamps and a terminal gland, and deepened the chain guard
after the checker proved the first panel did not fully envelope the sprockets.
The saved source passes mechanical checks for 31 rollers, 1.02 m roller face,
photoeye alignment, chain-guard coverage, and review artifacts. Godot imports
the GLB, selects it by catalog ID, binds all 31 rollers, and produces native
stopped/running pallet captures. Topology, material, scale, and animation are
reviewed; independent blind recognition remains open.

Godot authoring/runtime separation was also tightened: every asset `source/`
and `review/` folder now contains `.gdignore`, preventing Blender files and QA
renders from entering the runtime import queue. The dedicated headless import
step uses the workspace .NET SDK before native captures.

## Original-scene parity and executable Godot semantics - 2026-09-17

All 32 authored `.plcscene` files are now migrated into versioned Godot-side
JSON contracts under `rungproof-next/scenes/migrated`. The migration preserves
camera, equipment configuration, symbolic simulation points and ownership,
actions, boolean and edge rules, sequences, training guidance, and verification
cases. The catalog contains 194 equipment placements across 19 source types
with zero unresolved types. The original application remains intact.

The clean-sheet candidate catalog now contains 25 reusable modeled families:
the two conveyor pilots plus 23 scene-critical controls, indication, actuation,
drives, process, sensing, air-handling, lifting, machining, robotics, table, and
access-control assets. Each has Blender source, GLB delivery, collision proxy,
review renders, thumbnail, symbolic signal metadata, and kinematic metadata
where applicable. All 25 pass a fresh independent context-free recognition
review at or above 0.80, but all remain candidates and the production catalog
remains empty. Recognition is necessary but does not override visible realism,
topology, material, scale, or animation defects.

`SceneComposer` now instantiates every original equipment placement from the
candidate catalog, and `SceneSimulationRuntime` executes the preserved symbolic
contracts without owning PLC addresses or transport. It supports boolean rules,
rising-edge memory, toggle/cycle/pulse actions, safe/reset states, sequence
steps, translated and normalized-position motion, tank-level motion, indicator
aggregation, photoeye projection, and equipment running bindings. A visible
Run/Stop/Reset panel is generated for interactive scenes; exact authored actions
remain available through the scene contract and command-line verification path.

The executable verification runner launches Godot against all 25 scenes that
declare acceptance cases. Its first pass exposed 13 runtime-semantic failures;
after implementing top-level action execution, momentary scan behavior, and
boolean-output initialization, all 25 pass. The latest full render runner also
captures all 32 migrated scenes with zero deferred equipment and produces four
contact sheets for visual inspection.

Visual/runtime QA has already rejected and corrected several initially plausible
results: the radar visualization cone no longer contributes to collision bounds;
the roller shutter now honors the original `1=closed, 0=open` convention; stack
lights illuminate only the commanded tier; camera framing updates after motion;
and the lift was rebuilt as a two-stage mechanism because a single-stage model
could not physically achieve the authored 2.2 m travel. The latest lift is
recognizable at 0.91 and remains connected through full travel, though its pivot,
guide, cylinder, and plumbing details still require production-level refinement.

The process tank now has visible elevated supports, flanged outlet, bolted and
hinged manway, rail base plates, scaled sight glass, isolation handwheels, and a
non-colliding animated liquid column. Its first revised blind review failed at
0.78; the corrected view/model passed at 0.82 and remains a candidate with the
reviewer's remaining piping, weld, support, and instrumentation concerns open.

The long-term target remains 850 production families and 3,000 configured
variants. Passing the original-scene tranche proves the modeling/runtime/QA
pipeline; it is not catalog completion or enterprise parity.

## Factory construction, safety, utility, and load tranche - 2026-09-17

The next clean-sheet tranche adds 28 reusable candidates spanning factory
flooring, structural steel, catwalk/stair/ladder access, guarding, safety
devices, workstations and storage, electrical enclosures, cable and process
supports, pallets/containers/metal loads, a floor scale, and fixed barcode
identification. The candidate catalog now contains 53 families; the production
catalog remains empty by design.

Every new asset includes editable Blender source, GLB delivery, a separate
collision proxy, four review views, and a thumbnail. All 28 thumbnails were
visually inspected together and then sent to separate isolated context-free
vision-review processes. Initial reviews exposed incorrect silhouettes and
render choices: the stair rails did not land on their posts; door/window detail
was hidden on the back face; a cable tray read as a conveyor; a process support
read as mill rolls; a tote read as a cooler; a drum read as a filter; an IBC
read as shelving; a scale read as a camera; and the barcode scanner read as an
E-stop pull-cord. Those assets were rebuilt and freshly reviewed until all 53
catalog candidates passed both the 0.80 confidence threshold and semantic-family
matching. Failed reviews are retained under `build/blind-review-assets` as
regression evidence.

The review loop also corrected taxonomy instead of forcing a desired label onto
ambiguous geometry. The original nominal insulated-wall family consistently
read as a solid machine-guard/acoustic partition, while its door and window
variants read as guarding-enclosure modules. Their catalog IDs and categories
now reflect those visible functions. A separate architectural insulated-wall
family remains future work.

Godot imported the final GLBs successfully. The .NET project still builds with
zero warnings and zero errors, all 25 executable migrated-scene contracts pass,
and all 32 migrated scenes render with zero failures. Final contact sheets for
both the factory-kit tranche and the 32 scenes were visually inspected. A
project-level `build/.gdignore` now keeps generated review evidence out of the
Godot import queue.

These 53 assets remain candidates, not production assets. Independent
recognition does not close detailed topology, PBR material, LOD, connector,
collision, animation, or scene-scale acceptance. The 850-family enterprise
target remains active.

## Controls, sensing, instrumentation, and safety tranche - 2026-09-17

The clean-sheet catalog now contains 77 candidate families after adding 24
reusable controls/sensing assets: proximity, photoelectric, ultrasonic and
laser distance sensing; limit and safety interlocks; floor-area scanning;
RFID and rotary encoding; pressure, temperature, flow, vibration, and force
instrumentation; field IO-Link; operator stations; rope-pull E-stop; safety
mat; and five-tier indication with sounder. Each asset has editable Blender
source, GLB delivery and collision models, four full-resolution review views,
and a 1440 px context-free four-view thumbnail.

Every review image was inspected manually and then evaluated by its own
isolated vision-review process without filename or project context. The first
pass rejected 19 of 24 assets. Successive geometry passes corrected sensor
barrels, optical targets, process connections, guard mounting, M12 ports,
pedal and mat silhouettes, and installed machine context. The final shear-beam
load cell required true Boolean machined bores after visual QA found that black
cylinders standing above the body looked like pushbuttons. All 77 candidates
now pass the semantic-family check at or above 0.80; failed intermediate
reviews remain in `rungproof-next/build/blind-review-assets` as evidence.

The review loop again corrected taxonomy instead of forcing a desired answer.
The modeled optical pair consistently and correctly read as a through-beam
photoelectric pair, so it is cataloged as that family; a separate true
retroreflective family remains required. The ultrasonic entry was likewise
refined to an unambiguous single-transducer distance sensor rather than
claiming a dual-transducer subtype its final silhouette did not support.

Godot imports the 24 delivery and collision GLBs when launched with the bundled
.NET SDK explicitly supplied through `DOTNET_ROOT` and `PATH`. The C# project
builds with zero warnings and zero errors, and all 25 executable migrated-scene
contracts pass. All 32 migrated scenes also pass a fresh render regression, and
the three final controls/sensors contact sheets were inspected at native
resolution with no remaining silhouette, faceting, or perceptual-identity
failure. The through-beam asset's generated slug was corrected as well so its
filesystem identity no longer misleadingly says retroreflective. These assets remain candidates: production admission still
requires per-family topology, PBR material, scale, connector, collision,
animation/IO behavior, and in-engine scene acceptance. The target remains 850
production families and 3,000 configured variants.

## Mechanical motion and power-transmission tranche - 2026-09-17

The clean-sheet catalog now contains 93 candidate families after adding 16
mechanical-motion assets: ISO tie-rod, guided, rodless, rotary-pneumatic, and
welded-body hydraulic actuators; parallel-jaw and vacuum end effectors; AC
servo and NEMA stepper motors; inline helical and right-angle worm gearmotors;
a pillow-block bearing, flexible jaw coupling, profile rail guide, servo ball
screw actuator, and motorized rack-and-pinion stage. Each family has editable
Blender source, delivery and collision GLBs, four full-resolution review views,
a 1440 px context-free thumbnail, declared simulator signals, and named
kinematic nodes where motion is supported.

Manual contact-sheet review and isolated context-free review rejected seven of
the first 16 images. The guided cylinder read as a multi-plunger switch, the
rotary actuator as a gearbox, the gripper as a press or valve actuator, the
vacuum tool as an isolation table or bottle jack, the servo as a cam switch,
the worm reducer as a pump/blower, and the profile rail as a V-track trolley.
The models were rebuilt around functional cues rather than labels alone: air
plumbing and opposed rack housings, robot-wrist interfaces and clearly opposed
jaws, visible suction plumbing and cups, curved servo power/feedback cables,
true wraparound guide geometry, and an illustrative worm-wheel cutaway. Final
context-free confidence ranges from 0.81 to 0.98 and all 93 catalog candidates
pass the semantic-family threshold. Failed intermediate reports remain under
`rungproof-next/build/blind-review-assets`.

Taxonomy was corrected when the visible geometry did not support the initial
claim. The hydraulic cylinder is cataloged as welded-body rather than tie-rod,
and the parallel gripper is actuation-neutral because reviewers could identify
the jaw family but not reliably infer pneumatic versus electric drive. The
worm reducer's open gearing is explicitly a training cutaway and remains a
candidate requiring an enclosed production variant.

`validate_gltf_kinematics.py` now checks catalog axis declarations against the
actual GLB node names; all 35 current kinematic-node contracts resolve. Godot
imports the new GLBs cleanly with source/review directories excluded by
generated `.gdignore` markers. The C# project builds with zero warnings and
zero errors, all 25 executable migrated-scene contracts pass, and all 32
migrated scenes pass render regression. Both final mechanical contact sheets
and all four 32-scene regression sheets were inspected at native resolution
with no remaining perceptual or scene-composition regression.

These 93 entries remain candidates, not production assets. The production
catalog is intentionally empty until per-family topology, UV/PBR material,
LOD, connector, collision, animation/IO behavior, and in-engine scale
acceptance are closed. The long-term target remains 850 production families
and 3,000 configured variants.

## Material-flow and bulk-handling tranche - 2026-09-17

The clean-sheet catalog now contains 105 candidate families after adding 12
material-flow assets: gravity roller, two-strand pallet-chain, steel-slat, and
modular-plastic-belt conveyors; a 90-degree pop-up chain transfer; vertical
reciprocating conveyor; open-trough screw conveyor; continuous bucket
elevator; vibratory bowl feeder; bulk hopper with slide gate; powered swing-arm
diverter; and pneumatic pallet stop. Each family includes editable Blender
source, delivery and collision GLBs, four full-resolution review views, a
1440 px context-free thumbnail, declared simulator signals, and named motion
nodes where the asset supports animation.

Context-free review rejected four initial models. The pallet conveyor read as
a lumber conveyor because its load lacked real pallet construction, the
pop-up transfer read as a generic lift-and-rotate table, the vertical conveyor
read as a hoist/test stand, and the screw conveyor read as a drum or belt
conveyor. They were rebuilt with functional geometry: upper and lower pallet
decks with three stringers and fork openings, three visibly perpendicular
pop-up chain strands with sprockets and lift guides, a guarded roller carriage
inside a vertical mast, and a true open U-shaped trough containing a continuous
helical auger flight. The corrected isolated-review confidence is 0.91 to 0.93
for those four assets. All 105 current candidates now pass independent
context-free family recognition at or above 0.80; failed reports remain as
review evidence.

The catalog-to-GLB validator now resolves all 47 declared kinematic nodes with
zero failures. Godot imports the tranche cleanly, the C# project builds with
zero warnings and zero errors, all 25 executable migrated-scene contracts
pass, and all 32 migrated scenes pass render regression. Both final asset
contact sheets and all four complete-scene regression sheets were inspected
at native resolution; no missing meshes, collapsed geometry, camera clipping,
broken placement, or perceptual-identity regression remains in this tranche.

These 105 entries remain candidates, not production assets. Independent visual
recognition is only the semantic gate; topology, UV/PBR material, LOD,
connectors, collision, animation/IO behavior, and in-engine dimensional
acceptance must still close before production admission. The active target
remains 850 production families and 3,000 configured variants.

## Process-fluid, pneumatics, and separation tranche - 2026-09-18

The clean-sheet catalog now contains 119 candidate families after adding 14
process-fluid and pneumatic assets: handwheel gate and globe valves, lever
butterfly valve, swing check valve, knife gate, pneumatic globe control valve,
end-suction centrifugal pump, AODD pump, an external-gear hydraulic power-unit
trainer, three-piece FRL, seven-station pneumatic valve manifold, horizontal
shell-and-tube heat exchanger, tangential cyclone, and pulse-jet dust
collector. Each family includes editable Blender source, delivery and
collision GLBs, four full-resolution review views, a 1440 px context-free
thumbnail, process connectors, symbolic simulator signals, and named motion
nodes where applicable.

Manual review caught detached inline-valve flanges before independent review;
their generator had placed the flange centers at floor elevation instead of
the pipe centerline. Context-free review then rejected or misclassified the
initial gate, butterfly, check, external gear pump, valve manifold, and dust
collector models. Successive rebuilds added a true rising-stem gate body and
yoke, visibly angled butterfly disc, hinged swing-check cutaway, pneumatic
push-in fittings and solenoid cues, pulse-cleaning header and airlock, and an
explicit external-gear hydraulic trainer with proper closed spur-gear meshes,
aligned drive, reservoir, motor, gauge, process lines, and physical trainer
nameplate. Taxonomy was corrected rather than forced: the dust unit is now the
media-neutral `pulse-jet dust collector`, and the difficult gear family is
honestly a labeled hydraulic power-unit trainer rather than a production
standalone pump. All failed intermediate reviews remain as evidence.

All 119 candidates now pass independent context-free family recognition at or
above 0.80. The catalog-to-GLB validator resolves all 59 declared kinematic
nodes with zero failures. Godot imports the 42 new delivery, collision, and
thumbnail files cleanly. The C# project builds with zero warnings and zero
errors, all 25 executable scene contracts pass, and all 32 migrated scenes
pass render regression. Both final process-fluid contact sheets and all four
complete-scene sheets were inspected at native resolution with no remaining
missing mesh, detached component, faceting, clipping, placement, or
composition regression.

The tranche also exposed and fixed a catalog-loader regression. The physical
PLC-address guard used raw `Contains("DB")`, causing the symbolic signal
`position_feedback` to be rejected because `feedback` contains the adjacent
letters `db`. The loader now matches an actual bounded Siemens data-block token
such as `DB14` while preserving `%I` and `%Q` rejection. The exact failing
Godot launch now passes and the full contract suite confirms symbolic-only
runtime behavior. No physical PLC addresses were added.

These 119 entries remain candidates, not production assets. Semantic
recognition does not close production topology, UV/PBR material, LOD,
connectors, collision, animation/IO behavior, dimensional, or in-engine
acceptance. The active target remains 850 production families and 3,000
configured variants.

## Electrical distribution and industrial-control tranche - 2026-09-18

The clean-sheet catalog now contains 133 candidate families after adding 14
electrical and control assets: a racked-out withdrawable MCC feeder bucket,
wall-mount VFD, book-form servo amplifier, six-slot modular PLC rack, 10-inch
touch HMI, open-core control transformer, enclosed fused rotary disconnect,
three-pole molded-case breaker, 14-way DIN terminal strip, 24 VDC DIN power
supply, managed eight-port industrial Ethernet switch, dual-channel safety
relay, contactor/overload motor starter, and three-phase soft starter. Each
family includes editable Blender source, delivery and collision GLBs, four
full-resolution review views, a 1440 px neutral multi-view thumbnail, symbolic
simulator signals, and named motion nodes where the device has a controllable
state.

Manual multi-view inspection and independent context-free review rejected six
initial assets. The MCC bucket and VFD read as generic enclosures, the HMI as a
windowed box, the DIN supply as a generic panel, the safety relay as a wall
enclosure, and the servo amplifier first lacked enough identity and then read
as a dry transformer. Rebuilds changed functional geometry rather than merely
adding labels: the MCC feeder is visibly withdrawn from an open cubicle with
rails and bus stabs; drive families gained heat sinks, displays, and distinct
power/control connectors; the HMI gained a true process touchscreen; the DIN
supply gained terminal decks and venting; and the safety relay gained a narrow
DIN body, removable terminal decks, wire entries, channel LEDs, and reset
control. The servo required four review rounds. Its final visual hierarchy
uses an enclosed DC-bus plug, subordinate rear heat sink, and dominant motor,
encoder, brake, I/O, and motion-network connector field; it is independently
identified as a servo drive/amplifier at 0.94 confidence. Failed intermediate
reviews remain as evidence.

All 133 candidates now pass independent context-free family recognition at or
above 0.80. The catalog-to-GLB validator resolves all 62 declared kinematic
nodes with zero failures. Godot imported the changed electrical assets cleanly,
the C# project builds with zero warnings and zero errors, all 25 executable
migrated-scene contracts pass, and all 32 migrated scenes pass render
regression. Both final electrical contact sheets and all four complete-scene
regression sheets were inspected at native resolution with no missing meshes,
detached components, clipping, material failure, or composition regression.

These 133 entries remain candidates, not production assets. The next catalog
work must continue to expand missing utility, machine, robotics, packaging,
facility, and passive-hardware families while production admission separately
closes topology, UV/PBR material, LOD, connector, collision, animation/IO,
dimensional, and in-engine acceptance. The active target remains 850 production
families and 3,000 configured variants.

## Plant-utility and support-equipment tranche - 2026-09-18

The clean-sheet catalog now contains 147 candidate families after adding 14
plant-utility assets: an enclosed rotary-screw compressor, vertical air
receiver, refrigerated air dryer, twin-tower desiccant dryer, air-cooled water
chiller, induced-draft cooling tower, horizontal firetube boiler, rotary-vane
vacuum pump, regenerative blower, production hydraulic power unit, central
grease-lubrication skid, PSA nitrogen generator, plate-and-frame heat
exchanger, and duplex condensate-return unit. Each family includes editable
Blender source, delivery and collision GLBs, four full-resolution review views,
a 1440 px neutral multi-view thumbnail, declared connectors and symbolic
signals, and named motion nodes where applicable.

Context-free review exposed weak visual identity in the initial refrigerated
dryer, cooling tower, vacuum pump, regenerative blower, lubrication skid, PSA
generator, and condensate unit. These were rebuilt around recognizable working
geometry: separated refrigeration and condensate-management sections, a true
open tower basin and fill/fan stack, pump-specific housings and connected
drives, a side-channel blower casing, centralized pump/reservoir/metering
hardware, paired adsorption vessels with a distinct product receiver and
header logic, and a duplex receiver with two independently piped pumps. Manual
inspection also caught detached motor couplings on the vacuum pump and blower;
both alignments were corrected before acceptance. All 147 candidates now pass
independent context-free family recognition at or above 0.80, with failed
intermediate reports retained as evidence.

This tranche also exposed a presentation defect shared by three generators.
Front-facing Blender text was rotated into the correct plane and then reflected
again with a negative X scale, producing mirrored labels despite otherwise
valid geometry. The reflection was removed from the process-fluid, electrical,
and utility generators, all 42 affected families were rebuilt, and every one of
the 24 assets containing affected front labels received a fresh isolated review.
The only remaining weak result, the soft starter, was then rebuilt with clearly
visible and separated LINE and LOAD terminal banks and passed at 0.87. This is
recorded as a geometry and review correction, not as a substitute for asset
identity.

The catalog-to-GLB validator resolves all 71 declared kinematic nodes with zero
failures. Godot imported all changed process, electrical, and utility files
cleanly; the C# project builds with zero warnings and zero errors; all 25
executable migrated-scene contracts pass; and all 32 migrated scenes pass
render regression. Both final utility contact sheets and all four complete-scene
regression sheets were inspected at native resolution with no missing assets,
detached components, clipping, composition regression, or render failure.

These 147 entries remain candidates, not production assets. Semantic
recognition and clean scene regression do not close production topology,
UV/PBR material, LOD, connector, collision, animation/IO, dimensional, or
in-engine acceptance. The active target remains 850 production families and
3,000 configured variants.

## Production machines and machine tools tranche - 2026-09-18

The clean-sheet catalog now contains 161 candidate families after adding 14
production-machine assets: hydraulic C-frame press, mechanical gap-frame press,
CNC hydraulic press brake, horizontal pivot bandsaw, circular cold saw,
double-ended pedestal grinder, manual engine lathe, vertical knee mill,
horizontal injection-molding machine, tilt-rotate welding positioner, pedestal
resistance spot welder, front-load aqueous parts washer, rotary-barrel
mass-finishing tumbler, and enclosed Class-1 laser-marking station. Each family
has editable Blender source, delivery and collision GLBs, four full-resolution
review views, a 1440 px multi-view thumbnail, symbolic simulator signals, and
named controllable nodes where its mechanism supports motion.

Independent context-free review rejected the first cold saw as a rotary
slitter, the first welding positioner as a tube bender, the first spot welder
as a pneumatic press, and the initial circular finishing bowl as a parts
feeder. The saw was rebuilt around a pivoting blade head cutting stock held in
a screw vise; the positioner gained a visibly tilted rotary table, fixture,
weldment, torch, and cable; and the welder gained opposed copper C-arms,
electrode tips, overlapping sheet, cooling hoses, and transformer/controller
geometry. Their corrected confidence is 0.86 to 0.98 and each review names the
intended family.

The finishing concept required a taxonomy correction rather than another
label-based workaround. Both circular-bowl and rectangular-vibratory-tub
attempts were still confidently identified as feeding equipment. They were
removed from the catalog and retained under `build/superseded-assets` as
failure evidence. The accepted replacement is an open-hatch polygonal rotary
barrel mass-finisher with visible media and parts, geared drive, load/unload
hatch, and discharge tray. It is independently identified as an industrial
rotary drum tumbler at 0.82 confidence. The existing spiral-track vibratory
bowl feeder remains the distinct material-handling family.

All 161 candidates now pass independent context-free family recognition at or
above 0.80. The catalog-to-GLB validator resolves all 94 declared kinematic
nodes with zero failures. Godot imported all 42 new production-machine files
cleanly after binding the pinned portable .NET 10 SDK; the C# project builds
with zero warnings and zero errors; all 25 executable migrated-scene contracts
pass; and all 32 migrated scenes pass render regression. Both final machine
contact sheets and all four complete-scene regression sheets were inspected at
native resolution with no missing assets, detached components, faceting,
mirrored labels, clipping, placement regression, or render failure.

These 161 entries remain candidates, not production assets. The next catalog
work continues through robotics/end-of-arm tooling, packaging, facility,
passive hardware, process equipment, and remaining machine families while
production admission separately closes topology, UV/PBR material, LOD,
connectors, collision, animation/IO, dimensional, and in-engine acceptance.
The active target remains 850 production families and 3,000 configured
variants.

## Robotics and end-of-arm-tooling tranche - 2026-09-18

The clean-sheet catalog now contains 175 candidate families after adding 14
robotics and end-of-arm-tooling assets: SCARA robot, delta pick robot, six-axis
cobot, Cartesian XYZ gantry, four-axis palletizer, robot seventh-axis track,
automatic pneumatic tool changer, robotic MIG torch, servo spot-weld gun,
robotic paint gun, robotic high-speed spindle, electromagnetic sheet gripper,
robotic pallet fork, and industrial stereo 3D vision camera.

Context-free review rejected or materially under-specified the first delta
robot, palletizer, linear track, and vision camera. Their rebuilt geometry now
shows the decisive mechanism: overhead delta servos and parallel arms over a
pick conveyor, palletizing parallelogram and pallet load, rack/servo/energy
chain with a mounted robot on the seventh axis, and dual optical channels plus
structured-light projector and calibration target. Final independent family
recognition is 0.91 to 0.99 for the tranche. All 175 candidates pass the 0.80
recognition gate; all 121 declared kinematic nodes resolve with zero failures.

## Nested workspace hierarchy acceptance - 2026-09-18

The Godot simulator workspace now has a verified nested-assembly authoring
path. A parent group can contain two reusable child groups, and the Workspace
Hierarchy renders the relationship with explicit tree markers rather than
ambiguous whitespace. Selecting the parent header selects all four member
assets. Ungrouping that parent promotes its two child groups; Undo restores the
parent/child relationship. Grouping an already exact group is now idempotent,
preventing accidental wrapper groups.

The `--verify-workspace` gate creates that exact four-placement fixture,
verifies hierarchy selection, ungroup/undo, and version-5 save/load retention.
It passed with zero build warnings/errors. Native captures at 1600 x 900 and
1280 x 720 were visually inspected in
`rungproof-next/build/hud-workspace-nested-hierarchy-1600.png` and
`rungproof-next/build/hud-workspace-nested-hierarchy-1280.png`.

Godot imported the robotics delivery and collision files cleanly, the C# build
passes with zero warnings and zero errors, all 25 executable scene contracts
pass, and all 32 migrated scenes pass render regression. Both robotics contact
sheets and all four complete-scene regression sheets were manually inspected
at native resolution. These remain candidates, not production assets; the
850-family/3,000-variant production target and full production gates remain
unchanged.

## Godot simulator shell vertical slice - 2026-09-18

Normal RungProof Next launch now opens a simulator application shell instead of
defaulting to an asset preview. It provides a 32-scene browser, searchable
175-candidate catalog, scene and asset inspectors, symbolic points and
renderer-binding views, Run/Stop/Reset, independent local-runtime and guarded
PLC-connection status, catalog placement, viewport orbit/pan/zoom, actionable
project diagnostics, and validated save/load of user-added placements. The
legacy capture and scene-contract command paths remain intact.

The new project validator checks catalog resources, physical bounds, duplicate
IDs, connector poses, signal types/directions and kinematic references, scene
migration mappings, unresolved types, symbolic points, binding equipment, and
binding modes. It exposed an unsupported `levelSensor` renderer binding in the
sump scene; the runtime now implements visible level-switch state rather than
silently ignoring it. The complete loaded project now reports zero errors and
zero warnings. Headless application-shell verification passes with 32 scenes,
175 assets, and a deliberately DISCONNECTED guarded PLC client. Workspace
save/load also passes an end-to-end round trip, and its temporary verification
file is removed afterward.

The guarded PLC client is currently a safe disconnected implementation only.
No endpoint, PLC address, DB offset, or write scope is inferred or embedded in
scene data. A live guarded-runtime protocol, authorization flow, connection
recovery, advanced manipulation tools, and project packaging remain future
simulator tranches. The picking, connection authoring, and undo/redo gaps from
this first slice were closed by the interface baseline described next; neither
slice should be described as the completed enterprise editor.

## Godot interface and HUD baseline lock - 2026-09-18

Catalog expansion is paused at 175 candidates while the simulator shell is the
critical path. The Godot application now has direct viewport selection, a
visible selected-object envelope, numeric position/rotation/scale editing,
delete, 100-level snapshot undo/redo, dirty-state indication, camera
orbit/pan/zoom, and versioned persistence for placements, connector links, and
symbolic signal mappings. Keyboard access covers save, load, undo/redo, delete,
and deselect.

Connection authoring now rejects unavailable endpoints, self-links,
incompatible connector kinds, incompatible scalar types, and duplicates. Valid
connector links are shown as color-coded routed lines with endpoint markers.
Signal mappings state their execution truth directly in the HUD: `LIVE INPUT`
means a verified adapter currently applies the scene point; `AUTHORED ONLY`
means persistence exists but executable behavior does not. Belt and powered
pallet-roller conveyors currently support verified `run_command`, `estop_ok`,
and `speed_setpoint` inputs. Output/readback mappings remain authored-only
instead of writing PLC-owned points or inventing feedback.

The normal shell starts with local runtime STOPPED and guarded PLC runtime
DISCONNECTED. Its diagnostics dock is compact by default and expandable. The
1600 x 900 design layout and canvas-scaled 1280 x 720 layout were visually
inspected across the shell, workspace, connections, signals, and PLC views.
The automated HUD gate checks toolbar/side-dock/diagnostics non-overlap, a
minimum 480 x 420 3D aperture, toolbar visibility, and that every required
connection control fits without scrolling at the design viewport. Current
verification passes with a 1600 x 900 logical viewport, 822 x 704 aperture,
and 110-pixel compact diagnostics region.

The workspace gate additionally proves that a live-mapped conveyor command
overrides generic playback and holds the placed conveyor stopped while the
mapped symbolic PLC point is false. Build, application-shell, HUD, and
workspace checks pass with zero C# warnings/errors. The authoritative shell
contract is `rungproof-next/docs/HUD_ACCEPTANCE.md`. This locks the current
baseline against regression; live PLC transport, remaining asset adapters,
readback publication, advanced gizmos, and production asset admission remain
future work.

The locked workspace baseline was then extended without resuming catalog
growth. Selected placements can be duplicated, focused by the camera, or have
rotation/scale reset from the Workspace tab. Position and rotation snapping is
optional and uses configurable metric and angular increments. `Ctrl+D` and `F`
provide direct keyboard access. Transform edits now reject non-finite values.
The workspace gate proves 0.25 m/15 degree snapping, duplication, and undo of
duplication in addition to the existing persistence and signal-mapping checks.
The updated Workspace tab was visually inspected at 1600 x 900 with all
controls visible and the 3D aperture unchanged.

Direct viewport manipulation is now part of the locked baseline. The selected
placement exposes depth-independent red/green/blue move and scale handles or
three rotation rings. `W`, `E`, and `R` switch modes. Screen-space hit testing
drives the chosen world axis, honors the configured position/rotation snap,
clamps scale above zero, records one undo snapshot per completed drag, and lets
Escape cancel back to the exact starting transform. The automated workspace
gate executes move, rotate, and scale hit/drag paths rather than checking only
that a gizmo node exists. Move, rotate, and scale views were visually inspected
at 1600 x 900, and the complete Workspace layout plus gizmo was inspected at
1280 x 720.

The workspace now supports true multi-selection from both the object list and
Ctrl-click viewport picking. Duplicate, delete, copy, and paste operate on the
whole selection as one undoable transaction. Clipboard paste preserves member
transforms and connector links within the copied set, remaps every instance
and link ID, and restores the pasted set as the current selection. Signal
mappings are copied only when the destination scene still contains a
type-compatible symbolic point; cross-scene incompatibilities are skipped and
reported instead of creating invalid project data. The automated workspace
gate proves connected conveyor/photoeye copy/paste, copied signal mapping,
selection count, one-step undo, batch delete, and batch-delete undo. Native
1600 x 900 and scaled 1280 x 720 multi-selection views were visually inspected
with both selected envelopes, gizmo, clipboard controls, and batch inspector
state visible.

The locked editor now also supports persistent exclusive groups and world/local
transform spaces. `Ctrl+G` groups two or more selected placements;
`Ctrl+Shift+G` ungroups them; and selecting any member restores the complete
group selection. Group move, rotate, and scale use a shared selection pivot,
while local mode orients the gizmo from the primary placement. Version-3
workspace documents persist groups, and versions 1 and 2 remain loadable.
Copy/paste recreates complete copied groups with remapped member IDs. The
automated workspace gate executes world move, rotate, and scale plus a rotated
local-axis move and proves both members preserve the required relationship.
World- and local-axis group views were visually inspected at 1600 x 900, and
the local-axis view was also inspected at 1280 x 720. Catalog growth remains
paused at 175 candidates while the simulator interface is hardened.

Marquee selection is now part of the locked viewport contract. A left drag on
empty 3D space displays a depth-independent cyan selection rectangle and
selects workspace placements whose projected centers lie inside it. `Ctrl` or
`Shift` adds to the existing selection, `Escape` cancels the drag, and a hit on
one grouped member expands to the complete persistent group. The workspace
gate proves both ungrouped multi-selection and grouped-member expansion. The
active marquee was visually inspected at 1600 x 900 and 1280 x 720 with no HUD
overlap or loss of the STOPPED/DISCONNECTED safety state.

The Workspace editor now exposes a compact Arrange menu without increasing the
720p panel height. Align X/Y/Z moves selection-unit pivots to the primary
selection, while Distribute X/Y/Z keeps the outer pivots fixed and evenly
spaces intermediate units. Persistent groups are treated as rigid units, so
arranging does not destroy internal member spacing. Each operation records one
undo snapshot. The workspace gate exercises primary-pivot alignment and
three-unit distribution; closed and expanded menu states were visually
inspected at the supported layout sizes.

Persistent groups can now be renamed from a compact modal editor. Group names
are trimmed, limited to 64 characters, required to be nonblank, and unique
case-insensitively. A rename is persisted in the workspace document and is one
undoable transaction. The workspace gate proves rename, undo, redo, blank-name
rejection, and duplicate-name rejection. The focused dialog and the revised
three-button Group/Rename/Ungroup row were inspected at 1600 x 900 and
1280 x 720.

The former three-button row has been extended to Group/Rename/Pivot/Ungroup.
The Workspace group contract is now version 4 with an optional persistent local
XYZ pivot. The compact Group/Rename/Pivot/Ungroup row opens a focused pivot
editor that either uses the member centroid or stores a deliberate local pivot.
Group rotation and scale use that saved pivot as the fixed center; copy/paste
remaps and offsets it with its copied group, and save/reload preserves it.
The workspace gate proves the custom-pivot anchor remains fixed through rotation
as the other group member moves, alongside round-trip persistence. The pivot
editor was visually inspected at 1600 x 900 and 1280 x 720. Catalog growth
remains paused while this interface contract is hardened.

The Workspace list is now a compact hierarchy rather than a flattened placed-
asset list. Each persistent group is a selected group header with its member
assets indented below it; ungrouped assets remain at the root. Selecting a
header sends the complete group selection through the same shell event path as
viewport and member selection. The workspace gate proves that header behavior,
and the hierarchy was visually inspected at 1600 x 900 and 1280 x 720 without
reducing the usable 3D aperture.

## Candidate review evidence hardening and photoeye correction - 2026-09-18

Candidate metadata is no longer treated as proof of production readiness.
`rungproof-next/tools/validate_asset_evidence.py` checks source, delivery,
collision, thumbnail, named review views, quality flags, and — for production
promotion — a separate `independent_recognition.json` with a non-self reviewer,
identified family, and confidence of at least 0.80. The initial audit records
3 complete candidate review packages out of 175; the remaining 172 are
explicitly incomplete rather than silently appearing production-ready.

The original through-beam photoeye scene asset was rebuilt from Blender source
after review exposed bare pigtail cable ends. Each sensor now has a visible
M12-style connector/coupling termination; delivery GLB and collision output
were regenerated. Hero, two optical faces, rear cable/mount, underside,
alignment, scale, wireframe, and context-free review images were rendered and
inspected at full resolution. The Godot candidate preview was also corrected
to frame static small equipment at inspection distance rather than fitting a
generic motion witness. The photoeye remains a candidate pending genuinely
independent recognition; no production admission is claimed.

## Pneumatic pusher travel correction and scene proof - 2026-09-18

The original conveyor-pusher scene and its catalog asset now agree on the
authored 1.35 m stroke and the source scene's 0.3 s stroke timing. The previous
0.30 m generic translation was replaced by a dedicated pneumatic-pusher motion
adapter: a cylinder-mounted rod lengthens from the front cap while nine named
carriage members translate together. The Blender source, delivery/collision
GLBs, catalog bounds/node reference, thumbnail, and detailed stopped/running
review package were regenerated.

Full-resolution review found and corrected a too-distant first hero render and
a stale Godot imported delivery file. After a forced reimport, the migrated
scene reports nine bound pusher kinematic nodes. Its stopped and running Godot
captures visibly show the complete carriage extension. The asset is still a
candidate, not a production asset: an actually independent blind-recognition
record is still required and no such record has been fabricated.

## AC induction motor motion and review correction - 2026-09-18

The reusable TEFC induction motor now has terminal-box lid/gland/fastener
detail and a physically separated rotating assembly. Visual review exposed
that the old model had labelled the external stator shell as a rotor, causing
the whole housing to spin apart in a running render. The fixed housing is now
separate from the local-X rotating shaft and guarded cooling fan. The runtime
now carries an authored continuous-rotation axis, and this asset's catalog and
scene adapter agree on 1450 RPM. Godot reports ten bound motor motion nodes in
the migrated equipment gallery. Its detailed review package is complete as a
candidate; independent blind recognition remains a production blocker.

## Flanged pipe spool branch correction and review - 2026-09-18

The supported flanged pipe-spool candidate was rebuilt after full-resolution
review found its gauge visibly floating above the instrument branch. A modeled
gauge stem now makes the branch flange, stem, gauge body, face, and needle a
continuous assembly. Dedicated flange, branch/gauge, saddle, underside, scale,
and wireframe evidence was added and manually inspected. The asset remains a
candidate pending genuinely independent blind recognition.

## Vertical process tank runtime and review correction - 2026-09-18

The 3 m x 5 m vertical process-tank candidate received a source rebuild and a
runtime correction. Review added a continuous roof midrail, foot anchors, and
outlet bolt circle. The initially opaque cyan sight-glass tube hid the liquid
state in normal Godot views, so it was replaced with a transparent tube and a
high-contrast bottom-anchored liquid column.

The migrated tank runtime now mirrors the original symbolic behavior: Run plus
inlet/drain simulation controls drive level, pump rotation, level switches,
transmitter output, stack-light state, and the `KIN_liquid` visual. There is no
PLC address or transport write path in this scene runtime. The `tank-level`
contract proves the inlet raises level and transmitter feedback together and
that Stop clears the symbolic commands while holding the process state. All
detailed source renders and live stopped/running Godot captures were visually
inspected. The asset remains candidate-only without a genuine independent
recognition record.
## Reviewed scene source synchronization - 2026-09-18

The 32 Godot migrated scene documents are no longer allowed to drift silently
from their declared `prototype/scenes` sources. A new explicit promotion tool,
`rungproof-next/tools/promote_reviewed_scenes.py`, reports differences by
default and promotes accepted reviewed content only with `--apply`.
`migrate_original_scenes.py` now refuses to overwrite divergent reviewed
scenes unless the source edit is explicitly selected with `--accept-source`.

Twenty-five reviewed scene contracts were promoted back to source, including
the corrected photoeye elevations, peer-control layouts, pallet load, parcel
sensor bank, container receiver, and purpose-built tote finishing stations.
Both browser and Python scene validators, the browser asset catalog, JSON
schema, and Three.js builders now understand those contracts. The removed
floating valve was replaced by a supported isolation valve visibly mounted
inline in the Lab 2.14 sump discharge pipe.

Verification after synchronization: zero source divergences; 28/28 Node tests;
189 Python tests passing (45 locked-Qt skips); 25 training scenes and 50 cases;
32 library scenes; 26/26 Godot scene contracts; Godot app-shell, HUD, and
workspace acceptance; and a zero-warning, zero-error .NET build.

## Tote finishing equipment tranche - 2026-09-19

Lab 2.21 no longer substitutes three CNC machines or floating generic parts
for tote finishing operations. Four reusable Blender-authored candidate GLBs
now provide a metered tote filler, cap-torquing machine, print-and-apply
labeler, and three-camera vision inspection station. Their named kinematic
nodes are bound by the Godot runtime to the existing symbolic commands without
changing the original ten-step training sequence or PLC ownership contract.

The first scene integration incorrectly embedded a reference IBC in every
station asset. The delivery/collision exports now exclude those review-only
workpieces, while the scene's single moving `finishing_tote` uses the existing
1000 L IBC catalog asset and remains the sole sequence-controlled load.
Context-free independent recognition passed at 0.89 for the filler, 0.96 for
the capper, 0.91 for the labeler, and 0.82 for the vision station. They remain
candidate assets pending the complete production evidence gate.

Verification: 179 candidate catalog entries; 125/125 declared GLB kinematic
node checks; 26/26 executable Godot scene contracts; Lab 2.21 rendered all
eight scene objects with zero deferred objects; zero-warning, zero-error .NET
build; and the full fast repository lane passed 28 Node tests and 189 Python
tests (45 locked-Qt skips). The full lane requires a Windows-PowerShell-safe
`PSModulePath` on this workstation because the Codex runtime otherwise places
an incompatible PowerShell 7 utility module ahead of the Windows module.

## Scene support equipment tranche - 2026-09-19

The remaining procedural placeholders used by Labs 2.13, 2.17, and 2.23 were
replaced with reusable Blender-authored candidate GLBs: a positive-displacement
liquid metering skid, a two-position container receiving fixture, and a
three-height parcel dimensioning station. Review-only workpieces and belt
context are excluded from delivery and collision exports so complete scenes do
not receive duplicate containers or hidden conveyor geometry.

Independent context-free review rejected the first two modeling rounds. The
accepted third round identifies the metering skid at 0.82 confidence, the
dual-lane receiver at 0.82, and the multi-beam parcel-height station at 0.94.
The revisions added a continuous suction/discharge process path, diaphragm
pump detail, check valves and calibration hardware; five powered receiving
rollers, guides, docking funnels and presence sensors per bay; and a sparse
three-channel height-measurement portal with a physically mounted readout.
All three remain candidate-only because topology, material, and full animation
evidence gates are not yet complete.

Godot now loads the catalog GLBs instead of constructing low-detail primitive
stand-ins. The Lab 2.13 `fill_skid_run` command drives the named metering-pump
shaft, while the receiver and dimensioning station retain their original scene
semantics. Runtime captures of all three complete scenes were visually checked
for support, scale, alignment, product-path height, and duplicate review props.

Verification: 182 candidate catalog entries; 127/127 declared GLB kinematic
node checks; zero-warning, zero-error .NET build; all three affected scenes
rendered with zero deferred objects; and 26/26 executable Godot scene contracts.

## Palletized shipping load replacement - 2026-09-19

The last `procedural.*` scene-catalog mapping was removed. Lab 2.18 now uses a
reusable Blender-authored GMA palletized case load instead of assembling a
pallet and plain box primitives at runtime. The asset contains a block/stringer
pallet with visible fork openings, eight individual taped cases, shipping
labels and barcodes, and two continuous retention straps routed over the load
and down to the pallet base.

Visual review caught and rejected an initial strap-height error that left both
straps floating above the cartons. The corrected asset passed independent
context-free recognition at 0.98 confidence as a strapped corrugated-carton
unit load on a wooden stringer pallet. In the running Lab 2.18 capture it is
correctly scaled on the conveyor at the pickup position; all seven scene
objects render with zero deferred objects and the automatic sequence completes.
It remains a candidate pending the remaining production evidence gates.

## Semantic scene-load replacement and all-scene audit - 2026-09-19

The overloaded migrated `box` renderer no longer turns unrelated scene loads
into the same generic carton. Runtime routing now selects reusable catalog
assets by authored equipment identity: corrugated shipping cartons, reusable
plastic totes, an HDPE coolant jerry can, a capped process bottle, a GMA pallet,
an IBC, a two-clamp assembly fixture, and a clamped-plate workholding fixture.
The CNC workpiece now uses a reusable machine-vise assembly holding rectangular
4140 stock instead of a neutral metal primitive. Its first round was rejected:
the review-only spindle looked unsupported and the front jaw obscured the stock.
The misleading spindle was removed and the jaw/stock relationship was revised.

Independent context-free recognition accepted the carton at 0.99 confidence,
the jerry can at 0.86, the process bottle at 0.82, the modular assembly fixture
at 0.91, and the clamped-plate fixture at 0.89. A separate context-blind agent
then identified the revised CNC asset as a machinist's milling vise holding a
rectangular steel workpiece at 0.91 confidence, with no major physical or render
defect. Review-only context remains excluded from delivery GLBs. The candidate
catalog contains 189 assets; production remains zero because the complete
production evidence gate has not been met.

All 32 migrated scenes were rendered in running state and inspected together
for the repeated failure classes reported during review: unsupported or floating
equipment, front/back occlusion, incorrect orientation, inappropriate asset
substitution, implausible load scale, sensor/product-path alignment, and leaked
review props. Every scene loaded with zero deferred objects. The two affected
drill scenes visibly place supported clamped fixtures under their spindles.

Verification: zero-warning, zero-error .NET build; 127/127 declared GLB
kinematic node checks; 26/26 executable Godot scene contracts; Godot app-shell,
HUD, and workspace acceptance; 32/32 running scene renders; and the full fast
repository lane passed 28 Node tests and 189 Python tests with 45 expected
locked-Qt skips.

The revised machine-vise asset then became the first production admission. Its
package includes named hero and blind-review images, an explicit 1 m scale
witness, a renderable topology wireframe, written topology/material/scale/static-
motion review, and a machine-readable independent recognition record tied to
the separate review task. The strict production evidence validator reports no
gaps and the production catalog now contains one approved asset; 188 candidates
remain. A guarded promotion tool refuses catalog movement unless the full
evidence contract passes.

Moving an asset to production exposed a runtime catalog-boundary defect: scene
composition previously received only the candidate catalog, so a correctly
promoted asset became unavailable to its scene. The application now merges the
validated production and candidate catalogs into one duplicate-checked runtime
catalog while preserving their separate quality states. Lab 2.24 again renders
all eight objects with zero deferred objects, its full tended-machine sequence
contract passes, and app-shell verification reports 189 runtime assets split as
one production and 188 candidates.

The same strict promotion path was then applied to the seven remaining
candidates whose local evidence packages were otherwise complete. Separate
context-blind agents reviewed one image each. Five passed: the belt conveyor at
0.98, through-beam photoeye at 0.95, TEFC induction motor at 0.95, supported
flanged pipe spool at 0.91, and vertical process tank at 0.90. Their independent
recognition records are stored with the asset evidence and all five were
promoted. The production catalog now contains six fully evidenced assets and
the candidate catalog contains 183.

Two candidates were deliberately not promoted. The pallet roller conveyor was
recognizable at 0.96, but its drive and discharge-end member appeared
unsupported. The pneumatic pusher was recognizable at 0.84, but its tubing,
rod constraints, actuator linkage, and workpiece support remained physically
ambiguous. Both require source-model correction and a fresh blind review; their
existing completeness flags are not treated as overriding the reviewers'
failures.

The six-production runtime split also exposed an order-dependent workspace
verifier: it selected catalog element zero and silently assumed that element
was the belt conveyor. Production sorting made the motor first, which correctly
failed clipboard, connector, and live-mapping assertions. The verifier now
selects the required conveyor by stable asset ID, and the original full
workspace gate passes again. Catalog order is no longer part of the editor's
acceptance contract.

The pneumatic pusher was then corrected at source rather than admitted with its
first review defects. The moving carriage now carries two shortened guide shafts
and their locknuts through fixed bearing blocks; both air lines terminate at
modeled manifold fittings; and the review deck and carton are explicitly tagged
as review-only so they cannot leak into delivery GLBs. A fresh context-blind
agent identified the revised asset as a bench-mounted pneumatic linear pusher
with guided carriage at 0.93 confidence, found no major physical or rendering
defect, and passed it. Stopped and running complete-scene captures confirm a
supported cross-conveyor installation and extension across the product path.

The strict evidence gate promoted the corrected pusher as production asset
seven, leaving 182 candidates. Verification after promotion: 127/127 declared
GLB kinematic-node checks; 26/26 executable Godot scene contracts; Godot app-
shell, HUD, and workspace acceptance; zero-warning, zero-error .NET build; and
the full fast repository lane with 28 Node tests and 189 Python tests passing
(45 expected locked-Qt skips).

The previously rejected powered pallet roller conveyor was also corrected at
source. Its motor and reducer now sit on a visible two-rail cradle tied into the
main frame by paired hangers; the service cable tray ends inside its supported
span; and the local E-stop is clear of the drive guard. A fresh unlabeled-image
review by a separate context-blind agent identified it as a powered pallet
roller conveyor at 0.98 confidence and returned PASS with no major visible
support, collision, floating-part, or scale defect. Blender mechanical checks
confirm 31 rollers and all 14 evidence views. The strict gate promoted it as
production asset eight, leaving 181 candidates.

The combined pushbutton/E-stop station then completed a three-round corrective
review. The first two context-blind reviews identified it but rejected the tall
toy-like enclosure, weak pedestal, exposed cable loop, ambiguous terminations,
and undersized anchors. The source asset was rebuilt as a compact industrial
enclosure on a hollow structural pedestal with internal field wiring, a bolted
enclosure mounting flange, thicker base plate, four washer-and-stud anchors,
separate START and mushroom E-stop operators, readable neutral legends, and
independent runtime nodes. Complete hero, control, base, rear, underside,
stopped/running, scale, and wireframe evidence was regenerated.

The third separate agent identified the unlabeled image as a floor-mounted
industrial operator station with START and emergency-stop controls at 0.98
confidence and reported no major visible defect. The strict gate promoted it as
production asset nine, leaving 180 candidates. Declared GLB kinematic-node
checks remain 127/127.

The three-tier stack light then completed a two-round corrective review. Close-
up evidence exposed that the old cap and buzzer intersected the red lens, while
the first context-blind agent correctly rejected the visible result as an
improper fourth blue lamp. The source now uses one shared bezel at each tier
boundary, a non-luminous full-diameter black sounder housing above the red lens,
a perforated acoustic grille, and four visible base anchors. The second separate
agent identified one integrated red/amber/green industrial signal tower with
acoustic sounder at 0.98 confidence, found no major defect, and returned PASS.
The strict gate promoted it as production asset ten, leaving 179 candidates.

The centrifugal pump skid was corrected before admission. Its former lateral
inlet contradicted the visible impeller eye and shaft; the source now has a true
axial end-suction flange and bore, with tangential vertical discharge. A single
`KIN_pump_shaft` pivot owns the coupling hubs, shaft, and motor fan, and the
Godot scene composer now rotates that group around the physical X axis instead
of the default vertical axis. Complete topology, suction/discharge, coupling,
motor, underside, stopped/running, scale, and wireframe evidence was rendered.
A separate context-blind agent identified a motor-driven horizontal end-suction
centrifugal pump skid at 0.97 confidence, verified the process topology and
alignment, found no major defect, and returned PASS. The strict gate promoted
it as production asset eleven, leaving 178 candidates.

The actuated quarter-turn ball-valve assembly then completed a multi-round
source correction and independent review. The original candidate was a capped
pipe intersecting an oversized sphere, with a floating drum actuator and no
credible installed load path. The authoritative Blender generator now creates
a compact split-body valve with a continuous process bore, paired valve and
mating flanges, compressed gasket planes, through-studs and outside nuts,
connected pipe spools, V-saddles, anchored feet, an ISO-style four-post actuator
mount, retained visible drive coupling, solenoid valve, pneumatic working lines
and supply connector, limit-switch enclosure, and field cable terminated at a
mounted junction box. Measured catalog bounds are 2.22 x 1.816 x 0.77 metres.

The exported `KIN_valve_stem` pivot owns the stem and high-contrast position
pointer and provides the declared 0-90 degree Z-axis motion. Named hero, blind,
opposite-flange, exact-centerline bore, actuator, support, stopped/running,
scale, and wireframe evidence is stored with the asset. Early blind and
multi-view reviews rejected real defects including blocked or ambiguous bores,
unsupported presentation, buried fasteners, open flange gaps, block saddles,
ambiguous linkage, unterminated wiring, and dangling pneumatic hardware. After
those corrections, a fresh context-blind agent identified the unlabeled image
as a pneumatically actuated quarter-turn process valve, likely a ball valve, at
0.98 confidence and returned PASS with no major visible physical defect.

The strict evidence gate promoted the valve as production asset twelve, leaving
177 candidates. Verification after promotion: production evidence valid for all
12 assets; 127/127 GLB kinematic-node checks; 26/26 executable Godot scene
contracts; Godot app-shell acceptance with 32 scenes and 189 runtime assets;
HUD and full workspace acceptance; zero-warning, zero-error .NET build; and the
full fast repository lane with 28 Node tests and 189 Python tests passing (45
expected locked-Qt skips). This checkpoint remains deliberately uncommitted and
unpushed until the user requests the next Git backup.

The flange-mounted 4-20 mA level transmitter was then rebuilt from its former
generic box, blank screen, plain flange disk, bare probe, and dangling cable.
The authoritative source now contains a six-fastener process flange, sealed and
insulated probe entry, rigid sensing rod and weighted tip, round dual-
compartment electronics housing, readable 67.4% / 4-20 mA local display,
LT-101 nameplate, bolted rear terminal cover, supported field-entry gland, and
protective-earth lug. Measured bounds are 0.8305 x 3.605 x 0.64 metres.

Instrument-specific hero, blind, display, process seal, rear terminal, probe,
alignment, scale, and wireframe evidence replaced the generic cropped review.
A separate context-blind agent identified the unlabeled image as a flange-
mounted continuous level transmitter with a long insertion probe and 4-20 mA
output at 0.96 confidence, found no major visible defect, and returned PASS.
Its static no-motion contract is explicitly reviewed. The strict gate promoted
it as production asset thirteen, leaving 176 candidates.

Verification after the level-transmitter promotion: production evidence valid
for all 13 assets; 127/127 GLB kinematic-node checks; 26/26 executable Godot
scene contracts; Godot app-shell acceptance with 32 scenes and 189 runtime
assets; HUD and workspace acceptance; and the full fast repository lane with 28
Node tests and 189 Python tests passing (45 expected locked-Qt skips). Changes
remain deliberately uncommitted and unpushed until the user requests backup.

## Four-position selector station correction and promotion - 2026-09-21

The floor-mounted rotary selector station was rebuilt from the former tall,
unanchored generic cabinet. The authoritative Blender source now includes a
compact enclosure, hollow pedestal, enclosure gussets, base plate, four visible
washer-and-anchor sets, four flush numbered detents, matching radial ticks, and
a handle with an integrated direction inlay. `KIN_selector_handle` owns every
visible moving selector member. The Godot runtime now turns that hierarchy about
the physical front-face axis instead of swinging it out of the dial plane.

Three independent context-blind reviews identified early presentation defects:
a detached-looking red pointer, floating placard/index labels, and ambiguous
detents. Those source defects were corrected rather than waived. The final
unlabeled review identified a pedestal-mounted rotary selector/control station
at 0.98 confidence and returned PASS with no major physical, scale, support,
collision, or rendering failure.

The complete evidence package records hero, blind, dial, pedestal, rear,
stopped/Auto, scale, and wireframe views. Production evidence is valid for all
16 assets; the candidate catalog contains 173 assets. The catalog has 127/127
declared GLB kinematic nodes, the Godot/.NET build is zero-warning and
zero-error, and all 26 scene contracts pass. Changes remain deliberately
uncommitted and unpushed until the user requests backup.

On 2026-09-21, the industrial pedestal drill press was rebuilt and promoted as
production asset nineteen. The accepted asset has a continuous column, table
collar/gussets and anchors, motor and guarded belt-drive cover, spindle-bearing
housing, an exported `KIN_spindle` hierarchy for quill/chuck/bit motion, a
hinged rigid-frame polycarbonate guard, a visible opposed-jaw vise capturing a
test coupon, and a yellow-collared mushroom E-stop. Two independent
context-free reviews rejected early models for missing workholding, drive, and
guard evidence; the final review identified the corrected model at 0.95
confidence and returned PASS. Production evidence now validates 19 assets;
kinematic validation is 127/127, the .NET build has zero warnings/errors, and
all 26 Godot scene contracts pass. Changes remain uncommitted and unpushed
until the user requests backup.

The tuning-fork point-level switch was then rebuilt from a generic box,
oversized smooth process cylinder, crude fork bars, and loose cable into a
compact vibronic insertion instrument. The source now contains a stainless hex
process fitting, detailed threaded entry, process seal, supported neck,
symmetric welded fork/yoke with equal rounded tines, compact electronics head,
green status ring, LSH-102 vibronic tag, protective-earth lug, and fixed four-
pin M12 socket. External vessel and field cable remain scene-level connections.
Measured bounds are 0.46 x 2.104 x 0.435 metres.

Dedicated complete, fork, thread, status, connector, rear, scale, and wireframe
evidence replaced the cropped generic renders. A separate context-blind agent
identified the unlabeled image as a tuning-fork point-level switch for liquid
or bulk-material detection at 0.97 confidence, found no major visible defect,
and returned PASS. The strict gate promoted it as production asset fourteen,
leaving 175 candidates. Production evidence remains valid for all 14 assets;
127/127 kinematic checks, 26/26 scene contracts, 32-scene/189-asset app-shell,
HUD, and workspace verification all pass. Changes remain deliberately
uncommitted and unpushed until the user requests backup.

The 80 GHz non-contact radar level transmitter was then rebuilt from its
generic solid antenna barrel, unbolted flange, loose cable, and artificial
target ring. The authoritative source now contains a dual-compartment orange
electronics head, readable 5.42 m / ECHO OK local display, bolted rear terminal
cover, fixed cable gland, protective-earth lug, supported LT-201 nameplate,
process neck, eight-fastener annular flange, tapered antenna horn, and
dielectric lens. Its translucent radar cone is retained strictly as optional
simulator feedback below the lens and is hidden from physical recognition
evidence. Measured physical bounds are 0.771 x 1.422 x 0.68 metres.

Dedicated hero, blind, display, flange/horn, rear terminal, beam-path, scale,
and wireframe evidence replaced the generic review. The first independent
review passed but noted that the nameplate appeared unsupported; two visible
stainless stand-offs were added and the evidence was regenerated. A fresh
context-blind agent then identified the unlabeled image as a flange-mounted
radar level transmitter for non-contact liquid or bulk-solid measurement at
0.96 confidence and returned PASS with no major visible defect. The strict
gate promoted it as production asset fifteen, leaving 174 candidates. Changes
remain deliberately uncommitted and unpushed until the user requests backup.

The industrial axial exhaust fan was then rebuilt around a physical
`KIN_fan_hub` hierarchy: the hub, six blades, and shaft rotate together while
the shroud, motor, grille, and anchored pedestal remain fixed. The prior
box-spoke guard was replaced by a continuous perimeter ring, captured round
rods, concentric guard rings, and four bolted shroud-to-guard standoffs. Post
brackets, motor support arms, a crossrail, and correctly placed base anchors
make the load path visible instead of inferred. The final context-free review
identified it as a pedestal-mounted axial exhaust/ventilation fan at 0.98
confidence and returned PASS with no major visible geometry, guard-retention,
clearance, or support defect. Strict production promotion made it asset
seventeen, leaving 172 candidates. Production evidence is valid for all 17
assets; 127/127 kinematic checks, a zero-warning .NET build, and 26/26 Godot
scene contracts pass. Changes remain deliberately uncommitted and unpushed
until the user requests backup.

On 2026-09-21, the scissor lift table candidate was upgraded and promoted as
production asset eighteen. Its two-stage scissor mechanism now has retained
pivots, guided upper rails and rollers, a pinned inclined hydraulic actuator,
and a four-sided expanding black/yellow bellows barrier that keeps the pinch
zone enclosed in both stopped and raised review poses. The runtime controller
translates/scales the bellows deliberately with the platform. A separate
context-free review identified an enclosed scissor-lift table at 0.95 and
returned PASS; the strict evidence gate, catalog validation, kinematic checks,
.NET build, and Godot scene-contract checks all passed. Changes remain
uncommitted and unpushed until the user requests backup.

On 2026-09-21, the six-axis industrial robot was rebuilt and promoted as
production asset twenty. Its export now has a real nested `KIN_axis_1` through
`KIN_axis_6` hierarchy, exact-centreline arm links, separated joint housings,
base flange/hold-down hardware, restrained static dresspack route, and a
distinct J6 collar, bolted adapter plate, gripper actuator, guide rails, and
finger hardware. Early context-free reviews rejected merged joints, weak base
anchors, uncontrolled dresspack routing, and an ambiguous tool interface. The
final source-blind recognition review identified a credible six-axis articulated
industrial robot at 0.95 confidence and returned PASS. Production evidence now
validates 20 assets; catalog validation, 127/127 kinematic-node validation, the
zero-warning .NET build, and all 26 Godot scene contracts pass. Changes remain
uncommitted and unpushed until the user requests backup.

On 2026-09-21, the powered indexing rotary table was rebuilt and promoted as
production asset twenty-one. Its rotating platen now uses a nested `KIN_table`
hierarchy that owns the radial slots, index markers, register, fixture plate,
opposed jaws, and four T-nut/strap clamp sets. A fixed anchored base, bearing
housing, geared motor, coupling, guarded drive path, home flag/sensor pair, and
encoder with gland/cable route make the installation readable. The final
context-free review identified a credible powered indexing rotary table at 0.90
confidence and returned PASS. Production evidence validates 21 assets; catalog
validation, 127/127 kinematic checks, zero-warning .NET build, and all 26 Godot
scene contracts pass. Changes remain uncommitted and unpushed until the user
requests backup.

On 2026-09-21, the motorized industrial roller shutter was rebuilt and promoted
as production asset twenty-two. The established Godot `KIN_slat_*` and
`KIN_bottom_bar` movement contract is preserved, while slat seams, bottom end
caps, and a full-width safety edge now move with their proper owners. Fixed
geometry now includes deep curtain-capture guide lips, anchors, header shroud,
roll supports/bearings, motor/coupling/guard/bracket, and a cabled local control
box. The final independent review identified it at high confidence and passed.
Production evidence validates 22 assets; catalog validation, 127/127 kinematic
checks, zero-warning .NET build, and all 26 scene contracts pass. Changes remain
uncommitted and unpushed until the user requests backup.

On 2026-09-21, the enclosed machining-center candidate was materially rebuilt
but remains deliberately unpromoted. The source now has a closed framed
safety-glazing enclosure, a spindle `KIN_spindle` hierarchy, toolholder,
end-mill geometry, power vise with table T-slots/hold-downs, clamped stock,
coolant route, tool rack, CNC-oriented pendant, and yellow-collared E-stop.
The rebuild preserves the existing Godot continuous-spindle contract and
exports with 127/127 kinematic-node validation. Independent source-blind
reviews recognize a VMC (up to 0.92 confidence) but repeatedly reject the
visual finish as insufficiently credible for a professional catalog. Treat the
candidate's prior 0.96 catalog quality entry as stale; do not promote it until
a new independent review passes and complete evidence/quality metadata exists.
The full regression set remains clean: 22 production evidence packages,
zero-warning .NET build, and 26/26 scene contracts. The candidate portfolio
still has 167 incomplete review packages.

On 2026-09-21, the start-only pedestal pushbutton station completed a
three-round source-blind review and was promoted as production asset twenty-three.
The initial candidate was recognizable but its front-side flying lead read as a
second control operator; its next revision still exposed a weak legend and
ambiguous support transition. The accepted source has one green START operator
with an independent retaining ring, compact engraved-style legend, separated
fascia fasteners, a bolted enclosure flange on a heavier square pedestal and
anchored base, plus a rear gland and protected conduit. The final source-blind
review identified a pedestal-mounted industrial START pushbutton station at
0.94 confidence and passed it. The `KIN_pushbutton` 18 mm travel remains a
simulator-only visual witness, not proof of an energized command circuit.

After promotion, production evidence validates 23 assets and 166 candidates
remain incomplete. The catalog validates, GLB kinematic validation remains
127/127, the .NET build has zero warnings/errors, and all 26 Godot scene
contracts pass. Changes remain deliberately uncommitted and unpushed until the
user requests backup.

## Contract-derived help documentation - 2026-09-21

Every current catalog entry and migrated scene now has a generated help
document under `rungproof-next/docs/help/`: 189 asset documents and 32 scene
documents. Asset help records the exact catalog signal, kinematic, connector,
model, and admission contract without inventing PLC ownership or addresses.
Scene help records every symbolic PC/PLC/SIM point, type, initial value,
action, equipment binding, declared safe state, and machine guide when the
source supplies one. The generator and validator (`generate_help_documents.py`
and `validate_help_documents.py`) are now part of the documented asset-quality
standard; the validator confirms all 189 asset contracts and 32 scene I/O
contracts are covered. These documents describe simulator contracts only and
are not live PLC, electrical, safety, or commissioning evidence.

## Current rejected candidate evidence - 2026-09-21

The emergency-stop pedestal candidate remains deliberately unpromoted despite
high recognition confidence. Source revisions added a proportionate red
mushroom, yellow mounting field, twist-release marking, readable emergency-stop
legend, enclosure fasteners, and anchored base. Independent context-free
reviews still reject the overall visual fidelity and, specifically, any
front-visible field-cable route that can be mistaken for a mechanical linkage.
The current source therefore keeps its field entry at the rear/hollow support;
do not update the candidate's stale quality record or promote it until a new
complete review package and a fresh passing independent review exist.

The single-tier beacon candidate also remains unpromoted. Its revised source
now has an amber polycarbonate lens, internal reflector/LED modules, lens ribs,
anchored base, and cable gland, but a fresh context-free review still identifies
ambiguous cap/lens/fitting geometry and rejects its visual finish. Its existing
catalog confidence is stale evidence and must not be used for admission.

## Safety bollard admission - 2026-09-22

The surface-mounted 120 mm safety bollard completed its second source-blind
review and was promoted as production asset twenty-four. The accepted model has
a continuous yellow post and base shroud, full-height white reflective sleeve
with restrained black edge rings, rounded black cap, and a square base plate
with four distinct washer-and-anchor assemblies. The independent reviewer
identified the asset as a surface-mounted industrial protection bollard at
0.93 confidence and conditionally passed it; the recorded caveats are limited
to visual finish details rather than function or safety claims. Its evidence
package includes hero, blind-review, base-and-anchor, sleeve-and-cap,
opposite-side, scale-reference, and wireframe renders. It is a static visual
asset with no implied impact rating or certified protective performance.

After promotion, production evidence validates 24 assets and 165 candidates
remain incomplete. All 189 asset and 32 scene help documents were regenerated
and validate against their current contracts. Catalog validation, 127/127 GLB
kinematic-node checks, zero-warning .NET build, and all 26 Godot scene
contracts pass. Changes remain deliberately uncommitted and unpushed until the
user requests backup.

## Pedestrian guardrail admission - 2026-09-22

The 4 m pedestrian guardrail completed a corrected, source-blind visual review
and was promoted as production asset twenty-five. The former generic rail model
now exposes both galvanized base plates, four washered anchors per post, yellow
base gussets, rail-to-post joint collars, rounded end caps, two rails, and a
toe board. The first generic evidence render cropped the 4 m assembly, so the
factory review renderer was corrected to calculate camera distance from actual
source bounds before the final reviewer saw it. That reviewer identified a
floor-anchored pedestrian safety guardrail/walkway barrier at 0.93 confidence
and passed it. This asset represents visible separation hardware only; it does
not claim a design load, vehicle-impact rating, code compliance, or
site-specific anchorage performance.

After promotion, production evidence validates 25 assets and 164 candidates
remain incomplete. The regenerated 189 asset and 32 scene help documents
validate, GLB kinematic validation remains 127/127, the .NET build has zero
warnings/errors, and all 26 Godot scene contracts pass. Changes remain
deliberately uncommitted and unpushed until the user requests backup.

## Machine safety fence-panel admission - 2026-09-22

The 3 m fixed machine safety fence panel completed a two-round source-blind
review and was promoted as production asset twenty-six. The authored panel has
a yellow powder-coated frame, dark open welded-wire mesh, capped posts, base
plates, four washered anchors per post, gussets, and rail-joint collars. The
first review accepted its family recognition but identified exposed mesh tails
under the lower rail; the source was corrected to terminate those verticals
inside the frame, then the final reviewer identified an industrial
machine-safeguarding perimeter panel at 0.98 confidence and passed it. This is
fixed perimeter guarding only, not an access gate, interlock, safety rating, or
site-specific installation claim.

After promotion, production evidence validates 26 assets and 163 candidates
remain incomplete. The regenerated 189 asset and 32 scene help documents
validate, GLB kinematic validation remains 127/127, the .NET build has zero
warnings/errors, and all 26 Godot scene contracts pass. Changes remain
deliberately uncommitted and unpushed until the user requests backup.

## GMA wood pallet admission - 2026-09-22

The 48 x 40 in GMA-style wood pallet completed a two-round source-blind visual
review and was promoted as production asset thirty-three. The first round
rejected the smooth, monolithic candidate because it read closer to molded
plastic and did not make fork clearance sufficiently inspectable. The revised
asset has seven separately spaced deck boards, three lower runners, nine
support blocks, visible deck fasteners, and open fork/pallet-jack entries with
a rough-hardwood finish. The independent reviewer identified a wooden
forklift/warehouse material-handling pallet at 0.98 confidence and passed it
for normal simulator use. It remains a static visual asset: it does not claim
a load rating, ISPM marking, inspection status, or certified fork clearance.

After promotion, production evidence validates 33 assets and 156 candidates
remain incomplete. The generated help documentation still validates every one
of the 189 catalog assets and 32 scene I/O contracts. Catalog validation,
127/127 GLB kinematic-node checks, zero-warning .NET build, and all 26 Godot
scene contracts pass. Changes remain deliberately uncommitted and unpushed
until the user requests backup.

## Reusable plastic tote admission - 2026-09-22

The reusable plastic tote completed a source-blind visual review and was
promoted as production asset thirty-four. Its original opaque placeholder was
replaced by an open HDPE-style shell with a bottom, four walls, continuous
reinforced rim, recessed side handholds, and vertical reinforcement ribs. The
independent reviewer identified an open-top reusable industrial tote/bin at
0.96 confidence and passed it for normal simulator use. The documented
close-up caveats are a rim-corner overlap, a slightly uneven rear interior
transition, mild render grain, and a side feature that can read as either a
handhold or label pocket. This static visual container carries no manufacturer,
volume, food-grade, stackability, or load-rating claim.

After promotion, production evidence validates 34 assets and 155 candidates
remain incomplete. Generated help documentation continues to validate all 189
catalog assets and 32 scene I/O contracts; catalog validation and 127/127 GLB
kinematic-node checks pass. Changes remain deliberately uncommitted and
unpushed until the user requests backup.

## Generated help I/O completeness check - 2026-09-22

`rungproof-next/tools/generate_help_documents.py` generates one help document
for every production and candidate catalog asset and every migrated scene.
Asset pages state the complete reusable I/O contract (or explicitly state that
the asset is passive and has no declared external I/O); scene pages state every
symbolic point with its type, PC/PLC/SIM owner, initial state, action/binding
context, and declared simulation safe state. The validator now proves complete
rows rather than tag-name presence alone: asset signal name, type, direction,
unit, and description; scene point name, type, owner, and initial value.

On 2026-09-22, regeneration and validation passed for all 189 catalog assets
and 32 migrated scenes. These are simulator contracts only, never physical PLC
addresses, verified safety functions, or live commissioning evidence.

## Steel shipping drum admission - 2026-09-22

The generic 55-gallon closed-head steel drum completed a two-round source-blind
review and was promoted as production asset thirty-five. The initial asset was
rejected because four bright body rings and a flat lid read as a stylized vessel
rather than a shipping drum. The accepted revision uses proportionate
body-coloured rolling hoops, top/bottom chimes, a rolled top seam, two
hexagonal closure assemblies with collars/recesses, and a neutral blank
placard. The independent reviewer identified a generic closed-head industrial
steel drum at 0.90 confidence and passed it for normal simulator use. The
placard carries no product, hazard, handling, or identity information and must
never be read as evidence of contents or shipping compliance; the asset also
makes no pressure-rating, chemical-compatibility, sealing, or inspection claim.

After promotion, production evidence validates 35 assets and 154 candidates
remain incomplete. Generated help documentation validates all 189 catalog
assets and 32 scene I/O contracts; catalog validation, 127/127 GLB
kinematic-node checks, zero-warning .NET build, and all 26 Godot scene
contracts pass. Changes remain deliberately uncommitted and unpushed until the
user requests backup.

## IBC tote admission - 2026-09-22

The 1,000 L generic caged intermediate bulk container completed a two-round
source-blind review and was promoted as production asset thirty-six. Its first
review recognized the family but rejected the oversized disconnected outlet and
featureless pallet. The accepted revision has a flanged/capped outlet, valve
body, pivot/lever, and a slotted pallet base with runners and crossmembers.
Independent recognition passed at 0.94 confidence. It remains a static visual
IBC with no claim about contents, hazards, valve standard, flow capacity,
pressure rating, chemical compatibility, or shipping compliance.

After promotion, production evidence validates 36 assets and 153 candidates
remain incomplete. Generated help documentation validates all 189 catalog
assets and 32 scene I/O contracts; catalog validation and 127/127 GLB
kinematic-node checks pass. Changes remain deliberately uncommitted and
unpushed until the user requests backup.

## M30 capacitive proximity sensor admission - 2026-09-22

The M30 capacitive proximity sensor completed a source-blind recognition review
and was promoted as production asset forty-two. Earlier evidence was correctly
rejected as a generic wired sensor. The accepted revision exposes the threaded
M30 barrel, paired hex locknuts, black sensing face, cable termination, status
indicator, simulator-neutral `CAP`/adjustment detail, and a separate open
plastic hopper with non-metallic pellets. The reviewer identified a likely M30
capacitive proximity sensor at 0.89 confidence and accepted it for visual
industrial-simulator use.

Its sole catalog signal is symbolic simulator `detected`; it makes no claim
about range, target response, switching behavior, wiring standard, ratings,
safety function, or live commissioning. The small/oblique nameplate, partly
hidden sensing face, stylized hopper, and illustrated gap remain documented
presentation limitations. After promotion, catalog validation reports 42
production and 147 candidate assets; all 189 help documents, production
evidence, 127 GLB kinematic-node checks, the zero-warning .NET build, and 26
Godot scene contracts pass. Changes remain uncommitted and unpushed.

## Controls sensing batch admission - 2026-09-22

The roller-lever limit switch, tongue-actuated guard-door interlock, and
diffuse-reflective photoelectric sensor each completed fresh context-free
recognition reviews and were promoted as production assets 56 through 58. The
limit switch passed at 0.95 confidence; it exposes symbolic `actuated` only.
The tongue interlock passed at 0.90 confidence; it exposes symbolic
`guard_closed` and `safety_ok` only and makes no safety-integrity or
commissioning claim. The diffuse photoeye was initially rejected because its
face read as a control station. It was rebuilt with a recessed optical window,
compact apertures, status indicator, single-head target relationship, and
return-light cue, then passed at 0.84 confidence. Its only signal is symbolic
`detected`; no sensing range, target response, safety function, wiring
standard, PLC address, or live behavior is claimed.

The review renderer now accepts `RUNGPROOF_FACTORY_REVIEW_RESOLUTION`; 640 px
is enough for source-blind review evidence and avoids the CPU saturation caused
by several simultaneous 960 px renders, while the final-evidence default stays
at 960 px. After these promotions, catalog validation reports 58 production
assets and 131 candidates. Help documentation validates all 189 assets and 32
scene I/O contracts, production evidence validates 58 assets, 127/127 GLB
kinematic-node checks pass, the .NET build has zero warnings/errors, and all
26 Godot scene contracts pass. Changes remain deliberately uncommitted and
unpushed.

## Encoder and pressure-instrument batch admission - 2026-09-22

The flange-mounted rotary encoder, compact electronic pressure transmitter,
and analog pressure gauge completed context-free visual recognition and were
promoted as production assets 62 through 64. The encoder passed at 0.96 as a
rotary encoder; incremental counting remains a catalog/simulator behavior,
not something established by render geometry. The analog gauge passed at 0.94
and remains a passive visual instrument with no declared simulator I/O.

The pressure transmitter was initially rejected as an ambiguous electronic
gauge. A distinct threaded process stem, compact electronics housing, top
field-cable entry, and neutral local display corrected its visual identity;
it then passed at 0.90. Its cable is illustrative only. The symbolic simulator
outputs are `pressure_bar` and `healthy`; no range, accuracy, output protocol,
pressure rating, calibration, compatibility, connector standard, or live
commissioning is claimed.

After promotion, catalog validation reports 64 production assets and 125
candidates. All 189 asset help documents and 32 scene I/O contracts validate;
production evidence validates 64 assets; 127/127 GLB kinematic-node checks,
the zero-warning .NET build, and all 26 Godot scene contracts pass. Changes
remain uncommitted and unpushed.

## OEM-family source provenance correction - 2026-09-22

The user correctly identified that several catalog models read as invented
generic objects. Visual recognition evidence and declared simulator I/O do not
prove that an asset has believable real-world form factors. The catalog now has
an `industrial-reference-register.json` for official OEM family references,
with modeled physical features and an explicit no-claim/generic boundary. Four
high-risk controls/sensor forms have initial source records: M30 capacitive
proximity, compact diffuse photoelectric, tongue-actuated guard interlock, and
compact pressure transmitter. Existing production assets without a record are
reported as source-provenance remediation, not silently accepted. New candidate
promotion is blocked unless it has valid OEM-family evidence in addition to the
existing geometry, blind-review, collision, and I/O evidence. No branding,
exact model identity, ratings, wiring, safety performance, or live-device claim
is implied by the references. Changes remain uncommitted and unpushed.

## Safety and identification controls batch admission - 2026-09-22

The floor-area safety laser scanner, RFID read/write head, and coded magnetic
guard interlock pair completed fresh source-blind visual recognition and were
promoted as production assets 59 through 61. Scanner recognition was 0.94 and
RFID recognition was 0.93. Both remain simulator visuals: scanner field
geometry is not a safety-field design, and RFID geometry is not evidence of a
read protocol, range, or live hardware performance.

The coded magnetic interlock was initially rejected twice because its guard
assembly obscured the paired sensor/actuator relationship. It was corrected to
show a separate coded sensor and actuator across the guard seam, then passed
at 0.93. Its `guard_closed` and `safety_ok` points are symbolic simulator
outputs only; no safety category, fault tolerance, tamper resistance, wiring,
risk assessment, or commissioning claim is made. After promotion, the catalog
has 61 production assets and 128 candidates. Generated help validates 189
assets and 32 scene I/O contracts, production evidence validates 61 assets,
and 127/127 GLB kinematic-node checks pass. Changes remain uncommitted and
unpushed.

## Full production source-to-model audit - 2026-09-22

The initial OEM-family source-provenance seed has now been expanded to all 64
production assets. Each production asset has an authoritative OEM or
established industrial product-family reference, a physical-form comparison,
modeled-feature checklist, and explicit generic/no-claim boundaries in
`rungproof-next/assets/catalog/industrial-reference-register.json`. The
generated asset help documents include the same reference basis. The strict
validator reports 64/64 source coverage and 64/64 source-model passes. Source
identification is not treated as a passing geometry review. This full audit
supersedes any earlier individual visual-source pass statement where the
current register now records remodel-required. The help-document and
industrial-reference validators pass. The latest correction batch rebuilt the
M18 inductive proximity sensor, compact laser and ultrasonic distance sensors,
through-beam pair, roller-lever limit switch, analog dial gauge, and compact
pressure transmitter; their delivery GLBs and blind-review evidence now refresh
together from the shared controls/sensors builder. A second correction batch
passed the guided-wave level transmitter and vibronic tuning-fork switch and
made the scene-core builder refresh blind-review evidence. The radar transmitter
remains remodel-required because its current separated/oversized assembly does
not yet read as the compact documented product family. The third batch passed
the compact fixed barcode scanner, diffuse photoeye, and scene-core through-beam
pair, and also makes factory-kit blind review evidence refresh with the rebuilt
delivery GLB. The next correction passes rebuilt and cleared the compact coded
magnetic interlock, SMC-style tie-rod pneumatic pusher, flanged instrumented
pipe spool, axial exhaust fan, 22 mm selector station, exposed-mechanism
scissor lift, modular observation window and personnel door, and continuously
connected compact radar transmitter after fresh blind-render review. The strict
production gate is now 64/64 compared-pass. The 125 unpromoted candidates
remain a separate pending source-to-model audit rather than being implied by
the production result. Candidate evidence is recorded for all 125/125 assets,
with 125/125 source-model passes. The audit covers controls/safety, actuators,
motion, material flow, process fluid, electrical, utilities, production machines,
robotics, tote processing, support equipment, loads, and fixtures. The former
fence mismatch was traced to stale mesh-panel evidence; current source and render
prove the candidate uses the intended solid barrier panel.
(parallel and vacuum grippers, flange servo and NEMA stepper motors, and inline
helical and right-angle worm gearmotors), plus a pillow-block bearing, flexible
jaw coupling, profile-rail linear guide, ball-screw and rack-and-pinion linear
actuators, and the first material-flow set (gravity roller, twin-strand pallet
chain, steel slat, modular plastic belt, pop-up chain transfer, and VRC). The
material-flow builder now refreshes its blind-review artifact with each rebuild.
The second material-flow batch passed the open-trough screw conveyor, continuous
bucket elevator, vibratory bowl feeder, hopper slide gate, powered swing-arm
diverter, and pneumatic pallet stop. The process-fluid builder now also refreshes
blind-review evidence. Its first valve batch passed the flanged gate and globe,
wafer butterfly, swing check, knife gate, and diaphragm-actuated globe-control
forms. The remaining process-fluid batch passed the centrifugal, AODD, and
external-gear pump forms; FRL and seven-station valve manifold; shell-and-tube
heat exchanger; tangential-inlet cyclone; and pulse-jet dust collector. The
first electrical-controls batch passed the withdrawable MCC bucket, wall-mounted
VFD, book-form servo drive, modular PLC rack, touchscreen HMI, open-core control
transformer, fused rotary disconnect, and three-pole molded-case breaker. The
electrical review camera now uses the front three-quarter angle; the disconnect
was corrected to include a sealed three-fuse inspection treatment before pass.
The next electrical-controls batch passed the 14-way DIN terminal strip, 24 VDC
power supply, eight-port managed switch, dual-channel safety relay, contactor/
overload starter, and three-phase soft starter.
The one candidate mismatch remains explicit: the catalogued solid/acoustic fence panel
currently renders as a mesh
guard panel and must be remodeled or deliberately re-scoped before it can pass.
Changes remain uncommitted and unpushed.

## In-program catalog asset viewer - 2026-09-22

The Engineering > Assets browser now has a read-only `VIEW 3D PREVIEW` action
and a `RETURN TO SCENE` action. Preview loads only the selected catalog GLB in
an isolated viewport root; it does not place an asset, alter workspace state,
execute machine actions, create mappings, or connect to a PLC. The authored
scene stays loaded but hidden while previewing and is restored on return. The
existing inspector continues to show stable catalog ID, envelope, quality
gate, connectors, and declared symbolic signal I/O for the selected asset.

The .NET build completed with zero warnings/errors and the Godot app-shell
verification passed with 32 scenes, 189 catalog assets, and a default
DISCONNECTED PLC state. Changes remain uncommitted and unpushed.

## Classic RungProof shell default - 2026-09-22

At user direction, the Godot shell now defaults to the older RungProof
interaction pattern: one unobstructed scene viewport and a compact top
toolbar. A `TOOLS` menu opens exactly one work region at a time (Scenes, Asset
library, Workspace, Inspector, Signals, Connections, PLC status, or
Diagnostics). The old all-at-once arrangement remains available only as
`TOOLS > Advanced multi-panel layout`. Run, Stop, Reset, Save, Load, runtime
state, and guarded PLC state remain persistent in the toolbar; the default PLC
state remains DISCONNECTED. Build completed with zero warnings/errors and the
advanced HUD verification passed. Changes remain uncommitted and unpushed.

## Operator-console reference restoration - 2026-09-22

The user identified the existing native RungProof Qt operator console as the
correct interface reference. RungProof Next was therefore adjusted toward that
layout rather than toward a new compact/editor-first HUD: thin header; left
Scene/Runtime rail; center plant viewport; right Event-history, Scene-equipment,
and PLC-health rail; symbolic local point tables beneath; and compact bottom
Run/Stop/Reset transport. The asset viewer and all authoring functions remain
available through `TOOLS` and the wide Engineering layout, rather than taking
over the operator run screen. The point strip reads scene-declared owner/type
metadata and local runtime values only; it does not show PLC addresses or make
any connection claim. .NET build, Godot app-shell, and advanced HUD checks
passed. Changes remain uncommitted and unpushed.

## Viewer-first operator layout - 2026-09-22

The user then supplied a compact industrial viewer reference and asked the
next-generation RungProof interface to move closer to it. The default shell is
now a viewer-first console: compact persistent header with `TOOLS`, searchable
left hierarchy containing all 32 scenes and all 189 catalog assets, dominant
central 3D viewport, and a bottom tag-watch surface with selectable symbolic
points plus ownership/type/value columns. The earlier permanent right rail is
removed from the default. Selecting an asset in the hierarchy opens its
isolated preview and exposes a return-to-scene action; engineering/editor
tools remain deliberate `TOOLS` actions. The viewer capture is
`rungproof-next/build/viewer-first-operator-layout.png`. The .NET build and
Godot app-shell verifier pass with the default PLC state DISCONNECTED. Changes
remain uncommitted and unpushed.

## RungProof Next offline virtual controller Phase 1 - 2026-09-30

`rungproof-next` is the authoritative implementation target for the learning
loop because it owns the active Godot/C# plant runtime and operator shell; the
root Python/Qt application remains a packaged pilot and UI reference.

Phase 1 adds a dependency-free C# BOOL Ladder Diagram core with NO/NC contacts,
coils, series/parallel logic, document-order networks, strict validation,
immutable snapshots, and fixed-period scanning. The host coordinates each scan
as input sample, program execution, output commit, exact plant advance, and UI
publish. The Scene 1 demonstration implements Start/Stop seal-in, conveyor
motion, plant-driven photoeye stop, restart inhibit while occupied, and a Reset
that clears both program memory and plant position.

The UI labels the mode `IEC 61131-3-ALIGNED SUBSET · OFFLINE` and `NO PHYSICAL
PLC`, exposes only Run/Stop/Reset lifecycle commands, and shows live element
energization plus input/memory/output BOOL values. Simulation input buttons are
explicitly labeled and are not forces. The virtual-controller code has no PLC
transport dependency; plant output binding fails closed unless the target is a
declared PLC-owned BOOL point.

Decision, instruction matrix, schema/scan semantics, and external-engine
research/provenance are in `rungproof-next/docs/adr/0002-virtual-controller-phase-1.md`
and the `VIRTUAL_CONTROLLER_*.md` documents. No evaluated external runtime code
or binary is incorporated. TON and all other timers, counters, arithmetic,
retention, tasks, FBD/ST execution, online edits, and real PLC operations remain
out of scope.

Verified on the pinned local toolchain after implementation: .NET build passed
with zero warnings/errors; 19/19 focused controller tests passed; the rendered
Godot controller acceptance passed photoeye stop, blocked restart, Reset, and
live UI checks with no PLC connection attempted; 28/28 Node tests passed; 189
Python tests passed with 45 explicitly skipped; 25 training scenes / 50 cases
passed; 26 Godot scene contracts passed; app-shell, HUD, workspace, camera, and
scene-control verifiers passed; catalog, kinematic, help, reference, and asset
evidence validators exited successfully. The inspected rendered capture is
`rungproof-next/build/virtual-controller-phase1.png` and showed zero project
errors/warnings, an explicit offline/no-physical-PLC status, simulated inputs,
and live ladder state. Godot still prints existing immediate-shutdown RID leak
diagnostics and sandboxed headless runs cannot write `user://` logs or read the
Windows root certificate store; all acceptance processes returned exit code 0.

## Original operator-console layout restored - 2026-09-30

At user direction, RungProof Next again defaults to the original operator
hierarchy shown in the supplied reference: current scene/actions/runtime rail
on the left, central 3D machine viewport, event/equipment/PLC-health rail on the
right, split symbolic point tables below, and persistent Run/Stop/Reset
transport along the bottom. The later searchable viewer hierarchy remains
available as `TOOLS > Viewer hierarchy`, while authoring and the Virtual
Controller remain deliberate engineering tools. The camera aperture now ends at
the visible right rail rather than extending beneath it. Capture mode suppresses
the interactive simulator notice so layout evidence is unobstructed. The
rendered acceptance image is
`rungproof-next/build/original-operator-layout-restored.png`.

## Edge-to-edge classic shell and dual Ladder environments - 2026-09-30

The RungProof Next shell now restores the complete classic application menu
strip: File, View, Playback, Scene, Tools, PLC, and Help. Each menu is wired to
an existing local action or engineering view rather than serving as decoration.
The Godot stretch policy is `expand`, and all outer shell offsets are zero, so
wide windows use their full client area without fixed-aspect black side bars.

`Tools > Ladder Logic` and the operator rail's `Basic Logic / Ladder` button
open a dedicated full-width programming workspace with two selectable styles:

- TIA Portal style uses SIMATIC, OB1, network, PLC-tag, FC, and FB terminology;
- Studio 5000 style uses CompactLogix/ControlLogix, task, program, routine, and
  controller/program-tag terminology.

Both are explicitly simulator-native interfaces, not vendor software or vendor
project-file generators. Both create the same validated Phase 1 BOOL Ladder IR,
support editable symbolic contact/memory/coil names, and bind renamed variables
to the scene's declared simulator input and output points before execution. The
runtime remains offline and disconnected; no physical PLC connection or write
path is introduced.

The pinned .NET build completed with zero warnings/errors. Godot app-shell,
camera-input, and virtual-controller verification passed; the virtual-controller
test again reported `VIRTUAL_CONTROLLER_REAL_PLC_CONNECTION_ATTEMPTED FALSE`.
Wide rendered evidence is `rungproof-next/build/operator-edge-to-edge.png` and
`rungproof-next/build/ladder-tia-ab-workspace.png`.

## Integrated offline PLC editor direction - 2026-09-30

The user clarified that vendor-styled forms are not the goal. RungProof must
eventually provide the complete offline PLC-development loop when no physical
controller is available: tag creation, arbitrary program authoring, graphical
Ladder editing, validation, scan execution, live monitoring, project
persistence, and symbolic binding to the simulated plant. TIA and Studio 5000
are workflow/presentation choices over a shared simulator execution model, not
static templates and not claims of vendor compatibility.

The fixed seal-in form was replaced with the first real editor foundation:

- mutable Ladder program documents with BOOL tags and scene bindings;
- arbitrary networks/rungs, series contacts, parallel branches, and coils;
- graphical power rails, wired contacts, coils, rung/network numbering and
  comments rather than ASCII art;
- TIA-style project tree, block/network editor, instruction palette, tag pane,
  and diagnostics layout;
- Logix-style Controller Organizer, routine/rung editor, Language Element
  toolbar, tag pane, and Output layout;
- add/remove rung or network, add NO/NC contact, add branch, select output coil,
  add BOOL tag, edit rung/network description, verify, and load offline;
- context-aware Save/Load of `.ld.json` Ladder documents with validated
  round-trip reconstruction into the editor model.

This is an implementation foundation, not the completed editor. Required later
phases include arbitrary element selection/reordering, richer branch topology,
timers, counters, compare/math/move instructions, structured tag data types,
multiple routines/blocks, calls, task/OB scheduling, online-style monitoring,
forces with explicit simulator-only safety controls, cross-reference, search,
undo/redo, instruction help, and vendor import/export boundaries.

The pinned build passed with zero warnings/errors. The expanded controller test
suite passed 23/23, including arbitrary editor-rung construction, parallel OR
execution, compiler rejection, and JSON save/load reconstruction. App-shell
verification passed and no real PLC transport was constructed or connected.
Current visual evidence is `rungproof-next/build/plc-editor-foundation.png`.

## Ladder workbench interaction correction - 2026-09-30

The first editor-foundation capture exposed a functional acceptance gap: the
left project hierarchy and several workbench menu captions were decorative
labels rather than input controls. Screenshots looked plausible, but the user
could not select Program blocks, Main/OB1, PLC tags, or diagnostics. The prior
shell verifier checked node existence and therefore did not catch the defect.

The project hierarchy is now a real selectable Godot `Tree` in both TIA and
Logix workbenches. Selecting controller, device/I/O configuration,
diagnostics, program organization, main block/routine, tags, or watch tables
updates the appropriate editor focus or output/diagnostic message. Workbench
Project/File, Edit, Online/Communications, View, and Tools captions are now
functional menus wired to new/save/load, add/delete, verify/load, run/stop/reset,
program/tag/diagnostic navigation, and instruction help.

The right pane now has separate Instructions and PLC/Controller Tags tabs. Its
instruction hierarchy is selectable and supported instructions can be
double-clicked to insert NO/XIC contacts, NC/XIO contacts, parallel branches,
and networks/rungs. The correction added a dedicated
`--verify-ladder-editor` interaction verifier. The verifier originally failed
with `projectTree=False`; after the correction it passed with selectable tree,
handled selection, rung mutation, instruction insertion, and complete document
restoration. The 23 controller/editor tests and zero-warning build also pass.
The updated visual is `rungproof-next/build/tia-interactive-editor.png`.

## First stateful Ladder instruction: TON - 2026-09-30

The integrated editor now supports a real non-retentive on-delay timer rather
than only BOOL contacts and coils. Users can create TIMER memory instances,
insert TON from the toolbar or instruction tree, select the instance, and edit
the preset in milliseconds. The graphical network renders the TON block. TIA
views expose the done contact as `.Q`; Logix views expose `.DN`; both expose
`.TT`. These names map to the same simulator-owned timer state and do not imply
vendor project compatibility.

The deterministic runtime accumulates exactly one configured scan period per
true scan, clamps elapsed time at the preset, sets done on the scan that reaches
the preset, and clears a non-retentive timer on a false rung, Stop, or Reset.
The monitor publishes preset, elapsed time, timing, and done state. Compiler
validation rejects non-TIMER instances, non-memory TIMER tags, zero/negative
presets, and networks that do not contain exactly one output instruction.
Timer programs persist through `.ld.json` save/load.

Verification passed with a zero-warning build, 30/30 controller/editor tests,
the Ladder interaction verifier including actual TON insertion/restoration, and
the full virtual-controller UI sequence. No real PLC transport was constructed
or connected. Current visual evidence is
`rungproof-next/build/tia-ton-editor.png`.

## Stateful Set/Reset and OTL/OTU coils - 2026-09-30

The next editor/runtime slice adds latched BOOL outputs with vendor-familiar
presentation over shared simulator semantics. TIA shows assignment, Set (S),
and Reset (R) coils. Studio 5000 shows OTE, OTL, and OTU. Toolbar buttons,
instruction-tree entries, the selected-rung output-mode control, graphical
coil markers, monitoring text, compiler model, and JSON persistence all use
the same `assign`, `set`, or `reset` coil mode.

Set/OTL writes TRUE only while its rung is true and preserves the prior value
when false. Reset/OTU writes FALSE only while true and likewise preserves state
when false. Multiple writes follow deterministic document order, so a later
reset wins when set and reset networks are simultaneously true. Reset restores
the declared initial value; Stop still forces declared physical/simulated
outputs false under the existing safe-stop rule.

The zero-warning build, 35/35 engine/editor tests, interaction verifier, and
virtual-controller UI verifier pass. The interaction verifier now proves TON,
Set/OTL, and Reset/OTU button mutations and restores the document afterward.
No real PLC transport was constructed or connected. Visual evidence is
`rungproof-next/build/tia-stateful-coils.png`.

## Rising-edge CTU counters and reset - 2026-09-30

The Ladder workbench now supports COUNTER memory instances, CTU, and counter
reset. TIA presentation uses Q/CV terminology and a reset-input workflow;
Studio 5000 presentation uses DN/ACC and RES. Both views compile to one
documented simulator instruction model. The editor can create COUNTER tags,
insert CTU or reset from the toolbar/instruction tree, select an instance,
edit its positive integer preset, render the block graphically, persist it in
`.ld.json`, and monitor preset, accumulated count, count input, and done state.

CTU increments only on a false-to-true transition. A held-true rung does not
recount. Accumulated count is retentive across false scans and Stop, while the
explicit counter-reset instruction and controller Reset clear it. Later
networks observe Q/DN in the same deterministic scan. Numeric CV/ACC is
currently monitor-only; compare/math support remains a later slice and is not
implied.

The zero-warning build, 41/41 controller/editor tests, Ladder interaction
verifier (including CTU and counter-reset mutations), and virtual-controller UI
verifier pass. No real PLC transport was constructed or connected. Visual
evidence is `rungproof-next/build/tia-counter-editor.png`.

## Typed numeric tags and comparison blocks - 2026-09-30

The runtime/editor now executes INT and REAL tags plus all six fundamental
numeric comparisons: EQ, NE, GT, GE, LT, and LE. A comparison is a first-class
rung condition, not a precomputed BOOL. Operands can be numeric tags,
invariant-culture literals, counter ACC/CV/PRE/PV members, or timer ET/PT in
milliseconds. Numeric input samples are typed; INT samples use nearest-even
integer conversion while REAL samples retain fractional values.

Both vendor workbenches can create INT/REAL tags, select a left operand and
operator, enter a tag/member/literal right operand, insert from CMP or the
comparison instruction tree, render a graphical compare block, monitor typed
values, validate operand types, and save/load the result through `.ld.json`.
Arithmetic and MOV writes are still explicitly unsupported; this slice adds
read/evaluate semantics only.

The zero-warning build, 47/47 controller/editor tests, Ladder interaction
verifier (including actual comparison insertion), and virtual-controller UI
verifier pass. No real PLC transport was constructed or connected. Visual
evidence is `rungproof-next/build/tia-comparison-editor.png`.

## MOV and typed arithmetic instructions - 2026-09-30

The numeric execution layer now includes MOV, ADD, SUB, MUL, and DIV as
first-class Ladder output instructions. Both workbenches provide a dedicated
numeric toolbar, source/destination controls, instruction-tree entries,
graphical blocks, live numeric monitoring, validation, and `.ld.json`
persistence. Sources can be INT/REAL tags, literals, counter members, or timer
members. Destinations must be writable INT/REAL tags.

Numeric instructions write only on a true rung. REAL destinations preserve
fractions; INT destinations round nearest-even and clamp to the simulator's
signed 16-bit range. Literal division by zero is rejected before load. A
divisor that becomes zero at runtime leaves the prior destination unchanged
and publishes `VC_RUNTIME_DIV_ZERO`; non-finite results are likewise rejected
with a runtime diagnostic instead of contaminating controller memory.

The zero-warning build, 54/54 controller/editor tests, Ladder interaction
verifier (including real MOV insertion), and virtual-controller UI verifier
pass. No real PLC transport was constructed or connected. Visual evidence is
`rungproof-next/build/tia-math-move-editor.png`.

## Multiple blocks/routines and CALL/JSR - 2026-09-30

The project model is no longer limited to one flat network list. It now stores
multiple named blocks/routines, a stable entry-block ID, and a CALL/JSR output
instruction. TIA presentation adds FC-style blocks and CALL; Studio 5000
presentation adds routines and JSR. The project tree creates and selects real
editable blocks, the toolbar chooses a target, the canvas renders CALL/JSR,
and save/load preserves the complete hierarchy. Root `networks` remains a
first-block compatibility projection, while `blocks` is authoritative.

A true call rung executes the target block inline before the caller's next
network, making writes immediately visible in deterministic scan order. A false
call skips the target. Compiler validation rejects missing entry blocks,
missing targets, duplicate block identities/names, and direct or indirect
recursive call cycles. This simulator model does not claim Siemens instance-DB
or Rockwell routine-parameter compatibility.

The zero-warning build, 59/59 controller/editor tests, interaction verifier
(including block creation and real CALL insertion), and virtual-controller UI
verifier pass. No real PLC transport was constructed or connected. Visual
evidence is `rungproof-next/build/tia-multiblock-editor.png`.

## Continuous/periodic Task and OB scheduling - 2026-09-30

The offline project model now stores named continuous and periodic tasks with
stable IDs, priorities, periods, and entry-block assignments. The TIA-style
workbench presents these as OB scheduling controls; the Studio 5000-style
workbench presents the same validated simulator model as tasks. Both project
trees select real task records, and the editor can add, edit, persist, reload,
and monitor task schedules and execution counts.

Continuous tasks execute every deterministic base scan. Periodic tasks execute
only when their period is an integer multiple of the base scan. When multiple
tasks are due together, lower numeric priority executes first and document
order resolves ties. Compiler validation rejects missing entry blocks,
negative priorities, periods shorter than the base scan, and non-integral scan
multiples. This model is cooperative at scan boundaries and does not claim
asynchronous interrupts, preemption, execution-time budgets, or vendor project
compatibility.

The zero-warning build, 64/64 controller/editor tests, Ladder interaction
verifier (including actual task creation), and virtual-controller UI verifier
pass. No real PLC transport was constructed or connected. Visual evidence is
`rungproof-next/build/tia-task-ob-editor.png`.

## Ladder editor undo/redo history - 2026-09-30

The shared TIA-style and Studio 5000-style workbenches now use a bounded
mutable-document history rather than cosmetic Undo/Redo controls. History
captures exact offline editor state, including stable element IDs, invalid
work in progress, tags, blocks, tasks, active block, rung branches, instruction
types, operands, and presets. A new mutation after Undo invalidates Redo using
normal editor semantics.

Undo/Redo is available from each vendor workbench toolbar and Edit menu, plus
Ctrl+Z, Ctrl+Y, and Ctrl+Shift+Z. Ctrl+S and Ctrl+O now route to Ladder program
save/load while the Ladder view is active instead of changing the 3D workspace.
Opening or creating a different Ladder project clears its prior history.

The zero-warning build, 67/67 controller/editor tests, Ladder interaction
verifier (including real toolbar Undo and Redo), and virtual-controller UI
verifier pass. No real PLC transport was constructed or connected. Visual
evidence is `rungproof-next/build/tia-undo-redo-editor.png`.

## Simulator-only BOOL I/O forcing - 2026-09-30

The offline runtime and live virtual-controller panel now provide a real force
table for declared BOOL input and output tags. Input forces override the sampled
scene/operator input image before Ladder execution. Output forces override the
calculated output image after Ladder execution and therefore drive the bound 3D
scene output. Active forces are exposed in immutable snapshots and marked in
red beside live variable values and in the controller status banner.

The safety boundary is deliberate: only BOOL input/output tags are eligible;
memory and non-BOOL tags are rejected. Stop de-energizes output values while
leaving forces visibly armed, and Reset clears every force. Force state is
runtime-only, is excluded from `.ld.json`, and has no PLC transport or physical
address path. The UI labels every force as simulator-only and provides Remove
and Clear All controls.

The zero-warning build, 72/72 controller/editor tests, and expanded
virtual-controller end-to-end verifier pass. The verifier proves forced output,
safe Stop behavior, visible force state, Reset clearing, and no physical PLC
connection attempt. Visual evidence is
`rungproof-next/build/simulator-force-panel.png`.

## Semantic Find All and cross-reference - 2026-09-30

The TIA-style and Studio 5000-style workbenches now share a semantic project
index built from the executable Ladder IR. Find All performs case-insensitive
search across tag, block/routine, task/OB, network/rung, operand, and
instruction-detail fields. Exact cross-reference distinguishes declarations,
reads, writes, CALL/JSR sites, and scheduled entry-block assignments. Timer and
counter members such as `.Q`, `.DN`, `.ET`, `.ACC`, and `.CV` resolve to their
owning instance tag rather than appearing as unrelated strings.

Users can open the Find/Cross-reference tab from the vendor menus, press XREF
from a selected tag, or double-click a tag-table row. Double-clicking a search
result selects the owning block/routine and network/rung and scrolls the
graphical editor to it; declaration results return to the tag table. Result
tooltips retain stable block, network, and element identities.

The zero-warning build, 76/76 controller/editor tests, and expanded Ladder
interaction verifier pass. The verifier performs an actual `seal_in`
cross-reference and navigates a returned use site. Visual evidence is
`rungproof-next/build/tia-cross-reference.png`. No real PLC transport was
constructed or connected.

## Context-sensitive Ladder instruction help - 2026-09-30

Both vendor workbenches now expose a catalog-backed instruction help pane from
the toolbar, View/Tools menus, and F1. Selecting an instruction in the tree
updates the help context without inserting it. The pane presents the matching
TIA-style or Studio 5000-style name, purpose, valid parameters, deterministic
scan behavior, restrictions, and an example, plus the offline/vendor boundary.

The catalog covers all currently exposed contacts, coils, Set/Reset and
OTL/OTU, branches, TON, CTU, counter reset/RES, six comparisons, MOV and four
arithmetic instructions, network/rung insertion, and CALL/JSR. Catalog tests
enforce unique keys, complete content, coverage of every comparison/math enum,
vendor terminology, and rejection of unknown help keys.

The zero-warning build, 80/80 controller/editor tests, and expanded Ladder UI
verifier pass. The verifier selects TON help through the real UI and confirms
its non-retentive and Q/DN boundary text. Visual evidence is
`rungproof-next/build/tia-instruction-help.png`. No real PLC transport was
constructed or connected.

## Conditional RETURN/RET program control - 2026-09-30

The offline Ladder environment now implements a real conditional program-
control return. TIA presentation exposes `RETURN`; Studio 5000 presentation
exposes `RET`. The instruction is available from the program-control toolbar
and instruction tree, is rendered graphically, participates in instruction
help and semantic cross-reference, survives exact undo/redo and `.ld.json`
save/load, and is compiler-validated as the single output instruction for its
network/rung.

The runtime now uses explicit execution-frame boundaries. A powered RETURN in
a called block/routine exits only that frame and resumes the caller's next
network. A false RETURN falls through. A RETURN in a task entry block ends only
that task's current invocation, so other due tasks still execute in stable
priority/document order. These are deterministic simulator semantics; they do
not claim Siemens block parameters, Rockwell routine compatibility, online
editing, or physical PLC execution.

Verification passes with a zero-warning build, 84/84 controller/editor tests,
the expanded Ladder interaction verifier (including real RETURN insertion),
and the full virtual-controller UI verifier. Both test paths explicitly report
that no real PLC transport was constructed or connected.

## TOF and TP timer execution - 2026-09-30

The shared offline Ladder runtime now supports three explicit timer kinds:
TON/on-delay, TOF/off-delay, and TP/pulse. TOF sets done immediately on a true
rung and holds it for the preset after the falling edge. TP starts one fixed
pulse on a rising edge, does not extend the pulse when the input changes, and
requires a false input before retriggering. All timing advances only in
configured base-scan increments. Stop and Reset clear timer elapsed, timing,
done, and input-edge memory.

Both vendor workbenches expose real TON, TOF, and TP toolbar buttons and
instruction-tree entries. The editor canvas and live monitor render the actual
timer kind; instruction help explains that Studio 5000 has no direct TP
equivalent. Timer kind is preserved through undo/redo and `.ld.json`
persistence; older files without `timer.kind` load as TON/OnDelay.

Verification passes with a zero-warning build, 86/86 controller/editor tests,
the expanded Ladder UI verifier confirming all three timer insertion paths,
and the full virtual-controller/scene verifier. No physical PLC transport was
constructed or connected.

## Desktop resolution and DPI scaling correction - 2026-09-30

The oversized Ladder UI at 2048x1152 was reproduced and traced to Godot's
`canvas_items` stretch mode. The project treated 1600x900 as a fixed logical
canvas and enlarged all controls by 1.28x at 2048x1152. This was resolution
stretching, not a defect in each toolbar or font override.

The application now uses disabled stretch mode with a 1.0 content scale and
keeps Windows high-DPI awareness enabled. One UI unit maps to one window pixel,
so larger displays expose additional editor area rather than inflating the
entire shell. The fix follows Godot's non-game desktop-application guidance.

A real-window `--verify-ui-density` regression check now validates content
mode, scale factor, and one-to-one physical-window/viewport dimensions. It
passes at 1920x1080, 2048x1152, and 2560x1440. The 2048x1152 before/after
captures are `rungproof-next/build/dpi-before-2048x1152.png` and
`rungproof-next/build/dpi-after-2048x1152.png`. The application-shell,
Ladder-interaction, virtual-controller/scene, zero-warning build, and 86/86
controller/editor regressions also pass. The density verifier intentionally
requires a real window because Godot headless mode reports a synthetic 64x64
viewport.

## Resizable Ladder workbench and graphical element editing - 2026-09-30

The TIA-style and Studio 5000-style workbenches now use nested horizontal and
vertical split containers rather than fixed columns. The project/Controller
Organizer, task-card/Instruction Toolbox, and Inspector/Output regions have
working collapse/reopen controls. Instruction insertion is grouped into Bit
Logic, Timers, Counters, Compare, Math and Move, and Program Control tabs.
Light engineering-workspace surfaces replace the prior gray-on-gray panels.

The graphical canvas now hit-tests individual contacts, comparisons, and the
output instruction. Selected contacts expose operand and NO/NC editing,
stable-ID left/right series movement, exact deletion, and vendor-colored
selection feedback. Parallel branches have explicit add/remove behavior and
the model prevents deletion of the last required branch path. The tag table
supports definition edits and atomic rename across every block/routine; tag
deletion is blocked while executable references remain.

Verification passes with a zero-warning build, 95/95 controller/editor tests,
and the expanded Ladder interaction verifier. The verifier exercises all dock
collapse/reopen pairs, exact element movement/deletion and Undo, branch
deletion and Undo, unused-tag deletion, reference-propagating rename and Undo,
the existing instruction set, search, help, tasks, and blocks. Real-window
visual evidence is
`rungproof-next/build/tia-graphical-element-editing-2048x1152.png`. No real PLC
transport was constructed or connected.

## Atomic new Ladder project lifecycle - 2026-10-02

The New Project command previously cleared tags, blocks, and tasks directly but
could retain watch symbols, a non-default scan period, and the prior stable-ID
allocator. It also failed to explicitly invalidate graphical monitoring of the
already-loaded runtime. `LadderEditorDocument.ResetProject` now atomically
resets every project-owned authoring field, creates one entry block and one
continuous task with deterministic IDs, and is followed by starter I/O tag and
network/rung creation in the active vendor workbench. The shell clears
Undo/Redo and clipboard state, selects the empty insertion slot, invalidates
stale monitor highlights, and reports that Verify + Load is required.

The focused suite passes 133/133 with a reset-contract test covering old
blocks, periodic tasks, watches, scan period, and consumed stable IDs. The
native interaction verifier reports `newProject=True` after invoking the real
TIA Project menu signal and proving complete reset plus monitor invalidation.
No physical PLC transport was constructed or connected.

## Ladder project dirty state and active editor identity - 2026-10-02

Both workbenches now expose the current editable project state in the editor
tab rather than retaining a static `Main` title. TIA shows the active OB/FC,
project filename, and a leading asterisk for unsaved changes. Studio shows
MainProgram, the active routine, `[LAD]`, the filename, and a leading asterisk.
Dirty state is derived from exact `.rpproj.json` serialization against the last
successful Save/Open baseline, so Undo/Redo can cross the saved state without
an unreliable one-way flag. New Project is intentionally dirty and untitled;
Save and Open establish a clean filename baseline.

The native end-to-end persistence path now verifies dirty before Save, clean
after Save, the saved filename in both workbenches, clean after Open, and dirty
untitled state after invoking New Project. This exposed and fixed a shared-view
bug where New Project refreshed only the active vendor tab. The native verifier
again passes with `projectPersistence=True` and `newProject=True`. Visual
evidence is `rungproof-next/build/tia-new-project-dirty-state-2048x1152.png`
and `rungproof-next/build/studio5000-new-project-dirty-state-2048x1152.png`.
No physical PLC transport was constructed or connected.

Independent review of the current TIA and Studio contextual-property captures
found the Studio popup using TIA-style one-based rung numbering and an
ambiguous block breadcrumb. Studio now reports the exact organizer identity as
`MainProgram > Conveyor_Main > Rung 0`; TIA retains
`Conveyor_Main > Network 1`. The native interaction verifier asserts both
vendor-specific scopes and reports `contextualProperties=True/True/True` for
TIA popup, Studio popup, and right-click Properties access. Current captures
are `rungproof-next/build/tia-contextual-properties-current-2048x1152.png` and
`rungproof-next/build/studio5000-contextual-properties-current-2048x1152.png`.

## Live graphical Ladder power-flow monitoring - 2026-09-30

Both the TIA-style and Studio 5000-style graphical canvases now consume the
immutable virtual-controller snapshot and render live power flow from stable
runtime element IDs. Energized rails, the executed prefix of each parallel
branch, contacts, comparisons, and output instructions use the vendor green;
the work area also displays controller lifecycle and scan number. Prefix-based
branch rendering is deliberate: a true downstream contact is not shown as
powered when an earlier series condition has already broken continuity.

Monitoring fails stale-safe. The application compares the serialized editor
program with the program actually loaded in the virtual controller. Any edit
immediately clears graphical highlights and reports that Verify + Load is
required. Undo restores monitoring only when exact program equivalence returns,
so an older compiled result is never presented as evidence for changed logic.

Verification passes with a zero-warning build, 95/95 controller/editor tests,
the full Ladder interaction verifier (including monitor, stale-clear, and
Undo-restore checks), the application-shell verifier, and the offline virtual-
controller/scene verifier. Real-window evidence is
`rungproof-next/build/tia-live-power-flow-2048x1152.png`. The run remained
offline; no physical PLC transport was constructed or connected.

## Exact graphical wire-position insertion - 2026-09-30

The Ladder canvas now treats wire segments as real authoring targets. Clicking
between series instructions selects an exact insertion index and renders a
vendor-colored vertical cursor with a plus marker. The next NO, NC, or compare
instruction is inserted at that position rather than appended to the branch.
New branches and networks open with position zero selected so their first
condition can be entered immediately. Selecting an existing instruction still
edits that instruction; insertion and replacement therefore remain explicit
and visually distinct.

The mutable document exposes bounds-checked `InsertContact` and
`InsertComparison` operations while the existing append methods delegate to
them. Stable IDs of neighboring instructions remain unchanged, exact insertion
is undoable, and the same model drives both vendor workbenches. The interaction
verifier now injects an actual left-click at the computed wire slot, proves the
middle insertion order, performs Undo, and separately inserts a comparison at
an exact middle position.

Verification passes with a zero-warning build, 96/96 controller/editor tests,
and the expanded Ladder interaction verifier reporting
`exactInsert=True/True/True`. Real-window evidence is
`rungproof-next/build/tia-exact-insertion-cursor-2048x1152.png`. No physical PLC
transport was constructed or connected.

## Structured compiler Error List and navigation - 2026-09-30

The formerly ambiguous Ladder bottom drawer was initially made a three-tab
engineering dock. It has since been corrected again: the current bottom dock
contains Error List, Output, and Watch only. Verify failures populate
one structured Error List row per compiler issue with severity, VC code, exact
document path, and message. The header reports the error count and makes clear
that the program was not loaded. Successful verification clears the list and
selects Output; subsequent edits clear old rows and mark verification stale.

Double-click navigation resolves `variables`, `tasks`, `blocks`, and `networks`
indices from the compiler path. It selects and scrolls the appropriate tag,
task/OB, block/routine, or graphical network/rung without hiding the originating
error. The TIA project-tree diagnostics node and both vendor View menus now
open the Error List directly. This is simulator compiler evidence only, not a
vendor compile result or physical-controller diagnostic buffer.

Verification passes with a zero-warning build and the expanded Ladder
interaction verifier. The verifier deliberately assigns a BOOL input as a coil
target, proves the structured `VC005` row, activates it to navigate to Network
1, repairs the document, and proves the Error List clears after successful
verification (`validation=True/True/True`). Real-window evidence is
`rungproof-next/build/tia-structured-error-list-2048x1152.png`. No physical PLC
transport was constructed or connected.

## Active-scene Ladder I/O binding browser - 2026-09-30

The Ladder tag editor now derives binding choices from the attached scene's
declared point contract instead of accepting arbitrary free text. Input tags
can select operator Start/Stop where applicable or compatible PC-owned points;
Output tags can select compatible PLC-owned points. The selector exposes
the point type, owner, direction, and purpose, and always includes an explicit
`<unbound>` state. BOOL, INT, DINT, and REAL use exact type matching; TIMER,
COUNTER, and Memory tags remain controller-internal.

Verify + Load combines compiler diagnostics with the new scene-I/O validator.
It rejects undeclared points (`IO001`), unsupported or mismatched types
(`IO002`), invalid tag-role/point-owner direction and memory bindings (`IO003`),
and duplicate PLC output drivers (`IO004`). An empty binding now performs no
scene sample or output commit; the earlier implicit tag-name fallback was
removed. Loading an editor-authored program preserves the active scene, while
the separate demo-loader remains the only workflow that intentionally selects
the conveyor-stop demo scene.

Verification passes with a zero-warning build, 97/97 focused controller/editor
tests, and the Ladder interaction verifier reporting `bindingBrowser=True` and
`validation=True/True/True`. Real-window evidence is
`rungproof-next/build/tia-scene-io-binding-browser-2048x1152.png`. This remains
an offline simulator contract. No PLC transport, physical address, online edit,
or physical-controller write was added.

## Typed numeric Ladder scene I/O - 2026-09-30

The offline controller-to-scene bridge now carries REAL and signed integer
values through the same deterministic sample-execute-commit-plant-publish scan
cycle as BOOL data. DINT is a distinct editor/runtime type instead of being
silently treated as INT: ordinary REAL-to-INT and REAL-to-DINT conversion
rounds nearest-even and clamps to the signed 16-bit or signed 32-bit range.
TRUNC remains the explicit toward-zero operation. Runtime snapshots
publish a separate numeric output image, and Stop drives numeric outputs to
zero before the scene advances.

The tag binding browser now offers exact-type PC-owned inputs and PLC-owned
outputs for BOOL, INT, DINT, and REAL. `SceneSimulationRuntime` samples only
finite PC-owned numeric points and rejects unknown, simulator-owned,
non-numeric, or non-finite output commits. The existing `IO001`-`IO004`
validation remains fail closed, now with exact numeric type compatibility.

Verification passes with a zero-warning build and 99/99 focused tests. The new
scene-level verifier uses the actual `lab-2-15-fume-extractor` DINT selector and
fan-speed points and proves input sampling, MOV execution, output publication,
and safe Stop (`NUMERIC_SCENE_IO_VERIFY PASS`). Real-window evidence covers a
TIA-style PC-owned REAL transmitter binding in
`rungproof-next/build/tia-real-scene-binding-2048x1152.png` and a Studio
5000-style PC-owned DINT selector binding in
`rungproof-next/build/studio5000-dint-scene-binding-2048x1152.png`. The real
window density verifier also passes at one-to-one 2048x1152 scaling. This
remains an offline symbolic simulator boundary with no physical PLC transport
or address.

## Persistent typed Ladder watch tables - 2026-09-30

Both vendor workbenches now provide a functional persistent monitoring tool:
TIA-style `Watch table 1` and Studio 5000-style `Watch List`. The project tree
and View menu open the dock. Engineers can add one symbol, add all tags, remove
the selected row, clear the table, resize or collapse the bottom dock, and use
Undo/Redo for watch-list changes. Double-clicking a watch row opens the matching
tag declaration.

The ordered watch list persists in `.ld.json` and follows tag lifecycle changes:
renames update the watched symbol and deleting an unused tag removes it. Compiler
validation rejects missing or duplicate watched symbols. Loaded offline runtime
rows show typed BOOL/INT/DINT/REAL/TIMER/COUNTER values, tag role, GOOD and scan
state or simulator-force state, plus the active scene binding. Watch-list edits
are engineering metadata and intentionally do not invalidate matching loaded
logic or clear graphical power-flow monitoring.

Verification passes with a zero-warning build, 101/101 focused tests, and the
expanded Ladder interaction verifier reporting `watchTable=True/True/True` for
live data, metadata edits without monitor invalidation, and Undo restoration.
Application-shell, offline controller/scene, and numeric scene-I/O verifiers also
pass. The real-window density verifier passes at one-to-one 2048x1152 scaling.
Visual evidence is
`rungproof-next/build/tia-live-watch-table-2048x1152.png` and
`rungproof-next/build/studio5000-live-watch-table-2048x1152.png`. This remains an
offline simulator feature; no physical PLC transport was constructed or used.

## Deterministic rising/falling edge contacts - 2026-09-30

The offline Ladder runtime and both workbenches now support one-scan Boolean
edge conditions. Each instruction stores its previous operand state under its
own stable element ID, so two edge instructions observing the same tag remain
independent. Rising contacts pulse once on FALSE-to-TRUE; falling contacts pulse
once on TRUE-to-FALSE. Stop and Reset clear edge storage, and the first
subsequent execution establishes a baseline without generating a startup pulse.

The TIA presentation uses P/N edge contacts. The Studio 5000 presentation uses
portable `XIC+ONS` and `XIO+ONS/OSF` composite labels. That Logix presentation
does not claim a controller storage-bit tag, vendor prescan data layout, project
format, or physical-controller equivalence. Edge mode persists in `.ld.json`,
survives editor round-trip with stable IDs, participates in Undo/Redo and exact
wire-position insertion, appears in cross-reference and context help, and is
visible in live power-flow monitoring.

Verification passes with a zero-warning build, 106/106 focused tests, and the
expanded Ladder interaction verifier reporting `edges=True/True`. Application
shell, virtual-controller/scene, numeric scene-I/O, and real-window 2048x1152
density gates pass. Visual evidence is
`rungproof-next/build/tia-edge-contacts-2048x1152.png` and
`rungproof-next/build/studio5000-edge-composites-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.

## Local AI/MCP simulator boundary - 2026-10-02

RungProof Next includes `rungproof-next/tools/rungproof_mcp.py`, a local stdio
MCP server registered in Codex as `rungproof`. It lets AI agents list and read
the migrated scene catalog, read bounded engineering help, author/read Ladder
editor projects inside `artifacts/mcp-workspace/projects`, validate real
compiler and symbolic scene bindings, execute deterministic scene contracts,
run named regression lanes, and launch the local UI.

The server intentionally exposes no arbitrary shell, arbitrary path, physical
PLC, endpoint, driver, address, or I/O tools. Project names are traversal-safe,
writes are confined to the ignored MCP workspace, and project/integration
verification builds the current C# source before starting Godot so stale
assemblies cannot produce a false pass. `rungproof_verify_integration` was
smoke-tested with a saved `conveyor-cell` Ladder project: source build, compiler
and symbolic binding validation, and the scene contract all passed. The focused
virtual-controller suite also passed 134/134 with physical PLC transport
construction and connection both explicitly false.

## Editable Ladder project persistence - 2026-10-02

The Ladder workbench now distinguishes mutable engineering projects from
validated executable programs. Project/File -> Save project writes
`.rpproj.json` through `LadderEditorProjectJson`; Open project restores the
complete editor document, including compiler-invalid work in progress, active
block, stable rung/branch/instruction IDs, next-ID allocation, typed tags and
startup values, scene bindings, watch symbols, blocks/routines, and tasks/OBs.
Opening a project never replaces or starts the offline controller. Verify +
Load remains the separate compiler and scene-binding gate into deterministic
execution. Existing `.ld.json` is documented as executable interchange, not
the authoring project format.

Malformed JSON, unknown schema/kind/enums, null structural collections, and
rungs without a branch fail closed with `EPJ001`. Import also advances a
stale/hand-edited next-ID counter past all retained stable ID suffixes. The
current proof is a zero-warning build, 132/132 focused tests, and a passing
native Ladder interaction verifier reporting `projectPersistence=True`. That
native round trip saves a deliberately compiler-invalid draft through the same
operation used by the file dialog, mutates the editor, opens the project,
proves the original stable instruction ID and invalid operand were restored,
and proves the already-loaded runtime program and scan were not replaced. The
same verifier covers instruction-specific contextual
properties, dock behavior, editing, validation, monitoring, watch, search,
help, blocks/routines, tasks/OBs, and clipboard workflows. No physical PLC
transport was constructed or connected.

## Numeric math instruction expansion - 2026-09-30

The offline Ladder model, compiler, runtime, graphical canvas, instruction
palette/tree, context help, persistence, monitoring, and cross-reference now
share explicit MOD, ABS, NEG, and square-root operations in addition to MOV,
ADD, SUB, MUL, and DIV. Both workbenches now present the current `SQRT`
mnemonic; Studio 5000 help records `SQR` as the pre-v36 alias. This naming does
not claim vendor project-file or status-bit compatibility.

Binary operations require Source A and Source B. Unary MOV, ABS, NEG, and
SQRT use Source A and ignore Source B. The Properties dock now labels both
operands and accepts a tag, numeric timer/counter member, or invariant-culture
literal directly in Source A, so literal math is authorable through the UI
rather than only through JSON. Literal divide/modulo by zero and literal
negative square-root inputs fail validation. Equivalent dynamic faults preserve
the prior destination and publish distinct `VC_RUNTIME_DIV_ZERO`,
`VC_RUNTIME_MOD_ZERO`, or `VC_RUNTIME_DOMAIN` diagnostics; non-finite results
publish `VC_RUNTIME_NUMERIC`.

Verification passes with a zero-warning build, 109/109 focused
controller/editor tests, the Ladder interaction verifier reporting
`advancedMath=True/True`, the application-shell verifier, the offline virtual-
controller/scene verifier, the numeric scene-I/O verifier, and a real-window
one-to-one 2048x1152 density check. Visual evidence is
`rungproof-next/build/tia-advanced-math-2048x1152.png` and
`rungproof-next/build/studio5000-advanced-math-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.

## Scientific math and TRUNC instruction family - 2026-09-30

The offline Ladder IR, compiler, runtime, graphical canvases, organized
instruction palettes, instruction tree/help, persistence, cross-reference, and
monitoring now include EXPT, LN, SIN, COS, TAN, ASIN, ACOS, ATAN, and TRUNC.
Trigonometric angles are radians. EXPT is binary; the other additions are unary
and disable Source B in the Properties dock. TIA and Studio 5000 use separate
Scientific Math and Conversion palette tabs so these instructions do not
recreate the earlier flat, overcrowded toolbar.

Compiler validation rejects literal LN operands at or below zero, ASIN/ACOS
operands outside -1 through 1, negative EXPT bases with fractional exponents,
and zero raised to a negative exponent. Equivalent dynamic faults preserve the
prior destination and publish `VC_RUNTIME_DOMAIN`; non-finite results continue
to publish `VC_RUNTIME_NUMERIC`. Current Logix mnemonics are primary, while
instruction help records the pre-v36 aliases XPY, ASN, ACS, ATN, TRN, and SQR.

Verification passes with a zero-warning build, 112/112 focused tests, the
Ladder interaction verifier reporting `advancedMath=True/True/True/True`, the
application-shell verifier, the offline virtual-controller/scene verifier, the
numeric scene-I/O verifier, and a real-window one-to-one 2048x1152 density
check. Visual evidence is
`rungproof-next/build/tia-scientific-math-2048x1152.png` and
`rungproof-next/build/studio5000-scientific-math-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.

## Three-operand NORM_X and SCALE_X value conditioning - 2026-09-30

Numeric output instructions now persist and edit a third operand. Source A,
Source B, and Source C are MIN, VALUE, and MAX for normalization/scaling. The
new field participates in compiler validation, atomic tag rename/reference
counting, semantic cross-reference, history snapshots, JSON save/load, runtime
monitoring, and graphical block rendering. Older `.ld.json` files without
`sourceC` load it as `"0"`.

NORM_X computes `(VALUE - MIN) / (MAX - MIN)`. SCALE_X computes
`VALUE * (MAX - MIN) + MIN`. Literal ranges with MIN greater than or equal to
MAX fail compilation with `VC009`; invalid dynamic ranges preserve the prior
destination and publish `VC_RUNTIME_RANGE`. The TIA workbench presents the
native NORM_X/SCALE_X names. Studio 5000 has no matching native Ladder blocks,
so its workbench explicitly labels these as CPT-equivalent simulator macros
instead of claiming vendor equivalence or status-bit behavior.

Verification passes with a zero-warning build, 114/114 focused tests, the
Ladder interaction verifier reporting `scaling=True/True`, application-shell,
offline virtual-controller/scene, numeric scene-I/O, and real-window one-to-one
2048x1152 density gates. Visual evidence is
`rungproof-next/build/tia-scaling-2048x1152.png` and
`rungproof-next/build/studio5000-scaling-cpt-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.

## Explicit numeric conversions and vendor rounding semantics - 2026-09-30

The offline Ladder IR, runtime, graphical canvases, organized Conversion
palette, instruction tree/help, persistence, cross-reference, and monitoring
now include CONVERT, ROUND, CEIL, and FLOOR. TIA presents those native names.
The Studio 5000 view presents ordinary destination-type conversion as MOV and
labels ROUND/CEIL/FLOOR as simulator CPT macros; it does not claim that those
three macros are native Logix instructions or reproduce vendor status flags.

Ordinary finite REAL-to-INT/DINT conversion now follows the documented Siemens
and Rockwell nearest-even rule before clamping to signed 16-bit or signed
32-bit range. ROUND also uses nearest-even. CEIL rounds toward positive
infinity, FLOOR toward negative infinity, and TRUNC remains explicitly toward
zero before destination conversion. Focused regression cases cover positive
and negative midpoint ties, signed ceiling/floor behavior, ordinary arithmetic
destination conversion, and the distinction between CONVERT and TRUNC.

Verification passes with a zero-warning build, 115/115 focused tests, the
Ladder interaction verifier reporting `conversion=True/True/True/True`, the
application-shell verifier, the offline virtual-controller/scene verifier, the
numeric scene-I/O verifier, and a real-window one-to-one 2048x1152 density
check. Visual evidence is
`rungproof-next/build/tia-conversion-2048x1152.png` and
`rungproof-next/build/studio5000-conversion-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.

The reported `msedge.exe` breakpoint dialog is not emitted by the current
RungProof Next code path. Source inspection found no Edge/WebView/process or
shell-URL launch path. A live process audit showed the open simulator windows
as native Godot processes and Edge as a separate background
`--no-startup-window` process tree with no RungProof or localhost argument.
No Edge process was terminated or modified during diagnosis.

## Retentive TONR/RTO timers and explicit timer reset - 2026-09-30

The offline Ladder IR, compiler, deterministic runtime, mutable editor/history,
JSON persistence, semantic index, graphical canvases, instruction palette/tree,
context help, monitoring, and both vendor workbenches now support a retentive
on-delay timer plus explicit timer reset. TIA presents `TONR` and `RT`; the
Rockwell view presents Ladder `RTO` and `RES`. These names and scan semantics do
not claim Siemens/Rockwell project-file or status-word compatibility.

While enabled, TONR/RTO accumulates one configured base-scan period until its
preset. A false rung pauses without clearing elapsed or done state. Simulator
Stop clears active timing/input indications but preserves elapsed and done;
controller Reset clears all timer state. A true RT/RES rung clears accumulated,
timing, input, and done before later networks execute. Compiler issue `VC013`
rejects a TIMER instance assigned to more than one timer instruction so mixed
TON/RTO ownership cannot make Stop retention ambiguous; explicit reset
references to the owned instance remain valid.

Semantics were checked against Siemens V21 `TONR: Time accumulator` /
`RESET_TIMER` documentation and Rockwell Studio 5000 Ladder `RTO` / `RES`
documentation. Verification passes with a zero-warning build, 119/119 focused
tests, and the Ladder interaction verifier reporting
`timers=True/True/True/True/True`. Application-shell, offline virtual-controller,
numeric scene-I/O, and real-window one-to-one 2048x1152 density gates pass.
Visual evidence is
`rungproof-next/build/tia-retentive-timer-2048x1152.png` and
`rungproof-next/build/studio5000-rto-2048x1152.png`. No physical PLC transport
was constructed, connected, or written.

## Reference-safe block/routine and task/OB lifecycle - 2026-09-30

The offline project workspace now supports the full create, rename, and delete
lifecycle for blocks/routines and task/OB schedules. These controls live in the
vendor-specific Project objects / Controller objects tool page rather than in
the Ladder instruction strip or bottom diagnostics dock. Both vendor views use
their own labels while editing the same simulator-native project model.

Renames preserve stable IDs, so task entry assignments and CALL/JSR targets do
not break. Deletion fails closed when a block is the controller entry, is owned
by a task/OB, or is targeted by CALL/JSR. The final block and final task are also
protected. Successful lifecycle changes participate in the existing exact
snapshot Undo/Redo history. Direct JSON remains compiler-validated before load.

Verification passes with a zero-warning build, 122/122 focused tests, and the
Godot Ladder interaction verifier reporting
`blockLifecycle=True/True/True` and `taskLifecycle=True/True/True`. The
application-shell, offline virtual-controller/scene, numeric scene-I/O, and
real-window one-to-one 2048x1152 density gates also pass. Visual evidence is
`rungproof-next/build/tia-project-lifecycle-2048x1152.png` and
`rungproof-next/build/studio5000-project-lifecycle-2048x1152.png`. No physical
PLC transport was constructed, connected, or written.

## Final goal release gate - 2026-09-30

The user authorized a Git checkpoint and push only after the full offline PLC
Ladder programming-environment goal is genuinely complete. Do not push an
intermediate slice. Before that final push: run the complete unit, compiler,
runtime, persistence, scene-I/O, Godot interaction, app-shell, real-window DPI,
and visual-review gates; inventory every tracked modification and untracked
file; preserve or deliberately include all intended project work; resolve any
unrelated/user-owned files without destructive cleanup; review the final diff;
commit the finished checkpoint; push the current project branch to `origin`;
and verify both the remote result and a clean local working tree.

Current evidence is not a release-ready tree: branch
`codex/simulator-hud-pivot` has 1,282 status entries. That count is a live
snapshot, not permission to discard files. The overall PLC-editor goal remains
active, so no commit or push is due yet.

## Ladder branch spacing and conductor rendering correction - 2026-09-30

The graphical Ladder canvas previously used a fixed 62 px parallel-branch gap
while placing the upper branch's NO/NC caption and the lower branch's symbolic
tag in nearly the same vertical band. Each network also retained a fixed height
regardless of branch count. In addition, the base conductor was drawn across
the entire branch before contact symbols were overlaid, visibly running through
XIC/XIO and NO/NC bars.

The canvas now reserves a 92 px band per additional parallel branch and grows
the network/rung bounds and following-network position dynamically. Hit testing,
insertion cursors, scrolling extent, selection bounds, and the Logix End marker
use the same geometry. Base and monitored conductors are drawn as explicit
segments that stop at contact, comparison, coil, timer, counter, numeric,
CALL/JSR, and RETURN/RET symbol boundaries.

Verification passes with a zero-warning build, 122/122 focused controller
tests, the Ladder interaction verifier reporting `rungLayout=True`, the
application-shell, offline virtual-controller/scene, numeric scene-I/O, and
one-to-one 2048x1152 DPI gates. Visual evidence is
`rungproof-next/build/tia-rung-layout-after-2048x1152.png`,
`rungproof-next/build/studio5000-rung-layout-after-2048x1152.png`, and
`rungproof-next/build/tia-monitor-rung-layout-after-2048x1152.png`.

## Contextual Ladder instruction properties - 2026-10-02

The editor no longer displays network title, coil, timer, counter, compare,
numeric, block, and task fields together in a generic bottom Properties form.
That design did not match the object-specific workflows expected from either
TIA Portal or Studio 5000 and exposed unrelated controls for the selected
instruction.

The bottom engineering dock now contains only Error List, Output, and Watch.
Block/routine and task/OB lifecycle controls moved to the vendor-specific
Project objects / Controller objects tool page. A graphical contact,
comparison, coil, timer, counter, numeric instruction, CALL/JSR, RETURN/RET, or
network/rung opens an embedded contextual property editor by double-click or
through its right-click Properties command. The editor shows only fields valid
for that selected object and retains the TIA or Logix terminology of the active
workbench.

Verification passes with a zero-warning build, 122/122 focused controller and
editor tests, and the Ladder interaction verifier reporting
`contextualProperties=True/True`. Application-shell, offline controller/scene,
numeric scene-I/O, and visible one-to-one 2048x1152 DPI gates pass. Visual
evidence is
`rungproof-next/build/tia-contextual-properties-base-2048x1152-v3.png`,
`rungproof-next/build/tia-contextual-contact-properties-2048x1152-v3.png`, and
`rungproof-next/build/studio5000-contextual-contact-properties-2048x1152-v2.png`.
No physical PLC transport was constructed, connected, or written.

## Typed Ladder tag startup values - 2026-10-02

The offline Ladder tag editors now expose each BOOL, INT, DINT, or REAL tag's
startup value instead of silently retaining a hidden default. BOOL accepts
TRUE/FALSE and 1/0, INT and DINT are parsed with their signed 16-bit and 32-bit
ranges, and REAL rejects NaN and infinity. Timer and counter instance startup
storage remains runtime-defined and read-only in the tag editor.

Tag startup values participate in the exact editor undo/redo snapshots, are
written to and restored from `.ld.json`, and are applied by offline controller
Reset. Compiler validation rejects out-of-range integer or non-finite REAL
initial values even when they originate from hand-edited JSON rather than the
UI.

Verification passes with a zero-warning build, 123/123 focused controller and
editor tests, and the Godot Ladder interaction verifier reporting
`tagEdit=True/True/True/True`; that sequence proves unused deletion, atomic
rename, startup-value editing, and undo restoration through real controls.
Visual evidence is
`rungproof-next/build/tia-tag-initial-values-2048x1152-v3.png` and
`rungproof-next/build/studio5000-tag-initial-values-2048x1152-v3.png`. The
independent visual audit also identified and drove a correction to parallel
branch topology: every branch now visibly rejoins before the single shared
output, rather than allowing a lower conductor to appear to bypass the coil.
The tag edit form now has persistent NAME, TYPE, ROLE, INITIAL, and BINDING
labels, with improved selected-row, output-message, and Siemens menu contrast.
No physical PLC
transport was constructed, connected, or written. The overall Ladder-editor
goal remains active; this slice does not claim arrays, UDTs, nested branch
topology, or vendor project compatibility.
## Block-local JMP and LABEL/LBL program control - 2026-10-02

RungProof Next now implements simulator-scoped block-local jump control across
the IR, compiler, editor, persistence, runtime, monitoring, search, help, and
both vendor presentations. TIA exposes `JMP` and `LABEL`; Studio 5000 exposes
`JMP` and `LBL`. Names are local to the containing block/routine. Missing
targets, empty names, and duplicate declarations fail validation with `VC014`.

The deterministic runtime falls through on a false JMP and resumes at the
matching label on a true JMP. A 10,000-network-per-scan watchdog publishes
`VC_RUNTIME_JUMP_LIMIT`, stops the offline controller, and drives BOOL and
numeric outputs safe if a backward jump loops indefinitely. The feature does
not create physical PLC transport and does not claim vendor project-file or
commissioning compatibility.

The graphical editor has vendor-labeled Program Control buttons and tree
entries, graphical JMP and destination-marker blocks, instruction-scoped
right-click/double-click properties, undo/redo, JSON round-trip, help, and
cross-reference entries for both the jump site and declaration. The bottom
dock remains reserved for Error List, Output, and Watch data rather than
showing every instruction's operands at once.

Verification: solution build completed with zero warnings/errors; all 128
virtual-controller tests passed; the native Ladder interaction verifier passed
including JMP insertion, LABEL/LBL insertion, contextual label editing, and
the instruction-specific property popup. Deterministic 2048x1152 review images
are `rungproof-next/build/tia-jump-label-2048x1152.png` and
`rungproof-next/build/studio5000-jump-label-2048x1152.png`. Independent visual
review found no P1 defects or broken wire topology. It identified the need to
make the destination semantics more visually explicit and to improve the tiny
instruction captions; the destination now uses a distinct pale marker labeled
`DESTINATION`, and NO/NC/XIC/XIO plus coil captions use darker, larger text.

## Visible draggable Ladder workbench docks - 2026-10-02

The prior workbench used split containers, but their grab areas were visually
indistinct and narrow enough that the panels appeared fixed. All TIA and Studio
5000 Ladder splits now expose persistent high-contrast divider bars, a
12-pixel minimum drag target, and nested-intersection dragging. The project,
instruction/tag, and Error List/Output/Watch panels have practical minimum
sizes, resize tooltips, and still retain independent collapse/reopen buttons.
The split hosts no longer compete with the editor for stretch allocation, so
the project tree does not consume the center workspace. The instruction/tag
dock defaults to 340 pixels, retains full instruction names as hover tooltips,
and its contents fill and clip within the dock instead of leaking an orphaned
tab into the editor. NO/NC/XIC/XIO and coil captions use darker 11-pixel text.

The native interaction verifier now changes and restores every split offset
and checks visible/enabled draggers in addition to the three collapse/reopen
pairs. It passes with `docksWorked=True/True`. The real-window density gate
also passes at 2048x1152 with one UI unit per pixel. Visual evidence is
`rungproof-next/build/tia-resizable-docks-2048x1152.png` and
`rungproof-next/build/studio5000-resizable-docks-2048x1152.png`. Independent
visual review found no remaining rung/wire overlap, broken continuity, panel
overflow, splitter/collapse defect, or DPI distortion. The zero-warning build,
128/128 focused tests, application-shell, offline-controller, numeric scene-I/O,
Ladder interaction, and real-window density verifiers all pass. No physical
PLC transport was constructed or connected.

## Ladder instruction and network clipboard - 2026-10-02

The TIA and Studio 5000 workbenches now provide real editor clipboard behavior
through the Edit menu, the instruction/network right-click menu, and focused
canvas Ctrl+C/Ctrl+V shortcuts. A selected contact, edge contact, or comparison
is copied as an isolated instruction template and pasted at the active wire
insertion point or immediately after the selected instruction. Selecting an
output or network/rung copies the complete network/rung and pastes it after the
selection.

Paste is a document mutation, not a visual duplicate: complete network/rung
pastes regenerate the rung, every branch, and every contained instruction ID;
single-instruction paste generates a new type-appropriate ID. Operands,
instruction modes, presets, labels, and output configuration are retained.
Each paste records one exact Undo/Redo transaction, and loading or creating a
project clears the in-memory clipboard so stale objects cannot leak between
projects.

Verification passes with a zero-warning build, 130/130 focused controller and
editor tests, and the native Ladder interaction verifier reporting
`clipboard=True/True/True/True` for instruction paste, instruction undo, rung
paste, and rung undo. The verifier exercises Ctrl+C/Ctrl+V and context-menu
paths through live controls. Visual evidence is
`rungproof-next/build/tia-clipboard-menu-2048x1152.png` and
`rungproof-next/build/studio5000-clipboard-menu-2048x1152.png`. No physical PLC
transport was constructed, connected, or written.
