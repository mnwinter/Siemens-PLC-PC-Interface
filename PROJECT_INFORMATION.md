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

This proves PLC-side timeout and safe gating. It does not yet prove the new
continuous PC runtime.

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

This layer passes 41 offline unit tests with fake transports. It has not yet
been connected to the live PLC.

## Next implementation milestone

Run the guarded runtime against the real PLC and prove:

1. continuous heartbeat and echo progression;
2. `Simulation_Comm_OK` true while the loop is running;
3. timeout and gated false output after the loop stops;
4. recovery on a new progressing heartbeat;
5. cleanup of temporary PC-owned test values.

Do not add the graphical scene editor until the runtime and failure behavior
are proven.
