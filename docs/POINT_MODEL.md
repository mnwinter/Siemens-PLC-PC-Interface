# Typed digital and analog point model

The point model is the boundary between a future scene/process simulation and
the validated raw PLC tags. It is implemented and unit-tested offline. It does
not change the proven DB14 contract or the current typed-tag Snap7 transport.
Point-enabled configurations use schema version 2. The proven raw-tag DB14
configuration remains schema version 1.

## Layering

```text
Scene value
    |
Typed point: inversion, scaling, units, quality
    |
Configured tag: address, PLC type, ownership, raw safe value
    |
Dedicated standard-access simulation DB
```

Every point references one existing tag. The point inherits ownership from
that tag; direction is not repeated in the point configuration. This prevents
a point and its backing tag from declaring different writers.

Internal heartbeat tags cannot be exposed as scene points. One raw tag can be
used by only one point, preventing two scene objects from fighting over the
same PLC value.

## Digital point

```json
{
  "name": "simulated_photoeye",
  "kind": "digital",
  "tag": "simulated_photoeye_raw",
  "group": "conveyor_one",
  "inverted": false
}
```

Rules:

- the backing tag must be `BOOL`;
- `inverted` defaults to `false`;
- inversion is applied in both encode and decode directions;
- a PC-owned point's scene-facing safe state is decoded from the backing
  tag's required raw `safe_value`.

## Analog point

```json
{
  "name": "simulated_speed",
  "kind": "analog",
  "tag": "simulated_speed_raw",
  "group": "conveyor_one",
  "raw_min": 0,
  "raw_max": 27648,
  "engineering_min": 0,
  "engineering_max": 100,
  "unit": "percent",
  "out_of_range": "clamp"
}
```

Rules:

- the backing tag must be numeric;
- `raw_min` and `raw_max` must fit the backing PLC data type;
- `raw_min` must be less than `raw_max`;
- engineering limits must be finite and different;
- ascending and reverse-acting engineering ranges are supported;
- a PC-owned raw `safe_value` must lie inside the point's raw range;
- integer PLC values use half-away-from-zero rounding.

### Out-of-range policies

| Policy | Behavior | Diagnostic quality |
|---|---|---|
| `clamp` | Limits the value to the configured range | `clamped_low` or `clamped_high` |
| `fault` | Produces no writable raw value | `fault_low` or `fault_high` |

`fault` is the safer choice when silently clipping a process value would hide
a configuration or simulation error. The runtime refuses a point write when
the conversion produces a fault.

## Ownership and safe writes

`PointModel.encode_pc_value()` rejects PLC-owned points. The runtime's
`set_pc_point()` method converts a PC-owned scene value and then routes the raw
value through the existing `set_pc_value()` ownership and type checks.

The point model does not weaken the current safety boundary:

- no physical `%I` or `%Q` address is accepted;
- the runtime still requires explicit `--execute` authorization before PLC
  communication;
- heartbeat values remain internally generated;
- the PLC watchdog remains authoritative;
- safe shutdown still uses the backing tag's validated raw `safe_value`.

## Address grouping diagnostics

The configuration computes contiguous DB byte groups by DB number and
ownership. Groups never cross a PC/PLC ownership boundary.

`shares_byte_with_opposite_owner` identifies mixed-writer bytes such as DB14
byte 0, where `PC_To_PLC` and `PLC_To_PC` occupy adjacent bits. This is a
warning for the future block transport: a whole-byte write could overwrite a
PLC-owned bit. The current transport continues to use typed single-tag
operations and does not write address groups directly.

The offline `validate` command reports:

```text
DIGITAL_POINTS: 2
ANALOG_POINTS: 2
ADDRESS_GROUPS: 6
MIXED_OWNER_BYTE_GROUPS: 0
```

## Offline example

[`examples/typed-points.json`](../examples/typed-points.json) demonstrates
digital inputs/outputs, two analog scales, units, both out-of-range policies,
heartbeat tags, and ownership.

The example uses proposed `DB100` addresses and `192.168.0.1`. It has not been
downloaded to or tested against a PLC. Do not run it with `--execute` unless
the PLC DB and watchdog logic have been created to match it.

Validate it without connecting:

```powershell
siemens-plc-pc-interface validate .\examples\typed-points.json
```
