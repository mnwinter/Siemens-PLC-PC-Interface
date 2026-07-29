"""CLI tests for guarded first-scene validation and execution."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from siemens_plc_pc_interface.cli import main


ROOT = Path(__file__).resolve().parents[1]
INTERFACE = ROOT / "examples" / "db14-conveyor-interface.json"
SCENE = ROOT / "examples" / "conveyor-scene.json"
FAST_SCENE = ROOT / "examples" / "conveyor-scene-fast.json"


class SceneCliTests(unittest.TestCase):
    def test_scene_validate_reports_timing_and_no_connection(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            result = main(
                ["scene-validate", str(INTERFACE), str(SCENE)]
            )

        text = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("SCENE_VALID: True", text)
        self.assertIn("PLC_EXCHANGE_MS: 20", text)
        self.assertIn("PHYSICS_STEP_MS: 10", text)
        self.assertIn("PHYSICS_STEPS_PER_EXCHANGE: 2", text)
        self.assertIn("COMPONENT: conveyor_1", text)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", text)

    def test_scene_run_without_execute_never_connects(self) -> None:
        class NoConnectTransport:
            connected = False

            def connect(self, connection: object) -> None:
                raise AssertionError("dry run attempted a PLC connection")

            def disconnect(self) -> None:
                return None

        output = io.StringIO()
        with (
            patch(
                "siemens_plc_pc_interface.cli.Snap7Transport",
                return_value=NoConnectTransport(),
            ),
            redirect_stdout(output),
        ):
            result = main(
                ["scene-run", str(INTERFACE), str(SCENE), "--cycles", "1"]
            )

        self.assertEqual(result, 2)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", output.getvalue())
        self.assertIn("pc_to_plc=DB14.DBX0.0:BOOL", output.getvalue())

    def test_scene_visualize_without_execute_never_connects(self) -> None:
        class NoConnectTransport:
            connected = False

            def connect(self, connection: object) -> None:
                raise AssertionError("visual preview attempted a PLC connection")

            def disconnect(self) -> None:
                return None

        output = io.StringIO()
        with (
            patch(
                "siemens_plc_pc_interface.cli.Snap7Transport",
                return_value=NoConnectTransport(),
            ),
            redirect_stdout(output),
        ):
            result = main(
                [
                    "scene-visualize",
                    str(INTERFACE),
                    str(FAST_SCENE),
                ]
            )

        text = output.getvalue()
        self.assertEqual(result, 2)
        self.assertIn("VIEW: GRAPHICAL CONVEYOR AND PHOTOEYE", text)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", text)
        self.assertIn("pc_to_plc=DB14.DBX0.0:BOOL", text)

    def test_scene_visualize_execute_dispatches_to_viewer(self) -> None:
        output = io.StringIO()
        with (
            patch(
                "siemens_plc_pc_interface.visualizer.run_scene_visualizer",
                return_value=0,
            ) as viewer,
            redirect_stdout(output),
        ):
            result = main(
                [
                    "scene-visualize",
                    str(INTERFACE),
                    str(FAST_SCENE),
                    "--execute",
                    "--cycles",
                    "3",
                ]
            )

        self.assertEqual(result, 0)
        viewer.assert_called_once()
        _, runtime = viewer.call_args.args
        self.assertEqual(runtime.write_scope[0].name, "pc_to_plc")
        self.assertEqual(runtime.write_scope[1].name, "pc_heartbeat")
        self.assertEqual(viewer.call_args.kwargs["cycles"], 3)

    def test_cycle_override_is_validated_against_fast_scene(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            result = main(
                [
                    "scene-run",
                    str(INTERFACE),
                    str(FAST_SCENE),
                    "--cycle-ms",
                    "5",
                    "--cycles",
                    "1",
                ]
            )

        text = output.getvalue()
        self.assertEqual(result, 2)
        self.assertIn("PLC_EXCHANGE_MS: 5", text)
        self.assertIn("PHYSICS_STEPS_PER_EXCHANGE: 1", text)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", text)

    def test_cycle_override_preserves_heartbeat_timeout_rule(self) -> None:
        output = io.StringIO()
        errors = io.StringIO()

        with (
            redirect_stdout(output),
            redirect_stderr(errors),
        ):
            result = main(
                [
                    "scene-run",
                    str(INTERFACE),
                    str(FAST_SCENE),
                    "--cycle-ms",
                    "505",
                    "--cycles",
                    "1",
                ]
            )

        self.assertEqual(result, 2)
        self.assertIn("SCENE_INVALID:", errors.getvalue())
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", output.getvalue())

    def test_finite_fake_scene_proves_heartbeat_and_timing(self) -> None:
        class EchoTransport:
            def __init__(self) -> None:
                self.connected = False
                self.values = {
                    "plc_to_pc": True,
                    "plc_heartbeat_echo": 0,
                    "simulation_enable": True,
                    "simulation_comm_ok": True,
                    "simulation_timeout": False,
                }

            def connect(self, connection: object) -> None:
                self.connected = True

            def disconnect(self) -> None:
                self.connected = False

            def read(self, tag: object) -> object:
                return self.values[tag.name]

            def write(self, tag: object, value: object) -> None:
                if tag.name == "pc_heartbeat":
                    self.values["plc_heartbeat_echo"] = value

        output = io.StringIO()
        with (
            patch(
                "siemens_plc_pc_interface.cli.Snap7Transport",
                return_value=EchoTransport(),
            ),
            redirect_stdout(output),
        ):
            result = main(
                [
                    "scene-run",
                    str(INTERFACE),
                    str(SCENE),
                    "--execute",
                    "--cycles",
                    "2",
                ]
            )

        text = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("S7_SESSION_CONNECTED: True", text)
        self.assertIn("SCENE_CYCLE 2:", text)
        self.assertIn("TIMING: cycles=2", text)
        self.assertIn("HEARTBEAT_PROOF: PASS", text)

    def test_scene_output_is_throttled_but_final_cycle_is_reported(
        self,
    ) -> None:
        class EchoTransport:
            def __init__(self) -> None:
                self.connected = False
                self.values = {
                    "plc_to_pc": False,
                    "plc_heartbeat_echo": 0,
                    "simulation_enable": True,
                    "simulation_comm_ok": True,
                    "simulation_timeout": False,
                }

            def connect(self, connection: object) -> None:
                self.connected = True

            def disconnect(self) -> None:
                self.connected = False

            def read(self, tag: object) -> object:
                return self.values[tag.name]

            def write(self, tag: object, value: object) -> None:
                if tag.name == "pc_heartbeat":
                    self.values["plc_heartbeat_echo"] = value

        output = io.StringIO()
        with (
            patch(
                "siemens_plc_pc_interface.cli.Snap7Transport",
                return_value=EchoTransport(),
            ),
            redirect_stdout(output),
        ):
            result = main(
                [
                    "scene-run",
                    str(INTERFACE),
                    str(SCENE),
                    "--execute",
                    "--cycles",
                    "6",
                    "--report-every",
                    "5",
                ]
            )

        text = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("REPORT_EVERY_CYCLES: 5", text)
        self.assertIn("SCENE_CYCLE 1:", text)
        self.assertIn("SCENE_CYCLE 2:", text)
        self.assertNotIn("SCENE_CYCLE 3:", text)
        self.assertNotIn("SCENE_CYCLE 4:", text)
        self.assertIn("SCENE_CYCLE 5:", text)
        self.assertIn("SCENE_CYCLE 6:", text)

    def test_invalid_scene_fails_before_connection(self) -> None:
        errors = io.StringIO()
        output = io.StringIO()

        with (
            redirect_stdout(output),
            redirect_stderr(errors),
        ):
            result = main(
                ["scene-run", str(INTERFACE), str(INTERFACE), "--execute"]
            )

        self.assertEqual(result, 2)
        self.assertIn("SCENE_INVALID:", errors.getvalue())
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", output.getvalue())


if __name__ == "__main__":
    unittest.main()
