# Siemens PLC-PC Interface

PC interface for reading and writing a dedicated Siemens PLC simulation data
block. The long-term goal is a Factory I/O-style test interface without
writing directly to physical PLC I/O.

## Current status

The communication method has been proven on the following real system:

- CPU: Siemens CPU 1512SP-1 PN
- PLC address: `10.70.9.201`
- Engineering environment: TIA Portal V17
- PC environment: Windows Server 2019 VM
- Network path: passed-through ASIX USB Ethernet adapter
- S7 library: `python-snap7 3.1.0`

The validated test established an S7 session, wrote the two PC-owned DB14
fields, read both PLC echo fields, and restored the original values.

This repository is not yet a complete scene editor or general-purpose
simulation runtime. The current code is the proven communications baseline.

## DB14 interface

| Address | Symbol | Type | Owner |
|---|---|---|---|
| `DB14.DBX0.0` | `PC_To_PLC` | `Bool` | PC writes |
| `DB14.DBX0.1` | `PLC_To_PC` | `Bool` | PLC writes |
| `DB14.DBD2` | `PC_Heartbeat` | `DInt` | PC writes |
| `DB14.DBD6` | `PLC_Heartbeat_Echo` | `DInt` | PLC writes |

DB14 must use standard, non-optimized access for these absolute addresses.
See [docs/DB14_INTERFACE.md](docs/DB14_INTERFACE.md) before changing the PLC
data block.

## Run from source

Create a virtual environment and install the pinned dependency:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the read-only connection proof first:

```powershell
.\.venv\Scripts\python.exe .\tools\prove_s7_connection.py --ip 10.70.9.201
```

Then run the guarded DB14 round-trip test:

```powershell
.\.venv\Scripts\python.exe .\tools\round_trip_db14.py `
    --ip 10.70.9.201 `
    --execute `
    --hold-seconds 5
```

Without `--execute`, the round-trip utility exits before connecting or
writing.

## Safety boundary

The diagnostic write test is limited to `DB14.DBX0.0` and `DB14.DBD2`. It
does not write physical inputs, physical outputs, PLC-owned echo fields, or
CPU operating state.

Do not connect future simulation commands directly to machine motion or
hazardous outputs. PLC permissives, interlocks, safety logic, and a heartbeat
timeout must remain authoritative.
