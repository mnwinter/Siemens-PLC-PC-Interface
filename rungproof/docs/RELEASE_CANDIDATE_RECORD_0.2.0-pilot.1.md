# RungProof 0.2.0-pilot.1 candidate record

Status: local engineering candidate; **not approved for external delivery**.

## Proven locally on 2026-08-05

- Full source lane: 28 Node tests and 103 Python tests passed; 17 locked-Qt
  tests were expectedly skipped under system Python. All training-scene and tag
  contracts passed. No PLC connection was attempted.
- Locked package environment: 19 of 19 native Qt lifecycle/geometry tests
  passed.
- Clean isolated build installed exactly 17 hash-locked distributions and
  verified the vendored Siemens-interface source manifest.
- Package integrity verification passed for 1,256 files.
- Packaged self-test reported version `0.2.0-pilot.1`, software renderer,
  `realPlcWritesEnabled: false`, no browser engine/server, and no PLC attempt.
- Visible-window test passed three consecutive runs, observing one process, the
  exact RungProof title, zero TCP listeners, zero new browser processes, and
  clean exit after WM_CLOSE.
- The packaged capture command created 1920x1080 Views A/B/C plus an environment
  report with no PLC attempt. Local inspection found and corrected the bright
  scrollbar-track defect; final static captures have consistent dark tracks
  and coherent conveyor/rail/payload depth.
- `pip-audit 2.10.1` found no known vulnerabilities in the exact dependency
  lock on 2026-08-05. This is a point-in-time advisory lookup, not a guarantee.
- Candidate ZIP SHA-256:
  `c433b0a83a95bcd0cd0f405cd6768370c45eb7ab5980dae462d5c55fed990097`.

Generated evidence is under
`build/release-evidence/v0.2.0-pilot.1/`. It records Git revision
`9968dc3e3ec2d024068f82889943632a6b5ce5fc` and correctly reports that the
working tree was dirty because these launch-readiness changes were not yet
reviewed and committed.

## Not proven by this record

- Product-owner visual acceptance or exact 1920x1080 target-VM behavior.
- TIA import/compile or physical PLC bench behavior.
- Authenticode signature, installer/upgrade/uninstall, SmartScreen, or rollback.
- Clean tagged Git rebuild and independent remote recovery.
- Formal Codex Security completion; see `SECURITY_REVIEW_2026-08-05.md`.
- Qt/legal/IP/name/privacy/EULA approval or a completed user pilot.

This recorded candidate is deliberately unable to start the persistent
real-PLC writer. It is retained as the read-only baseline. The next internal
candidate must be built with `-EnableRealPlc` so Matt can perform the live bench
gate; it must not be described as bench-accepted until those results are added.
