"""Release metadata must have one version source across code and packaging."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from tools.generate_sbom import build_sbom
from tools.rungproof_native import APP_VERSION
from tools.verify_vendor_manifest import verify as verify_vendor_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?$"
)


class ReleaseMetadataTests(unittest.TestCase):
    def test_version_is_valid_and_shared_with_package_metadata(self) -> None:
        version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        package = json.loads(
            (REPO_ROOT / "package.json").read_text(encoding="utf-8")
        )

        self.assertRegex(version, SEMVER)
        self.assertEqual(APP_VERSION, version)
        self.assertEqual(package["version"], version)

    def test_builder_uses_version_file_as_the_release_authority(self) -> None:
        builder = (REPO_ROOT / "tools" / "build_vm_exe.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn('Join-Path $repoRoot "VERSION"', builder)
        self.assertIn("$PackageVersion = $declaredVersion", builder)
        self.assertNotIn('[string]$PackageVersion = "0.1.0"', builder)

    def test_builder_removes_conflicting_versioned_icu_runtime(self) -> None:
        builder = (REPO_ROOT / "tools" / "build_vm_exe.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn('$conflictingQtIcu = Join-Path $packageDir "icuuc.dll"', builder)
        self.assertIn(
            "Remove-Item -LiteralPath $conflictingQtIcu -Force",
            builder,
        )

    def test_source_launcher_uses_package_module_entrypoint(self) -> None:
        launcher = (REPO_ROOT / "RUN-3D-PLAYER.cmd").read_text(
            encoding="utf-8"
        )
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("-m tools.rungproof_native", launcher)
        self.assertNotIn("python.exe\" tools\\rungproof_native.py", launcher)
        self.assertIn("-m tools.rungproof_native", readme)

    def test_real_plc_package_requires_an_explicit_build_switch(self) -> None:
        builder = (REPO_ROOT / "tools" / "build_vm_exe.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("[switch]$EnableRealPlc", builder)
        self.assertIn("realPlcWritesEnabled = [bool]$EnableRealPlc", builder)
        self.assertIn('"operator-authorized-live-bench"', builder)
        self.assertNotIn("BenchAcceptancePath", builder)
        self.assertIn('"docs\\LIVE_PLC_PILOT_CHECKLIST.md"', builder)
        self.assertIn('"packaging\\vm\\BENCH-PREFLIGHT.ps1"', builder)
        self.assertIn('"packaging\\vm\\VALIDATE-BENCH-RESULT.ps1"', builder)
        self.assertIn('"packaging\\vm\\VALIDATE-BENCH-DELTA.ps1"', builder)
        self.assertIn('"packaging\\vm\\DELTA-RETEST-QUICKSTART.txt"', builder)

    def test_bench_preflight_is_offline_and_acceptance_is_hash_bound(self) -> None:
        preflight = (
            REPO_ROOT / "packaging" / "vm" / "BENCH-PREFLIGHT.ps1"
        ).read_text(encoding="utf-8")
        validator = (
            REPO_ROOT / "packaging" / "vm" / "VALIDATE-BENCH-RESULT.ps1"
        ).read_text(encoding="utf-8")
        delta_validator = (
            REPO_ROOT / "packaging" / "vm" / "VALIDATE-BENCH-DELTA.ps1"
        ).read_text(encoding="utf-8")

        for forbidden in (
            "snap7",
            "Test-NetConnection",
            "Invoke-WebRequest",
            "Invoke-RestMethod",
            "ping.exe",
        ):
            self.assertNotIn(forbidden, preflight)
        self.assertIn('plcConnectionAttempted = $false', preflight)
        self.assertIn('preflightSha256 = &$hash $preflightPath', preflight)
        self.assertIn("BENCH-RESULT.json is not tied", validator)
        self.assertIn('approval.result must be exactly PASS', validator)
        self.assertIn("BENCH-DELTA-RESULT.json is not tied", delta_validator)
        self.assertIn("baseline preflight/result/acceptance hash chain", delta_validator)
        self.assertIn("not compatible with the accepted baseline", delta_validator)

    def test_release_lane_requires_clean_git_and_collects_evidence(self) -> None:
        runner = (REPO_ROOT / "tools" / "run_checks.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "release verification requires a clean git working tree",
            runner.lower(),
        )
        self.assertIn("collect_release_evidence.ps1", runner)
        self.assertIn("tools.test_native_qt", runner)
        self.assertIn("tools.test_native_static_editor_qt", runner)

    def test_release_lane_forwards_live_plc_capability_to_build_and_smoke(self) -> None:
        runner = (REPO_ROOT / "tools" / "run_checks.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("[switch]$EnableRealPlc", runner)
        self.assertIn('$buildArguments += "-EnableRealPlc"', runner)
        self.assertIn(
            '$smokeArguments += "-ExpectRealPlcWritesEnabled"',
            runner,
        )

    def test_sbom_contains_release_and_required_runtime_components(self) -> None:
        sbom = build_sbom()
        components = sbom["components"]
        names = {component["name"] for component in components}

        self.assertEqual(sbom["metadata"]["component"]["version"], APP_VERSION)
        self.assertIn("PySide6", names)
        self.assertIn("python-snap7", names)
        self.assertIn("Siemens-PLC-PC-Interface snapshot", names)
        three = next(
            component for component in components if component["name"] == "three.js"
        )
        self.assertEqual(three["scope"], "excluded")

    def test_every_locked_python_artifact_has_a_sha256_hash(self) -> None:
        entries = [
            line.strip()
            for line in (REPO_ROOT / "requirements-build.lock")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip() and not line.startswith("#")
        ]

        self.assertTrue(entries)
        for entry in entries:
            with self.subTest(entry=entry):
                self.assertRegex(entry, r"^[^=]+==[^ ]+ --hash=sha256:[0-9a-f]{64}$")

        builder = (REPO_ROOT / "tools" / "build_vm_exe.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn("--require-hashes", builder)
        self.assertIn("Path(r'$requirementsLockFile')", builder)

    def test_vendored_siemens_source_matches_its_audited_manifest(self) -> None:
        verify_vendor_manifest()


if __name__ == "__main__":
    unittest.main()
