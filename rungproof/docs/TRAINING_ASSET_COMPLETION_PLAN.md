# Training asset package completion plan

This checklist tracks the full asset-package standard for the visual training
labs. The current simulator scenes contain reusable static training geometry,
but that is not by itself a complete production asset package.

## Scope

- [ ] Inventory every lesson-specific asset used by the 70 training labs.
- [ ] Assign every asset a stable catalog ID and display name.
- [ ] Keep the asset generic and copyright-safe; do not reproduce logos, trade
      dress, product numbers, or book diagrams.

## Model and runtime contract

- [ ] Provide a standalone source model for every catalog asset.
- [ ] Provide a standalone delivery model for every catalog asset.
- [ ] Provide a collision model where placement or interaction requires one.
- [ ] Record a 1:1 physical envelope in meters.
- [ ] Record connectors, mounting interfaces, and declared passive/commandable
      behavior.
- [ ] Record every kinematic node, travel/range, and maximum rate.
- [ ] Verify that visual, collision, and kinematic data agree.

## Provenance and copyright boundary

- [ ] Add an industrial-reference record for every candidate asset.
- [ ] Record the generic equipment family and the features used as modeling
      guidance.
- [ ] Record what was deliberately generalized or omitted.
- [ ] Keep reference material separate from claims about ratings, safety,
      dimensions, wiring, certification, or live behavior.

## Help and scene documentation

- [ ] Generate one help file for every catalog asset.
- [ ] Generate one help file for every migrated/training scene.
- [ ] Include only declared signals, types, directions, units, kinematics,
      connectors, bounds, bindings, and safe-state behavior.
- [ ] Validate that help files contain the complete authoritative contracts.

## Review evidence

- [ ] Produce hero, side, mechanism, opposite-end, underside, and alignment
      views for every asset where those views apply.
- [ ] Produce a context-free blind-recognition image.
- [ ] Produce a wireframe/topology image.
- [ ] Produce a scale-reference image.
- [ ] Produce animated-state images for each kinematic axis.
- [ ] Write a visual review record with defects, corrections, blockers, and
      disposition.
- [ ] Add an independent recognition record with a non-author self-reviewer
      and confidence of at least 0.80.

## Validation gates

- [ ] Catalog validation passes.
- [ ] Asset evidence validation passes.
- [ ] Help-document validation passes.
- [ ] Industrial-reference validation passes.
- [ ] GLTF kinematics validation passes.
- [ ] Training scene validation passes.
- [ ] Full simulator regression tests pass.
- [ ] Confirm that no live PLC connection is attempted during validation.

## Current baseline

- Training scenes: 70
- Training cases: 140
- Lesson-specific visual requirements represented in scenes: 105
- Current runtime implementation: reusable `trainingAccessory` geometry
- Stable candidate packages registered: 105 lesson-specific packages
- Candidate package model resources: source, delivery, collision, and
  thumbnail files present for all 105 packages
- Candidate and scene help generated: 297 asset documents and 102 scene
  documents validate
- Current full-package status: incomplete. The 105 new packages still require
  asset-specific structural review, blind-recognition evidence, and final
  provenance/evidence promotion gates.
- External review status: not run because submitting project thumbnails to
  isolated review processes requires explicit user authorization.
