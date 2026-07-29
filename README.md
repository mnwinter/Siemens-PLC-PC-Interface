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
| Result | DB14 round trip, watchdog, continuous runtime, and safe cleanup passed |

S7-1200 support is planned but has not yet been hardware-proven by this
project. Other S7-1500 models and firmware must also be verified before being
listed as proven.

This repository is not yet a graphical scene editor. It currently contains the proven
connection diagnostics, the PLC-side communication watchdog, the DB14 memory
contract, setup documentation, a validated JSON configuration model, and a
guarded configuration-driven Snap7 runtime. It also contains an offline-tested
typed point layer for digital inversion, analog scaling, units, range quality,
and ownership-aware DB address grouping. A deterministic typed simulation
update loop now stages scene values, decodes PLC points, reports communication
and point health, and can emit JSON-lines cycle logs. The first reusable
offline equipment model adds a single-object conveyor, simulated photoeye,
explicit operating states, product discharge, reset, and fail-safe point
binding. The first deterministic headless scene now loads the conveyor from
JSON, advances physics in fixed steps, exchanges typed points at a configured
rate, and reports bounded timing/overrun metrics. The optimized transport
reads the PLC-owned DB14 fields in one contiguous request and normally writes
only the heartbeat in a second request.

The Snap7 transport and runtime pass offline tests with fake clients. On
2026-07-29, the packaged runtime passed live heartbeat progression, recovery,
the enabled gated command path, and its best-effort safe-state write against
the real CPU 1512SP-1 PN. The earlier live watchdog test proved timeout and
gated false behavior when heartbeat progression stops.

## Start here

New users should follow:

1. [Processor, network, DB, and PC setup](docs/USER_SETUP.md)
2. [DB14 memory contract](docs/DB14_INTERFACE.md)
3. [JSON configuration reference](docs/CONFIGURATION.md)
4. [Typed digital and analog point model](docs/POINT_MODEL.md)
5. [Typed simulation update loop and logging](docs/UPDATE_LOOP.md)
6. [Reusable simulation components](docs/COMPONENTS.md)
7. [First conveyor/photoeye scene](docs/FIRST_SCENE.md)
8. [Real-hardware proof results](docs/PROOF_RESULTS.md)

The setup guide covers:

- processor network configuration;
- CPU PUT/GET and firmware-dependent access-control settings;
- the secure PG/PC option;
- creation of the standard/non-optimized DB14;
- PLC watchdog, gated mapping logic, and watch table;
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

Validate the example configuration without connecting:

```powershell
.\.venv\Scripts\siemens-plc-pc-interface.exe validate `
    .\examples\db14-interface.json
```

Preview the runtime's exact write scope. This still does not connect:

```powershell
.\.venv\Scripts\siemens-plc-pc-interface.exe run `
    .\examples\db14-interface.json `
    --cycles 20 `
    --set pc_to_plc=true
```

Both commands explicitly report
`PLC_CONNECTION_ATTEMPTED: False`.

Validate the first scene without connecting:

```powershell
.\.venv\Scripts\siemens-plc-pc-interface.exe scene-validate `
    .\examples\db14-conveyor-interface.json `
    .\examples\conveyor-scene.json
```

The proven first scene uses a 10 ms fixed physics step and a 20 ms PLC
exchange. A separate 5 ms physics profile supports controlled 20, 15, 10, and
5 ms rate tests through `scene-run --cycle-ms`. Read
[the first-scene commissioning guide](docs/FIRST_SCENE.md) before live use:
the original DB14 Boolean echo rung must become a stop-at-photoeye PLC command
rung for the conveyor to move.

Only after DB14 and the PLC watchdog are downloaded, set
`Simulation_Enable = true` from TIA and authorize the guarded runtime:

```powershell
.\.venv\Scripts\siemens-plc-pc-interface.exe run `
    .\examples\db14-interface.json `
    --execute `
    --cycles 20 `
    --set pc_to_plc=true `
    --write-safe-state-on-exit
```

The runtime writes only the two configured PC-owned DB14 fields. It does not
write `Simulation_Enable`.

## Validated DB14 proof contract

| Address | Symbol | Type | Owner |
|---|---|---|---|
| `DB14.DBX0.0` | `PC_To_PLC` | `Bool` | PC writes |
| `DB14.DBX0.1` | `PLC_To_PC` | `Bool` | PLC writes |
| `DB14.DBD2` | `PC_Heartbeat` | `DInt` | PC writes |
| `DB14.DBD6` | `PLC_Heartbeat_Echo` | `DInt` | PLC writes |
| `DB14.DBX10.0` | `Simulation_Enable` | `Bool` | Operator/PLC writes |
| `DB14.DBX10.1` | `Simulation_Comm_OK` | `Bool` | PLC writes |
| `DB14.DBX10.2` | `Simulation_Timeout` | `Bool` | PLC writes |

DB14 must use standard/non-optimized access because the current S7 client uses
fixed absolute addresses.

## Safety and security boundary

The configured runtime write scope is limited to `DB14.DBX0.0` and
`DB14.DBD2`. It does not write physical I/O, the operator enable, the
PLC-owned status fields, or CPU operating state.

PUT/GET is not authenticated or encrypted. Use an isolated or properly
segmented controls network, limit access to TCP port 102, and never expose the
PLC directly to the Internet.

Do not connect simulated commands directly to hazardous motion or outputs.
PLC permissives, interlocks, safety logic, and a heartbeat timeout must remain
authoritative.

## Roadmap

1. **Complete:** validated configuration-driven connection and tag model.
2. **Complete offline:** guarded Snap7 transport and continuous heartbeat
   runtime with unit-tested ownership and shutdown behavior.
3. **Complete on hardware:** continuous heartbeat, healthy state, recovery,
   enabled gated output, watchdog timeout, and safe cleanup.
4. **Complete offline:** typed digital and analog point model with ownership,
   inversion, scaling, units, safe values, range quality, and address-group
   diagnostics.
5. **Complete offline:** deterministic simulation update loop with retained
   scene values, point diagnostics, communication health, and JSON-lines
   logging.
6. **Complete offline:** first reusable conveyor/photoeye component.
7. **Complete on hardware:** deterministic first conveyor/photoeye scene,
   guarded 20 ms PLC exchange, heartbeat proof, and safe cleanup.
8. **Complete on hardware:** the optimized 20/15/10/5 ms rate sweep retained
   heartbeat and safe cleanup at every rate. Only 20 ms passed the timing
   criteria with zero overruns, zero resynchronizations, 6.758 ms p99, and
   9.660 ms maximum duration in the five-second sweep. A later 30,000-cycle
   soak retained heartbeat and safe cleanup with 5.913 ms p99 and 13.012 ms
   maximum workload, but recorded 23 scheduler overruns and seven
   resynchronizations. The project is a visual logic simulator rather than a
   real-time machine controller, so the proven best-effort 20 ms exchange is
   the supported default; the PLC watchdog remains authoritative.
9. **Next:** graphical conveyor scene runtime using the existing headless
   engine and proven 20 ms PLC exchange.

## Development

Install development dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Generated EXEs, ZIP packages, PLC project archives, credentials, and Python
environments are intentionally excluded from Git.

Build the standalone Windows runtime from an approved development computer:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm --clean --onefile `
    --name SiemensPlcPcInterface `
    --paths src --collect-all snap7 `
    --distpath build\vm-package `
    --workpath build\pyinstaller-work `
    --specpath build\pyinstaller-spec `
    tools\runtime_entrypoint.py
```

Run the offline unit suite:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -v
```
