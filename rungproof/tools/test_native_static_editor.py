"""Contract tests for the native static authoring boundary."""

from __future__ import annotations

import copy
import tempfile
from pathlib import Path
import unittest

try:
    from .native_static_editor import (
        DraftAsset,
        StaticDraftError,
        build_static_draft_targets,
        build_static_draft_document,
        load_static_draft,
        parse_static_draft,
        save_static_draft,
        snap_static_transform,
        suggest_non_overlapping_position,
        suggest_asset_position,
    )
except ImportError:
    from native_static_editor import (
        DraftAsset,
        StaticDraftError,
        build_static_draft_targets,
        build_static_draft_document,
        load_static_draft,
        parse_static_draft,
        save_static_draft,
        snap_static_transform,
        suggest_non_overlapping_position,
        suggest_asset_position,
    )


class NativeStaticEditorContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assets = (
            DraftAsset("conveyor", "main_conveyor", "Main conveyor", (0.0, 0.0, 0.0)),
            DraftAsset("box", "inspection_box", "Inspection box", (0.0, 1.2, 0.0), 15.0, 0.9),
        )

    def test_build_is_schema_valid_and_behavior_free(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        self.assertEqual(document["simulation"], {"type": "static"})
        self.assertNotIn("plcTestProfile", document)
        self.assertEqual(parse_static_draft(document), self.assets)

    def test_round_trip_preserves_symbolic_layout(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "draft.plcscene"
            save_static_draft(path, document)
            loaded, assets = load_static_draft(path)
        self.assertEqual(loaded["id"], "static-review-01")
        self.assertEqual(assets, self.assets)

    def test_round_trip_preserves_bounded_editor_view(self) -> None:
        editor_view = {
            "yawDegrees": 58.0,
            "pitchDegrees": 40.0,
            "zoom": 1.24,
            "panX": 2.5,
            "panY": -1.0,
        }
        document = build_static_draft_document(
            draft_id="static-review-01",
            name="Static review",
            assets=self.assets,
            editor_view=editor_view,
        )
        self.assertEqual(document["editorView"], editor_view)
        self.assertEqual(parse_static_draft(document), self.assets)

    def test_rejects_malformed_or_unsafe_editor_view(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        malformed = copy.deepcopy(document)
        malformed["editorView"] = {"yawDegrees": 10.0}
        with self.assertRaisesRegex(StaticDraftError, "missing"):
            parse_static_draft(malformed)
        unsafe = copy.deepcopy(document)
        unsafe["editorView"] = {
            "yawDegrees": 10.0,
            "pitchDegrees": 0.0,
            "zoom": 1.0,
            "panX": 0.0,
            "panY": 0.0,
            "runtime": True,
        }
        with self.assertRaisesRegex(StaticDraftError, "unsupported keys"):
            parse_static_draft(unsafe)
        non_finite = copy.deepcopy(document)
        non_finite["editorView"] = {
            "yawDegrees": float("nan"),
            "pitchDegrees": 28.0,
            "zoom": 1.0,
            "panX": 0.0,
            "panY": 0.0,
        }
        with self.assertRaisesRegex(StaticDraftError, "finite"):
            parse_static_draft(non_finite)

    def test_rejects_pan_outside_actual_viewport_range(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        document["editorView"] = {
            "yawDegrees": 34.0,
            "pitchDegrees": 28.0,
            "zoom": 1.0,
            "panX": 401.0,
            "panY": 0.0,
        }
        with self.assertRaisesRegex(StaticDraftError, "pan"):
            parse_static_draft(document)

    def test_targets_are_stable_and_cover_each_placed_asset(self) -> None:
        targets = build_static_draft_targets(self.assets)
        self.assertEqual(
            tuple(target.target_id for target in targets),
            ("main_conveyor", "inspection_box"),
        )
        for target in targets:
            self.assertLess(target.bounds[0], target.bounds[3])
            self.assertLess(target.bounds[1], target.bounds[4])
            self.assertLess(target.bounds[2], target.bounds[5])
            self.assertEqual(target.status, "STATIC DRAFT")
            self.assertGreater(len(target.outline_points), 8)

    def test_long_asset_labels_use_compact_overlay_identity(self) -> None:
        assets = (
            DraftAsset(
                "conveyor",
                "main_conveyor",
                "Discharge conveyor / Cell A",
                (0.0, 0.0, 0.0),
            ),
        )
        target = build_static_draft_targets(assets)[0]
        self.assertEqual(target.label, "Discharge conveyor")

    def test_new_asset_positions_use_non_overlapping_grid_slots(self) -> None:
        self.assertEqual(suggest_asset_position(0), (-3.0, 0.0, 0.0))
        self.assertEqual(suggest_asset_position(1), (0.0, 0.0, 0.0))
        self.assertEqual(suggest_asset_position(2), (3.0, 0.0, 0.0))
        self.assertEqual(suggest_asset_position(3), (-3.0, 0.0, 2.8))
        with self.assertRaises(ValueError):
            suggest_asset_position(-1)

    def test_snap_static_transform_uses_stable_authoring_increments(self) -> None:
        self.assertEqual(
            snap_static_transform((1.13, -0.12, 2.38), 13.0, 0.97),
            ((1.25, 0.0, 2.5), 15.0, 0.95),
        )

    def test_new_asset_position_clears_existing_conveyor_drive_area(self) -> None:
        position = suggest_non_overlapping_position("motor", self.assets)
        self.assertEqual(position, (5.0, 0.0, 0.0))

    def test_rejects_controller_profile_and_runtime_points(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        with self.assertRaisesRegex(StaticDraftError, "PLC profiles"):
            parse_static_draft({**document, "plcTestProfile": "scene-2.json"})
        with self.assertRaisesRegex(StaticDraftError, "runtime points"):
            runtime_document = copy.deepcopy(document)
            runtime_document["simulation"]["points"] = [
                {"name": "unsafe", "type": "BOOL", "owner": "PLC", "initial": False}
            ]
            parse_static_draft(runtime_document)

    def test_rejects_behavior_and_non_native_assets(self) -> None:
        document = build_static_draft_document(
            draft_id="static-review-01", name="Static review", assets=self.assets
        )
        behavior_document = copy.deepcopy(document)
        behavior_document["simulation"]["actions"] = []
        with self.assertRaisesRegex(StaticDraftError, "runtime points or behavior"):
            parse_static_draft(behavior_document)
        invalid_document = copy.deepcopy(document)
        invalid_document["equipment"][0]["type"] = "customRobot"
        with self.assertRaises(StaticDraftError):
            parse_static_draft(invalid_document)


if __name__ == "__main__":
    unittest.main()
