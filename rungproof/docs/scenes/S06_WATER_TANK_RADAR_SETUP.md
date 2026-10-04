# S06 - Water Tank - Radar Level

## Status and scope

- Native visual approval: **Pending**
- Native behavior/runtime: **Not created**
- Native PLC profile: **Not created**
- Source contract: `prototype/scenes/tank-radar.json`
- Player mode: **Visual review only; all PLC and playback commands disabled**

## Purpose

Prove a non-contact radar level example in which level percent, antenna-to-
surface distance, idealized 4-20 mA signal, and echo health describe one liquid
surface.

## Equipment and physical topology

| Equipment | Setup requirement |
| --- | --- |
| Water tank T-301 | Freestanding tank with a full-height level sight indication. |
| Inlet pump P-301 | Pump connected to inlet riser and top tank header. |
| Drain piping | Low outlet connected to drain piping. |
| LT-301 radar | Transmitter mounted over the vessel with antenna aimed down at the liquid. |
| Measurement volume | One tapered cone/frustum from antenna to liquid surface, not stepped pipe-like cylinders. |
| Local stations | Separate pump and drain stations outside the process envelope. |
| Stacklight | Status light clear of vessel and piping. |

## Source behavior

1. Initial level is 35%; pump and drain commands are FALSE; radar echo is good.
2. With the scene running, `inlet_pump_run` raises level at 7% of span per
   second.
3. With the scene running, `drain_valve_open` lowers level at 4.5% of span per
   second.
4. If both commands are TRUE, the net level rate is +2.5% of span per second.
5. `radar_level` follows tank level in percent.
6. `radar_signal = 4 + 16 x level_fraction` mA.
7. `radar_distance` is the modeled antenna-apex-to-liquid-surface distance,
   clamped to a minimum of 0.08 m. The source initial value is 2.754 m.
8. `radar_echo_ok` is TRUE in the current idealized source model.
9. Level is clamped to 0-100%.

## Point contract

| Point | Type | Owner | Initial | Intended use |
| --- | --- | --- | --- | --- |
| `inlet_pump_run` | BOOL | PLC | FALSE | PLC-owned inlet-pump command. |
| `drain_valve_open` | BOOL | PLC | FALSE | PLC-owned drain-valve command. |
| `tank_level` | REAL | SIM | 35% | Internal process level. |
| `radar_level` | REAL | PC | 35% | Simulator-owned radar level feedback. |
| `radar_distance` | REAL | PC | 2.754 m | Simulator-owned antenna-to-surface distance. |
| `radar_signal` | REAL | PC | 9.6 mA | Simulator-owned idealized analog signal. |
| `radar_echo_ok` | BOOL | PC | TRUE | Simulator-owned echo-health feedback. |

## Initial-state and process settings

- Initial level: 35%
- Inlet rate: 0.07 fraction/s
- Outlet rate: 0.045 fraction/s
- Initial radar distance: 2.754 m
- Initial radar signal: 9.6 mA
- Echo health: TRUE

## PLC profile and addressing

No native PLC profile or absolute address map exists for S06. Scene 2 DB14 is
not compatible and must not be reused. Connect and Test PLC remain disabled in
the review entry. Any later profile must type and map all four PC-owned radar
feedback points explicitly.

## Player review procedure

1. Select `S06 - Water Tank - Radar Level` in the scene playlist.
2. Confirm the tank visibly indicates 35% level.
3. Confirm LT-301 is top-mounted and aimed down into the vessel.
4. Confirm one tapered measurement cone ends at the liquid surface and does
   not look like piping.
5. Orbit to inspect the transmitter, vessel, pump, piping, and stations for
   clipping.
6. Confirm all PLC and playback commands are disabled.

## Acceptance criteria

- Radar transmitter and non-contact measurement path are immediately readable.
- Measurement cone terminates at the same surface shown by the level indicator.
- The cone is a tapered volume, not a stepped cylinder or solid pipe.
- Pump, inlet, vessel, and drain form a credible connected process path.
- No live PLC operation is exposed without a dedicated S06 profile.

Likely failure symptoms are a pipe-like radar beam, beam ending above or below
the shown liquid, hidden level, transmitter clipping, or enabled PLC controls.

## Bench PLC assignment and operation guide

Complete `docs/PLC_BENCH_SETUP.md` first. S06 is an independent radar
instrumentation example and does not inherit S04 analog or S05 discrete-only
assumptions.

Create or map these exact process names:

```text
inlet_pump_run      BOOL  PLC -> Simulator
drain_valve_open    BOOL  PLC -> Simulator
radar_level         REAL  Simulator -> PLC
radar_distance      REAL  Simulator -> PLC
radar_signal        REAL  Simulator -> PLC
radar_echo_ok       BOOL  Simulator -> PLC
```

`tank_level` is internal simulator state. The pump and drain move one liquid
surface; level rises, radar distance falls, signal follows the idealized
4-20 mA relationship, and echo health reports the actual configured feedback.
The simulator must not fabricate a good echo when feedback is missing or stale.
