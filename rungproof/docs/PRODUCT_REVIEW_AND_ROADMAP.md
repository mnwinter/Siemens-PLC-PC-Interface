# RungProof product review and roadmap

## Product definition

RungProof is a PLC-led visual-simulation product under controlled engineering
pilot preparation. The native candidate does not execute ladder or emulate a
PLC. TIA is used to create the ladder, the live bench PLC executes it, and
RungProof provides Scene 2 plant behavior, simulated feedback, visualization,
and the guarded DB14 exchange. Offline reference control is deferred.

Primary keywords:

- PLC
- visual
- simulator
- ladder logic
- test

## Users and jobs

| User | Job |
|---|---|
| New controls technician | Learn I/O ownership, seal-in, permissive, timer, counter, sequence, and alarm behavior without risking a machine |
| Experienced PLC engineer | Explain and test expected plant response against a small deterministic contract |
| Instructor | Assign versioned scenes with configuration, progressive hints, solution, and acceptance criteria |
| Integrator | Run a read-only PLC profile diagnostic before a separately authorized live integration |

## Current product surface

- Native Windows application with Views A, B, and C.
- One supported native vertical slice: Scene 2 - Conveyor Pusher.
- Explicit disconnected operation, simulated-controller demonstration,
  read-only Siemens S7 diagnostics, and a guarded exact DB14 live session.
- Run, Stop, Reset, watchdog/readiness, reconnect, and clean-close
  semantics in the native runtime.
- S03-S06 native compositions are review-only and fail closed.
- The 32 scene contracts, 25 labs, browser player, reusable equipment catalog,
  and Scene Editor remain source/prototype regression surfaces.
- SHA-256 package manifest and reproducible one-folder VM ZIP build.

## Product truth

RungProof proves offline scene behavior against the declared point contract. It
does not yet:

- execute ladder logic;
- emulate a Siemens CPU or TIA Portal;
- support arbitrary live PLC scenes or DB layouts;
- model safety functions;
- provide physics-grade collision or process fidelity;
- prove that a real machine is safe.

Those boundaries must remain visible in UI, sales copy, and training material.

The authorized native Scene 2 session **does write** four declared PC-owned
DB14 feedback/heartbeat points after explicit operator confirmation. It reads
the declared PLC-owned command/status points. This narrow capability must not
be described as generic PLC compatibility, read-only operation, or proof of
physical machine safety.

## Release tiers

### Tier 0 — Internal engineering build

Achieved as an engineering baseline. Unsigned Windows executable, deterministic source tests,
packaged smoke test, fixed scene contract, dependency notices, and working
brand system.

Exit evidence:

- full and release checks pass;
- 1920×1080 VM visual review passes;
- no unintended network/PLC connection occurs;
- the initial Git baseline is intentionally established.

### Tier 1 — Instructor pilot

Current target. The dependency-ordered gates are in
`docs/LAUNCH_READINESS_PLAN.md` and `docs/RELEASE_CHECKLIST.md`.

- learner progress and result export;
- lab assignment packs;
- scene/version compatibility reporting;
- accessibility and keyboard review;
- signed installer/update policy;
- 5–10 observed training sessions.

### Tier 2 — Paid training product

- formal naming/trademark/domain clearance;
- code signing and installer;
- support and privacy terms;
- crash/update telemetry by explicit opt-in;
- content authoring workflow and compatibility policy;
- paid pilot evidence.

### Tier 3 — Broader guarded live integration

Scene 2 already has a focused renderer-neutral native runtime and guarded DB14
session. Broader scene/PLC support begins only after the pilot proves that
vertical slice and each new scene independently completes:

- explicit symbolic point-binding adapter;
- independently reviewed PC/PLC ownership map;
- safe scene-change handshake;
- watchdog and timeout proof;
- commissioning mode separate from training;
- live validation on exact PLC/firmware/TIA configuration.

## Immediate next decisions

1. Keep the Scene Editor, browser player, S03-S06, and the remaining source
   catalog outside the supported pilot surface.
2. Run the release candidate on the exact target VM at 1920×1080 and record
   screenshots, load timing, supported orbit output, and clean close behavior.
3. Build the internal candidate with `-EnableRealPlc`, then complete the named
   TIA V17/CPU/firmware DB14 import and live bench acceptance.
4. Configure a recoverable Git remote and approve the release tag/rollback
   process; the local baseline alone is insufficient.
5. Complete signing, installer, security, Qt distribution, legal/support, and
   formal RungProof name-clearance gates before external delivery.
