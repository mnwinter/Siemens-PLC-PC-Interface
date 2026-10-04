"""Deterministic tests for the presentation-only Scene 2 inspection layer."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from tools.native_inspection import (
    build_scene2_targets,
    hit_test_targets,
    inspection_source_text,
    is_click_gesture,
)


class NativeInspectionTests(unittest.TestCase):
    def test_scene2_targets_have_unique_expected_ids(self) -> None:
        targets = build_scene2_targets(
            SimpleNamespace(object_present=True, object_leading_edge_m=0.10)
        )
        ids = [target.target_id for target in targets]
        self.assertEqual(
            ids,
            ["main_conveyor", "photoeye", "pusher", "drive_motor", "stacklight", "package"],
        )
        self.assertEqual(len(ids), len(set(ids)))

    def test_empty_projected_point_hits_nothing(self) -> None:
        targets = build_scene2_targets(
            SimpleNamespace(object_present=True, object_leading_edge_m=0.10)
        )
        self.assertIsNone(
            hit_test_targets((99.0, 99.0), targets, lambda point: (point[0], point[1]))
        )

    def test_package_priority_wins_over_conveyor(self) -> None:
        targets = build_scene2_targets(
            SimpleNamespace(object_present=True, object_leading_edge_m=0.10)
        )
        package = next(target for target in targets if target.target_id == "package")
        center = (
            (package.bounds[0] + package.bounds[3]) / 2,
            (package.bounds[1] + package.bounds[4]) / 2,
        )
        selected = hit_test_targets(center, targets, lambda point: (point[0], point[1]))
        self.assertIsNotNone(selected)
        self.assertEqual(selected.target_id, "package")

    def test_package_is_absent_without_a_position(self) -> None:
        targets = build_scene2_targets(SimpleNamespace(object_present=True))
        self.assertNotIn("package", {target.target_id for target in targets})

    def test_drag_threshold_rejects_selection_gesture(self) -> None:
        self.assertTrue(is_click_gesture(4.9, 0.0))
        self.assertFalse(is_click_gesture(5.0, 0.0))
        self.assertFalse(is_click_gesture(0.0, -8.0))

    def test_disconnected_inspection_wording_is_explicit(self) -> None:
        self.assertEqual(
            inspection_source_text(True),
            "LOCAL MODEL / PLC STATE NOT VERIFIED",
        )


if __name__ == "__main__":
    unittest.main()
