# Tank Level / 4–20 mA help

Scene ID: `tank-level`  
Migrated source: `prototype/scenes/tank-level.json`  
Scene contract: `res://scenes/migrated/tank-level.scene.json`

## Purpose

Run the scene, start the inlet pump, and open or close the drain. Fluid level, discrete low/high switches, and a linear 4–20 mA transmitter update together.

## Expected I/O to operate this scene

All entries below are symbolic scene points. They are not `%I`, `%Q`, DB, or hardware addresses. PC-owned points are simulator feedback; PLC-owned points are commands supplied by the controller; SIM points are internal and should not be wired as external I/O.

| Point | Type | Owner | Initial value |
| --- | --- | --- | --- |
| `inlet_pump_run` | `BOOL` | **PLC** | `False` |
| `drain_valve_open` | `BOOL` | **PLC** | `False` |
| `tank_level` | `REAL` | **SIM** | `42` |
| `level_transmitter` | `REAL` | **PC** | `10.72` |
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
| `drain_valve_open` | `drain_valve` | `position` |

## Expected equipment

| ID | Type | Label |
| --- | --- | --- |
| `process_tank` | `tank` | Process tank T-101 |
| `inlet_pump` | `pump` | Inlet pump P-101 |
| `inlet_pipe` | `pipe` | Tank inlet pipe |
| `outlet_pipe` | `pipe` | Tank outlet pipe |
| `drain_valve` | `valve` | Tank drain valve |
| `low_level_switch` | `levelSensor` | Low level switch LSL-101 |
| `high_level_switch` | `levelSensor` | High level switch LSH-101 |
| `level_transmitter` | `levelSensor` | Level transmitter LT-101 |
| `pump_station` | `switch` | Pump local station |
| `drain_station` | `switch` | Drain valve local station |
| `tank_stacklight` | `indicator` | Tank status light |

The low/high probes are mounted horizontally through sockets on the tank wall.
Their tips sit inside the vessel at the runtime's threshold elevations, measured
from the authored liquid/sight-glass range. This placement was checked in the
native Windows scene. Full operator dynamics remain an open review finding.
These visual sockets do not establish a rated pressure-vessel nozzle design.

The analog transmitter is mounted through a short roof socket, clear of the
central manway and guardrail. Its scene-specific sensing rod reaches the
modeled zero-level datum and covers the full liquid/sight-glass range. The
reusable asset is unchanged. Exterior placement was inspected in native
Windows views; internal placement was checked by transformed mesh bounds.
This custom virtual probe does not establish purchased-probe compatibility,
hardware calibration, or a rated pressure-vessel penetration.

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
