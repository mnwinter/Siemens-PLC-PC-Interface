# Hardware proof results

## Test environment

- Date: 2026-07-24
- PLC: CPU 1512SP-1 PN
- PLC address: `10.70.9.201`
- PC address: `10.70.9.242`
- PC environment: Windows Server 2019 VM
- Network adapter: passed-through ASIX USB Ethernet
- Rack/slot: `0/1`
- Negotiated S7 PDU: 480 bytes

## Read-only proof

The client established an S7 session and identified the controller as a CPU
1512SP-1 PN. Process input and output byte reads also completed.

Some optional system-information queries returned unsupported-service errors.
Those errors did not affect the S7 session or DB read/write operations.

## DB14 round-trip proof

```text
ORIGINAL:
  PC_To_PLC=False
  PLC_To_PC=False
  PC_Heartbeat=12345
  PLC_Heartbeat_Echo=12345

TEST_A:
  PC_To_PLC=True
  PLC_To_PC=True
  PC_Heartbeat=24072401
  PLC_Heartbeat_Echo=24072401
  PASS=True

TEST_B:
  PC_To_PLC=False
  PLC_To_PC=False
  PC_Heartbeat=24072402
  PLC_Heartbeat_Echo=24072402
  PASS=True

RESTORED:
  PC_To_PLC=False
  PC_Heartbeat=12345

RESTORE_CONFIRMED=True
ROUND_TRIP_PROOF=PASS
```

This proves the custom PC client can exchange data bidirectionally with this
controller through the dedicated DB14 interface.

## PLC watchdog proof

After the baseline proof, DB14 and the PLC logic were extended with:

```text
DB14.DBX10.0  Simulation_Enable
DB14.DBX10.1  Simulation_Comm_OK
DB14.DBX10.2  Simulation_Timeout
```

`Simulation_Watchdog [FB3]` was called from OB1 with a `T#2s` timeout. A
rebuild compiled with zero errors and zero warnings before the software was
downloaded.

Live watch-table results:

```text
Simulation_Enable=True
PC_Heartbeat=1
PLC_Heartbeat_Echo=1
Simulation_Comm_OK=False
Simulation_Timeout=True
PC_To_PLC=True
PLC_To_PC=False
```

Interpretation:

- the heartbeat change was received and echoed;
- the heartbeat then stopped progressing for longer than two seconds;
- the PLC declared a timeout;
- the watchdog gate prevented `PC_To_PLC=True` from propagating to
  `PLC_To_PC`.

This proves the PLC-side communication-loss behavior.

## Guarded continuous runtime proof

On 2026-07-29, the packaged `SiemensPlcPcInterface.exe` was run from the
Windows Server 2019 VM. The live CLI reported this exact authorized scope:

```text
pc_to_plc=DB14.DBX0.0:BOOL
pc_heartbeat=DB14.DBD2:DINT
```

Across two commissioning runs, the observed runtime states included:

```text
CYCLE 1:
  heartbeat=1
  echo=0
  healthy=False
  reason=waiting_for_first_echo

CYCLE 2 and later:
  echo progressing
  healthy=True
  Simulation_Enable=True
  Simulation_Comm_OK=True
  Simulation_Timeout=False
  PLC_To_PC=True

Final CLI results:
  HEARTBEAT_PROOF: PASS
  SAFE_STATE_WRITE: PASS

Post-stop watch table:
  PC_To_PLC=False
  PC_Heartbeat=0
  Simulation_Enable=True
  Simulation_Comm_OK=False
  Simulation_Timeout=True
  PLC_To_PC=False
```

The heartbeat/echo count difference is intentional. The runtime reads the
PLC-owned echo before it writes the new PC-owned heartbeat, so the accepted
echo normally trails the newly generated heartbeat by one cycle.

This proves continuous exchange, recovery from a prior timeout, the enabled
command path, watchdog timeout after the runtime stops, gated false output,
and best-effort restoration of the PC-owned safe values.
