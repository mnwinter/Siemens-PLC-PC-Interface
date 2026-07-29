"""Unit tests for typed digital/analog scene points."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.config import Direction, parse_config
from siemens_plc_pc_interface.points import (
    PointModel,
    PointQuality,
    PointValueError,
    build_address_groups,
)
from test_config import valid_config


def valid_point_config() -> dict:
    """Return a configuration with both point types and ownership directions."""
    raw = valid_config()
    raw["version"] = 2
    raw["tags"].extend(
        [
            {
                "name": "simulated_speed_raw",
                "plc_symbol": "DB_SimulationProof.SimulatedSpeedRaw",
                "address": "DB14.DBW12",
                "data_type": "WORD",
                "direction": "pc_to_plc",
                "safe_value": 0,
            },
            {
                "name": "measured_temperature_raw",
                "plc_symbol": "DB_SimulationProof.MeasuredTemperatureRaw",
                "address": "DB14.DBW14",
                "data_type": "INT",
                "direction": "plc_to_pc",
            },
        ]
    )
    raw["points"] = [
        {
            "name": "simulated_photoeye",
            "kind": "digital",
            "tag": "pc_to_plc",
            "group": "line_one",
            "inverted": True,
        },
        {
            "name": "conveyor_running",
            "kind": "digital",
            "tag": "plc_to_pc",
            "group": "line_one",
        },
        {
            "name": "simulated_speed",
            "kind": "analog",
            "tag": "simulated_speed_raw",
            "group": "line_one",
            "raw_min": 0,
            "raw_max": 27648,
            "engineering_min": 0,
            "engineering_max": 100,
            "unit": "percent",
            "out_of_range": "clamp",
        },
        {
            "name": "measured_temperature",
            "kind": "analog",
            "tag": "measured_temperature_raw",
            "group": "line_one",
            "raw_min": -27648,
            "raw_max": 27648,
            "engineering_min": -50,
            "engineering_max": 150,
            "unit": "deg_c",
            "out_of_range": "fault",
        },
    ]
    return raw


class PointModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = parse_config(valid_point_config())
        self.model = PointModel(self.config)

    def test_point_ownership_is_inherited_from_tag(self) -> None:
        self.assertIs(
            self.model.direction("simulated_photoeye"),
            Direction.PC_TO_PLC,
        )
        self.assertIs(
            self.model.direction("conveyor_running"),
            Direction.PLC_TO_PC,
        )

    def test_digital_inversion_is_symmetric(self) -> None:
        decoded = self.model.decode("simulated_photoeye", False)
        encoded = self.model.encode_pc_value("simulated_photoeye", True)

        self.assertIs(decoded.value, True)
        self.assertIs(encoded.raw_value, False)
        self.assertIs(encoded.quality, PointQuality.GOOD)

    def test_analog_decode_scales_midpoint(self) -> None:
        sample = self.model.decode("simulated_speed", 13824)

        self.assertEqual(sample.value, 50.0)
        self.assertEqual(sample.raw_value, 13824)
        self.assertEqual(sample.unit, "percent")
        self.assertIs(sample.quality, PointQuality.GOOD)

    def test_analog_encode_scales_and_rounds_for_integer_tag(self) -> None:
        sample = self.model.encode_pc_value("simulated_speed", 25.0)

        self.assertEqual(sample.value, 25.0)
        self.assertEqual(sample.raw_value, 6912)
        self.assertIs(sample.quality, PointQuality.GOOD)

    def test_clamp_policy_reports_high_clamp(self) -> None:
        decoded = self.model.decode("simulated_speed", 30000)
        encoded = self.model.encode_pc_value("simulated_speed", 120)

        self.assertEqual(decoded.value, 100.0)
        self.assertIs(decoded.quality, PointQuality.CLAMPED_HIGH)
        self.assertEqual(encoded.value, 100.0)
        self.assertEqual(encoded.raw_value, 27648)
        self.assertIs(encoded.quality, PointQuality.CLAMPED_HIGH)

    def test_fault_policy_returns_non_writable_diagnostic(self) -> None:
        raw = valid_point_config()
        raw["points"][2]["out_of_range"] = "fault"
        model = PointModel(parse_config(raw))

        sample = model.encode_pc_value("simulated_speed", -1)

        self.assertIsNone(sample.raw_value)
        self.assertFalse(sample.conversion_succeeded)
        self.assertIs(sample.quality, PointQuality.FAULT_LOW)

    def test_fault_policy_preserves_bad_raw_value_for_diagnostics(self) -> None:
        sample = self.model.decode("measured_temperature", 30000)

        self.assertIsNone(sample.value)
        self.assertEqual(sample.raw_value, 30000)
        self.assertIs(sample.quality, PointQuality.FAULT_HIGH)

    def test_reverse_engineering_scale_is_supported(self) -> None:
        raw = valid_point_config()
        raw["points"][2]["engineering_min"] = 100
        raw["points"][2]["engineering_max"] = 0
        model = PointModel(parse_config(raw))

        decoded = model.decode("simulated_speed", 6912)
        encoded = model.encode_pc_value("simulated_speed", 75)

        self.assertEqual(decoded.value, 75.0)
        self.assertEqual(encoded.raw_value, 6912)

    def test_plc_owned_point_cannot_be_encoded_for_write(self) -> None:
        with self.assertRaisesRegex(PointValueError, "PLC-owned"):
            self.model.encode_pc_value("conveyor_running", True)

    def test_safe_sample_is_scene_facing(self) -> None:
        digital = self.model.safe_sample("simulated_photoeye")
        analog = self.model.safe_sample("simulated_speed")
        plc_owned = self.model.safe_sample("conveyor_running")

        self.assertIsNotNone(digital)
        self.assertIs(digital.value, True)
        self.assertIsNotNone(analog)
        self.assertEqual(analog.value, 0.0)
        self.assertIsNone(plc_owned)

    def test_address_groups_preserve_ownership_and_flag_shared_byte(self) -> None:
        groups = build_address_groups(self.config)
        pc_byte_zero = next(
            group
            for group in groups
            if group.direction is Direction.PC_TO_PLC
            and group.db_number == 14
            and group.start_byte == 0
        )
        plc_byte_zero = next(
            group
            for group in groups
            if group.direction is Direction.PLC_TO_PC
            and group.db_number == 14
            and group.start_byte == 0
        )
        pc_analog = next(
            group
            for group in groups
            if "simulated_speed_raw" in group.tag_names
        )

        self.assertEqual(pc_byte_zero.tag_names, ("pc_to_plc",))
        self.assertTrue(pc_byte_zero.shares_byte_with_opposite_owner)
        self.assertTrue(plc_byte_zero.shares_byte_with_opposite_owner)
        self.assertEqual(pc_analog.start_byte, 12)
        self.assertEqual(pc_analog.byte_length, 2)
        self.assertFalse(pc_analog.shares_byte_with_opposite_owner)


if __name__ == "__main__":
    unittest.main()
