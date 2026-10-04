# RungProof failure-test catalog

Failure testing is a separate acceptance lane from the normal happy-path
sequence. Every case injects one bad condition and verifies the resulting
machine state, PLC command state, and diagnostic response.

| Case | Injection | Required response |
| --- | --- | --- |
| `profile_missing_photoeye` | Remove the PC-owned photoeye tag from the Scene 2 PLC profile | Reject the profile before connecting; do not run the machine |
| `normal_sequence` | Valid photoeye and normal PLC output sequence | Package reaches the photoeye, conveyor stops, and the pusher waits for its command |
| `photoeye_stuck_low` | Ignore photoeye writes so the PLC never sees `part_at_pusher = TRUE` | Conveyor remains commanded to run, the part discharges, and the pusher does not fire; the real PLC program should additionally alarm/timeout if pass-through is not acceptable |
| `photoeye_stuck_high` | Hold `part_at_pusher = TRUE` with no physical part at the sensor | Conveyor stops and the pusher may extend, but no transfer is allowed; require a PLC diagnostic/interlock and operator-visible fault |
| `conveyor_output_missing` | PLC never produces the conveyor command | Package remains in place; no transfer is reported |
| `pusher_without_part` | PLC extends the pusher before a package is present | Cylinder moves but no transfer is invented; ladder logic should interlock or alarm |
| `both_outputs` | Conveyor and pusher outputs are active together | No silent valid transfer; this is a command-conflict alarm case |
| `conveyor_stopped` | PLC conveyor command is forced false | Package remains in place and the sequence does not complete |
| `ladder_missing_pusher_command` | Part-at-pusher becomes TRUE but no PLC pusher command is generated | Agent must fail the ladder test and require `Pusher_Extend` or a sequence timeout/fault |
| `heartbeat_loss` | Stop echoing the PC heartbeat | Playback must stop and outputs must go safe; reconnection requires a fresh Run |
| `simulation_not_enabled` | Keep `Simulation_Enable = FALSE` | Scene remains PLC WAIT/disabled; no PLC-owned command is synthesized |
| `communication_not_ok` | Keep `Simulation_Comm_OK = FALSE` | Scene remains safe even if a process command was previously TRUE |
| `simulation_timeout` | Set `Simulation_Timeout = TRUE` | Commands are suppressed and the operator receives a watchdog diagnostic |
| `wrong_type_mapping` | Map a BOOL/REAL/DINT point to the wrong type | Profile/connection validation rejects the contract before exchange |
| `scene_missing_command` | Remove one scene PLC output from the ladder trace | Equipment affected by that command remains stopped; no completion is invented |
| `feedback_stuck` | Hold a scene feedback point at its initial value | Equipment follows actual commands; the test reports the missing/stale feedback |
| `contradictory_commands` | Energize mutually exclusive outputs together | The simulator reflects the commands and reports the conflict; it does not choose a preferred output |

Run the current deterministic agent with:

```powershell
py -3 tools\failure_test_agent.py
```

The agent intentionally reports `ladder_missing_pusher_command` as a failure
against the current screenshot logic. That is the expected result until the
PLC ladder contains the pusher-extension sequence or an explicit timeout/fault
path. The agent must not be changed to hide that failure.
