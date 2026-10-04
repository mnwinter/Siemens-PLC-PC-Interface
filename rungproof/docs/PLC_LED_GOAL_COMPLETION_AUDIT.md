# PLC-led launch goal completion audit

Status: complete live PLC/TIA baseline retained; corrected executable awaits
focused hash-bound delta qualification.

| Goal requirement | Required evidence | Current evidence | Status |
|---|---|---|---|
| PLC-led pilot | Native package enables the guarded real-PLC path and does not substitute an offline controller | Enabled package manifest reports `realPlcWritesEnabled: true` and `operator-authorized-live-bench` | Proven locally |
| Real ladder execution | TIA program executes in the named physical PLC while RungProof supplies feedback and reads commands | Retained baseline records two cycles against the live S7-1500 and is hash-bound to its accepted executable | Proven for baseline; one current-executable cycle remains |
| Guarded simulated-I/O exchange | Exact ownership, address scope, explicit authorization, no automatic connection | Baseline records zero-write diagnostic and exact write scope; current package retains the same profile and four-write/six-read contract | Proven for baseline and locally for current; current scope reconfirmation remains |
| Verified TIA/CPU mapping | Exact TIA update, CPU order number/firmware, standard DB14 offsets, compile and watch table | Baseline records TIA V17 Update 9, `6ES7 512-1DK01-0AB0`, firmware V2.9, standard DB14, confirmed endpoint, and passing compile | Proven for the unchanged profile/target |
| Fail-safe communications | Matching heartbeat echo, enable/comm/timeout gating, safe commands on loss, fresh Run after recovery | Baseline records heartbeat/network loss and recovery as passing; corrected UI/runtime has deterministic state-transition tests | PLC safe behavior proven for baseline; corrected display/recovery delta remains |
| Packaged runtime proof | Integrity, enabled capability, native startup, zero unintended listeners/browsers/connections | 1,261-file integrity, enabled smoke, visible-window test, current preflight, and fail-closed delta-template proof | Proven locally |
| Clear user-only actions | Exact sequence and machine-readable acceptance record | Packaged checklist, current preflight, delta template, full validator, and lineage-preserving delta validator | Complete locally |

## Current candidate

- ZIP: `build\RungProof-VM-v0.2.0-pilot.2.zip`
- SHA-256: `215e67e0f9385452f6140d9ba2d80821cdebe536ea041d2dbeacbac5564735c3`
- EXE SHA-256: `138a41a2e81a7a902fbd7fc5220506dc567e575743d9cd49c5c67f501bda5fac`
- Full source: 28 Node tests and 114 Python tests passed; 18 expected
  PySide6-only skips under system Python.
- Package smoke: enabled live capability, exact four-address write scope,
  correct target/timing, and no PLC connection attempt.
- Offline bench preflight proof:
  `build\bench-preflight-local-proof\BENCH-PREFLIGHT.json`.

## Retained accepted baseline

`bench-evidence\0.2.0-pilot.1\bench-evidence` contains an internally consistent
preflight/result/acceptance chain for executable SHA-256
`641db3528d0a2cbfec35c7c721281fa1281daf6a4c288857da9a4e350437e894`.
It records the named VM, TIA/CPU/firmware, standard DB14, exact endpoint,
compile, read-only zero-write test, write scope, cycles, controls, heartbeat and
network loss, reconnect/fresh Run, Disconnect, Close, and Matt's PASS approval.

The result notes the stale healthy-telemetry UI defect. Therefore that
acceptance proves the PLC watchdog and baseline behavior but does not accept
the corrected executable. The retained files remain unchanged.

## Only remaining completion evidence

On the PLC-reachable VM, Matt must use the corrected package and unchanged
baseline directory to:

1. Run `BENCH-PREFLIGHT.ps1 -BaselineEvidenceDirectory <baseline>`.
2. Pass one normal cycle and reconfirm only the four declared write addresses.
3. Explicitly Disconnect while connected data is visible; confirm RungProof
   immediately shows unavailable heartbeat/status and PLC-owned commands, then
   confirm watchdog safe state in TIA.
4. Reconnect and confirm motion requires a fresh Run.
5. Interrupt the VM network; confirm unavailable telemetry, stopped RungProof
   plant commands, automatic reconnect, and no restart without a fresh Run.
   The accepted baseline remains the PLC-watchdog proof for this exact target;
   do not claim simultaneous TIA observation if the VM adapter loss also
   disconnects TIA.
6. Close while connected and confirm the PLC returns safe.
7. Fill `BENCH-DELTA-RESULT.json`, approve it, and run
   `VALIDATE-BENCH-DELTA.ps1 -BaselineEvidenceDirectory <baseline>`.
8. Return current preflight, delta result, delta acceptance, and focused
   RungProof/TIA screenshots.

Until that delta chain exists, the corrected candidate is not bench-accepted.

The supported operator controls and acceptance checks are Run, Stop, and
Reset. Step is not exposed and is not required. A legacy `stepPassed` field may
remain `null` in an already-generated result without blocking validation.
