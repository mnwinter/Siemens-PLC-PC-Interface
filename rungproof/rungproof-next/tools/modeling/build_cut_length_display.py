"""Replace the shutter copy with an original, explicitly static length readout.

Run in Blender with RUNGPROOF_PROJECT_ROOT. This creates training geometry,
not a measurement algorithm or OEM replica. Old identity evidence is retained
as invalid history instead of being inherited by the replacement.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(os.environ["RUNGPROOF_PROJECT_ROOT"]).resolve()
os.environ["RUNGPROOF_ASSET_FILTER"] = "__helpers_only__"
spec = importlib.util.spec_from_file_location("length_display_exports", ROOT / "tools/modeling/build_material_flow_assets.py")
flow = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(flow)
flow.BASE = ROOT / "assets/training_accessories"
bpy.context.preferences.filepaths.save_version = 0
SLUG = "cut_length_display"
ASSET_ID = "training.accessory.cut_length_display.v1"


def display(materials):
    # Blender Z is height; the base datum is the scene floor. The mast overlaps
    # both the base and housing so the delivered readout has visible support.
    flow.box("LENGTH_DISPLAY_base", (0, 0, .04), (.85, .70, .08), materials["zinc"])
    flow.box("LENGTH_DISPLAY_mast", (0, .14, .69), (.085, .085, 1.22), materials["blue"])
    flow.box("LENGTH_DISPLAY_housing", (0, .06, 1.51), (.82, .24, .48), materials["steel"])
    flow.box("LENGTH_DISPLAY_screen", (0, -.069, 1.51), (.70, .018, .34), materials["black"], collision=False)
    flow.text("LENGTH_DISPLAY_static_legend", "LENGTH\nNO MEASUREMENT", (0, -.084, 1.51), .055,
              materials["white"], (math.pi / 2, 0, 0))


review = flow.BASE / SLUG / "review"
archive = review / "historical_invalid_identity_20261005"
archive.mkdir(parents=True, exist_ok=True)
for file in review.iterdir():
    if file.is_file() and file.name != ".gdignore" and not file.name.startswith(SLUG + "_"):
        if not (archive / file.name).exists():
            file.rename(archive / file.name)
flow.save(SLUG, display)

points = []
graph = bpy.context.evaluated_depsgraph_get()
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and obj.get("rungproof_asset"):
        evaluated = obj.evaluated_get(graph)
        points.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
assert abs(min(p.z for p in points)) < .001, "Display floor datum is incorrect"
size = [max(p[a] for p in points) - min(p[a] for p in points) for a in range(3)]
catalog_path = ROOT / "assets/catalog/candidates.catalog.json"
catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
asset = next(a for a in catalog["assets"] if a["id"] == ASSET_ID)
asset.pop("genericBasisAssetId", None)
asset["bounds"] = dict(widthM=size[0], heightM=size[2], depthM=size[1])
asset["kinematics"] = []
asset["animationTags"] = []
asset["quality"] = dict(status="candidate", blindReviewId=None, recognitionConfidence=None,
                        topologyReviewed=False, materialReviewed=False,
                        scaleReviewed=False, animationReviewed=False)
catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
register_path = ROOT / "assets/catalog/industrial-reference-register.json"
register = json.loads(register_path.read_text(encoding="utf-8"))
register["entries"] = [entry for entry in register["entries"] if entry["assetId"] != ASSET_ID]
register_path.write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
(review / "repair_scope.json").write_text(json.dumps({
    "assetId": ASSET_ID, "status": "candidate-unapproved",
    "scope": "Original static readout. LENGTH / NO MEASUREMENT; no numeric point or measurement behavior is bound.",
    "historicalEvidence": "historical_invalid_identity_20261005 is invalid for this replacement.",
}, indent=2) + "\n", encoding="utf-8")
help_spec = importlib.util.spec_from_file_location("length_display_help", ROOT / "tools/generate_help_documents.py")
help_module = importlib.util.module_from_spec(help_spec)
assert help_spec.loader is not None
help_spec.loader.exec_module(help_module)
help_text = help_module.asset_help(asset, "candidate", {})
help_text += ("\n## Replacement scope - 2026-10-05\n\n"
              "Original static training readout displaying LENGTH / NO MEASUREMENT. "
              "No numeric scene point or measurement algorithm is bound. "
              "Historical shutter/parking-display evidence is invalid for the replacement. "
              "Independent approval remains pending.\n")
(ROOT / "docs/help/assets" / f"{ASSET_ID}.md").write_text(help_text, encoding="utf-8")
print("CUT_LENGTH_DISPLAY_BUILT original static geometry; measurement remains unimplemented")
