# Energy Meter help

Asset ID: `training.accessory.energy_meter.v1`  
Catalog status: **candidate / candidate**  
Category: `training/accessories`
Training requirement: `energy meter`
Generic basis asset: `process.dosing.skid.liquid-metering.v1`

## Purpose and integration boundary

This document is generated from the reusable asset catalog. It defines only the symbolic asset contract; it does not assign PLC addresses, DB offsets, safety ratings, or live commissioning behavior. Scene-level bindings determine PC/PLC/SIM ownership.
Copyright boundary: Generic training visual; no logo, trade dress, product number, or exact OEM claim.

## How to use this asset

1. Add the delivery model to a scene and position it using the documented physical envelope.
2. Bind only the declared signal names. Treat each name as a symbolic tag; assign actual PLC addresses, DB members, or HMI aliases only in the scene/integration contract.
3. Initialize command inputs to a known inactive state before enabling the scene. Read output signals as simulator feedback, not as proof of a real sensor or actuator.
4. If the asset declares kinematics, drive motion through its declared command signals and observe the declared feedback signals and axis limits.
5. Use the collision resource for interaction and placement checks. Do not use the visual mesh as a substitute for a safety envelope or certified guarding model.

## Physical envelope

- Width: 2.3 m
- Height: 1.9 m
- Depth: 1.5 m
- Source: `res://assets/training_accessories/energy_meter/source/energy_meter.blend`
- Delivery: `res://assets/training_accessories/energy_meter/delivery/energy_meter.glb`
- Collision: `res://assets/training_accessories/energy_meter/collision/energy_meter_collision.glb`
- Thumbnail: `res://assets/training_accessories/energy_meter/thumbnail.png`

## Expected reusable I/O

No reusable external signals are declared. Do not invent I/O for this passive asset.

Direction is the reusable asset direction only. An `input` is a command or demand supplied to the asset model; an `output` is feedback produced by the asset model. A scene binding must explicitly map each signal to a symbolic point and declare whether that point is PC-, PLC-, or simulator-owned. The signal list is the complete expected I/O for this catalog revision; an asset with no listed signals is passive and must not be assigned invented I/O.

## Kinematics


### Tag-by-tag use

This asset has no tags. It is used as geometry only; do not invent commands, feedback, or PLC addresses.

## Tag mapping checklist

- Preserve the catalog signal name when creating a scene binding so the asset contract remains traceable.
- Record the point owner explicitly: PC points are simulator feedback, PLC points are controller commands, and SIM points are internal model state.
- Keep units and data types unchanged at the asset boundary. Any scaling, inversion, debounce, timeout, or alarm policy belongs in the scene/controller contract and must be documented there.
- Do not infer a safety input, permissive, E-stop, interlock, or certified diagnostic from a similarly named tag.
| ID | Kind | Node | Range | Maximum rate |
| --- | --- | --- | --- | --- |
| `pump_rotation` | continuous | `KIN_metering_pump_shaft` | 0 to 360 deg | 1750 |

### Animation tags

| Tag ID | Node | Kind |
| --- | --- | --- |
| `pump_rotation` | `KIN_metering_pump_shaft` | continuous |

### Motion use and limits

Use only the declared axis ID and exported node path. The range and maximum rate are the simulator contract for this catalog revision; they are not a physical actuator stroke, pressure rating, acceleration limit, or commissioning value.
Motion is safe-model behavior only. Verify commanded direction, end-stop behavior, and feedback transitions in the scene before using the asset in a training sequence.

## Connectors

No reusable connector contract is declared.

## Admission status

This is a candidate asset. It is not approved for production use until its visual evidence, independent recognition review, and catalog quality gates pass.

## Verification record

- Topology reviewed: `True`
- Materials reviewed: `True`
- Scale reviewed: `True`
- Animation evidence recorded: `True`
- Blind recognition review: `inherited:blind-2026-09-30-authorized-review-image-123`
- Recognition confidence: `0.96`
- Evidence basis: `identical-delivery-independent-review`

These records document catalog/evidence checks. They do not certify the asset for a real machine, real PLC, electrical safety circuit, guarding, or production commissioning.

## Industrial reference basis

Generic reference family: **diaphragm liquid-metering skid**.
Source-model review: **compared-pass** — Compared against the registered generic basis family and the delivery model was verified byte-identical to the basis asset. Training-specific naming and scene placement remain generic; logos, trade dress, product numbers, and exact OEM claims are excluded.

| OEM source | Type | Accessed |
| --- | --- | --- |
| [Milton Roy: Series Process Diaphragm Pump](https://www.miltonroy.com/api/get-file?id=CONT05B4D727AFCC4FE9B73AF6B907AF68A1) | oem-datasheet | 2026-09-22 |

Modeled family features:
- motor/reducer
- diaphragm pump head
- dampener
- calibration column
- suction/discharge piping
- gauge
- local panel

Intentionally generic / not claimed:
- No Milton Roy mark, capacity, pressure, chemistry, materials, calibration, controls, containment, or certification is reproduced.
- The visual does not pump, meter, or contain a process chemical.
