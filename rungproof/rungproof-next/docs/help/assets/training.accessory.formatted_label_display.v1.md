# Formatted Label Display help

Asset ID: `training.accessory.formatted_label_display.v1`  
Catalog status: **candidate / candidate**  
Category: `training/accessories`
Training requirement: `formatted label display`
Generic basis asset: `controls.display.parking-occupancy.v1`

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

- Width: 1.1 m
- Height: 0.72 m
- Depth: 2.44 m
- Source: `res://assets/training_accessories/formatted_label_display/source/formatted_label_display.blend`
- Delivery: `res://assets/training_accessories/formatted_label_display/delivery/formatted_label_display.glb`
- Collision: `res://assets/training_accessories/formatted_label_display/collision/formatted_label_display_collision.glb`
- Thumbnail: `res://assets/training_accessories/formatted_label_display/thumbnail.png`

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
No animated axis is declared; the asset is static unless a future catalog revision adds a kinematic contract.

### Animation tags

No animation tags are declared; this asset is static in the reusable contract.

### Motion use and limits

No motion controls apply to this asset.

## Connectors

No reusable connector contract is declared.

## Admission status

This is a candidate asset. It is not approved for production use until its visual evidence, independent recognition review, and catalog quality gates pass.

## Verification record

- Topology reviewed: `True`
- Materials reviewed: `True`
- Scale reviewed: `True`
- Animation evidence recorded: `True`
- Blind recognition review: `inherited:blind-2026-09-30-parking-round1-image-128`
- Recognition confidence: `0.98`
- Evidence basis: `identical-delivery-independent-review`

These records document catalog/evidence checks. They do not certify the asset for a real machine, real PLC, electrical safety circuit, guarding, or production commissioning.

## Industrial reference basis

Generic reference family: **parking space-availability digital display**.
Source-model review: **compared-pass** — Compared against the registered generic basis family and the delivery model was verified byte-identical to the basis asset. Training-specific naming and scene placement remain generic; logos, trade dress, product numbers, and exact OEM claims are excluded.

| OEM source | Type | Accessed |
| --- | --- | --- |
| [Daktronics: DF-2053 drop-in space availability displays](https://www.daktronics.com/en-us/support/products/df-2053) | oem-product-page | 2026-09-30 |
| [Daktronics: DF-2053 product manual and reference shop drawings](https://www.daktronics.com/web-documents/manuals/dd1421948.pdf) | oem-manual | 2026-09-30 |

Modeled family features:
- freestanding support and base
- electronic display enclosure
- large numeric display area
- occupancy label
- open/full status indicators

Intentionally generic / not claimed:
- No Daktronics mark, digit technology, visibility range, enclosure rating, communications, count accuracy, or installation approval is reproduced.
- The count and status are symbolic simulator outputs only; the asset does not measure a parking facility.
