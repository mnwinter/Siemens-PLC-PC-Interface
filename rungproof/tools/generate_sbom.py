"""Generate a deterministic CycloneDX inventory from locked release inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "requirements-build.lock"
VERSION_FILE = REPO_ROOT / "VERSION"
LOCK_LINE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s]+)$")


def locked_python_components() -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(
        LOCK_FILE.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        requirement = line.split(" --hash=", 1)[0]
        match = LOCK_LINE.fullmatch(requirement)
        if match is None:
            raise ValueError(
                f"Unsupported lock entry at {LOCK_FILE}:{line_number}: {line}"
            )
        name, version = match.groups()
        normalized = name.lower().replace("_", "-")
        components.append(
            {
                "type": "library",
                "bom-ref": f"pkg:pypi/{normalized}@{version}",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{normalized}@{version}",
                "scope": "required",
            }
        )
    return components


def build_sbom() -> dict[str, object]:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    application_ref = f"pkg:generic/rungproof@{version}"
    components = locked_python_components()
    components.extend(
        [
            {
                "type": "library",
                "bom-ref": "pkg:github/mrdoob/three.js@r179",
                "name": "three.js",
                "version": "r179",
                "purl": "pkg:github/mrdoob/three.js@r179",
                "scope": "excluded",
                "properties": [
                    {
                        "name": "rungproof:package-status",
                        "value": "source-prototype-only; not in native package",
                    }
                ],
            },
            {
                "type": "library",
                "bom-ref": (
                    "pkg:github/mnwinter/Siemens-PLC-PC-Interface@"
                    "754fcfb88192f2a932bd7df70feea0d08088ab97"
                ),
                "name": "Siemens-PLC-PC-Interface snapshot",
                "version": "754fcfb88192f2a932bd7df70feea0d08088ab97",
                "scope": "required",
            },
        ]
    )
    required_refs = [
        component["bom-ref"]
        for component in components
        if component.get("scope") == "required"
    ]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:rungproof-{version}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": application_ref,
                "name": "RungProof - PLC Visual Simulator",
                "version": version,
                "purl": application_ref,
            },
            "properties": [
                {
                    "name": "rungproof:inventory-source",
                    "value": "VERSION + requirements-build.lock + pinned vendor provenance",
                }
            ],
        },
        "components": components,
        "dependencies": [
            {"ref": application_ref, "dependsOn": required_refs},
            *({"ref": ref, "dependsOn": []} for ref in required_refs),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_sbom(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"SBOM: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
