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

## Next implementation milestone

Replace hard-coded proof tags with a validated configuration file containing:

- connection settings;
- symbolic tag names;
- absolute PLC addresses and data types;
- direction and ownership;
- update rate;
- safe default value;
- heartbeat timeout behavior.

The configuration layer must be completed before adding a graphical scene
editor.
