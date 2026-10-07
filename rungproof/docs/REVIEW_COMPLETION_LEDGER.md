# Whole-program completion ledger

## 2026-10-07 elevator evidence refresh

Later checkpoints supersede the historical door-travel gap below: modeled door travel/closure gating, partial Stop and opening reversal are implemented and observed. Call-station leaf collision repaired c7ac0fa with101 sampled leaf poses and fresh five-angle home inspection. Native repaired roundtrip recorded ed8c345; adjacent native scans350/351 now directly show upper feedback selecting exclusive return. Hoist/access installation and continuous motion clearance remain open. Historical counts and unresolved feature lists below are checkpoint evidence, not current acceptance.

## 2026-10-07 queue triage update

At source0f94a16, the eleven literal FAIL/open rows were reviewed against their full recorded results. Five contain missing implementation (typed STRUCT/ARRAY interfaces, wastewater process, elevator hoist/access/door travel, traffic timing/vehicle feedback); six contain verification gaps (sorter/robot between-sample clearance, sump visual/process limits, shipping last-active scan/intermediate poses, two tank operator/threshold checks). Generator58ddf72 now distinguishes IMPLEMENT_RECORDED_GAP from VERIFY_RECORDED_GAP and sends unknown FAIL records to TRIAGE_RECORDED_FAILURE. Original result text and failure flags remain; no row changed to PASS.

This triage covers only those eleven records. Other OPEN rows, including tote label/inspection and EV charging/connector/readout, still need reconciliation. Counts do not close them or establish current-build acceptance. Recent radar cycle/nonzero withdrawal evidence is recorded in the matrix and whole-program log. Next inspect the actual motor data model or elevator door mechanism before choosing an implementation repair. Full visual and product/editor requirements remain active.

Audit checkpoint: 2026-10-07, source `8b34a57`. This ledger separates the requested visual review from broader product requirements in the supplied migration handoff. It does not certify release readiness or live PLC operation.

## Evidence inspected at this checkpoint

- Canonical remote is `https://github.com/mnwinter/Siemens-PLC-PC-Interface.git`; branch is `agent/add-config-foundation`. Work is under `rungproof/rungproof-next`; unrelated generated/import files are retained.
- `MULTI_ANGLE_SCENE_REVIEW.md` and its generated `SCENE_NATIVE_REVIEW_QUEUE.json` contain 77 unique scene rows and five recorded home-view directions for every row. The queue reports 11 explicit FAIL/open records and no known changed home layouts awaiting inspection. Its scope explicitly permits historical views; the counts are not current-build functional acceptance.
- Current Demo 5 build: zero warnings/errors. `.tools/demo5-current-completion-audit.log` terminates with failures=0, 60 successful checks, 2576 actual 20 ms controller-driven cycle samples, and zero static candidates.
- Demo 5 plant/composer/runtime/audit files have no diff between the earlier native four-carton source `0de1262` and this checkpoint. Native full-cycle records cover four pickup, transfer, release and home-return cycles, capacity rejection and Reset. Fresh native window204426 adds an unheld normal cycle and retained landing viewed FR/FL/RL/RR/Top. Occluded views are supplemented by opposing views; no every-frame collision certification is inferred.
- The sorter matrix records four supported receiving lanes and native post-repair handoffs, retained endpoints, Stop and Reset. Sampled triangle screens cover all four routes. The reported missing receiving surface and disappearing load have documented repairs; continuous between-sample clearance remains unverified.
- Current tote records include active fill and cap engagement/release in two native directions, retained discharge and Reset. Five camera world-transform regressions pass. `Main.ToteFinishingGeometryReview.cs` explicitly states that label/inspection/native review remains pending; its passing result is not full finishing-line acceptance.
- `SimulatorShell.cs` contains instruction drag/drop handling and split-divider handling. Source presence alone does not prove all requested editor interactions or window sizes.

## Requirement ledger

| Requirement | Current evidence and disposition |
| --- | --- |
| Repair Demo 5 pallet/support intersection | Repaired; native home/retained-load views and current support/post checks agree. |
| Demo 5 static and full-cycle multi-angle inspection | Recorded four-cycle native phase inspection plus current unheld refresh. Sampled motion only; continuous solids unverified. |
| Review every catalog scene from multiple directions | All 77 have five recorded directions. Historical/source freshness and functional coverage must be evaluated per scene, not inferred from count. |
| Repair discovered placement/intersection issues | Repairs and post-change observations are documented per matrix row. Known FAIL/open rows also contain absent features and process verification limits, rather than eleven confirmed collisions. |
| Receiving surface and carton retention | Four sorter receivers/handoffs implemented and observed; native stopped endpoints retain cartons. |
| Separate completed visuals from unverified runtime | Matrix and queue maintain separate caveats; the remaining runtime inventory below remains open. |
| Preserve canonical repository and unrelated work | Current branch/remote verified; no reset/clean/discard performed. |
| Preserve external control and separate execution sources | Repository guidance defines the guarded live transport separately from the Godot shell. Existing offline/fake-adapter reports are bounded evidence; current live transport acceptance is unverified. |
| PLC selector and complete external settings | Earlier review documents cover these workflows. A fresh requirement-by-requirement native comparison against the supplied profile/IP/rack-slot/timing/timeout/permissions/handshake/watchdog/mapping list is still required for current product acceptance. |
| Every demo loads scene/program/interface; complex Demo 5 | Current Demo 5 audit checks saved document/menu equality and controller-driven cycle. This does not independently refresh the other four demos or prove every mixed instruction's visible editor behavior. |
| TIA editor layout, symbols, drag/drop, insertion cues | Implementations and earlier native checks exist. Current complete interaction/layout acceptance across the requested drawers, split view and resizing is not established by the recent scene runs. |
| E-stop, Reset, scan/running status and green power flow | Earlier controller/native evidence exists; recent Demo 5/tote tests cover their stated Stop/Reset/status behavior. A scene Stop is not an independently verified E-stop or complete highlighting acceptance. |
| Browser groups/numeric demo order/title/toolbar | Earlier shell evidence exists; native scene title/status visibly agree in recent runs. Current full browser/order/toolbar acceptance remains a separate workflow check. |
| Committed handoff/background documentation | Review matrix, whole-program review, AI handoff and this ledger are tracked. Historical handoff sections must be read with the newer review checkpoints. |

## Remaining runtime and verification inventory

The explicit FAIL/open rows retain: typed motor STRUCT data; typed ten-motor ARRAY interface; wastewater fluid/analog process; elevator hoist/access/door travel; traffic reference synchronization/vehicle feedback; sump mechanical float actuation; sampled versus continuous sorter/robot clearance; exact pallet-pickup timer transitions; and tank uninterrupted threshold-cycle/operator acceptance. Tote label application/inspection and several other scene-specific gaps are recorded as OPEN without the literal FAIL marker, so the eleven-row count is not the total unresolved-product count.

Next acceptance work should refresh the browser and all five demo loading workflows in the native app, then the editor layout/interaction requirements. Missing process features need explicit implementation and corresponding native verification; do not close them by changing labels to PASS. Live PLC verification requires the repository's exact configured CPU/profile, authorized network/write scope and direct machine observation, which this offline review has not supplied.

The overall goal remains active. This ledger is an evidence audit, not a completion declaration.
