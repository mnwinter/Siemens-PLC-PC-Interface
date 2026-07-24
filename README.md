# Siemens PLC-PC Interface

An open PC-to-Siemens PLC interface for testing automation logic with
simulated sensors, actuators, and processes.

## Project goal

The goal is to build a maintainable Factory I/O-style interface that can:

- connect a Windows PC to a Siemens S7-1200 or S7-1500;
- read PLC commands and status;
- write simulated sensor and process values;
- use configuration files instead of hard-coded PLC addresses;
- provide connection state, heartbeat, diagnostics, and safe defaults;
- eventually support a graphical scene/runtime layer for PLC program testing.

The PLC remains responsible for permissives, interlocks, operating modes,
fault handling, and safety. The PC interface is a simulation and commissioning
tool, not a safety controller.

## Architecture

```mermaid
flowchart LR
    Scene["Future scene / simulation runtime"]
    Client["PC S7 client"]
    DB["Dedicated standard-access simulation DB"]
    Mapping["PLC mapping and heartbeat logic"]
    Program["Machine control program"]

    Scene <--> Client
    Client <--> DB
    DB <--> Mapping
    Mapping <--> Program
```

The dedicated DB prevents the PC from writing physical `%I` or `%Q` addresses
directly and gives every field one defined writer.

## Current status

The communications baseline has been proven on real hardware:

| Component | Proven configuration |
|---|---|
| PLC | Siemens CPU 1512SP-1 PN |
| Engineering software | TIA Portal V17 |
| PC | Windows Server 2019 VM |
| Network | Passed-through ASIX USB Ethernet adapter |
| Library | `python-snap7 3.1.0` |
| Result | Bidirectional DB14 round trip passed and original values restored |

S7-1200 support is planned but has not yet been hardware-proven by this
project. Other S7-1500 models and firmware must also be verified before being
listed as proven.

This repository is not yet a scene editor or complete simulation runtime. It
currently contains the proven connection diagnostics, PLC memory contract,
and setup documentation that the full interface will build on.

## Start here

New users should follow:

1. [Processor, network, DB, and PC setup](docs/USER_SETUP.md)
2. [DB14 memory contract](docs/DB14_INTERFACE.md)
3. [Real-hardware proof results](docs/PROOF_RESULTS.md)

The setup guide covers:

- processor network configuration;
- CPU PUT/GET and firmware-dependent access-control settings;
- the secure PG/PC option;
- creation of the standard/non-optimized DB14;
- PLC echo logic and watch table;
- PC dependency installation;
- read-only and guarded round-trip testing;
- failure symptoms and first checks.

## Quick software setup

```powershell
git clone https://github.com/mnwinter/Siemens-PLC-PC-Interface.git
cd Siemens-PLC-PC-Interface
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the read-only connection proof first:

```powershell
.\.venv\Scripts\python.exe .\tools\prove_s7_connection.py `
    --ip 10.70.9.201
```

Only after the processor and DB are configured, run the guarded write test:

```powershell
.\.venv\Scripts\python.exe .\tools\round_trip_db14.py `
    --ip 10.70.9.201 `
    --execute `
    --hold-seconds 5
```

Without `--execute`, the round-trip utility exits before connecting or
writing.

## Validated DB14 proof contract

| Address | Symbol | Type | Owner |
|---|---|---|---|
| `DB14.DBX0.0` | `PC_To_PLC` | `Bool` | PC writes |
| `DB14.DBX0.1` | `PLC_To_PC` | `Bool` | PLC writes |
| `DB14.DBD2` | `PC_Heartbeat` | `DInt` | PC writes |
| `DB14.DBD6` | `PLC_Heartbeat_Echo` | `DInt` | PLC writes |

DB14 must use standard/non-optimized access because the current S7 client uses
fixed absolute addresses.

## Safety and security boundary

The diagnostic write test is limited to `DB14.DBX0.0` and `DB14.DBD2`. It
does not write physical I/O, the PLC-owned echo fields, or CPU operating
state.

PUT/GET is not authenticated or encrypted. Use an isolated or properly
segmented controls network, limit access to TCP port 102, and never expose the
PLC directly to the Internet.

Do not connect simulated commands directly to hazardous motion or outputs.
PLC permissives, interlocks, safety logic, and a heartbeat timeout must remain
authoritative.

## Roadmap

1. Configuration-driven PLC connections and tag mappings.
2. Continuous heartbeat and communication-loss safe state.
3. Typed digital and analog point model.
4. Simulation update loop with diagnostics and logging.
5. Reusable equipment components.
6. Graphical scene editor and runtime.

## Development

Install development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Generated EXEs, ZIP packages, PLC project archives, credentials, and Python
environments are intentionally excluded from Git.
