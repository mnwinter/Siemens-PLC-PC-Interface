"""Header Scene-menu catalog tests for the native RungProof app."""

from __future__ import annotations

import unittest

from tools.native_runtime import SCENE_FILE, SCENE_ID
from tools.native_scene_catalog import load_native_scene_catalog
from tools.native_scene_library import NATIVE_SCENE_BY_ID


class NativeSceneCatalogTests(unittest.TestCase):
    def test_catalog_lists_all_source_scenes_without_enabling_fallbacks(
        self,
    ) -> None:
        catalog = load_native_scene_catalog(
            SCENE_FILE.parent,
            live_scene_ids={SCENE_ID},
            review_scene_ids=set(NATIVE_SCENE_BY_ID),
        )

        production = tuple(
            entry for entry in catalog if entry.category == "production"
        )
        review = tuple(entry for entry in catalog if entry.category == "review")
        tools = tuple(entry for entry in catalog if entry.category == "tool")
        labs = tuple(entry for entry in catalog if entry.category == "lab")

        self.assertEqual(len(catalog), 77)
        self.assertEqual(len(production), 2)
        self.assertEqual(len(review), 4)
        self.assertEqual(len(tools), 1)
        self.assertEqual(len(labs), 70)
        self.assertEqual(production[0].scene_id, "scene-1-conveyor-stop")
        self.assertEqual(production[1].scene_id, SCENE_ID)
        self.assertEqual(
            tuple(entry.scene_id for entry in review),
            ("conveyor-cell", "tank-level", "tank-high-low", "tank-radar"),
        )
        self.assertEqual(tools[0].scene_id, "equipment-gallery")
        self.assertEqual(labs[0].scene_id, "lab-2-01-workstation-call")
        self.assertEqual(labs[-1].scene_id, "lab-11-19-powder-batch-mixer")
        self.assertEqual(
            {entry.scene_id for entry in catalog if entry.live_available},
            {SCENE_ID},
        )
        self.assertEqual(
            {entry.scene_id for entry in catalog if entry.review_available},
            set(NATIVE_SCENE_BY_ID),
        )
        self.assertTrue(
            all(
                not entry.selectable
                for entry in labs
            )
        )


if __name__ == "__main__":
    unittest.main()
