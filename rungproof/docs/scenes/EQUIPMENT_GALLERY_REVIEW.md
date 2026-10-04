# Reusable Equipment Gallery Review

The Equipment Gallery is a geometry-review workspace, not a PLC scene. It
shows reusable assets in isolation before they are placed into production
cells or training scenes.

Use it to review:

- scale and proportions;
- topology and recognizable industrial construction;
- clipping, depth order, and hidden geometry;
- mounting, supports, shafts, guards, rails, and process connections;
- whether an asset can be reused without changing an approved machine cell.

## Review workflow

1. Open `Scene > Equipment Gallery`.
2. Drag the viewport to orbit, use the middle button to pan, and use the wheel
   to zoom.
3. Review one asset at a time against its label and expected physical topology.
4. Record geometry corrections in the native asset library and add a focused
   regression test before changing a production scene.
5. Re-run the geometry tests and then review the affected production scenes.

The gallery uses the same native asset factory as the production scenes. It
does not connect to a PLC, create process tags, or authorize machine motion.
