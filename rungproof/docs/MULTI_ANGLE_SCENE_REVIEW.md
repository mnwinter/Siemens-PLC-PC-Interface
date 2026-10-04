# Multi-angle scene review - 2026-10-04

Status: **active**. The prior software review did not establish multi-angle
visual acceptance. Six scenes have five-view native static inspections; 71 remain pending.
Demo 5 and Powder Batch Mixer have repaired layouts. Parcel Size Sorter still
requires repair; three simple panels have clear spacing but incorrect START plates. Other scenes
remain pending unless their row explicitly records observation.

## Acceptance method

Use the native Windows Godot application and the opt-in `--visual-scene-review`
bar. Inspect front-right, front-left, rear-left, rear-right and overhead views.
Use close views where occlusion hides a support, workpiece or moving attachment.
Check workpiece support, post/beam clearance, equipment identity, floor contact
and relevant motion extremes. Run/Stop/Reset and permissive transitions require
separate behavior evidence. A camera log is evidence of navigation, not a
substitute for inspecting its screenshot. Do not silently pass obscured details.

The bounds inventory uses actual imported visible meshes after world transforms,
not catalog dimensions. Its column counts intersecting mesh AABBs between
separate equipment, with more than 5 mm overlap on each axis. Curved/rotated
meshes and intentional connections can create false positives. Zero candidates
also does not prove proper support, equipment identity, or moving clearance.
44 of 77 scenes have positive counts after the mixer and tank-sizing repairs.
Every row requires native inspection.

## Repairs and open findings

- Demo 5: pallet now centered between four posts on the base slab; carton rests
  inside the conveyor deck footprint; robot clears the shortened conveyor;
  coordinate-sensor foot clears the separate gripper model. The gantry tool now
  follows its Z axis through the XYZ sweep, Stop and Reset. All seven focused
  geometry checks pass. Native static five-view inspection is complete. Motion
  was observed from front-left and rear-right, including Stop/Reset. No real
  carton transfer or automatic home/pick feedback is implemented.
- Powder Batch Mixer: the intersecting tanks and motor/hopper interference are
  repaired. Tank diameter/height now size the actual cylindrical shell (2.6 m /
  2.5 m here), with equipment scale applied separately. A copied roller-shutter
  previously labeled as a powder chute is replaced by an original static open
  channel; its inherited door approval/reference is removed and the old review
  is archived. The builder checks that cross-support corners stay below the
  channel. Family registration rejects zero/tied matches and preserves existing
  authored packages. Native five-view reinspection covers spacing, floor contact
  and channel clearance, including close/overhead views where rear tanks occlude
  details. The scene remains a symbolic batch exercise, with manual feedback and
  PLC-driven indicators; no actual powder transfer, weighing, mixer process or
  supplied batch reference ladder is proven.
- Tank resizing exposed radar feedback that ignored parent scale. It now uses
  the world-space liquid surface, and Reset projects the restored tank feedback.
  The focused scaled-radar case passes; other tank scenes still need native review.
- Workstation Call, Dual Confirmation and Service Marker inspections find clear supports/spacing
  but generic START plates on call/confirmation buttons. This shared label issue
  remains open. Global help validation also fails at Count Display's inherited
  door-axis metadata (`KIN_bottom_bar`); do not regenerate help to legitimize that
  identity without checking its actual model.
- Whole-shell startup: the inventory reproduced REAL initial `0` arriving as a
  long in the editor. The catalog test previously decoded it as double instead
  of following the plant reader. The test now reproduces the actual boundary
  and failed before normalization in `SceneLadderProject`. All 142 tests pass
  after the fix, and the shell inventory completes for all 77 scenes.
- Parcel Size Sorter: the repaired build opens normally in Windows with
  `route_position` REAL = 0. Five-view static inspection finds overlapping
  turntables, belts through turntable supports, boxes penetrating the deck and
  overlapping each other, and the smallest box overhanging the infeed end.
  These require placement/transfer repair; successful startup is not acceptance.

## Evidence

Local ignored logs under `rungproof-next/.tools/`:
`scene-geometry-before.log`, `scene-static-clearance-before.log`,
`scene-geometry-final.log`, `multi-angle-native-review.log`,
`multi-angle-native-final.log`, `scene-real-initial-before.log`,
`scene-real-initial-after.log`, `all-scene-geometry-inventory.log`,
`multi-angle-native-parcel.log`, `geometry-review-shell-final.log`.
Build: zero warnings/errors. Controller: 142 pass / 0 fail. Existing plant:
19 checks pass. Twelve focused geometry checks pass (seven Demo 5, four mixer,
one scaled radar); all 71 authored scene cases pass, with six scenes having none.
Three family-selection regression cases pass. Current mixer evidence:
`mixer-build.log`, `powder-chute-build.log`, `mixer-import.log`,
`mixer-geometry-final.log`, `mixer-plant-regression.log`,
`mixer-scene-contracts.log`, `mixer-native-final.log`,
`all-scene-geometry-mixer-final.log`. Global help validation remains failed at
the unrelated Count Display metadata/document mismatch. These counts do not
approve the rest of the catalog. Restore tag:
`codex/multi-angle-review-baseline-20261004` at `2c3de4b`.

## Catalog coverage

FR/FL/RL/RR/T = front-right / front-left / rear-left / rear-right / top.
Pending means not inspected in this new pass. Previous single-view pictures,
initial-state cases, inherited asset reviews and catalog `mapped` status do not
count as this scene's multi-angle or runtime acceptance.

| # | Scene | Bounds candidates | Native static views | Current result |
| --- | --- | ---: | --- | --- |
| 1 | `conveyor-cell` | 14 | Pending | Pending |
| 2 | `equipment-gallery` | 5 | Pending | Pending |
| 3 | `lab-10-01-drive-alarm-code-string` | 56 | Pending | Pending |
| 4 | `lab-10-02-chicken-label-print` | 131 | Pending | Pending |
| 5 | `lab-10-03-vision-package-sorter` | 40 | Pending | Pending |
| 6 | `lab-10-04-motor-enum-state` | 0 | Pending | Pending |
| 7 | `lab-10-05-motor-struct-data` | 67 | Pending | Pending |
| 8 | `lab-10-06-ten-motor-array-startup` | 260 | Pending | Pending |
| 9 | `lab-11-06-wastewater-collection` | 222 | Pending | Pending |
| 10 | `lab-11-07-multi-conveyor-pallet-route` | 693 | Pending | Pending |
| 11 | `lab-11-11-service-elevator` | 63 | Pending | Pending |
| 12 | `lab-11-12-mobile-traffic-lights` | 21 | Pending | Pending |
| 13 | `lab-11-13-xy-palletizing` | 0 | FR/FL/RL/RR/T | Repaired; bounded static/motion checks pass |
| 14 | `lab-11-19-powder-batch-mixer` | 0 | FR/FL/RL/RR/T | Repaired static layout/chute; process behavior unverified |
| 15 | `lab-2-01-workstation-call` | 0 | FR/FL/RL/RR/T | Clear supports/spacing; generic START plate needs correction; runtime pending |
| 16 | `lab-2-02-dual-confirmation` | 0 | FR/FL/RL/RR/T | Clear three-component footprint/supports; generic START plates need correction; runtime pending |
| 17 | `lab-2-03-service-marker-inhibit` | 0 | FR/FL/RL/RR/T | Clear button/beacon footprint/supports; incorrect START plate; runtime pending |
| 18 | `lab-2-04-two-station-call` | 0 | Pending | Pending |
| 19 | `lab-2-05-bay-light-selector` | 0 | Pending | Pending |
| 20 | `lab-2-06-ready-attention` | 0 | Pending | Pending |
| 21 | `lab-2-07-dual-contact-permissive` | 0 | Pending | Pending |
| 22 | `lab-2-08-inspection-vote` | 0 | Pending | Pending |
| 23 | `lab-2-09-maintenance-beacon` | 0 | Pending | Pending |
| 24 | `lab-2-10-dust-collector-seal-in` | 0 | Pending | Pending |
| 25 | `lab-2-11-inbound-tote-stop` | 4 | Pending | Pending |
| 26 | `lab-2-12-assembly-lift` | 0 | Pending | Pending |
| 27 | `lab-2-13-coolant-jug-fill` | 39 | Pending | Pending |
| 28 | `lab-2-14-sump-pump` | 41 | Pending | Pending |
| 29 | `lab-2-15-fume-extractor` | 0 | Pending | Pending |
| 30 | `lab-2-16-safe-drill` | 24 | Pending | Pending |
| 31 | `lab-2-17-pallet-robot` | 24 | Pending | Pending |
| 32 | `lab-2-18-pallet-pickup` | 8 | Pending | Pending |
| 33 | `lab-2-19-service-door` | 54 | Pending | Pending |
| 34 | `lab-2-20-bottle-shuttle` | 0 | Pending | Pending |
| 35 | `lab-2-21-tote-finishing` | 88 | Pending | Pending |
| 36 | `lab-2-22-dual-spindle` | 2 | Pending | Pending |
| 37 | `lab-2-23-parcel-sorter` | 198 | FR/FL/RL/RR/T | FAIL: table/belt and carton interference; startup fixed |
| 38 | `lab-2-24-robot-cnc` | 6 | Pending | Pending |
| 39 | `lab-2-25-inspection-toggle` | 0 | Pending | Pending |
| 40 | `lab-3-01-guarded-pallet-transfer` | 24 | Pending | Pending |
| 41 | `lab-3-02-robot-cell-safe-restart` | 42 | Pending | Pending |
| 42 | `lab-4-01-press-count-lamp` | 0 | Pending | Pending |
| 43 | `lab-4-02-counter-reset-lamp` | 0 | Pending | Pending |
| 44 | `lab-4-03-repeat-cycle-counter` | 0 | Pending | Pending |
| 45 | `lab-4-04-sequence-light-tower` | 0 | Pending | Pending |
| 46 | `lab-4-05-dual-input-count-window` | 0 | Pending | Pending |
| 47 | `lab-4-06-multi-press-confirmation` | 0 | Pending | Pending |
| 48 | `lab-4-07-parking-garage-entry` | 20 | Pending | Pending |
| 49 | `lab-4-08-package-grouping` | 24 | Pending | Pending |
| 50 | `lab-4-09-chain-drive-lift` | 54 | Pending | Pending |
| 51 | `lab-4-10-cookie-packaging` | 170 | Pending | Pending |
| 52 | `lab-4-11-barrel-fill-station` | 151 | Pending | Pending |
| 53 | `lab-4-12-cable-cut-length` | 21 | Pending | Pending |
| 54 | `lab-5-01-delayed-lamp` | 0 | Pending | Pending |
| 55 | `lab-5-02-timed-lamp-off` | 0 | Pending | Pending |
| 56 | `lab-5-03-rotary-flasher` | 0 | Pending | Pending |
| 57 | `lab-5-04-alternating-lamps` | 0 | Pending | Pending |
| 58 | `lab-5-05-variable-flash-rate` | 0 | Pending | Pending |
| 59 | `lab-5-06-running-light-tower` | 0 | Pending | Pending |
| 60 | `lab-5-07-pedestrian-crossing` | 26 | Pending | Pending |
| 61 | `lab-5-08-drawbridge-control` | 43 | Pending | Pending |
| 62 | `lab-5-09-bag-indexing-conveyor` | 41 | Pending | Pending |
| 63 | `lab-5-10-coating-line` | 84 | Pending | Pending |
| 64 | `lab-6-07-luggage-weight-sort` | 108 | Pending | Pending |
| 65 | `lab-6-08-hand-dryer` | 634 | Pending | Pending |
| 66 | `lab-9-01-sum-function` | 0 | Pending | Pending |
| 67 | `lab-9-02-product-function` | 0 | Pending | Pending |
| 68 | `lab-9-03-sum-and-counter-function` | 0 | Pending | Pending |
| 69 | `lab-9-04-function-selector` | 0 | Pending | Pending |
| 70 | `lab-9-10-box-volume` | 46 | Pending | Pending |
| 71 | `lab-9-11-pallet-counting` | 68 | Pending | Pending |
| 72 | `lab-9-12-ev-charging-manager` | 95 | Pending | Pending |
| 73 | `scene-1-conveyor-stop` | 8 | Pending | Pending |
| 74 | `scene-2-conveyor-pusher` | 29 | Pending | Pending |
| 75 | `tank-high-low` | 60 | Pending | Pending |
| 76 | `tank-level` | 52 | Pending | Pending |
| 77 | `tank-radar` | 80 | Pending | Pending |
