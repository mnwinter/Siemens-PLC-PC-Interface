"""Verify portable source hashes still reject adapter changes/inventory drift."""
from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import verify_vendor_manifest as verifier


class VendorManifestTests(unittest.TestCase):
    def test_line_endings_are_portable_but_source_changes_are_rejected(self) -> None:
        with TemporaryDirectory() as folder:
            root = Path(folder)
            package = root / "siemens_plc_pc_interface"
            package.mkdir()
            source = package / "runtime.py"
            canonical = b"# Reviewed fixture\nvalue = 1\n"
            manifest = root / "SOURCE-SHA256.txt"
            manifest.write_text(
                hashlib.sha256(canonical).hexdigest()
                + "  siemens_plc_pc_interface/runtime.py\n", encoding="utf-8"
            )
            with patch.object(verifier, "VENDOR_ROOT", root), patch.object(verifier, "MANIFEST", manifest):
                for content in (canonical, canonical.replace(b"\n", b"\r\n")):
                    source.write_bytes(content)
                    verifier.verify()
                source.write_bytes(canonical.replace(b"value = 1", b"value = 2"))
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    verifier.verify()
                source.write_bytes(canonical)
                extra = package / "extra.py"
                extra.write_text("", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                    verifier.verify()
                extra.unlink()
                source.unlink()
                with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                    verifier.verify()


if __name__ == "__main__":
    unittest.main()
