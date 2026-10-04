"""Behavior contracts for the next native scene-review batch."""

from __future__ import annotations

import json
import unittest

from tools.native_scene_library import (
    EQUIPMENT_GALLERY_DEFINITION,
    NATIVE_SCENE_DEFINITIONS,
    build_native_scene_geometry,
)
from tools.native_software_viewport import (
    project_isometric,
    scene_faces,
    sort_faces_for_painter,
)


class NativeSceneLibraryTests(unittest.TestCase):
    def test_equipment_gallery_builds_every_reusable_asset_type(self) -> None:
        source = json.loads(
            EQUIPMENT_GALLERY_DEFINITION.source_file.read_text(encoding="utf-8")
        )
        geometry = build_native_scene_geometry("equipment-gallery")
        self.assertEqual(
            {item["type"] for item in source["equipment"]},
            {
                "box",
                "conveyor",
                "drillPress",
                "fan",
                "indicator",
                "levelSensor",
                "liftTable",
                "machine",
                "motor",
                "photoeye",
                "pipe",
                "pump",
                "robotArm",
                "rollerShutter",
                "rotarySwitch",
                "rotaryTable",
                "switch",
                "tank",
                "valve",
            },
        )
        self.assertGreater(len(geometry), 100)

    def test_gallery_fan_preserves_source_yaw(self) -> None:
        geometry = build_native_scene_geometry("equipment-gallery")
        fan = next(
            item
            for item in geometry
            if item.role == "gallery_fan::tubular_housing"
        )
        self.assertEqual(fan.rotation[1], -18.0)

    def test_every_review_scene_has_a_source_backed_setup_document(
        self,
    ) -> None:
        for definition in NATIVE_SCENE_DEFINITIONS:
            source = json.loads(
                definition.source_file.read_text(encoding="utf-8")
            )
            setup_text = definition.setup_file.read_text(encoding="utf-8")

            self.assertIn(
                f"# {definition.approval_id} - {definition.label}",
                setup_text,
            )
            self.assertIn("Native PLC profile: **Not created**", setup_text)
            for point in source["simulation"]["points"]:
                self.assertIn(f"`{point['name']}`", setup_text)

    def test_batch_is_the_next_four_source_scenes_after_native_scene_two(
        self,
    ) -> None:
        self.assertEqual(
            tuple(scene.scene_id for scene in NATIVE_SCENE_DEFINITIONS),
            (
                "conveyor-cell",
                "tank-level",
                "tank-high-low",
                "tank-radar",
            ),
        )
        self.assertEqual(
            tuple(scene.approval_id for scene in NATIVE_SCENE_DEFINITIONS),
            ("S03", "S04", "S05", "S06"),
        )

    def test_conveyor_inspection_scene_reuses_every_required_asset(self) -> None:
        definition = next(
            scene
            for scene in NATIVE_SCENE_DEFINITIONS
            if scene.scene_id == "conveyor-cell"
        )
        source = json.loads(
            definition.source_file.read_text(encoding="utf-8")
        )
        source_types = {item["type"] for item in source["equipment"]}
        roles = {
            primitive.role
            for primitive in build_native_scene_geometry(definition.scene_id)
        }

        self.assertEqual(
            source_types,
            {"box", "conveyor", "indicator", "photoeye", "switch"},
        )
        for required_role in (
            "main_conveyor::side_rail_left",
            "main_conveyor::drive_roller",
            "main_conveyor::gearmotor_frame",
            "carton_1::carton_body",
            "carton_2::carton_body",
            "carton_3::carton_body",
            "inspection_photoeye::sender_housing",
            "inspection_photoeye::receiver_housing",
            "operator_station::station_enclosure",
            "cell_stacklight::green_module",
        ):
            self.assertIn(required_role, roles)

    def test_composed_conveyor_keeps_rollers_between_its_two_rails(self) -> None:
        geometry = build_native_scene_geometry("conveyor-cell")
        rails = [
            primitive
            for primitive in geometry
            if "::side_rail_" in primitive.role
        ]
        for yaw_degrees in (8.0, 34.0, 72.0):
            ordered = sort_faces_for_painter(
                scene_faces(geometry),
                yaw_degrees=yaw_degrees,
            )
            far_rail, near_rail = sorted(
                rails,
                key=lambda rail: project_isometric(
                    rail.center,
                    yaw_degrees=yaw_degrees,
                )[2],
            )
            far_indexes = [
                index
                for index, face in enumerate(ordered)
                if face.role == far_rail.role
            ]
            roller_indexes = [
                index
                for index, face in enumerate(ordered)
                if "::roller_" in face.role
                or "::drive_roller" in face.role
            ]
            near_indexes = [
                index
                for index, face in enumerate(ordered)
                if face.role == near_rail.role
            ]

            self.assertLess(max(far_indexes), min(roller_indexes))
            self.assertLess(max(roller_indexes), min(near_indexes))

    def test_analog_tank_scene_has_connected_process_equipment_and_level(
        self,
    ) -> None:
        definition = next(
            scene
            for scene in NATIVE_SCENE_DEFINITIONS
            if scene.scene_id == "tank-level"
        )
        source = json.loads(
            definition.source_file.read_text(encoding="utf-8")
        )
        source_types = {item["type"] for item in source["equipment"]}
        geometry = build_native_scene_geometry(definition.scene_id)
        by_role = {primitive.role: primitive for primitive in geometry}

        self.assertEqual(
            source_types,
            {"indicator", "levelSensor", "pipe", "pump", "switch", "tank"},
        )
        for required_role in (
            "process_tank::tank_shell",
            "inlet_pump::pump_volute",
            "inlet_riser::pipe_spool",
            "inlet_header::pipe_spool",
            "outlet_header::pipe_spool",
            "low_level_switch::sensor_body",
            "high_level_switch::sensor_body",
            "level_transmitter::local_display",
            "pump_station::station_enclosure",
            "drain_station::station_enclosure",
            "tank_stacklight::amber_module",
        ):
            self.assertIn(required_role, by_role)

        filled_segments = [
            primitive
            for primitive in geometry
            if "process_tank::sight_glass_segment_" in primitive.role
            and primitive.color == "#00C8F0"
        ]
        self.assertEqual(len(filled_segments), 4)

    def test_high_low_tank_scene_is_discrete_only_and_shows_half_level(
        self,
    ) -> None:
        geometry = build_native_scene_geometry("tank-high-low")
        roles = {primitive.role for primitive in geometry}

        for required_role in (
            "water_tank_hl::tank_shell",
            "hl_inlet_pump::pump_volute",
            "hl_low_switch::sensor_body",
            "hl_high_switch::sensor_body",
            "hl_pump_station::station_enclosure",
            "hl_drain_station::station_enclosure",
            "hl_stacklight::amber_module",
        ):
            self.assertIn(required_role, roles)
        self.assertFalse(
            any("level_transmitter::" in role for role in roles)
        )
        self.assertFalse(any("radar_" in role for role in roles))

        filled_segments = [
            primitive
            for primitive in geometry
            if "water_tank_hl::sight_glass_segment_" in primitive.role
            and primitive.color == "#00C8F0"
        ]
        self.assertEqual(len(filled_segments), 5)

    def test_radar_tank_scene_has_noncontact_measurement_to_liquid_surface(
        self,
    ) -> None:
        geometry = build_native_scene_geometry("tank-radar")
        roles = {primitive.role for primitive in geometry}

        for required_role in (
            "water_tank_radar::tank_shell",
            "radar_inlet_pump::pump_volute",
            "radar_transmitter::antenna_horn",
            "radar_transmitter::electronics_housing",
            "radar_transmitter::local_display",
            "radar_pump_station::station_enclosure",
            "radar_drain_station::station_enclosure",
            "radar_stacklight::amber_module",
        ):
            self.assertIn(required_role, roles)
        self.assertFalse(any("::sensor_body" in role for role in roles))

        measurement_cone = [
            primitive
            for primitive in geometry
            if primitive.role.startswith(
                "radar_transmitter::measurement_cone_"
            )
        ]
        self.assertEqual(len(measurement_cone), 1)
        self.assertLessEqual(
            min(
                primitive.center[1] - primitive.length / 2
                for primitive in measurement_cone
            ),
            1.75,
        )
        self.assertGreaterEqual(
            max(
                primitive.center[1] + primitive.length / 2
                for primitive in measurement_cone
            ),
            4.15,
        )

        filled_segments = [
            primitive
            for primitive in geometry
            if "water_tank_radar::sight_glass_segment_" in primitive.role
            and primitive.color == "#00C8F0"
        ]
        self.assertEqual(len(filled_segments), 4)

    def test_radar_measurement_volume_is_one_tapered_frustum(self) -> None:
        measurement_cone = [
            primitive
            for primitive in build_native_scene_geometry("tank-radar")
            if primitive.role.startswith(
                "radar_transmitter::measurement_cone_"
            )
        ]

        self.assertEqual(len(measurement_cone), 1)
        cone = measurement_cone[0]
        self.assertEqual(cone.kind, "frustum")
        self.assertGreater(cone.radius, cone.top_radius)


if __name__ == "__main__":
    unittest.main()
