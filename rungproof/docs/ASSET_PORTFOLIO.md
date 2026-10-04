# RungProof Native Asset Portfolio

The native portfolio is the authoritative reusable equipment library for the
VM-safe isometric renderer. Each asset has two linked parts:

1. `tools/native_asset_library.py` — renderer-neutral geometry with fabrication
   cues, mounting/support topology, guarded moving parts, and readable sensor
   surfaces.
2. `tools/native_asset_catalog.py` — a typed symbolic control contract. It
   describes commands, feedback, units, and interlocks without PLC addresses.

The portfolio currently covers 50 distinct renderable asset types. The first
21 remain available, and the enterprise expansion adds:

- drives: inline helical gearmotor;
- material handling: slider-bed belt conveyor and twin-chain pallet conveyor;
- pneumatics/robotics: ISO profile cylinder and parallel gripper;
- loads: four-way pallet and stackable industrial tote;
- bulk process: hopper and vertical storage silo;
- machine safety: modular fence, interlocked gate, and safety light curtain;
- sensing: M18 inductive proximity sensor;
- electrical: floor-standing control panel and VFD cabinet.
- utilities: rotary-screw compressor, air receiver, desiccant dryer, and
  hydraulic power unit;
- process: plate heat exchanger and top-entry mixer/agitator;
- inspection: platform scale, fixed barcode scanner, and smart vision camera;
- advanced handling: pop-up transfer, conveyor turntable, vertical lift,
  swing-arm diverter, and autonomous mobile robot.

These are separate geometry builders, not labels applied to the same mesh.
Each has an independent approval ID, manufacturer/topology reference, camera
span, category, search tags, and symbolic control contract.

## Modeling direction informed by Visual Components

The [Visual Components workflow](https://www.visualcomponents.com/see-how-it-works/)
and [eCatalog](https://www.visualcomponents.com/ecatalog/#/) establish useful
product expectations: assets should be ready to place, configurable, reusable
across layouts, and able to participate in process simulation before a live
controller is connected. The public eCatalog describes a large library of
pre-defined, ready-to-use components with plug-and-play use; RungProof will
apply the same product pattern at a smaller, controls-training scale.

That means each RungProof asset is being developed as a catalog entry with:

- a visual envelope and mounting/support topology;
- validated parameters and material variants;
- explicit motion axes and safe travel limits;
- typed symbolic commands, feedback, and interlocks;
- an inspection/review card before it is used in a training scene.

The catalog can be queried by free text or category through
`search_asset_catalog()`. Current categories include drives,
material-handling, loads, sensors, operator-controls, process, pneumatics,
robotics, safety, electrical, machines, and access equipment.

This is the important distinction between a reusable equipment asset and a
decorative mesh. The asset can be placed in a layout and connected to a plant
runtime, while real PLC addresses remain in the separately guarded binding
configuration.

## Control contract rule

Asset contracts are symbolic only. A scene may bind a point name to an asset
action, but `%I`, `%Q`, DB numbers, byte offsets, PLC IP addresses, and
transport behavior remain outside the asset and scene model. The guarded live
adapter is the only place that can authorize a real controller exchange.

Commands use `PLC -> plant`; feedback uses `plant -> PLC`. The catalog is
validated at import time and by `tools/test_native_asset_catalog.py`.

## Visual quality pass

The native raster renderer now uses 24 radial segments for cylinders, tubes,
and frustums, plus 24x12 sphere tessellation for articulated joints. This is a
measured, centralized quality floor for every asset and keeps the VM-safe
renderer architecture unchanged. Geometry remains intentionally authored from
validated primitives; these are not manufacturer CAD files and reference links
are used for topology/proportion review only.

The generated 50-card approval set is written to
`build/asset-review-20260916-enterprise-50`. The generator explicitly reports
`PLC_CONNECTION_ATTEMPTED: FALSE`.

The next catalog tranche should cover utilities and process equipment
(compressors, dryers, air receivers, hydraulic power units, heat exchangers,
mixers, boilers, chillers), warehouse automation (turntables, transfers,
diverters, lifts, AS/RS, AMRs), and additional sensors. Each must meet the same
geometry, controls, catalog, and screenshot-review gates before inclusion.
