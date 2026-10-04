"""Bounded native static scene authoring and review workspace.

This module deliberately owns symbolic layout plus a bounded deterministic
local review scenario. A draft can be saved and reopened for training review,
but it cannot describe a PLC profile, address, transport, or live machine
behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping

try:
    from .native_asset_library import ASSET_DEFINITIONS
    from .native_review_viewport import NativeSceneReviewViewport
    from .native_draft_runtime import DraftRuntimeError, NativeDraftReviewRuntime
    from .native_scene_library import (
        EQUIPMENT_GALLERY_DEFINITION,
        place_asset,
    )
    from .native_inspection import InspectionTarget
    from .native_software_viewport import (
        MAX_PAN_PIXELS,
        MAX_PITCH_DEGREES,
        MAX_YAW_DEGREES,
        MAX_ZOOM,
        MIN_PAN_PIXELS,
        MIN_PITCH_DEGREES,
        MIN_YAW_DEGREES,
        MIN_ZOOM,
        scene_faces,
    )
    from .scene_contract import SceneContractError, validate_scene_document
except ImportError:
    from native_asset_library import ASSET_DEFINITIONS
    from native_review_viewport import NativeSceneReviewViewport
    from native_draft_runtime import DraftRuntimeError, NativeDraftReviewRuntime
    from native_scene_library import EQUIPMENT_GALLERY_DEFINITION, place_asset
    from native_inspection import InspectionTarget
    from native_software_viewport import (
        MAX_PAN_PIXELS,
        MAX_PITCH_DEGREES,
        MAX_YAW_DEGREES,
        MAX_ZOOM,
        MIN_PAN_PIXELS,
        MIN_PITCH_DEGREES,
        MIN_YAW_DEGREES,
        MIN_ZOOM,
        scene_faces,
    )
    from scene_contract import SceneContractError, validate_scene_document


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "prototype" / "scene.schema.json"
ASSET_TYPES = frozenset(item.asset_type for item in ASSET_DEFINITIONS)
_SYMBOLIC_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
COMPACT_PALETTE_LABELS = {
    "motor": "Foot AC",
    "conveyor": "End roller",
    "box": "FEFCO 0201",
    "photoeye": "Photoeye",
    "switch": "22 mm",
    "indicator": "3-color",
    "pump": "End-suction",
    "fan": "Axial fan",
    "pusher": "ISO pusher",
    "tank": "SS tank",
    "levelSensor": "Point level",
    "radarLevelSensor": "Radar",
    "pipe": "Flanged",
    "rotarySwitch": "3-position",
    "liftTable": "Scissor",
    "valve": "Butterfly",
    "drillPress": "Floor drill",
    "robotArm": "6-axis",
    "rollerShutter": "Roll-up",
    "rotaryTable": "Index table",
    "machine": "CNC process",
}
COMPACT_PALETTE_TYPES = {
    "levelSensor": "LEVEL",
    "radarLevelSensor": "RADAR",
    "rotarySwitch": "ROTARY",
    "liftTable": "LIFT",
    "drillPress": "DRILL",
    "robotArm": "ROBOT",
    "rollerShutter": "SHUTTER",
    "rotaryTable": "TABLE",
    "machine": "CNC",
}


class StaticDraftError(ValueError):
    """A draft is malformed or contains runtime-owned fields."""


@dataclass(frozen=True, slots=True)
class DraftAsset:
    asset_type: str
    instance_id: str
    label: str
    position: tuple[float, float, float]
    yaw_degrees: float = 0.0
    scale: float = 1.0


EditorState = tuple[tuple[DraftAsset, ...], str, str, tuple[str, str, str, str, str]]
EditorView = tuple[float, float, float, float, float]


def default_review_scenario() -> dict[str, Any]:
    return {
        "sequence": [
            {"id": "ready", "label": "Ready / safe state"},
            {"id": "cycle", "label": "Local cycle / asset outputs active"},
            {"id": "complete", "label": "Cycle complete / reset required"},
        ],
        "alarm": {
            "id": "review_interlock",
            "message": "Review interlock raised locally; acknowledge before clear.",
        },
    }


def _number(value: object, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StaticDraftError(f"{path} must be numeric.")
    if not math.isfinite(float(value)):
        raise StaticDraftError(f"{path} must be finite.")
    if abs(float(value)) > 10_000:
        raise StaticDraftError(f"{path} is outside the safe draft range.")
    return float(value)


def _vector(value: object, path: str) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise StaticDraftError(f"{path} must contain three numbers.")
    return tuple(_number(item, f"{path}[{index}]") for index, item in enumerate(value))  # type: ignore[return-value]


def _parse_editor_view(value: object) -> EditorView:
    """Validate the review camera without allowing it to become scene data."""

    if not isinstance(value, Mapping):
        raise StaticDraftError("editorView must be an object.")
    expected = {"yawDegrees", "pitchDegrees", "zoom", "panX", "panY"}
    unknown = set(value) - expected
    if unknown:
        raise StaticDraftError(f"editorView contains unsupported keys: {', '.join(sorted(unknown))}.")
    missing = expected - set(value)
    if missing:
        raise StaticDraftError(f"editorView is missing: {', '.join(sorted(missing))}.")
    yaw = _number(value["yawDegrees"], "editorView.yawDegrees")
    pitch = _number(value["pitchDegrees"], "editorView.pitchDegrees")
    zoom = _number(value["zoom"], "editorView.zoom")
    pan_x = _number(value["panX"], "editorView.panX")
    pan_y = _number(value["panY"], "editorView.panY")
    if not MIN_YAW_DEGREES <= yaw <= MAX_YAW_DEGREES:
        raise StaticDraftError("editorView.yawDegrees is outside the review range.")
    if not MIN_PITCH_DEGREES <= pitch <= MAX_PITCH_DEGREES:
        raise StaticDraftError("editorView.pitchDegrees is outside the review range.")
    if not MIN_ZOOM <= zoom <= MAX_ZOOM:
        raise StaticDraftError("editorView.zoom is outside the review range.")
    if not MIN_PAN_PIXELS <= pan_x <= MAX_PAN_PIXELS or not MIN_PAN_PIXELS <= pan_y <= MAX_PAN_PIXELS:
        raise StaticDraftError("editorView pan is outside the review range.")
    return yaw, pitch, zoom, pan_x, pan_y


def _asset_from_document(raw: Mapping[str, Any], index: int) -> DraftAsset:
    asset_type = raw.get("type")
    instance_id = raw.get("id")
    if asset_type not in ASSET_TYPES:
        raise StaticDraftError(f"equipment[{index}].type is not a native asset.")
    if not isinstance(instance_id, str) or not _SYMBOLIC_ID.fullmatch(instance_id):
        raise StaticDraftError(f"equipment[{index}].id is not a valid symbolic id.")
    position = _vector(raw.get("position", [0.0, 0.0, 0.0]), f"equipment[{index}].position")
    rotation = _vector(raw.get("rotation", [0.0, 0.0, 0.0]), f"equipment[{index}].rotation")
    scale_vector = _vector(raw.get("scale", [1.0, 1.0, 1.0]), f"equipment[{index}].scale")
    if min(scale_vector) <= 0.0 or max(scale_vector) - min(scale_vector) > 0.0001:
        raise StaticDraftError("Static authoring uses one uniform positive scale per asset.")
    scale = scale_vector[0]
    label = raw.get("label") or instance_id
    if not isinstance(label, str) or not label.strip():
        raise StaticDraftError(f"equipment[{index}].label must be readable text.")
    config = raw.get("config", {})
    if config not in ({}, None):
        raise StaticDraftError("Static drafts cannot contain equipment behavior config.")
    return DraftAsset(asset_type, instance_id, label, position, rotation[1], scale)


def _parse_review_scenario(value: object) -> Mapping[str, Any]:
    """Validate the bounded local training contract carried by a draft."""
    if not isinstance(value, Mapping):
        raise StaticDraftError("reviewScenario must be an object.")
    raw_sequence = value.get("sequence")
    if not isinstance(raw_sequence, list) or not 2 <= len(raw_sequence) <= 8:
        raise StaticDraftError("reviewScenario.sequence must contain 2-8 steps.")
    ids: set[str] = set()
    for index, step in enumerate(raw_sequence):
        if not isinstance(step, Mapping):
            raise StaticDraftError(f"reviewScenario.sequence[{index}] must be an object.")
        step_id = step.get("id")
        label = step.get("label")
        if not isinstance(step_id, str) or not _SYMBOLIC_ID.fullmatch(step_id):
            raise StaticDraftError(f"reviewScenario.sequence[{index}].id is invalid.")
        if step_id in ids:
            raise StaticDraftError(f"reviewScenario.sequence contains duplicate id {step_id}.")
        if not isinstance(label, str) or not 1 <= len(label.strip()) <= 128:
            raise StaticDraftError(f"reviewScenario.sequence[{index}].label is invalid.")
        ids.add(step_id)
    alarm = value.get("alarm")
    if not isinstance(alarm, Mapping):
        raise StaticDraftError("reviewScenario.alarm is required.")
    if not isinstance(alarm.get("id"), str) or not _SYMBOLIC_ID.fullmatch(alarm["id"]):
        raise StaticDraftError("reviewScenario.alarm.id is invalid.")
    if not isinstance(alarm.get("message"), str) or not 1 <= len(alarm["message"].strip()) <= 256:
        raise StaticDraftError("reviewScenario.alarm.message is invalid.")
    try:
        NativeDraftReviewRuntime(value)
    except DraftRuntimeError as exc:
        raise StaticDraftError(str(exc)) from exc
    return value  # type: ignore[return-value]


def parse_static_draft(document: object) -> tuple[DraftAsset, ...]:
    """Validate and extract the static layout portion of a scene document."""

    try:
        validate_scene_document(document, SCHEMA_PATH)
    except SceneContractError as exc:
        raise StaticDraftError(str(exc)) from exc
    if not isinstance(document, Mapping):
        raise StaticDraftError("Draft must be an object.")
    if document.get("plcTestProfile") is not None:
        raise StaticDraftError("PLC profiles are not permitted in a static draft.")
    if document.get("editorView") is not None:
        _parse_editor_view(document["editorView"])
    if document.get("reviewScenario") is not None:
        _parse_review_scenario(document["reviewScenario"])
    simulation = document.get("simulation")
    if not isinstance(simulation, Mapping) or simulation.get("type") != "static":
        raise StaticDraftError("Only simulation.type=static may be opened here.")
    runtime_keys = set(simulation) - {"type", "points"}
    if runtime_keys or simulation.get("points"):
        raise StaticDraftError("Static drafts cannot contain runtime points or behavior.")
    equipment = document.get("equipment")
    if not isinstance(equipment, list):
        raise StaticDraftError("Draft equipment must be a list.")
    assets = tuple(_asset_from_document(item, index) for index, item in enumerate(equipment))
    if len({asset.instance_id for asset in assets}) != len(assets):
        raise StaticDraftError("Static draft asset ids must be unique.")
    return assets


def build_static_draft_document(
    *,
    draft_id: str,
    name: str,
    assets: tuple[DraftAsset, ...],
    editor_view: Mapping[str, object] | None = None,
    review_scenario: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a schema-valid symbolic scene with PLC-free review behavior."""

    if not _SYMBOLIC_ID.fullmatch(draft_id):
        raise StaticDraftError("Draft id must be a valid symbolic id.")
    if not name.strip():
        raise StaticDraftError("Draft name cannot be empty.")
    if not assets:
        raise StaticDraftError("A draft needs at least one visual asset.")
    document: dict[str, Any] = {
        "fileType": "plc-visual-scene",
        "version": 1,
        "id": draft_id,
        "name": name.strip(),
        "description": "Static symbolic layout with deterministic local review behavior. No PLC behavior or transport is defined.",
        "reviewScenario": dict(review_scenario or default_review_scenario()),
        "camera": {"position": [10.8, 7.0, 10.8], "target": [0.0, 1.0, 0.0], "fov": 43},
        "equipment": [
            {
                "id": asset.instance_id,
                "type": asset.asset_type,
                "label": asset.label,
                "position": list(asset.position),
                "rotation": [0.0, asset.yaw_degrees, 0.0],
                "scale": [asset.scale, asset.scale, asset.scale],
                "config": {},
            }
            for asset in assets
        ],
        "simulation": {"type": "static"},
    }
    if editor_view is not None:
        view = _parse_editor_view(editor_view)
        document["editorView"] = {
            "yawDegrees": view[0],
            "pitchDegrees": view[1],
            "zoom": view[2],
            "panX": view[3],
            "panY": view[4],
        }
    parse_static_draft(document)
    return document


def load_static_draft(path: Path) -> tuple[dict[str, Any], tuple[DraftAsset, ...]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StaticDraftError(f"Could not read draft: {exc}") from exc
    return document, parse_static_draft(document)


def save_static_draft(path: Path, document: Mapping[str, Any]) -> None:
    parse_static_draft(document)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def suggest_asset_position(asset_index: int) -> tuple[float, float, float]:
    """Return a readable grid slot so newly added assets do not stack."""

    if asset_index < 0:
        raise ValueError("Asset index cannot be negative.")
    column = asset_index % 3
    row = asset_index // 3
    return ((column - 1) * 3.0, 0.0, row * 2.8)


def _inspection_overlay_label(label: str) -> str:
    """Keep the viewport callout concise while preserving the full label elsewhere."""

    base = label.split(" / ", 1)[0].strip()
    if len(base) <= 24:
        return base
    return " ".join(base.split()[:3])


def snap_static_transform(
    position: tuple[float, float, float],
    yaw_degrees: float,
    scale: float,
) -> tuple[tuple[float, float, float], float, float]:
    """Return stable industrial-layout increments for optional authoring snap."""

    snapped_position = tuple(round(value / 0.25) * 0.25 for value in position)
    snapped_yaw = round(yaw_degrees / 15.0) * 15.0
    snapped_scale = round(scale / 0.05) * 0.05
    return (
        tuple(round(value, 3) for value in snapped_position),
        round(snapped_yaw, 3),
        round(snapped_scale, 3),
    )  # type: ignore[return-value]


def _bounds_overlap(
    first: tuple[float, float, float, float, float, float],
    second: tuple[float, float, float, float, float, float],
    padding: float = 0.25,
) -> bool:
    return all(
        first[index] - padding < second[index + 3] + padding
        and second[index] - padding < first[index + 3] + padding
        for index in range(3)
    )


def suggest_non_overlapping_position(
    asset_type: str,
    assets: tuple[DraftAsset, ...],
) -> tuple[float, float, float]:
    """Choose the first open staging position around the current layout."""

    existing_targets = build_static_draft_targets(assets)
    candidates = (
        (5.0, 0.0, 0.0),
        (-5.0, 0.0, 0.0),
        (0.0, 0.0, 4.5),
        (0.0, 0.0, -4.5),
        (5.0, 0.0, 4.5),
        (-5.0, 0.0, 4.5),
        (5.0, 0.0, -4.5),
        (-5.0, 0.0, -4.5),
    )
    for position in candidates:
        probe = DraftAsset(asset_type, "placement_probe", "Placement probe", position)
        probe_target = build_static_draft_targets((probe,))[0]
        if not any(
            _bounds_overlap(probe_target.bounds, target.bounds)
            for target in existing_targets
        ):
            return position
    return suggest_asset_position(len(assets) + 2)


def build_static_draft_targets(
    assets: tuple[DraftAsset, ...],
) -> tuple[InspectionTarget, ...]:
    """Create broad, stable pointer envelopes for placed draft equipment."""

    targets: list[InspectionTarget] = []
    for asset in assets:
        primitives = place_asset(
            asset.asset_type,
            asset.instance_id,
            asset.position,
            scale=asset.scale,
            yaw_degrees=asset.yaw_degrees,
        )
        outline_points = tuple(
            point
            for face in scene_faces(primitives)
            for point in face.points
        )
        points: list[tuple[float, float, float]] = list(outline_points)
        for primitive in primitives:
            if primitive.kind == "box":
                extent = tuple(value / 2.0 for value in primitive.size)
            elif primitive.axis == "x":
                extent = (primitive.length / 2.0, primitive.radius, primitive.radius)
            elif primitive.axis == "z":
                extent = (primitive.radius, primitive.radius, primitive.length / 2.0)
            else:
                extent = (primitive.radius, primitive.length / 2.0, primitive.radius)
            extent = tuple(max(value, primitive.top_radius) for value in extent)
            points.extend(
                tuple(primitive.center[index] + sign * extent[index] for index in range(3))
                for sign in (-1.0, 1.0)
            )
        minimum = tuple(min(point[index] for point in points) for index in range(3))
        maximum = tuple(max(point[index] for point in points) for index in range(3))
        targets.append(
            InspectionTarget(
                asset.instance_id,
                _inspection_overlay_label(asset.label),
                asset.asset_type,
                (*minimum, *maximum),
                status="STATIC DRAFT",
                detail="Selected symbolic asset; no PLC or live-machine behavior is attached.",
                priority=100,
                outline_points=outline_points,
            )
        )
    return tuple(targets)


class StaticSceneEditorDialog:
    """Native source-mode authoring dialog; never creates a PLC session."""

    def __init__(self, qt: dict[str, Any], parent: Any = None) -> None:
        QtCore = qt["QtCore"]
        QtWidgets = qt["QtWidgets"]
        self.qt = qt
        owner = self

        class EditorDialog(QtWidgets.QDialog):
            def resizeEvent(self, event: Any) -> None:  # noqa: N802
                super().resizeEvent(event)
                if hasattr(owner, "draft_list"):
                    compact = self.width() < 1200
                    owner._apply_compact_palette(compact)
                    owner._apply_compact_inspector(compact)
                    owner._ensure_active_asset_visible()

            def closeEvent(self, event: Any) -> None:  # noqa: N802
                if owner._confirm_discard():
                    event.accept()
                else:
                    event.ignore()

        self.dialog = EditorDialog(parent)
        self.dialog.setWindowTitle("RungProof · Static Scene Authoring")
        self.dialog.resize(1500, 860)
        self.dialog.setStyleSheet(self._stylesheet())
        self.assets = self._default_assets()
        self.draft_id = "static-review-draft"
        self.current_path: Path | None = None
        self._dirty = False
        self._validation_state = False
        self._suppress_view_dirty = False
        self._transform_edit_pending = False
        self._asset_label_edit_pending = False
        self._clipboard_asset: DraftAsset | None = None
        self._review_scenario = default_review_scenario()
        self._build_ui()
        self._history: list[EditorState] = [self._editor_state()]
        self._history_index = 0
        self._saved_state = self._editor_state()
        self._saved_view = self._editor_view_tuple()
        QtGui = self.qt["QtGui"]
        QtWidgets = self.qt["QtWidgets"]
        self._undo_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self.dialog)
        self._redo_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Y"), self.dialog)
        self._undo_shortcut.setContext(QtCore.Qt.ShortcutContext.WindowShortcut)
        self._redo_shortcut.setContext(QtCore.Qt.ShortcutContext.WindowShortcut)
        self._undo_shortcut.activated.connect(self._shortcut_undo)
        self._redo_shortcut.activated.connect(self._shortcut_redo)
        self._copy_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self.dialog)
        self._paste_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+V"), self.dialog)
        self._copy_shortcut.setContext(QtCore.Qt.ShortcutContext.WindowShortcut)
        self._paste_shortcut.setContext(QtCore.Qt.ShortcutContext.WindowShortcut)
        self._copy_shortcut.activated.connect(self._shortcut_copy)
        self._paste_shortcut.activated.connect(self._shortcut_paste)
        self._refresh()

    def _default_assets(self) -> list[DraftAsset]:
        return [
            DraftAsset("conveyor", "draft_conveyor", "Main conveyor", (0.0, 0.0, 0.0), 0.0, 1.0),
            DraftAsset("box", "draft_carton", "Inspection carton", (0.0, 1.25, 0.0), 0.0, 0.9),
        ]

    def _stylesheet(self) -> str:
        return """
        QDialog { background:#08151B; color:#EAF2F4; }
        QFrame#editorPanel, QFrame#editorHeader { background:#0D2028; border:1px solid #29414B; }
        QLabel { color:#EAF2F4; }
        QLabel#editorTitle { font-size:20px; font-weight:900; }
        QLabel#editorScope { color:#F2B94B; font-family:Consolas; font-size:11px; font-weight:800; }
        QLabel#dirtyBadge { color:#F2B94B; font-family:Consolas; font-size:10px; font-weight:900; }
        QLabel#validationBadge { color:#8FAAB3; font-family:Consolas; font-size:10px; font-weight:900; }
        QLabel#sectionLabel { color:#8FAAB3; font-family:Consolas; font-size:10px; font-weight:900; }
        QListWidget, QLineEdit, QDoubleSpinBox, QLineEdit#draftName { background:#07151B; color:#EAF2F4; border:1px solid #3A5C67; padding:7px; }
        QListWidget::item { padding:8px; border-bottom:1px solid #203741; }
        QListWidget::item:selected { background:#5FC5EC; color:#071015; }
        QPushButton { min-height:34px; color:#C4D5D9; background:#13252C; border:1px solid #3A5C67; padding:0 12px; font-weight:800; }
        QPushButton#primary { color:#071015; background:#5FC5EC; border-color:#7CD9F7; }
        QPushButton#danger { color:#FFD4B5; border-color:#955348; }
        QPushButton:disabled { color:#536970; background:#0A171C; border-color:#20363D; }
        QDoubleSpinBox { min-height:28px; }
        """

    def _label(self, text: str, object_name: str = "sectionLabel") -> Any:
        label = self.qt["QtWidgets"].QLabel(text)
        label.setObjectName(object_name)
        return label

    def _build_ui(self) -> None:
        QtCore = self.qt["QtCore"]
        QtWidgets = self.qt["QtWidgets"]
        outer = QtWidgets.QVBoxLayout(self.dialog)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(10)
        header = QtWidgets.QFrame(objectName="editorHeader")
        header_layout = QtWidgets.QVBoxLayout(header)
        title = self._label("STATIC SCENE AUTHORING", "editorTitle")
        scope = self._label("REVIEW ONLY  ·  PLC DISABLED  ·  NO PLC TRANSPORT", "editorScope")
        subtitle = QtWidgets.QLabel("Compose reusable native equipment and export a symbolic .plcscene draft.")
        subtitle.setStyleSheet("color:#9DB4BB; font-size:12px;")
        self.dirty_badge = self._label(
            "UNSAVED CHANGES  ·  NEW / OPEN / CLOSE / DELETE ARE GUARDED",
            "dirtyBadge",
        )
        self.dirty_badge.setVisible(False)
        header_layout.addWidget(title)
        header_layout.addWidget(scope)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(self.dirty_badge)
        validation_row = QtWidgets.QHBoxLayout()
        self.validation_badge = self._label(
            "DRAFT GATE  |  NOT VALIDATED",
            "validationBadge",
        )
        validation_row.addWidget(self.validation_badge)
        validation_row.addStretch(1)
        validate_button = QtWidgets.QPushButton("Validate draft")
        validate_button.setToolTip(
            "Validate the symbolic scene contract; PLC transport remains disabled."
        )
        validate_button.clicked.connect(self._validate_draft)
        self.validate_button = validate_button
        preview_button = QtWidgets.QPushButton("Open Review Player")
        preview_button.setToolTip(
            "Hand the validated draft to a read-only player surface; PLC transport stays disabled."
        )
        preview_button.setEnabled(False)
        preview_button.clicked.connect(self._preview_draft)
        self.preview_button = preview_button
        validation_row.addWidget(validate_button)
        validation_row.addWidget(preview_button)
        header_layout.addLayout(validation_row)
        outer.addWidget(header)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(10)
        outer.addLayout(body, 1)
        palette = QtWidgets.QFrame(objectName="editorPanel")
        palette_layout = QtWidgets.QVBoxLayout(palette)
        palette_layout.addWidget(self._label("ASSET PALETTE"))
        self.asset_search = QtWidgets.QLineEdit()
        self.asset_search.setPlaceholderText("Filter assets")
        self.asset_search.textChanged.connect(self._filter_palette)
        palette_layout.addWidget(self.asset_search)
        self.palette_list = QtWidgets.QListWidget()
        self.palette_list.setWordWrap(True)
        self.palette_list.setTextElideMode(QtCore.Qt.TextElideMode.ElideNone)
        self.palette_list.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.palette_list.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollMode.ScrollPerItem
        )
        self.palette_list.itemDoubleClicked.connect(lambda _item: self._add_asset())
        palette_layout.addWidget(self.palette_list, 1)
        add_button = QtWidgets.QPushButton("＋  Add to draft")
        add_button.setObjectName("primary")
        add_button.clicked.connect(self._add_asset)
        palette_layout.addWidget(add_button)
        body.addWidget(palette, 0)

        center = QtWidgets.QFrame(objectName="editorPanel")
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.addWidget(self._label("DRAFT VIEWPORT"))
        draft_definition = replace(
            EQUIPMENT_GALLERY_DEFINITION,
            approval_id="DRAFT",
            scene_id="static-draft",
            label="Static review draft",
            source_file=Path("static-review-draft.plcscene"),
            setup_file=Path("STATIC-REVIEW-ONLY"),
        )
        # The review viewport constructor builds a known catalog scene first;
        # the editor immediately replaces that geometry with the draft below.
        viewport = NativeSceneReviewViewport(self.qt, EQUIPMENT_GALLERY_DEFINITION)
        viewport.definition = draft_definition
        viewport.inspection_hover_label = "CLICK TO SELECT"
        viewport.inspection_selected_label = "SELECTED"
        viewport.short_inspection_leader = True
        viewport.review_handoff_callout = True
        viewport.review_authoring_callout = True
        viewport.review_callout_no_leader = True
        self.viewport = viewport
        viewport.container.equipmentSelected.connect(self._select_viewport_target)
        viewport.container.equipmentCleared.connect(self._clear_viewport_selection)
        viewport.container.viewChanged.connect(self._mark_view_dirty)
        center_layout.addWidget(viewport.container, 1)
        body.addWidget(center, 1)

        inspector = QtWidgets.QFrame(objectName="editorPanel")
        inspector_layout = QtWidgets.QVBoxLayout(inspector)
        inspector_layout.addWidget(self._label("DRAFT INSPECTOR"))
        self.draft_name = QtWidgets.QLineEdit("Static Draft")
        self.draft_name.setObjectName("draftName")
        self.draft_name.textChanged.connect(self._mark_dirty)
        self.draft_name.editingFinished.connect(self._record_history)
        inspector_layout.addWidget(self.draft_name)
        scenario_title = self._label("LOCAL REVIEW SCENARIO")
        scenario_title.setToolTip(
            "Author the deterministic local training sequence; no PLC points or transport are permitted."
        )
        inspector_layout.addWidget(scenario_title)
        scenario_hint = QtWidgets.QLabel(
            "3 TYPED STEPS  |  BOOL POINTS  |  PLC DISABLED"
        )
        scenario_hint.setStyleSheet(
            "color:#8FAAB3; font-family:Consolas; font-size:9px;"
        )
        inspector_layout.addWidget(scenario_hint)
        scenario_form = QtWidgets.QFormLayout()
        self.scenario_fields: dict[str, Any] = {}
        for key, label in (
            ("ready", "STEP 1 / READY"),
            ("cycle", "STEP 2 / CYCLE"),
            ("complete", "STEP 3 / COMPLETE"),
            ("alarm_id", "ALARM ID"),
            ("alarm_message", "ALARM MESSAGE"),
        ):
            field = QtWidgets.QLineEdit()
            field.setObjectName("scenarioField")
            field.setMinimumHeight(28)
            field.setMaximumHeight(28)
            field.setStyleSheet("padding:3px 6px;")
            field.setPlaceholderText("Author readable local review behavior")
            field.textChanged.connect(self._mark_dirty)
            if key == "alarm_message":
                field.textChanged.connect(field.setToolTip)
            field.editingFinished.connect(self._record_history)
            self.scenario_fields[key] = field
            scenario_form.addRow(self._label(label), field)
        inspector_layout.addLayout(scenario_form)
        self._set_review_scenario_fields(self._review_scenario)
        self.draft_list = QtWidgets.QListWidget()
        self.draft_list.setMinimumHeight(86)
        self.draft_list.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.draft_list.customContextMenuRequested.connect(
            self._show_asset_context_menu
        )
        self.draft_list.currentRowChanged.connect(self._select_asset)
        inspector_layout.addWidget(self.draft_list, 1)
        self.asset_clipboard_hint = QtWidgets.QLabel(
            "ASSET LIST COPY / PASTE  ·  RIGHT-CLICK OR CTRL+C / CTRL+V"
        )
        self.asset_clipboard_hint.setToolTip(
            "Copy the selected symbolic asset, then paste a fresh collision-safe copy."
        )
        self.asset_clipboard_hint.setStyleSheet(
            "color:#8FAAB3; font-family:Consolas; font-size:10px;"
        )
        inspector_layout.addWidget(self.asset_clipboard_hint)
        inspector_layout.addWidget(self._label("ASSET LABEL"))
        self.asset_label = QtWidgets.QLineEdit()
        self.asset_label.setPlaceholderText("Readable equipment label")
        self.asset_label.textChanged.connect(self._apply_asset_label)
        self.asset_label.editingFinished.connect(self._commit_asset_label)
        inspector_layout.addWidget(self.asset_label)
        form = QtWidgets.QFormLayout()
        self.fields: dict[str, Any] = {}
        for key, label in (("x", "X POSITION [SCENE UNITS]"), ("y", "Y POSITION [SCENE UNITS]"), ("z", "Z POSITION [SCENE UNITS]"), ("yaw", "YAW [DEGREES]"), ("scale", "UNIFORM SCALE")):
            field = QtWidgets.QDoubleSpinBox()
            field.setRange(-100.0 if key != "scale" else 0.05, 100.0 if key != "scale" else 10.0)
            field.setDecimals(3)
            field.valueChanged.connect(self._apply_fields)
            field.editingFinished.connect(self._commit_transform_edit)
            self.fields[key] = field
            form.addRow(self._label(label), field)
        inspector_layout.addLayout(form)
        self.snap_checkbox = QtWidgets.QCheckBox("SNAP TO GRID  ·  POS .25 / YAW 15° / SCALE .05")
        self.snap_checkbox.setToolTip(
            "Round position to 0.25 scene units, yaw to 15 degrees, and scale to 0.05."
        )
        self.snap_checkbox.stateChanged.connect(self._apply_fields)
        inspector_layout.addWidget(self.snap_checkbox)
        row = QtWidgets.QHBoxLayout()
        delete_button = QtWidgets.QPushButton("Delete")
        delete_button.setObjectName("danger")
        delete_button.setToolTip("Requires explicit confirmation before removing an asset.")
        delete_button.clicked.connect(self._delete_asset)
        row.addWidget(delete_button)
        duplicate_button = QtWidgets.QPushButton("Duplicate")
        duplicate_button.setToolTip("Create a symbolic copy in the next collision-free layout slot.")
        duplicate_button.clicked.connect(self._duplicate_asset)
        row.addWidget(duplicate_button)
        reset_button = QtWidgets.QPushButton("Reset view")
        reset_button.clicked.connect(self.viewport.reset_camera)
        row.addWidget(reset_button)
        frame_button = QtWidgets.QPushButton("Frame")
        frame_button.setToolTip("Center and size the selected asset for inspection.")
        frame_button.clicked.connect(self.viewport.frame_selected_target)
        row.addWidget(frame_button)
        inspector_layout.addLayout(row)
        body.addWidget(inspector, 0)

        footer = QtWidgets.QHBoxLayout()
        self.status = QtWidgets.QLabel("DRAFT READY  ·  2 ASSETS  ·  SYMBOLIC ONLY")
        self.status.setStyleSheet("color:#8FAAB3; font-family:Consolas; font-size:11px;")
        footer.addWidget(self.status, 1)
        undo_button = QtWidgets.QPushButton("Undo")
        undo_button.setObjectName("historyButton")
        undo_button.setToolTip("Undo the last symbolic draft edit (Ctrl+Z).")
        undo_button.clicked.connect(self._undo)
        self.undo_button = undo_button
        redo_button = QtWidgets.QPushButton("Redo")
        redo_button.setObjectName("historyButton")
        redo_button.setToolTip("Redo the last symbolic draft edit (Ctrl+Y).")
        redo_button.clicked.connect(self._redo)
        self.redo_button = redo_button
        footer.addWidget(undo_button)
        footer.addWidget(redo_button)
        new_button = QtWidgets.QPushButton("New draft")
        new_button.clicked.connect(self._new_draft)
        open_button = QtWidgets.QPushButton("Open .plcscene")
        open_button.clicked.connect(self._open)
        save_button = QtWidgets.QPushButton("Save draft")
        save_button.setObjectName("primary")
        save_button.clicked.connect(self._save)
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(self._close)
        footer.addWidget(new_button)
        footer.addWidget(open_button)
        footer.addWidget(save_button)
        footer.addWidget(close_button)
        outer.addLayout(footer)

    def _filter_palette(self, text: str) -> None:
        needle = text.strip().lower()
        for index in range(self.palette_list.count()):
            item = self.palette_list.item(index)
            item.setHidden(
                needle not in item.text().lower()
                and needle not in item.toolTip().lower()
            )

    def _palette_label(self, asset_type: str, compact: bool) -> str:
        definition = next(
            definition for definition in ASSET_DEFINITIONS
            if definition.asset_type == asset_type
        )
        if not compact:
            return f"{definition.label}\n{definition.asset_type.upper()}"
        short_label = COMPACT_PALETTE_LABELS.get(asset_type, definition.label)
        compact_type = COMPACT_PALETTE_TYPES.get(
            asset_type,
            definition.asset_type.upper(),
        )
        return f"{short_label}\n{compact_type}"

    def _apply_compact_palette(self, compact: bool) -> None:
        if not hasattr(self, "palette_list"):
            return
        self.palette_list.setStyleSheet(
            "QListWidget::item { padding: 1px; font-size: 9px; }"
            if compact
            else "QListWidget::item { padding: 8px; font-size: 12px; }"
        )
        for index in range(self.palette_list.count()):
            item = self.palette_list.item(index)
            asset_type = item.data(self.qt["QtCore"].Qt.ItemDataRole.UserRole)
            item.setText(self._palette_label(str(asset_type), compact))

    def _apply_compact_inspector(self, compact: bool) -> None:
        if not hasattr(self, "draft_list"):
            return
        self.draft_list.setMinimumHeight(92 if compact else 0)
        compact_height = 28 if compact else 34
        for field in (self.draft_name, self.asset_label, *self.scenario_fields.values(), *self.fields.values()):
            field.setFixedHeight(compact_height)

    def _refresh(self) -> None:
        self.palette_list.clear()
        for definition in ASSET_DEFINITIONS:
            item = self.qt["QtWidgets"].QListWidgetItem(
                f"{definition.label}\n{definition.asset_type.upper()}"
            )
            item.setData(self.qt["QtCore"].Qt.ItemDataRole.UserRole, definition.asset_type)
            item.setToolTip(f"{definition.label}  ·  {definition.asset_type}")
            self.palette_list.addItem(item)
        self.draft_list.clear()
        for asset in self.assets:
            self.draft_list.addItem(f"{asset.label}\n{asset.instance_id}  ·  {asset.asset_type}")
        self.draft_list.setCurrentRow(0 if self.assets else -1)
        self._ensure_active_asset_visible()
        self._refresh_viewport()
        self._apply_compact_palette(self.dialog.width() < 1200)
        self._apply_compact_inspector(self.dialog.width() < 1200)
        prefix = "UNSAVED CHANGES" if self._dirty else "DRAFT READY"
        suffix = (
            "SAVE BEFORE CLOSE / NEW  ·  DELETE IS GUARDED"
            if self._dirty
            else "SYMBOLIC ONLY"
        )
        self.status.setText(f"{prefix}  ·  {len(self.assets)} ASSETS  ·  {suffix}")
        self.dirty_badge.setVisible(self._dirty)
        self._update_history_buttons()

    def _editor_state(self) -> EditorState:
        return (
            tuple(self.assets),
            self.draft_name.text(),
            self.draft_id,
            self._review_scenario_state(),
        )

    def _update_history_buttons(self) -> None:
        self.undo_button.setEnabled(self._history_index > 0)
        self.redo_button.setEnabled(
            self._history_index < len(self._history) - 1
        )

    def _reset_history(self) -> None:
        self._transform_edit_pending = False
        self._asset_label_edit_pending = False
        self._history = [self._editor_state()]
        self._history_index = 0
        self._saved_state = self._editor_state()
        self._dirty = False

    def _record_history(self) -> None:
        state = self._editor_state()
        if state != self._history[self._history_index]:
            self._history = self._history[: self._history_index + 1]
            self._history.append(state)
            self._history_index += 1
        self._mark_dirty()
        self._update_history_buttons()

    def _restore_history_state(self, state: EditorState) -> None:
        self._transform_edit_pending = False
        self._asset_label_edit_pending = False
        assets, name, draft_id, scenario_state = state
        self.assets = list(assets)
        self.draft_id = draft_id
        self.draft_name.blockSignals(True)
        self.draft_name.setText(name)
        self.draft_name.blockSignals(False)
        self._set_review_scenario_fields(
            {
                "sequence": [
                    {"id": "ready", "label": scenario_state[0]},
                    {"id": "cycle", "label": scenario_state[1]},
                    {"id": "complete", "label": scenario_state[2]},
                ],
                "alarm": {
                    "id": scenario_state[3],
                    "message": scenario_state[4],
                },
            }
        )
        self._refresh()
        self._mark_dirty()

    def _undo(self) -> None:
        if self._history_index <= 0:
            return
        self._history_index -= 1
        self._restore_history_state(self._history[self._history_index])

    def _shortcut_edit_is_active(self) -> bool:
        focused = self.qt["QtWidgets"].QApplication.focusWidget()
        return (
            focused is self.draft_name
            or focused is self.asset_label
            or focused is self.asset_search
            or focused in self.fields.values()
        )

    def _shortcut_undo(self) -> None:
        if not self._shortcut_edit_is_active():
            self._undo()

    def _shortcut_redo(self) -> None:
        if not self._shortcut_edit_is_active():
            self._redo()

    def _shortcut_copy(self) -> None:
        if not self._shortcut_edit_is_active():
            self._copy_asset()

    def _shortcut_paste(self) -> None:
        if not self._shortcut_edit_is_active():
            self._paste_asset()

    def _redo(self) -> None:
        if self._history_index >= len(self._history) - 1:
            return
        self._history_index += 1
        self._restore_history_state(self._history[self._history_index])

    def _mark_dirty(self) -> None:
        self._dirty = (
            self._editor_state() != self._saved_state
            or self._editor_view_tuple() != self._saved_view
        )
        if self._validation_state and hasattr(self, "validation_badge"):
            self._validation_state = False
            self.validation_badge.setText("DRAFT GATE  |  NOT VALIDATED")
            self.preview_button.setEnabled(False)
        if hasattr(self, "status"):
            self.status.setText(
                f"UNSAVED CHANGES  ·  {len(self.assets)} ASSETS  ·  SAVE BEFORE CLOSE / NEW  ·  DELETE IS GUARDED"
            )
            self.dirty_badge.setVisible(True)

    def _validate_draft(self) -> bool:
        self._commit_transform_edit()
        self._commit_asset_label()
        try:
            document = self._document()
        except (SceneContractError, StaticDraftError, ValueError) as exc:
            self._validation_state = False
            self.validation_badge.setText("DRAFT GATE  |  REJECTED")
            self.preview_button.setEnabled(False)
            self.status.setText(f"VALIDATION FAILED  Â·  {exc}")
            return False
        self._validation_state = True
        self.validation_badge.setText(
            "DRAFT GATE  |  VALID  |  SYMBOLIC ONLY  |  PLC DISABLED"
        )
        self.preview_button.setEnabled(True)
        self.status.setText(
            f"VALIDATED  |  {len(document['equipment'])} ASSETS  |  SAVE BEFORE RUNTIME HANDOFF"
        )
        return True

    def _build_review_player_dialog(self, document: Mapping[str, Any]) -> Any:
        """Build an interactive, read-only player handoff for a valid draft."""
        QtCore = self.qt["QtCore"]
        QtWidgets = self.qt["QtWidgets"]

        class ReviewPlayerDialog(QtWidgets.QDialog):
            def resizeEvent(dialog_self: Any, event: Any) -> None:  # noqa: N802
                super().resizeEvent(event)
                handoff_viewport.compact_display = (
                    dialog_self.width() < 1050 or dialog_self.height() < 680
                )
                handoff_viewport.container.update()

        handoff = ReviewPlayerDialog(self.dialog)
        handoff.setWindowTitle("RungProof | Review Player Handoff")
        handoff.resize(1120, 760)
        layout = QtWidgets.QVBoxLayout(handoff)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        title = QtWidgets.QLabel("REVIEW PLAYER HANDOFF")
        title.setObjectName("editorTitle")
        layout.addWidget(title)
        scope = QtWidgets.QLabel(
            "VALIDATED UNSAVED DRAFT  |  REVIEW ONLY  |  PLC DISABLED  |  NO TRANSPORT"
        )
        scope.setObjectName("editorScope")
        layout.addWidget(scope)

        runtime = NativeDraftReviewRuntime.from_document(document)
        runtime_panel = QtWidgets.QFrame(objectName="editorPanel")
        runtime_layout = QtWidgets.QVBoxLayout(runtime_panel)
        runtime_layout.setContentsMargins(10, 8, 10, 8)
        runtime_layout.setSpacing(5)
        runtime_title = QtWidgets.QLabel(
            "LOCAL TRAINING SCENARIO  |  DETERMINISTIC  |  PLC DISABLED"
        )
        runtime_title.setObjectName("sectionLabel")
        runtime_layout.addWidget(runtime_title)
        runtime_state = QtWidgets.QLabel()
        runtime_state.setObjectName("reviewRuntimeState")
        runtime_step = QtWidgets.QLabel()
        runtime_step.setObjectName("reviewRuntimeStep")
        runtime_points = QtWidgets.QLabel()
        runtime_points.setObjectName("reviewRuntimePoints")
        runtime_alarm = QtWidgets.QLabel()
        runtime_alarm.setObjectName("reviewRuntimeAlarm")
        for label in (runtime_state, runtime_step, runtime_points, runtime_alarm):
            label.setWordWrap(True)
            runtime_layout.addWidget(label)
        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(6)
        run_button = QtWidgets.QPushButton("Run")
        run_button.setObjectName("primary")
        stop_button = QtWidgets.QPushButton("Stop")
        reset_button = QtWidgets.QPushButton("Reset")
        raise_button = QtWidgets.QPushButton("Raise alarm")
        acknowledge_button = QtWidgets.QPushButton("Acknowledge")
        clear_button = QtWidgets.QPushButton("Clear")
        for button in (
            run_button,
            stop_button,
            reset_button,
            raise_button,
            acknowledge_button,
            clear_button,
        ):
            controls.addWidget(button)
        runtime_layout.addLayout(controls)
        layout.addWidget(runtime_panel)

        # Construct through the known catalog definition, then replace it
        # with the already-validated symbolic draft. This keeps the handoff
        # interactive without inventing PLC runtime or transport behavior.
        handoff_viewport = NativeSceneReviewViewport(
            self.qt, EQUIPMENT_GALLERY_DEFINITION
        )
        handoff_viewport.compact_display = handoff.width() < 1050
        handoff_viewport.review_handoff_compact = True
        handoff_viewport.definition = self.viewport.definition
        handoff_viewport.geometry = tuple(self.viewport.geometry)
        handoff_viewport._targets = tuple(self.viewport._targets)
        handoff_viewport._yaw_degrees = self.viewport._yaw_degrees
        handoff_viewport._pitch_degrees = self.viewport._pitch_degrees
        handoff_viewport._zoom = self.viewport._zoom
        handoff_viewport._pan_x = self.viewport._pan_x
        handoff_viewport._pan_y = self.viewport._pan_y
        handoff_viewport._selected_target = self.viewport._selected_target
        handoff_viewport.review_runtime_snapshot = runtime.snapshot()
        handoff_viewport.review_handoff_callout = True
        handoff_viewport.inspection_hover_label = "CLICK TO SELECT"
        handoff_viewport.inspection_selected_label = "SELECTED"
        handoff_viewport.short_inspection_leader = True
        handoff_viewport.container.setMinimumHeight(360)
        handoff_viewport.container.setFocusPolicy(
            QtCore.Qt.FocusPolicy.StrongFocus
        )
        handoff_viewport.container.setToolTip(
            "Review-only viewport | drag to orbit | wheel to zoom | PLC disabled"
        )
        layout.addWidget(handoff_viewport.container, 1)

        def refresh_runtime() -> None:
            snapshot = runtime.snapshot()
            handoff_viewport.review_runtime_snapshot = snapshot
            runtime_state.setText(
                f"STATE  {snapshot.state.upper()}  |  "
                f"{'RUNNING' if snapshot.cycle_active else 'SAFE / STOPPED'}"
            )
            runtime_step.setText(
                f"STEP  {snapshot.step_index + 1}  |  {snapshot.step_label}"
            )
            runtime_points.setText(
                "POINTS  "
                + "  ".join(
                    f"{name}={'1' if value else '0'}"
                    for name, value in snapshot.points.items()
                )
            )
            runtime_alarm.setText(
                f"ALARM  {snapshot.fault_message if snapshot.fault_active else 'NONE'}  |  "
                f"{snapshot.notice}"
            )
            runtime_alarm.setStyleSheet(
                "color:#FFB36B; font-family:Consolas; font-size:10px; font-weight:800;"
                if snapshot.fault_active
                else "color:#8FAAB3; font-family:Consolas; font-size:10px;"
            )
            is_running = snapshot.cycle_active
            is_complete = snapshot.cycle_complete
            run_button.setEnabled(
                not snapshot.fault_active and not is_running and not is_complete
            )
            stop_button.setEnabled(is_running)
            reset_button.setEnabled(not is_running)
            raise_button.setEnabled(not snapshot.fault_active)
            acknowledge_button.setEnabled(
                snapshot.fault_active and not snapshot.fault_acknowledged
            )
            clear_button.setEnabled(
                snapshot.fault_active and snapshot.fault_acknowledged
            )
            run_button.setObjectName("primary" if run_button.isEnabled() else "")
            stop_button.setObjectName("primary" if is_running else "")
            acknowledge_button.setObjectName(
                "primary" if acknowledge_button.isEnabled() else ""
            )
            clear_button.setObjectName("danger" if clear_button.isEnabled() else "")
            for button in (
                run_button,
                stop_button,
                acknowledge_button,
                clear_button,
            ):
                button.style().unpolish(button)
                button.style().polish(button)
            handoff_viewport.container.update()

        run_button.clicked.connect(lambda: (runtime.run(), refresh_runtime()))
        stop_button.clicked.connect(lambda: (runtime.stop(), refresh_runtime()))
        reset_button.clicked.connect(lambda: (runtime.reset(), refresh_runtime()))
        raise_button.clicked.connect(lambda: (runtime.raise_fault(), refresh_runtime()))
        acknowledge_button.clicked.connect(
            lambda: (runtime.acknowledge_fault(), refresh_runtime())
        )
        clear_button.clicked.connect(lambda: (runtime.clear_fault(), refresh_runtime()))
        runtime_timer = QtCore.QTimer(handoff)
        runtime_timer.setInterval(450)
        runtime_timer.timeout.connect(
            lambda: (runtime.advance(), refresh_runtime())
            if runtime.snapshot().cycle_active
            else None
        )
        runtime_timer.start()
        refresh_runtime()

        summary = QtWidgets.QLabel(
            f"DRAFT  {document['name']}  |  ID  {document['id']}  |  "
            f"ASSETS  {len(document['equipment'])}  |  STATE  VALIDATED UNSAVED DRAFT\n"
            "PROVENANCE  SYMBOLIC DRAFT  |  RUNTIME BEHAVIOR  LOCAL DETERMINISTIC  |  "
            "PLC PROFILE  NONE  |  TRANSPORT  NONE"
        )
        summary.setObjectName("reviewHandoffSummary")
        summary.setWordWrap(True)
        summary.setStyleSheet(
            "color:#B8D0D5; background:#0D252C; border:1px solid #2E6877; padding:8px; font-family:Consolas; font-size:10px;"
        )
        layout.addWidget(summary)
        close_button = QtWidgets.QPushButton("Return to authoring")
        close_button.clicked.connect(handoff.accept)
        layout.addWidget(close_button)
        handoff._review_viewport = handoff_viewport
        handoff._review_scope = scope
        handoff._review_summary = summary
        handoff._review_runtime = runtime
        handoff._review_runtime_state = runtime_state
        handoff._review_runtime_step = runtime_step
        handoff._review_runtime_points = runtime_points
        handoff._review_runtime_alarm = runtime_alarm
        handoff._review_runtime_timer = runtime_timer
        return handoff

    def _preview_draft(self) -> None:
        if not self._validation_state or not self._validate_draft():
            return
        document = self._document()
        self._build_review_player_dialog(document).exec()
        return
        document = self._document()
        preview = QtWidgets.QDialog(self.dialog)
        preview.setWindowTitle("RungProof Â· Validated Draft Preview")
        preview.resize(980, 700)
        layout = QtWidgets.QVBoxLayout(preview)
        title = QtWidgets.QLabel("VALIDATED DRAFT PREVIEW")
        title.setObjectName("editorTitle")
        layout.addWidget(title)
        scope = QtWidgets.QLabel(
            "READ-ONLY PREVIEW  |  SYMBOLIC CONTRACT VALID  |  PLC DISABLED  |  NO TRANSPORT"
        )
        scope.setObjectName("editorScope")
        layout.addWidget(scope)
        image = QtWidgets.QLabel()
        image.setAlignment(self.qt["QtCore"].Qt.AlignmentFlag.AlignCenter)
        image.setMinimumHeight(360)
        pixmap = self.viewport.container.grab()
        if not pixmap.isNull():
            image.setPixmap(
                pixmap.scaled(
                    900,
                    420,
                    self.qt["QtCore"].Qt.AspectRatioMode.KeepAspectRatio,
                    self.qt["QtCore"].Qt.TransformationMode.SmoothTransformation,
                )
            )
        layout.addWidget(image, 1)
        summary = QtWidgets.QLabel(
            f"DRAFT  {document['name']}  Â·  ID  {document['id']}  Â·  "
            f"ASSETS  {len(document['equipment'])}\n"
            "PROVENANCE  SYMBOLIC DRAFT  Â·  RUNTIME BEHAVIOR  NONE  Â·  PLC PROFILE  NONE"
        )
        summary.setWordWrap(True)
        summary.setStyleSheet(
            "color:#B8D0D5; background:#0D252C; border:1px solid #2E6877; padding:8px; font-family:Consolas; font-size:10px;"
        )
        layout.addWidget(summary)
        close_button = QtWidgets.QPushButton("Close preview")
        close_button.clicked.connect(preview.accept)
        layout.addWidget(close_button)
        preview.exec()

    def _mark_view_dirty(self) -> None:
        if self._suppress_view_dirty:
            return
        self._mark_dirty()

    def _ensure_active_asset_visible(self) -> None:
        row = self.draft_list.currentRow()
        if row >= 0:
            self.qt["QtCore"].QTimer.singleShot(
                0,
                lambda: self._scroll_active_asset_row(row),
            )

    def _scroll_active_asset_row(self, row: int) -> None:
        if 0 <= row < self.draft_list.count():
            self.draft_list.scrollToItem(
                self.draft_list.item(row),
                self.qt["QtWidgets"].QAbstractItemView.ScrollHint.PositionAtCenter,
            )

    def _refresh_viewport(self) -> None:
        geometry = tuple(
            primitive
            for asset in self.assets
            for primitive in place_asset(asset.asset_type, asset.instance_id, asset.position, scale=asset.scale, yaw_degrees=asset.yaw_degrees)
        )
        self.viewport.geometry = geometry
        self.viewport.definition = replace(
            self.viewport.definition,
            source_file=(
                self.current_path
                if self.current_path is not None
                else Path("UNSAVED DRAFT")
            ),
        )
        self.viewport._targets = build_static_draft_targets(tuple(self.assets))
        selected_row = self.draft_list.currentRow()
        if 0 <= selected_row < len(self.assets):
            selected_id = self.assets[selected_row].instance_id
            self.viewport._selected_target = next(
                (
                    target
                    for target in self.viewport._targets
                    if target.target_id == selected_id
                ),
                None,
            )
        self.viewport.container.update()

    def _select_viewport_target(self, target: Any) -> None:
        row = next(
            (
                index
                for index, asset in enumerate(self.assets)
                if asset.instance_id == getattr(target, "target_id", None)
            ),
            -1,
        )
        if row >= 0:
            self.draft_list.setCurrentRow(row)

    def _clear_viewport_selection(self) -> None:
        self.draft_list.clearSelection()
        self.viewport._selected_target = None
        self.viewport.container.update()

    def _select_asset(self, row: int) -> None:
        self._commit_transform_edit()
        self._commit_asset_label()
        if not 0 <= row < len(self.assets):
            return
        asset = self.assets[row]
        self.asset_label.blockSignals(True)
        self.asset_label.setText(asset.label)
        self.asset_label.blockSignals(False)
        for key, value in (("x", asset.position[0]), ("y", asset.position[1]), ("z", asset.position[2]), ("yaw", asset.yaw_degrees), ("scale", asset.scale)):
            self.fields[key].blockSignals(True)
            self.fields[key].setValue(value)
            self.fields[key].blockSignals(False)
        self.viewport._selected_target = next(
            (
                target
                for target in getattr(self.viewport, "_targets", ())
                if target.target_id == asset.instance_id
            ),
            None,
        )
        self.viewport.container.update()

    def _apply_asset_label(self) -> None:
        row = self.draft_list.currentRow()
        if not 0 <= row < len(self.assets):
            return
        label = self.asset_label.text().strip()
        if not label:
            return
        asset = self.assets[row]
        if asset.label == label:
            return
        self.assets[row] = replace(asset, label=label)
        item = self.draft_list.item(row)
        if item is not None:
            item.setText(f"{label}\n{asset.instance_id}  ·  {asset.asset_type}")
        self._refresh_viewport()
        self._asset_label_edit_pending = True
        self._mark_dirty()

    def _commit_asset_label(self) -> None:
        row = self.draft_list.currentRow()
        if 0 <= row < len(self.assets) and not self.asset_label.text().strip():
            self.asset_label.blockSignals(True)
            self.asset_label.setText(self.assets[row].label)
            self.asset_label.blockSignals(False)
        if not self._asset_label_edit_pending:
            return
        self._asset_label_edit_pending = False
        self._record_history()

    def _apply_fields(self) -> None:
        row = self.draft_list.currentRow()
        if not 0 <= row < len(self.assets):
            return
        position = (self.fields["x"].value(), self.fields["y"].value(), self.fields["z"].value())
        yaw = self.fields["yaw"].value()
        scale = self.fields["scale"].value()
        if self.snap_checkbox.isChecked():
            position, yaw, scale = snap_static_transform(position, yaw, scale)
            for key, value in zip(("x", "y", "z"), position):
                self.fields[key].blockSignals(True)
                self.fields[key].setValue(value)
                self.fields[key].blockSignals(False)
            for key, value in (("yaw", yaw), ("scale", scale)):
                self.fields[key].blockSignals(True)
                self.fields[key].setValue(value)
                self.fields[key].blockSignals(False)
        self.assets[row] = DraftAsset(
            self.assets[row].asset_type,
            self.assets[row].instance_id,
            self.assets[row].label,
            position,
            yaw,
            scale,
        )
        self._refresh_viewport()
        self._transform_edit_pending = True
        self._mark_dirty()

    def _commit_transform_edit(self) -> None:
        if not self._transform_edit_pending:
            return
        self._transform_edit_pending = False
        self._record_history()

    def _add_asset(self) -> None:
        self._commit_transform_edit()
        item = self.palette_list.currentItem()
        if item is None:
            return
        asset_type = item.data(self.qt["QtCore"].Qt.ItemDataRole.UserRole)
        definition = next(item for item in ASSET_DEFINITIONS if item.asset_type == asset_type)
        index = 1
        while any(asset.instance_id == f"draft_{asset_type}_{index}" for asset in self.assets):
            index += 1
        self.assets.append(
            DraftAsset(
                asset_type,
                f"draft_{asset_type}_{index}",
                definition.label,
                suggest_non_overlapping_position(asset_type, tuple(self.assets)),
            )
        )
        self._dirty = True
        self._refresh()
        self.draft_list.setCurrentRow(len(self.assets) - 1)
        self._ensure_active_asset_visible()
        self._record_history()

    def _delete_asset(self) -> None:
        self._commit_transform_edit()
        row = self.draft_list.currentRow()
        if not 0 <= row < len(self.assets) or len(self.assets) <= 1:
            return
        answer = self.qt["QtWidgets"].QMessageBox.question(
            self.dialog,
            "Delete draft asset",
            f"Remove {self.assets[row].label} from this static draft?",
            self.qt["QtWidgets"].QMessageBox.StandardButton.Yes
            | self.qt["QtWidgets"].QMessageBox.StandardButton.No,
            self.qt["QtWidgets"].QMessageBox.StandardButton.No,
        )
        if answer == self.qt["QtWidgets"].QMessageBox.StandardButton.Yes:
            self.assets.pop(row)
            self._refresh()
            self._record_history()

    def _show_asset_context_menu(self, position: Any) -> None:
        QtWidgets = self.qt["QtWidgets"]
        menu = QtWidgets.QMenu(self.dialog)
        copy_action = menu.addAction("Copy asset")
        paste_action = menu.addAction("Paste asset")
        menu.addSeparator()
        delete_action = menu.addAction("Delete asset")
        row = self.draft_list.currentRow()
        copy_action.setEnabled(0 <= row < len(self.assets))
        paste_action.setEnabled(self._clipboard_asset is not None)
        delete_action.setEnabled(0 <= row < len(self.assets) and len(self.assets) > 1)
        copy_action.triggered.connect(self._copy_asset)
        paste_action.triggered.connect(self._paste_asset)
        delete_action.triggered.connect(self._delete_asset)
        menu.exec(self.draft_list.mapToGlobal(position))

    def _copy_asset(self) -> None:
        self._commit_transform_edit()
        self._commit_asset_label()
        row = self.draft_list.currentRow()
        if not 0 <= row < len(self.assets):
            return
        self._clipboard_asset = self.assets[row]
        self.status.setText(
            f"COPIED  ·  {self._clipboard_asset.label}  ·  CTRL+V PASTES A NEW SYMBOLIC ASSET"
        )

    def _stage_copy_position(self, source: DraftAsset) -> tuple[float, float, float]:
        position = suggest_non_overlapping_position(source.asset_type, tuple(self.assets))
        if position == (0.0, 0.0, 4.5):
            orthogonal = DraftAsset(
                source.asset_type,
                "placement_probe",
                "Placement probe",
                (5.0, 0.0, 4.5),
                source.yaw_degrees,
                source.scale,
            )
            orthogonal_target = build_static_draft_targets((orthogonal,))[0]
            if not any(
                _bounds_overlap(orthogonal_target.bounds, target.bounds)
                for target in build_static_draft_targets(tuple(self.assets))
            ):
                position = orthogonal.position
        return position

    def _append_asset_copy(self, source: DraftAsset) -> None:
        index = 1
        while any(asset.instance_id == f"draft_{source.asset_type}_{index}" for asset in self.assets):
            index += 1
        self.assets.append(
            DraftAsset(
                source.asset_type,
                f"draft_{source.asset_type}_{index}",
                f"{source.label} copy",
                self._stage_copy_position(source),
                source.yaw_degrees,
                source.scale,
            )
        )
        self._refresh()
        self.draft_list.setCurrentRow(len(self.assets) - 1)
        self._ensure_active_asset_visible()
        self._record_history()

    def _paste_asset(self) -> None:
        self._commit_transform_edit()
        self._commit_asset_label()
        if self._clipboard_asset is None:
            return
        self._append_asset_copy(self._clipboard_asset)

    def _duplicate_asset(self) -> None:
        self._commit_transform_edit()
        self._commit_asset_label()
        row = self.draft_list.currentRow()
        if not 0 <= row < len(self.assets):
            return
        self._append_asset_copy(self.assets[row])

    def _review_scenario_document(self) -> dict[str, Any]:
        return {
            "sequence": [
                {"id": "ready", "label": self.scenario_fields["ready"].text().strip()},
                {"id": "cycle", "label": self.scenario_fields["cycle"].text().strip()},
                {"id": "complete", "label": self.scenario_fields["complete"].text().strip()},
            ],
            "alarm": {
                "id": self.scenario_fields["alarm_id"].text().strip(),
                "message": self.scenario_fields["alarm_message"].text().strip(),
            },
        }

    def _review_scenario_state(self) -> tuple[str, str, str, str, str]:
        scenario = self._review_scenario_document()
        return (
            scenario["sequence"][0]["label"],
            scenario["sequence"][1]["label"],
            scenario["sequence"][2]["label"],
            scenario["alarm"]["id"],
            scenario["alarm"]["message"],
        )

    def _set_review_scenario_fields(self, scenario: Mapping[str, Any]) -> None:
        fallback = default_review_scenario()
        raw_sequence = scenario.get("sequence") if isinstance(scenario, Mapping) else None
        sequence = raw_sequence if isinstance(raw_sequence, list) else fallback["sequence"]
        raw_alarm = scenario.get("alarm") if isinstance(scenario, Mapping) else None
        alarm = raw_alarm if isinstance(raw_alarm, Mapping) else fallback["alarm"]
        values = {
            "ready": str(sequence[0].get("label", fallback["sequence"][0]["label"])),
            "cycle": str(sequence[1].get("label", fallback["sequence"][1]["label"])) if len(sequence) > 1 else fallback["sequence"][1]["label"],
            "complete": str(sequence[2].get("label", fallback["sequence"][2]["label"])) if len(sequence) > 2 else fallback["sequence"][2]["label"],
            "alarm_id": str(alarm.get("id", fallback["alarm"]["id"])),
            "alarm_message": str(alarm.get("message", fallback["alarm"]["message"])),
        }
        for key, value in values.items():
            field = self.scenario_fields[key]
            field.blockSignals(True)
            field.setText(value)
            field.blockSignals(False)
            if key == "alarm_message":
                field.setToolTip(value)
                field.setCursorPosition(0)

    def _set_review_scenario_defaults(self) -> None:
        self._set_review_scenario_fields(default_review_scenario())

    def _document(self) -> dict[str, Any]:
        return build_static_draft_document(
            draft_id=self.draft_id,
            name=self.draft_name.text(),
            assets=tuple(self.assets),
            editor_view=self._editor_view_document(),
            review_scenario=self._review_scenario_document(),
        )

    def _editor_view_document(self) -> dict[str, float]:
        return {
            "yawDegrees": float(self.viewport._yaw_degrees),
            "pitchDegrees": float(self.viewport._pitch_degrees),
            "zoom": float(self.viewport._zoom),
            "panX": float(self.viewport._pan_x),
            "panY": float(self.viewport._pan_y),
        }

    def _editor_view_tuple(self) -> EditorView:
        view = self._editor_view_document()
        return (
            view["yawDegrees"],
            view["pitchDegrees"],
            view["zoom"],
            view["panX"],
            view["panY"],
        )

    def _restore_editor_view(self, document: Mapping[str, Any]) -> None:
        raw_view = document.get("editorView")
        if raw_view is None:
            self.viewport.reset_camera()
            return
        yaw, pitch, zoom, pan_x, pan_y = _parse_editor_view(raw_view)
        self.viewport._yaw_degrees = yaw
        self.viewport._pitch_degrees = pitch
        self.viewport._zoom = zoom
        self.viewport._pan_x = pan_x
        self.viewport._pan_y = pan_y
        self.viewport.container.update()

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        answer = self.qt["QtWidgets"].QMessageBox.question(
            self.dialog,
            "Unsaved draft changes",
            "Discard unsaved static layout changes?",
            self.qt["QtWidgets"].QMessageBox.StandardButton.Yes
            | self.qt["QtWidgets"].QMessageBox.StandardButton.No,
            self.qt["QtWidgets"].QMessageBox.StandardButton.No,
        )
        return answer == self.qt["QtWidgets"].QMessageBox.StandardButton.Yes

    def _close(self) -> None:
        if self._confirm_discard():
            self.dialog.reject()

    def _new_draft(self) -> None:
        if not self._confirm_discard():
            return
        self.assets = self._default_assets()
        self.draft_id = "static-review-draft"
        self.current_path = None
        self.draft_name.blockSignals(True)
        self.draft_name.setText("Static Draft")
        self.draft_name.blockSignals(False)
        self._set_review_scenario_defaults()
        self._dirty = False
        self._reset_history()
        self._suppress_view_dirty = True
        try:
            self.viewport.reset_camera()
        finally:
            self._suppress_view_dirty = False
        self._saved_view = self._editor_view_tuple()
        self._refresh()

    def _save(self) -> None:
        self._commit_transform_edit()
        QtWidgets = self.qt["QtWidgets"]
        suggested_path = str(self.current_path) if self.current_path else "static-review-draft.plcscene"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self.dialog, "Save static review draft", suggested_path, "RungProof scenes (*.plcscene)")
        if not path:
            return
        try:
            save_static_draft(Path(path), self._document())
        except (OSError, StaticDraftError) as exc:
            QtWidgets.QMessageBox.critical(self.dialog, "Draft not saved", str(exc))
            return
        self.current_path = Path(path)
        self._saved_state = self._editor_state()
        self._saved_view = self._editor_view_tuple()
        self._dirty = False
        self._refresh_viewport()
        self.dirty_badge.setVisible(False)
        self.status.setText(
            f"SAVED  ·  {Path(path).name}  ·  STATIC / REVIEW ONLY  ·  VIEW SAVED"
        )

    def _open(self) -> None:
        QtWidgets = self.qt["QtWidgets"]
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self.dialog, "Open static review draft", "", "RungProof scenes (*.plcscene *.json)")
        if not path:
            return
        if not self._confirm_discard():
            return
        try:
            document, assets = load_static_draft(Path(path))
        except StaticDraftError as exc:
            QtWidgets.QMessageBox.critical(self.dialog, "Draft rejected", str(exc))
            return
        self.assets = list(assets)
        self.draft_id = str(document["id"])
        self.current_path = Path(path)
        self.draft_name.blockSignals(True)
        self.draft_name.setText(str(document.get("name", "Static Draft")))
        self.draft_name.blockSignals(False)
        self._set_review_scenario_fields(document.get("reviewScenario", default_review_scenario()))
        self._dirty = False
        self._reset_history()
        self._suppress_view_dirty = True
        try:
            self._restore_editor_view(document)
        finally:
            self._suppress_view_dirty = False
        self._saved_view = self._editor_view_tuple()
        self._refresh()
        self.status.setText(f"OPENED  ·  {Path(path).name}  ·  STATIC / REVIEW ONLY")

    def exec(self) -> int:
        return self.dialog.exec()
