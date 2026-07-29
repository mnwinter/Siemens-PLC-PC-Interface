"""Unit tests for configuration validation."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from siemens_plc_pc_interface.config import (
    AnalogPointConfig,
    ConfigError,
    DataType,
    DigitalPointConfig,
    Direction,
    OutOfRangePolicy,
    load_config,
    parse_config,
)


def valid_config() -> dict:
    """Return an independent, valid DB14 configuration."""
    return {
        "version": 1,
        "connection": {
            "cpu_family": "s7-1500",
            "ip": "10.70.9.201",
            "rack": 0,
            "slot": 1,
            "cycle_ms": 100,
            "connect_timeout_ms": 2_000,
        },
        "heartbeat": {
            "pc_tag": "pc_heartbeat",
            "echo_tag": "plc_heartbeat_echo",
            "timeout_ms": 1_000,
        },
        "tags": [
            {
                "name": "pc_to_plc",
                "plc_symbol": "DB_SimulationProof.PC_To_PLC",
                "address": "DB14.DBX0.0",
                "data_type": "BOOL",
                "direction": "pc_to_plc",
                "safe_value": False,
            },
            {
                "name": "plc_to_pc",
                "plc_symbol": "DB_SimulationProof.PLC_To_PC",
                "address": "DB14.DBX0.1",
                "data_type": "BOOL",
                "direction": "plc_to_pc",
            },
            {
                "name": "pc_heartbeat",
                "plc_symbol": "DB_SimulationProof.PC_Heartbeat",
                "address": "DB14.DBD2",
                "data_type": "DINT",
                "direction": "pc_to_plc",
                "safe_value": 0,
            },
            {
                "name": "plc_heartbeat_echo",
                "plc_symbol": "DB_SimulationProof.PLC_Heartbeat_Echo",
                "address": "DB14.DBD6",
                "data_type": "DINT",
                "direction": "plc_to_pc",
            },
            {
                "name": "simulation_enable",
                "plc_symbol": "DB_SimulationProof.Simulation_Enable",
                "address": "DB14.DBX10.0",
                "data_type": "BOOL",
                "direction": "plc_to_pc",
            },
            {
                "name": "simulation_comm_ok",
                "plc_symbol": "DB_SimulationProof.Simulation_Comm_OK",
                "address": "DB14.DBX10.1",
                "data_type": "BOOL",
                "direction": "plc_to_pc",
            },
            {
                "name": "simulation_timeout",
                "plc_symbol": "DB_SimulationProof.Simulation_Timeout",
                "address": "DB14.DBX10.2",
                "data_type": "BOOL",
                "direction": "plc_to_pc",
            },
        ],
    }


class ConfigTests(unittest.TestCase):
    def test_valid_config_is_typed(self) -> None:
        config = parse_config(valid_config())

        self.assertEqual(config.connection.ip, "10.70.9.201")
        self.assertEqual(config.connection.rack, 0)
        self.assertEqual(config.connection.slot, 1)
        self.assertEqual(config.heartbeat.timeout_ms, 1_000)
        self.assertEqual(len(config.tags), 7)

        pc_bool = config.tag("pc_to_plc")
        self.assertIs(pc_bool.data_type, DataType.BOOL)
        self.assertIs(pc_bool.direction, Direction.PC_TO_PLC)
        self.assertEqual(pc_bool.snap7_tag, "DB14.DBX0.0:BOOL")
        self.assertEqual(config.points, ())

    def test_five_millisecond_cycle_is_allowed_for_rate_testing(
        self,
    ) -> None:
        raw = valid_config()
        raw["connection"]["cycle_ms"] = 5

        config = parse_config(raw)

        self.assertEqual(config.connection.cycle_ms, 5)

    def test_cycle_below_five_milliseconds_is_rejected(self) -> None:
        raw = valid_config()
        raw["connection"]["cycle_ms"] = 4

        with self.assertRaisesRegex(
            ConfigError,
            r"connection\.cycle_ms must be between 5 and 5000",
        ):
            parse_config(raw)

    def test_version_one_rejects_point_extension(self) -> None:
        raw = valid_config()
        raw["points"] = []

        with self.assertRaisesRegex(ConfigError, "unknown field.*points"):
            parse_config(raw)

    def test_unknown_schema_version_is_rejected(self) -> None:
        raw = valid_config()
        raw["version"] = 3

        with self.assertRaisesRegex(ConfigError, "version must be 1 or 2"):
            parse_config(raw)

    def test_version_two_requires_at_least_one_point(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["points"] = []

        with self.assertRaisesRegex(ConfigError, "at least one point"):
            parse_config(raw)

    def test_digital_and_analog_points_are_typed(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["tags"].append(
            {
                "name": "simulated_speed_raw",
                "plc_symbol": "DB_SimulationProof.SimulatedSpeedRaw",
                "address": "DB14.DBW12",
                "data_type": "WORD",
                "direction": "pc_to_plc",
                "safe_value": 0,
            }
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
        ]

        config = parse_config(raw)

        digital = config.point("simulated_photoeye")
        analog = config.point("simulated_speed")
        self.assertIsInstance(digital, DigitalPointConfig)
        self.assertTrue(digital.inverted)
        self.assertIsInstance(analog, AnalogPointConfig)
        self.assertEqual(analog.raw_max, 27648)
        self.assertIs(analog.out_of_range, OutOfRangePolicy.CLAMP)

    def test_point_type_must_match_tag_type(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["points"] = [
            {
                "name": "bad_analog",
                "kind": "analog",
                "tag": "pc_to_plc",
                "group": "proof",
                "raw_min": 0,
                "raw_max": 1,
                "engineering_min": 0,
                "engineering_max": 100,
                "unit": "percent",
                "out_of_range": "fault",
            }
        ]

        with self.assertRaisesRegex(ConfigError, "numeric tag"):
            parse_config(raw)

    def test_point_cannot_expose_internal_heartbeat(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["points"] = [
            {
                "name": "heartbeat_as_scene_point",
                "kind": "analog",
                "tag": "pc_heartbeat",
                "group": "proof",
                "raw_min": 0,
                "raw_max": 100,
                "engineering_min": 0,
                "engineering_max": 100,
                "unit": "count",
                "out_of_range": "fault",
            }
        ]

        with self.assertRaisesRegex(ConfigError, "internal heartbeat"):
            parse_config(raw)

    def test_analog_raw_range_must_be_ordered(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["tags"].append(
            {
                "name": "simulated_speed_raw",
                "plc_symbol": "DB_SimulationProof.SimulatedSpeedRaw",
                "address": "DB14.DBW12",
                "data_type": "WORD",
                "direction": "pc_to_plc",
                "safe_value": 0,
            }
        )
        raw["points"] = [
            {
                "name": "simulated_speed",
                "kind": "analog",
                "tag": "simulated_speed_raw",
                "group": "line_one",
                "raw_min": 27648,
                "raw_max": 0,
                "engineering_min": 0,
                "engineering_max": 100,
                "unit": "percent",
                "out_of_range": "clamp",
            }
        ]

        with self.assertRaisesRegex(ConfigError, "raw_min must be less"):
            parse_config(raw)

    def test_analog_range_must_contain_pc_safe_value(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["tags"].append(
            {
                "name": "simulated_speed_raw",
                "plc_symbol": "DB_SimulationProof.SimulatedSpeedRaw",
                "address": "DB14.DBW12",
                "data_type": "WORD",
                "direction": "pc_to_plc",
                "safe_value": 0,
            }
        )
        raw["points"] = [
            {
                "name": "simulated_speed",
                "kind": "analog",
                "tag": "simulated_speed_raw",
                "group": "line_one",
                "raw_min": 1000,
                "raw_max": 27648,
                "engineering_min": 0,
                "engineering_max": 100,
                "unit": "percent",
                "out_of_range": "clamp",
            }
        ]

        with self.assertRaisesRegex(ConfigError, "contain.*safe_value"):
            parse_config(raw)

    def test_two_points_cannot_control_the_same_tag(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["points"] = [
            {
                "name": "photoeye_one",
                "kind": "digital",
                "tag": "pc_to_plc",
                "group": "line_one",
            },
            {
                "name": "photoeye_two",
                "kind": "digital",
                "tag": "pc_to_plc",
                "group": "line_two",
            },
        ]

        with self.assertRaisesRegex(ConfigError, "duplicates point tag"):
            parse_config(raw)

    def test_invalid_ip_is_rejected(self) -> None:
        raw = valid_config()
        raw["connection"]["ip"] = "10.70.9.999"

        with self.assertRaisesRegex(ConfigError, "valid IPv4"):
            parse_config(raw)

    def test_physical_io_address_is_rejected(self) -> None:
        raw = valid_config()
        raw["tags"][0]["address"] = "%I0.0"

        with self.assertRaisesRegex(ConfigError, "absolute DB address"):
            parse_config(raw)

    def test_data_type_must_match_address_area(self) -> None:
        raw = valid_config()
        raw["tags"][0]["data_type"] = "BYTE"
        raw["tags"][0]["safe_value"] = 0

        with self.assertRaisesRegex(ConfigError, "area DBX requires"):
            parse_config(raw)

    def test_overlapping_memory_is_rejected(self) -> None:
        raw = valid_config()
        raw["tags"].append(
            {
                "name": "overlap_byte",
                "plc_symbol": "DB_SimulationProof.OverlapByte",
                "address": "DB14.DBB0",
                "data_type": "BYTE",
                "direction": "pc_to_plc",
                "safe_value": 0,
            }
        )

        with self.assertRaisesRegex(ConfigError, "overlaps tag"):
            parse_config(raw)

    def test_duplicate_name_is_rejected(self) -> None:
        raw = valid_config()
        raw["tags"][1]["name"] = "pc_to_plc"

        with self.assertRaisesRegex(ConfigError, "duplicates"):
            parse_config(raw)

    def test_pc_owned_tag_requires_safe_value(self) -> None:
        raw = valid_config()
        del raw["tags"][0]["safe_value"]

        with self.assertRaisesRegex(ConfigError, "safe_value is required"):
            parse_config(raw)

    def test_real_safe_value_must_be_finite(self) -> None:
        raw = valid_config()
        raw["tags"].append(
            {
                "name": "simulated_speed",
                "plc_symbol": "DB_SimulationProof.SimulatedSpeed",
                "address": "DB14.DBD12",
                "data_type": "REAL",
                "direction": "pc_to_plc",
                "safe_value": float("inf"),
            }
        )

        with self.assertRaisesRegex(ConfigError, "finite 32-bit REAL"):
            parse_config(raw)

    def test_plc_owned_tag_cannot_define_non_null_safe_value(self) -> None:
        raw = valid_config()
        raw["tags"][1]["safe_value"] = False

        with self.assertRaisesRegex(ConfigError, "must be omitted or null"):
            parse_config(raw)

    def test_heartbeat_timeout_requires_two_cycles(self) -> None:
        raw = valid_config()
        raw["heartbeat"]["timeout_ms"] = 100

        with self.assertRaisesRegex(ConfigError, "at least twice"):
            parse_config(raw)

    def test_heartbeat_direction_is_validated(self) -> None:
        raw = valid_config()
        raw["tags"][2]["direction"] = "plc_to_pc"
        del raw["tags"][2]["safe_value"]

        with self.assertRaisesRegex(ConfigError, "pc_to_plc DINT"):
            parse_config(raw)

    def test_heartbeat_data_type_is_validated(self) -> None:
        raw = valid_config()
        raw["tags"][2]["data_type"] = "REAL"
        raw["tags"][2]["safe_value"] = 0.0

        with self.assertRaisesRegex(ConfigError, "pc_to_plc DINT"):
            parse_config(raw)

    def test_unknown_field_is_rejected(self) -> None:
        raw = valid_config()
        raw["connection"]["password"] = "do-not-accept-secrets"

        with self.assertRaisesRegex(ConfigError, "unknown field"):
            parse_config(raw)

    def test_invalid_json_reports_line_and_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{\n  "version": 1,\n', encoding="utf-8")

            with self.assertRaisesRegex(
                ConfigError,
                r"line \d+, column \d+",
            ):
                load_config(path)

    def test_file_load_matches_direct_parse(self) -> None:
        raw = valid_config()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(json.dumps(raw), encoding="utf-8")

            loaded = load_config(path)

        direct = parse_config(copy.deepcopy(raw))
        self.assertEqual(loaded, direct)


if __name__ == "__main__":
    unittest.main()
