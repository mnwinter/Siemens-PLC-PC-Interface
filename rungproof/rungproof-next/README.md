# RungProof Next

RungProof Next is the clean-sheet, enterprise-oriented successor to the
prototype/native RungProof renderer. It uses Godot 4.7.2 for real-time 3D,
Blender-authored source models, glTF 2.0 delivery assets, PBR materials, and a
typed C# simulation/application layer.

The previous primitive-built models are reference material only. They are not
part of this production catalog.

## Toolchain

- Godot 4.7.2 .NET for Windows;
- .NET 10 SDK for the Godot 4.7 editor host and application target;
- Blender 5.2 LTS for source modeling and glTF export;
- Python 3 only for repository validation/build tooling.

The verified portable toolchain is stored in the ignored `.tools` directory.
Double-click `RUN-RUNGPROOF-NEXT.cmd` to restore packages, build, import assets,
and open the Windows application. A fresh source copy does not need generated
Godot/NuGet caches. See `docs/DEVELOPMENT_SETUP.md` for the required tool layout.

Current review evidence is maintained in
[`../docs/WHOLE_PROGRAM_REVIEW.md`](../docs/WHOLE_PROGRAM_REVIEW.md).
The catalog contains 77 scenes in three groups, including five authored demos,
and 294 runtime assets. Candidate/training inclusion does not establish
production quality approval. Older phase descriptions below record the
original milestones; use the review matrix for current verification boundaries.

For native multi-angle inspection, launch Godot with `-- --app-shell
--visual-scene-review`. The opt-in review bar provides catalog navigation, four
diagonal camera views, overhead, detail zoom and an equipment-focus selector. Scene navigation uses the
normal unsaved-work guards. Normal launch has no review bar.
`-- --audit-dual-spindle` checks Scene 36's shared-stock alignment, fixture
bearing, axial feed, moving clearance, slide contact/travel and Stop/Reset/restart
behavior. Eighteen checks pass for the repaired reference installation. This
diagnostic is separate from the geometry regressions and does not imply
selected-controller operation or mechanical acceptance.

`-- --audit-robot-cnc` checks Scene 38's stock bearing, actual six-joint/tool
attachment, two-finger contact, staged transfers through open doors, retracted
tool clearance, door track bearing, sampled clearance and Stop/Reset/restart
behavior. All 23 focused checks pass for the repaired reference. It is separate
from geometry regressions and does not establish normal selected-controller
operation, physical interlocks or mechanical acceptance.
In standalone `--visual-plant-review`, held Step advances the sequence and its
explicit joint/access motions; generic autonomous adapters such as the spindle
remain frozen. Release the clock to observe those animations. Held steps also
discard leftover time at phase boundaries, so counts are not time acceptance.

For Demo 5's offline operator view, Hold offline plant clock freezes scans and
equipment motion. Step 0.5 s executes 25 existing 20 ms scan/gantry ticks;
normal Run and manual permissives are still required. Editor, scene and source
changes release the hold. Scene 50 uses the same controls with Step 2.0 s
(100 actual 20 ms scans) for its single-clock carton plant. External PLC stepping
and other scene clocks are excluded.
`-- --verify-plant-motion --visual-scene-review` runs 32 offline motion checks,
including hold, full-sweep stepping, Stop, permissive loss, Reset and release.
`-- --verify-carton-static-routes` runs the focused Scene 2 cable and optical
path checks without the full catalog sweep. It screens 5 mm broad overlaps
against cable triangle bounds with a 1 mm world allowance; it is offline only.

The Scene 32 standalone `--visual-plant-review` action bar also has a camera-only
Pallet underside view for inspecting strap returns inside the fork openings.

`-- --verify-scene-geometry` runs 487 focused geometry/workflow checks for Demo 5 clearance/attachment,
the pallet cell's grounded installation, imported robot joints/tool attachment,
sampled transfer clearance, supported outbound path, receiver landing/count
agreement, Stop/Reset/restart guard and unreachable-target rejection,
shipping pallet/case bearing contacts, closed strap bands, sampled strap/load clearance,
strap return/belt clearance, belt support, mode guards, bounded incremental jog, Stop/resume,
continuous actual-case optical/position feedback and selected-controller ownership,
bottle shuttle label bounds, belt support, sensor installation, actual body optical feedback,
configured travel/belt speed, both-leg Stop/resume, event transitions and controller ownership,
tote finishing station/conveyor clearance, grounded supports and connected overhead heads,
full-route belt contact, supported discharge and attached tools through the declared preview,
mixer placement/tank sizing/chute identity/floor support, scaled radar feedback,
the parcel sorter's supported paths, optical heights and Stop/Reset,
inspection conveyor support/photoeye clearance/feedback, gallery floor/probe support,
drive-alarm identity/labels/mast support/alarm projection, and motor-state plates
and actual shaft true/false/Reset output projection, plus label-print prop identity,
tray/carton support, readout mast and printer-paper contact. The rendered
`-- --verify-scene-controls --visual-scene-review` regression also checks
that the review bar/menu and gantry clock cannot activate underlying 3D controls. These checks do not supply
missing controllers or implement enum/STRUCT/array lesson behavior.
For the declared plant geometry only, use `-- --scene-id=lab-2-23-parcel-sorter
--visual-plant-review`. It starts stopped and labels the preview as having no PLC
controller. This mode cannot be combined with app-shell/verification modes.
It does not establish normal operator Run behavior: this sorter currently has
no supplied reference controller, and its normal shell Run opens the blank editor.
`-- --report-scene-geometry` inventories the actual composed meshes in
all 77 shell scenes. Overlapping bounds are inspection candidates, not proof of
solid collision or visual acceptance. Track native observations in
[`../docs/MULTI_ANGLE_SCENE_REVIEW.md`](../docs/MULTI_ANGLE_SCENE_REVIEW.md).

## Saved demo projects

The five editable files in `programs/demos` are generated from the same authored
documents used by the Demo menu. In Logic Editor, choose Project > Open project
and select one of these files; opening a valid file selects its bound scene and
loads its controller stopped. Return to the scene and press Run.

After editing `AuthoredDemoLadderPrograms.cs`, regenerate and check the files
from this directory:

```powershell
.\.tools\dotnet\dotnet.exe run --project tools/demo-projects/RungProof.DemoProjects.csproj -- --write
.\.tools\dotnet\dotnet.exe run --project tools/demo-projects/RungProof.DemoProjects.csproj -- --check
```

The tool defaults to read-only checking. App-shell verification also rejects
saved projects that differ from their Demo-menu document. These are offline
references; machine feedback remains manual where the scene declares it.

## Sum and Product exercise references

Lab 9.1 and Lab 9.2 retain their empty ladder exercise. Their A NEXT/B NEXT
readouts and sidebar actions cycle manual DINT values through 0, 1, 2, 5, 10.
To run the supplied references, open Logic Editor > Project > Open project:

- Sum: `programs/examples/09-sum-function-reference.rpproj.json`
- Product: `programs/examples/09-product-function-reference.rpproj.json`

Return to the scene, press Run, set A=2 and B=5, and enable A VALID, B VALID
and CALCULATE. Expect SUM 7 or PRODUCT 10 and a green validity lamp. Losing
any permissive clears validity while retaining the last result. Stop clears
the numeric output image; Reset clears all inputs and values.

Each reference always scans its calculation FB and uses global symbolic tags.
It does not model FB parameter transfer or instance-local storage. The scenes
remain offline and require a loaded program before calculating.

## Function Selector exercise reference

Lab 9.4 has manual DINT operands and a real function choice. Open
`programs/examples/09-function-selector-reference.rpproj.json` through Logic
Editor > Project > Open, verify and load offline, then return and Run.
Set A=2, B=5 and enable OPERANDS, FUNC VALID and CALCULATE. FUNC NEXT cycles
0, 1 SUM, 2 PRODUCT, 99 invalid. Expect RESULT 7 for choice 1 and 10 for choice
2. Choices 0/99 clear validity and retain the last result; Stop clears the
output image and Reset clears all inputs and readouts.

Main always calls FB_Selector, which calls only the selected FC_Sum or
FC_Product. This original offline reference uses global symbolic tags; it
does not model FB parameter transfer or instance-local storage. The exercise
starts empty until a program is loaded. Readouts sit behind the pushbuttons
so their picking areas do not intercept front-view button clicks.

## Box Volume exercise reference

Lab 9.10 now provides manual DINT length, width and height in millimetres and
a live PLC-owned volume in cubic millimetres. Open
`programs/examples/09-box-volume-reference.rpproj.json` through Logic Editor >
Project > Open, verify and load offline, then return to the scene and Run.
The three input readouts cycle 0, 250, 500, 720, 850, 1000 mm. Set 850/720/720
and enable all three validity buttons: expect `440640000` and a green lamp.
All six actions also appear in the sidebar.

Main always calls FB_Volume; two MUL networks calculate base area and volume
using global symbolic tags. The reference requires each dimension to be
1..1000 mm, keeping the largest result (`1000000000`) within DINT range.
Missing validity or an invalid dimension clears the lamp and retains the last
result; Stop clears outputs and Reset clears all inputs and values. The
exercise starts empty. Its carton and sensor heads remain static illustrations;
manual dimensions do not resize the carton or represent sensor acquisition.
FB parameter transfer and instance-local storage are not modeled.

## Sum and Counter exercise reference

Scene `lab-9-03-sum-and-counter-function` opens with an empty ladder exercise.
Its A NEXT and B NEXT readouts are clickable numeric inputs; SUM and COUNT are
PLC-owned live output readouts. To run the supplied offline reference:

1. Select Lab 9.3 and open Logic Editor.
2. Choose Project > Open project and open
   `programs/examples/09-sum-counter-reference.rpproj.json`.
3. Choose Online > Verify + load offline, return to the scene, and press Run.
4. Cycle A to 2 and B to 5. Enable INPUTS VALID and CALCULATE, then toggle
   CALL COMPLETE on. Expect SUM 7 and COUNT 1. Toggle completion off/on for
   another event; leaving it held must not recount.
5. Stop shows output readouts zero while retaining counter memory. Run restores
   the count. Reset clears manual inputs, operand values and counter memory.

CALL COMPLETE is manually supplied feedback. The reference stores its counter
in global memory; it does not model an instance-local FC counter or a physical
machine call. Losing a permissive clears result_valid while retaining the last
sum and count; Stop clears their output images.

## Architecture rule

The 3D application never owns direct PLC transport. A separate guarded runtime
owns any authorized S7 session and exchanges typed symbolic state through a
versioned local IPC contract. Scene files and asset definitions contain no PLC
IP addresses, physical I/O addresses, or DB offsets.

## Offline virtual controller (Phase 1)

The application includes a bounded, deterministic, simulation-only Ladder
Diagram controller. It supports BOOL normally-open/normally-closed contacts,
coils, series paths, parallel branches, network-order execution, and a fixed
scan period. The conveyor demonstration provides simulated Start and Stop
inputs, seal-in memory, a plant-driven photoeye inhibit, blocked restart, and a
controller/plant Reset.

Open `TOOLS > Virtual Controller`, then choose `LOAD DEMO LADDER`. The persistent
Run, Stop, and Reset controls operate the local controller. Live rung
energization and typed variable values appear in the same panel.

This feature does not connect to, configure, download to, force, or write a
physical PLC. It is not a safety validator, commissioning result, certified IEC
runtime, or evidence of Siemens/Rockwell/CODESYS/OpenPLC equivalence.

See:

- `docs/adr/0002-virtual-controller-phase-1.md` for the engine decision;
- `docs/OFFLINE_LADDER_ACCEPTANCE.md` for the requirement-by-requirement
  completion gate and reproducible evidence commands;
- `docs/VIRTUAL_CONTROLLER_CONFORMANCE.md` for the supported instruction matrix;
- `docs/VIRTUAL_CONTROLLER_PROGRAM_SCHEMA.md` for JSON and scan semantics;
- `docs/VIRTUAL_CONTROLLER_ENGINE_EVALUATION.md` for compiler/runtime research;
- `docs/VIRTUAL_CONTROLLER_PROVENANCE.md` for evaluated engines and licenses.

Run the focused automated acceptance checks from this directory:

```powershell
.\.tools\dotnet\dotnet.exe run --project .\tests\RungProof.Next.VirtualController.Tests.csproj
$godot = '.\.tools\godot\Godot_v4.7.2-stable_mono_win64\Godot_v4.7.2-stable_mono_win64_console.exe'
& $godot --headless --path . -- --verify-virtual-controller
```

The focused suite includes a coherent offline-engineering acceptance path that
authors and persists an editable project, reopens it without starting a
runtime, validates bindings, compiles a fresh immutable program, exchanges
symbolic scene I/O, publishes live monitor state, and proves simulator-only
force, safe Stop, and force-clearing Reset behavior. Scene I/O translation is
centralized in a pure symbolic mapper and cannot resolve physical PLC
addresses.

## Catalog gates

`production.catalog.json` accepts approved assets only. Work in progress lives
in `candidates.catalog.json`; moving an asset to production requires the full
quality checklist, blind recognition score, model/import validation, and
animation/control verification. Candidate count is not marketed as catalog
count.

## Current application shell

Normal launch now opens the simulator shell rather than an asset-preview
harness. The current vertical slice includes:

- all 77 catalog scenes in a selectable scene browser;
- searchable access to all candidate assets, with metadata, signal, connector,
  scale, and recognition evidence in the inspector;
- Run, Stop, and Reset controls backed by the deterministic symbolic scene
  runtime;
- clickable in-scene operator controls. Only equipment with an explicit scene
  action (such as Start, Stop, Reset, E-stop, selector, or two-hand control)
  can issue a symbolic runtime command; other scene equipment remains
  non-commanding;
- separate local-runtime and guarded-PLC connection status;
- symbolic point and renderer-binding inspection with no physical addresses;
- project validation with actionable error and warning messages;
- catalog placement into the active scene;
- validated workspace save/load for user-added placements;
- workspace-hierarchy selection with group headers and indented members,
  numeric transform editing, configurable position and
  rotation snapping, color-coded move/rotate/scale viewport gizmos,
  click/list/marquee multi-selection, relationship-preserving copy/paste,
  duplicate/focus/reset,
  persistent named groups with editable saved pivots (or centroid reset),
  world/local transform axes,
  group-safe alignment/distribution, batch deletion, undo/redo, and dirty-state
  indication;
- compatible connector-link authoring with routed 3D link visualization;
- type-checked symbolic signal mappings with explicit `LIVE INPUT` versus
  `AUTHORED ONLY` runtime status;
- verified live input adapters for belt and powered pallet-roller conveyors;
- right-mouse orbit, middle-mouse pan, and wheel zoom navigation.

In-scene controls invoke the scene action declared in that scene's JSON
contract. They do not write a PLC, resolve a physical address, or bypass a
declared interlock. A blocked action is reported in the workspace status line.
Click selection tests each visible mesh's local bounds, preserving rotation
and scale. Empty space between a readout head, mast and foot no longer captures
clicks meant for another control. These are mesh-box tests, not triangle-level
selection or occlusion checks against non-control equipment.

The guarded PLC client starts disconnected. External PLC Settings loads the
parent repository's configured profiles through the Python bridge; approval,
typed ownership and scene/profile matching guard connection and exchange.
The Godot process owns no S7 socket. Offline/fake-adapter checks do not establish
live PLC commissioning; scene contracts alone never authorize physical I/O.
The settings dialog selects and verifies the two supplied JSON profiles; it
does not edit endpoint addresses or mappings. Edit the parent profile/config
files while disconnected, then Verify Profile and authorize the exact scope
again. Faults close the session; reconnect is an explicit verified Connect,
and recovered readiness requires a fresh Run. The configured cycle is a
minimum exchange interval with one pending request, not real-time scheduling.

Launch with `RUN-RUNGPROOF-NEXT.cmd`. Headless verification is available with
`--verify-app-shell`, `--verify-hud`, `--verify-workspace`, and
`--verify-scene-controls`, and `--verify-virtual-controller` (which executes the
conveyor/photoeye/reset path without constructing a real PLC transport). The
scene-control verifier ray-picks the default in-scene Start station
and verifies its symbolic conveyor command). The locked shell contract,
supported resolutions, shortcuts, safety rules, and visual evidence are
recorded in `docs/HUD_ACCEPTANCE.md`.

The classic top menu strip is available on every view. Open the offline Ladder
builder with `Tools > Ladder Logic` or `Basic Logic / Ladder` in the operator
rail, then choose either the TIA Portal-style or Studio 5000-style environment.
These are simulator-native workflows with vendor-familiar organization and
terminology; they do not create Siemens or Rockwell project files and never
connect to a physical PLC.

The integrated PLC editor is now an editable foundation rather than a fixed
demo form. It supports BOOL, INT, DINT, REAL, TIMER, and COUNTER tags,
active-scene symbolic bindings, arbitrary
networks/rungs, NO/NC contacts, parallel branches, output coils, deterministic
one-scan rising/falling edge contacts with per-instruction state,
TON on-delay, TOF off-delay, TP pulse, and retentive TONR/RTO timers with
explicit RT/RES timer reset, TIA Set/Reset coils, Logix OTL/OTU coils, TIA-style `.Q`,
Logix-style `.DN`, shared `.TT`, editable timer presets, rising-edge CTU
counters, TIA `.Q/.CV` and Logix `.DN/.ACC` presentation, counter reset/RES,
comments, graphical Ladder rendering, validation, offline loading,
live timer state, INT/DINT/REAL tags, and EQ/NE/GT/GE/LT/LE comparison blocks with
tag, literal, counter, and timer operands, MOV, ADD, SUB, MUL, DIV, MOD,
ABS, NEG, SQRT, EXPT, LN, SIN/COS/TAN, ASIN/ACOS/ATAN, TRUNC, NORM_X,
SCALE_X, CONVERT, ROUND, CEIL, and FLOOR, typed
numeric destinations and runtime arithmetic/domain diagnostics, plus editable
`.rpproj.json` project Save/Open. Projects can contain multiple selectable blocks/routines with
validated inline CALL/JSR, conditional RETURN/RET, and block-local JMP with
TIA LABEL / Logix LBL destination instructions. A true
RETURN exits only the current called routine/block and resumes the caller; in
a task entry it ends only that task's current scan invocation. Continuous and
periodic tasks/OBs can
be created, named, assigned to entry blocks, prioritized, persisted, and
monitored. Blocks/routines and task/OB schedules can be renamed or deleted from
the vendor-specific Project objects / Controller objects tool page with Undo/Redo. Stable IDs preserve CALL and scheduler
references across renames; deletion is refused for the controller entry block,
task-owned blocks, CALL/JSR targets, and the final remaining block or task.
Their scheduler is deterministic at base-scan boundaries; it does not claim
asynchronous interrupts or preemption. Editor mutations have bounded undo/redo
history with toolbar, Edit-menu, Ctrl+Z/Ctrl+Y, and Ctrl+Shift+Z access; Ctrl+S
and Ctrl+O route to editable Ladder project persistence while the editor is active.
The live virtual-controller panel also provides conspicuous simulator-only
BOOL input/output forcing. Input forces override sampled scene values, output
forces override the calculated simulator output image, Stop de-energizes all
outputs, and Reset clears all forces. Force state is runtime-only and cannot be
saved as a project or sent to a physical PLC.
CTD and counter-preset load are available alongside CTU and RES, with
false-to-true edge memory kept per instruction. This is not yet a complete
replacement for TIA Portal or Studio 5000; wider bit-string, time, and string
conversions, arrays/UDTs,
and the rest of the full editor roadmap remain to be implemented. TIA exposes
NORM_X/SCALE_X directly. The Logix view labels the same simulator operations as
CPT-equivalent macros because Studio 5000 has no native NORM_X/SCALE_X blocks.
TIA also exposes CONVERT, ROUND, CEIL, and FLOOR directly. In the Logix view,
ordinary destination conversion is presented as MOV conversion, while
ROUND/CEIL/FLOOR are explicitly labeled simulator CPT macros rather than native
Logix instructions.

Both vendor workbenches include project-wide Find All and semantic
cross-reference. The index distinguishes tag declarations, reads, writes,
block/routine calls, task entry assignments, and rung/network declarations.
Double-clicking a result navigates to the owning block and rung, while tag
declarations return to the tag table. Timer/counter member references resolve
to their root instance tag.

Context-sensitive instruction help is available from the editor toolbar,
vendor menus, and F1. The selected instruction drives an authoritative catalog
entry with the appropriate TIA-style or Logix-style name, operands, scan
semantics, restrictions, and an example. The catalog covers every instruction
currently exposed by the editor and states the offline/vendor boundary.

The project tree and instruction tree are interactive controls, not display
text. Selecting hierarchy nodes changes editor focus or diagnostics, and
double-clicking supported instructions inserts them into the selected branch.
The TIA-style Watch table and Logix-style Watch List are persistent project
tools rather than placeholders. They support adding one symbol, adding all
symbols, removing selected symbols, clearing the list, and Undo/Redo. While an
offline program is loaded they show typed live values, role, simulator force or
GOOD/scan quality, and scene binding. Watch-list edits are engineering metadata,
so they do not invalidate otherwise identical loaded logic; double-clicking a
row opens that tag's declaration.
Individual graphical contacts, comparisons, and output instructions can be
selected directly on the canvas. Contact operands and NO/NC type can be
changed without replacing their stable identity; selected series instructions
can be moved left/right or deleted exactly, with every mutation participating
in Undo/Redo. The Edit and right-click menus plus Ctrl+C/Ctrl+V copy either the
selected condition instruction or the selected network/rung. Instruction paste
targets the active wire insertion slot or follows the selected instruction;
network/rung paste follows the selected network/rung. Every pasted rung,
branch, and instruction receives a new stable ID and the complete paste is one
undoable operation. Double-clicking an instruction, or choosing Properties from its
right-click menu, opens a contextual editor containing only that instruction's
applicable operands. Network/rung titles use the same contextual workflow;
timer, counter, compare, numeric, CALL/JSR, RETURN/RET, JMP/LABEL/LBL, and coil fields are never displayed
together as an unrelated generic form. Parallel branch rows reserve independent tag, symbol, and caption
bands, and multi-branch networks grow vertically instead of allowing labels to
collide with adjacent logic. Conductors terminate at XIC/XIO/NO/NC, comparison,
and output symbol boundaries rather than being painted through the symbols.
Clicking a wire segment places a vendor-colored insertion cursor;
the next contact or comparison is inserted at that exact series position
instead of being appended blindly. New empty branches and networks open with
an insertion cursor ready for their first condition. Parallel branches can be
added and removed explicitly while the
document model enforces at least one logic path per network/rung. Tag-table
editing supports type, role, startup value, and binding changes plus atomic
symbolic rename across all blocks. BOOL startup values accept TRUE/FALSE or
1/0; INT and DINT values are range checked; REAL values must be finite. Reset
restores these typed startup values. **Save project** writes an editable
`.rpproj.json` document that preserves stable IDs, the active block, tags,
typed startup values, bindings, watches, blocks/routines, tasks/OBs, and even
compiler-invalid work in progress. **Open project** restores that authoring
state but never starts or replaces the simulator controller. Verify + Load is
the separate fail-closed boundary that compiles the current document before it
can execute. The `.ld.json` format remains the validated executable-program
interchange described in the program schema; it is not the editor project file.
Both workbenches show the active block/routine and current project filename in
the editor tab. Both use the conventional leading `*` while the
current editor snapshot differs from the last successful Save/Open baseline;
Undo back to that exact baseline clears the marker automatically.
Referenced tags cannot be deleted; unused tags can be removed and all
tag-table mutations participate in Undo/Redo.
Tag bindings are selected from the active scene contract instead of entered as
unchecked text. The selector filters inputs to type-compatible PC-owned scene
points and outputs to type-compatible PLC-owned scene points, shows each
point's type, owner, and purpose, and always provides an explicit `<unbound>`
choice. BOOL, INT, DINT, and REAL points are supported with exact type matching.
Verify + Load
fails closed with `IO001`-`IO004` diagnostics for missing points, unsupported
types, invalid direction/ownership, or duplicate output drivers. INT is signed
16-bit, DINT is signed 32-bit, and ordinary REAL-to-integer conversion rounds
nearest-even before clamping to the declared range. TRUNC explicitly discards
the fractional part first. Loading an editor program preserves the active scene.
Only `Load Demo Ladder` selects the dedicated demo scene.
The project/organizer and instruction/tag/project-object docks are horizontally resizable
and independently collapsible. The central editor and named Inspector/Output
dock are vertically resizable. The bottom engineering dock contains only Error
List, Output, and Watch data; instruction parameters are contextual and project
object scheduling lives in the right tool dock. Verify failures populate
structured error rows with the compiler code, exact document path, and message;
double-clicking an error navigates to its tag, task/OB, block/routine, and
network/rung when that location exists. Editing marks the prior result as stale,
and successful reverification clears the Error List before loading the offline
runtime. Instructions are grouped into Bit Logic, Timers, Counters,
Compare, Math and Move, and Program Control palettes rather than one flat bar.
When the exact editor document is loaded into the offline controller, both
vendor canvases monitor executed Ladder state directly: energized rails,
branch prefixes, contacts, comparisons, and output instructions are highlighted
from stable runtime element IDs, and the canvas shows lifecycle plus scan
number. Any edit immediately removes those highlights and reports that Verify
+ Load is required, preventing results from an older compiled program from
being drawn over changed logic. Undo restores monitoring only when the editor
document once again exactly matches the loaded program.
Use `--verify-ladder-editor` for the headless interaction regression check.

Catalog expansion is intentionally paused at 175 candidates while simulator
interface, authoring, diagnostics, and runtime contracts are hardened. The
850-family/3,000-variant target remains the long-term production goal, not the
current catalog count.

Desktop UI density and DPI behavior are documented in
[`docs/UI_SCALING.md`](docs/UI_SCALING.md). The engineering shell uses the
actual window viewport rather than stretching a fixed design canvas, so higher
resolutions provide more workspace instead of oversized controls.

### Robot cell restart reference

Scene `lab-3-02-robot-cell-safe-restart` includes an editable offline example:
`programs/examples/robot-cell-restart-reference.rpproj.json`. Open it with
**File -> Open Ladder Agent Project**, Run scans, close Gate, set Robot Ready,
press Reset to authorize the cell, then press the separate Start motion button.
Gate/ready loss or Stop clears authorization; recovery requires Reset and Start.
The default lab template remains an exercise. See
[`the scene guide`](docs/help/scenes/lab-3-02-robot-cell-safe-restart.md).

Use `--audit-robot-restart` after building for 35 focused offline checks of
the saved ladder reference, restart sequencing, gate mounting/swing and robot
sweep clearance. The installed CNC is static and the E-stop prop is a visual
reference only. These checks do not validate physical safety or live operation.

### Sequence light tower reference

Scene `lab-4-04-sequence-light-tower` includes the editable offline example
`programs/examples/sequence-light-tower-reference.rpproj.json`. Open it with
**File -> Open Ladder Agent Project**, Run scans and press Start for red.
Separate Step presses select amber, green, blue, then off with the completion
beacon. Stop clears all lamp commands; restarting requires a fresh Start.
The default template remains an exercise. See
[`the scene guide`](docs/help/scenes/lab-4-04-sequence-light-tower.md).

Use `--audit-sequence-tower` after building for 30 focused checks of the saved
reference, actual controller sequencing, independent lamp channels and tier
clearance. The CNC remains static and the sounder is uncommanded. These are
offline checks; no physical or live PLC acceptance is implied.

### Chain lift carton cycle reference

Scene `lab-4-09-chain-drive-lift` includes an editable offline carton cycle:
`programs/examples/chain-lift-installation-reference.rpproj.json`. Open it with
**File -> Open Ladder Agent Project**, Run scans, then press **Start carton
cycle (momentary)**. The carton moves from the chain infeed across the lower
bridge, rises on the lift belt, transfers across the upper bridge onto the
receiving conveyor and stops at its end stop. The empty lift returns home.
Feedback follows actual carton/carriage positions. Stop holds the position;
Run requires a fresh Start to resume. Global Reset restores the carton to the
infeed, the lift home and both belt/chain drive phases. The completed carton
stays on the receiver until Reset. See
[`the scene guide`](docs/help/scenes/lab-4-09-chain-drive-lift.md).

Use `--audit-chain-lift-installation` after building for 36 focused offline
checks of bearing contacts, selected clearance at 211 heights and the full
actual-controller cycle at 10 ms plant samples. It checks automatic feedback,
four-leg Stop/resume, invalid-command diagnostics, exact drive Reset and the
native review clock path. This fixed-geometry, single-carton model excludes
falling loads, slip, inertia and flexible-chain physics. Sampled bounds and
native snapshots do not establish mechanical or live PLC acceptance.

### Cookie packaging batch reference

Scene `lab-4-10-cookie-packaging` includes the editable offline project
`programs/examples/cookie-packaging-reference.rpproj.json`. Open it with
**File -> Open Ladder Agent Project**, return to Scene, Run scans, then press
**Start / resume cookie batch**. Expect six photoeye counts and six jaw cycles;
COOKIES and SEALED finish at 6, with all packages retained on the conveyor.
Stop holds trays and head. Run alone stays held; a fresh Start resumes. Reset
restores six unwrapped trays, zero counts, head home and stopped playback.
Default empty ladder remains an exercise. See
[`the scene guide`](docs/help/scenes/lab-4-10-cookie-packaging.md).

After building, `--audit-cookie-packaging` runs 24 focused checks with 1,252
actual-controller 20 ms samples of support, visible bounds, optical crossings,
counts, retained packages, Stop/resume, Reset and command diagnostics.
`--visual-scene-review --shell-scene=lab-4-10-cookie-packaging
--shell-view=operator` exposes camera views and offline Hold/Step 2.0 s
(100 actual scans). This finite model assumes mechanical indexing; heat, film
mechanics, slip and replenishment are excluded. Bounds and native snapshots
do not establish physical process or live PLC acceptance.

### Barrel fill batch reference

Scene `lab-4-11-barrel-fill-station` includes the editable offline project
`programs/examples/barrel-fill-reference.rpproj.json`. Open it with **File ->
Open Ladder Agent Project**, return to Scene, Run scans, then press **Start /
resume barrel batch**. The empty barrel indexes beneath the connected nozzle,
receives 150 L and parks on the outfeed. The meter reads 150.0 L and the source
retains 50 L. Stop retains position and inventory; Run alone holds until a
fresh Start. An interrupted discharge retains its ownership even when its own
barrel occupies the exit sensor. Completion stays held until Reset restores
an empty barrel and 200 L source. See
[`the scene guide`](docs/help/scenes/lab-4-11-barrel-fill-station.md).

After building, `--audit-barrel-fill` runs 29 focused checks with 1,344 actual
20 ms controller samples. These check liquid inventory/rendering, support,
selected geometry, pipe connections, optical feedback, Stop/resume, Reset,
invalid-command diagnostics and the native Hold/Step path. Launch with
`--visual-scene-review --shell-scene=lab-4-11-barrel-fill-station
--shell-view=operator` for camera views and 2 s steps of 100 actual scans.
This finite model assumes mechanical indexing and prescribed constant flow;
hydraulics, slosh, slip and replenishment are excluded. Bounds and native
snapshots do not establish physical process or live PLC acceptance.

### Measured cable cut reference

Scene `lab-4-12-cable-cut-length` includes the editable offline project
`programs/examples/cable-cut-reference.rpproj.json`. Open it through **File ->
Open Ladder Agent Project**, return to Scene, Run scans, then press **Start /
resume cable cut**. The encoder readout rises to 3.00 m; feed stops, the knife
cuts and returns home, and the piece stays on the anvil/receiving table.
Available stock finishes at 7 m. Run alone cannot start or resume the cut.
Stop preserves length and blade pose; a fresh Start resumes. Reset restores
10 m available stock, zero measurement, home knife and stopped scans.
The default empty ladder remains an exercise. See
[the scene guide](docs/help/scenes/lab-4-12-cable-cut-length.md).

After building, `--audit-cable-cut` runs 31 focused checks with 581 actual
20 ms controller samples. These check measured inventory, readout, selected
support/clearance, knife/reel/roller motion, Stop/resume, Reset and diagnostics.
Launch with `--visual-scene-review --shell-scene=lab-4-12-cable-cut-length
--shell-view=operator` for camera views and offline Hold/Step 0.5 s, executing
25 actual scans. This finite model assumes no-slip feed and a constant-radius
reel. Tension, sag, layering, elasticity and cutting force are excluded.
Sampled bounds and native snapshots do not establish physical process or
live PLC acceptance.
