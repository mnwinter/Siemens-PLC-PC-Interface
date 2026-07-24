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

This proves the PLC-side communication-loss behavior. It does not yet prove
the new continuous PC runtime against hardware; that is the next live test.
