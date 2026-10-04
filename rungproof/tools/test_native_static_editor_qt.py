"""Qt lifecycle checks for native static authoring history and view state."""

from __future__ import annotations

import importlib.util
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

HAS_PYSIDE = importlib.util.find_spec("PySide6") is not None

if HAS_PYSIDE:
    from tools.rungproof_native import _qt_imports
    from tools.native_static_editor import StaticSceneEditorDialog


@unittest.skipUnless(HAS_PYSIDE, "PySide6 is required for native Qt checks")
class NativeStaticEditorQtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from PySide6 import QtWidgets

        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_add_undo_redo_restores_symbolic_layout(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.palette_list.setCurrentRow(0)
        dialog._add_asset()
        self.app.processEvents()
        self.assertEqual(len(dialog.assets), 3)
        self.assertTrue(dialog.undo_button.isEnabled())

        dialog._undo()
        self.app.processEvents()
        self.assertEqual(len(dialog.assets), 2)
        self.assertTrue(dialog.redo_button.isEnabled())

        dialog._redo()
        self.app.processEvents()
        self.assertEqual(len(dialog.assets), 3)
        self.assertFalse(dialog.redo_button.isEnabled())
        dialog.dialog.done(0)

    def test_document_captures_and_restores_inspection_view(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.viewport._yaw_degrees = 58.0
        dialog.viewport._pitch_degrees = 40.0
        dialog.viewport._zoom = 1.24
        dialog.viewport._pan_x = 2.5
        dialog.viewport._pan_y = -1.0
        document = dialog._document()
        self.assertEqual(document["editorView"]["yawDegrees"], 58.0)
        dialog.viewport.reset_camera()
        dialog._restore_editor_view(document)
        self.assertEqual(dialog.viewport._yaw_degrees, 58.0)
        self.assertEqual(dialog.viewport._pitch_degrees, 40.0)
        self.assertEqual(dialog.viewport._zoom, 1.24)
        self.assertEqual(dialog.viewport._pan_x, 2.5)
        self.assertEqual(dialog.viewport._pan_y, -1.0)
        dialog.dialog.done(0)

    def test_duplicate_stages_a_collision_free_symbolic_copy(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        dialog._duplicate_asset()
        self.app.processEvents()
        self.assertEqual(len(dialog.assets), 3)
        self.assertEqual(dialog.assets[-1].asset_type, "conveyor")
        self.assertEqual(dialog.assets[-1].label, "Main conveyor copy")
        self.assertEqual(dialog.assets[-1].position, (5.0, 0.0, 4.5))
        dialog.dialog.done(0)

    def test_copy_paste_creates_a_fresh_collision_free_symbolic_asset(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        dialog._copy_asset()
        dialog._paste_asset()
        self.app.processEvents()
        self.assertEqual(len(dialog.assets), 3)
        self.assertEqual(dialog.assets[-1].asset_type, "conveyor")
        self.assertEqual(dialog.assets[-1].label, "Main conveyor copy")
        self.assertNotEqual(dialog.assets[-1].instance_id, dialog.assets[0].instance_id)
        self.assertEqual(dialog.assets[-1].yaw_degrees, dialog.assets[0].yaw_degrees)
        self.assertEqual(dialog.assets[-1].scale, dialog.assets[0].scale)
        dialog.dialog.done(0)

    def test_validation_gate_accepts_symbolic_draft_and_invalidates_on_edit(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        self.assertTrue(dialog._validate_draft())
        self.assertTrue(dialog._validation_state)
        self.assertTrue(dialog.preview_button.isEnabled())
        self.assertIn("VALID", dialog.validation_badge.text())

        dialog.draft_name.setText("Edited after validation")
        self.assertFalse(dialog._validation_state)
        self.assertFalse(dialog.preview_button.isEnabled())
        self.assertIn("NOT VALIDATED", dialog.validation_badge.text())
        dialog.dialog.done(0)

    def test_review_scenario_is_authored_and_part_of_history(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        initial_history = len(dialog._history)
        dialog.scenario_fields["cycle"].setText("Index carton to inspection point")
        dialog.scenario_fields["alarm_id"].setText("guard_open")
        dialog._record_history()
        document = dialog._document()
        self.assertEqual(
            document["reviewScenario"]["sequence"][1]["label"],
            "Index carton to inspection point",
        )
        self.assertEqual(document["reviewScenario"]["alarm"]["id"], "guard_open")
        self.assertEqual(len(dialog._history), initial_history + 1)
        dialog._undo()
        self.assertEqual(
            dialog._document()["reviewScenario"]["sequence"][1]["label"],
            "Local cycle / asset outputs active",
        )
        dialog.dialog.done(0)

    def test_review_player_handoff_is_interactive_and_fail_closed(self) -> None:
        from PySide6 import QtWidgets

        dialog = StaticSceneEditorDialog(_qt_imports())
        self.assertTrue(dialog._validate_draft())
        handoff = dialog._build_review_player_dialog(dialog._document())
        self.assertEqual(handoff.windowTitle(), "RungProof | Review Player Handoff")
        self.assertIn("PLC DISABLED", handoff._review_scope.text())
        self.assertIn("NO TRANSPORT", handoff._review_scope.text())
        self.assertIn("PROVENANCE", handoff._review_summary.text())
        self.assertEqual(
            handoff._review_viewport.geometry,
            tuple(dialog.viewport.geometry),
        )
        self.assertIsNotNone(handoff._review_viewport.container)
        handoff.resize(980, 620)
        handoff.show()
        self.app.processEvents()
        self.assertTrue(handoff._review_viewport.compact_display)
        buttons = {
            button.text(): button
            for button in handoff.findChildren(QtWidgets.QPushButton)
        }
        buttons["Run"].click()
        self.app.processEvents()
        self.assertTrue(handoff._review_runtime.snapshot().cycle_active)
        self.assertIn("review_run=1", handoff._review_runtime_points.text())
        buttons["Raise alarm"].click()
        self.app.processEvents()
        self.assertTrue(handoff._review_runtime.snapshot().fault_active)
        buttons["Acknowledge"].click()
        buttons["Clear"].click()
        self.app.processEvents()
        self.assertFalse(handoff._review_runtime.snapshot().fault_active)
        handoff.done(0)
        dialog.dialog.done(0)

    def test_transform_spinbox_gesture_creates_one_history_step(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        initial_history = len(dialog._history)
        dialog.fields["x"].setValue(1.0)
        dialog.fields["x"].setValue(2.0)
        dialog.fields["x"].setValue(3.0)
        self.assertEqual(len(dialog._history), initial_history)
        self.assertTrue(dialog._transform_edit_pending)
        dialog._commit_transform_edit()
        self.assertEqual(len(dialog._history), initial_history + 1)
        self.assertEqual(dialog.assets[0].position[0], 3.0)
        dialog.dialog.done(0)

    def test_compact_palette_keeps_short_identity_without_elision(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.dialog.resize(980, 760)
        dialog.dialog.show()
        self.app.processEvents()
        self.assertEqual(dialog.asset_search.placeholderText(), "Filter assets")
        self.assertTrue(all("..." not in dialog.palette_list.item(index).text() for index in range(dialog.palette_list.count())))
        dialog.dialog.done(0)

    def test_undo_redo_shortcuts_are_bound_to_the_editor_window(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        self.assertEqual(dialog._undo_shortcut.key().toString(), "Ctrl+Z")
        self.assertEqual(dialog._redo_shortcut.key().toString(), "Ctrl+Y")
        self.assertEqual(dialog._copy_shortcut.key().toString(), "Ctrl+C")
        self.assertEqual(dialog._paste_shortcut.key().toString(), "Ctrl+V")
        self.assertEqual(
            dialog._undo_shortcut.context(),
            dialog.qt["QtCore"].Qt.ShortcutContext.WindowShortcut,
        )
        dialog.dialog.done(0)

    def test_asset_label_edit_is_saved_as_one_symbolic_history_step(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        initial_history = len(dialog._history)
        dialog.asset_label.setText("Discharge conveyor")
        dialog.asset_label.setText("Discharge conveyor / Cell A")
        self.assertEqual(dialog.assets[0].label, "Discharge conveyor / Cell A")
        self.assertEqual(len(dialog._history), initial_history)
        dialog._commit_asset_label()
        self.assertEqual(len(dialog._history), initial_history + 1)
        self.assertEqual(dialog._document()["equipment"][0]["label"], "Discharge conveyor / Cell A")
        dialog.asset_label.setText("")
        dialog._commit_asset_label()
        self.assertEqual(dialog.asset_label.text(), "Discharge conveyor / Cell A")
        dialog.dialog.done(0)

    def test_snap_to_grid_rounds_transform_fields_and_preserves_one_edit(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        dialog.snap_checkbox.setChecked(True)
        dialog.fields["x"].setValue(1.13)
        dialog.fields["y"].setValue(-0.12)
        dialog.fields["z"].setValue(2.38)
        dialog.fields["yaw"].setValue(13.0)
        dialog.fields["scale"].setValue(0.97)
        dialog._commit_transform_edit()
        self.assertEqual(dialog.assets[0].position, (1.25, 0.0, 2.5))
        self.assertEqual(dialog.assets[0].yaw_degrees, 15.0)
        self.assertEqual(dialog.assets[0].scale, 0.95)
        dialog.dialog.done(0)

    def test_frame_selected_target_changes_camera_without_changing_symbolic_layout(self) -> None:
        dialog = StaticSceneEditorDialog(_qt_imports())
        dialog.draft_list.setCurrentRow(0)
        before = tuple(dialog.assets)
        dialog.viewport._zoom = 0.72
        dialog.viewport.frame_selected_target()
        self.app.processEvents()
        self.assertEqual(tuple(dialog.assets), before)
        self.assertGreaterEqual(dialog.viewport._zoom, 0.72)
        self.assertTrue(dialog._dirty)
        dialog.dialog.done(0)


if __name__ == "__main__":
    unittest.main()
