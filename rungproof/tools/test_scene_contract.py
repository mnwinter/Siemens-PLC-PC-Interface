"""Cross-language persistence-adapter tests for the v1 scene contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

try:
    from .scene_contract import SceneContractError, validate_scene_document
except ImportError:
    from scene_contract import SceneContractError, validate_scene_document


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "prototype" / "scene.schema.json"
SCENES = ROOT / "prototype" / "scenes"


class SceneContractTests(unittest.TestCase):
    def _load(self, file_name: str) -> dict[str, object]:
        return json.loads((SCENES / file_name).read_text(encoding="utf-8"))

    def test_every_built_in_scene_is_valid_for_server_persistence(self) -> None:
        paths = sorted((*SCENES.glob("*.plcscene"), *SCENES.glob("*.json")))

        self.assertEqual(len(paths), 32)
        for path in paths:
            with self.subTest(path=path.name):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertIs(
                    validate_scene_document(document, SCHEMA),
                    document,
                )

    def test_rejects_unbounded_geometry_and_unknown_config(self) -> None:
        document = self._load("equipment-gallery.json")
        fan = next(
            item
            for item in document["equipment"]
            if item["type"] == "fan"
        )
        fan["config"]["bladeCount"] = 1_000_000_000
        with self.assertRaisesRegex(SceneContractError, "bladeCount"):
            validate_scene_document(document, SCHEMA)

        document = self._load("equipment-gallery.json")
        document["equipment"][0]["config"]["surpriseAllocation"] = 42
        with self.assertRaisesRegex(
            SceneContractError,
            "Additional properties are not allowed",
        ):
            validate_scene_document(document, SCHEMA)

    def test_rejects_missing_equipment_and_wrong_point_writes(self) -> None:
        document = self._load("lab-2-01-workstation-call.plcscene")
        document["simulation"]["pointBindings"][0]["equipmentId"] = "missing"
        with self.assertRaisesRegex(SceneContractError, "equipmentId"):
            validate_scene_document(document, SCHEMA)

        document = self._load("lab-2-01-workstation-call.plcscene")
        document["simulation"]["rules"][0]["set"][
            "material_call_on"
        ] = "wrong"
        with self.assertRaisesRegex(SceneContractError, "wrong value type"):
            validate_scene_document(document, SCHEMA)

    def test_document_is_not_mutated(self) -> None:
        document = self._load("scene-2-conveyor-pusher.plcscene")
        before = copy.deepcopy(document)
        validate_scene_document(document, SCHEMA)
        self.assertEqual(document, before)

    def test_training_guides_and_cumulative_lineage_are_complete(self) -> None:
        paths = sorted(SCENES.glob("lab-2-*.plcscene"))
        self.assertEqual(len(paths), 25)
        previous_id = None
        for sequence, path in enumerate(paths, start=1):
            with self.subTest(path=path.name):
                document = json.loads(path.read_text(encoding="utf-8"))
                validate_scene_document(document, SCHEMA)
                training = document["training"]
                self.assertEqual(training["sequenceNumber"], sequence)
                self.assertEqual(
                    training["foundation"],
                    "common-plc-watchdog-foundation",
                )
                self.assertTrue(training["machineGuide"]["purpose"])
                self.assertTrue(training["machineGuide"]["normalSequence"])
                self.assertTrue(training["machineGuide"]["faultBehavior"])
                self.assertTrue(training["retainedTags"])
                if previous_id is None:
                    self.assertEqual(
                        training["inheritsFrom"],
                        "common-plc-watchdog-foundation",
                    )
                else:
                    self.assertEqual(training["inheritsFrom"], previous_id)
                    self.assertIn(previous_id, training["previousAcceptance"])
                previous_id = document["id"]


if __name__ == "__main__":
    unittest.main()
