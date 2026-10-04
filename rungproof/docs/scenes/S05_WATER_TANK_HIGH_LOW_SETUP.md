# S05 - Water Tank - High/Low Switches

## Status and scope

- Native visual approval: **Pending**
- Native behavior/runtime: **Not created**
- Native PLC profile: **Not created**
- Source contract: `prototype/scenes/tank-high-low.json`
- Player mode: **Visual review only; all PLC and playback commands disabled**

## Purpose

Prove a discrete tank-level exercise using separate low and high point switches
without an analog or radar transmitter.

## Equipment and physical topology

| Equipment | Setup requirement |
| --- | --- |
| Water tank T-201 | Freestanding tank with a full-height level sight indication. |
| Inlet pump P-201 | Pump connected to the tank inlet riser and top header. |
| Drain piping | Low outlet connected to the drain path. |
| LSL-201 | Discrete low switch at 25% elevation. |
| LSH-201 | Discrete high switch at 75% elevation. |
| Local stations | Separate pump and drain stations outside the process envelope. |
| Stacklight | Status light clear of the vessel and piping. |

The scene intentionally has no analog level transmitter and no radar sensor.

## Source behavior

1. Initial level is 50%; pump and drain commands are FALSE; both discrete
   switches are inactive.
2. With the scene running, `inlet_pump_run` raises level at 8% of span per
   second.
3. With the scene running, `drain_valve_open` lowers level at 6% of span per
   second.
4. If both commands are TRUE, the net level rate is +2% of span per second.
5. `low_level_switch` is TRUE at or below 25%.
6. `high_level_switch` is TRUE at or above 75%.
7. Level is clamped to 0-100%.

## Point contract

| Point | Type | Owner | Initial | Intended use |
| --- | --- | --- | --- | --- |
| `inlet_pump_run` | BOOL | PLC | FALSE | PLC-owned inlet-pump command. |
| `drain_valve_open` | BOOL | PLC | FALSE | PLC-owned drain-valve command. |
| `tank_level` | REAL | SIM | 50% | Internal process level. |
| `low_level_switch` | BOOL | PC | FALSE | Simulator-owned low-level switch feedback. |
| `high_level_switch` | BOOL | PC | FALSE | Simulator-owned high-level switch feedback. |

## Initial-state and process settings

- Initial level: 50%
- Inlet rate: 0.08 fraction/s
- Outlet rate: 0.06 fraction/s
- Low threshold: 25%
- High threshold: 75%

## PLC profile and addressing

No native PLC profile or absolute address map exists for S05. Do not reuse the
Scene 2 DB14 mapping. Connect and Test PLC must remain disabled. A dedicated
future profile must preserve PC/PLC ownership and contain only the points
listed above.

## Player review procedure

1. Select `S05 - Water Tank - High/Low Switches` in the scene playlist.
2. Confirm the tank visibly indicates 50% level.
3. Confirm LSL-201 and LSH-201 are separate devices at low and high elevations.
4. Confirm there is no analog or radar transmitter.
5. Orbit to inspect pump/piping connections and clipping around the vessel.
6. Confirm all PLC and playback commands are disabled.

## Acceptance criteria

- The discrete-only purpose is immediately readable.
- The two switches are at distinct elevations and outside the tank shell.
- The tank fill level is visually readable.
- The inlet and outlet topology forms credible connected flow paths.
- No live PLC action is exposed without a dedicated profile.

Likely failure symptoms are an extra transmitter, switches at the same height,
hidden liquid indication, disconnected piping, or enabled PLC controls.

## Bench PLC assignment and operation guide

Complete `docs/PLC_BENCH_SETUP.md` first. S05 is an independent discrete tank
example and intentionally has no analog or radar tag.

Create or map these exact process names:

```text
inlet_pump_run      BOOL  PLC -> Simulator
drain_valve_open    BOOL  PLC -> Simulator
low_level_switch    BOOL  Simulator -> PLC
high_level_switch   BOOL  Simulator -> PLC
```

`tank_level` is internal simulator state. The simulator changes only the two
discrete switches at the documented thresholds. Test the ladder above and
below each threshold and confirm a missing command stops the modeled level.
