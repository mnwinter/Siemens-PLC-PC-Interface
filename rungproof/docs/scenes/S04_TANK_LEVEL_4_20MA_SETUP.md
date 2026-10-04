# S04 - Tank Level / 4-20 mA

## Status and scope

- Native visual approval: **Pending**
- Native behavior/runtime: **Not created**
- Native PLC profile: **Not created**
- Source contract: `prototype/scenes/tank-level.json`
- Player mode: **Visual review only; all PLC and playback commands disabled**

This document records the source-backed process and I/O contract. The native
player currently presents the equipment for visual review only.

## Purpose

Prove an analog tank-level example in which an inlet pump and drain change the
process level while low/high switches and a linear 4-20 mA transmitter follow
the same simulated liquid surface.

## Equipment and physical topology

| Equipment | Setup requirement |
| --- | --- |
| Process tank T-101 | Freestanding tank with a full-height level sight indication. |
| Inlet pump P-101 | Centrifugal pump connected to a vertical riser and top inlet header. |
| Outlet | Low tank outlet connected to drain piping. |
| LSL-101 / LSH-101 | Separate low and high point switches mounted at their process elevations. |
| LT-101 | Distinct analog level transmitter with a readable local display. |
| Local stations | Separate pump and drain command stations outside the piping envelope. |
| Stacklight | Tank status light located outside the vessel and piping envelope. |

## Source behavior

1. Initial level is 42%, both PLC commands are FALSE, both switches are
   inactive, and the transmitter is 10.72 mA.
2. With the scene running, `inlet_pump_run` raises level at 7% of span per
   second.
3. With the scene running, `drain_valve_open` lowers level at 4.5% of span per
   second.
4. If both commands are TRUE, the net level rate is +2.5% of span per second.
5. `low_level_switch` is TRUE at or below 20%; `high_level_switch` is TRUE at
   or above 80%.
6. The idealized signal is `level_transmitter = 4 + 16 x level_fraction` mA.
7. Level is clamped to 0-100%.

## Point contract

| Point | Type | Owner | Initial | Intended use |
| --- | --- | --- | --- | --- |
| `inlet_pump_run` | BOOL | PLC | FALSE | PLC-owned inlet-pump command. |
| `drain_valve_open` | BOOL | PLC | FALSE | PLC-owned drain-valve command. |
| `tank_level` | REAL | SIM | 42% | Internal process level. |
| `level_transmitter` | REAL | PC | 10.72 mA | Simulator-owned analog feedback to the PLC. |
| `low_level_switch` | BOOL | PC | FALSE | Simulator-owned low-level feedback. |
| `high_level_switch` | BOOL | PC | FALSE | Simulator-owned high-level feedback. |

## Initial-state and process settings

- Initial level: 42%
- Inlet rate: 0.07 fraction/s
- Outlet rate: 0.045 fraction/s
- Low threshold: 20%
- High threshold: 80%
- Transmitter range: 4-20 mA for 0-100%

## PLC profile and addressing

No native PLC profile or absolute address map exists for S04. Scene 2 DB14 is
not compatible and must not be reused. Connect and Test PLC remain disabled in
this review entry. A future profile must define the two PLC-owned BOOL commands
and the three PC-owned feedback values with explicit addresses and types.

## Player review procedure

1. Select `S04 - Tank Level / 4-20 mA` in the scene playlist.
2. Confirm the 42% liquid indication is visible for the height of the tank.
3. Orbit the scene and confirm the pump is physically connected to the inlet
   riser/header and the outlet is connected to the drain pipe.
4. Verify low/high switches are at distinct elevations and LT-101 is visually
   distinct from them.
5. Check for vessel, pipe, sensor, and station clipping.
6. Confirm all PLC and playback commands are disabled.

## Acceptance criteria

- Tank fill level is readable without relying only on text.
- Pump, inlet riser, top header, vessel, and drain form a credible flow path.
- Point sensors and analog transmitter do not overlap the vessel shell.
- No Scene 2 PLC mapping is available from this review entry.

Likely failure symptoms are hidden liquid level, disconnected piping, a sensor
buried in the shell, or enabled PLC controls.

## Bench PLC assignment and operation guide

Complete `docs/PLC_BENCH_SETUP.md` first. S04 is an independent tank example;
it does not inherit S03 conveyor tags or Scene 2 process mappings.

Create or map these exact process names:

```text
inlet_pump_run      BOOL  PLC -> Simulator
drain_valve_open    BOOL  PLC -> Simulator
level_transmitter   REAL  Simulator -> PLC
low_level_switch    BOOL  Simulator -> PLC
high_level_switch   BOOL  Simulator -> PLC
```

`tank_level` is internal simulator state. The PLC commands the pump and drain;
the simulator derives both switches and the 4-20 mA signal from one liquid
surface. No simulator logic may turn on a pump or valve when its PLC command is
FALSE. Monitor both commands, all three feedback points, `tank_level`, and the
watchdog while testing.
