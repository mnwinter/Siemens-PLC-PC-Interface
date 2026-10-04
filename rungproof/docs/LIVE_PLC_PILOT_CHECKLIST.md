# Live PLC pilot checklist

Use this record for Matt's internal Scene 2 ladder-logic test. RungProof is the
simulated plant. TIA creates the ladder and the live PLC executes it. Do not use
this procedure on a production CPU or a controller connected to field outputs.

## 1. Record the exact bench

First run packaged `BENCH-PREFLIGHT.ps1`. Retain the generated
`bench-evidence/BENCH-PREFLIGHT.json`; it records package/profile hashes and
creates `BENCH-RESULT.json` for the live observations below without contacting
the PLC.

- [ ] TIA Portal version and update: ______________________________
- [ ] CPU order number: ___________________________________________
- [ ] CPU firmware: _______________________________________________
- [ ] VM Windows edition/build: ___________________________________
- [ ] VM platform/version: ________________________________________
- [ ] PLC IP: `10.70.9.201`, or approved profile change: __________
- [ ] Rack/slot: `0/1`, or approved profile change: _______________
- [ ] Confirm no physical field I/O or machine energy is connected.

Any endpoint change must be made in the external PLC profile and reviewed in
RungProof before connection. Do not put PLC addressing in the scene file.

## 2. Confirm the DB14 contract in TIA

- [ ] `DB_SimulationProof` is standard/non-optimized.
- [ ] `DB14.DBX0.0` `Part_At_Pusher` BOOL, RungProof to PLC.
- [ ] `DB14.DBX0.1` `Pusher_Extended` BOOL, RungProof to PLC.
- [ ] `DB14.DBX0.2` `Pusher_Retracted` BOOL, RungProof to PLC.
- [ ] `DB14.DBX1.0` `Conveyor_Run` BOOL, PLC to RungProof.
- [ ] `DB14.DBX1.1` `Pusher_Extend` BOOL, PLC to RungProof.
- [ ] `DB14.DBD2` `PC_Heartbeat` DINT, RungProof to PLC.
- [ ] `DB14.DBD6` `PLC_Heartbeat_Echo` DINT, PLC to RungProof.
- [ ] `DB14.DBX10.0` `Simulation_Enable` BOOL, PLC to RungProof.
- [ ] `DB14.DBX10.1` `Simulation_Comm_OK` BOOL, PLC to RungProof.
- [ ] `DB14.DBX10.2` `Simulation_Timeout` BOOL, PLC to RungProof.
- [ ] Project compiles with no unresolved DB layout or optimized-access issue.
- [ ] Create a watch table containing all ten members above.

## 3. Minimum ladder behavior to prove

The exact rung structure is yours; RungProof tests the observable behavior.

- [ ] With simulation disabled or communication unhealthy, both PLC commands
      are FALSE.
- [ ] Echo each newly accepted `PC_Heartbeat` into `PLC_Heartbeat_Echo`.
- [ ] Set `Simulation_Comm_OK` only while heartbeat data is fresh.
- [ ] Set `Simulation_Timeout` when heartbeat data is stale.
- [ ] `Simulation_Enable` is an explicit permission and cannot override a bad
      watchdog.
- [ ] Run the conveyor while a part approaches the pusher.
- [ ] Stop the conveyor when `Part_At_Pusher` becomes TRUE.
- [ ] Extend the pusher only with the conveyor stopped and the part present.
- [ ] Remove the extend command after `Pusher_Extended` becomes TRUE so the
      single-solenoid pusher spring-returns.
- [ ] Do not admit the next part until `Pusher_Retracted` is TRUE.

## 4. Connect and prove normal operation

1. Verify the package hash and start RungProof. Expected: disconnected; no
   automatic PLC connection.
2. Run **Test PLC - Read-only**. Expected: two reads, zero writes, clean
   disconnect. This proves reachability and address readability only.
3. Open **Connect Real PLC**, compare every displayed read/write address with
   this record, check the authorization box, and connect.
4. In the TIA watch table, set or otherwise establish `Simulation_Enable` by
   the intended program/operator method.
5. Confirm heartbeat changes and exact echo, `Simulation_Comm_OK = TRUE`, and
   `Simulation_Timeout = FALSE`.
6. Press **Run** and observe two complete cycles:
   conveyor run -> photoeye blocked -> conveyor stop -> pusher extend -> part
   transfer -> pusher retract -> next part admitted.
7. Record two-cycle result and any timing issue: ____________________________

## 5. Prove controls and failure recovery

- [ ] **Stop** holds the plant while the connection and heartbeat remain live.
- [ ] A fresh **Run** resumes only when readiness is healthy.
- [ ] **Reset** resets the plant without altering PLC-owned commands.
- [ ] Disconnect RungProof. The app immediately stops presenting cached PLC
      telemetry as current: Health becomes `CLOSING`/`DISCONNECTED`, heartbeat
      and PLC status values show unavailable (`--`), and PLC-owned command
      points such as `conveyor_running` and `pusher_extend` show `--`. After
      the watchdog delay, confirm in TIA that communication is bad/timed out
      and commands are safe.
- [ ] Reconnect. Motion does not resume until a fresh operator **Run**.
- [ ] Close RungProof. Session closes and PLC watchdog returns commands safe.
- [ ] Interrupt the bench network. RungProof reports the fault, commands are
      suppressed in the plant model, and recovery requires a fresh **Run**.
- [ ] Confirm in the watch table that RungProof changed only the four declared
      PC-owned addresses.

## 6. Acceptance

- Candidate version: ______________________________________________
- Candidate ZIP SHA-256: __________________________________________
- Date/time: ______________________________________________________
- Result: [ ] PASS  [ ] FAIL
- Notes or defects: _______________________________________________
- Matt approval for this exact internal bench configuration:
  [ ] APPROVED  [ ] NOT APPROVED

Passing this checklist approves the recorded internal configuration. It does
not establish generic Siemens compatibility or authorize production-machine
use or external distribution.

After filling the matching fields in `bench-evidence/BENCH-RESULT.json`, run
packaged `VALIDATE-BENCH-RESULT.ps1`. A complete passing record produces
`bench-evidence/BENCH-ACCEPTANCE.json`; incomplete or failed evidence is
rejected.

## 7. Corrected-candidate delta qualification

The retained accepted baseline may be used only for the exact unchanged
profile and PLC target. It does not accept a different executable by itself.
For the disconnect-telemetry correction, keep the baseline folder unchanged
and run the corrected package's preflight with:

```powershell
.\BENCH-PREFLIGHT.ps1 `
  -BaselineEvidenceDirectory "C:\path\to\baseline\bench-evidence"
```

Fill the generated `BENCH-DELTA-RESULT.json`. The required current-executable
checks are one normal cycle, exact write-scope reconfirmation, truthful
unavailable telemetry during explicit Disconnect and network loss, PLC
watchdog safe state after explicit Disconnect, a stopped RungProof plant
during network loss, automatic reconnect, fresh Run after recovery, and safe
application Close. Then run:

```powershell
.\VALIDATE-BENCH-DELTA.ps1 `
  -BaselineEvidenceDirectory "C:\path\to\baseline\bench-evidence"
```

Only the resulting `BENCH-DELTA-ACCEPTANCE.json`, together with the unchanged
baseline chain, accepts the corrected executable.
