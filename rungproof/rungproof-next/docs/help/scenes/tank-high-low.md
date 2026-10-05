# Water Tank — High/Low Switches help

Scene ID: `tank-high-low`  
Migrated source: `prototype/scenes/tank-high-low.json`  
Scene contract: `res://scenes/migrated/tank-high-low.scene.json`

## Purpose

A discrete level-control example with separate low and high point level switches. Run the scene, then operate the inlet pump and drain to cross each switch elevation.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `inlet_pump_run` | `BOOL` | **PLC** | `False` |
| `drain_valve_open` | `BOOL` | **PLC** | `False` |
| `tank_level` | `REAL` | **SIM** | `50` |
| `low_level_switch` | `BOOL` | **PC** | `False` |
| `high_level_switch` | `BOOL` | **PC** | `False` |

## Operator actions

| Action | Type | Bound point/sequence |
| --- | --- | --- |
| `Run simulated process` | `run` | `` |
| `Toggle inlet pump (simulated)` | `toggle` | `inlet_pump_run` |
| `Toggle drain valve (simulated)` | `toggle` | `drain_valve_open` |
| `Stop simulated process` | `stop` | `` |

## Equipment bindings

| Point | Equipment | Mode |
| --- | --- | --- |
| `drain_valve_open` | `hl_drain_valve` | `position` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `water_tank_hl` | `tank` | Water tank T-201 |
| `hl_inlet_pump` | `pump` | Water inlet pump P-201 |
| `hl_inlet_pipe` | `pipe` | Tank inlet pipe |
| `hl_outlet_pipe` | `pipe` | Tank outlet pipe |
| `hl_drain_valve` | `valve` | Tank drain valve |
| `hl_low_switch` | `levelSensor` | Low level switch LSL-201 |
| `hl_high_switch` | `levelSensor` | High level switch LSH-201 |
| `hl_pump_station` | `switch` | Pump local station |
| `hl_drain_station` | `switch` | Drain valve local station |
| `hl_stacklight` | `indicator` | Tank status light |

The low/high probes are mounted horizontally through sockets on the tank wall.
Their tips sit inside the vessel at the runtime's threshold elevations, measured
from the authored liquid/sight-glass range. This placement was checked in the
native Windows scene. Full operator dynamics remain an open review finding.
These visual sockets do not establish a rated pressure-vessel nozzle design.

The pump's upward discharge is connected through a riser and elbow to a
radial tank inlet. The outlet spool meets the delivered tank outlet flange.
Pipe supports reach the floor; a separate shoe supports the supply line.
The pump and inlet spool approach diagonally to clear the ladder. These two
lessons opt into `tankPiping`; installation uses the full delivered spool size,
not the legacy length/diameter fields. Reusable asset files are unchanged.
`FROM SUPPLY` and `TO DRAIN` mark external scene boundaries. The scene does not
model a supply vessel. A full-size quarter-turn drain valve is appended to the
outlet spool, with a mating flange and grounded shoes. `drain_valve_open` TRUE
puts its pointer parallel to the pipe; FALSE puts it perpendicular. This
indication follows the existing instantaneous drain command; it does not model
actuator travel time or add valve-position feedback. Reusable assets, level
calculation and point ownership remain unchanged. Both installations received
native five-angle and valve-focused inspections. An offline QA ladder program
was opened, verified and run through the normal Windows menus, with open/closed
pointer, Stop and Reset observations. These checks do not establish complete
process commissioning, hydraulics, fabrication ratings, or pipe stress.

## Stop and safety boundary

A normal Stop removes PLC-owned commands according to the scene runtime. This document does not prove a safety function, a real E-stop circuit, a PLC watchdog, or live-machine commissioning.
