"""Build a reusable GMA palletized case load for shipping scenes."""
from __future__ import annotations

import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(os.environ["RUNGPROOF_PROJECT_ROOT"])
ASSET = ROOT / "assets" / "loads" / "palletized_case_load"
bpy.context.preferences.filepaths.save_version = 0


def material(name, color, metallic=0.0, roughness=0.5, alpha=1.0):
    value = bpy.data.materials.new(name)
    value.diffuse_color = (*color, alpha)
    value.use_nodes = True
    shader = value.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if alpha < 1.0:
        shader.inputs["Alpha"].default_value = alpha
        value.surface_render_method = "DITHERED"
    return value


def box(name, location, dimensions, mat, bevel=0.006, collision=True):
    bpy.ops.mesh.primitive_cube_add(location=location)
    item = bpy.context.object
    item.name = name
    item.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    item.data.materials.append(mat)
    if bevel:
        edge = item.modifiers.new("Manufactured edge radius", "BEVEL")
        edge.width = bevel
        edge.segments = 3
        edge.limit_method = "ANGLE"
    item["rungproof_asset"] = True
    item["rungproof_collision"] = collision
    return item


def point_at(item, target):
    item.rotation_euler = (Vector(target) - item.location).to_track_quat("-Z", "Y").to_euler()


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    wood = material("Heat-treated pallet wood", (0.45, 0.25, 0.09), 0.0, 0.82)
    cardboard = material("Kraft corrugated cases", (0.57, 0.36, 0.16), 0.0, 0.90)
    tape = material("Carton sealing tape", (0.88, 0.75, 0.47), 0.0, 0.78)
    white = material("Shipping label", (0.93, 0.94, 0.90), 0.0, 0.68)
    black = material("Barcode print", (0.015, 0.018, 0.020), 0.0, 0.48)
    strap = material("Polypropylene strap", (0.03, 0.07, 0.09), 0.0, 0.32)

    # GMA block pallet: top/bottom boards, stringer boards and nine blocks leave
    # visible fork openings instead of reading as a solid wooden slab.
    # Derive the bearing planes instead of positioning each part separately.
    # Preserve the installed runner datum and top-deck height. Previously the
    # blocks penetrated the lower boards and the deck floated 40 mm above the
    # stringers; cases then floated another 22.5 mm above the deck.
    bottom_center, board_thickness = 0.055, 0.035
    bottom_top = bottom_center + board_thickness / 2
    deck_center = 0.23
    deck_bottom = deck_center - board_thickness / 2
    deck_top = deck_center + board_thickness / 2
    stringer_thickness = 0.045
    stringer_bottom = deck_bottom - stringer_thickness
    block_height = stringer_bottom - bottom_top
    for index, x in enumerate((-0.53, -0.35, -0.17, 0.0, 0.17, 0.35, 0.53)):
        box(f"PALLET_TOP_DECK_{index}", (x, 0, deck_center), (0.13, 1.016, board_thickness), wood, 0.004)
    for index, y in enumerate((-0.43, 0, 0.43)):
        box(f"PALLET_STRINGER_{index}", (0, y, (deck_bottom + stringer_bottom) / 2), (1.219, 0.105, stringer_thickness), wood, 0.004)
        box(f"PALLET_BOTTOM_{index}", (0, y, bottom_center), (1.219, 0.105, board_thickness), wood, 0.004)
        for x in (-0.53, 0, 0.53):
            box(f"PALLET_BLOCK_{index}_{x}", (x, y, (bottom_top + stringer_bottom) / 2), (0.14, 0.14, block_height), wood, 0.005)

    case_w, case_d, case_h = 0.52, 0.43, 0.34
    tape_thickness = 0.0002
    for layer in range(2):
        rotated = layer % 2 == 1
        for row in range(2):
            for column in range(2):
                x = (column - 0.5) * (case_w + 0.035)
                y = (row - 0.5) * (case_d + 0.035)
                z = deck_top + case_h * (layer + 0.5) + tape_thickness * layer
                dims = (case_d, case_w, case_h) if rotated else (case_w, case_d, case_h)
                box(f"CASE_{layer}_{row}_{column}", (x, y, z), dims, cardboard, 0.012)
                # Thin sealing tape sits on the case surface. The upper cases
                # bear on this modeled strip rather than intersecting it.
                box(f"CASE_TAPE_{layer}_{row}_{column}", (x, y, z + case_h / 2 + tape_thickness / 2),
                    (dims[0] - 0.025, 0.075, tape_thickness), tape, 0.00008, False)
                if row == 0:
                    box(f"CASE_LABEL_{layer}_{row}_{column}", (x, y - dims[1] * 0.506, z),
                        (0.23, 0.012, 0.14), white, 0.002, False)
                    for line in range(7):
                        box(f"BARCODE_{layer}_{column}_{line}",
                            (x - 0.075 + line * 0.025, y - dims[1] * 0.514, z - 0.015),
                            (0.010 if line % 2 else 0.015, 0.006, 0.075), black, 0.001, False)

    # Two vertical retention straps visibly bind the complete load to the pallet.
    load_top_z = deck_top + case_h * 2 + tape_thickness * 2
    strap_center_z = (0.055 + load_top_z) / 2
    strap_height = load_top_z - 0.055
    for x in (-0.34, 0.34):
        box(f"LOAD_STRAP_FRONT_{x}", (x, -0.526, strap_center_z),
            (0.035, 0.012, strap_height), strap, 0.002, False)
        box(f"LOAD_STRAP_BACK_{x}", (x, 0.526, strap_center_z),
            (0.035, 0.012, strap_height), strap, 0.002, False)
        box(f"LOAD_STRAP_TOP_{x}", (x, 0, load_top_z + 0.008),
            (0.035, 1.052, 0.012), strap, 0.002, False)

    for folder in ("source", "delivery", "collision", "review"):
        (ASSET / folder).mkdir(parents=True, exist_ok=True)
    for folder in (ASSET / "source", ASSET / "review"):
        (folder / ".gdignore").touch()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET / "source" / "palletized_case_load.blend"))

    objects = [item for item in bpy.context.scene.objects if item.type == "MESH" and item.get("rungproof_asset")]
    bpy.ops.object.select_all(action="DESELECT")
    for item in objects:
        item.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(filepath=str(ASSET / "delivery" / "palletized_case_load.glb"),
        export_format="GLB", use_selection=True, export_apply=True)

    bpy.ops.object.select_all(action="DESELECT")
    box("COLLISION_primary", (0, 0, 0.60), (1.219, 1.016, 1.20), black, 0, True).select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET / "collision" / "palletized_case_load_collision.glb"),
        export_format="GLB", use_selection=True, export_apply=True)
    bpy.data.objects.remove(bpy.context.object, do_unlink=True)

    floor = box("REVIEW_floor", (0, 0, -0.035), (4.2, 4.2, 0.05), black, 0.002, False)
    floor["rungproof_asset"] = False
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.color = (0.018, 0.024, 0.028)
    for index, (location, energy, size) in enumerate((((3, -4, 4), 1300, 3), ((-3, -1, 2.5), 800, 2.5), ((0, 3, 4), 900, 3))):
        data = bpy.data.lights.new(f"REVIEW_light_{index}", "AREA")
        data.energy, data.shape, data.size = energy, "DISK", size
        light = bpy.data.objects.new(data.name, data)
        light.location = location
        bpy.context.collection.objects.link(light)
        point_at(light, (0, 0, 0.6))
    camera_data = bpy.data.cameras.new("REVIEW_camera")
    camera = bpy.data.objects.new("REVIEW_camera", camera_data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    camera_data.lens = 58
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    for index, angle in enumerate((305, 215, 35, 125), 1):
        radians = math.radians(angle)
        camera.location = (3.1 * math.cos(radians), 3.1 * math.sin(radians), 1.75)
        point_at(camera, (0, 0, 0.6))
        scene.render.filepath = str(ASSET / "review" / f"palletized_case_load_{index:02d}.png")
        bpy.ops.render.render(write_still=True)
    (ASSET / "thumbnail.png").write_bytes((ASSET / "review" / "palletized_case_load_01.png").read_bytes())
    print("PALLETIZED_CASE_LOAD_BUILT")


if __name__ == "__main__":
    main()
