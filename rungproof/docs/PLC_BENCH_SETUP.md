# RungProof PLC Bench and Watchdog Setup

This document is the common foundation for every RungProof scene and training
lab. It is written for an isolated Siemens S7-1500 bench PLC with no physical
inputs, outputs, motors, valves, or safety circuits connected.

RungProof is a plant simulator. The PLC remains the controller: PLC-owned
commands drive the simulated equipment, and simulator-owned feedback is sent
back to the PLC. Never use this procedure on a production controller or a
machine with field energy connected.

## 1. Create the TIA Portal project

1. Open TIA Portal V17 and create one project for the bench exercise.
2. Add the actual S7-1500 CPU model and firmware used by the bench PLC.
3. Configure the PROFINET interface with the bench IP address, subnet, and
   device name supplied by the test workstation.
4. Use the CPU's actual rack and slot. The current reviewed Scene 2 profile is
   rack `0`, slot `1`; do not copy that value to another CPU without checking
   the hardware configuration.
5. Use a 20 ms exchange target for the simulator. This is a timing target, not
   permission to change the PLC cycle watchdog or safety settings.
6. Compile hardware and software before downloading. Use a software-only
   download when the hardware configuration is already correct.

## 2. Create the common simulation data block

Create a global DB named `DB_SimulationProof`. Keep the members below stable
across scenes and labs. Scene-specific process members are added separately;
they must not rename or reuse these members for another purpose.

| Member | Type | Direction | Purpose |
|---|---|---|---|
| `PC_Heartbeat` | DINT | Simulator → PLC | Counter/value sent by RungProof |
| `PLC_Heartbeat_Echo` | DINT | PLC → Simulator | Echo of the last accepted heartbeat |
| `Simulation_Enable` | BOOL | PLC → Simulator | Explicit bench permission |
| `Simulation_Comm_OK` | BOOL | PLC → Simulator | Watchdog communication status |
| `Simulation_Timeout` | BOOL | PLC → Simulator | Watchdog timeout indication |

The current Scene 2 DB14 layout places these members at `DBD2`, `DBD6`, and
`DBX10.0` through `DBX10.2`. Those offsets belong to that reviewed profile;
the symbolic members and verified profile must remain the source of truth.

For any live or bench profile, confirm optimized/non-optimized DB behavior and
absolute offsets in TIA before connecting. Never assume an offset after adding
or reordering members.

## 3. Watchdog behavior

The watchdog block should:

1. accept a new `PC_Heartbeat` value;
2. echo the accepted value to `PLC_Heartbeat_Echo`;
3. set `Simulation_Comm_OK` only while heartbeat updates arrive within the
   configured timeout;
4. set `Simulation_Timeout` when updates stop or become stale;
5. keep all exercise outputs in their safe state when communication is not
   healthy;
6. require a fresh healthy exchange before outputs are considered enabled.

`Simulation_Enable` is an explicit operator/program permission. It is not a
replacement for the watchdog. A TRUE enable with a stale heartbeat must still
produce `Simulation_Comm_OK = FALSE` and `Simulation_Timeout = TRUE`.

Do not create a second watchdog inside an individual lab. If a lab intentionally
tests a watchdog fault, document the changed condition and restore the common
block afterward.

## 4. Watch-table verification

Create a watch table containing the five common members and the active scene's
process tags. With RungProof disconnected, outputs must remain safe. With the
bench connection authorized:

1. confirm `PC_Heartbeat` changes across exchanges;
2. confirm `PLC_Heartbeat_Echo` follows it;
3. confirm `Simulation_Enable` is deliberately TRUE;
4. confirm `Simulation_Comm_OK` becomes TRUE;
5. confirm `Simulation_Timeout` becomes FALSE;
6. confirm scene feedback changes only when the simulated equipment changes;
7. confirm PLC commands change only from the PLC program.

The read-only diagnostic does not increment the heartbeat and cannot prove
watchdog readiness. Use the authorized simulation exchange for that test.

## 5. Safe stop and reset

- **Stop** holds the simulated plant and leaves the bench session connected.
- **Reset** returns the scene to its documented initial state; it does not
  silently repair PLC logic or force PLC-owned commands.
- **Disconnect** ends the exchange and the PLC watchdog must return the plant
  to its configured safe state.
- A communication loss, stale heartbeat, invalid profile, or failed exchange
  must fail closed and require a fresh healthy Run.

## 6. Scene and lab point ownership

Every scene Setup page lists its exact process contract:

- `PLC → Simulator`: commands the PLC must produce;
- `Simulator → PLC`: feedback the simulator produces;
- `Internal SIM`: diagnostics not assigned in the PLC.

The student may use the canonical symbolic names directly or map them to
verified PLC symbols in an external profile. Scene files never contain IP
addresses, rack/slot values, physical `%I`/`%Q` addresses, or write authority.

## 7. Troubleshooting readiness

| Indication | Meaning | First check |
|---|---|---|
| `PLC WAIT` | No controller source is authorized | Enable the intended bench path |
| `Simulation_Enable = FALSE` | PLC has not permitted the exercise | Check the setup rung/watch table |
| `Simulation_Comm_OK = FALSE` | Heartbeat is not accepted | Check profile, DB type, and exchange |
| `Simulation_Timeout = TRUE` | Heartbeat stopped or is stale | Check transport and watchdog timing |
| Healthy heartbeat but no motion | PLC command is FALSE | Monitor the scene output rung |
| Motion with no expected command | Stop and inspect the PLC mapping/profile | Do not correct it in the simulator |
| Feedback never changes | Check simulated equipment state and point binding | Verify sensor tag direction/type |

## 8. Cumulative labs

Lab 2.1 creates this foundation. Later labs retain the watchdog, common DB,
watch table, and earlier project logic. Each lab's Setup page lists only its
new or changed tags and links back to the retained foundation. Independent
scenes reuse this foundation where compatible but keep their process contracts
separate.

