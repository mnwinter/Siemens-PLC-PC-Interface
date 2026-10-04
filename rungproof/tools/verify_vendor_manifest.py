"""Verify the exact audited Siemens adapter source before packaging."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = REPO_ROOT / "vendor" / "siemens-plc-pc-interface"
MANIFEST = VENDOR_ROOT / "SOURCE-SHA256.txt"
ENTRY = re.compile(r"^([0-9a-f]{64})  ([a-zA-Z0-9_./-]+)$")


def verify() -> None:
    expected: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = ENTRY.fullmatch(raw_line)
        if match is None:
            raise ValueError(f"Invalid vendor manifest line {line_number}.")
        digest, relative = match.groups()
        if relative in expected:
            raise ValueError(f"Duplicate vendor manifest path: {relative}")
        expected[relative] = digest

    actual_paths = {
        path.relative_to(VENDOR_ROOT).as_posix()
        for path in (VENDOR_ROOT / "siemens_plc_pc_interface").glob("*.py")
    }
    if actual_paths != set(expected):
        raise ValueError(
            "Vendor manifest inventory mismatch; "
            f"missing={sorted(actual_paths - set(expected))}, "
            f"extra={sorted(set(expected) - actual_paths)}"
        )

    for relative, expected_digest in expected.items():
        path = (VENDOR_ROOT / relative).resolve()
        if path.parent != (VENDOR_ROOT / relative).parent.resolve():
            raise ValueError(f"Vendor source path escaped its folder: {relative}")
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(f"Vendor source hash mismatch: {relative}")


def main() -> int:
    verify()
    print(f"VENDOR_SOURCE_SHA256: PASS ({MANIFEST})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
