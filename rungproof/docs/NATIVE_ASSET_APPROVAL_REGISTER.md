# Native asset approval register

This register is the acceptance gate for rebuilding the RungProof native asset
library. Every asset is modeled from the selected real-world topology below,
rendered by the VM-safe isometric renderer, and reviewed independently before
it may be used to rebuild a scene.

Approval states:

- `PENDING`: rebuilt asset is not yet approved by Matt;
- `APPROVED`: acceptable for use in native scenes;
- `REVISE`: do not use in scenes until the recorded issue is corrected.

| ID | Native asset | Selected topology and required visible features | Primary reference | Status |
|---|---|---|---|---|
| A01 | AC motor | IEC/NEMA foot-mounted induction motor; axial cooling fins without circumferential banding, shaft, end bells, fan cover, terminal box, four mounting feet | [Siemens SIMOTICS GP/SD](https://cache.industry.siemens.com/dl/files/197/109749197/att_1122986/v1/Motors-D81-1-complete-English-12-2022.pdf) | PENDING |
| A02 | Conveyor | End-driven roller conveyor; two side rails, crossmembers, rollers contained inside both channels with hidden assembled end caps, legs/feet, guarded shaft coupling, bracket-mounted gearbox and motor on the discharge roller axis | [Dorner 2200 end drive](https://www.dornerconveyors.com/europe/products/2200-series/2200-belted-conveyor/flat-belt-end-drive) | PENDING |
| A03 | Product carton | FEFCO 0201 regular slotted corrugated case; visible top seam and sealing tape | [FEFCO regular slotted case](https://www.fefco.org/node/656) | PENDING |
| A04 | Through-beam photoeye | Separate sender and receiver housings, opposed lenses, mounting brackets/posts, visible beam path | [SICK W4 WSE4-3](https://www.sick.com/media/pdf/5/85/085/dataSheet_WSE4-3P2130_1028163_en.pdf) | PENDING |
| A05 | Operator pushbutton | 22 mm round panel operator in a small station; bezel, colored cap, enclosure and mounting stem | [Allen-Bradley 800F](https://www.rockwellautomation.com/en-us/products/hardware/push-buttons-and-signaling-devices/800f-round-push-buttons.html) | PENDING |
| A06 | Stacklight | Pole/base-mounted modular red/amber/green LED tower with distinct lens modules and top cap | [PATLITE LR series](https://shop.patlite.com/Articles.asp?=&ID=266) | PENDING |
| A07 | Centrifugal pump | Close-coupled end-suction pump; axial suction, radial discharge, volute, motor stool, motor and supported feet | [Grundfos NB/NBE](https://www.grundfos.com/au/learn/ecademy/all-courses/grundfos-end-suction-pumps/introduction-to-end-suction-pumps) | PENDING |
| A08 | Industrial axial fan | Open tubular inline housing and flanges; six visible axial impeller blades, hub, supports and external drive detail | [Greenheck TBI-CA](https://www.greenheck.com/products/fans/inline/tbi-ca) | PENDING |
| A09 | Pneumatic pusher | ISO 15552 profile cylinder; barrel, end caps, ports, piston rod, mounting brackets and pusher plate | [Festo DSBC](https://festo.com/rep/en-us_us/assets/pdf/Standard_Cylinders_DSBC.pdf) | PENDING |
| A10 | Process tank | Vertical stainless vessel with dished top/bottom, adjustable legs/feet, top nozzle/vent, side outlet, access cover, and full-height external segmented sight gauge showing approximately 60% liquid | [Alfa Laval tank equipment](https://www.alfalaval.com/products/process-solutions/brewery-solutions/tank-top-systems/) | PENDING |
| A11 | Point level switch | Side-mounted stainless point sensor with threaded process connection, short wetted tip, body and M12 connector | [ifm LMT/LM series](https://www.ifm.com/in/en/shared/products/level/lm/point-level-detection) | PENDING |
| A12 | Radar level transmitter | Top-mounted non-contact radar transmitter; process flange, antenna/nozzle, electronics housing, display and measurement cone | [VEGA VEGAPULS](https://www.vega.com/en-us/products/product-catalog/level/radar/vegapuls-67) | PENDING |
| A13 | Flanged process pipe | Pipe spool with raised-face end flanges, visible bolt circle and support saddle | [ASME B16.5](https://www.asme.org/codes-standards/find-codes-standards/b16-5-pipe-flanges-flanged-fittings-nps-1-2-nps-24-metric-inch-standard/2025) | PENDING |
| A14 | Rotary selector | 22 mm three-position selector; round metal bezel, black short lever, enclosure and position witness marks | [Allen-Bradley 800F selector](https://www.rockwellautomation.com/en-us/products/details.800FM-HR32CR.html) | PENDING |
| A15 | Scissor lift table | Base frame, crossed scissor arms with center pivots, hydraulic cylinder, and supported top platform with verified mechanism-to-platform clearance | [Southworth lift tables](https://www.southworthproducts.com/scissor-lift-tables/) | PENDING |
| A16 | Butterfly valve | Cutaway wafer/lug body between flanges with an open bore, visible internal disc, stem/neck, and manual lever | [Bray Series 3-Cx](https://www.bray.com/cx-line/3-cx-resilient-seated-butterfly-valve) | PENDING |
| A17 | Floor drill press | Anchored base, separated column and T-slot table, head/belt guard, motor, non-overlapping quill/spindle/chuck/bit chain, and outward feed handles | [Clausing 2277](https://clausing-industrial.com/product/2277/) | PENDING |
| A18 | Six-axis robot | Pedestal-mounted articulated arm with spherical shoulder/elbow/wrist joints, links terminating at joint housings, tool flange, and protected cable covers | [FANUC M-20iD/25](https://www.fanucamerica.com/products/robot/m-20id-25) | PENDING |
| A19 | High-speed roller shutter | Side columns, top roll/header, fabric curtain, bottom bar, side-mounted geared operator and control box | [Rytec Fast-Seal](https://www.rytecdoors.com/high-performance-doors/fabric-doors/fast-seal) | PENDING |
| A20 | Rotary indexing table | Low rigid housing, circular rotary plate, center opening, mounting pattern and side-mounted gearmotor | [WEISS Generation 5 CR-N](https://gen5.weiss-world.com/en-us/) | PENDING |
| A21 | Enclosed process machine | Full-height guarded CNC-style enclosure; front doors, viewing windows, base/coolant plinth, control pendant and stacklight | [Haas VF-2](https://www.haascnc.com/machines/vertical-mills/vf-series/models/small/vf-2.html) | PENDING |

## Review round 1 corrections

Matt rejected A01, A02, A15-A18 and identified additional fan and tank issues.
The screenshot labels establish that the referenced fan is A08 (not A20) and
the referenced tank is A10 (not A22). The regenerated cards incorporate:

- A01: axial fins replace the false circumferential motor banding;
- A02: roller barrels have at least 0.24 world-unit clearance to both rail
  inner faces, and hidden assembled end caps are not painted through either
  channel;
- A08: the housing and flanges are hollow tubes with six visible blades;
- A10: a full-height ten-segment external sight gauge shows six filled and four
  empty segments without a single large face that can sort through the tank;
- A15: the scissor mechanism clears the platform underside;
- A16: an intentional transparent cutaway exposes the disc inside the wafer
  body and large-bore adjoining pipework;
- A17: the table clears the column, the tooling chain does not intersect, and
  three outward feed handles remain outside the head casting;
- A18: shoulder, elbow, and wrist joints are faceted spheres, with shortened
  links and cable covers that terminate before the joint centers.

All corrected assets return to `PENDING` for Matt's next visual review. No
correction is treated as approved automatically.

## Rejected review round 2 A02 occlusion correction

Matt found that suppressing the roller end caps did not fully correct A02:
individual roller side polygons still alternated in front of and behind the
back rail. The physical dimensions were valid, but average-depth face sorting
made the assembled conveyor read like an M. C. Escher drawing.

A02 temporarily used an explicit fixed assembly render order in both the
isolated review asset and native Scene 2:

- roller barrels and crossmembers render first;
- both side channels rendered after every roller face;
- the attached shaft, coupling guard, bearing, gearbox, bracket, and gearmotor
  render after the channels so the real discharge-end drive connection remains
  visible;
- Scene 2 payload geometry renders above the rail assembly so a carton cannot
  be visually sliced by the back rail.

Matt rejected that result because the back channel was consequently drawn over
the rollers even though it is physically farther from the camera. The fixed
same-layer treatment is superseded by review round 3 below.

## Review round 3 A02 camera-aware rail correction

The renderer now classifies the two conveyor channels from the active orbit
camera and enforces the physical order:

- back channel first;
- roller bed and payload second;
- front channel third;
- attached discharge-end drive last.

This relationship is verified at the minimum, default, and maximum supported
orbit yaw angles. The same sorter drives both the isolated approval card and
native Scene 2, so the back rail stays behind the rollers while the front rail
masks their near ends. A02 remains `PENDING` for Matt's explicit approval.

## Scene migration gate

No legacy scene is considered recreated merely because its JSON still exists.
A native scene may move to acceptance only when:

1. every asset type it uses is `APPROVED`;
2. the native renderer consumes the renderer-neutral scene definition;
3. its deterministic PLC/plant behavior tests still pass;
4. the scene is captured and visually reviewed in the packaged VM renderer;
5. local automated verification reports `PLC_CONNECTION_ATTEMPTED: FALSE`.

The last item describes this development machine's network boundary, not a ban
on PLC testing. The PLC has no connected field I/O, and communication testing
is acceptable after Matt transfers a build to the VM that can reach the
controls network. A VM communication test remains an explicit operator action,
separate from offline automation.

## Native scene review batch 1 - S03 through S06

Matt directed work to proceed with the next four scenes in the actual built-in
source order after native Scene 2. These are now complete native geometry
compositions in the VM-safe review renderer:

| ID | Source scene | Native review content | Status |
|---|---|---|---|
| S03 | Conveyor Inspection Cell | End-driven roller conveyor, three cartons, opposed through-beam photoeye outside the channels, operator station, and stacklight | PENDING |
| S04 | Tank Level / 4-20 mA | Connected inlet pump/riser/header, process tank at 42%, low/high point switches, analog transmitter, outlet piping, stations, and stacklight | PENDING |
| S05 | Water Tank - High/Low Switches | Connected pump and piping, tank at 50%, discrete low/high switches, stations, and stacklight; no analog or radar transmitter | PENDING |
| S06 | Water Tank - Radar Level | Connected pump and piping, tank at 35%, top-mounted radar, one tapered measurement frustum terminating at the liquid surface, stations, and stacklight | PENDING |

The composed conveyor retains the camera-aware rule for every placed conveyor
instance: back rail, roller bed/payload, front rail, attached end drive. Tank
level remains readable through the full-height external sight gauge. The radar
measurement volume is an intentional process visualization, not physical pipe.

These are scene-layout approval compositions. Their existing source behavior
and tag contracts remain validated, but they are not presented as new live PLC
sessions: only Scene 2 currently has an approved native DB14 profile and
`NativePlcSession`. No fallback to another scene's PLC profile is permitted.

## Legacy scene inventory

The source library contains 32 scene documents. They are inventoried now, but
native scene recreation is intentionally waiting for the asset approvals above.

| Source scene | Required asset types | Native migration status |
|---|---|---|
| Conveyor Inspection Cell | box, conveyor, indicator, photoeye, switch | S03 NATIVE REVIEW PENDING |
| Reusable Equipment Gallery | box, conveyor, drillPress, fan, indicator, levelSensor, liftTable, machine, motor, photoeye, pipe, pump, robotArm, rollerShutter, rotarySwitch, rotaryTable, switch, tank, valve | WAITING FOR ASSET APPROVAL |
| Lab 2.1 - Workstation Call Lamp | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.2 - Dual Confirmation Lamp | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.3 - Service Marker Inhibit | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.4 - Two-Station Call Beacon | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.5 - Bay Light Selector | indicator, rotarySwitch | WAITING FOR ASSET APPROVAL |
| Lab 2.6 - Ready / Attention Button | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.7 - Dual-Contact Permissive | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.8 - Inspection Vote Stacklight | indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.9 - Maintenance Beacon Selector | indicator, rotarySwitch | WAITING FOR ASSET APPROVAL |
| Lab 2.10 - Dust Collector Seal-In | fan, indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.11 - Inbound Tote Stop | box, conveyor, indicator, photoeye, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.12 - Ergonomic Assembly Lift | box, indicator, liftTable, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.13 - Coolant Jug Filling Cell | box, conveyor, indicator, machine, photoeye, switch, valve | WAITING FOR ASSET APPROVAL |
| Lab 2.14 - Sump Dewatering Pump | indicator, levelSensor, pipe, pump, switch, tank | WAITING FOR ASSET APPROVAL |
| Lab 2.15 - Weld Fume Extractor | fan, indicator, rotarySwitch, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.16 - Fixture-Safe Drill Station | box, drillPress, indicator, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.17 - Twin-Container Pallet Cell | box, conveyor, indicator, machine, photoeye, robotArm, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.18 - Shipping Pallet Accumulation | box, conveyor, indicator, photoeye, rotarySwitch, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.19 - Service Door Shutter | indicator, rollerShutter, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.20 - Bottle Shuttle Conveyor | box, conveyor, indicator, photoeye, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.21 - Chemical Tote Finishing Line | box, conveyor, indicator, machine, switch, valve | WAITING FOR ASSET APPROVAL |
| Lab 2.22 - Dual-Spindle Plate Cell | box, drillPress, indicator, pusher, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.23 - Parcel Size Sorter | box, conveyor, indicator, photoeye, rotaryTable, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.24 - Robot CNC Tending Cell | box, conveyor, indicator, machine, photoeye, robotArm, switch | WAITING FOR ASSET APPROVAL |
| Lab 2.25 - Inspection Light Toggle | indicator, switch | WAITING FOR ASSET APPROVAL |
| Scene 1 — Conveyor Stop | box, conveyor, indicator, photoeye, switch | WAITING FOR ASSET APPROVAL |
| Scene 2 — Conveyor Pusher | box, conveyor, indicator, photoeye, pusher, switch | WAITING FOR ASSET APPROVAL |
| Water Tank — High/Low Switches | indicator, levelSensor, pipe, pump, switch, tank | S05 NATIVE REVIEW PENDING |
| Tank Level / 4–20 mA | indicator, levelSensor, pipe, pump, switch, tank | S04 NATIVE REVIEW PENDING |
| Water Tank — Radar Level | indicator, pipe, pump, radarLevelSensor, switch, tank | S06 NATIVE REVIEW PENDING |
