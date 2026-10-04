# RungProof Outstanding Tasks

This is the implementation task list for the foundation, independent scenes,
and cumulative labs. Completed items remain in the project acceptance records.

## Completed in this implementation

- [x] Common PLC/watchdog bench setup documentation.
- [x] Complete S03-S06 machine guides and exact point contracts.
- [x] Add cumulative lineage and tag-delta metadata to Labs 2.1-2.25.
- [x] Validate retained, added, and changed lab tags.
- [x] Add watchdog, stale-feedback, wrong-type, and missing-command failure tests.
- [x] Replace plain setup text with document-style Setup dialogs and exact tag tables.
- [x] Add starter ladder networks to Basic Logic for the native scenes.

## Required follow-up

- [x] Verify the Scene 2 profile, DB14 offsets, endpoint, TIA V17 Update 9,
      CPU order number, and firmware on the isolated live bench. A reusable
      TIA export bundle remains deferred; no export syntax is guessed.
- [ ] Preserve prior lab acceptance cases when native cumulative PLC projects
      are supplied.
- [ ] Review photoeye beam alignment and conveyor rail/roller depth ordering.
- [x] Rebuild and smoke-test the internal `v0.1.18` engineering package after
      the contract changes.
- [ ] Rebuild `0.2.0-pilot.2` from its final clean release commit and retain the
      source, package, visual, and applicable live-bench evidence defined in
      `docs/RELEASE_CHECKLIST.md`.
- [x] Build, live-test, and retain acceptance for the PLC-enabled
      `0.2.0-pilot.1` baseline; its stale disconnect telemetry is documented.
- [x] Build and offline-verify the corrected PLC-enabled `0.2.0-pilot.2`
      candidate without initiating a PLC connection.
- [ ] Complete the focused pilot.1-to-pilot.2 delta checklist on the reachable
      VM/PLC bench and retain `BENCH-DELTA-ACCEPTANCE.json`.

## Boundary

The repository contains scene contracts and runtime tests, not a TIA project or
ladder-block archive. Actual cumulative PLC blocks remain on the bench PLC until
they are exported and reviewed. No production I/O is authorized by this list.
