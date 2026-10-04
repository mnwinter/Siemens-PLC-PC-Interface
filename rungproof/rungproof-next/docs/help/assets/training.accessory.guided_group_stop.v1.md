# Guided Group Stop help

Asset ID: `training.accessory.guided_group_stop.v1`  
Catalog status: **candidate / candidate**  
Category: `training/accessories`
Training requirement: `guided group stop`
Generic basis asset: `actuation.pneumatic.cylinder.guided.v1`

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

- Width: 1.05 m
- Height: 0.82 m
- Depth: 0.88 m
- Source: `res://assets/training_accessories/guided_group_stop/source/guided_group_stop.blend`
- Delivery: `res://assets/training_accessories/guided_group_stop/delivery/guided_group_stop.glb`
- Collision: `res://assets/training_accessories/guided_group_stop/collision/guided_group_stop_collision.glb`
- Thumbnail: `res://assets/training_accessories/guided_group_stop/thumbnail.png`

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
| `tool_plate_travel` | linear | `KIN_TOOL_PLATE` | 0 to 0.55 m | 0.8 |

### Animation tags

| Tag ID | Node | Kind |
| --- | --- | --- |
| `tool_plate_travel` | `KIN_TOOL_PLATE` | linear |

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
- Blind recognition review: `inherited:blind-2026-09-17-rerun-image-079`
- Recognition confidence: `0.88`
- Evidence basis: `identical-delivery-independent-review`

These records document catalog/evidence checks. They do not certify the asset for a real machine, real PLC, electrical safety circuit, guarding, or production commissioning.

## Industrial reference basis

Generic reference family: **compact guided pneumatic cylinder with internal guide shafts**.
Source-model review: **compared-pass** — Compared against the registered generic basis family and the delivery model was verified byte-identical to the basis asset. Training-specific naming and scene placement remain generic; logos, trade dress, product numbers, and exact OEM claims are excluded.

| OEM source | Type | Accessed |
| --- | --- | --- |
| [SMC: MGP standard guided cylinder](https://www.smcusa.com/products/pneumatic-actuators/guided-actuators/heavy-duty/internal-guide-shaft/standard-guided-cylinder-mgp~137432) | oem-product-page | 2026-09-22 |

Modeled family features:
- compact guide body
- twin guide shafts
- moving plate
- piston rod
- port fittings
- mounting base

Intentionally generic / not claimed:
- No SMC mark, bore, stroke, bearing type, load rating, cushion, port, sensor, or pressure specification is reproduced.
- Guided travel is visual-only simulator kinematics and carries no physical-motion claim.
