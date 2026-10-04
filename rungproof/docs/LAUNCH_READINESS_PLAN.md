# RungProof launch-readiness plan

Status: proposed execution baseline, 2026-08-05

## Goal

Make RungProof ready for Matt's PLC-led engineering pilot: write ladder in TIA,
execute it in the live bench PLC, use RungProof as the simulated plant and I/O
exchange, and prove the ladder by observing commanded motion, feedback,
sequence transitions, watchdog behavior, and fault recovery.

The internal pilot is successful when the PLC-enabled Scene 2 candidate runs
repeatable live cycles on the named PLC/VM configuration and retains the
reviewed PLC ownership and fail-closed communication boundaries. Offline
controller development and a multi-user or paid launch are later work.

## Recommended first-launch contract

Ship the smallest supportable product before expanding the catalog.

| Area | Pilot support | Not part of the pilot promise |
|---|---|---|
| Product | Native Windows RungProof application | Browser player as a product surface |
| Scene | Scene 2 - Conveyor Pusher | S03-S06 or the 32 source scenes as playable native scenes |
| Offline mode | Setup, disconnected visual review, and bounded read-only PLC diagnostic | Siemens CPU emulation, ladder execution, or native offline controller |
| PLC mode | Core pilot workflow: named TIA V17/S7-1500/DB14 live bench | Generic Siemens compatibility or production I/O |
| Editor | Source-only prototype | Supported authoring workflow |
| Safety | Training and bench simulation with no physical field I/O | Safety function, machine commissioning, or digital-twin claims |
| Delivery | Signed, versioned Windows x64 release candidate with hashes | Automatic update service or unattended deployment |

The internal test candidate is intentionally built with **Connect Real PLC**
enabled so the bench gate can be performed. External delivery remains blocked
until that exact configuration has passed and its evidence is retained.

## Critical path and required order

### 1. Freeze the launch contract

Why first: scope changes invalidate documentation, acceptance tests, packaging,
and commercial work performed later.

- Name the launch `Instructor/controls-lab pilot`, not a general public release.
- Declare supported Windows editions, x64 requirement, target VM platform,
  minimum display resolution, and administrator/install requirements.
- For the PLC-enabled build, record exact TIA Portal version, CPU order number,
  firmware, rack/slot, network assumptions, DB14 layout, optimized-access state,
  and the fact that the bench has no connected production I/O.
- Freeze Scene 2, Views A/B/C, Run/Stop/Reset behavior, read-only check,
  and the guarded connection workflow as the supported surface.
- Keep S03-S06, the scene editor, generic scene loading, TIA generation, and
  production-machine use visibly out of scope.

Exit gate: one approved support matrix and one product-truth statement are used
by the UI, README, sales copy, setup guide, and test plan.

### 2. Reconcile product truth, versioning, and repository state

Why second: at the planning baseline, the repository contained contradictory
current and legacy claims, and the build defaulted to `0.1.0` although
`v0.1.18` was the latest accepted package artifact.

- Create one version source consumed by the UI, package folder, ZIP name,
  build metadata, and release notes; remove the builder's hard-coded stale
  default.
- Rewrite the README around the native application. Move browser-player steps
  to an explicitly archived prototype document.
- Correct the roadmap: a baseline commit now exists, the native package can
  write only the authorized PC-owned DB14 points, and only Scene 2 is native.
- Add `CHANGELOG.md`, known limitations, support matrix, and a release checklist.
- Configure a private remote/backup, protect the release branch, and define the
  release tag and rollback process. A local commit alone is not a recoverable
  release repository.
- Use `0.2.0-pilot.2` for the disconnect-telemetry correction. Preserve
  `0.2.0-pilot.1` as the accepted-but-superseded baseline; never publish two
  different executable hashes under the same version.

Exit gate: a clean checkout produces an artifact whose UI, folder, ZIP,
manifest, documentation, and Git tag report the same version and scope.

### 3. Close the offline product and visual gates

Why before PLC commissioning: deterministic product behavior and the supported
renderer must be stable before adding bench/network variables.

- Obtain explicit approval for the Scene 2 assets it actually uses: conveyor,
  carton, through-beam photoeye, operator controls/indication, and pusher.
  Other asset approvals do not block the one-scene pilot.
- Reproduce the supported target-VM output at 1920x1080. Capture Views A/B/C,
  minimum/default/maximum orbit, package motion, photoeye transition, pusher
  extend/retract, window resizing, and clean close.
- Resolve the remaining conveyor/photoeye depth or alignment defect if it is
  visible in those exact captures. Geometry tests alone are not visual proof.
- Verify first launch, repeat launch, extraction to a normal user path,
  read-only operation, no new browser process, no listener, no automatic PLC
  connection, no residual process, and useful errors for missing/corrupt files.
- Run `fast`, `full`, and `release -EnableRealPlc` from a clean checkout and
  retain logs,
  screenshots, artifact SHA-256, dependency versions, and test counts.

Exit gate: explicit visual approval plus a reproducible, clean target-VM release
record. The current 2026-08-05 `fast` lane passes, but it is not this gate.

### 4. Close the exact PLC/TIA bench gate

Why here: this is required only because the current UI exposes a real PLC write
path. Offline/package proof cannot establish PLC compatibility.

- Author the DB14 interface and reference ladder artifacts in TIA Portal V17;
  do not generate or guess Siemens export syntax from RungProof.
- Import the exported tags/blocks into the named CPU project and record any
  namespace, optimized-access, version, or compile warnings.
- Verify the read-only check first and prove zero writes.
- In TIA watch tables and RungProof, record Test, two full cycles, Stop,
  fresh Run, Reset, heartbeat echo, enable/communication/timeout bits, explicit
  Disconnect, application Close, cable/network loss, reconnect, and the fresh-
  Run requirement after recovery.
- Prove the writer touches only the four declared PC-owned DB14 points and that
  the PLC watchdog, not the PC application, is the final safe-state authority.
- Package the exact engineer-authored TIA exports separately from `.plcscene`
  content, with version/CPU compatibility and import instructions.

Exit gate: completed bench acceptance record for the named configuration. The
internal test candidate may expose Connect Real PLC to perform this work; an
externally delivered candidate may not claim support until the gate passes.

### 5. Complete distribution, security, and legal gates

Why before external delivery: a passing executable is not yet a distributable
commercial product.

- Perform a release-focused security review of the native code, profile/file
  parsing, update/install path, secret handling, and dependency inventory.
- Produce an SBOM and vulnerability report from the locked dependencies; define
  how critical dependency fixes trigger a new build.
- Complete Qt/PySide LGPL review, ship the applicable full license texts and
  required source/relinking offer, and confirm whether a commercial Qt license
  is needed. Retain the existing third-party notices.
- Complete RungProof trademark, company-name, and domain clearance before paid
  branding or public promotion.
- Confirm ownership/IP and employer moonlighting boundaries for all source,
  graphics, documents, and Siemens interface code.
- Add the product license/EULA, training-and-bench safety disclaimer, privacy
  statement (including an explicit no-telemetry statement if applicable),
  support policy, and vulnerability-reporting contact.
- Select a maintainable Windows packaging method, sign the executable and
  installer with Authenticode, test SmartScreen/UAC behavior, and verify clean
  install, upgrade, uninstall, and rollback on a fresh VM.

Exit gate: legal/compliance sign-off, signed artifacts, clean install/rollback,
and no unresolved high-severity security finding.

### 6. Finish onboarding and support readiness

- Provide a five-minute quick start, instructor setup guide, learner exercise,
  exact PLC bench setup, troubleshooting decision tree, known limitations, and
  artifact/hash verification instructions.
- Add an in-app About/Diagnostics export containing version, renderer, OS,
  profile identity, readiness state, and sanitized logs; never export PLC
  credentials or unrelated machine data.
- Define the supported contact, response expectations, issue template, severity
  levels, reproduction data, and release/rollback ownership.
- Run a fresh-user documentation test: a person who did not build RungProof
  must install it and complete Scene 2 without verbal rescue.

Exit gate: the fresh-user test passes and support can diagnose the expected
failure modes from the packaged information.

### 7. Run the controlled pilot

- Recruit 5-10 representative learners/instructors or controls engineers.
- Use scripted tasks and record completion, setup time, defects, confusion,
  unsafe interpretations, and support effort.
- Treat crashes, data/profile corruption, unintended connection/write,
  misleading safety claims, inability to install, or failure of the core Scene
  2 workflow as release blockers.
- Fix blockers, rerun every affected release gate, freeze the release candidate,
  tag it, archive hashes/evidence, and retain the prior rollback package.

Exit gate: all pilot-blocking findings are closed, no critical safety ambiguity
remains, and the product owner approves the release candidate in writing.

### 8. Decide on paid/public launch

Do not automatically turn the pilot build into a paid public release. Review
pilot demand, support load, installation friction, lesson completion, defect
rate, and the value of additional native scenes. Then choose one next product
slice: instructor content/export, additional approved scenes, or broader PLC
compatibility. Do not combine all three in one release.

## Current evidence and blockers

| Item | Current evidence | Launch status |
|---|---|---|
| Source checks | 2026-08-05 `fast`/`full` lanes: 28 Node tests and 114 Python tests, 18 expected system-Python Qt skips; scene/tag, live-capability release wiring, and delta-evidence contracts pass; no PLC attempt | Pass on working tree; `release -EnableRealPlc` from a clean release commit remains required |
| Packaged artifact | Local corrected `RungProof-VM-v0.2.0-pilot.2.zip`; integrity, enabled self-test, 20 locked Qt tests, visible-window lifecycle, zero listener/browser, and hash-bound delta preflight pass | Engineering candidate; current ZIP hash is recorded in the candidate audit |
| Native scope | One supported Scene 2 vertical slice; S03-S06 are review-only and fail closed | Acceptable if stated honestly |
| Visual acceptance | Scene 2 assets and S03-S06 remain pending; exact target-VM 1920x1080 acceptance is outstanding | Blocker |
| Live PLC | Pilot.1 has retained full acceptance on the named PLC but is superseded by its stale-telemetry defect; pilot.2 preserves the profile and fixes the display | Focused pilot.1-to-pilot.2 live delta remains |
| TIA artifacts | Actual V17 Update 9 project compiled and ran on CPU `6ES7 512-1DK01-0AB0` firmware V2.9; reusable export bundle is absent | Mapping proven for Matt's bench; export bundle deferred beyond the sole-tester pilot |
| Version truth | Root, UI, package, ZIP, SBOM, and package metadata use `0.2.0-pilot.2`; pilot.1 remains immutable baseline evidence | Pass for corrected candidate |
| Repository recovery | Local baseline commit exists; no Git remote or release tag is configured | Blocker |
| Distribution | Versioned portable ZIP has internal/package SHA-256 and evidence collector; no signed installer, upgrade/uninstall, or fresh-VM rollback record | Blocker for external pilot |
| Security | Partitioned manual review completed and validated findings fixed; exact lock audit and dated `pip-audit` report show no known vulnerabilities; formal scan is blocked by its Windows path-normalization defect | Manual/package evidence passes; formal scan remains incomplete |
| Compliance | Third-party notices exist; Qt commercial-distribution review and product legal documents are incomplete | Blocker |
| Brand | Working identity and assets exist; formal clearance is not complete | Blocker before paid/public promotion |
| Pilot evidence | Matt's complete pilot.1 live acceptance is retained; pilot.2 delta tooling and quickstart are packaged | Focused live delta is the next internal gate; multi-user evidence is deferred |

## Definition of launch-ready

RungProof is ready for the controlled pilot only when every applicable exit gate
above has objective evidence, all release-blocking findings are closed, the
release is reproducible from a clean tagged commit, the prior build is
recoverable, and the product owner has approved the exact visual output and
support/safety language. Offline proof, packaged smoke proof, TIA import proof,
and physical PLC commissioning proof must remain separately labeled.
