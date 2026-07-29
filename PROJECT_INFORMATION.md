# Project information

## Objective

Build a maintainable PC interface that exchanges simulated sensor and actuator
data with Siemens PLCs through a dedicated data block. The interface should
eventually support configurable tag mappings and a scene/runtime layer similar
in purpose to Factory I/O.

## Proven baseline

On 2026-07-24, the standalone client completed a bidirectional round-trip test
from a Windows Server 2019 VM to the real CPU 1512SP-1 PN at `10.70.9.201`.

Confirmed evidence:

- TCP port 102 was reachable.
- The S7 session connected with rack/slot `0/1`.
- Controller information identified a CPU 1512SP-1 PN.
- `PC_To_PLC = true` echoed as `PLC_To_PC = true`.
- `PC_Heartbeat = 24072401` echoed as
  `PLC_Heartbeat_Echo = 24072401`.
- The false state and heartbeat `24072402` also echoed correctly.
- Original PC-owned values `false` and `12345` were restored and verified.
- Final diagnostic result was `ROUND_TRIP_PROOF: PASS`.
- No physical I/O address was written.

The first test held values for only 100 ms, which was faster than the TIA
watch-table display refresh. A five-second hold made both states visible in
TIA without changing the communications result.

## Current design decisions

- Use a dedicated standard/non-optimized simulation DB.
- Separate PC-owned commands from PLC-owned feedback.
- Keep the PLC program responsible for mapping simulation data into machine
  logic.
- Never treat a TCP connection alone as proof of usable S7 read/write access.
- Require an explicit write authorization flag in diagnostic tools.
- Keep the IP address and future tag mappings configurable.
- Do not commit generated executables or VM-specific Python runtimes.

## Current DB contract

The validated DB14 contract is documented in `docs/DB14_INTERFACE.md`.
The complete processor, network, DB, PLC logic, PC, and verification procedure
is documented in `docs/USER_SETUP.md`.

The contract now also includes:

- `DB14.DBX10.0` `Simulation_Enable` (operator/PLC-owned);
- `DB14.DBX10.1` `Simulation_Comm_OK` (PLC-owned);
- `DB14.DBX10.2` `Simulation_Timeout` (PLC-owned).

The PC reads but never writes these three fields.

## Configuration milestone

The first configuration layer now replaces hard-coded proof settings with a
validated JSON file containing:

- connection settings;
- symbolic tag names;
- absolute PLC addresses and data types;
- direction and ownership;
- update rate;
- safe default value;
- heartbeat timeout behavior.

The validator rejects physical I/O addresses, data-type/address mismatches,
duplicate or overlapping DB memory, wrong tag ownership, invalid safe values,
and inconsistent heartbeat references. Validation is offline and cannot
connect to the PLC.

The heartbeat counter and progress timeout are implemented as an I/O-free
state machine with unit tests.

## Typed point model milestone

The scene-facing point layer is implemented and proven offline:

- schema version 1 remains the proven raw-tag format, while version 2 adds
  typed points explicitly;
- digital points require a `BOOL` backing tag and support explicit inversion;
- analog points support validated raw and engineering ranges, units,
  reverse-acting scales, and deterministic integer rounding;
- `clamp` produces a bounded value with a clamp diagnostic;
- `fault` produces no writable raw value and reports a range fault;
- point ownership is inherited from the backing tag instead of duplicated;
- PC-owned analog ranges must contain the backing tag's raw safe value;
- internal heartbeat tags cannot be exposed as scene points;
- one raw tag can back only one point;
- contiguous DB byte groups are computed by ownership for a future block
  transport;
- mixed-owner bytes are flagged so a future grouped write cannot silently
  overwrite an opposite-owner bit.

`examples/typed-points.json` is an offline DB100 architecture example. Its
addresses and PLC behavior have not been downloaded or hardware-tested. The
proven DB14 contract and current single-tag Snap7 transport are unchanged.

## Watchdog proof

On 2026-07-24, `Simulation_Watchdog [FB3]` and
`Simulation_Watchdog_DB [DB5]` were compiled and downloaded to the real
CPU 1512SP-1 PN. The FB uses a `T#2s` progress timeout.

Live tests confirmed:

- a heartbeat change from `0` to `1` was echoed;
- a stopped heartbeat produced `Simulation_Comm_OK = false` and
  `Simulation_Timeout = true`;
- with `PC_To_PLC = true` during timeout, the gated `PLC_To_PC` remained
  false.

That 2026-07-24 test proved PLC-side timeout and safe gating but did not yet
prove the new continuous PC runtime.

## Continuous runtime proof

On 2026-07-29, the packaged guarded runtime was run from the Windows Server
2019 VM against the real CPU 1512SP-1 PN. Across two commissioning runs, the
screenshots confirmed:

- the configured target was `10.70.9.201`, rack/slot `0/1`;
- the reported write scope was limited to `DB14.DBX0.0` and `DB14.DBD2`;
- the runtime established an S7 session;
- the heartbeat echo progressed continuously and `HEARTBEAT_PROOF: PASS`;
- while `Simulation_Enable = true`, the PLC reported
  `Simulation_Comm_OK = true`, `Simulation_Timeout = false`, and
  `PLC_To_PC = true`;
- the enabled run remained healthy through cycle 50 and reported
  `HEARTBEAT_PROOF: PASS` and `SAFE_STATE_WRITE: PASS`;
- after the operator returned `Simulation_Enable` to false, the watch table
  showed all command, heartbeat, status, and timeout fields at their clean
  false/zero baseline.

The echo is intentionally one count behind the newly generated PC heartbeat:
each runtime cycle reads the PLC-owned values first and writes the next
PC heartbeat last. The first cycle therefore showed heartbeat `1` and echo
`0`; subsequent cycles showed a progressing echo and healthy communication.

This proves the guarded continuous runtime, PLC recovery, enabled gated
command path, and best-effort cleanup on this hardware. The separate
2026-07-24 watchdog test proved the stopped-heartbeat timeout and gated false
state. Together, the tests close the end-to-end commissioning milestone.

## Runtime milestone

The first Snap7 adapter and controlled runtime cycle are implemented:

- Snap7 is lazy-loaded behind a small testable transport protocol.
- The transport refuses reads of PC-owned tags and writes of PLC-owned tags.
- The runtime reads only configured `plc_to_pc` tags.
- The runtime writes only configured `pc_to_plc` tags.
- Non-heartbeat PC values are written only when changed, reducing the
  read/modify/write race created by opposite-owner DB14 bits sharing byte 0.
- The heartbeat is generated internally and written last.
- The default shutdown policy relies on the authoritative PLC watchdog.
- An explicit option enables best-effort safe-value writes before disconnect.
- The CLI does not connect without `--execute` and prints its exact write
  scope.

## Simulation update loop milestone

The typed simulation update loop is implemented and proven offline:

- scene inputs are supplied as partial PC-owned point updates;
- omitted PC points retain their last accepted value;
- point conversions are staged before one existing guarded runtime cycle;
- `clamp` stages the bounded raw value and reports degraded health;
- `fault` skips that point write, retains the previous accepted value, and
  reports fault health;
- all PLC-owned points are decoded from the current cycle read;
- bad PLC analog values preserve their raw value for diagnostics;
- heartbeat state and point quality produce explicit `starting`, `healthy`,
  `degraded`, or `fault` loop health;
- one optional JSON-lines record captures heartbeat, PC points, PLC points,
  and diagnostics for every completed update.

The implementation does not change the DB14 contract, current typed-tag
Snap7 transport, read/write ownership, live-proven cycle order, safe shutdown,
or PLC watchdog behavior. The loop requires schema version 2 with configured
points. Its tests use an in-memory transport and do not connect to a PLC.

The project passes 74 offline unit tests, including fake-transport runtime and
update-loop tests. The live hardware proof described above remains applicable
to the unchanged transport/runtime layer, not to the proposed DB100 typed
point example.

## Next implementation milestone

Build reusable simulation equipment components above the typed update loop,
starting with a small conveyor/photoeye component that has explicit inputs,
outputs, state transitions, timing, and reset-safe behavior.
