"""Regression contract for the VM-safe isometric 3D renderer."""

from __future__ import annotations

import unittest

from tools.native_software_viewport import (
    Primitive3D,
    SOFTWARE_RENDER_MODE,
    build_scene_geometry,
    project_isometric,
    scene_faces,
    sort_faces_for_painter,
)


def _polygon_area(points: list[tuple[float, float]]) -> float:
    area = 0.0
    for index, point in enumerate(points):
        following = points[(index + 1) % len(points)]
        area += point[0] * following[1] - following[0] * point[1]
    return abs(area) * 0.5


class Software3DGeometryContractTests(unittest.TestCase):
    def test_native_renderer_uses_the_high_fidelity_radial_quality_floor(self) -> None:
        from tools.native_software_viewport import (
            DEFAULT_RADIAL_SEGMENTS,
            DEFAULT_SPHERE_LATITUDE_SEGMENTS,
            DEFAULT_SPHERE_LONGITUDE_SEGMENTS,
            _cylinder_faces,
            _sphere_faces,
        )

        cylinder = Primitive3D(
            role="quality_cylinder",
            kind="cylinder",
            center=(0.0, 0.0, 0.0),
            color="#FFFFFF",
            radius=1.0,
            length=1.0,
        )
        sphere = Primitive3D(
            role="quality_sphere",
            kind="sphere",
            center=(0.0, 0.0, 0.0),
            color="#FFFFFF",
            radius=1.0,
        )

        self.assertEqual(DEFAULT_RADIAL_SEGMENTS, 24)
        self.assertEqual(DEFAULT_SPHERE_LONGITUDE_SEGMENTS, 24)
        self.assertEqual(DEFAULT_SPHERE_LATITUDE_SEGMENTS, 12)
        self.assertEqual(len(_cylinder_faces(cylinder)), DEFAULT_RADIAL_SEGMENTS + 2)
        self.assertEqual(
            len(_sphere_faces(sphere)),
            DEFAULT_SPHERE_LONGITUDE_SEGMENTS * DEFAULT_SPHERE_LATITUDE_SEGMENTS,
        )

    def test_sphere_primitive_renders_a_closed_three_dimensional_joint(
        self,
    ) -> None:
        joint = Primitive3D(
            role="robot_joint",
            kind="sphere",
            center=(0.0, 1.0, 0.0),
            color="#26343C",
            radius=0.4,
        )

        faces = scene_faces((joint,))
        points = {point for face in faces for point in face.points}

        self.assertGreaterEqual(len(faces), 24)
        self.assertAlmostEqual(min(point[0] for point in points), -0.4)
        self.assertAlmostEqual(max(point[0] for point in points), 0.4)
        self.assertLess(min(point[1] for point in points), 1.0)
        self.assertGreater(max(point[1] for point in points), 1.0)
        self.assertLess(min(point[2] for point in points), 0.0)
        self.assertGreater(max(point[2] for point in points), 0.0)

    def test_tube_primitive_keeps_its_end_open(self) -> None:
        housing = Primitive3D(
            role="fan_housing",
            kind="tube",
            center=(0.0, 1.0, 0.0),
            color="#536873",
            axis="x",
            radius=1.0,
            inner_radius=0.76,
            length=0.8,
        )

        faces = scene_faces((housing,))
        roles = {face.role for face in faces}

        self.assertTrue(any("outer" in role for role in roles))
        self.assertTrue(any("inner" in role for role in roles))
        self.assertTrue(any("end_start" in role for role in roles))
        self.assertTrue(any("end_finish" in role for role in roles))
        self.assertFalse(any(role == "fan_housing_end_start" for role in roles))
        self.assertFalse(any(role == "fan_housing_end_finish" for role in roles))

    def test_frustum_primitive_has_one_wide_end_and_one_narrow_end(
        self,
    ) -> None:
        cone = Primitive3D(
            role="radar_measurement_cone",
            kind="frustum",
            center=(0.0, 2.0, 0.0),
            color="#43C7F4",
            radius=0.80,
            top_radius=0.12,
            length=2.5,
            end_caps=False,
        )

        faces = scene_faces((cone,))
        points = {point for face in faces for point in face.points}

        self.assertGreaterEqual(len(faces), 12)
        bottom_points = [point for point in points if point[1] < 1.0]
        top_points = [point for point in points if point[1] > 3.0]
        self.assertGreater(
            max(abs(point[0]) for point in bottom_points),
            max(abs(point[0]) for point in top_points),
        )

    def test_primitives_support_rotated_machine_members(self) -> None:
        member = Primitive3D(
            role="scissor_arm",
            kind="box",
            center=(0.0, 1.0, 0.0),
            color="#F2B94B",
            size=(2.0, 0.2, 0.2),
            rotation=(0.0, 0.0, 45.0),
        )

        points = {
            tuple(round(value, 4) for value in point)
            for face in scene_faces((member,))
            for point in face.points
        }

        self.assertGreater(len({point[0] for point in points}), 2)
        self.assertGreater(len({point[1] for point in points}), 2)

    def test_default_software_scene_has_real_projected_depth(self) -> None:
        self.assertEqual(SOFTWARE_RENDER_MODE, "isometric-3d")

        deck_top = [
            project_isometric(point)[:2]
            for point in (
                (-3.5, 1.08, -0.75),
                (3.5, 1.08, -0.75),
                (3.5, 1.08, 0.75),
                (-3.5, 1.08, 0.75),
            )
        ]
        self.assertGreater(_polygon_area(deck_top), 1.0)
        self.assertGreater(
            abs(deck_top[1][1] - deck_top[0][1]),
            0.25,
            "The conveyor length must recede in perspective, not stay flat.",
        )
        self.assertGreater(
            abs(deck_top[3][0] - deck_top[0][0]),
            0.25,
            "The conveyor top must expose visible cross-belt depth.",
        )

    def test_scene_geometry_preserves_machine_and_drive_topology(self) -> None:
        geometry = build_scene_geometry()
        by_role = {primitive.role: primitive for primitive in geometry}

        for required in (
            "conveyor_deck",
            "drive_roller",
            "drive_coupling_guard",
            "drive_gearbox",
            "drive_motor",
            "pusher_body",
            "photoeye_emitter",
            "stacklight_pole",
        ):
            self.assertIn(required, by_role)

        drive_roller = by_role["drive_roller"]
        gearbox = by_role["drive_gearbox"]
        motor = by_role["drive_motor"]
        self.assertEqual(drive_roller.axis, "z")
        self.assertEqual(motor.axis, "z")
        self.assertEqual(gearbox.center[:2], drive_roller.center[:2])
        self.assertEqual(motor.center[:2], drive_roller.center[:2])
        self.assertGreater(gearbox.center[2], drive_roller.center[2])
        self.assertGreater(motor.center[2], gearbox.center[2])

    def test_photoeye_beam_is_centered_on_pusher_plate(self) -> None:
        geometry = {
            primitive.role: primitive for primitive in build_scene_geometry()
        }
        beam = geometry["photoeye_beam"]
        plate = geometry["pusher_plate"]
        self.assertAlmostEqual(beam.center[0], plate.center[0], places=6)
        self.assertAlmostEqual(beam.center[1], plate.center[1], places=6)
        self.assertLessEqual(beam.size[1], 0.012)

    def test_scene_conveyor_bed_and_payload_stay_between_the_side_channels(
        self,
    ) -> None:
        """The camera-facing rail is the only rail in front of the bed."""

        geometry = build_scene_geometry()
        rails = [
            primitive
            for primitive in geometry
            if primitive.role.startswith("side_rail_")
        ]
        for yaw_degrees in (8.0, 34.0, 72.0):
            ordered_faces = sort_faces_for_painter(
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

            def indexes_for(*prefixes: str) -> list[int]:
                return [
                    index
                    for index, face in enumerate(ordered_faces)
                    if face.role.startswith(prefixes)
                ]

            far_rail_indexes = indexes_for(far_rail.role)
            roller_indexes = indexes_for("roller_", "drive_roller")
            product_indexes = indexes_for("product_")
            near_rail_indexes = indexes_for(near_rail.role)
            drive_indexes = indexes_for(
                "drive_output_shaft",
                "drive_coupling_guard",
                "drive_bearing_flange",
                "drive_adapter_plate",
                "drive_gearbox",
                "drive_mounting_bracket",
                "drive_motor",
                "drive_run_lamp",
            )

            self.assertTrue(far_rail_indexes)
            self.assertTrue(roller_indexes)
            self.assertTrue(product_indexes)
            self.assertTrue(near_rail_indexes)
            self.assertTrue(drive_indexes)
            self.assertLess(max(far_rail_indexes), min(roller_indexes))
            self.assertLess(max(roller_indexes), min(near_rail_indexes))
            self.assertLess(max(far_rail_indexes), min(product_indexes))
            self.assertLess(max(product_indexes), min(near_rail_indexes))
            self.assertLess(max(near_rail_indexes), min(drive_indexes))


if __name__ == "__main__":
    unittest.main()
