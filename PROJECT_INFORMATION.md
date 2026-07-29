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
- The optimized transport batches the five PLC-owned DB14 values into one
  contiguous DB read. The steady scene exchange is normally one DB read plus
  one heartbeat DB write.
- Boolean PC writes retain a read/modify/write boundary so the adjacent
  PLC-owned `DB14.DBX0.1` bit is preserved.
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

## Reusable component milestone

The first reusable offline process component is implemented:

- one-dimensional constant-speed conveyor motion;
- one product with explicit length and leading-edge position;
- one configured photoeye with swept-crossing detection;
- configurable minimum photoeye on-time to prevent a narrow simulated event
  from disappearing between update samples;
- explicit reset, stopped/running, empty/loaded states;
- one-cycle discharge event and completed-product count;
- dominant scene reset that suppresses run and clears product/sensor state;
- binding from a PLC-owned Boolean run point to a PC-owned photoeye point;
- fail-safe run suppression during update-loop startup, fault, bad command
  quality, or missing/invalid command mapping.

This component is intentionally single-product and forward-only. It does not
yet model acceleration, slip, accumulation, jams, collisions, reverse motion,
or a motor/drive. Product loading and scene reset remain host simulation
events rather than PLC commands.

The component layer has no Snap7 dependency and no knowledge of PLC IP,
rack/slot, DB numbers, or absolute addresses. Its behavior is proven only with
offline unit tests. DB14 and the typed DB100 example remain unchanged.

The project passes 88 offline unit tests through this component milestone.

## First deterministic scene milestone

The first deterministic headless scene is implemented:

- the DB14 interface was promoted to schema version 2 without changing any
  proven address or field ownership;
- `simulated_photoeye` maps to PC-owned `DB14.DBX0.0`;
- `conveyor_running` maps to PLC-owned `DB14.DBX0.1`;
- the scene file contains components, physical parameters, point names, and
  events but no PLC IP or address;
- the fixed physics step is 10 ms;
- the initial PLC exchange period is 20 ms with two exact physics steps per
  exchange;
- component and event types are allowlisted;
- binding type, ownership, group, uniqueness, and event alignment are
  validated offline before a connection;
- product load/reset events run on logical scene time;
- PLC commands from one completed exchange are applied to the following
  exchange;
- startup/fault/bad-quality command handling remains fail-safe;
- the real-time runner never makes large physics jumps or bursts extra PLC
  exchanges to recover lateness;
- average, maximum, recent-window p99, deadline overruns, and schedule
  resynchronizations are reported;
- `scene-run` retains the explicit `--execute` boundary and prints the exact
  DB write scope before connecting.

The original proof rung `PLC_To_PC := Simulation_Comm_OK AND PC_To_PLC` is not
a valid conveyor control rung because it creates a circular dependency. The
first scene commissioning guide requires:

```text
PLC_To_PC := Simulation_Comm_OK AND NOT PC_To_PLC
```

That PLC logic change uses the same DB14 contract. On 2026-07-29 it was
compiled, downloaded, and tested with the packaged first-scene runtime against
the target VM and CPU. The 250-exchange run completed with exit code 0:

```text
HEARTBEAT_PROOF: PASS
SAFE_STATE_WRITE: PASS
TIMING: cycles=250 overruns=24 resyncs=2 average_ms=9.261 maximum_ms=14.780 p99_ms=13.332
```

The scene reached its expected stopped-at-photoeye state with the product
loaded, photoeye blocked, and conveyor motor command false. This proves the
scene's functional PLC/PC loop on hardware. The original configured 20 ms run
still recorded 24 deadline overruns and two schedule resynchronizations.

After that result, the runtime was optimized offline:

- the five DB14 PLC-owned values are read in one contiguous S7 DB request;
- the normal heartbeat update is one S7 DB write;
- sensor writes remain ownership-safe read/modify/write operations;
- full scene JSON is printed every 25 cycles instead of every cycle, while
  health/state changes and the final cycle remain visible;
- `--cycle-ms` permits a guarded 20/15/10/5 ms rate sweep against a 5 ms
  physics profile.

These optimizations pass 113 offline unit tests.

On 2026-07-29, the optimized package was tested live from the Windows Server
2019 VM against the same CPU 1512SP-1 PN:

| Requested period | Cycles | Overruns | Resyncs | Average | Maximum | p99 | Result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 20 ms | 250 | 0 | 0 | 3.701 ms | 9.660 ms | 6.758 ms | Pass |
| 15 ms | 334 | 5 | 3 | 3.482 ms | 50.055 ms | 7.835 ms | Fail |
| 10 ms | 500 | 32 | 7 | 4.304 ms | 56.674 ms | 18.209 ms | Fail |
| 5 ms | 1000 | 136 | 1 | 3.175 ms | 12.617 ms | 6.412 ms | Fail |

All four runs retained `HEARTBEAT_PROOF: PASS` and
`SAFE_STATE_WRITE: PASS`. Only 20 ms satisfied the timing acceptance criteria:
zero resynchronizations and both maximum and p99 transaction duration below
the requested period. The Windows/VM scheduler produced occasional long-tail
delays at the faster rates even though their average transaction duration was
low.

A subsequent 30,000-cycle 20 ms soak, approximately ten minutes, reported:

```text
TIMING: cycles=30000 overruns=23 resyncs=7 average_ms=3.573 maximum_ms=13.012 p99_ms=5.913
HEARTBEAT_PROOF: PASS
SAFE_STATE_WRITE: PASS
```

`Simulation_Enable` was changed from false to true near cycle 2,867. The
heartbeat and safe-state proofs passed, and both maximum and p99 transaction
duration remained below 20 ms. The 23 scheduler overruns and seven
resynchronizations confirm that the Windows/VM host is not deterministic, but
this project is a visual logic simulator rather than a real-time machine
controller. The proven best-effort 20 ms exchange is therefore accepted as the
supported default. The PLC watchdog remains authoritative if communication
actually stops.

After the operator returned `Simulation_Enable` to false, the live watch table
confirmed `PC_To_PLC`, `PLC_To_PC`, `Simulation_Comm_OK`, and
`Simulation_Timeout` false, with both heartbeat values restored to zero.

The rate-test command files currently return the runtime's functional exit
code. Therefore, the faster timing failures still displayed exit code zero.
The printed timing criteria, not that exit code alone, were used to judge the
rate sweep.

## First graphical viewer milestone

The first graphical conveyor/photoeye runtime is implemented:

- `scene-visualize` preserves the existing `--execute` write authorization;
- previewing without `--execute` prints the exact scope and cannot connect;
- the existing deterministic `SceneEngine` remains the only process model;
- a worker thread owns Snap7, scene physics, timing, and cleanup;
- Tkinter only renders the latest completed scene report;
- GUI redraw timing is independent of the supported best-effort 20 ms PLC
  exchange;
- the viewer displays product position, conveyor state, photoeye state,
  heartbeat health, communication health, simulation enable, PLC timeout, and
  exchange timing;
- closing the window requests a stop before the runtime disconnects;
- optional best-effort safe-state writing remains available, while the PLC
  watchdog stays authoritative.

This milestone is offline-tested and packaged. Tkinter 8.6 imports on the
development PC, PyInstaller collected its `_tkinter` hook and Tcl/Tk data,
and the standalone EXE passed `scene-validate` plus the guarded
`scene-visualize` preview. The graphical window has not yet been opened in
the Windows Server 2019 VM or tested against the live DB14 exchange.

## Next implementation milestone

Copy `build\SiemensPlcPcInterface-GraphicalViewer-VM.zip` to the Windows
Server 2019 VM and run the first live visual test. Confirm the displayed
conveyor command, product movement, photoeye transition, DB14 status, clean
stop, and safe-state result.
