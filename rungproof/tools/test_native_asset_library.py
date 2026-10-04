"""Behavior and topology contracts for independently reviewed native assets."""

from __future__ import annotations

import math
import unittest

from tools.native_asset_library import (
    ASSET_DEFINITIONS,
    build_asset_geometry,
)
from tools.native_software_viewport import scene_faces


class NativeAssetLibraryTests(unittest.TestCase):
    def test_native_review_library_covers_every_legacy_builder_type(
        self,
    ) -> None:
        expected_types = {
            "motor",
            "conveyor",
            "box",
            "photoeye",
            "switch",
            "indicator",
            "pump",
            "fan",
            "pusher",
            "tank",
            "levelSensor",
            "radarLevelSensor",
            "pipe",
            "rotarySwitch",
            "liftTable",
            "valve",
            "drillPress",
            "robotArm",
            "rollerShutter",
            "rotaryTable",
            "machine",
            "gearedMotor",
            "beltConveyor",
            "palletConveyor",
            "pneumaticCylinder",
            "parallelGripper",
            "pallet",
            "tote",
            "hopper",
            "silo",
            "safetyFence",
            "safetyGate",
            "lightCurtain",
            "proximitySensor",
            "controlPanel",
            "vfdCabinet",
            "airCompressor",
            "airReceiver",
            "airDryer",
            "hydraulicPowerUnit",
            "heatExchanger",
            "mixerAgitator",
            "weighScale",
            "barcodeScanner",
            "visionCamera",
            "rollerTransfer",
            "conveyorTurntable",
            "verticalLift",
            "diverterArm",
            "amr",
        }

        self.assertEqual(
            {definition.asset_type for definition in ASSET_DEFINITIONS},
            expected_types,
        )
        self.assertEqual(
            [definition.approval_id for definition in ASSET_DEFINITIONS],
            [f"A{index:02d}" for index in range(1, 51)],
        )

    def test_each_review_asset_preserves_its_required_real_world_topology(
        self,
    ) -> None:
        required_roles = {
            "conveyor": {
                "drive_roller",
                "drive_shaft",
                "coupling_guard",
                "bearing_flange",
                "gearbox",
                "drive_bracket",
                "gearmotor_frame",
            },
            "box": {"carton_body", "top_tape", "top_seam"},
            "photoeye": {
                "sender_housing",
                "sender_lens",
                "receiver_housing",
                "receiver_lens",
                "beam",
            },
            "switch": {
                "station_enclosure",
                "operator_bezel",
                "operator_cap",
            },
            "indicator": {
                "pole",
                "red_module",
                "amber_module",
                "green_module",
            },
            "pump": {
                "pump_motor_frame",
                "motor_stool",
                "pump_volute",
                "suction_flange",
                "discharge_flange",
            },
            "fan": {
                "tubular_housing",
                "housing_flange_-0.43",
                "impeller_hub",
                "external_motor",
            },
            "pusher": {
                "cylinder_barrel",
                "piston_rod",
                "pusher_plate",
                "rear_mount",
            },
            "tank": {
                "tank_shell",
                "top_nozzle",
                "side_outlet",
                "access_cover",
                "tank_leg_0",
            },
            "levelSensor": {
                "welded_process_nozzle",
                "threaded_process_connection",
                "wetted_tip",
                "sensor_body",
                "m12_connector",
            },
            "radarLevelSensor": {
                "process_flange",
                "antenna_horn",
                "electronics_housing",
                "local_display",
                "radar_measurement_cone",
            },
            "pipe": {
                "pipe_spool",
                "left_flange",
                "right_flange",
                "support_saddle",
            },
            "rotarySwitch": {
                "selector_enclosure",
                "selector_bezel",
                "selector_knob",
            },
            "liftTable": {
                "lift_base",
                "lift_platform",
                "hydraulic_cylinder",
                "center_pivot_-0.54",
            },
            "valve": {
                "valve_body",
                "valve_disc",
                "valve_stem",
                "manual_lever",
            },
            "drillPress": {
                "drill_base",
                "drill_column",
                "work_table",
                "head_casting",
                "spindle",
                "feed_hub",
            },
            "robotArm": {
                "axis_1_base",
                "axis_2_shoulder",
                "upper_arm",
                "axis_3_elbow",
                "forearm",
                "axis_6_tool_flange",
            },
            "rollerShutter": {
                "top_header",
                "curtain_roll",
                "fabric_curtain",
                "bottom_bar",
                "operator_motor",
                "control_box",
            },
            "rotaryTable": {
                "indexer_housing",
                "rotary_plate",
                "center_opening",
                "side_gearbox",
                "indexer_motor",
            },
            "machine": {
                "machine_enclosure",
                "left_front_door",
                "right_front_door",
                "left_window",
                "right_window",
                "control_pendant",
            },
            "gearedMotor": {
                "motor_frame",
                "gearbox_housing",
                "gearbox_input_flange",
                "gearbox_output_bearing",
                "output_shaft",
            },
            "beltConveyor": {
                "belt_carry_run",
                "belt_return_run",
                "head_pulley",
                "tail_pulley",
                "drive_guard",
                "drive_motor",
            },
            "palletConveyor": {
                "chain_bed_-0.48",
                "chain_bed_0.48",
                "tail_sprocket_-0.48",
                "head_sprocket_0.48",
                "pallet_load_deck",
            },
            "pneumaticCylinder": {
                "profile_barrel",
                "piston_rod",
                "rod_clevis",
                "air_port_0",
                "reed_sensor_0",
            },
            "parallelGripper": {
                "gripper_body",
                "left_jaw",
                "right_jaw",
                "left_finger",
                "right_finger",
            },
            "pallet": {"top_deck_0", "support_block_0.0_0.0", "bottom_runner_0.0"},
            "tote": {"tote_body", "tote_inner_shadow", "rim_long_-0.54", "label_pocket_plate"},
            "hopper": {"hopper_bin", "outlet_transition", "slide_gate", "gate_actuator", "bin_vibrator"},
            "silo": {"silo_shell", "cone_bottom", "roof", "fill_nozzle", "load_cell_0", "ladder_rung_00"},
            "safetyFence": {"post_-1.55", "frame_rail_2.12", "mesh_vertical_00", "kickplate"},
            "safetyGate": {"gate_post_-1.45", "gate_frame_horizontal_2.2", "hinge_0.72", "safety_switch", "trapped_key"},
            "lightCurtain": {"sender_housing", "receiver_housing", "safety_beam_00", "sender_status_green"},
            "proximitySensor": {"threaded_barrel", "locknut_0", "sensing_face", "status_ring", "m12_connector"},
            "controlPanel": {"enclosure", "door", "hmi_screen", "main_disconnect", "disconnect_handle", "plinth"},
            "vfdCabinet": {"cabinet", "cabinet_door", "drive_display", "cooling_fan", "cable_gland_plate"},
            "airCompressor": {"compressor_enclosure", "service_door", "controller_screen", "discharge_connection", "base_skid"},
            "airReceiver": {"receiver_shell", "top_head", "bottom_head", "relief_valve", "pressure_gauge", "automatic_drain"},
            "airDryer": {"left_tower", "right_tower", "upper_manifold", "lower_manifold", "dryer_controller"},
            "hydraulicPowerUnit": {"reservoir", "motor", "pump", "valve_manifold", "return_filter", "level_gauge"},
            "heatExchanger": {"frame_plate_-0.72", "frame_plate_0.72", "heat_transfer_plate_00", "process_port_0"},
            "mixerAgitator": {"mixing_vessel", "gearbox", "agitator_motor", "agitator_shaft", "impeller_blade_0"},
            "weighScale": {"scale_platform", "scale_frame", "load_cell_0", "weight_indicator", "weight_display"},
            "barcodeScanner": {"scanner_post", "adjustable_bracket", "scanner_housing", "scanner_window", "aiming_beam"},
            "visionCamera": {"camera_body", "lens_barrel", "illumination_ring", "field_of_view", "camera_status"},
            "rollerTransfer": {"roller_00", "popup_chain_-0.42", "lift_carriage", "lift_cylinder", "transfer_drive"},
            "conveyorTurntable": {"turntable_base", "rotating_deck", "deck_roller_00", "center_bearing", "index_drive"},
            "verticalLift": {"mast_-1.18", "top_crossbeam", "lift_carriage", "counterweight", "hoist_motor", "lower_gate"},
            "diverterArm": {"pivot_column", "diverter_arm", "impact_roller_0", "swing_cylinder", "extended_sensor"},
            "amr": {"amr_chassis", "lift_deck", "drive_wheel_-0.72", "front_safety_scanner", "front_scanner_field", "emergency_stop"},
        }

        for asset_type, expected in required_roles.items():
            with self.subTest(asset_type=asset_type):
                roles = {
                    primitive.role
                    for primitive in build_asset_geometry(asset_type)
                }
                self.assertTrue(expected.issubset(roles), expected - roles)

    def test_motor_is_a_supported_foot_mounted_induction_motor(self) -> None:
        geometry = build_asset_geometry("motor")
        roles = {primitive.role for primitive in geometry}

        self.assertTrue(
            {
                "motor_frame",
                "drive_end_bell",
                "fan_end_bell",
                "fan_cover",
                "output_shaft",
                "terminal_box",
                "cable_gland",
                "nameplate",
            }.issubset(roles)
        )
        self.assertEqual(
            len([role for role in roles if role.startswith("mounting_foot_")]),
            4,
        )
        self.assertGreaterEqual(
            len([role for role in roles if role.startswith("cooling_rib_")]),
            8,
        )

    def test_motor_cooling_fins_run_axially_instead_of_banding_frame(
        self,
    ) -> None:
        fins = [
            primitive
            for primitive in build_asset_geometry("motor")
            if primitive.role.startswith("cooling_rib_")
        ]

        self.assertGreaterEqual(len(fins), 8)
        self.assertTrue(all(fin.kind == "box" for fin in fins))
        self.assertTrue(all(fin.size[0] >= 1.30 for fin in fins))

    def test_gallery_fidelity_pass_adds_readable_fabrication_cues(self) -> None:
        expected_detail_prefixes = {
            "motor": ("nameplate_fastener_", "terminal_box_fastener_"),
            "conveyor": ("wear_strip_", "foot_anchor_"),
            "box": ("shipping_label_mark_", "carton_front_seam"),
            "photoeye": ("sender_fastener_", "receiver_housing_face_seam"),
            "pump": ("baseplate_fastener_", "pump_nameplate_fastener_"),
            "tank": ("access_cover_fastener_", "tank_shell_seam"),
            "machine": ("door_center_seam", "safety_label_mark"),
        }

        for asset_type, prefixes in expected_detail_prefixes.items():
            with self.subTest(asset_type=asset_type):
                geometry = build_asset_geometry(asset_type)
                roles = {primitive.role for primitive in geometry}
                self.assertTrue(
                    all(
                        any(role.startswith(prefix) for role in roles)
                        for prefix in prefixes
                    ),
                    (asset_type, prefixes),
                )
                fasteners = [
                    primitive
                    for primitive in geometry
                    if "fastener" in primitive.role or "anchor" in primitive.role
                ]
                if fasteners:
                    self.assertTrue(
                        all(primitive.color == "#1A252A" for primitive in fasteners)
                    )

    def test_detail_layers_keep_material_contrast_explicit(self) -> None:
        for asset_type in ("motor", "conveyor", "pump", "tank", "machine"):
            with self.subTest(asset_type=asset_type):
                colors = {
                    primitive.color
                    for primitive in build_asset_geometry(asset_type)
                }
                self.assertIn("#1A252A", colors)
                self.assertGreaterEqual(len(colors), 4)

    def test_conveyor_rollers_clear_both_side_rails(self) -> None:
        geometry = build_asset_geometry("conveyor")
        positive_rail = next(
            primitive
            for primitive in geometry
            if primitive.role == "side_rail_right"
        )
        negative_rail = next(
            primitive
            for primitive in geometry
            if primitive.role == "side_rail_left"
        )
        rollers = [
            primitive
            for primitive in geometry
            if primitive.role == "drive_roller"
            or primitive.role.startswith("roller_")
        ]
        positive_inner_face = (
            positive_rail.center[2] - positive_rail.size[2] / 2
        )
        negative_inner_face = (
            negative_rail.center[2] + negative_rail.size[2] / 2
        )

        for roller in rollers:
            with self.subTest(roller=roller.role):
                self.assertGreaterEqual(
                    positive_inner_face - roller.length / 2,
                    0.24,
                )
                self.assertGreaterEqual(
                    -roller.length / 2 - negative_inner_face,
                    0.24,
                )

    def test_assembled_conveyor_does_not_draw_hidden_roller_end_caps(
        self,
    ) -> None:
        rollers = tuple(
            primitive
            for primitive in build_asset_geometry("conveyor")
            if primitive.role == "drive_roller"
            or primitive.role.startswith("roller_")
        )
        face_roles = {
            face.role
            for face in scene_faces(rollers)
        }

        self.assertFalse(
            any(
                role.endswith("_end_start")
                or role.endswith("_end_finish")
                for role in face_roles
            )
        )

    def test_conveyor_rollers_render_between_far_and_near_side_channels(
        self,
    ) -> None:
        from tools.native_software_viewport import (
            project_isometric,
            sort_faces_for_painter,
        )

        geometry = build_asset_geometry("conveyor")
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
            roller_indexes = [
                index
                for index, face in enumerate(ordered_faces)
                if face.role.startswith(("roller_", "drive_roller"))
            ]
            far_rail_indexes = [
                index
                for index, face in enumerate(ordered_faces)
                if face.role == far_rail.role
            ]
            near_rail_indexes = [
                index
                for index, face in enumerate(ordered_faces)
                if face.role == near_rail.role
            ]

            self.assertTrue(roller_indexes)
            self.assertTrue(far_rail_indexes)
            self.assertTrue(near_rail_indexes)
            self.assertLess(max(far_rail_indexes), min(roller_indexes))
            self.assertLess(max(roller_indexes), min(near_rail_indexes))

    def test_conveyor_external_drive_stays_in_front_of_side_channels(
        self,
    ) -> None:
        from tools.native_software_viewport import sort_faces_for_painter

        geometry = build_asset_geometry("conveyor")
        ordered_faces = sort_faces_for_painter(scene_faces(geometry))
        rail_indexes = [
            index
            for index, face in enumerate(ordered_faces)
            if face.role.startswith("side_rail_")
        ]
        drive_indexes = [
            index
            for index, face in enumerate(ordered_faces)
            if face.role.startswith(
                (
                    "drive_shaft",
                    "coupling_guard",
                    "bearing_flange",
                    "gearbox",
                    "drive_bracket",
                    "gearmotor_",
                )
            )
        ]

        self.assertTrue(rail_indexes)
        self.assertTrue(drive_indexes)
        self.assertLess(max(rail_indexes), min(drive_indexes))

    def test_axial_fan_has_open_housing_and_visible_impeller_blades(
        self,
    ) -> None:
        geometry = build_asset_geometry("fan")
        housing = next(
            primitive
            for primitive in geometry
            if primitive.role == "tubular_housing"
        )
        blades = [
            primitive
            for primitive in geometry
            if primitive.role.startswith("impeller_blade_")
        ]

        self.assertEqual(housing.kind, "tube")
        self.assertGreaterEqual(housing.inner_radius, 0.75)
        self.assertEqual(len(blades), 6)
        self.assertTrue(all(blade.kind == "box" for blade in blades))

    def test_tank_exposes_a_full_height_liquid_level_sight_window(
        self,
    ) -> None:
        geometry = build_asset_geometry("tank")
        by_role = {primitive.role: primitive for primitive in geometry}

        self.assertTrue(
            {
                "sight_glass_meniscus",
                "sight_glass_frame_left",
                "sight_glass_frame_right",
                "sight_glass_bottom_connection",
                "sight_glass_top_connection",
            }.issubset(by_role)
        )
        segments = [
            primitive
            for primitive in geometry
            if primitive.role.startswith("sight_glass_segment_")
        ]
        self.assertEqual(len(segments), 10)
        self.assertNotEqual(segments[0].color, segments[-1].color)
        segment_bottom = min(
            segment.center[1] - segment.size[1] / 2
            for segment in segments
        )
        segment_top = max(
            segment.center[1] + segment.size[1] / 2
            for segment in segments
        )
        self.assertGreaterEqual(segment_top - segment_bottom, 2.0)

    def test_scissor_lift_mechanism_clears_platform_bottom(self) -> None:
        geometry = build_asset_geometry("liftTable")
        platform = next(
            primitive
            for primitive in geometry
            if primitive.role == "lift_platform"
        )
        mechanism = tuple(
            primitive
            for primitive in geometry
            if primitive.role.startswith("scissor_arm_")
            or primitive.role.startswith("arm_pin_")
        )
        platform_bottom = min(
            point[1]
            for face in scene_faces((platform,))
            for point in face.points
        )
        mechanism_top = max(
            point[1]
            for face in scene_faces(mechanism)
            for point in face.points
        )

        self.assertGreaterEqual(platform_bottom - mechanism_top, 0.03)

    def test_butterfly_valve_exposes_disc_inside_open_wafer_body(
        self,
    ) -> None:
        geometry = build_asset_geometry("valve")
        by_role = {primitive.role: primitive for primitive in geometry}
        body = by_role["valve_body"]
        disc = by_role["valve_disc"]

        self.assertEqual(body.kind, "tube")
        self.assertGreater(body.inner_radius, disc.radius)
        self.assertGreater(
            disc.center[0] - disc.length / 2,
            body.center[0] + body.length / 2,
        )
        self.assertGreater(by_role["right_pipe"].inner_radius, disc.radius)
        self.assertGreater(by_role["right_flange"].inner_radius, disc.radius)
        self.assertLessEqual(by_role["right_pipe"].opacity, 110)
        self.assertLessEqual(by_role["right_flange"].opacity, 110)
        self.assertTrue(
            {
                "body_lug_top",
                "body_lug_bottom",
                "body_lug_front",
                "body_lug_rear",
            }.issubset(by_role)
        )

    def test_drill_press_table_clears_support_column(self) -> None:
        geometry = build_asset_geometry("drillPress")
        by_role = {primitive.role: primitive for primitive in geometry}
        column = by_role["drill_column"]
        table = by_role["work_table"]
        table_rear_face = table.center[2] - table.size[2] / 2
        column_front = column.center[2] + column.radius

        self.assertGreaterEqual(table_rear_face - column_front, 0.08)

    def test_drill_press_feed_handles_extend_outward_without_crossing_head(
        self,
    ) -> None:
        geometry = build_asset_geometry("drillPress")
        by_role = {primitive.role: primitive for primitive in geometry}
        head = by_role["head_casting"]
        rods = [
            primitive
            for primitive in geometry
            if primitive.role.startswith("feed_handle_rod_")
        ]
        knobs = [
            primitive
            for primitive in geometry
            if primitive.role.startswith("feed_handle_knob_")
        ]
        head_right_face = head.center[0] + head.size[0] / 2

        self.assertEqual(len(rods), 3)
        self.assertEqual(len(knobs), 3)
        self.assertTrue(all(rod.axis == "y" for rod in rods))
        self.assertTrue(
            all(rod.center[0] - rod.radius > head_right_face for rod in rods)
        )
        self.assertTrue(all(knob.kind == "sphere" for knob in knobs))

    def test_drill_press_tooling_sections_meet_without_overlap(self) -> None:
        geometry = build_asset_geometry("drillPress")
        by_role = {primitive.role: primitive for primitive in geometry}
        chain = [
            by_role["quill"],
            by_role["spindle"],
            by_role["chuck"],
            by_role["drill_bit"],
        ]

        for upper, lower in zip(chain, chain[1:]):
            with self.subTest(upper=upper.role, lower=lower.role):
                upper_bottom = upper.center[1] - upper.length / 2
                lower_top = lower.center[1] + lower.length / 2
                self.assertGreaterEqual(upper_bottom - lower_top, 0.0)
                self.assertLessEqual(upper_bottom - lower_top, 0.03)

        table = by_role["work_table"]
        table_top = table.center[1] + table.size[1] / 2
        bit_bottom = chain[-1].center[1] - chain[-1].length / 2
        self.assertGreaterEqual(bit_bottom - table_top, 0.01)

    def test_robot_uses_ball_joints_and_links_stop_short_of_joint_centers(
        self,
    ) -> None:
        geometry = build_asset_geometry("robotArm")
        by_role = {primitive.role: primitive for primitive in geometry}
        joint_roles = (
            "axis_2_shoulder",
            "axis_3_elbow",
            "axis_4_wrist",
            "axis_5_wrist",
        )

        self.assertTrue(
            all(by_role[role].kind == "sphere" for role in joint_roles)
        )

        for link_role, start_role, finish_role, center_clearance in (
            ("upper_arm", "axis_2_shoulder", "axis_3_elbow", 0.35),
            ("forearm", "axis_3_elbow", "axis_4_wrist", 0.25),
        ):
            link = by_role[link_role]
            start = by_role[start_role]
            finish = by_role[finish_role]
            center_distance = math.dist(start.center, finish.center)
            with self.subTest(link=link_role):
                self.assertLessEqual(
                    link.length,
                    center_distance - center_clearance,
                )


if __name__ == "__main__":
    unittest.main()
