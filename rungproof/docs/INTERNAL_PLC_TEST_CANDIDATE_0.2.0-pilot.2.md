# RungProof 0.2.0-pilot.2 internal PLC test candidate

Status: ready for Matt's live PLC bench test; **not bench-accepted and not
approved for external delivery**.

## Candidate

- ZIP: `build\RungProof-VM-v0.2.0-pilot.2.zip`
- SHA-256: `215e67e0f9385452f6140d9ba2d80821cdebe536ea041d2dbeacbac5564735c3`
- EXE SHA-256: `138a41a2e81a7a902fbd7fc5220506dc567e575743d9cd49c5c67f501bda5fac`
- Capability: `realPlcWritesEnabled: true`
- Mode: `operator-authorized-live-bench`
- Target profile: S7-1500 at `10.70.9.201`, rack `0`, slot `1`, 20 ms
- Write scope: `DB14.DBX0.0`, `DB14.DBX0.1`, `DB14.DBX0.2`, `DB14.DBD2`

## Proven without connecting to a PLC

- Full source lane passed 28 Node and 114 Python tests, with 18 expected
  PySide6-only skips under system Python.
- Locked PySide6 native tests passed 20 of 20.
- Enabled-package self-test passed and reported no PLC connection attempt.
- Package integrity passed for 1,261 files.
- Visible-window test passed with one process, zero listening ports, zero new
  browser processes, and a clean close.
- The packaged `LIVE_PLC_PILOT_CHECKLIST.md` records the exact DB contract,
  expected ladder behavior, normal-cycle proof, and failure-recovery tests.
- Packaged `BENCH-PREFLIGHT.ps1` passed without a PLC connection, verified the
  enabled capability and exact ten-tag Scene 2 profile, and generated a
  machine-readable preflight plus result template.
- `VALIDATE-BENCH-RESULT.ps1` is regression-tested to reject incomplete results
  and mismatched preflight hashes and to produce acceptance only for a complete
  explicitly passing result.
- `VALIDATE-BENCH-DELTA.ps1` validates the complete baseline hash chain,
  requires the `pilot.1` baseline / `pilot.2` current version pair and the same
  profile/target, rejects an unchanged executable, and accepts the correction
  only after all affected current-binary checks pass.
- `DELTA-RETEST-QUICKSTART.txt` gives the exact VM/TIA sequence and distinguishes
  independently observable PLC watchdog proof from VM-adapter-loss behavior.
- The supported playback controls are Run, Stop, and Reset. Step is not a
  product or bench-acceptance option. New result templates omit it, and the
  validator ignores the unused legacy `stepPassed` field in older templates.
- Disconnect-state telemetry now fails truthful: as soon as the session leaves
  Connected, cached heartbeat/status and PLC-owned command samples are marked
  unavailable and the point tables repaint even without a new PLC cycle. This
  correction is locally regression-tested but still requires one focused live
  Disconnect/TIA recheck before `disconnectSafe` can pass.

These checks prove packaging and guarded capability only. They do not prove
reachability, TIA DB layout, watchdog ladder behavior, scan timing, or the
machine sequence against the actual PLC.

## Required live completion

The retained baseline proves the named TIA V17 Update 9, CPU order number,
firmware, DB14 layout, guarded write scope, normal cycles, watchdog, network
loss, reconnect, and Close behavior for executable SHA-256 `641db352...e894`.
Its notes correctly identify the stale disconnect-telemetry display as a
launch blocker, so it cannot accept the corrected executable by itself.

Run this candidate's `BENCH-PREFLIGHT.ps1` with the retained baseline evidence
directory, fill the generated `BENCH-DELTA-RESULT.json`, and run
`VALIDATE-BENCH-DELTA.ps1`. The focused current-binary checks and commands are
in `LIVE_PLC_PILOT_CHECKLIST.md`. Return the current preflight, delta result,
delta acceptance, and relevant RungProof/TIA screenshots.
