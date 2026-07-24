"""Unit tests for the offline configuration-validation command."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from siemens_plc_pc_interface.cli import main
from test_config import valid_config


class CliTests(unittest.TestCase):
    def test_valid_config_reports_no_plc_connection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(
                json.dumps(valid_config()),
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                result = main(["validate", str(path)])

        self.assertEqual(result, 0)
        self.assertIn("CONFIG_VALID: True", output.getvalue())
        self.assertIn(
            "PLC_CONNECTION_ATTEMPTED: False",
            output.getvalue(),
        )

    def test_invalid_config_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("{}", encoding="utf-8")
            errors = io.StringIO()

            with redirect_stderr(errors):
                result = main(["validate", str(path)])

        self.assertEqual(result, 2)
        self.assertIn("CONFIG_INVALID:", errors.getvalue())

    def test_run_without_execute_never_connects(self) -> None:
        class NoConnectTransport:
            connected = False

            def connect(self, connection: object) -> None:
                raise AssertionError("dry run attempted a PLC connection")

            def disconnect(self) -> None:
                return None

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(
                json.dumps(valid_config()),
                encoding="utf-8",
            )
            output = io.StringIO()

            with (
                patch(
                    "siemens_plc_pc_interface.cli.Snap7Transport",
                    return_value=NoConnectTransport(),
                ),
                redirect_stdout(output),
            ):
                result = main(["run", str(path), "--cycles", "1"])

        self.assertEqual(result, 2)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", output.getvalue())
        self.assertIn(
            "pc_to_plc=DB14.DBX0.0:BOOL",
            output.getvalue(),
        )

    def test_run_rejects_assignment_to_plc_owned_tag_before_connect(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(
                json.dumps(valid_config()),
                encoding="utf-8",
            )
            output = io.StringIO()
            errors = io.StringIO()

            with (
                redirect_stdout(output),
                redirect_stderr(errors),
            ):
                result = main(
                    [
                        "run",
                        str(path),
                        "--set",
                        "plc_to_pc=true",
                        "--execute",
                        "--cycles",
                        "1",
                    ]
                )

        self.assertEqual(result, 2)
        self.assertIn("PLC_CONNECTION_ATTEMPTED: False", output.getvalue())
        self.assertIn("PLC-owned", errors.getvalue())

    def test_finite_fake_runtime_requires_and_reports_heartbeat_progress(self) -> None:
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

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "valid.json"
            path.write_text(
                json.dumps(valid_config()),
                encoding="utf-8",
            )
            output = io.StringIO()

            with (
                patch(
                    "siemens_plc_pc_interface.cli.Snap7Transport",
                    return_value=EchoTransport(),
                ),
                patch("siemens_plc_pc_interface.cli.time.sleep"),
                redirect_stdout(output),
            ):
                result = main(
                    [
                        "run",
                        str(path),
                        "--execute",
                        "--cycles",
                        "2",
                    ]
                )

        self.assertEqual(result, 0)
        self.assertIn("HEARTBEAT_PROOF: PASS", output.getvalue())
        self.assertIn('"simulation_comm_ok":true', output.getvalue())


if __name__ == "__main__":
    unittest.main()
