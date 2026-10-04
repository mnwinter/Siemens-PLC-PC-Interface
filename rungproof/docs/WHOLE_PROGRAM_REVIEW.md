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
| A missing bridge reply freezes UI/physics indefinitely | Async serialized JSON exchange with deadline/cancellation, continuous bounded stderr drain, and process teardown on a bad reply. Poll completions on the Godot main thread. | 13 process/client/contract tests include hung reads, stderr flooding, malformed/EOF replies, cancellation, fresh-process recovery, and stale session rejection. No PLC transport. |
| Mismatched profile can still Connect; approval survives a selection change | Enforce declared scene/profile and typed PC/PLC mapping; clear approval on scene/profile/source changes. Revalidate before Connect and bind backend connection to the verified descriptor from the same configuration load. | App-shell guard regression; two new fake Python regressions reject changed IP/slot/cadence before transport creation. |
| Partial or wrongly typed external image changes some scene points | Require the complete configured PLC point scope and validate all ownership/types/ranges before committing any point. | Pure contract tests and rendered scene-control regression require typed and atomic rejection. |
| Every physics frame issues PLC I/O and can queue stale work | Use profile cycleMs as the minimum request interval and allow only one pending exchange. Discard late results after source/scene changes. | Source review and single-pending/session cancellation tests. This is frame-limited scheduling, not a measured real-time 20 ms guarantee. |
| External health placeholders conceal actual readback | Display the guarded result's cycle health, heartbeat reason/echo/age and required readiness status. Reject malformed health metadata. Keep unavailable labels while disconnected. | Fake healthy/fault/status-type regressions; native disconnected health inspected. No live readiness proof. |
| Read-only test competes with an active session | Require a disconnected session before opening the separate diagnostic transport. | Guarded UI source review. |
| Settings buttons fall below the native window | Bound the autowrapped explanation width before initial layout and keep profile details at a scrollable fixed height. | Native 1200x675 settings and profile mismatch inspected; rendered bounds verifier passes. |

## Review matrix

| Area | Current evidence | Remaining work |
| --- | --- | --- |
| Launch/import/toolchain | Pinned Godot/.NET start; native window opened; build clean | Fresh install/export and missing-dependency recovery |
| All scene data | All 77 catalog entries load; 71 have declared cases and pass; six have none. Rerun logs in `.tools/plant-scene-review` | Visual controls and runtime coverage; many declared cases cover only initial state |
| Authored demos | All five compile; 142 controller tests pass. Native demos 1-4 exercised; Demo 5 four-pick completion, mixed instructions, FB/FC/DB views, gantry command motion, Stop and Reset inspected | Broader scene runtime coverage; Demo 5 remains a manual-feedback command visualization |
| Operator controls | Native Run/Stop, normal conveyor Start/E-stop/Reset, action inputs and history; complete runtime/health rails now scroll at 1200x675 and 1600x900 | E-stop/reset across other applicable scenes |
| Conveyor/pusher/tank plant execution | Pusher repeated transfers, stroke/sensor feedback, Stop and Reset; tank fill, analog/full-level feedback, Stop and Reset inspected natively through File/Open. Fill/drain regression passes; model matches eight Python traces / 83 snapshots | Other scene runtime coverage; native tank drain |
| Ladder editor | Native drag insertion/Undo, block browsing, Save/Open, invalid drafts, retained execution, multi-scene close guards and watch Remove/Clear/Undo in both views verified; rendered interaction verifier passed | Native tag editing, interface editing, help; crash recovery |
| Scene/workspace authoring | Rendered mappings, transforms, atomic Save and replacement guards; native asset placement/selection, Undo/Redo, close Cancel, scene-change Save and workspace Open verified | Native mappings/transforms and malformed files |
| Layout/camera | Split regressions and native resize/points/browser/scrollable rails inspected; block summary bounded and hovered selection contrast repaired | Remaining native tag/edit flows; broader scene visual acceptance |
| External execution boundary | 16 offline bridge/contract/playback tests; 16 fake Python tests; fake full-app exchange/playback regression and native Run/Stop/Reset; profile guards, exclusive source, atomic output | Broader profile/cadence integration, reconnect, configuration editing and mapping UI; authorized live commissioning |
| Python canonical interface / legacy tools | 129 root tests and 16 fake live/diagnostic tests passed | Continue source review for legacy conflicts |
| Shutdown/resource lifecycle | Orphan Studio block selector repaired; diagnostic/rendered tests exit without resource leak reports; native launch/close completes; 13 offline connection lifecycle tests pass | Repeat resource behavior during longer native authoring sessions |

## Specific open issues

- Unsaved ladder drafts/history survive scene changes; New/Open and close
  now guard unsaved work. Crash/power-loss recovery remains unimplemented.
- Non-demo labs open as blank exercises with matching typed scene tags. One
  catalog I/O type is unsupported by the offline controller and is reported.
  Complete lab instruction/reference-program coverage remains under review.
- External playback/readiness now follows the existing native/reference
  binding; offline full-app and native controls verified. Broader profiles and
  reconnect remain under review. No live communication has been verified.
- Demo 5 currently commands output indicators; complete palletizing motion and
  reusable FB interface/instance behavior require further verification.
- Workspace placements/groups/links now compare with a saved baseline and are
  protected on scene changes, Load, cross-scene ladder Open and close. Failed or
  cancelled Save prevents replacement. Crash/power-loss recovery remains open.

## Checkpoint results

- .NET build: zero warnings and errors.
- Controller unit/behavior suite: 139 passed, zero failed, no transport created.
- Canonical Python interface: 129 passed. Fake live/diagnostic suites: 16 passed.
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

## External bridge checkpoint - 2026-10-04

Restore tag `codex/external-review-baseline-20261003` at `22e2dbb` precedes
these changes. Build is clean, controller tests pass 139/139, connection tests
pass 13/13, canonical Python tests pass 129/129, and fake live/diagnostic tests
pass 16/16. App-shell/profile guard, rendered scene-control/atomic image, and
rendered settings bounds regressions pass. Native inspection proves local
profile validation, mismatch display and usable controls at 1200x675; Connect
and the read-only hardware test were not invoked. Runtime scheduling uses a
minimum profile interval with one outstanding request; real cadence/readiness
remain unverified. Shutdown rendering/resource leaks remain open.

Run the new offline suites from `rungproof-next/`:

```powershell
.\.tools\dotnet\dotnet.exe run --project tests/Connections/RungProof.Next.Connections.Tests.csproj -- ..\build\.venv-rungproof\Scripts\python.exe
# Set DOTNET_ROOT and PATH as documented before launching Godot.
.\.tools\godot\Godot_v4.7.2-stable_mono_win64\Godot_v4.7.2-stable_mono_win64_console.exe --path . --resolution 1200x675 -- --verify-external-dialog --shell-scene=scene-1-conveyor-stop
```

Next work remains unsaved project/scene transitions, all demo native workflows,
external playback/reference semantics, and the rest of the review matrix.

## Scenario draft checkpoint - 2026-10-04

Restore tag `codex/project-persistence-baseline-20261004` at `49c5019`
preserves the external bridge checkpoint. Native Windows use reproduced loss
of an unsaved network and Undo history after Demo 3 -> Demo 1 -> Demo 3.
Scene loading reinstalled the authored template on every attachment. Each
scene now retains its exact in-memory draft, saved baseline/path, and separate
Undo/Redo history; selecting the current scene also preserves its project.
Cached drafts never have user bindings overwritten by template alignment.
This retains work during scenario navigation; it is not crash recovery or
automatic disk persistence. Explicit Save remains necessary before closing.

The app-shell regression failed before the fix and passes afterward, including
invalid draft contents, dirty state/path, isolation, Undo, Redo across another
round trip, and same-scene selection. Build has zero warnings/errors and the
rendered editor interaction regression passes. Native Windows inspection
confirms the third network, dirty marker, and Undo/Redo after the round trip.
The unrelated conveyor template assigned to non-demo labs and their Run path
remain under review, as do shutdown resource leaks and the rest of the matrix.

## Native demo / valid-event checkpoint - 2026-10-04

Restore tag `codex/lab-execution-baseline-20261004` at `a7d455d` precedes
these changes. Demo 4 counted invalid detections without type-valid or
count-request, so enabling permissives later could validate an old count.
The counter now sees a raw pallet-detection rising edge qualified by both
permissives. Regression failed before the fix (expected 0, actual 5) and now
passes for each missing-permissive combination, held detection, five valid
events, and loss of type-valid. Controller suite passes 139/139, build has
zero warnings/errors, and app-shell/draft regressions pass.

Native Windows checks cover Demo 1's lamp off through two rising edges and on
at three, Stop output removal and Reset; Demo 2's initial delay, subsequent
lamp activation and removal on request loss; Demo 3's package motion after
Start and stop at photoeye position 0.5; and corrected Demo 4's ignored invalid
event, output off through four valid events/on at five, and removal when the
type permissive drops. These are bounded user workflow checks, not complete
scene visual or hardware acceptance. Demo 4's shutter partly obscures its
equipment; broader visual and block-structure review remains open.

## Lab authoring / bounded drawers checkpoint - 2026-10-04

Restore tag `codex/lab-project-baseline-20261004` at `6ee9328` precedes
these changes. Non-demo scenes incorrectly opened the conveyor ladder and
could run hidden scene rules instead of the user's selected controller.
They now open blank exercise projects with PC-owned inputs and PLC-owned
outputs mapped to their actual BOOL/INT/DINT/REAL points. Unsupported types
are reported rather than coerced. The conveyor starter and five authored
demos retain their programs. Empty exercise Run and Verify + Load report
EDIT001; scene feedback alone cannot fabricate a PLC output without logic.

The exercise factory regression checks all 77 scenes, including owner/type
binding consistency and one reported unsupported type. Controller suite is
140/140; build has zero warnings/errors. App-shell/draft and rendered editor
interaction regressions pass. Native Lab 2.1 testing covers empty Run feedback,
adding a network/contact with the correct lamp coil, Run/scan monitoring,
input true/lamp on, input false/lamp off, Stop, and Save through the file
dialog. Saved JSON contains the matching scene ID, tags, contact, and coil;
the native tab title reflects its filename and clears the dirty marker.

Native use also exposed project/footer and diagnostics overlap under points.
Tag/block forms and inspector pages now scroll within their docks; the palette
compacts by height. A strengthened fresh-editor regression first failed with
all drawers open and now passes at 1200x675 and 1600x900 in both vendor views.
Native 1600x900 inspection confirms usable footer, diagnostics, and routine.
This checkpoint does not complete the review matrix or prove physical PLC I/O.

## Draft validation / loaded controller checkpoint - 2026-10-04

Restore tag `codex/validation-state-baseline-20261004` at `1e5b22b`
precedes this fix. Native loading of a readable draft with an undeclared
contact retained the good runtime in Main but erased its shell program and
snapshot, falsely displaying Stopped/program not running. Validation now
retains the loaded program/snapshot, reports draft errors in the editor's
Error List, and suppresses monitoring of the mismatched edited ladder.
Toolbar/footer execution and scans continue to reflect the loaded controller.
Programmatic control refresh no longer emits a spurious user-edit warning.

The rendered persistence regression now starts with a valid running program
and requires its identity, running snapshot/scan, cycle status, cleared stale
monitoring, and draft errors after invalid Open. It passes alongside the
complete rendered editor interaction and app-shell/draft regressions; build
is clean. Native Windows testing confirms cross-scene Open from Demo 1 to the
saved Lab 2.1 project, Run, invalid draft Open, retained advancing scans,
and correct lamp response from the previous good program. Unsaved replacement
and exit prompts, resource cleanup, and remaining review areas stay open.

## Unsaved replacement / close checkpoint - 2026-10-04

Restore tag `codex/unsaved-work-baseline-20261004` at `433454f` precedes
this fix. New/Open require Save, Discard, or Cancel for the current dirty
ladder; close checks the current and all cached scene drafts. Cancel is the
default focus. Save prompts for each queued project and blocks the pending
action until every write succeeds. Saving cached drafts never attaches their
scene or controller. Cancelling a later Save keeps earlier saves and leaves
the remaining drafts protected. Writes complete in a temporary file before
replacing an existing project, avoiding truncation during a failed write.

Build is clean. App-shell regression verifies all-scene detection, Cancel,
failed Save preventing continuation, waiting for all saves, matching saved
contents/source IDs, and Discard. Rendered editor regression verifies the
New guard's Cancel and Discard branches. Native Windows checks cover close
Cancel, two-scene detection, sequential Save dialogs, and cancelling the
second Save; the next close lists only the remaining cached draft. Saving
that final draft produced the correct scene JSON and the review process exited.
Crash recovery is outside this repair and remains absent.

## Shutdown ownership checkpoint - 2026-10-04

Restore tag `codex/shutdown-review-baseline-20261004` at `aaf2f8d`
precedes this fix. After pending scene frees settled, orphan diagnostics
identified an unparented Studio `BlockTypeSelector` and its popup subtree.
It retained the viewport, canvas, themes, fonts, and textures reported at exit.
The hidden Studio selector is now owned by its workbench, as in TIA. Before
the fix the diagnostic run listed 14 stray nodes and shutdown leaks; afterward
it lists none and exits without RID/ObjectDB leak reports. Rendered editor and
1200x675 split regressions also pass and exit without those reports. Normal
batch-file startup and native window close were inspected; the process exits.

Build has zero warnings/errors; controller suite passes 140/140 and offline
connection/process suite 13/13. Save-failure feedback hides its file dialog
before showing the error guard, preventing competing exclusive windows.
Unsaved-dialog text is bounded and abbreviates long scene lists, with Cancel
focused by default. Longer native authoring and the rest of the matrix remain
under review. No physical PLC connection was attempted.

For settled orphan diagnostics, append `--trace-orphans` to `--verify-app-shell`.
Inspect its output for `Stray Node`, `leaked`, or `RID allocations`.

## External playback checkpoint - 2026-10-04

Restore tag `codex/external-playback-baseline-20261004` at `4157d6b`
precedes this fix. The full-app offline bridge reproduced movement immediately
after Connect, before Run. Main advanced plant physics on every connected frame,
the equipment controllers independently animated, and the PLC readiness bits
were not used to gate the returned output image. Run/Stop/Reset had incorrectly
been treated as PLC commands rather than plant playback controls.

Readiness now matches `prototype/src/livePlcBinding.js` and the legacy native
runtime: healthy exchange, simulation enabled, communication OK, and no PLC
timeout. Connect, Stop, Reset, readiness loss, and disconnect leave playback
paused; recovery never resumes automatically. Connected exchange continues
while paused. Reset restores the plant without replacing its last PLC command
image. Unready output images are not applied. Equipment physics is frozen with
the plant; no PLC RUN/STOP/reset command or output write was introduced.
Momentary PC feedback remains set until an accepted exchange samples it, then
clears independently of plant playback. Scene changes also cancel pending
connections so a late connect cannot attach to another scene.

The offline full-app regression passes connection without motion, Run motion,
Stop holding package/equipment while cycles continue, paused Reset, readiness
loss and output rejection, blocked Run, recovery requiring new Run, disconnect,
and sampled pulse handling. The connection suite passes 16/16, including all
eight PLC status-bit combinations, unhealthy/incomplete readback and new-session
behavior. Controller suite remains 140/140; build has zero warnings/errors.
Rendered scene-control and app-shell/orphan regressions pass without leaks.
The headless scene-control ray-pick check requires a rendered viewport and was
rerun there successfully; headless popup placement is not layout evidence.

Native Windows mouse tests exercised the offline connected scene's Run, Stop,
and Reset. Screenshots showed motion, frozen playback, advancing exchange
counts and retained PLC output. External source/playing/paused/readiness/cycle
labels now report actual state; the footer no longer says LOCAL ONLY during
external mode. REAL values use six significant figures for display without
changing the runtime values. Final native error log is empty and the process
exits on close. No physical PLC adapter or network was used by the fixture.

Run `--verify-external-playback` for the offline regression. Add
`--keep-playback-review-open` to inspect its fake connected scene with native
controls; this flag only applies to that verifier and never selects real PLC
transport. Logs are under `rungproof-next/.tools/external-playback-*` and
`native-external-playback-*`.

## Continuous plant execution checkpoint - 2026-10-04

Restore tag `codex/scene-motion-baseline-20261004` at `3bff1d9` precedes
this fix. The full-app execution test reproduced Scene 2's package/photoeye,
pusher stroke/limits, and transfer count remaining unchanged under actual
ladder scans. The `conveyorPusher` runtime had no update implementation. Tank
outputs likewise failed to move the level because a separate local Run flag
was never set by the selected ladder controller.

The conveyor/photoeye/pusher plant now follows the existing canonical Python
components and native reload policy. Physics produces PC-owned feedback from
the commanded motion; it never writes PLC-owned commands or executes hidden
PLC logic. Transfer requires a package at the photoeye crossing the declared
stroke threshold. Reload waits for the delay and retracted limit. Photoeye
sweep/hold handles crossing between steps, discharge counts once, and the
package is hidden after discharge. Selected-controller execution now gates
plant/equipment playback; Stop holds the plant, and Reset restores its model.
Tank motion uses the selected playback state instead of the unused local flag.

`--verify-plant-motion` passes actual ladder scan feedback, repeated pusher
transfers, a Stop during partial stroke, Reset, the tank's declared 7 percent/s
fill and 4.5 percent/s drain, 4-20 mA feedback, high/low limits, saturation,
Stop and Reset. The pure model matches eight independent canonical Python
traces (83 snapshots), including swept photoeye, hold decay, partial stroke,
off-station extension, and counted discharge. The stored trace records its
source SHA-256; tests reject a stale source. Invalid elapsed time is rejected.
Run the suite with `dotnet run --project tests/Plant/RungProof.Next.Plant.Tests.csproj`.

Build is clean; 140 controller tests, numeric I/O, rendered scene controls,
app-shell/orphan checks, and external playback regression pass. All 77 scenes
were rerun: 71 have passing declared cases, and these six have no cases:
conveyor-cell, equipment-gallery, scene-1-conveyor-stop,
scene-2-conveyor-pusher, tank-high-low, tank-radar. Loading them is not motion
acceptance. The new motion checks cover previously untested execution paths.

Native Windows inspection of the new pusher/tank visuals and normal file
loading is pending: a Windows update overlay currently blocks native input.
The normal launcher was opened, but the tool cannot target the system overlay.
No visual acceptance is claimed for this checkpoint. Review fixtures are
generated under `.tools/plant-review-scene2.rpproj.json` and
`.tools/plant-review-tank.rpproj.json` for subsequent native File/Open testing.
The review goal remains active and no PLC connection was attempted.

## Workspace write checkpoint - 2026-10-04

Restore tag `codex/workspace-review-baseline-20261004` at `84714d7`
precedes this fix. Workspace saves previously wrote over the destination
directly. They now finish a temporary file in the destination directory and
replace the saved workspace only after that write completes, for both absolute
and Godot user paths. The rendered workspace regression passes its existing
group, hierarchy, mapping, transform, Undo/Redo and Save/Load assertions.
A Windows exclusive-reader failure check also passes: the original saved JSON
survives failed replacement, the temporary file is removed, and retry succeeds.
Build is clean; log: `.tools/workspace-atomic-final.log`.

Remaining work: preserve/protect unsaved workspace changes at scene replacement,
workspace Load and close, and compare Undo state against the saved document.
Keep cross-scene ladder Open synchronous until attachment is complete; inserting
an asynchronous guard only in Main's SceneRequested callback would restore the
ladder into the old scene before attachment and reintroduce the earlier bug.
Native inspection remains pending behind the Windows update overlay.

## Workspace baseline checkpoint - 2026-10-04

Restore tag `codex/workspace-drafts-baseline-20261004` at `d4394c9`
precedes this fix. The rendered workspace regression reproduced UNSAVED
remaining set after Undo returned to the empty baseline. Dirty-state updates
now compare the current workspace document against its baseline from scene
attachment, successful Save or successful Load. Undo/Redo therefore report the
actual state; a failed Save never advances the baseline. This also avoids
marking a workspace dirty for scene controls whose values are not stored in
workspace files.

Build and the complete rendered workspace regression pass, including edits,
Undo to the original baseline, Redo, Save of a nonempty workspace, another
edit, Undo to that saved baseline, and Redo. The atomic replacement test still
passes. Logs: `.tools/workspace-dirty-before.log` and
`.tools/workspace-dirty-final.log`. Native manual inspection remains pending.
Next repair: scene replacement, workspace Load and close must consume this
accurate dirty state without breaking cross-scene ladder attachment ordering.

## Workspace replacement checkpoint - 2026-10-04

Restore tag `codex/workspace-guards-baseline-20261004` at `ca9af4b`
precedes this fix. Unsaved workspace edits now require Save, Discard, or Cancel
before scene replacement, workspace Open/Load, cross-scene ladder Open, and
window close. Save cancellation/failure retains the current document and blocks
continuation; successful Save resumes the pending operation. Discard authorizes
only that operation without falsely marking the current workspace saved. Close
then checks current/cached ladder drafts. Cross-scene ladder Open queues the
whole open and preserves attach-before-restore ordering. Scenario selection
tracks the actual active scene when replacement is queued or loaded from a file.

Build, rendered workspace replacement/dirty/atomic-write regression, and rendered
ladder editor regression pass. The injected denied replacement intentionally
logs WORKSPACE_SAVE_FAILED; it verifies preservation and successful retry.
Logs: `.tools/workspace-guards-final.log`, `.tools/workspace-guards-ladder.log`.
Native Windows launch and File/Open loaded the pusher and tank review projects.
Pusher package advance, extended cylinder/transfer, repeated cycles, Stop hold,
and Reset were inspected; tank fill, 42-percent/10.72-mA reset state, full-level
20-mA feedback, indicators and Stop hold were inspected. This is offline visual
simulation evidence, not live-machine or physical geometry acceptance.

Native asset search/selection/placement, Undo/Redo header state, close Cancel,
scene-change Save, and saved workspace File/Open round trip were also inspected.
The bounded guard dialog defaults to Cancel. The own review file is
`.tools/native-workspace-guard-20261004.rungproof.json`; it contains one sensor
placement in tank-level. The Windows overlay has cleared. Remaining visual
issues found here: the operator rail clips runtime/navigation on the tank, and
Undo to an empty workspace leaves a stale gizmo/selection inspector. Next fixes
will address those observed issues. Whole-program review goal remains active.

## Operator rail and Undo selection checkpoint - 2026-10-04

Restore tag `codex/operator-review-baseline-20261004` at `dc8f54d`
precedes these fixes. The operator and PLC-health rails now scroll their whole
content; runtime, equipment and health text fit their content, while the bounded
event history keeps its own scrolling. This prevents long descriptions/action
lists from reducing runtime and health text to a few clipped pixels. Native
1600x900 and 1200x675 inspection confirmed runtime details and both navigation
buttons can be reached; the narrow window also exposes the complete PLC-health
summary by scrolling. The Engineering button was exercised from the scrolled
operator rail.

Undo to an empty workspace now detaches its transform gizmo and replaces stale
placement inspector text with the current scene summary. The prior failure was
reproduced in `.tools/workspace-selection-before.log`; the corrected rendered
workspace test and native place/Undo workflow both confirm it. Scenario list
selection also tracks the actual loaded scene after file Open or guarded changes.

Build, workspace replacement/dirty/write/transform tests, app-shell/orphan and
split-view tests pass. Controller suite remains 140/140; the full-app controller
UI verifier passes its stable actions, stop/reset, monitor and force assertions.
Native sessions closed normally with no ERROR or leak reports. Logs include
`.tools/operator-workspace-final.log`, `.tools/operator-shell-final.log`,
`.tools/operator-split-final.log`, `.tools/operator-native-final.log`, and
`.tools/operator-native-narrow-final.log`. Whole-program review remains active;
remaining editor interactions, demo presentation/sequence boundaries, external
profiles, installation/export and legacy-path conflicts still need review.

## Editor browsing and contrast checkpoint - 2026-10-04

Restore tag `codex/editor-review-baseline-20261004` at `aca9e3f` precedes
these fixes. Selecting another block previously marked the project unsaved and
caused an unnecessary close prompt. Dirty comparison now excludes navigation
while saved files still retain the selected block. Real network edits and
cached drafts still require Save/Discard/Cancel. The controller suite passes
141/141, including every Demo 5 block, saved navigation and actual edits.

Native drag insertion at an FB wire and Undo were exercised. FB, FC and DB
pages were inspected; selecting/hovering rows now keeps readable text and
backgrounds. The shared selection styles cover project, instruction, interface,
tag, watch, validation and search browsers. The interface summary stays bounded
and scrollable, and explicitly identifies declarations/shared project tags.
Offline parameter passing and per-instance FB storage remain unimplemented;
the UI must not imply those declarations execute as real Siemens interfaces.

Build (zero warnings/errors), rendered ladder interaction and split/layout
checks pass. Logs: `.tools/editor-review-controller.log`,
`.tools/editor-review-rendered.log`, `.tools/editor-review-split.log`, and
`.tools/editor-review-native.log`. Native clean block browsing closes without a
false save prompt. Whole-program review remains active.

## Authored demo sequence and first Run checkpoint - 2026-10-04

Restore tag `codex/demo-sequence-review-baseline-20261004` at `5cc5dff`
precedes these fixes. Native testing found that setting scene inputs before the
first Run lost them when loading the controller reset the plant. Initial Run
now preserves current feedback; explicit Reset and explicit program loading
retain their reset behavior. Native inputs-before-Run and the rendered plant
regression both confirm the correction.

Demo 4's advertised block program previously had only its main block and an
unused timer. Its existing qualified counter and immediate completion output
now execute in a counter FB and validation FC, called each scan. Existing
invalid-event and threshold behavior still passes.

Demo 5 now demonstrates comparisons, a meaningful parallel actuator-status
branch and two populated DB declaration views in addition to its two FBs,
two FCs, timer, counter and arithmetic. Its completed four-pick layer removes
pick commands and cannot accept a fifth pick until Reset. Held carton feedback
counts once; completed-layer arithmetic increments once. Native four-carton
input sequence showed layer_complete=True and both commands=False; native
FB comparison monitoring and DB declarations were inspected. The watch dock
can be resized; its per-scan row recreation needs further review.

The XYZ gantry now follows gantry_cycle while playback runs, holds on Stop or
loss of command, and resets its authored pose. The three delivered sibling KIN
nodes move together; Z travel stays within the solid-rod/carriage overlap.
The shutter-shaped coordinate-sensor substitute in this scene was replaced
by a sensor pair and overlapping equipment was spaced to expose the gantry.
The scene/help now state the actual manual-feedback/command-visualization
boundary: this is not a closed-loop carton placement model or real FB/DB
instance execution. Other generic accessory substitutions remain under review.

Build is clean; controller suite passes 142/142; app-shell, cached-draft/unsaved
guards, profile guards and settled orphan checks pass; plant regression passes
19 checks. Native first Run, gantry motion, Stop hold, Reset pose, four-pick
completion, watch resizing and comparison/DB views were inspected. Logs:
`.tools/demo-sequence-controller-final.log`, `.tools/demo-sequence-shell-final.log`,
`.tools/demo-sequence-plant-final.log`, and
`.tools/demo-sequence-native-acceptance.log`. Goal remains active.

## Watch stability and saved metadata checkpoint - 2026-10-04

Restore tag `codex/watch-review-baseline-20261004` at `bd99654` precedes
these fixes. Every scan recreated watch rows and symbol-menu items, losing
selection and disrupting Remove or an open picker. Controls now retain identity
until symbols or membership change; scans update values in place. The rendered
regression failed before the change and now passes selection/value checks.

Watch edits also left the unsaved marker and toolbar Undo stale. Both editor
views now refresh saved-metadata state without invalidating the executing
controller. The regression verifies Clear/Undo, both titles and retained
monitoring. Native Windows Remove and Clear updated the marker and enabled
Undo; toolbar Undo in TIA and Studio 5000 restored the clean baseline while
scans continued. Earlier native testing also retained an open picker across
scans and added a symbol successfully. Native sessions closed cleanly.

Build has zero warnings/errors; rendered ladder interaction passes. Logs:
`.tools/watch-stability-before.log`, `.tools/watch-stability-final.log`,
`.tools/watch-native-final.log`, `.tools/watch-controls-native-final.log`.
Whole-program review remains active.

## Verification boundary

Native mouse/keyboard interaction proves only the inspected Windows workflows.
Headless declared scene cases prove only the stated cases, not full user
acceptance. Fake adapters and offline programs never prove live PLC behavior.
Live commissioning remains subject to the repository's approved CPU/profile,
exact write scope, network authorization, and direct machine observation.
