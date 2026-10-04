# Destination Conveyor Bank help

Asset ID: `training.accessory.destination_conveyor_bank.v1`  
Catalog status: **candidate / candidate**  
Category: `training/accessories`
Training requirement: `destination conveyor bank`
Generic basis asset: `material-handling.belt-conveyor.600x6000.v1`

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

- Width: 6.2 m
- Height: 1.5 m
- Depth: 1.55 m
- Source: `res://assets/training_accessories/destination_conveyor_bank/source/destination_conveyor_bank.blend`
- Delivery: `res://assets/training_accessories/destination_conveyor_bank/delivery/destination_conveyor_bank.glb`
- Collision: `res://assets/training_accessories/destination_conveyor_bank/collision/destination_conveyor_bank_collision.glb`
- Thumbnail: `res://assets/training_accessories/destination_conveyor_bank/thumbnail.png`

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
| `belt_speed` | linear_continuous | `KIN_belt_surface` | -2.0 to 2.0 m/s | 0.75 |

### Animation tags

| Tag ID | Node | Kind |
| --- | --- | --- |
| `belt_speed` | `KIN_belt_surface` | linear_continuous |

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
- Blind recognition review: `inherited:codex-task-01a0ba41-c283-77a3-9ae9-1df82220f7a0`
- Recognition confidence: `0.98`
- Evidence basis: `identical-delivery-independent-review`

These records document catalog/evidence checks. They do not certify the asset for a real machine, real PLC, electrical safety circuit, guarding, or production commissioning.

## Industrial reference basis

Generic reference family: **600 mm flat-belt conveyor with support legs**.
Source-model review: **compared-pass** — Compared against the registered generic basis family and the delivery model was verified byte-identical to the basis asset. Training-specific naming and scene placement remain generic; logos, trade dress, product numbers, and exact OEM claims are excluded.

| OEM source | Type | Accessed |
| --- | --- | --- |
| [Dorner Conveyors: GAL-25-VUA Flat Belt Conveyor product page](https://www.dornerconveyors.com/europe/en/gal-ges/gal-25-vua-flat-belt-conveyor) | oem-product-page | 2026-09-22 |

Modeled family features:
- flat belt and end rollers
- side frame
- drive/end structure
- multiple adjustable support legs

Intentionally generic / not claimed:
- No Dorner mark, exact profile, drive option, belt construction, load capacity, electrical specification, or guarding configuration is reproduced.
- Motion and I/O remain scene-declared simulator behavior only.
