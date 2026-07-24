# Interface configuration

The first production layer replaces hard-coded PLC settings with a validated
JSON file. Configuration validation is completely offline and does not import
Snap7, connect to a PLC, or write PLC memory.

## Validate the included DB14 example

After installing the project:

```powershell
siemens-plc-pc-interface validate .\examples\db14-interface.json
```

Or run the package directly:

```powershell
python -m siemens_plc_pc_interface validate `
    .\examples\db14-interface.json
```

Expected output includes:

```text
CONFIG_VALID: True
PC_TO_PLC_TAGS: 2
PLC_TO_PC_TAGS: 2
PLC_CONNECTION_ATTEMPTED: False
```

## Top-level fields

| Field | Purpose |
|---|---|
| `version` | Configuration schema version; currently `1` |
| `connection` | CPU family, IP, rack/slot, and timing |
| `heartbeat` | PC heartbeat tag, PLC echo tag, and timeout |
| `tags` | Typed PLC tag mappings and ownership |

Unknown fields are rejected. This catches spelling mistakes instead of
silently ignoring them.

## Connection

```json
{
  "cpu_family": "s7-1500",
  "ip": "10.70.9.201",
  "rack": 0,
  "slot": 1,
  "cycle_ms": 100,
  "connect_timeout_ms": 2000
}
```

Rules:

- `cpu_family` must be `s7-1200` or `s7-1500`.
- `ip` must be a valid IPv4 address.
- `rack` must be from 0 through 7.
- `slot` must be from 0 through 31.
- `cycle_ms` must be from 10 through 5000.
- `connect_timeout_ms` must be from 100 through 30000.

Rack/slot `0/1` is the proven value for this project's CPU 1512SP-1 PN test.
Keep both fields configurable for other hardware.

## Tag mapping

```json
{
  "name": "pc_to_plc",
  "plc_symbol": "DB_SimulationProof.PC_To_PLC",
  "address": "DB14.DBX0.0",
  "data_type": "BOOL",
  "direction": "pc_to_plc",
  "safe_value": false
}
```

### Name

`name` is the stable PC-side identifier. It must begin with a lowercase
letter and contain only lowercase letters, digits, and underscores.

### PLC symbol

`plc_symbol` is documentation for the matching TIA Portal symbol. The current
Snap7 path still uses the absolute `address`.

### Address

Only absolute data-block addresses are accepted:

| Data type | Required address area | Example |
|---|---|---|
| `BOOL` | `DBX` | `DB14.DBX0.0` |
| `BYTE` | `DBB` | `DB14.DBB10` |
| `WORD`, `INT` | `DBW` | `DB14.DBW12` |
| `DWORD`, `DINT`, `REAL` | `DBD` | `DB14.DBD14` |

Physical `%I`, `%Q`, and `%M` addresses are rejected. Overlapping DB fields are
also rejected, including a byte/word/dword that overlaps configured bits.

### Direction and ownership

`direction` determines the only allowed writer:

- `pc_to_plc`: the PC runtime may write the tag;
- `plc_to_pc`: the PLC owns the tag and the PC runtime may only read it.

The future runtime will build separate read and write lists from this field.

### Safe value

Every `pc_to_plc` tag requires a type-checked `safe_value`. PLC-owned tags must
omit it or set it to `null`.

The validator checks signed/unsigned integer ranges and requires a real JSON
Boolean for `BOOL`.

Safe values are configuration data only in the current milestone. No code in
this release writes them to the PLC.

## Heartbeat

```json
{
  "pc_tag": "pc_heartbeat",
  "echo_tag": "plc_heartbeat_echo",
  "timeout_ms": 1000
}
```

Rules:

- `pc_tag` must reference a `pc_to_plc` `DINT`;
- `echo_tag` must reference a different `plc_to_pc` `DINT`;
- `timeout_ms` must be at least twice the configured cycle time.

The heartbeat state machine detects progress, not merely a connected socket.
If the PLC echo stops changing longer than the timeout, its status becomes
`echo_stalled`.

The current milestone implements and tests this state machine offline. The
next milestone will connect it to the Snap7 runtime and define exactly when
safe values may be written.

## Validation failures

Invalid configuration returns exit code `2` and a specific path:

```text
CONFIG_INVALID: tags[0].address must use an absolute DB address such as
DB14.DBX0.0 or DB14.DBD2
```

Fix every validation error before attempting PLC communication.
