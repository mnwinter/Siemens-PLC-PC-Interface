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
