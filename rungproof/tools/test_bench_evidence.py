"""Tests for the packaged live-PLC bench evidence validator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "packaging" / "vm" / "VALIDATE-BENCH-RESULT.ps1"
DELTA_VALIDATOR = REPO_ROOT / "packaging" / "vm" / "VALIDATE-BENCH-DELTA.ps1"


class BenchEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rungproof-bench-evidence-")
        self.evidence = Path(self.temp.name)
        self.preflight_path = self.evidence / "BENCH-PREFLIGHT.json"
        self.result_path = self.evidence / "BENCH-RESULT.json"
        self.preflight = {
            "schemaVersion": 1,
            "packageVersion": "0.2.0-pilot.1",
            "hashes": {
                "executableSha256": "1" * 64,
                "profileSha256": "2" * 64,
            },
            "target": {
                "cpuFamily": "s7-1500",
                "ip": "10.70.9.201",
                "rack": 0,
                "slot": 1,
            },
        }
        self._write_json(self.preflight_path, self.preflight)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _write_json(path: Path, document: object) -> None:
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def _preflight_hash(self) -> str:
        return hashlib.sha256(self.preflight_path.read_bytes()).hexdigest()

    def _result(self, *, passed: bool) -> dict[str, object]:
        value = True if passed else None
        return {
            "schemaVersion": 1,
            "preflightSha256": self._preflight_hash(),
            "bench": {
                "tiaPortalVersion": "V17 Update test",
                "cpuOrderNumber": "AUTOMATED-TEST",
                "cpuFirmware": "AUTOMATED-TEST",
                "vmPlatform": "AUTOMATED-TEST",
                "noPhysicalIoConnected": value,
                "db14StandardNonOptimized": value,
                "profileEndpointConfirmed": value,
            },
            "observations": {
                "tiaCompilePassed": value,
                "readOnlyZeroWritesObserved": value,
                "exactWriteScopeObserved": value,
                "twoCyclesPassed": value,
                "stopFreshRunPassed": value,
                "resetPassed": value,
                "heartbeatLossSafe": value,
                "networkLossSafe": value,
                "reconnectFreshRunPassed": value,
                "disconnectSafe": value,
                "closeSafe": value,
            },
            "approval": {
                "result": "PASS" if passed else "",
                "approvedBy": "AUTOMATED VALIDATOR TEST",
                "approvedAt": "2026-08-05T00:00:00Z",
            },
            "notes": "Synthetic validator test; not live PLC evidence.",
        }

    def _validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(VALIDATOR),
                "-EvidenceDirectory",
                str(self.evidence),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_incomplete_live_observations_are_rejected(self) -> None:
        self._write_json(self.result_path, self._result(passed=False))

        completed = self._validate()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Bench acceptance is incomplete", completed.stderr)
        self.assertFalse((self.evidence / "BENCH-ACCEPTANCE.json").exists())

    def test_result_must_match_the_current_preflight_hash(self) -> None:
        result = self._result(passed=True)
        result["preflightSha256"] = "0" * 64
        self._write_json(self.result_path, result)

        completed = self._validate()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not tied to the current preflight", completed.stderr)
        self.assertFalse((self.evidence / "BENCH-ACCEPTANCE.json").exists())

    def test_complete_passing_result_creates_hash_bound_acceptance(self) -> None:
        self._write_json(self.result_path, self._result(passed=True))

        completed = self._validate()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        acceptance = json.loads(
            (self.evidence / "BENCH-ACCEPTANCE.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(acceptance["result"], "PASS")
        self.assertEqual(acceptance["preflightSha256"], self._preflight_hash())
        self.assertEqual(acceptance["approvedBy"], "AUTOMATED VALIDATOR TEST")

    def test_legacy_unused_step_field_does_not_block_acceptance(self) -> None:
        result = self._result(passed=True)
        result["observations"]["stepPassed"] = None
        self._write_json(self.result_path, result)

        completed = self._validate()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((self.evidence / "BENCH-ACCEPTANCE.json").exists())


class BenchDeltaEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="rungproof-bench-delta-")
        root = Path(self.temp.name)
        self.baseline = root / "baseline"
        self.current = root / "current"
        self.baseline.mkdir()
        self.current.mkdir()
        self.target = {
            "cpuFamily": "s7-1500",
            "ip": "10.70.9.201",
            "rack": 0,
            "slot": 1,
            "cycleMs": 20,
            "connectTimeoutMs": 2000,
            "heartbeatTimeoutMs": 1000,
        }
        self._write_json(
            self.baseline / "BENCH-PREFLIGHT.json",
            self._preflight(
                executable="1" * 64,
                package_version="0.2.0-pilot.1",
            ),
        )
        self._write_json(
            self.current / "BENCH-PREFLIGHT.json",
            self._preflight(
                executable="3" * 64,
                package_version="0.2.0-pilot.2",
            ),
        )
        self._write_json(
            self.baseline / "BENCH-RESULT.json",
            self._full_result(self.baseline / "BENCH-PREFLIGHT.json"),
        )
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(VALIDATOR),
                "-EvidenceDirectory",
                str(self.baseline),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _write_json(path: Path, document: object) -> None:
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    @staticmethod
    def _hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _preflight(
        self,
        *,
        executable: str,
        package_version: str,
    ) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "packageVersion": package_version,
            "hashes": {
                "executableSha256": executable,
                "profileSha256": "2" * 64,
                "packageManifestSha256": "4" * 64,
            },
            "target": self.target,
        }

    def _full_result(self, preflight_path: Path) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "preflightSha256": self._hash(preflight_path),
            "bench": {
                "tiaPortalVersion": "V17 Update test",
                "cpuOrderNumber": "AUTOMATED-TEST",
                "cpuFirmware": "AUTOMATED-TEST",
                "vmPlatform": "AUTOMATED-TEST",
                "noPhysicalIoConnected": True,
                "db14StandardNonOptimized": True,
                "profileEndpointConfirmed": True,
            },
            "observations": {
                "tiaCompilePassed": True,
                "readOnlyZeroWritesObserved": True,
                "exactWriteScopeObserved": True,
                "twoCyclesPassed": True,
                "stopFreshRunPassed": True,
                "resetPassed": True,
                "heartbeatLossSafe": True,
                "networkLossSafe": True,
                "reconnectFreshRunPassed": True,
                "disconnectSafe": True,
                "closeSafe": True,
            },
            "approval": {
                "result": "PASS",
                "approvedBy": "AUTOMATED VALIDATOR TEST",
                "approvedAt": "2026-08-05T00:00:00Z",
            },
            "notes": "Synthetic baseline; not live evidence.",
        }

    def _delta_result(self, *, passed: bool = True) -> dict[str, object]:
        value = True if passed else None
        return {
            "schemaVersion": 1,
            "changeId": "disconnect-telemetry-truthfulness",
            "preflightSha256": self._hash(
                self.current / "BENCH-PREFLIGHT.json"
            ),
            "baselineAcceptanceSha256": self._hash(
                self.baseline / "BENCH-ACCEPTANCE.json"
            ),
            "observations": {
                "normalCyclePassed": value,
                "exactWriteScopeReconfirmed": value,
                "disconnectTelemetryUnavailable": value,
                "disconnectWatchdogSafe": value,
                "networkLossTelemetryUnavailable": value,
                "networkLossPlantSafe": value,
                "automaticReconnectPassed": value,
                "reconnectFreshRunPassed": value,
                "closeSafe": value,
            },
            "approval": {
                "result": "PASS" if passed else "",
                "approvedBy": "AUTOMATED DELTA TEST",
                "approvedAt": "2026-08-05T00:00:00Z",
            },
            "notes": "Synthetic delta; not live evidence.",
        }

    def _validate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(DELTA_VALIDATOR),
                "-EvidenceDirectory",
                str(self.current),
                "-BaselineEvidenceDirectory",
                str(self.baseline),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_complete_delta_creates_hash_bound_lineage_acceptance(self) -> None:
        self._write_json(
            self.current / "BENCH-DELTA-RESULT.json",
            self._delta_result(),
        )

        completed = self._validate()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        acceptance = json.loads(
            (self.current / "BENCH-DELTA-ACCEPTANCE.json").read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(acceptance["qualification"], "delta")
        self.assertEqual(acceptance["result"], "PASS")
        self.assertEqual(
            acceptance["baseline"]["acceptanceSha256"],
            self._hash(self.baseline / "BENCH-ACCEPTANCE.json"),
        )

    def test_incomplete_delta_is_rejected(self) -> None:
        self._write_json(
            self.current / "BENCH-DELTA-RESULT.json",
            self._delta_result(passed=False),
        )

        completed = self._validate()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Bench delta acceptance is incomplete", completed.stderr)
        self.assertFalse(
            (self.current / "BENCH-DELTA-ACCEPTANCE.json").exists()
        )

    def test_delta_rejects_a_different_profile_contract(self) -> None:
        current_preflight = self._preflight(
            executable="3" * 64,
            package_version="0.2.0-pilot.2",
        )
        current_preflight["hashes"]["profileSha256"] = "9" * 64
        self._write_json(
            self.current / "BENCH-PREFLIGHT.json",
            current_preflight,
        )
        self._write_json(
            self.current / "BENCH-DELTA-RESULT.json",
            self._delta_result(),
        )

        completed = self._validate()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not compatible with the accepted baseline", completed.stderr)

    def test_delta_rejects_reusing_the_baseline_version(self) -> None:
        self._write_json(
            self.current / "BENCH-PREFLIGHT.json",
            self._preflight(
                executable="3" * 64,
                package_version="0.2.0-pilot.1",
            ),
        )
        self._write_json(
            self.current / "BENCH-DELTA-RESULT.json",
            self._delta_result(),
        )

        completed = self._validate()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("pilot.1 baseline and pilot.2 candidate", completed.stderr)


if __name__ == "__main__":
    unittest.main()
