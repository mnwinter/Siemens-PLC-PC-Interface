# Bulk Powder Hopper help

Asset ID: `training.accessory.bulk_powder_hopper.v1`  
Catalog status: **candidate / candidate**  
Category: `training/accessories`
Training requirement: `bulk powder hopper`
Generic basis asset: `material-handling.hopper.bulk-slide-gate.v1`

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

- Width: 1.75 m
- Height: 1.45 m
- Depth: 2.05 m
- Source: `res://assets/training_accessories/bulk_powder_hopper/source/bulk_powder_hopper.blend`
- Delivery: `res://assets/training_accessories/bulk_powder_hopper/delivery/bulk_powder_hopper.glb`
- Collision: `res://assets/training_accessories/bulk_powder_hopper/collision/bulk_powder_hopper_collision.glb`
- Thumbnail: `res://assets/training_accessories/bulk_powder_hopper/thumbnail.png`

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
| `gate_position` | linear | `KIN_SLIDE_GATE` | 0 to 0.4 m | 0.35 |

### Animation tags

| Tag ID | Node | Kind |
| --- | --- | --- |
| `gate_position` | `KIN_SLIDE_GATE` | linear |

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
- Blind recognition review: `inherited:blind-2026-09-17-rerun-image-103`
- Recognition confidence: `0.91`
- Evidence basis: `identical-delivery-independent-review`

These records document catalog/evidence checks. They do not certify the asset for a real machine, real PLC, electrical safety circuit, guarding, or production commissioning.

## Industrial reference basis

Generic reference family: **gravity-discharge bulk hopper with slide-gate valve**.
Source-model review: **compared-pass** — Compared against the registered generic basis family and the delivery model was verified byte-identical to the basis asset. Training-specific naming and scene placement remain generic; logos, trade dress, product numbers, and exact OEM claims are excluded.

| OEM source | Type | Accessed |
| --- | --- | --- |
| [WAMGROUP: VIB-VIBX low profile slide valves](https://sepcom.wamgroup.com/pt-BR/SEPCOM/Product/VIB-VIBX/Valvulas-de-gaveta-de-baixo-perfil) | oem-product-page | 2026-09-22 |

Modeled family features:
- wide rectangular hopper
- converging hopper walls
- lower outlet
- transverse slide-gate blade
- support frame

Intentionally generic / not claimed:
- No WAMGROUP mark, material flow rate, hopper volume, material compatibility, valve size, seal, actuator, pressure, dust control, guard, or installation specification is reproduced.
- The illustrated gate never releases physical bulk material or creates a process-safety claim.
