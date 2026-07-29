"""Unit tests for the typed simulation update loop and diagnostics."""

from __future__ import annotations

import io
import json
import unittest

from siemens_plc_pc_interface.config import ConfigError, parse_config
from siemens_plc_pc_interface.points import PointQuality, PointValueError
from siemens_plc_pc_interface.runtime import InterfaceRuntime
from siemens_plc_pc_interface.update_loop import (
    DiagnosticLevel,
    JsonLinesUpdateLogger,
    LoopHealth,
    SimulationUpdateLoop,
)
from test_config import valid_config
from test_points import valid_point_config
from test_runtime import FakeTransport, initial_plc_values


def point_plc_values() -> dict[str, bool | int | float]:
    """Return all PLC-owned values required by the typed test config."""
    return {
        **initial_plc_values(),
        "measured_temperature_raw": 0,
    }


class SimulationUpdateLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = parse_config(valid_point_config())
        self.transport = FakeTransport(point_plc_values())
        self.runtime = InterfaceRuntime(
            self.config,
            self.transport,
            start_time=0.0,
        )
        self.runtime.connect()
        self.loop = SimulationUpdateLoop(self.runtime)

    def _establish_healthy_heartbeat(self) -> None:
        first = self.loop.step(0.0, {})
        self.assertIs(first.health, LoopHealth.STARTING)
        self.transport.plc_values["plc_heartbeat_echo"] = 1
        second = self.loop.step(0.1, {})
        self.assertIs(second.health, LoopHealth.HEALTHY)

    def test_first_cycle_reports_starting_and_all_typed_samples(self) -> None:
        result = self.loop.step(0.0, {})

        self.assertIs(result.health, LoopHealth.STARTING)
        self.assertEqual(
            set(result.pc_point_samples),
            {"simulated_photoeye", "simulated_speed"},
        )
        self.assertEqual(
            set(result.plc_point_samples),
            {"conveyor_running", "measured_temperature"},
        )
        self.assertIs(
            result.pc_point_samples["simulated_photoeye"].value,
            True,
        )
        self.assertEqual(
            result.plc_point_samples["measured_temperature"].value,
            50.0,
        )
        self.assertEqual(result.diagnostics, ())

    def test_progressing_echo_and_good_points_report_healthy(self) -> None:
        self.loop.step(0.0, {})
        self.transport.plc_values["plc_heartbeat_echo"] = 1
        self.transport.plc_values["plc_to_pc"] = True
        self.transport.plc_values["measured_temperature_raw"] = 13_824

        result = self.loop.step(
            0.1,
            {
                "simulated_photoeye": False,
                "simulated_speed": 25.0,
            },
        )

        self.assertIs(result.health, LoopHealth.HEALTHY)
        self.assertIs(
            result.plc_point_samples["conveyor_running"].value,
            True,
        )
        self.assertEqual(
            result.plc_point_samples["measured_temperature"].value,
            100.0,
        )
        self.assertEqual(
            result.pc_point_samples["simulated_speed"].raw_value,
            6_912,
        )

    def test_clamped_pc_point_is_written_and_reports_degraded(self) -> None:
        self._establish_healthy_heartbeat()
        self.transport.plc_values["plc_heartbeat_echo"] = 2

        result = self.loop.step(0.2, {"simulated_speed": 120.0})

        self.assertIs(result.health, LoopHealth.DEGRADED)
        self.assertEqual(
            result.pc_point_samples["simulated_speed"].raw_value,
            27_648,
        )
        self.assertIn(
            ("simulated_speed_raw", 27_648),
            self.transport.writes,
        )
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIs(
            result.diagnostics[0].quality,
            PointQuality.CLAMPED_HIGH,
        )
        self.assertIs(
            result.diagnostics[0].level,
            DiagnosticLevel.WARNING,
        )

    def test_faulted_pc_point_skips_write_and_reports_fault(self) -> None:
        raw = valid_point_config()
        raw["points"][2]["out_of_range"] = "fault"
        transport = FakeTransport(point_plc_values())
        runtime = InterfaceRuntime(
            parse_config(raw),
            transport,
            start_time=0.0,
        )
        runtime.connect()
        loop = SimulationUpdateLoop(runtime)
        loop.step(0.0, {})
        transport.plc_values["plc_heartbeat_echo"] = 1
        writes_before = len(transport.writes)

        result = loop.step(0.1, {"simulated_speed": -1.0})

        self.assertIs(result.health, LoopHealth.FAULT)
        self.assertIsNone(
            result.pc_point_samples["simulated_speed"].raw_value,
        )
        self.assertNotIn(
            "simulated_speed_raw",
            result.cycle.pc_values_written,
        )
        self.assertEqual(len(transport.writes), writes_before + 1)
        self.assertIn(
            "PLC write skipped",
            result.diagnostics[0].message,
        )

    def test_plc_point_range_fault_preserves_raw_diagnostic(self) -> None:
        self.loop.step(0.0, {})
        self.transport.plc_values["plc_heartbeat_echo"] = 1
        self.transport.plc_values["measured_temperature_raw"] = 30_000

        result = self.loop.step(0.1, {})

        sample = result.plc_point_samples["measured_temperature"]
        self.assertIs(result.health, LoopHealth.FAULT)
        self.assertIsNone(sample.value)
        self.assertEqual(sample.raw_value, 30_000)
        self.assertIs(sample.quality, PointQuality.FAULT_HIGH)
        self.assertNotIn(
            "PLC write skipped",
            result.diagnostics[0].message,
        )

    def test_plc_owned_scene_input_is_rejected_before_cycle(self) -> None:
        with self.assertRaisesRegex(PointValueError, "PLC-owned"):
            self.loop.step(0.0, {"conveyor_running": True})

        self.assertEqual(self.transport.reads, [])
        self.assertEqual(self.transport.writes, [])

    def test_invalid_input_batch_does_not_stage_earlier_values(self) -> None:
        with self.assertRaisesRegex(PointValueError, "PLC-owned"):
            self.loop.step(
                0.0,
                {
                    "simulated_speed": 25.0,
                    "conveyor_running": True,
                },
            )

        result = self.loop.step(0.0, {})

        self.assertEqual(
            result.pc_point_samples["simulated_speed"].value,
            0.0,
        )
        self.assertEqual(
            result.cycle.pc_values_written["simulated_speed_raw"],
            0,
        )

    def test_missing_pc_point_retains_last_accepted_value(self) -> None:
        first = self.loop.step(0.0, {"simulated_speed": 25.0})
        self.assertEqual(
            first.pc_point_samples["simulated_speed"].value,
            25.0,
        )
        self.transport.plc_values["plc_heartbeat_echo"] = 1

        second = self.loop.step(0.1, {})

        self.assertEqual(
            second.pc_point_samples["simulated_speed"].value,
            25.0,
        )
        self.assertNotIn(
            "simulated_speed_raw",
            second.cycle.pc_values_written,
        )

    def test_json_lines_logger_emits_structured_cycle_record(self) -> None:
        stream = io.StringIO()
        loop = SimulationUpdateLoop(
            self.runtime,
            logger=JsonLinesUpdateLogger(stream),
        )

        result = loop.step(0.0, {"simulated_speed": 50.0})
        record = json.loads(stream.getvalue())

        self.assertEqual(record["cycle"], result.cycle.cycle_number)
        self.assertEqual(record["health"], "starting")
        self.assertEqual(
            record["heartbeat"]["reason"],
            "waiting_for_first_echo",
        )
        self.assertEqual(
            record["pc_points"]["simulated_speed"]["raw_value"],
            13_824,
        )
        self.assertEqual(
            record["plc_points"]["measured_temperature"]["unit"],
            "deg_c",
        )

    def test_stalled_echo_reports_fault(self) -> None:
        self._establish_healthy_heartbeat()

        result = self.loop.step(1.101, {})

        self.assertIs(result.health, LoopHealth.FAULT)
        self.assertEqual(result.cycle.heartbeat.reason, "echo_stalled")

    def test_schema_without_points_is_rejected(self) -> None:
        transport = FakeTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            parse_config(valid_config()),
            transport,
        )

        with self.assertRaisesRegex(ConfigError, "schema version 2"):
            SimulationUpdateLoop(runtime)


if __name__ == "__main__":
    unittest.main()
