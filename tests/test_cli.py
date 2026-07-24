"""Unit tests for the offline configuration-validation command."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
