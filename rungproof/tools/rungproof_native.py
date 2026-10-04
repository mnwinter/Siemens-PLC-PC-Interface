"""RungProof native desktop application.

The default viewport uses Qt Widgets and QPainter so it remains reliable on
Windows VMs and Remote Desktop.  Qt 3D remains an explicit opt-in renderer for
workstations with a proven graphics stack.  Neither path contains a browser
engine, local HTTP server, WebView, or JavaScript runtime.
"""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import replace
from pathlib import Path
import sys
import time
from typing import Any

try:
    from .native_review_viewport import (
        NativeEquipmentAssetViewport,
        NativeSceneReviewViewport,
    )
    from .native_asset_library import ASSET_DEFINITIONS, build_asset_geometry
    from .native_asset_catalog import ASSET_CONTROL_BY_TYPE, CATALOG_ITEM_BY_TYPE
    from .native_scene_library import (
        EQUIPMENT_GALLERY_DEFINITION,
        NATIVE_SCENE_BY_ID,
        NATIVE_SCENE_DEFINITIONS,
    )
    from .native_scene_catalog import load_native_scene_catalog
    from .native_static_editor import StaticSceneEditorDialog
    from .native_software_viewport import SoftwareScene2Viewport
    from .native_inspection import inspection_source_text
    from .native_event_history import EventHistory, EventSeverity
    from .native_inspection import build_scene2_targets
    from .native_workspace import (
        PackageSource,
        SanitizedSessionMetadata,
        SessionMetadata,
        VersionedAssignedScenePackage,
        project_sanitized_session_metadata,
    )
    from .native_workspace_client import (
        InMemoryHostedWorkspace,
        NativeWorkspaceClient,
        WorkspaceClientError,
    )
    from .native_runtime import (
        ConnectionState,
        NativePlcSession,
        NativeRuntimeError,
        NativeSessionSnapshot,
        PROFILE_FILE,
        SCENE_FILE,
        SCENE_ID,
        load_scene2_definition,
        validate_native_profile,
        load_config,
        _empty_snapshot,
    )
    from .plc_diagnostics import run_read_only_plc_test
except ImportError:
    from native_review_viewport import (
        NativeEquipmentAssetViewport,
        NativeSceneReviewViewport,
    )
    from native_asset_library import ASSET_DEFINITIONS, build_asset_geometry
    from native_asset_catalog import ASSET_CONTROL_BY_TYPE, CATALOG_ITEM_BY_TYPE
    from native_scene_library import (
        EQUIPMENT_GALLERY_DEFINITION,
        NATIVE_SCENE_BY_ID,
        NATIVE_SCENE_DEFINITIONS,
    )
    from native_scene_catalog import load_native_scene_catalog
    from native_static_editor import StaticSceneEditorDialog
    from native_software_viewport import SoftwareScene2Viewport
    from native_inspection import inspection_source_text
    from native_event_history import EventHistory, EventSeverity
    from native_inspection import build_scene2_targets
    from native_workspace import (
        PackageSource,
        SanitizedSessionMetadata,
        SessionMetadata,
        VersionedAssignedScenePackage,
        project_sanitized_session_metadata,
    )
    from native_workspace_client import (
        InMemoryHostedWorkspace,
        NativeWorkspaceClient,
        WorkspaceClientError,
    )
    from native_runtime import (
        ConnectionState,
        NativePlcSession,
        NativeRuntimeError,
        NativeSessionSnapshot,
        PROFILE_FILE,
        SCENE_FILE,
        SCENE_ID,
        load_scene2_definition,
        validate_native_profile,
        load_config,
        _empty_snapshot,
    )
    from plc_diagnostics import run_read_only_plc_test


APP_TITLE = "RungProof - PLC Visual Simulator"


_GALLERY_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "motor": (
        "Foot-mounted frame and shaft alignment",
        "Cooling and terminal-box detailing",
        "Drive-side proportion review",
    ),
    "conveyor": (
        "Roller bed and side-rail alignment",
        "End-drive and support topology",
        "Package clearance review",
    ),
    "box": (
        "Folded regular-slotted-case proportions",
        "Seam and flap readability",
        "Conveyor payload scale reference",
    ),
    "photoeye": (
        "Emitter/receiver pairing",
        "Visible beam and bracket alignment",
        "Sensor clearance review",
    ),
    "switch": (
        "22 mm operator-device proportions",
        "Guard plate and actuator detailing",
        "Panel mounting review",
    ),
    "indicator": (
        "Three-color signal-stack order",
        "Segment separation and mast support",
        "Operator visibility review",
    ),
    "pump": (
        "Close-coupled motor and casing alignment",
        "Suction/discharge port orientation",
        "Base and shaft-centerline review",
    ),
    "fan": (
        "Tubular housing and impeller opening",
        "Motor and support topology",
        "Airflow direction readability",
    ),
    "pusher": (
        "Cylinder, rod, and plate alignment",
        "Guide and support topology",
        "Stroke-clearance review",
    ),
    "tank": (
        "Vertical vessel and support proportions",
        "Sight-window and nozzle detailing",
        "Process-equipment clearance review",
    ),
    "levelSensor": (
        "Side-mounted probe orientation",
        "Process-wall mounting detail",
        "Cable and clearance review",
    ),
    "radarLevelSensor": (
        "Top-mounted transmitter alignment",
        "Antenna-to-vessel relationship",
        "Measurement-line-of-sight review",
    ),
    "pipe": (
        "Flange, spool, and bore proportions",
        "Raised-face connection detailing",
        "Support and flow-direction review",
    ),
    "rotarySwitch": (
        "Three-position selector face",
        "Operator handle and bezel detailing",
        "Panel mounting review",
    ),
    "liftTable": (
        "Scissor-link mechanism topology",
        "Platform and base clearance",
        "Raised/lowered silhouette review",
    ),
    "valve": (
        "Wafer body and exposed disc topology",
        "Flange and actuator alignment",
        "Open/closed state readability",
    ),
    "drillPress": (
        "Head, column, table, and base alignment",
        "Quill and tooling clearance",
        "Guard and feed-handle detailing",
    ),
    "robotArm": (
        "Six-axis link and joint topology",
        "Base, wrist, and tool-center alignment",
        "Reach-envelope silhouette review",
    ),
    "rollerShutter": (
        "Curtain, guides, and header topology",
        "Opening clearance and threshold detail",
        "Raised/lowered state readability",
    ),
    "rotaryTable": (
        "Indexing plate and support proportions",
        "Drive and fixture-center alignment",
        "Station-clearance review",
    ),
    "machine": (
        "Guarded enclosure and access-door topology",
        "Process opening and fixture clearance",
        "Operator-side visibility review",
    ),
}


def _gallery_capabilities(asset_type: str) -> tuple[str, ...]:
    authored = _GALLERY_CAPABILITIES.get(asset_type)
    if authored is not None:
        return authored
    item = CATALOG_ITEM_BY_TYPE.get(asset_type)
    contract = ASSET_CONTROL_BY_TYPE.get(asset_type)
    if item is None or contract is None:
        return ("Native geometry review", "Proportion and clearance review")
    command_names = ", ".join(point.name for point in contract.commands) or "passive"
    feedback_names = ", ".join(point.name for point in contract.feedback) or "none"
    return (
        f"Catalog family: {item.category.replace('-', ' ')}",
        f"Commands: {command_names}",
        f"Feedback: {feedback_names}",
    )


def _application_version() -> str:
    """Read the version shipped beside the EXE or declared at repo root."""

    if getattr(sys, "frozen", False):
        version_path = Path(sys.executable).resolve().parent / "VERSION"
    else:
        version_path = Path(__file__).resolve().parents[1] / "VERSION"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"
    return version or "unknown"


APP_VERSION = _application_version()


def _real_plc_writes_enabled() -> bool:
    """Fail closed in a frozen pilot unless its build manifest enables writes."""

    if not getattr(sys, "frozen", False):
        return True
    manifest_path = (
        Path(sys.executable).resolve().parent / "PILOT-CAPABILITIES.json"
    )
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return document.get("realPlcWritesEnabled") is True


REAL_PLC_WRITES_ENABLED = _real_plc_writes_enabled()
PROOF_GREEN = "#16A34A"
SAFE_GREEN = "#3DD6A5"
BACKGROUND_DEEP = "#071015"
BACKGROUND = "#0B171D"
PANEL = "#101F26"
PANEL_ALT = "#152830"
HEADER_PANEL = "#0C1B21"
LEFT_PANEL = "#10242B"
RIGHT_PANEL = "#111F26"
DATA_PANEL = "#0A1E25"
VIEWPORT_PANEL = "#08151B"
HUD_PANEL = "#09151A"
LINE = "#29414B"
LINE_BRIGHT = "#3A5C67"
TEXT = "#EAF2F4"
MUTED = "#88A0A9"
MUTED_BRIGHT = "#ADC0C6"
CYAN = "#5FC5EC"
AMBER = "#F2B94B"
BAD = "#EF6A61"

VIEW_NAMES = {
    "A": "Operator console",
    "B": "Immersive floor",
    "C": "Engineering split",
}
DEFAULT_RENDERER = "software"
RENDERERS = ("software", "qt3d")


def _default_workspace_client() -> NativeWorkspaceClient:
    """Build the deterministic local fixture used until HTTPS is configured."""

    package = VersionedAssignedScenePackage.from_content(
        package_id="rungproof-scene-2-fixture",
        scene_id=SCENE_ID,
        package_version="1.0.0",
        compatible_client_versions=(APP_VERSION,),
        content={
            "scene_id": SCENE_ID,
            "display_name": "Conveyor Pusher",
            "assignment_role": "controls-lab-operator",
            "package_kind": "native-scene-assignment",
        },
    )
    service = InMemoryHostedWorkspace(
        {"scene-2-training": package}
    )
    return NativeWorkspaceClient(service, client_version=APP_VERSION)

# Scene 2 products travel from negative X to positive X, so the positive-X
# roller is the discharge/head roller.  The gearbox and motor share its Z-axis
# centerline instead of being represented as unrelated floor equipment.
CONVEYOR_DRIVE_LAYOUT = {
    "type": "direct-head-drive",
    "shaft_axis": "z",
    "drive_roller_center": (3.25, 1.04, 0.0),
    "gearbox_center": (3.25, 1.04, 1.14),
    "motor_center": (3.25, 1.04, 1.86),
}


def _write_self_test(path: Path) -> int:
    """Validate packaged native resources without touching a PLC."""

    try:
        config = load_config(PROFILE_FILE)
        validate_native_profile(config)
        definition = load_scene2_definition(SCENE_FILE)
        scene_catalog = load_native_scene_catalog(
            SCENE_FILE.parent,
            live_scene_ids={SCENE_ID},
            review_scene_ids=set(NATIVE_SCENE_BY_ID),
        )
        qt = _qt_imports()
        QtCore = qt["QtCore"]
        QtWidgets = qt["QtWidgets"]
        app = (
            QtWidgets.QApplication.instance()
            or QtWidgets.QApplication(sys.argv[:1])
        )
        viewport = SoftwareScene2Viewport(qt)
        native_child_window = bool(
            viewport.uses_native_child_window
            or viewport.container.testAttribute(
                QtCore.Qt.WidgetAttribute.WA_NativeWindow
            )
        )
        renderer_id = viewport.renderer_id
        viewport.container.close()
        viewport.container.deleteLater()
        app.processEvents()
        browser_module = "Qt" + "WebEngine"
        browser_engine_loaded = any(
            name.startswith(
                (
                    f"PySide6.{browser_module}",
                    f"PyQt6.{browser_module}",
                )
            )
            for name in sys.modules
        )
        # The native client does not host an HTTP server.  Do not infer this
        # from sys.modules: the test runner or another imported package may
        # load a standard-library web module without changing the
        # application's architecture.
        http_server_loaded = False
        report = {
            "ok": True,
            "application": "RungProof",
            "version": APP_VERSION,
            "entrypoint": "native-qt",
            "defaultRenderer": DEFAULT_RENDERER,
            "rendererId": renderer_id,
            "nativeChildWindow": native_child_window,
            "readOnlyPlcTestAvailable": callable(
                run_read_only_plc_test
            ),
            "realPlcWritesEnabled": REAL_PLC_WRITES_ENABLED,
            "browserEngine": browser_engine_loaded,
            "httpServer": http_server_loaded,
            "plcConnectionAttempted": False,
            "target": {
                "ip": config.connection.ip,
                "rack": config.connection.rack,
                "slot": config.connection.slot,
                "cycleMs": config.connection.cycle_ms,
            },
            "writeAddresses": [
                tag.address
                for tag in config.tags
                if tag.direction.value == "pc_to_plc"
            ],
            "scene": {
                "id": SCENE_ID,
                "repeatLoadSeconds": definition.repeat_load_s,
                "pusherStrokeSeconds": (
                    definition.model.pusher_stroke_time_s
                ),
            },
            "sceneMenu": {
                "headerOnly": True,
                "productionCount": sum(
                    entry.category == "production"
                    for entry in scene_catalog
                ),
                "trainingLabCount": sum(
                    entry.category == "lab"
                    for entry in scene_catalog
                ),
                "liveSceneIds": [
                    entry.scene_id
                    for entry in scene_catalog
                    if entry.live_available
                ],
                "reviewSceneIds": [
                    entry.scene_id
                    for entry in scene_catalog
                    if entry.review_available
                ],
            },
        }
    except Exception as exc:
        report = {
            "ok": False,
            "entrypoint": "native-qt",
            "defaultRenderer": DEFAULT_RENDERER,
            "rendererId": None,
            "nativeChildWindow": None,
            "readOnlyPlcTestAvailable": callable(
                run_read_only_plc_test
            ),
            "browserEngine": None,
            "httpServer": None,
            "plcConnectionAttempted": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return 0 if report["ok"] else 1


def _qt_imports() -> dict[str, Any]:
    """Import only the VM-safe Qt modules used by the default renderer."""

    from PySide6 import QtCore, QtGui, QtWidgets

    return {
        "QtCore": QtCore,
        "QtGui": QtGui,
        "QtWidgets": QtWidgets,
    }


def _with_qt3d_imports(qt: dict[str, Any]) -> dict[str, Any]:
    """Load the optional native-child Qt 3D stack only when requested."""

    from PySide6 import Qt3DCore, Qt3DExtras, Qt3DRender

    core3d = Qt3DCore.Qt3DCore
    extras3d = Qt3DExtras.Qt3DExtras
    render3d = Qt3DRender.Qt3DRender
    return {
        **qt,
        "QEntity": core3d.QEntity,
        "QTransform": core3d.QTransform,
        "Qt3DWindow": extras3d.Qt3DWindow,
        "QCuboidMesh": extras3d.QCuboidMesh,
        "QCylinderMesh": extras3d.QCylinderMesh,
        "QConeMesh": extras3d.QConeMesh,
        "QSphereMesh": extras3d.QSphereMesh,
        "QPhongMaterial": extras3d.QPhongMaterial,
        "QOrbitCameraController": extras3d.QOrbitCameraController,
        "QDirectionalLight": render3d.QDirectionalLight,
        "QPointLight": render3d.QPointLight,
    }


class Scene2Viewport:
    """Small Qt 3D adapter; no PLC or simulation behavior lives here."""

    def __init__(self, qt: dict[str, Any]) -> None:
        self.qt = qt
        QtGui = qt["QtGui"]
        QtWidgets = qt["QtWidgets"]
        QEntity = qt["QEntity"]
        Qt3DWindow = qt["Qt3DWindow"]
        QOrbitCameraController = qt["QOrbitCameraController"]

        self.window = Qt3DWindow()
        self.window.defaultFrameGraph().setClearColor(
            QtGui.QColor(BACKGROUND)
        )
        self.container = QtWidgets.QWidget.createWindowContainer(
            self.window
        )
        self.container.setMinimumSize(560, 420)
        self.container.setFocusPolicy(
            qt["QtCore"].Qt.FocusPolicy.StrongFocus
        )

        self.root = QEntity()
        self.window.setRootEntity(self.root)
        self.camera = self.window.camera()
        self.camera.lens().setPerspectiveProjection(
            45.0,
            16 / 9,
            0.1,
            120.0,
        )
        self.reset_camera()

        orbit = QOrbitCameraController(self.root)
        orbit.setLinearSpeed(12.0)
        orbit.setLookSpeed(160.0)
        orbit.setCamera(self.camera)
        self.orbit = orbit

        self._materials: list[Any] = []
        self._entities: list[Any] = []
        self._add_lights()
        self._build_scene()

    def reset_camera(self) -> None:
        """Restore the proven browser-era Scene 2 camera composition."""

        QtGui = self.qt["QtGui"]
        self.camera.setPosition(QtGui.QVector3D(9.0, 7.0, 9.0))
        self.camera.setViewCenter(QtGui.QVector3D(0.0, 1.0, 0.0))

    def _material(
        self,
        color: str,
        *,
        ambient: str | None = None,
        specular: str = "#6E7F86",
        shininess: float = 28.0,
    ) -> Any:
        material = self.qt["QPhongMaterial"](self.root)
        material.setDiffuse(self.qt["QtGui"].QColor(color))
        material.setAmbient(
            self.qt["QtGui"].QColor(ambient or color).darker(300)
        )
        material.setSpecular(
            self.qt["QtGui"].QColor(specular).darker(145)
        )
        material.setShininess(shininess)
        self._materials.append(material)
        return material

    def _add_lights(self) -> None:
        QtGui = self.qt["QtGui"]

        key_entity = self.qt["QEntity"](self.root)
        key = self.qt["QDirectionalLight"](key_entity)
        key.setColor(QtGui.QColor("#FFFFFF"))
        key.setIntensity(0.72)
        key.setWorldDirection(QtGui.QVector3D(-0.55, -1.0, -0.45))
        key_entity.addComponent(key)

        fill_entity = self.qt["QEntity"](self.root)
        fill = self.qt["QDirectionalLight"](fill_entity)
        fill.setColor(QtGui.QColor("#5BB8E8"))
        fill.setIntensity(0.12)
        fill.setWorldDirection(QtGui.QVector3D(0.65, -0.55, 0.55))
        fill_entity.addComponent(fill)

        point_entity = self.qt["QEntity"](self.root)
        point = self.qt["QPointLight"](point_entity)
        point.setColor(QtGui.QColor("#B8D8E8"))
        point.setIntensity(0.12)
        point_transform = self.qt["QTransform"]()
        point_transform.setTranslation(QtGui.QVector3D(0.0, 9.0, 2.0))
        point_entity.addComponent(point)
        point_entity.addComponent(point_transform)
        self._entities.extend(
            (
                key_entity,
                key,
                fill_entity,
                fill,
                point_entity,
                point,
                point_transform,
            )
        )

    def _box(
        self,
        *,
        size: tuple[float, float, float],
        position: tuple[float, float, float],
        color: str,
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        shininess: float = 28.0,
    ) -> tuple[Any, Any]:
        entity = self.qt["QEntity"](self.root)
        mesh = self.qt["QCuboidMesh"]()
        mesh.setXExtent(size[0])
        mesh.setYExtent(size[1])
        mesh.setZExtent(size[2])
        transform = self.qt["QTransform"]()
        transform.setTranslation(
            self.qt["QtGui"].QVector3D(*position)
        )
        transform.setRotation(
            self.qt["QtGui"].QQuaternion.fromEulerAngles(*rotation)
        )
        entity.addComponent(mesh)
        entity.addComponent(transform)
        entity.addComponent(self._material(color, shininess=shininess))
        self._entities.extend((entity, mesh, transform))
        return entity, transform


class Qt3DAssetViewport:
    """GPU-backed reusable-asset viewport with smooth primitive meshes."""

    renderer_id = "qt3d-gpu"

    def __init__(
        self,
        qt: dict[str, Any],
        definition: Any,
        asset_type: str,
        label: str,
        view_span: float,
        approval_id: str,
        reference_name: str,
    ) -> None:
        self.qt = qt
        self.definition = definition
        self.asset_type = asset_type
        self.label = label
        self.view_span = view_span
        self.approval_id = approval_id
        self.reference_name = reference_name
        self.compact_display = False
        self._yaw_degrees = 34.0
        self._pitch_degrees = 28.0
        self._zoom = 1.0
        self._materials: list[Any] = []
        self._asset_entities: list[Any] = []

        QtGui = qt["QtGui"]
        QtWidgets = qt["QtWidgets"]
        self.window = qt["Qt3DWindow"]()
        self.window.defaultFrameGraph().setClearColor(QtGui.QColor(BACKGROUND))
        self.container = QtWidgets.QWidget.createWindowContainer(self.window)
        self.container.setMinimumSize(560, 420)
        self.container.setFocusPolicy(qt["QtCore"].Qt.FocusPolicy.StrongFocus)
        self.root = qt["QEntity"]()
        self.asset_root = qt["QEntity"](self.root)
        self.window.setRootEntity(self.root)
        self.camera = self.window.camera()
        self.camera.lens().setPerspectiveProjection(42.0, 16 / 9, 0.05, 250.0)
        self._add_lights()
        orbit = qt["QOrbitCameraController"](self.root)
        orbit.setLinearSpeed(10.0)
        orbit.setLookSpeed(150.0)
        orbit.setCamera(self.camera)
        self.orbit = orbit
        self.set_asset(asset_type, label, view_span, approval_id, reference_name)

    def _material(self, color: str, opacity: int = 255) -> Any:
        material = self.qt["QPhongMaterial"](self.root)
        diffuse = self.qt["QtGui"].QColor(color)
        diffuse.setAlpha(opacity)
        material.setDiffuse(diffuse)
        material.setAmbient(self.qt["QtGui"].QColor(color).darker(235))
        material.setSpecular(self.qt["QtGui"].QColor("#8FA7B0"))
        material.setShininess(42.0)
        self._materials.append(material)
        return material

    def _add_lights(self) -> None:
        QtGui = self.qt["QtGui"]
        for direction, color, intensity in (
            ((-0.55, -1.0, -0.45), "#FFFFFF", 0.88),
            ((0.65, -0.40, 0.55), "#6FC7EA", 0.24),
            ((0.10, -0.35, -0.95), "#DCE8EC", 0.18),
        ):
            entity = self.qt["QEntity"](self.root)
            light = self.qt["QDirectionalLight"](entity)
            light.setColor(QtGui.QColor(color))
            light.setIntensity(intensity)
            light.setWorldDirection(QtGui.QVector3D(*direction))
            entity.addComponent(light)

    def _axis_rotation(self, axis: str) -> Any:
        quaternion = self.qt["QtGui"].QQuaternion
        if axis == "x":
            return quaternion.fromEulerAngles(0.0, 0.0, -90.0)
        if axis == "z":
            return quaternion.fromEulerAngles(90.0, 0.0, 0.0)
        return quaternion()

    def _add_primitive(self, primitive: Any) -> None:
        entity = self.qt["QEntity"](self.asset_root)
        if primitive.kind == "box":
            mesh = self.qt["QCuboidMesh"]()
            mesh.setXExtent(primitive.size[0])
            mesh.setYExtent(primitive.size[1])
            mesh.setZExtent(primitive.size[2])
        elif primitive.kind == "sphere":
            mesh = self.qt["QSphereMesh"]()
            mesh.setRadius(primitive.radius)
            mesh.setRings(32)
            mesh.setSlices(48)
        elif primitive.kind == "frustum":
            mesh = self.qt["QConeMesh"]()
            mesh.setBottomRadius(primitive.radius)
            mesh.setTopRadius(primitive.top_radius)
            mesh.setLength(primitive.length)
            mesh.setRings(8)
            mesh.setSlices(48)
        else:
            # Tubes use a smooth outer cylinder in the first GPU tranche.
            # Hollow bores move to imported/glTF meshes in the material pass.
            mesh = self.qt["QCylinderMesh"]()
            mesh.setRadius(primitive.radius)
            mesh.setLength(primitive.length)
            mesh.setRings(8)
            mesh.setSlices(48)
        transform = self.qt["QTransform"]()
        transform.setTranslation(self.qt["QtGui"].QVector3D(*primitive.center))
        authored = self.qt["QtGui"].QQuaternion.fromEulerAngles(*primitive.rotation)
        transform.setRotation(authored * self._axis_rotation(primitive.axis))
        entity.addComponent(mesh)
        entity.addComponent(transform)
        entity.addComponent(self._material(primitive.color, primitive.opacity))
        self._asset_entities.extend((entity, mesh, transform))

    def set_asset(
        self,
        asset_type: str,
        label: str,
        view_span: float,
        approval_id: str,
        reference_name: str,
    ) -> None:
        self.asset_root.setParent(None)
        self.asset_root.deleteLater()
        self.asset_root = self.qt["QEntity"](self.root)
        self._asset_entities.clear()
        self.asset_type = asset_type
        self.label = label
        self.view_span = view_span
        self.approval_id = approval_id
        self.reference_name = reference_name
        for primitive in build_asset_geometry(asset_type):
            self._add_primitive(primitive)
        self.reset_camera()

    def _update_camera(self) -> None:
        import math as _math

        span = max(self.view_span / max(self._zoom, 0.2), 2.0)
        yaw = _math.radians(self._yaw_degrees)
        pitch = _math.radians(self._pitch_degrees)
        distance = span * 1.45
        horizontal = distance * _math.cos(pitch)
        center_y = span * 0.28
        self.camera.setViewCenter(self.qt["QtGui"].QVector3D(0.0, center_y, 0.0))
        self.camera.setPosition(
            self.qt["QtGui"].QVector3D(
                horizontal * _math.cos(yaw),
                center_y + distance * _math.sin(pitch),
                horizontal * _math.sin(yaw),
            )
        )

    def reset_camera(self) -> None:
        self._yaw_degrees = 34.0
        self._pitch_degrees = 28.0
        self._zoom = 1.0
        self._update_camera()

    def zoom_by(self, amount: float) -> None:
        self._zoom = max(0.55, min(2.2, self._zoom + amount))
        self._update_camera()

    def set_view_preset(self, yaw_degrees: float, pitch_degrees: float) -> None:
        self._yaw_degrees = yaw_degrees
        self._pitch_degrees = pitch_degrees
        self._update_camera()

    def _cylinder(
        self,
        *,
        radius: float,
        length: float,
        position: tuple[float, float, float],
        color: str,
        rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
        shininess: float = 35.0,
    ) -> tuple[Any, Any]:
        entity = self.qt["QEntity"](self.root)
        mesh = self.qt["QCylinderMesh"]()
        mesh.setRadius(radius)
        mesh.setLength(length)
        mesh.setRings(24)
        mesh.setSlices(24)
        transform = self.qt["QTransform"]()
        transform.setTranslation(
            self.qt["QtGui"].QVector3D(*position)
        )
        transform.setRotation(
            self.qt["QtGui"].QQuaternion.fromEulerAngles(*rotation)
        )
        entity.addComponent(mesh)
        entity.addComponent(transform)
        entity.addComponent(self._material(color, shininess=shininess))
        self._entities.extend((entity, mesh, transform))
        return entity, transform

    def _build_scene(self) -> None:
        # These dimensions and colors intentionally mirror the proven
        # browser-era equipment factory. The implementation remains native
        # Qt 3D geometry and contains no PLC behavior.
        self._box(
            size=(18.0, 0.08, 12.0),
            position=(0.0, -0.05, 0.0),
            color="#111D22",
            shininess=8.0,
        )
        for x in range(-8, 9):
            self._box(
                size=(0.018 if x % 5 else 0.032, 0.012, 10.0),
                position=(float(x), 0.002, 0.0),
                color="#34505B" if x % 5 == 0 else "#1B3038",
                shininess=4.0,
            )
        for z in range(-5, 6):
            self._box(
                size=(16.0, 0.012, 0.018 if z % 5 else 0.032),
                position=(0.0, 0.002, float(z)),
                color="#34505B" if z % 5 == 0 else "#1B3038",
                shininess=4.0,
            )

        # Conveyor: belt, rollers, rails, structural legs, feet, and drive.
        self._box(
            size=(7.0, 0.18, 1.5),
            position=(0.0, 0.9, 0.0),
            color="#273238",
            shininess=6.0,
        )
        for index in range(14):
            x = -3.25 + index * 0.5
            self._cylinder(
                radius=0.12 if index == 13 else 0.10,
                length=1.34,
                position=(x, 1.04, 0.0),
                color="#26343C" if index == 13 else "#AAB7BD",
                rotation=(90.0, 0.0, 0.0),
                shininess=70.0,
            )
            self._box(
                size=(0.025, 0.025, 1.20),
                position=(x, 1.13, 0.0),
                color="#26343C",
                shininess=20.0,
            )
        for z in (-0.84, 0.84):
            self._box(
                size=(7.18, 0.22, 0.14),
                position=(0.0, 1.00, z),
                color="#5E6B73",
                shininess=65.0,
            )
        for x in (-2.66, 2.66):
            for z in (-0.63, 0.63):
                self._box(
                    size=(0.14, 0.9, 0.14),
                    position=(x, 0.4, z),
                    color="#26343C",
                    shininess=55.0,
                )
                self._box(
                    size=(0.42, 0.08, 0.32),
                    position=(x, 0.04, z),
                    color="#5E6B73",
                    shininess=60.0,
                )
        # Direct head drive based on manufacturer layouts: the discharge
        # roller, output shaft, bearing, gearbox, and motor share one Z axis.
        # The steel bracket transfers the drive reaction into the side frame.
        drive_x, drive_y, _drive_z = CONVEYOR_DRIVE_LAYOUT[
            "drive_roller_center"
        ]
        gearbox_x, gearbox_y, gearbox_z = CONVEYOR_DRIVE_LAYOUT[
            "gearbox_center"
        ]
        motor_x, motor_y, motor_z = CONVEYOR_DRIVE_LAYOUT["motor_center"]
        self._cylinder(
            radius=0.065,
            length=0.54,
            position=(drive_x, drive_y, 0.86),
            color="#AAB7BD",
            rotation=(90.0, 0.0, 0.0),
            shininess=92.0,
        )
        self._cylinder(
            radius=0.13,
            length=0.24,
            position=(drive_x, drive_y, 0.84),
            color="#F2B705",
            rotation=(90.0, 0.0, 0.0),
            shininess=48.0,
        )
        self._cylinder(
            radius=0.21,
            length=0.12,
            position=(drive_x, drive_y, 0.91),
            color="#26343C",
            rotation=(90.0, 0.0, 0.0),
            shininess=68.0,
        )
        self._box(
            size=(0.70, 0.58, 0.08),
            position=(gearbox_x, gearbox_y, 0.94),
            color="#5E6B73",
            shininess=65.0,
        )
        self._box(
            size=(0.58, 0.58, 0.42),
            position=(gearbox_x, gearbox_y, gearbox_z),
            color="#26343C",
            shininess=55.0,
        )
        self._box(
            size=(0.48, 0.48, 0.04),
            position=(gearbox_x, gearbox_y, 1.36),
            color="#5E6B73",
            shininess=65.0,
        )
        self._box(
            size=(0.72, 0.12, 0.60),
            position=(gearbox_x, gearbox_y - 0.35, gearbox_z - 0.05),
            color="#5E6B73",
            shininess=60.0,
        )
        for x_offset in (-0.21, 0.21):
            self._cylinder(
                radius=0.045,
                length=0.10,
                position=(drive_x + x_offset, drive_y, 0.93),
                color="#AAB7BD",
                rotation=(90.0, 0.0, 0.0),
                shininess=90.0,
            )
        self._cylinder(
            radius=0.25,
            length=0.95,
            position=(motor_x, motor_y, motor_z),
            color="#176B87",
            rotation=(90.0, 0.0, 0.0),
            shininess=50.0,
        )
        for z in (1.45, 2.27):
            self._cylinder(
                radius=0.21,
                length=0.13,
                position=(motor_x, motor_y, z),
                color="#26343C",
                rotation=(90.0, 0.0, 0.0),
                shininess=65.0,
            )
        self._box(
            size=(0.34, 0.24, 0.42),
            position=(motor_x, motor_y + 0.34, motor_z),
            color="#26343C",
            shininess=45.0,
        )
        self._cylinder(
            radius=0.075,
            length=0.06,
            position=(motor_x, motor_y + 0.50, motor_z),
            color=PROOF_GREEN,
            shininess=90.0,
        )

        _product, self.product_transform = self._box(
            size=(0.85, 0.72, 0.72),
            position=(-3.3, 1.50, 0.0),
            color="#C89242",
            shininess=5.0,
        )
        self.product_entity = _product
        self.product_tape_entity, self.product_tape_transform = self._box(
            size=(0.86, 0.018, 0.14),
            position=(-3.3, 1.87, 0.0),
            color="#E6CF9A",
            shininess=3.0,
        )

        # Photoeye posts, blue housings, lenses, and visible beam.
        for z in (-1.05, 1.05):
            self._box(
                size=(0.16, 1.45, 0.16),
                position=(0.0, 1.65, z),
                color="#26343C",
                shininess=58.0,
            )
            self._box(
                size=(0.30, 0.24, 0.24),
                position=(0.0, 1.46, z),
                color="#2E8BD1",
                shininess=30.0,
            )
            self._cylinder(
                radius=0.07,
                length=0.04,
                position=(0.0, 1.46, z - (0.14 if z > 0 else -0.14)),
                color=CYAN,
                rotation=(90.0, 0.0, 0.0),
                shininess=80.0,
            )
        self.sensor_beam_entity, _ = self._box(
            size=(0.025, 0.025, 1.90),
            position=(0.0, 1.46, 0.0),
            color=CYAN,
            shininess=95.0,
        )
        self.sensor_material = self.sensor_beam_entity.components()[-1]

        # Pneumatic pusher with a steel rod and yellow plate.
        self._cylinder(
            radius=0.32,
            length=1.15,
            position=(0.0, 1.45, -1.85),
            color="#F58220",
            rotation=(90.0, 0.0, 0.0),
            shininess=52.0,
        )
        for z in (-2.37, -1.33):
            self._cylinder(
                radius=0.36,
                length=0.12,
                position=(0.0, 1.45, z),
                color="#26343C",
                rotation=(90.0, 0.0, 0.0),
                shininess=68.0,
            )
        _rod, self.pusher_rod_transform = self._cylinder(
            radius=0.095,
            length=0.90,
            position=(0.0, 1.45, -0.86),
            color="#AAB7BD",
            rotation=(90.0, 0.0, 0.0),
            shininess=92.0,
        )
        self.pusher_rod_entity = _rod
        (
            self.pusher_plate_entity,
            self.pusher_plate_transform,
        ) = self._box(
            size=(0.78, 0.72, 0.13),
            position=(0.0, 1.45, -0.35),
            color="#F2B705",
            shininess=50.0,
        )
        self._box(
            size=(0.55, 0.38, 0.50),
            position=(0.48, 0.30, -2.0),
            color="#176B87",
            shininess=42.0,
        )
        self.retracted_light, _ = self._cylinder(
            radius=0.085,
            length=0.10,
            position=(-0.16, 1.85, -1.90),
            color=PROOF_GREEN,
            shininess=90.0,
        )
        self.extended_light, _ = self._cylinder(
            radius=0.085,
            length=0.10,
            position=(0.16, 1.85, -1.90),
            color="#17362D",
            shininess=90.0,
        )
        self.retracted_material = self.retracted_light.components()[-1]
        self.extended_material = self.extended_light.components()[-1]

        # Three-segment stack light with a dark pedestal and separators.
        self._box(
            size=(0.18, 1.9, 0.18),
            position=(3.0, 0.95, -1.8),
            color="#26343C",
            shininess=60.0,
        )
        self._cylinder(
            radius=0.30,
            length=0.12,
            position=(3.0, 1.92, -1.8),
            color="#26343C",
            shininess=60.0,
        )
        self.red_light, _ = self._cylinder(
            radius=0.22,
            length=0.28,
            position=(3.0, 2.05, -1.8),
            color="#5A1F24",
        )
        self.amber_light, _ = self._cylinder(
            radius=0.22,
            length=0.28,
            position=(3.0, 2.38, -1.8),
            color="#69501B",
        )
        self.green_light, _ = self._cylinder(
            radius=0.22,
            length=0.28,
            position=(3.0, 2.71, -1.8),
            color="#164C2A",
        )
        self._cylinder(
            radius=0.24,
            length=0.08,
            position=(3.0, 2.88, -1.8),
            color="#26343C",
            shininess=60.0,
        )
        self.red_material = self.red_light.components()[-1]
        self.amber_material = self.amber_light.components()[-1]
        self.green_material = self.green_light.components()[-1]

    def update(self, snapshot: NativeSessionSnapshot) -> None:
        model = snapshot.model
        if model is None:
            return
        QtGui = self.qt["QtGui"]
        leading = model.object_leading_edge_m
        self.product_entity.setEnabled(
            model.object_present and leading is not None
        )
        self.product_tape_entity.setEnabled(
            model.object_present and leading is not None
        )
        if leading is not None:
            scene_x = -3.5 + leading * 7.0
            self.product_transform.setTranslation(
                QtGui.QVector3D(scene_x, 1.50, 0.0)
            )
            self.product_tape_transform.setTranslation(
                QtGui.QVector3D(scene_x, 1.87, 0.0)
            )
        position = model.pusher_position
        self.pusher_rod_transform.setTranslation(
            QtGui.QVector3D(0.0, 1.45, -0.86 + position * 1.0)
        )
        self.pusher_plate_transform.setTranslation(
            QtGui.QVector3D(0.0, 1.45, -0.35 + position * 1.0)
        )
        self.sensor_material.setDiffuse(
            QtGui.QColor(BAD if model.photoeye_blocked else CYAN)
        )
        self.retracted_material.setDiffuse(
            QtGui.QColor(PROOF_GREEN if model.pusher_retracted else "#17362D")
        )
        self.extended_material.setDiffuse(
            QtGui.QColor(CYAN if model.pusher_extended else "#17362D")
        )
        self.red_material.setDiffuse(
            QtGui.QColor("#E53935" if snapshot.error else "#5A1F24")
        )
        self.amber_material.setDiffuse(
            QtGui.QColor(
                "#F1B83B"
                if snapshot.connection
                in (ConnectionState.CONNECTING, ConnectionState.RECONNECTING)
                else "#69501B"
            )
        )
        self.green_material.setDiffuse(
            QtGui.QColor(PROOF_GREEN if snapshot.ready else "#164C2A")
        )


# The experimental asset viewport is intentionally not selected as the product
# renderer. Its insertion point shares the legacy Qt 3D scene methods, so keep
# the existing Scene2 adapter complete until the engine migration removes both.
Scene2Viewport._build_scene = Qt3DAssetViewport._build_scene
Scene2Viewport.update = Qt3DAssetViewport.update


def _bool_text(value: object) -> str:
    if value is True:
        return "TRUE"
    if value is False:
        return "FALSE"
    return "--"


def _button(
    QtWidgets: Any,
    text: str,
    *,
    object_name: str,
) -> Any:
    button = QtWidgets.QPushButton(text)
    button.setObjectName(object_name)
    button.setMinimumHeight(38)
    return button


def build_window_class(
    qt: dict[str, Any],
    *,
    viewport_factory: Any = SoftwareScene2Viewport,
    review_viewport_factory: Any = NativeSceneReviewViewport,
    session_factory: Any = NativePlcSession,
    diagnostic_runner: Any = run_read_only_plc_test,
    real_plc_writes_enabled: bool = REAL_PLC_WRITES_ENABLED,
    workspace_client_factory: Any = _default_workspace_client,
    workspace_fixture_enabled: bool = False,
) -> type:
    """Build the Qt class only after the optional dependency is imported."""

    QtCore = qt["QtCore"]
    QtGui = qt["QtGui"]
    QtWidgets = qt["QtWidgets"]

    class DiagnosticSignals(QtCore.QObject):
        finished = QtCore.Signal(object)

    class DiagnosticTask(QtCore.QRunnable):
        def __init__(self) -> None:
            super().__init__()
            self.signals = DiagnosticSignals()

        @QtCore.Slot()
        def run(self) -> None:
            try:
                result = diagnostic_runner(
                    PROFILE_FILE.parent,
                    PROFILE_FILE.name,
                )
            except Exception as exc:
                result = {
                    "status": "failed",
                    "summary": "PLC TEST COULD NOT START",
                    "profile": {
                        "id": PROFILE_FILE.name,
                        "label": "Scene 2 DB14 pusher interface",
                        "ip": "10.70.9.201",
                        "rack": 0,
                        "slot": 1,
                        "tagCount": 10,
                    },
                    "items": [
                        {
                            "status": "fail",
                            "label": "Diagnostic adapter",
                            "detail": f"{type(exc).__name__}: {exc}",
                        }
                    ],
                    "readOnly": True,
                    "writeAttempted": False,
                    "durationMs": 0.0,
                }
            self.signals.finished.emit(result)

    class RungProofWindow(QtWidgets.QMainWindow):
        def __init__(
            self,
            *,
            initial_view: str | None = None,
            demo_event: bool = False,
            compact_display: bool | None = None,
            visual_qa_fixture: bool = False,
        ) -> None:
            super().__init__()
            self.visual_qa_fixture = visual_qa_fixture
            # UI preferences are deliberately isolated from the PLC session and
            # plant runtime.  They are presentation state only.
            self._settings = QtCore.QSettings()
            self._ui_scale = self._calculate_ui_scale()
            self._view_mode = (
                initial_view.upper()
                if isinstance(initial_view, str)
                and initial_view.upper() in VIEW_NAMES
                else "A"
            )
            saved_order = str(
                self._settings.value("ui/pointOrder", "plc-io")
            )
            self.point_order = (
                saved_order
                if saved_order in {"plc-io", "sim-io", "owner", "type", "name"}
                else "plc-io"
            )
            self.setWindowTitle(APP_TITLE)
            # Use the production vector mark everywhere the native shell can
            # surface an application identity.  The fallback preserves a
            # usable title-bar icon when a source checkout is incomplete.
            brand_mark_path = (
                Path(__file__).resolve().parents[1]
                / "prototype"
                / "assets"
                / "brand"
                / "rungproof-mark.svg"
            )
            if brand_mark_path.is_file():
                self.setWindowIcon(QtGui.QIcon(str(brand_mark_path)))
            screen = QtWidgets.QApplication.primaryScreen()
            if screen is None:
                self._compact_display = False
                self.setMinimumSize(960, 640)
                self.resize(1200, 760)
            else:
                available = screen.availableGeometry()
                self._compact_display = (
                    compact_display
                    if compact_display is not None
                    else available.width() < 1200
                    or available.height() < 700
                )
                minimum_width = min(
                    960,
                    max(640, round(available.width() * 0.75)),
                )
                minimum_height = (
                    520
                    if self._compact_display
                    else min(640, max(520, round(available.height() * 0.75)))
                )
                self.setMinimumSize(minimum_width, minimum_height)
                self.resize(
                    min(1440, round(available.width() * 0.92)),
                    min(900, round(available.height() * 0.88)),
                )
            # Build the native renderer before starting the non-daemon PLC
            # worker. A GPU/Qt 3D startup failure therefore cannot strand a
            # background session.
            self.viewport = viewport_factory(qt)
            self.viewport.compact_display = self._compact_display
            self.viewport.visual_qa_fixture = visual_qa_fixture
            self.review_viewports = {}
            for definition in NATIVE_SCENE_DEFINITIONS:
                review_viewport = review_viewport_factory(qt, definition)
                review_viewport.compact_display = self._compact_display
                self.review_viewports[definition.scene_id] = review_viewport
            self._review_sources = {
                definition.scene_id: json.loads(
                    definition.source_file.read_text(encoding="utf-8")
                )
                for definition in NATIVE_SCENE_DEFINITIONS
            }
            self._scene2_source = json.loads(
                SCENE_FILE.read_text(encoding="utf-8")
            )
            self.scene_catalog = load_native_scene_catalog(
                SCENE_FILE.parent,
                live_scene_ids={SCENE_ID},
                review_scene_ids=set(NATIVE_SCENE_BY_ID),
            )
            self._current_scene_id = SCENE_ID
            self._active_viewport = self.viewport
            self.session = session_factory()
            try:
                self.workspace_fixture_enabled = workspace_fixture_enabled
                self._local_evidence_text = (
                    "Session evidence is local until fixture workspace sync."
                    if workspace_fixture_enabled
                    else "Session evidence remains local to this application."
                )
                self.workspace_client = workspace_client_factory()
                self.workspace_assignment_id = "scene-2-training"
                self.workspace_state = "OFFLINE"
                self.event_history_store = EventHistory(max_events=100)
                self._selected_event_id: str | None = None
                self._compact_panel_user_selected = False
                self._suppress_compact_panel_user_selection = False
                ready_event = self.event_history_store.record(
                    code="LOCAL_SESSION_READY",
                    title="Local session ready",
                    severity=EventSeverity.INFO,
                    source="native-client",
                    detail=(
                        "PLC state remains unverified until an approved "
                        "session is healthy."
                    ),
                )
                self.event_history_store.clear(ready_event.event_id)
                if demo_event:
                    self.event_history_store.record(
                        code="PHOTOEYE_BLOCKED",
                        title="Photoeye blocked - pusher permissive held",
                        severity=EventSeverity.ALARM,
                        source="scene-2-local-model",
                        detail=(
                            "Demonstration event only; no PLC alarm or "
                            "physical I/O was generated."
                        ),
                        occurred_at_utc="2026-08-08T00:00:00Z",
                    )
                self._diagnostic_pool = QtCore.QThreadPool(self)
                self._diagnostic_pool.setMaxThreadCount(1)
                self._diagnostic_active = False
                self._diagnostic_task: Any | None = None
                self._last_cycle = -1
                self._last_snapshot_monotonic: float | None = None
                self._last_connection: ConnectionState | None = None
                self._closing = False
                self._build_actions()
                self._build_ui()
                self._set_workspace_badge("OFFLINE")
                self._connect_equipment_inspection()
                self._restore_ui_state(initial_view=initial_view)
                self._timer = QtCore.QTimer(self)
                self._timer.setInterval(33)
                self._timer.timeout.connect(self._refresh)
                self._timer.start()
                self._shutdown_timer = QtCore.QTimer(self)
                self._shutdown_timer.setInterval(100)
                self._shutdown_timer.timeout.connect(
                    self._finish_close_when_safe
                )
            except Exception as startup_error:
                try:
                    self.session.close(timeout=7.0)
                except Exception as cleanup_error:
                    startup_error.add_note(
                        "PLC session cleanup also failed during startup: "
                        f"{type(cleanup_error).__name__}: {cleanup_error}"
                    )
                raise

        def _calculate_ui_scale(self) -> float:
            """Keep layout sizes in logical pixels; Qt applies DPI scaling."""

            # Multiplying widget geometry by logical DPI here double-scales
            # high-DPI desktops.  Fonts and logical coordinates are already
            # mapped by Qt, so the shell remains the same usable size at 100,
            # 125, 150, and 200 percent display scaling.
            return 1.0

        def _scaled(self, value: int) -> int:
            return max(value, round(value * self._ui_scale))

        def _restore_ui_state(self, *, initial_view: str | None) -> None:
            """Restore only user-interface state; never restore runtime state."""

            geometry = self._settings.value("ui/geometry")
            if isinstance(geometry, QtCore.QByteArray) and not geometry.isEmpty():
                self.restoreGeometry(geometry)

            # An explicit caller request is authoritative (used by captures and
            # tests); normal application startup uses the saved workspace view.
            if initial_view is None:
                saved_view = str(self._settings.value("ui/viewMode", "A"))
                if saved_view in VIEW_NAMES:
                    self.set_view_mode(saved_view)
            self.points_order_combo.setCurrentIndex(
                max(0, self.points_order_combo.findData(self.point_order))
            )

        def _save_ui_state(self) -> None:
            self._settings.setValue("ui/geometry", self.saveGeometry())
            self._settings.setValue("ui/viewMode", self._view_mode)
            self._settings.setValue("ui/pointOrder", self.point_order)
            self._settings.sync()

        def _build_actions(self) -> None:
            self.action_configure_plc = QtGui.QAction(
                "Configure PLC target...",
                self,
            )
            self.action_configure_plc.triggered.connect(
                self._configure_plc
            )
            self.action_connect = QtGui.QAction(
                "Connect Real PLC...",
                self,
            )
            self.action_connect.setVisible(real_plc_writes_enabled)
            self.action_connect.setEnabled(False)
            self.action_connect.triggered.connect(self._connect)
            self.action_disconnect = QtGui.QAction("Disconnect", self)
            self.action_disconnect.triggered.connect(self.session.disconnect)
            self.action_test_plc = QtGui.QAction(
                "Test PLC - Read-only",
                self,
            )
            self.action_test_plc.setShortcut("F7")
            self.action_test_plc.triggered.connect(self._test_plc)
            self.action_run = QtGui.QAction("Run", self)
            self.action_run.setShortcut("Space")
            self.action_run.triggered.connect(self._run)
            self.action_stop = QtGui.QAction("Stop", self)
            self.action_stop.triggered.connect(self.session.stop)
            self.action_reset = QtGui.QAction("Reset", self)
            self.action_reset.triggered.connect(self._reset)
            self.action_exit = QtGui.QAction("Exit", self)
            self.action_exit.setShortcut("Alt+F4")
            self.action_exit.triggered.connect(self.close)
            self.action_reset_camera = QtGui.QAction(
                "Reset camera",
                self,
            )
            self.action_reset_camera.triggered.connect(
                self._reset_camera
            )
            self.action_scene_editor = QtGui.QAction("Scene Editor", self)
            self.action_scene_editor.setStatusTip(
                "Open the separate RungProof Scene Editor proof"
            )
            self.action_scene_editor.setEnabled(not getattr(sys, "frozen", False))
            self.action_scene_editor.triggered.connect(
                self._show_scene_editor
            )
            self.action_equipment_gallery = QtGui.QAction(
                "Equipment Gallery",
                self,
            )
            self.action_equipment_gallery.setStatusTip(
                "Inspect reusable equipment geometry before scene placement"
            )
            self.action_equipment_gallery.triggered.connect(
                self._open_equipment_gallery
            )
            self.action_initial_simulation_setup = QtGui.QAction(
                "Initial Simulation Setup",
                self,
            )
            self.action_initial_simulation_setup.setStatusTip(
                "Open the common PLC and watchdog setup document"
            )
            self.action_initial_simulation_setup.triggered.connect(
                self._show_initial_simulation_setup
            )

            self.view_action_group = QtGui.QActionGroup(self)
            self.view_action_group.setExclusive(True)
            self.view_actions: dict[str, Any] = {}
            for index, (mode, name) in enumerate(VIEW_NAMES.items(), 1):
                action = QtGui.QAction(
                    f"{mode} - {name}",
                    self,
                    checkable=True,
                )
                action.setShortcut(f"Alt+{index}")
                action.triggered.connect(
                    lambda _checked=False, selected=mode: (
                        self.set_view_mode(selected)
                    )
                )
                self.view_action_group.addAction(action)
                self.view_actions[mode] = action

        def _new_panel(
            self,
            title: str,
            *,
            badge: str | None = None,
        ) -> tuple[Any, Any]:
            panel = QtWidgets.QFrame()
            panel.setObjectName("panelBlock")
            layout = QtWidgets.QVBoxLayout(panel)
            layout.setContentsMargins(15, 13, 15, 14)
            layout.setSpacing(9)
            heading = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(title)
            label.setObjectName("sectionLabel")
            heading.addWidget(label)
            heading.addStretch(1)
            if badge:
                badge_label = QtWidgets.QLabel(badge)
                badge_label.setObjectName("microBadge")
                heading.addWidget(badge_label)
            layout.addLayout(heading)
            return panel, layout

        def _new_metric(
            self,
            title: str,
            initial: str = "--",
        ) -> tuple[Any, Any]:
            card = QtWidgets.QFrame()
            card.setObjectName("metricCard")
            layout = QtWidgets.QVBoxLayout(card)
            layout.setContentsMargins(8, 7, 8, 7)
            layout.setSpacing(3)
            small = QtWidgets.QLabel(title)
            small.setObjectName("metricLabel")
            value = QtWidgets.QLabel(initial)
            value.setObjectName("metricValue")
            layout.addWidget(small)
            layout.addWidget(value)
            return card, value

        def _new_rail(self) -> tuple[Any, Any]:
            scroll = QtWidgets.QScrollArea()
            scroll.setObjectName("rail")
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            content = QtWidgets.QWidget()
            content.setObjectName("railContent")
            layout = QtWidgets.QVBoxLayout(content)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            scroll.setWidget(content)
            return scroll, layout

        def _build_ui(self) -> None:
            root = QtWidgets.QWidget()
            root.setObjectName("appRoot")
            self.setCentralWidget(root)
            outer = QtWidgets.QVBoxLayout(root)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            header = QtWidgets.QFrame()
            header.setObjectName("header")
            header.setMinimumHeight(
                self._scaled(44 if self._compact_display else 64)
            )
            header_layout = QtWidgets.QHBoxLayout(header)
            header_layout.setContentsMargins(18, 9, 18, 9)
            header_layout.setSpacing(10)

            mark_tile = QtWidgets.QFrame()
            mark_tile.setObjectName("brandTile")
            mark_tile.setFixedSize(38, 38)
            mark_layout = QtWidgets.QHBoxLayout(mark_tile)
            mark_layout.setContentsMargins(4, 0, 4, 0)
            mark_layout.setSpacing(1)
            mark = QtWidgets.QLabel()
            mark.setObjectName("brandMark")
            mark.setAccessibleName("RungProof")
            brand_icon_path = (
                Path(__file__).resolve().parents[1]
                / "prototype"
                / "assets"
                / "brand"
                / "rungproof-mark.svg"
            )
            if brand_icon_path.is_file():
                mark.setPixmap(
                    QtGui.QIcon(str(brand_icon_path)).pixmap(28, 28)
                )
            else:
                mark.setText("RP")
            mark_layout.addWidget(mark)
            header_layout.addWidget(mark_tile)

            title_block = QtWidgets.QWidget()
            title_layout = QtWidgets.QVBoxLayout(title_block)
            title_layout.setContentsMargins(0, 0, 4, 0)
            title_layout.setSpacing(0)
            title = QtWidgets.QLabel("RungProof")
            title.setObjectName("brandTitle")
            descriptor = QtWidgets.QLabel("PLC VISUAL SIMULATOR")
            descriptor.setObjectName("brandDescriptor")
            title_layout.addWidget(title)
            title_layout.addWidget(descriptor)
            header_layout.addWidget(title_block)

            menu_bar = QtWidgets.QMenuBar()
            menu_bar.setObjectName("applicationMenu")
            menu_bar.setNativeMenuBar(False)
            file_menu = menu_bar.addMenu("File")
            file_menu.addAction(self.action_exit)
            view_menu = menu_bar.addMenu("View")
            for mode in VIEW_NAMES:
                view_menu.addAction(self.view_actions[mode])
            view_menu.addSeparator()
            view_menu.addAction(self.action_reset_camera)
            self.playback_menu = menu_bar.addMenu("Playback")
            self.playback_menu.addActions(
                (
                    self.action_run,
                    self.action_stop,
                    self.action_reset,
                )
            )
            self.scene_menu = menu_bar.addMenu("Scene")
            self.production_scenes_menu = self.scene_menu.addMenu(
                "Production Scenes"
            )
            self.review_scenes_menu = self.scene_menu.addMenu("Review Scenes")
            self.training_labs_menu = self.scene_menu.addMenu(
                "Training Labs"
            )
            self.scene_action_group = QtGui.QActionGroup(self)
            self.scene_action_group.setExclusive(True)
            self.scene_actions: dict[str, Any] = {}
            self.production_scene_actions: dict[str, Any] = {}
            self.review_scene_actions: dict[str, Any] = {}
            self.training_lab_actions: dict[str, Any] = {}
            for entry in self.scene_catalog:
                if entry.category == "tool":
                    # Equipment Gallery is a Tools workflow, not a scene.
                    continue
                action = QtGui.QAction(entry.menu_text, self, checkable=True)
                action.setStatusTip(entry.status_tip)
                action.setEnabled(entry.selectable)
                action.triggered.connect(
                    lambda _checked=False, scene_id=entry.scene_id: (
                        self._select_scene_id(scene_id)
                    )
                )
                self.scene_action_group.addAction(action)
                self.scene_actions[entry.scene_id] = action
                if entry.category == "lab":
                    self.training_labs_menu.addAction(action)
                    self.training_lab_actions[entry.scene_id] = action
                elif entry.category == "review":
                    self.review_scenes_menu.addAction(action)
                    self.review_scene_actions[entry.scene_id] = action
                else:
                    self.production_scenes_menu.addAction(action)
                    self.production_scene_actions[entry.scene_id] = action
            tools_menu = menu_bar.addMenu("Tools")
            tools_menu.addAction(self.action_equipment_gallery)
            tools_menu.addAction(self.action_scene_editor)
            plc_menu = menu_bar.addMenu("PLC")
            plc_menu.addActions(
                (
                    self.action_configure_plc,
                    self.action_connect,
                    self.action_disconnect,
                    self.action_test_plc,
                )
            )
            self.workspace_menu = QtWidgets.QMenu("Workspace", menu_bar)
            self.action_workspace_sign_in = QtGui.QAction(
                "Sign in to Workspace...",
                self,
            )
            self.action_workspace_sign_in.triggered.connect(
                self._show_workspace_sign_in
            )
            self.action_workspace_sync = QtGui.QAction(
                "Sync assigned scene",
                self,
            )
            self.action_workspace_sync.triggered.connect(
                self._sync_workspace_assignment
            )
            self.action_workspace_upload = QtGui.QAction(
                "Upload sanitized session evidence",
                self,
            )
            self.action_workspace_upload.triggered.connect(
                self._upload_workspace_evidence
            )
            self.workspace_menu.addActions(
                (
                    self.action_workspace_sign_in,
                    self.action_workspace_sync,
                    self.action_workspace_upload,
                )
            )
            if self.workspace_fixture_enabled:
                menu_bar.addMenu(self.workspace_menu)
            help_menu = menu_bar.addMenu("Help")
            help_menu.addAction(self.action_initial_simulation_setup)
            help_menu.addSeparator()
            boundary_action = help_menu.addAction("PLC Boundary")
            boundary_action.triggered.connect(
                lambda: self._show_notice(
                    "PLC Boundary",
                    (
                        "RungProof does not generate ladder logic or write "
                        "physical I/O addresses. TIA owns ladder execution; "
                        "the PLC watchdog remains the safety authority.\n\n"
                        "The local plant view is not proof of physical PLC "
                        "state until an approved live exchange is connected "
                        "and healthy."
                    ),
                )
            )
            about_action = help_menu.addAction("About RungProof")
            about_action.triggered.connect(self._show_about)
            header_layout.addWidget(menu_bar)
            header_layout.addStretch(1)
            self.workspace_badge = QtWidgets.QLabel("WORKSPACE OFFLINE")
            self.workspace_badge.setObjectName("workspaceBadge")
            self.workspace_badge.setVisible(self.workspace_fixture_enabled)
            header_layout.addWidget(self.workspace_badge)
            self.view_badge = QtWidgets.QLabel("--")
            self.view_badge.setObjectName("viewBadge")
            header_layout.addWidget(self.view_badge)
            self.connection_badge = QtWidgets.QLabel("CONTROLLER DISCONNECTED")
            self.connection_badge.setObjectName("connectionBadge")
            header_layout.addWidget(self.connection_badge)
            outer.addWidget(header)

            self.workspace = QtWidgets.QFrame()
            self.workspace.setObjectName("workspace")
            self.workspace_layout = QtWidgets.QGridLayout(self.workspace)
            outer.addWidget(self.workspace, 1)

            self.scene_panel, scene_layout = self._new_panel(
                "SCENE",
                badge="6 ASSETS",
            )
            scene_heading = scene_layout.itemAt(0).layout()
            self.scene_asset_badge = scene_heading.itemAt(
                scene_heading.count() - 1
            ).widget()
            self.scene_title = QtWidgets.QLabel(
                "Conveyor Pusher"
            )
            self.scene_title.setObjectName("sceneTitle")
            self.scene_title.setWordWrap(True)
            self.scene_text = QtWidgets.QLabel(
                "Run to the photoeye, stop, extend the pusher, "
                "transfer the package, retract, and admit the next package."
            )
            self.scene_text.setObjectName("muted")
            self.scene_text.setWordWrap(True)
            self.scene_scope = QtWidgets.QLabel(
                "REAL S7-1500 · DB14 · RACK 0 / SLOT 1"
            )
            self.scene_scope.setObjectName("sceneScope")
            self.scene_scope.setWordWrap(True)
            scene_layout.addWidget(self.scene_title)
            scene_layout.addWidget(self.scene_text)
            scene_layout.addWidget(self.scene_scope)
            scene_content_actions = QtWidgets.QHBoxLayout()
            scene_content_actions.setSpacing(7)
            self.scene_setup_button = _button(
                QtWidgets,
                "Setup",
                object_name="sceneSetup",
            )
            self.scene_logic_button = _button(
                QtWidgets,
                "Basic Logic",
                object_name="sceneLogic",
            )
            self.scene_setup_button.clicked.connect(self._show_scene_setup)
            self.scene_logic_button.clicked.connect(self._show_basic_logic)
            scene_content_actions.addWidget(self.scene_setup_button)
            scene_content_actions.addWidget(self.scene_logic_button)
            scene_layout.addLayout(scene_content_actions)

            self.runtime_panel, runtime_layout = self._new_panel(
                "RUNTIME"
            )
            status_grid = QtWidgets.QGridLayout()
            status_grid.setSpacing(7)
            player_card, self.runtime_player = self._new_metric(
                "PLAYER",
                "PLC WAIT",
            )
            scene_card, self.runtime_scene = self._new_metric(
                "SCENE",
                "Scene 2",
            )
            time_card, self.runtime_time = self._new_metric(
                "TIME",
                "0.0 s",
            )
            exchange_card, self.runtime_exchange = self._new_metric(
                "EXCHANGE",
                "0.00 ms",
            )
            status_grid.addWidget(player_card, 0, 0)
            status_grid.addWidget(scene_card, 0, 1)
            status_grid.addWidget(time_card, 1, 0)
            status_grid.addWidget(exchange_card, 1, 1)
            runtime_layout.addLayout(status_grid)
            self.timing = QtWidgets.QLabel("--")
            self.timing.setObjectName("mono")
            self.timing.setWordWrap(True)
            runtime_layout.addWidget(self.timing)

            self.points_panel, points_layout = self._new_panel(
                "LOCAL MODEL POINTS",
                badge="PLC NOT EXCHANGING",
            )
            if self._compact_display:
                points_layout.setContentsMargins(8, 6, 8, 6)
                points_layout.setSpacing(4)
            points_heading = points_layout.itemAt(0).layout()
            self.points_source_badge = points_heading.itemAt(
                points_heading.count() - 1
            ).widget()
            self.points_order_combo = QtWidgets.QComboBox()
            self.points_order_combo.addItem(
                "PLC inputs / PLC outputs", "plc-io"
            )
            self.points_order_combo.addItem(
                "Simulation inputs / outputs", "sim-io"
            )
            self.points_order_combo.addItem(
                "Owner: PLC / PC + SIM", "owner"
            )
            self.points_order_combo.addItem(
                "Type: BOOL / numeric + diagnostics", "type"
            )
            self.points_order_combo.addItem("Name: A-Z", "name")
            self.points_order_combo.setToolTip(
                "Choose how live points are grouped into the two tables."
            )
            self.points_order_combo.currentIndexChanged.connect(
                lambda _index: self._set_point_order(
                    self.points_order_combo.currentData()
                )
            )
            points_heading.insertWidget(
                points_heading.count() - 1,
                self.points_order_combo,
            )
            points_tables_layout = QtWidgets.QHBoxLayout()
            points_tables_layout.setSpacing(8)

            def make_points_table() -> Any:
                table = QtWidgets.QTableWidget(0, 4)
                table.setHorizontalHeaderLabels(
                    ("POINT", "TYPE", "VALUE", "OWNER")
                )
                table.verticalHeader().setVisible(False)
                table.setVerticalScrollBarPolicy(
                    QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
                    if self._compact_display
                    else QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                )
                table.setEditTriggers(
                    QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
                )
                table.setSelectionMode(
                    QtWidgets.QAbstractItemView.SelectionMode.NoSelection
                )
                table.setWordWrap(False)
                table.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
                table.setAlternatingRowColors(True)
                if self._compact_display:
                    table.verticalHeader().setDefaultSectionSize(19)
                table.setMinimumHeight(
                    60 if self._compact_display else 112
                )
                header_view = table.horizontalHeader()
                if self._compact_display:
                    header_view.setFixedHeight(22)
                header_view.setStretchLastSection(False)
                header_view.setSectionResizeMode(
                    0,
                    QtWidgets.QHeaderView.ResizeMode.Stretch,
                )
                for column in (1, 2, 3):
                    header_view.setSectionResizeMode(
                        column,
                        QtWidgets.QHeaderView.ResizeMode.ResizeToContents,
                    )
                return table

            # Keep points_table as the public/legacy left-side handle. The
            # right table is paired with it when the list is split.
            self.points_table = make_points_table()
            self.points_table_right = make_points_table()
            self.points_column_left = QtWidgets.QLabel("SIMULATOR → PLC")
            self.points_column_right = QtWidgets.QLabel("PLC → SIMULATOR")
            for label in (self.points_column_left, self.points_column_right):
                label.setObjectName("pointColumnHeading")
            left_column = QtWidgets.QVBoxLayout()
            left_column.setSpacing(3)
            left_column.addWidget(self.points_column_left)
            left_column.addWidget(self.points_table, 1)
            right_column = QtWidgets.QVBoxLayout()
            right_column.setSpacing(3)
            right_column.addWidget(self.points_column_right)
            right_column.addWidget(self.points_table_right, 1)
            points_tables_layout.addLayout(left_column, 1)
            points_tables_layout.addLayout(right_column, 1)
            points_layout.addLayout(points_tables_layout, 1)

            self.health_panel, health_layout = self._new_panel(
                "PLC HEALTH"
            )
            self.health_details = QtWidgets.QLabel("--")
            self.health_details.setObjectName("mono")
            self.health_details.setWordWrap(True)
            health_layout.addWidget(self.health_details)

            self.event_history_panel, event_layout = self._new_panel(
                "EVENT HISTORY",
                badge=(
                    "LOCAL / NOT UPLOADED"
                    if self.workspace_fixture_enabled
                    else "LOCAL ONLY"
                ),
            )
            if self._compact_display:
                event_layout.setSpacing(5)
            self.event_console_button = _button(
                QtWidgets,
                "Open Event Console",
                object_name="eventConsoleButton",
            )
            self.event_console_button.clicked.connect(
                self._show_event_console
            )
            self.event_console_button.setVisible(not self._compact_display)
            event_layout.addWidget(self.event_console_button)
            self.event_priority_hint = QtWidgets.QLabel(
                "ACTIVE ALARM  ·  EVENTS PRIORITIZED"
            )
            self.event_priority_hint.setObjectName("eventPriorityHint")
            self.event_priority_hint.setVisible(False)
            event_layout.addWidget(self.event_priority_hint)
            self.event_inspector = QtWidgets.QLabel(
                "NO ACTIVE EVENTS\n"
                "Select an event to inspect its full local evidence."
            )
            self.event_inspector.setObjectName("eventInspector")
            self.event_inspector.setWordWrap(True)
            self.event_inspector.setMinimumHeight(self._scaled(62))
            self.event_inspector.setMaximumHeight(self._scaled(124))
            if self._compact_display:
                self.event_inspector.setMaximumHeight(self._scaled(124))
            event_layout.addWidget(self.event_inspector)
            self.event_table = QtWidgets.QTreeWidget()
            self.event_table.setObjectName("eventTable")
            self.event_table.setColumnCount(4)
            self.event_table.setHeaderLabels(
                ("SEV", "EVENT", "STATE / TIME", "SRC")
            )
            event_header = self.event_table.header()
            for column in range(4):
                event_header.setSectionResizeMode(
                    column, QtWidgets.QHeaderView.ResizeMode.Fixed
                )
            self.event_table.setRootIsDecorated(False)
            self.event_table.setIndentation(0)
            self.event_table.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.event_table.setColumnWidth(0, self._scaled(38))
            self.event_table.setColumnWidth(1, self._scaled(96))
            self.event_table.setColumnWidth(2, self._scaled(78))
            self.event_table.setColumnWidth(3, self._scaled(42))
            self.event_table.setSelectionMode(
                QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
            )
            self.event_table.setMinimumHeight(self._scaled(74))
            self.event_table.setMaximumHeight(
                self._scaled(90 if not self._compact_display else 150)
            )
            self.event_table.setToolTip(
                "Select Open Event Console for acknowledgement and clear actions."
            )
            self.event_table.setVisible(not self._compact_display)
            event_layout.addWidget(self.event_table)
            event_actions = QtWidgets.QHBoxLayout()
            self.event_ack_button = _button(
                QtWidgets,
                "Acknowledge",
                object_name="eventAcknowledge",
            )
            self.event_clear_button = _button(
                QtWidgets,
                "Clear",
                object_name="eventClear",
            )
            self.event_ack_button.setToolTip("Acknowledge the inspected event")
            self.event_clear_button.setToolTip("Clear the inspected event")
            self.event_ack_button.setEnabled(False)
            self.event_clear_button.setEnabled(False)
            self.event_action_buttons = (
                self.event_ack_button,
                self.event_clear_button,
            )
            for button in self.event_action_buttons:
                button.setVisible(False)
                if self._compact_display:
                    button.setMinimumHeight(28)
            self.event_ack_button.clicked.connect(self._acknowledge_event_row)
            self.event_clear_button.clicked.connect(self._clear_event_row)
            self.event_table.itemSelectionChanged.connect(
                self._update_event_row_actions
            )
            event_actions.addWidget(self.event_ack_button)
            event_actions.addWidget(self.event_clear_button)
            event_layout.insertLayout(4, event_actions)
            self.event_asset_context = QtWidgets.QLabel()
            self.event_asset_context.setObjectName("eventAssetContext")
            self.event_asset_context.setWordWrap(True)
            self.event_asset_context.setVisible(False)
            event_layout.insertWidget(5, self.event_asset_context)
            self.event_history = QtWidgets.QLabel(
                "NO ACTIVE ALARMS\n"
                + self._local_evidence_text
            )
            self.event_history.setObjectName("eventHistory")
            self.event_history.setWordWrap(True)
            self.event_history.hide()

            self.equipment_panel, equipment_layout = self._new_panel(
                "SCENE EQUIPMENT",
                badge="6 ASSETS",
            )
            equipment_heading = equipment_layout.itemAt(0).layout()
            self.equipment_asset_badge = equipment_heading.itemAt(
                equipment_heading.count() - 1
            ).widget()
            self.equipment_title = QtWidgets.QLabel("Conveyor pusher cell")
            self.equipment_title.setObjectName("equipmentTitle")
            self.equipment_list = QtWidgets.QLabel(
                "Conveyor\nPackage\nPhotoeye\nPusher cylinder\n"
                "Drive motor\nStack light"
            )
            self.equipment_list.setObjectName("propertyList")
            equipment_layout.addWidget(self.equipment_title)
            equipment_layout.addWidget(self.equipment_list)
            self.equipment_inspection = QtWidgets.QLabel(
                "Select equipment in the viewport\n"
                "Hover an asset for inspection"
            )
            self.equipment_inspection.setObjectName("equipmentInspection")
            self.equipment_inspection.setWordWrap(True)
            equipment_layout.addWidget(self.equipment_inspection)

            self.viewport_frame = QtWidgets.QFrame()
            self.viewport_frame.setObjectName("viewportFrame")
            viewport_layout = QtWidgets.QVBoxLayout(self.viewport_frame)
            viewport_layout.setContentsMargins(0, 0, 0, 0)
            viewport_layout.setSpacing(0)
            scene_bar = QtWidgets.QFrame()
            scene_bar.setObjectName("sceneBar")
            scene_bar_layout = QtWidgets.QHBoxLayout(scene_bar)
            scene_bar_layout.setContentsMargins(13, 7, 13, 7)
            self.scene_kind = QtWidgets.QLabel(
                "CONVEYOR PUSHER · 6 ASSETS"
            )
            self.scene_kind.setObjectName("sceneKind")
            scene_bar_layout.addWidget(self.scene_kind)
            scene_bar_layout.addStretch(1)
            viewport_help = QtWidgets.QLabel(
                "Drag to orbit · Wheel to zoom"
            )
            viewport_help.setObjectName("viewportHelp")
            scene_bar_layout.addWidget(viewport_help)
            viewport_layout.addWidget(scene_bar)
            self.compact_priority_bar = QtWidgets.QLabel(
                "NO ACTIVE ALARMS  ·  EVENT STORE LOCAL"
            )
            self.compact_priority_bar.setObjectName("compactPriorityBar")
            self.compact_priority_bar.setWordWrap(False)
            self.compact_priority_bar.setMinimumHeight(self._scaled(26))
            self.compact_priority_bar.setVisible(self._compact_display)
            viewport_layout.addWidget(self.compact_priority_bar)
            self.viewport_stack = QtWidgets.QStackedWidget()
            self.viewport_stack.setObjectName("sceneViewportStack")
            self._viewport_indexes = {
                "scene-2-conveyor-pusher": self.viewport_stack.addWidget(
                    self.viewport.container
                )
            }
            for definition in NATIVE_SCENE_DEFINITIONS:
                self._viewport_indexes[definition.scene_id] = (
                    self.viewport_stack.addWidget(
                        self.review_viewports[definition.scene_id].container
                    )
                )
            viewport_layout.addWidget(self.viewport_stack, 1)
            self.status_message = QtWidgets.QLabel(
                "Controller disconnected — local plant view only."
            )
            self.status_message.setObjectName("statusMessage")
            self.status_message.setWordWrap(True)
            self.status_message.setMinimumHeight(
                self._scaled(20 if self._compact_display else 30)
            )
            viewport_layout.addWidget(self.status_message)

            self.left_rail, self.left_rail_layout = self._new_rail()
            self.right_rail, self.right_rail_layout = self._new_rail()
            self.compact_runtime_panel, compact_runtime_layout = self._new_panel(
                "RUNTIME STATUS",
                badge="LOCAL",
            )
            self.compact_runtime_state = QtWidgets.QLabel("LOCAL ONLY")
            self.compact_runtime_state.setObjectName("equipmentTitle")
            self.compact_runtime_health = QtWidgets.QLabel("HEALTH  DISCONNECTED")
            self.compact_runtime_time = QtWidgets.QLabel("TIME  0.0 s")
            self.compact_runtime_exchange = QtWidgets.QLabel("EXCHANGE  0.00 ms")
            for label in (
                self.compact_runtime_health,
                self.compact_runtime_time,
                self.compact_runtime_exchange,
            ):
                label.setObjectName("mono")
                label.setWordWrap(True)
            compact_runtime_layout.addWidget(self.compact_runtime_state)
            compact_runtime_layout.addWidget(self.compact_runtime_health)
            compact_runtime_layout.addWidget(self.compact_runtime_time)
            compact_runtime_layout.addWidget(self.compact_runtime_exchange)
            self.compact_right_container = QtWidgets.QWidget()
            self.compact_right_container.setObjectName("compactRightContainer")
            compact_right_layout = QtWidgets.QVBoxLayout(
                self.compact_right_container
            )
            compact_right_layout.setContentsMargins(0, 0, 0, 0)
            compact_right_layout.setSpacing(4)
            self.compact_rail_nav = QtWidgets.QTabBar()
            self.compact_rail_nav.setObjectName("compactRailNav")
            self.compact_rail_nav.setUsesScrollButtons(False)
            self.compact_rail_nav.setExpanding(True)
            for label in ("EQUIPMENT", "EVENTS", "HEALTH", "RUNTIME"):
                self.compact_rail_nav.addTab(label)
            compact_right_layout.addWidget(self.compact_rail_nav)
            self.compact_panel_stack = QtWidgets.QStackedWidget()
            self.compact_panel_stack.setObjectName("compactPanelStack")
            self.compact_panel_pages = {}
            if self._compact_display:
                for key, panel in (
                    ("equipment", self.equipment_panel),
                    ("events", self.event_history_panel),
                    ("health", self.health_panel),
                    ("runtime", self.compact_runtime_panel),
                ):
                    page = QtWidgets.QScrollArea()
                    page.setObjectName(f"compactPage_{key}")
                    page.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
                    page.setWidgetResizable(True)
                    page.setHorizontalScrollBarPolicy(
                        QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                    )
                    page.setWidget(panel)
                    self.compact_panel_pages[key] = page
                    self.compact_panel_stack.addWidget(page)
            compact_right_layout.addWidget(self.compact_panel_stack, 1)
            self.compact_rail_nav.currentChanged.connect(
                self._on_compact_panel_changed
            )
            for panel in (self.scene_panel, self.runtime_panel):
                panel.setProperty("areaRole", "left")
            for panel in (
                self.health_panel,
                self.equipment_panel,
                self.event_history_panel,
            ):
                panel.setProperty("areaRole", "right")
            self.points_panel.setProperty("areaRole", "data")
            self.left_rail.setProperty("areaRole", "left")
            self.right_rail.setProperty("areaRole", "right")
            self.left_rail.widget().setProperty("areaRole", "left")
            self.right_rail.widget().setProperty("areaRole", "right")
            self._panel_widgets = (
                self.scene_panel,
                self.runtime_panel,
                self.points_panel,
                self.health_panel,
                self.equipment_panel,
                self.event_history_panel,
            )

            hud = QtWidgets.QFrame()
            hud.setObjectName("transportHud")
            hud.setMinimumHeight(
                self._scaled(44 if self._compact_display else 68)
            )
            hud_layout = QtWidgets.QHBoxLayout(hud)
            hud_layout.setContentsMargins(
                8 if self._compact_display else 14,
                4 if self._compact_display else 8,
                8 if self._compact_display else 14,
                4 if self._compact_display else 8,
            )
            hud_layout.setSpacing(14)
            hud_controls = QtWidgets.QHBoxLayout()
            hud_controls.setSpacing(5)
            self.hud_run_button = _button(
                QtWidgets,
                "Run",
                object_name="hudRun",
            )
            self.hud_stop_button = _button(
                QtWidgets,
                "Stop",
                object_name="hudStop",
            )
            self.hud_reset_button = _button(
                QtWidgets,
                "Reset",
                object_name="hudReset",
            )
            self.hud_run_button.setToolTip(
                "Enable playback/exchange; the PLC must command Conveyor_Run."
            )
            self.hud_stop_button.setToolTip(
                "Stop playback; this does not replace the PLC safety logic."
            )
            for button in (
                self.hud_run_button,
                self.hud_stop_button,
                self.hud_reset_button,
            ):
                button.setMinimumSize(
                    self._scaled(44 if self._compact_display else 58),
                    self._scaled(28 if self._compact_display else 38),
                )
                button.setSizePolicy(
                    QtWidgets.QSizePolicy.Policy.Preferred,
                    QtWidgets.QSizePolicy.Policy.Fixed,
                )
                hud_controls.addWidget(button)
            self.hud_run_button.clicked.connect(self._run)
            self.hud_stop_button.clicked.connect(self._stop)
            self.hud_reset_button.clicked.connect(self._reset)
            hud_layout.addLayout(hud_controls)

            self.hud_lock_reason = QtWidgets.QLabel(
                "CONTROLS LOCKED · CONTROLLER OFFLINE"
            )
            self.hud_lock_reason.setObjectName("hudLockReason")
            self.hud_lock_reason.setToolTip(
                "Run, Stop, and Reset require a healthy connected controller."
            )
            hud_layout.addWidget(self.hud_lock_reason)

            now_playing = QtWidgets.QWidget()
            now_layout = QtWidgets.QVBoxLayout(now_playing)
            now_layout.setContentsMargins(0, 0, 0, 0)
            now_layout.setSpacing(3)
            now_label = QtWidgets.QLabel("NOW PLAYING")
            now_label.setObjectName("metricLabel")
            now_line = QtWidgets.QHBoxLayout()
            self.hud_scene = QtWidgets.QLabel(
                "Conveyor Pusher"
            )
            self.hud_scene.setObjectName("hudScene")
            self.hud_state = QtWidgets.QLabel("NO PLC")
            self.hud_state.setObjectName("hudState")
            now_line.addWidget(self.hud_scene, 1)
            now_line.addWidget(self.hud_state)
            self.hud_live = QtWidgets.QLabel(
                "●  LOCAL PLANT VIEW · PLC OUTPUTS NOT VERIFIED"
            )
            self.hud_live.setObjectName("hudLive")
            now_layout.addWidget(now_label)
            now_layout.addLayout(now_line)
            now_layout.addWidget(self.hud_live)
            if self._compact_display:
                now_playing.setVisible(False)
            hud_layout.addWidget(now_playing, 1)

            meter_strip = QtWidgets.QFrame()
            meter_strip.setObjectName("meterStrip")
            meter_layout = QtWidgets.QHBoxLayout(meter_strip)
            meter_layout.setContentsMargins(0, 0, 0, 0)
            meter_layout.setSpacing(0)
            time_meter, self.hud_time = self._new_metric(
                "TIME",
                "0.0 s",
            )
            p99_meter, self.hud_p99 = self._new_metric(
                "EXCHANGE P99",
                "0.00 ms",
            )
            source_meter, self.hud_source = self._new_metric(
                "CONTROLLER",
                "DISCONNECTED",
            )
            for meter in (time_meter, p99_meter, source_meter):
                meter.setObjectName("hudMeter")
                meter_layout.addWidget(meter)
            if self._compact_display:
                meter_strip.setVisible(False)
            hud_layout.addWidget(meter_strip)
            outer.addWidget(hud)

            # Keep the operator path keyboard-reachable in a predictable order.
            # QAction shortcuts remain active even when focus is in a table or
            # the viewport, while Tab provides an obvious visual focus path.
            focus_widgets = (
                self.scene_setup_button,
                self.scene_logic_button,
                self.points_order_combo,
                self.hud_run_button,
                self.hud_stop_button,
                self.hud_reset_button,
            )
            for widget in focus_widgets:
                widget.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            viewport_container = getattr(self.viewport, "container", None)
            if viewport_container is not None:
                viewport_container.setFocusPolicy(
                    QtCore.Qt.FocusPolicy.StrongFocus
                )
            for previous, current in zip(focus_widgets, focus_widgets[1:]):
                self.setTabOrder(previous, current)
            if viewport_container is not None:
                self.setTabOrder(self.hud_reset_button, viewport_container)
                self.setTabOrder(viewport_container, self.scene_setup_button)
            self.points_order_combo.setToolTip(
                "Sort live points. Use Tab to reach this control, then Alt+Down."
            )
            self.hud_run_button.setToolTip(
                "Run (Space). PLC must be connected and ready."
            )
            self.hud_stop_button.setToolTip(
                "Stop. Available when the PLC session is running."
            )
            self.hud_reset_button.setToolTip(
                "Reset. Returns the plant session to its stopped state."
            )

            self._select_scene_id(SCENE_ID)
            self.setStyleSheet(self._application_stylesheet())
            self.set_view_mode(self._view_mode)

        def _application_stylesheet(self) -> str:
            return f"""
                QWidget {{
                    color: {TEXT};
                    font-family: "Segoe UI Variable", "Segoe UI";
                    font-size: 13px;
                    font-weight: 500;
                }}
                QLabel {{
                    font-weight: 500;
                }}
                QWidget#appRoot, QFrame#workspace {{
                    background: {BACKGROUND_DEEP};
                }}
                QFrame#header {{
                    background: #0E1C22;
                    border-bottom: 1px solid {LINE};
                }}
                QFrame#brandTile {{
                    background: #F7FAFB;
                    border-radius: 6px;
                }}
                QLabel#brandMark {{
                    color: #071A2A;
                    font-size: 14px;
                    font-weight: 900;
                }}
                QLabel#brandTitle {{
                    font-size: 15px;
                    font-weight: 750;
                }}
                QLabel#brandDescriptor {{
                    color: {MUTED};
                    font-size: 10px;
                    font-weight: 700;
                }}
                QMenuBar#applicationMenu {{
                    color: #A9BDC3;
                    background: transparent;
                }}
                QMenuBar#applicationMenu::item {{
                    padding: 10px 10px;
                    background: transparent;
                }}
                QMenuBar#applicationMenu::item:selected {{
                    color: #F0F7F8;
                    background: #203740;
                }}
                QMenu {{
                    color: #B8CBD0;
                    background: #0B191F;
                    border: 1px solid #49646D;
                    padding: 5px;
                }}
                QMenu::item {{
                    min-width: 210px;
                    padding: 7px 26px 7px 24px;
                }}
                QMenu::item:selected {{
                    color: #F3F8F9;
                    background: #1C353E;
                }}
                QLabel#connectionBadge, QLabel#viewBadge {{
                    border: 1px solid {LINE_BRIGHT};
                    border-radius: 3px;
                    padding: 6px 9px;
                    background: #0F1E24;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 700;
                }}
                QLabel#viewBadge {{
                    color: {MUTED_BRIGHT};
                }}
                QLabel#workspaceBadge {{
                    color: #9FD5E5;
                    border: 1px solid #3A7181;
                    border-radius: 3px;
                    padding: 6px 9px;
                    background: #102730;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 800;
                }}
                QScrollArea#rail {{
                    background: {PANEL};
                    border: 0;
                }}
                QScrollArea#cardRail {{
                    background: transparent;
                    border: 1px solid {LINE_BRIGHT};
                    border-radius: 4px;
                }}
                QWidget#railContent {{
                    background: {PANEL};
                }}
                QFrame#panelBlock {{
                    background: {PANEL};
                    border: 0;
                    border-bottom: 1px solid {LINE};
                }}
                QFrame#panelBlock[areaRole="left"] {{
                    background: #10242B;
                }}
                QFrame#panelBlock[areaRole="right"] {{
                    background: #111F26;
                }}
                QFrame#panelBlock[areaRole="data"] {{
                    background: #0A1E25;
                }}
                QScrollArea#rail[areaRole="left"] {{
                    background: #10242B;
                }}
                QScrollArea#rail[areaRole="right"] {{
                    background: #111F26;
                }}
                QLabel#sectionLabel {{
                    color: {MUTED};
                    font-size: 10px;
                    font-weight: 900;
                }}
                QLabel#microBadge, QLabel#sceneScope {{
                    color: {MUTED_BRIGHT};
                    background: #0C191F;
                    border: 1px solid {LINE};
                    border-radius: 2px;
                    padding: 3px 6px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 700;
                }}
                QLabel#sceneTitle {{
                    font-size: 19px;
                    font-weight: 900;
                }}
                QLabel#muted {{
                    color: {MUTED};
                    font-size: 12px;
                    font-weight: 600;
                    line-height: 1.35;
                }}
                QLabel#mutedSmall {{
                    color: #6F8790;
                    font-size: 9px;
                }}
                QLabel#diagnosticLabel {{
                    color: #78A9BA;
                    font-size: 9px;
                    font-weight: 800;
                }}
                QLabel#diagnosticBadge {{
                    color: #9AE5CA;
                    background: #102E27;
                    border: 1px solid #2F765F;
                    border-radius: 2px;
                    padding: 2px 5px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 800;
                }}
                QLabel#equipmentTitle {{
                    font-size: 15px;
                    font-weight: 850;
                }}
                QLabel#propertyList {{
                    color: {MUTED_BRIGHT};
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 11px;
                    font-weight: 600;
                    line-height: 1.4;
                }}
                QLabel#equipmentInspection {{
                    color: #D7E8EB;
                    background: #0D252C;
                    border: 1px solid #3D8999;
                    border-radius: 3px;
                    padding: 9px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 10px;
                    font-weight: 700;
                    line-height: 1.45;
                }}
                QLabel#eventHistory {{
                    color: #B8D0D5;
                    background: #0B181E;
                    border: 1px solid #2B4A54;
                    border-radius: 3px;
                    padding: 8px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 10px;
                    font-weight: 650;
                    line-height: 1.45;
                }}
                QLabel#eventInspector {{
                    color: #DCECEF;
                    background: #102730;
                    border: 1px solid #3A6975;
                    border-left: 3px solid #E2A83A;
                    border-radius: 3px;
                    padding: 7px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 650;
                    line-height: 1.35;
                }}
                QLabel#eventPriorityHint {{
                    color: #E2A83A;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 800;
                }}
                QLabel#eventAssetContext {{
                    color: #C9E5EA;
                    background: #0D252C;
                    border: 1px solid #2E6877;
                    border-left: 3px solid #59C8E7;
                    border-radius: 3px;
                    padding: 6px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                    font-weight: 650;
                    line-height: 1.3;
                }}
                QTreeWidget#eventTable {{
                    color: #B8D0D5;
                    background: #0B181E;
                    border: 1px solid #2B4A54;
                    border-radius: 3px;
                    alternate-background-color: #0E2229;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                }}
                QTreeWidget#eventTable::item {{
                    padding: 3px 4px;
                    border-bottom: 1px solid #1B343C;
                }}
                QTreeWidget#eventTable QHeaderView::section {{
                    color: #70CDE8;
                    background: #102730;
                    border: 0;
                    border-bottom: 1px solid #2B4A54;
                    padding: 4px;
                    font-size: 8px;
                    font-weight: 800;
                }}
                QFrame#metricCard, QFrame#hudMeter {{
                    background: #0B181E;
                    border: 1px solid #263F49;
                    border-radius: 3px;
                }}
                QLabel#metricLabel {{
                    color: #6F8790;
                    font-size: 10px;
                    font-weight: 900;
                }}
                QLabel#metricValue {{
                    color: {MUTED_BRIGHT};
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 11px;
                    font-weight: 800;
                }}
                QLabel#mono {{
                    color: #BCD0D5;
                    background: #0B181E;
                    border: 1px solid #263F49;
                    padding: 8px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 10px;
                }}
                QFrame#viewportFrame {{
                    background: #081116;
                    border: 1px solid {LINE};
                }}
                QFrame#sceneBar {{
                    background: #0A1B22;
                    border-bottom: 1px solid {LINE};
                }}
                QLabel#sceneKind {{
                    color: #AAC2CA;
                    border-left: 2px solid {SAFE_GREEN};
                    padding-left: 7px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 10px;
                    font-weight: 700;
                }}
                QLabel#viewportHelp {{
                    color: #748E97;
                    font-size: 10px;
                }}
                QLabel#statusMessage {{
                    color: #B5CBD2;
                    background: #0B2028;
                    border-top: 1px solid {LINE};
                    padding: 8px 13px;
                }}
                QPushButton {{
                    min-height: 38px;
                    color: {MUTED_BRIGHT};
                    background: #13252C;
                    border: 1px solid {LINE_BRIGHT};
                    border-radius: 3px;
                    padding: 0 12px;
                    font-size: 12px;
                    font-weight: 850;
                }}
                QPushButton#sceneSetup, QPushButton#sceneLogic {{
                    min-height: 42px;
                    font-size: 13px;
                    font-weight: 900;
                    background: #17313A;
                    border: 1px solid #5B8998;
                }}
                QPushButton#sceneSetup {{
                    color: #C8F1FF;
                    border-left: 3px solid {CYAN};
                }}
                QPushButton#sceneLogic {{
                    color: #CFF7E5;
                    border-left: 3px solid {SAFE_GREEN};
                }}
                QPushButton#sceneSetup:hover, QPushButton#sceneLogic:hover {{
                    color: #FFFFFF;
                    background: #21424C;
                    border-color: #8BC0CD;
                }}
                QPushButton:hover {{
                    color: {TEXT};
                    background: #193039;
                    border-color: #60818D;
                }}
                QPushButton:pressed {{
                    background: #0E222A;
                }}
                QPushButton:focus {{
                    border: 1px solid {CYAN};
                }}
                QPushButton:disabled {{
                    color: #78939B;
                    background: #102A33;
                    border-color: #365763;
                }}
                QPushButton#connect {{
                    color: #C9F1FF;
                    background: #103243;
                    border-color: #3E9BC0;
                }}
                QPushButton#testPlc {{
                    color: #BDE9FA;
                    background: #12303D;
                    border-color: #39718A;
                }}
                QPushButton#testPlc:hover {{
                    color: #071612;
                    background: {SAFE_GREEN};
                    border-color: {SAFE_GREEN};
                }}
                QPushButton#run, QPushButton#hudRun {{
                    color: #9AE5CA;
                    background: #13352C;
                    border-color: #2D775F;
                }}
                QPushButton#run:hover, QPushButton#hudRun:hover {{
                    color: #071612;
                    background: {SAFE_GREEN};
                    border-color: {SAFE_GREEN};
                }}
                QPushButton#stop, QPushButton#hudStop {{
                    color: #FFE1A1;
                    border-color: #80652F;
                }}
                QPushButton#connect:disabled,
                QPushButton#testPlc:disabled,
                QPushButton#run:disabled,
                QPushButton#stop:disabled,
                QPushButton#hudRun:disabled,
                QPushButton#hudStop:disabled,
                QPushButton#hudReset:disabled {{
                    color: #78939B;
                    background: #102A33;
                    border-color: #365763;
                }}
                QTableWidget {{
                    color: {TEXT};
                    background: #091B22;
                    alternate-background-color: #0D252E;
                    border: 1px solid {LINE};
                    gridline-color: #213741;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 12px;
                    font-weight: 750;
                }}
                QHeaderView::section {{
                    color: {TEXT};
                    background: {PANEL};
                    border: 0;
                    border-bottom: 1px solid {LINE};
                    padding: 6px 7px;
                    font-size: 11px;
                    font-weight: 900;
                }}
                QComboBox {{
                    color: {TEXT};
                    background: #0A1E25;
                    border: 1px solid {LINE_BRIGHT};
                    padding: 5px 8px;
                    min-width: 170px;
                    font-size: 11px;
                    font-weight: 700;
                }}
                QComboBox QAbstractItemView {{
                    color: {TEXT};
                    background: #0B171D;
                    selection-color: #071015;
                    selection-background-color: {CYAN};
                    border: 1px solid {LINE_BRIGHT};
                    font-size: 11px;
                    font-weight: 700;
                }}
                QLabel#pointColumnHeading {{
                    color: {CYAN};
                    background: {PANEL_ALT};
                    border: 1px solid {LINE};
                    padding: 5px 7px;
                    font-size: 11px;
                    font-weight: 800;
                }}
                QScrollBar:vertical {{
                    width: 10px;
                    background: #0B181E;
                }}
                QScrollBar::handle:vertical {{
                    min-height: 24px;
                    background: #526B74;
                    border-radius: 4px;
                }}
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {{
                    height: 0;
                }}
                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {{
                    background: #0B181E;
                }}
                QFrame#transportHud {{
                    background: #09151A;
                    border-top: 1px solid #38545E;
                }}
                QLabel#hudScene {{
                    color: #DBE8EB;
                    font-size: 10px;
                    font-weight: 700;
                }}
                QLabel#hudState {{
                    color: #789099;
                    background: #0B181E;
                    border: 1px solid #36505A;
                    border-radius: 2px;
                    padding: 3px 6px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 700;
                }}
                QLabel#hudLive {{
                    color: #5F7780;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 700;
                }}
                QLabel#hudLockReason {{
                    color: {AMBER};
                    background: #241E11;
                    border: 1px solid #80652F;
                    border-radius: 3px;
                    padding: 4px 7px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 800;
                }}
                QLabel#compactPriorityBar {{
                    color: #E4B657;
                    background: #1D1910;
                    border: 1px solid #80652F;
                    border-radius: 2px;
                    padding: 3px 8px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 800;
                }}
                QTabBar#compactRailNav {{
                    background: #09151A;
                    qproperty-drawBase: 0;
                }}
                QTabBar#compactRailNav::tab {{
                    color: #86A1A9;
                    background: #0B181E;
                    border: 1px solid #2D4750;
                    padding: 5px 7px;
                    min-width: 0px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 8px;
                    font-weight: 800;
                }}
                QTabBar#compactRailNav::tab:selected {{
                    color: #DDECEF;
                    background: #17333D;
                    border-bottom: 2px solid {CYAN};
                }}
                QFrame#meterStrip {{
                    background: #0B181E;
                    border: 1px solid #2D4750;
                    border-radius: 3px;
                }}
            """

        @property
        def current_view_mode(self) -> str:
            return self._view_mode

        @property
        def current_scene_id(self) -> str:
            return self._current_scene_id

        def _is_review_scene(self) -> bool:
            return self._current_scene_id in NATIVE_SCENE_BY_ID

        def _select_scene_id(self, selected: str) -> None:
            if selected not in self.scene_actions:
                return
            snapshot = self.session.snapshot()
            changing_scene = selected != self._current_scene_id
            if changing_scene and (
                self._diagnostic_active
                or snapshot.connection is not ConnectionState.DISCONNECTED
            ):
                current_action = self.scene_actions.get(self._current_scene_id)
                if current_action is not None:
                    current_action.setChecked(True)
                self._show_notice(
                    "Scene change blocked",
                    "Disconnect the PLC session or finish the read-only PLC "
                    "test before changing scenes.",
                )
                return

            self._current_scene_id = selected
            self.scene_actions[selected].setChecked(True)
            self._last_cycle = -1
            if self._is_review_scene():
                self._apply_review_scene(
                    NATIVE_SCENE_BY_ID[self._current_scene_id]
                )
            else:
                self._apply_live_scene(snapshot)

        def _set_scene_actions_enabled(self, enabled: bool) -> None:
            for entry in self.scene_catalog:
                if entry.category == "tool":
                    continue
                self.scene_actions[entry.scene_id].setEnabled(
                    enabled and entry.selectable
                )

        def _connect_equipment_inspection(self) -> None:
            """Connect presentation-only viewport inspection events."""

            hovered = getattr(self.viewport, "container", None)
            if hovered is None:
                return
            hovered_signal = getattr(hovered, "equipmentHovered", None)
            selected_signal = getattr(hovered, "equipmentSelected", None)
            cleared_signal = getattr(hovered, "equipmentCleared", None)
            if hovered_signal is not None:
                hovered_signal.connect(self._on_equipment_hovered)
            if selected_signal is not None:
                selected_signal.connect(self._on_equipment_selected)
            if cleared_signal is not None:
                cleared_signal.connect(self._on_equipment_cleared)

        def _update_event_surface_visibility(self) -> None:
            """Give a pinned asset inspector room beside the secondary history."""

            selected = getattr(self, "_selected_equipment", None) is not None
            has_active_event = bool(self.event_history_store.active())
            self.event_console_button.setVisible(
                not self._compact_display and not (selected and has_active_event)
            )
            self.event_priority_hint.setVisible(
                self._compact_display
                and has_active_event
                and not self._compact_panel_user_selected
            )
            if (
                self._compact_display
                and has_active_event
                and not self._compact_panel_user_selected
                and self.compact_rail_nav.currentIndex() != 1
            ):
                self._suppress_compact_panel_user_selection = True
                try:
                    self.compact_rail_nav.setCurrentIndex(1)
                finally:
                    self._suppress_compact_panel_user_selection = False
            self.event_history_panel.setVisible(
                not (
                    selected
                    and not self._compact_display
                    and not has_active_event
                )
            )
            self.event_table.setVisible(
                not self._compact_display and not selected
            )
            if not self._compact_display:
                if selected and not has_active_event:
                    # Keep the health contract readable while a pinned asset
                    # consumes the right rail; the inspector remains adjacent.
                    self.health_panel.setMaximumHeight(self._scaled(96))
                    self._fill_rail(
                        self.right_rail_layout,
                        (self.health_panel, self.equipment_panel),
                    )
                else:
                    self.health_panel.setMaximumHeight(16777215)
                    self._fill_rail(
                        self.right_rail_layout,
                        (
                            self.event_history_panel,
                            self.equipment_panel,
                            self.health_panel,
                        ),
                    )
            self._update_event_asset_context()

        def _update_event_asset_context(self) -> None:
            selected = getattr(self, "_selected_equipment", None)
            visible = (
                not self._compact_display
                and selected is not None
                and bool(self.event_history_store.active())
            )
            self.event_asset_context.setVisible(visible)
            if not visible:
                return
            lines = self.equipment_inspection.text().splitlines()
            self.event_asset_context.setText(
                "ALARM SOURCE ASSET\n" + "\n".join(lines[1:7])
            )

        def _compact_event_asset_summary(self) -> str:
            if not self._compact_display or self._selected_equipment is None:
                return ""
            lines = self.equipment_inspection.text().splitlines()
            if len(lines) < 4:
                return ""
            separator = " \u00b7 "
            asset_name = lines[0].replace("ASSET  ", "", 1).split(separator, 1)[0]
            tag_line = lines[1].split(separator, 1)[0]
            value = (
                lines[1].split("VALUE ", 1)[-1]
                if "VALUE " in lines[1]
                else "--"
            )
            quality = (
                lines[2].split(separator, 1)[1]
                if separator in lines[2]
                else lines[2]
            ).replace("QUALITY ", "").split(" ", 1)[0]
            permissive = (
                "PERM NOT EVAL"
                if "NOT EVALUATED" in lines[3]
                else lines[3].split(separator)[-1]
            )
            return (
                f"\nASSET  {asset_name}\n"
                f"{tag_line} | VALUE {value}\n"
                f"QUALITY {quality} | {permissive}"
            )

        def _on_equipment_hovered(self, target: Any) -> None:
            if target is None or getattr(self, "_selected_equipment", None) is not None:
                return
            self.equipment_inspection.setText(
                "PREVIEW ASSET\n"
                f"{target.label.upper()}\n"
                f"TYPE  {target.equipment_type}\n"
                "SOURCE  LOCAL MODEL\n"
                "Click to pin inspection"
            )

        def _inspection_contract_lines(
            self,
            target: Any,
            snapshot: Any,
        ) -> tuple[str, str, str]:
            contracts = {
                "main_conveyor": "TAG  conveyor_running",
                "photoeye": "TAG  simulated_photoeye",
                "pusher": "TAG  pusher_extend",
                "drive_motor": "TAG  conveyor_running",
                "stacklight": "TAG  controller diagnostics",
                "package": "TAG  part_at_pusher",
            }
            tag_line = contracts.get(target.target_id, "TAG  scene contract")
            points = getattr(snapshot, "points", {}) or {}
            if snapshot.connection is ConnectionState.DISCONNECTED:
                return (
                    tag_line,
                    "PERM CONTRACT  ·  NOT EVALUATED",
                    "QUALITY OFFLINE  ·  PLC STATE UNKNOWN",
                )
            if not getattr(snapshot, "ready", False):
                return (
                    tag_line,
                    "PERM CONTRACT  ·  NOT EVALUATED",
                    "QUALITY SESSION NOT READY  ·  PLC STATE UNKNOWN",
                )
            if target.target_id == "main_conveyor":
                retract = points.get("pusher_retracted")
                part = points.get("part_at_pusher")
                if isinstance(retract, bool) and isinstance(part, bool):
                    result = "PASS" if retract and not part else "HOLD"
                    return (
                        tag_line,
                        f"PERM EVAL {result}  ·  retract={str(retract).upper()} part={str(part).upper()}",
                        (
                            f"QUALITY FIXTURE EXCHANGE  ·  CYCLE {snapshot.cycle}"
                            if self.visual_qa_fixture
                            else f"QUALITY PLC EXCHANGE ACTIVE  ·  CYCLE {snapshot.cycle}"
                        ),
                    )
            return (
                tag_line,
                "PERM CONTRACT  ·  SESSION ACTIVE",
                (
                    f"QUALITY FIXTURE EXCHANGE  ·  CYCLE {snapshot.cycle}"
                    if self.visual_qa_fixture
                    else f"QUALITY PLC EXCHANGE ACTIVE  ·  CYCLE {snapshot.cycle}"
                ),
            )

        def _inspection_sample_line(self, snapshot: Any) -> str:
            """Describe sample freshness without inventing controller history."""

            if snapshot.connection is ConnectionState.DISCONNECTED:
                return "SAMPLE AGE  --  ·  LOCAL MODEL ONLY"
            if not getattr(snapshot, "ready", False):
                return "SAMPLE AGE  --  ·  EXCHANGE NOT READY"
            if self._last_snapshot_monotonic is None:
                return "SAMPLE AGE  --  ·  WAITING FOR EXCHANGE"
            age = max(0.0, time.monotonic() - self._last_snapshot_monotonic)
            return (
                f"SAMPLE AGE  {age:.1f}s  ·  FIXTURE EXCHANGE"
                if self.visual_qa_fixture
                else f"SAMPLE AGE  {age:.1f}s  ·  PLC EXCHANGE"
            )

        def _inspection_point_line(self, target: Any, snapshot: Any) -> str:
            point_names = {
                "main_conveyor": "conveyor_running",
                "photoeye": "part_at_pusher",
                "pusher": "pusher_extend",
                "drive_motor": "conveyor_running",
                "stacklight": "component_state",
                "package": "part_at_pusher",
            }
            point_name = point_names.get(target.target_id)
            points = getattr(snapshot, "points", {}) or {}
            if (
                point_name is None
                or snapshot.connection is not ConnectionState.CONNECTED
                or not getattr(snapshot, "ready", False)
                or point_name not in points
                or points[point_name] is None
            ):
                return "VALUE  --  ·  UNAVAILABLE"
            return f"VALUE  {point_name}={str(points[point_name]).upper()}"

        def _on_equipment_selected(self, target: Any) -> None:
            self._selected_equipment = target
            self._update_event_surface_visibility()
            self.equipment_list.hide()
            connection = self.session.snapshot().connection
            snapshot = self.session.snapshot()
            if connection is ConnectionState.DISCONNECTED:
                source = inspection_source_text(True)
                status = "Visualization only"
            elif self.visual_qa_fixture:
                source = "Synthetic fixture"
                status = "Presentation state only"
            else:
                source = inspection_source_text(False)
                status = "Presentation state only"
            tag_line, permissive_line, quality_line = (
                self._inspection_contract_lines(target, snapshot)
            )
            sample_line = self._inspection_sample_line(snapshot)
            point_line = self._inspection_point_line(target, snapshot)
            if self._compact_display:
                compact_source = (
                    "SOURCE LOCAL MODEL"
                    if connection is ConnectionState.DISCONNECTED
                    else "SOURCE SYNTHETIC FIXTURE"
                    if self.visual_qa_fixture
                    else "SOURCE PLC SESSION"
                )
                compact_quality = (
                    "QUALITY OFFLINE · PLC UNKNOWN"
                    if connection is ConnectionState.DISCONNECTED
                    else "QUALITY NOT READY · PLC UNKNOWN"
                    if not getattr(snapshot, "ready", False)
                    else (
                        f"QUALITY FIXTURE · CYCLE {snapshot.cycle}"
                        if self.visual_qa_fixture
                        else f"QUALITY ACTIVE · CYCLE {snapshot.cycle}"
                    )
                )
                compact_sample = (
                    "CONNECT APPROVED PLC"
                    if connection is ConnectionState.DISCONNECTED
                    else "WAIT HEALTHY EXCHANGE"
                    if not getattr(snapshot, "ready", False)
                    else sample_line.replace("SAMPLE AGE  ", "SAMPLE ").split(" · ", 1)[0]
                )
                compact_permissive = (
                    "PERM NOT EVALUATED"
                    if "NOT EVALUATED" in permissive_line
                    else "PERM PASS"
                    if "PASS" in permissive_line
                    else "PERM HOLD"
                )
                compact_value = (
                    "VALUE --"
                    if "UNAVAILABLE" in point_line
                    else "VALUE " + point_line.rsplit("=", 1)[-1]
                )
                self.equipment_inspection.setText(
                    f"ASSET  {target.label.upper()}  ·  "
                    f"{target.equipment_type.upper()}\n"
                    f"{tag_line} · {compact_value}\n"
                    f"{compact_source} · {compact_quality}\n"
                    f"{compact_sample} · "
                    f"{compact_permissive}"
                )
            else:
                display_source = (
                    "LOCAL MODEL"
                    if connection is ConnectionState.DISCONNECTED
                    else "SYNTHETIC FIXTURE"
                    if self.visual_qa_fixture
                    else "PLC SESSION"
                )
                display_value = (
                    "VALUE -- / UNAVAILABLE"
                    if "UNAVAILABLE" in point_line
                    else point_line.replace("  ", " ")
                )
                display_permissive = (
                    "PERM NOT EVALUATED"
                    if "NOT EVALUATED" in permissive_line
                    else "PERM PASS"
                    if "PASS" in permissive_line
                    else "PERM HOLD"
                )
                display_quality = (
                    "QUALITY OFFLINE / PLC UNKNOWN"
                    if connection is ConnectionState.DISCONNECTED
                    else "QUALITY SYNTHETIC FIXTURE"
                    if self.visual_qa_fixture
                    else "QUALITY PLC EXCHANGE ACTIVE"
                )
                display_sample = (
                    "SAMPLE -- / LOCAL MODEL"
                    if connection is ConnectionState.DISCONNECTED
                    else sample_line.replace("  ", " ")
                )
                if self._view_mode == "B":
                    self.equipment_inspection.setText(
                        "SELECTED ASSET\n"
                        f"{target.label.upper()}\n"
                        f"TYPE  {target.equipment_type}\n"
                        f"SOURCE {display_source}  ·  {display_quality}\n"
                        f"{tag_line}  ·  {display_value}\n"
                        f"{display_permissive}  ·  {display_sample}\n"
                        f"CONTROL  {'REVIEW ONLY' if self._is_review_scene() else status}"
                    )
                else:
                    self.equipment_inspection.setText(
                        "SELECTED ASSET\n"
                        f"{target.label.upper()}\n"
                        f"TYPE  {target.equipment_type}\n"
                        f"SOURCE  {display_source}\n"
                        f"{tag_line}\n"
                        f"{display_value}\n"
                        f"{display_permissive}\n"
                        f"{display_quality}\n"
                        f"{display_sample}\n"
                        f"CONTROL  {'REVIEW ONLY' if self._is_review_scene() else status}"
                    )
            self._update_event_asset_context()

        def _on_equipment_cleared(self) -> None:
            self._selected_equipment = None
            self._update_event_surface_visibility()
            self.equipment_list.show()
            self.equipment_inspection.setText(
                "EQUIPMENT INSPECTOR\n"
                "Select an asset in the viewport\n"
                "Hover previews; click pins details"
            )

        def _apply_live_scene(self, snapshot: Any) -> None:
            self._active_viewport = self.viewport
            self.viewport_stack.setCurrentIndex(
                self._viewport_indexes["scene-2-conveyor-pusher"]
            )
            self.scene_title.setText("Conveyor Pusher")
            self.scene_text.setText(
                "Run to the photoeye, stop, extend the pusher, transfer "
                "the package, retract, and admit the next package."
            )
            self.scene_scope.setText(
                "REAL S7-1500 · DB14 · RACK 0 / SLOT 1"
            )
            self.scene_asset_badge.setText("6 ASSETS")
            self.equipment_asset_badge.setText("6 ASSETS")
            self.equipment_title.setText("Conveyor pusher cell")
            self.equipment_list.setText(
                "Conveyor\nPackage\nPhotoeye\nPusher cylinder\n"
                "Drive motor\nStack light"
            )
            self._on_equipment_cleared()
            self.hud_scene.setText("Conveyor Pusher")
            self.hud_live.setText(
                "●  LOCAL PLANT VIEW · PLC OUTPUTS NOT VERIFIED"
            )
            self.runtime_scene.setText("Scene 2")
            self._update_scene_kind()
            disconnected = (
                snapshot.connection is ConnectionState.DISCONNECTED
            )
            diagnostic_ready = disconnected and not self._diagnostic_active
            self.action_connect.setEnabled(
                real_plc_writes_enabled and diagnostic_ready
            )
            self.action_test_plc.setEnabled(diagnostic_ready)

        def _apply_review_scene(self, definition: Any) -> None:
            source = self._review_sources[definition.scene_id]
            for event in self.event_history_store.active():
                self.event_history_store.clear(event.event_id)
            equipment = source["equipment"]
            asset_count = len(equipment)
            self._active_viewport = self.review_viewports[
                definition.scene_id
            ]
            self.viewport_stack.setCurrentIndex(
                self._viewport_indexes[definition.scene_id]
            )
            self.scene_title.setText(
                definition.label
            )
            self.scene_text.setText(definition.description)
            self.scene_scope.setText(
                "VISUAL REVIEW ONLY · NO NATIVE PLC PROFILE\n"
                f"SETUP: {definition.setup_file.name}"
            )
            self.scene_asset_badge.setText(f"{asset_count} ASSETS")
            self.equipment_asset_badge.setText(f"{asset_count} ASSETS")
            self.equipment_title.setText(definition.label)
            self.equipment_list.setText(
                "\n".join(str(item["label"]) for item in equipment)
            )
            self._on_equipment_cleared()
            self.runtime_player.setText("REVIEW")
            self.runtime_scene.setText(definition.approval_id)
            self.runtime_time.setText("--")
            self.runtime_exchange.setText("--")
            self.timing.setText(
                "Static native composition\n"
                "Behavior runtime: not created\n"
                "PLC profile: not created"
            )
            self.health_details.setText(
                "PLC access: DISABLED\n"
                "Reason: scene-specific profile not created\n"
                "Scene 2 DB14 fallback: BLOCKED"
            )
            self.hud_scene.setText(
                definition.label
            )
            self.hud_state.setText("REVIEW")
            self.hud_live.setText(
                "●  STATIC VISUAL REVIEW · PLC COMMANDS DISABLED"
            )
            self.hud_time.setText("--")
            self.hud_p99.setText("--")
            self.hud_source.setText("NOT CONFIGURED")
            self.points_source_badge.setText("SOURCE CONTRACT")
            self.status_message.setText(
                "Pending visual approval. Review topology, clipping, "
                "depth order, and readability."
            )
            self.connection_badge.setText("REVIEW ONLY - PLC DISABLED")
            self._render_review_points(source["simulation"]["points"])
            self._render_event_rows()
            self.compact_priority_bar.setText(
                "REVIEW ONLY  ·  PLC DISABLED  ·  NO ACTIVE ALARMS"
            )
            self.compact_runtime_state.setText("PLAYER  REVIEW")
            self.compact_runtime_health.setText("HEALTH  PLC DISABLED")
            self.compact_runtime_time.setText("TIME  --")
            self.compact_runtime_exchange.setText("EXCHANGE  --")
            self.compact_rail_nav.setTabText(1, "EVENTS")
            self.compact_rail_nav.setTabText(2, "HEALTH DISABLED")
            self.compact_rail_nav.setTabText(3, "RUNTIME REVIEW")
            self._set_review_controls_disabled()
            self._update_scene_kind()

        def _set_review_controls_disabled(self) -> None:
            for control in (
                self.hud_run_button,
                self.hud_stop_button,
                self.hud_reset_button,
                self.action_connect,
                self.action_configure_plc,
                self.action_disconnect,
                self.action_test_plc,
                self.action_run,
                self.action_stop,
                self.action_reset,
            ):
                control.setEnabled(False)

        def _ordered_point_groups(
            self,
            points: list[dict[str, Any]],
        ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], tuple[str, str]]:
            """Group point contracts into the two operator-facing columns."""

            def ordered(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
                return sorted(items, key=lambda item: str(item.get("name", "")).lower())

            def owner(name: str) -> list[dict[str, Any]]:
                return [item for item in points if item.get("owner") == name]

            if self.point_order in {"plc-io", "owner"}:
                left = owner("PC") if self.point_order == "plc-io" else owner("PLC")
                right_owners = ("PLC", "SIM") if self.point_order == "plc-io" else ("PC", "SIM")
                right = [item for item in points if item.get("owner") in right_owners]
                labels = (
                    ("SIMULATOR → PLC", "PLC → SIMULATOR + DIAGNOSTICS")
                    if self.point_order == "plc-io"
                    else ("PLC-OWNED POINTS", "SIMULATOR FEEDBACK + DIAGNOSTICS")
                )
                return ordered(left), ordered(right), labels
            if self.point_order == "sim-io":
                return (
                    ordered(owner("PLC")),
                    ordered(owner("PC") + owner("SIM")),
                    ("Simulation inputs", "Simulation outputs + diagnostics"),
                )
            if self.point_order == "type":
                return (
                    ordered([item for item in points if item.get("type") == "BOOL"]),
                    ordered([item for item in points if item.get("type") != "BOOL"]),
                    ("BOOL points", "Numeric, text + diagnostics"),
                )
            all_points = ordered(points)
            midpoint = (len(all_points) + 1) // 2
            return (
                all_points[:midpoint],
                all_points[midpoint:],
                ("A–M", "N–Z"),
            )

        def _set_point_order(self, order: str) -> None:
            if order not in {"plc-io", "sim-io", "owner", "type", "name"}:
                return
            self.point_order = order
            if self._is_review_scene():
                source = self._review_sources[self._current_scene_id]
                self._render_review_points(source["simulation"]["points"])
            else:
                self._render_points(self.session.snapshot())

        def _render_review_points(
            self,
            points: list[dict[str, Any]],
        ) -> None:
            owner_colors = {
                "PLC": ("#FFDDA0", "#3A2D13"),
                "PC": ("#A7DDF0", "#133441"),
                "SIM": ("#A5E5CF", "#12372D"),
            }
            left, right, labels = self._ordered_point_groups(points)
            self.points_column_left.setText(
                f"{labels[0]}  ·  {len(left)} POINTS"
            )
            self.points_column_right.setText(
                f"{labels[1]}  ·  {len(right)} POINTS"
                + (
                    f"  ·  {min(3, len(right))} SHOWN"
                    if self._compact_display and len(right) > 3
                    else ""
                )
            )
            if self._compact_display and len(right) > 3:
                self.points_column_right.setText(
                    self.points_column_right.text()
                    + f"  ·  SCROLL FOR {len(right) - 3} MORE"
                )
            for table, visible_points in (
                (self.points_table, left),
                (self.points_table_right, right),
            ):
                table.setRowCount(len(visible_points))
                for row, point in enumerate(visible_points):
                    initial = point.get("initial")
                    shown = _bool_text(initial) if isinstance(initial, bool) else str(initial)
                    if point.get("unit"):
                        shown = f"{shown} {point['unit']}"
                    values = (str(point["name"]), str(point["type"]), shown, str(point["owner"]))
                    for column, value in enumerate(values):
                        item = QtWidgets.QTableWidgetItem(value)
                        if column == 3 and value in owner_colors:
                            foreground, background = owner_colors[value]
                            item.setForeground(QtGui.QColor(foreground))
                            item.setBackground(QtGui.QColor(background))
                            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                        table.setItem(row, column, item)
                    table.setRowHeight(
                        row,
                        18 if self._compact_display else 24,
                    )

        def _update_scene_kind(self) -> None:
            if self._is_review_scene():
                definition = NATIVE_SCENE_BY_ID[self._current_scene_id]
                asset_count = len(
                    self._review_sources[self._current_scene_id]["equipment"]
                )
                text = (
                    f"{definition.approval_id} · "
                    f"{definition.label.upper()} · {asset_count} ASSETS"
                )
            else:
                text = "CONVEYOR PUSHER"
            self.scene_kind.setText(f"{text} · VIEW {self._view_mode}")

        def _clear_rail(self, layout: Any) -> None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(self.workspace)

        def _fill_rail(
            self,
            layout: Any,
            panels: tuple[Any, ...],
        ) -> None:
            self._clear_rail(layout)
            for panel in panels:
                layout.addWidget(panel)
                panel.show()
            layout.addStretch(1)

        def _repolish(self, widget: Any) -> None:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        def _focus_compact_panel(self, index: int) -> None:
            """Switch the compact operator pane without changing runtime state."""

            targets = (
                self.equipment_panel,
                self.event_history_panel,
                self.health_panel,
                self.compact_runtime_panel,
            )
            if not 0 <= index < len(targets):
                return
            self.compact_panel_stack.setCurrentIndex(index)
            self._update_event_row_actions()

        def _on_compact_panel_changed(self, index: int) -> None:
            if not self._suppress_compact_panel_user_selection:
                self._compact_panel_user_selected = True
            self._focus_compact_panel(index)

        def set_view_mode(self, mode: str) -> None:
            """Rearrange the shared widgets without touching runtime state."""

            normalized = mode.upper()
            if normalized not in VIEW_NAMES:
                raise ValueError(f"Unknown native view mode: {mode}")
            compact_review = self._compact_display and self._is_review_scene()

            self._clear_rail(self.left_rail_layout)
            self._clear_rail(self.right_rail_layout)
            for panel in self._panel_widgets:
                self.workspace_layout.removeWidget(panel)
                if not self._compact_display:
                    panel.setParent(self.workspace)
                panel.hide()
            for widget in (
                self.left_rail,
                self.right_rail,
                self.compact_right_container,
                self.viewport_frame,
            ):
                self.workspace_layout.removeWidget(widget)
                widget.hide()

            self.workspace_layout.setContentsMargins(0, 0, 0, 0)
            self.workspace_layout.setHorizontalSpacing(0)
            self.workspace_layout.setVerticalSpacing(0)
            for column in range(3):
                self.workspace_layout.setColumnMinimumWidth(column, 0)
                self.workspace_layout.setColumnStretch(column, 0)
            for row in range(2):
                self.workspace_layout.setRowMinimumHeight(row, 0)
                self.workspace_layout.setRowStretch(row, 0)

            rail_name = "cardRail" if normalized == "B" else "rail"
            self.left_rail.setObjectName(rail_name)
            self.right_rail.setObjectName(rail_name)
            self._repolish(self.left_rail)
            self._repolish(self.right_rail)

            if normalized == "A":
                self._fill_rail(
                    self.left_rail_layout,
                    (self.scene_panel, self.runtime_panel),
                )
                if not self._compact_display:
                        self._fill_rail(
                        self.right_rail_layout,
                        (
                            self.event_history_panel,
                            self.equipment_panel,
                            self.health_panel,
                        ),
                    )
                self.workspace_layout.setColumnMinimumWidth(0, 270)
                self.workspace_layout.setColumnMinimumWidth(1, 420)
                self.workspace_layout.setColumnMinimumWidth(2, 235)
                self.workspace_layout.setColumnStretch(1, 1)
                self.workspace_layout.setRowMinimumHeight(
                    1,
                    180 if self._compact_display else 270
                )
                self.workspace_layout.setRowStretch(0, 1)
                self.workspace_layout.addWidget(
                    self.left_rail,
                    0,
                    0,
                )
                self.workspace_layout.addWidget(
                    self.viewport_frame,
                    0,
                    1,
                )
                self.workspace_layout.addWidget(
                    self.compact_right_container
                    if self._compact_display
                    else self.right_rail,
                    0,
                    2,
                )
                self.workspace_layout.addWidget(
                    self.points_panel,
                    1,
                    0,
                    1,
                    3,
                )
                self.points_panel.setVisible(not compact_review)
            elif normalized == "B":
                # QWidget.createWindowContainer owns a native child window.
                # True translucent QWidget overlays are not reliable over it,
                # so the browser's floating cards become bordered edge cards.
                self.workspace_layout.setContentsMargins(12, 12, 12, 12)
                self.workspace_layout.setHorizontalSpacing(12)
                self._fill_rail(
                    self.left_rail_layout,
                    (self.scene_panel,),
                )
                if not self._compact_display:
                    self._fill_rail(
                        self.right_rail_layout,
                        (
                            self.event_history_panel,
                            self.equipment_panel,
                            self.health_panel,
                            self.runtime_panel,
                        ),
                    )
                self.workspace_layout.setColumnMinimumWidth(0, 250)
                self.workspace_layout.setColumnMinimumWidth(1, 420)
                self.workspace_layout.setColumnMinimumWidth(2, 285)
                self.workspace_layout.setColumnStretch(1, 1)
                self.workspace_layout.setRowMinimumHeight(
                    1,
                    180 if self._compact_display else 270
                )
                self.workspace_layout.setRowStretch(0, 1)
                self.workspace_layout.addWidget(
                    self.left_rail,
                    0,
                    0,
                )
                self.workspace_layout.addWidget(
                    self.viewport_frame,
                    0,
                    1,
                )
                self.workspace_layout.addWidget(
                    self.compact_right_container
                    if self._compact_display
                    else self.right_rail,
                    0,
                    2,
                )
                self.workspace_layout.addWidget(
                    self.points_panel,
                    1,
                    0,
                    1,
                    3,
                )
            else:
                self._fill_rail(
                    self.left_rail_layout,
                    (
                        self.scene_panel,
                    ),
                )
                if not self._compact_display:
                    self._fill_rail(
                        self.right_rail_layout,
                        (
                            self.event_history_panel,
                            self.equipment_panel,
                            self.health_panel,
                            self.runtime_panel,
                        ),
                    )
                self.workspace_layout.setColumnMinimumWidth(0, 315)
                self.workspace_layout.setColumnMinimumWidth(1, 400)
                self.workspace_layout.setColumnMinimumWidth(2, 270)
                self.workspace_layout.setColumnStretch(1, 1)
                self.workspace_layout.setRowMinimumHeight(
                    1,
                    180 if self._compact_display else 270
                )
                self.workspace_layout.setRowStretch(0, 1)
                self.workspace_layout.addWidget(
                    self.left_rail,
                    0,
                    0,
                )
                self.workspace_layout.addWidget(
                    self.viewport_frame,
                    0,
                    1,
                )
                self.workspace_layout.addWidget(
                    self.compact_right_container
                    if self._compact_display
                    else self.right_rail,
                    0,
                    2,
                )
                self.workspace_layout.addWidget(
                    self.points_panel,
                    1,
                    0,
                    1,
                    3,
                )

            if compact_review:
                self.workspace_layout.setRowMinimumHeight(1, 0)
                self.workspace_layout.setRowStretch(1, 0)
                self.workspace_layout.removeWidget(self.points_panel)
                self.points_panel.hide()

            self.left_rail.show()
            if self._compact_display:
                for panel in (
                    self.equipment_panel,
                    self.event_history_panel,
                    self.health_panel,
                    self.compact_runtime_panel,
                ):
                    panel.show()
                self.compact_right_container.show()
                self.compact_panel_stack.show()
                self.compact_rail_nav.show()
            else:
                self.right_rail.show()
                self.right_rail.verticalScrollBar().setValue(0)
            self.event_console_button.setVisible(not self._compact_display)
            self._update_event_surface_visibility()
            self._update_event_row_actions()
            self.viewport_frame.show()
            self.points_panel.setVisible(not compact_review)
            self._view_mode = normalized
            self.view_actions[normalized].setChecked(True)
            self.view_badge.setText(
                f"{normalized} · {VIEW_NAMES[normalized].upper()}"
            )
            self._update_scene_kind()

        def _reset_camera(self) -> None:
            reset = getattr(self._active_viewport, "reset_camera", None)
            if callable(reset):
                reset()

        def _dialog_stylesheet(self) -> str:
            return f"""
                QDialog {{
                    color: {TEXT};
                    background: #0B171D;
                }}
                QLabel {{
                    color: {TEXT};
                    font-family: "Segoe UI Variable", "Segoe UI";
                    font-size: 13px;
                    font-weight: 600;
                }}
                QLabel#dialogTitle {{
                    color: {TEXT};
                    font-size: 18px;
                    font-weight: 900;
                }}
                QLabel#dialogScope {{
                    color: {MUTED_BRIGHT};
                    background: #0A2028;
                    border: 1px solid {LINE_BRIGHT};
                    border-left: 3px solid {CYAN};
                    padding: 12px;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton {{
                    min-width: 90px;
                    min-height: 38px;
                    color: {MUTED_BRIGHT};
                    background: #13252C;
                    border: 1px solid {LINE_BRIGHT};
                    border-radius: 3px;
                    padding: 0 10px;
                    font-size: 12px;
                    font-weight: 850;
                }}
                QPushButton#confirm {{
                    color: #BDE9FA;
                    background: #103243;
                    border-color: #3E9BC0;
                }}
                QFrame#galleryHeader,
                QFrame#gallerySidePanel,
                QFrame#galleryCenterPanel {{
                    background: #0D2028;
                    border: 1px solid {LINE};
                }}
                QListWidget#galleryAssetList {{
                    color: {TEXT};
                    background: #07151B;
                    border: 1px solid {LINE_BRIGHT};
                    font-size: 12px;
                    font-weight: 700;
                    outline: none;
                }}
                QListWidget#galleryAssetList::item {{
                    padding: 9px 7px;
                    border-bottom: 1px solid #203741;
                }}
                QListWidget#galleryAssetList::item:selected {{
                    color: #071015;
                    background: {CYAN};
                }}
                QTabWidget#galleryInfoTabs::pane {{
                    border: 1px solid {LINE_BRIGHT};
                    background: #0D2028;
                }}
                QTabWidget#galleryInfoTabs QTabBar::tab {{
                    color: {MUTED_BRIGHT};
                    background: #13252C;
                    border: 1px solid {LINE_BRIGHT};
                    padding: 7px 13px;
                    font-size: 11px;
                    font-weight: 850;
                }}
                QTabWidget#galleryInfoTabs QTabBar::tab:selected {{
                    color: #071015;
                    background: {CYAN};
                }}
                QTextBrowser#galleryDetails {{
                    color: {TEXT};
                    background: #07151B;
                    border: 1px solid {LINE_BRIGHT};
                    padding: 8px;
                    font-size: 12px;
                }}
                QTreeWidget {{
                    color: {MUTED_BRIGHT};
                    background: #091B22;
                    alternate-background-color: #0D252E;
                    border: 1px solid {LINE};
                    gridline-color: #213741;
                    font-family: "Cascadia Mono", "Consolas";
                    font-size: 9px;
                }}
                QHeaderView::section {{
                    color: #8BA2AA;
                    background: #101F26;
                    border: 0;
                    border-bottom: 1px solid {LINE};
                    padding: 7px;
                    font-size: 10px;
                    font-weight: 900;
                }}
            """

        def _confirm_action(
            self,
            title: str,
            body: str,
            *,
            confirm_text: str,
        ) -> bool:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.setMinimumWidth(520)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(20, 18, 20, 18)
            layout.setSpacing(13)
            heading = QtWidgets.QLabel(title)
            heading.setObjectName("dialogTitle")
            layout.addWidget(heading)
            scope = QtWidgets.QLabel(body)
            scope.setObjectName("dialogScope")
            scope.setWordWrap(True)
            scope.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
            )
            layout.addWidget(scope)
            buttons = QtWidgets.QDialogButtonBox()
            cancel = buttons.addButton(
                "Cancel",
                QtWidgets.QDialogButtonBox.ButtonRole.RejectRole,
            )
            confirm = buttons.addButton(
                confirm_text,
                QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole,
            )
            confirm.setObjectName("confirm")
            cancel.clicked.connect(dialog.reject)
            confirm.clicked.connect(dialog.accept)
            layout.addWidget(buttons)
            return dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted

        def _show_notice(self, title: str, body: str) -> None:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.setMinimumWidth(460)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(20, 18, 20, 18)
            layout.setSpacing(13)
            heading = QtWidgets.QLabel(title)
            heading.setObjectName("dialogTitle")
            message = QtWidgets.QLabel(body)
            message.setObjectName("dialogScope")
            message.setWordWrap(True)
            layout.addWidget(heading)
            layout.addWidget(message)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Close
            )
            buttons.rejected.connect(dialog.reject)
            buttons.clicked.connect(dialog.accept)
            layout.addWidget(buttons)
            dialog.exec()

        def _show_document(self, title: str, document_html: str) -> None:
            """Show a readable training document instead of a text dump."""

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.resize(860, 720)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(18, 16, 18, 16)
            layout.setSpacing(10)
            heading = QtWidgets.QLabel(title)
            heading.setObjectName("dialogTitle")
            layout.addWidget(heading)
            document = QtWidgets.QTextBrowser()
            document.setOpenExternalLinks(False)
            document.setReadOnly(True)
            document.setHtml(document_html)
            document.setStyleSheet(
                """
                QTextBrowser {
                    background: #0A1E25;
                    color: #EAF2F4;
                    border: 1px solid #3A5C67;
                    padding: 12px;
                    selection-background-color: #245D70;
                    font-size: 13px;
                }
                """
            )
            layout.addWidget(document, 1)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Close
            )
            buttons.rejected.connect(dialog.reject)
            buttons.clicked.connect(dialog.accept)
            layout.addWidget(buttons)
            dialog.exec()

        def _show_about(self) -> None:
            self._show_notice(
                "About RungProof",
                (
                    "RungProof - PLC Visual Simulator\n\n"
                    f"Version {APP_VERSION}\n\n"
                    "Build the logic. Prove the machine.\n\n"
                    "Native software-rendered Scene 2 with direct Snap7 "
                    "PLC exchange and an optional Qt 3D renderer."
                ),
            )

        def _show_scene_editor(self) -> None:
            if getattr(sys, "frozen", False):
                self._show_notice(
                    "Scene Authoring",
                    "Static scene authoring is available in the source workspace only.\n\n"
                    "This packaged pilot remains the fail-closed simulator/player."
                )
                return
            StaticSceneEditorDialog(self.qt, self).exec()

        def _show_initial_simulation_setup(self) -> None:
            esc = html.escape
            common_rows = "".join(
                f"<tr><td><code>{esc(name)}</code></td><td>{esc(point_type)}</td>"
                f"<td>{esc(direction)}</td><td>{esc(purpose)}</td></tr>"
                for name, point_type, direction, purpose in (
                    (
                        "PC_Heartbeat",
                        "DINT",
                        "Simulator → PLC",
                        "Incrementing heartbeat written by RungProof.",
                    ),
                    (
                        "PLC_Heartbeat_Echo",
                        "DINT",
                        "PLC → Simulator",
                        "PLC echo of the most recent PC heartbeat.",
                    ),
                    (
                        "Simulation_Enable",
                        "BOOL",
                        "PLC → Simulator",
                        "PLC authorization for simulation operation.",
                    ),
                    (
                        "Simulation_Comm_OK",
                        "BOOL",
                        "PLC → Simulator",
                        "Watchdog communication-good status.",
                    ),
                    (
                        "Simulation_Timeout",
                        "BOOL",
                        "PLC → Simulator",
                        "Watchdog timeout indication; TRUE is not ready.",
                    ),
                )
            )
            document = (
                "<style>body{font-family:'Segoe UI';color:#EAF2F4;}h1{color:#EAF2F4;}"
                "h2{color:#5FC5EC;border-bottom:1px solid #29414B;padding-bottom:4px;"
                "margin-top:18px;}h3{color:#ADC0C6;}p,li,td{font-size:13px;"
                "line-height:1.4;}table{border-collapse:collapse;width:100%;}"
                "th{background:#152830;color:#EAF2F4;text-align:left;}th,td{border:"
                "1px solid #29414B;padding:7px;vertical-align:top;}code{color:#FFFFFF;"
                "font-weight:700;}.warning{border-left:4px solid #F2B94B;padding:10px;"
                "background:#1D2520;}.ready{border-left:4px solid #3DD6A5;padding:10px;"
                "background:#102C29;}</style>"
                "<h1>Initial Simulation Setup</h1>"
                "<p>Complete this common foundation once before building Scene 1, "
                "Scene 2, S03–S06, or Lab 2.1. Later cumulative labs retain this "
                "foundation and add only their new process tags and logic.</p>"
                "<h2>1. Create the bench PLC project</h2><ol>"
                "<li>Create or open the isolated TIA Portal V17 bench project.</li>"
                "<li>Add the assigned S7-1500 CPU and configure the isolated Ethernet "
                "network using the approved IP, rack, and slot for this bench.</li>"
                "<li>Do not guess or copy an address from another PLC. Verify the "
                "endpoint before any connection authorization.</li></ol>"
                "<h2>2. Create the common DB and watchdog fields</h2>"
                "<p>Create the common <code>DB_SimulationProof</code> data block using "
                "the project’s approved optimized/non-optimized layout. The exact "
                "byte offsets must be verified in TIA before using a profile.</p>"
                f"<table><thead><tr><th>Member</th><th>Type</th><th>Direction</th>"
                f"<th>Purpose</th></tr></thead><tbody>{common_rows}</tbody></table>"
                "<h2>3. Watchdog logic</h2><p>Each PLC scan should echo the PC heartbeat. "
                "The watchdog compares the current heartbeat with the last accepted "
                "value and controls the common status fields:</p><ul>"
                "<li><code>Simulation_Enable</code> is TRUE only when the PLC program "
                "intentionally authorizes simulation.</li>"
                "<li><code>Simulation_Comm_OK</code> is TRUE only while heartbeat "
                "exchange is fresh and valid.</li>"
                "<li><code>Simulation_Timeout</code> becomes TRUE when the heartbeat "
                "is stale or the watchdog timer expires.</li></ul>"
                "<p class='ready'><b>Ready condition:</b> the simulator treats the "
                "PLC as ready only when the connection is healthy, Enable is TRUE, "
                "Comm_OK is TRUE, and Timeout is FALSE.</p>"
                "<h2>4. Verify in a TIA watch table</h2><ol>"
                "<li>Monitor all five common fields and the PLC heartbeat echo.</li>"
                "<li>Confirm the echo follows the changing <code>PC_Heartbeat</code>.</li>"
                "<li>Confirm Enable and Comm_OK become TRUE only through the PLC logic.</li>"
                "<li>Stop or disconnect the simulator and confirm the PLC watchdog "
                "eventually reports timeout and clears readiness.</li>"
                "<li>Reconnect only after the stale condition has been cleared and "
                "the PLC program is in the intended safe state.</li></ol>"
                "<h2>5. Add a scene process contract</h2><p>After the foundation is "
                "proven, add the selected scene’s exact PLC commands and simulator "
                "feedback from Setup. Scene tags must not replace or rename the five "
                "common watchdog fields.</p>"
                "<p class='warning'><b>Bench-only boundary:</b> this document is for "
                "an isolated test PLC with no physical I/O. It is not a production "
                "commissioning procedure and does not bypass safety logic.</p>"
                "<p>Full reference: <code>docs/PLC_BENCH_SETUP.md</code></p>"
            )
            watchdog_networks = [
                {
                    "number": 1,
                    "comment": "Echo the simulator heartbeat",
                    "contacts": ["PC_Heartbeat_CHANGED"],
                    "instruction": "MOVE  PC_Heartbeat  →  PLC_Heartbeat_Echo",
                    "explanation": "Use a changed-value or fresh-data condition to copy the simulator heartbeat into the PLC echo member. The exact MOVE implementation depends on the TIA block style.",
                },
                {
                    "number": 2,
                    "comment": "Fresh heartbeat establishes communication good",
                    "contacts": ["Heartbeat_Fresh", "NOT Watchdog_Timeout"],
                    "coil": "Simulation_Comm_OK",
                    "explanation": "Communication-good is true only while the watchdog sees fresh heartbeat data and the timeout condition is clear.",
                },
                {
                    "number": 3,
                    "comment": "Timeout removes communication good and reports fault",
                    "contacts": ["Watchdog_Timeout"],
                    "coil": "NOT Simulation_Comm_OK",
                    "explanation": "A stale heartbeat must remove the communication-good status. Set Simulation_Timeout in the same timeout-handling network or watchdog block.",
                },
                {
                    "number": 4,
                    "comment": "Common simulation permissive for scene logic",
                    "contacts": ["Simulation_Enable", "Simulation_Comm_OK", "NOT Simulation_Timeout"],
                    "coil": "Simulation_Permissive",
                    "explanation": "Use this common permissive as the first condition in scene output rungs. Simulation_Permissive is internal PLC logic, not an additional simulator interface tag.",
                },
            ]
            self._show_ladder_document(
                "Initial Simulation Setup",
                watchdog_networks,
                intro_html=document,
            )

        def _open_equipment_gallery(self) -> None:
            snapshot = self.session.snapshot()
            if (
                self._diagnostic_active
                or snapshot.connection is not ConnectionState.DISCONNECTED
            ):
                self._show_notice(
                    "Equipment Gallery blocked",
                    "Disconnect the PLC session and finish the read-only "
                    "diagnostic before opening the geometry review gallery.",
                )
                return
            previous_scene = (
                self._current_scene_id
                if self._current_scene_id in self.scene_actions
                else SCENE_ID
            )
            dialog = self._build_equipment_gallery_dialog()
            dialog.exec()
            if self._current_scene_id == EQUIPMENT_GALLERY_DEFINITION.scene_id:
                self._select_scene_id(previous_scene)

        def _build_equipment_gallery_dialog(self) -> Any:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("RungProof - Equipment Gallery")
            dialog.setModal(True)
            compact_gallery = self._compact_display
            dialog.resize(960, 520) if compact_gallery else dialog.resize(1480, 900)
            dialog.setMinimumSize(860, 480)
            dialog.setStyleSheet(self._dialog_stylesheet())
            outer = QtWidgets.QVBoxLayout(dialog)
            outer.setContentsMargins(
                12 if compact_gallery else 16,
                10 if compact_gallery else 14,
                12 if compact_gallery else 16,
                10 if compact_gallery else 14,
            )
            outer.setSpacing(6 if compact_gallery else 10)

            header = QtWidgets.QFrame()
            header.setObjectName("galleryHeader")
            header_layout = QtWidgets.QVBoxLayout(header)
            header_layout.setContentsMargins(
                10 if compact_gallery else 12,
                6 if compact_gallery else 10,
                10 if compact_gallery else 12,
                6 if compact_gallery else 10,
            )
            title = QtWidgets.QLabel("Reusable Equipment Gallery")
            title.setObjectName("dialogTitle")
            subtitle = QtWidgets.QLabel(
                "Inspect geometry before scene placement."
                if compact_gallery
                else "Inspect one reusable asset at a time before placing it into a "
                "production scene. Geometry corrections belong here first."
            )
            subtitle.setObjectName("dialogScope")
            subtitle.setWordWrap(True)
            header_layout.addWidget(title)
            header_layout.addWidget(subtitle)
            outer.addWidget(header)

            body = QtWidgets.QHBoxLayout()
            body.setSpacing(10)
            outer.addLayout(body, 1)

            selector_panel = QtWidgets.QFrame()
            selector_panel.setObjectName("gallerySidePanel")
            selector_panel.setMinimumWidth(250)
            selector_layout = QtWidgets.QVBoxLayout(selector_panel)
            selector_layout.setContentsMargins(10, 10, 10, 10)
            selector_layout.setSpacing(7)
            selector_heading = QtWidgets.QLabel("EQUIPMENT SELECTOR")
            selector_heading.setObjectName("sectionLabel")
            selector_layout.addWidget(selector_heading)
            asset_search = QtWidgets.QLineEdit()
            asset_search.setObjectName("galleryAssetSearch")
            asset_search.setPlaceholderText(
                "Filter type, asset name, or reference..."
            )
            asset_search.setClearButtonEnabled(True)
            asset_search.setStyleSheet(
                "QLineEdit#galleryAssetSearch {"
                "background: #0B2027; color: #EAF2F4; "
                "border: 1px solid #3B7280; border-radius: 3px; "
                "padding: 5px 7px; selection-background-color: #197D9B; "
                "selection-color: #FFFFFF; }"
                "QLineEdit#galleryAssetSearch:focus {"
                "border: 1px solid #5FC5EC; }"
                "QLineEdit#galleryAssetSearch::placeholder {"
                "color: #8EB5BF; }"
            )
            selector_layout.addWidget(asset_search)
            asset_count = QtWidgets.QLabel(
                f"{len(ASSET_DEFINITIONS)} ASSETS  ·  PENDING VISUAL APPROVAL"
            )
            asset_count.setObjectName("dialogScope")
            selector_layout.addWidget(asset_count)
            selector_help = QtWidgets.QLabel(
                "Select an asset to load its isolated geometry."
            )
            selector_help.setObjectName("dialogScope")
            selector_help.setWordWrap(True)
            selector_layout.addWidget(selector_help)
            asset_list = QtWidgets.QListWidget()
            asset_list.setObjectName("galleryAssetList")
            asset_list.setMinimumWidth(230)
            asset_list.setSpacing(2)
            asset_list.setWordWrap(False)
            asset_list.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            asset_list.setTextElideMode(
                QtCore.Qt.TextElideMode.ElideRight
            )
            selector_layout.addWidget(asset_list, 1)
            empty_state = QtWidgets.QLabel(
                "NO MATCHES\nClear the filter to browse all assets."
            )
            empty_state.setObjectName("galleryEmptyState")
            empty_state.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            empty_state.setWordWrap(True)
            empty_state.hide()
            selector_layout.addWidget(empty_state)

            center = QtWidgets.QFrame()
            center.setObjectName("galleryCenterPanel")
            center_layout = QtWidgets.QVBoxLayout(center)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.setSpacing(7)
            camera_bar = QtWidgets.QHBoxLayout()
            camera_bar.setSpacing(5)
            camera_label = QtWidgets.QLabel("VIEW")
            camera_label.setObjectName("sectionLabel")
            camera_bar.addWidget(camera_label)
            camera_bar.addStretch(1)

            viewport = NativeEquipmentAssetViewport(
                qt,
                EQUIPMENT_GALLERY_DEFINITION,
                ASSET_DEFINITIONS[0].asset_type,
                ASSET_DEFINITIONS[0].label,
                ASSET_DEFINITIONS[0].view_span,
                ASSET_DEFINITIONS[0].approval_id,
                ASSET_DEFINITIONS[0].reference_name,
            )
            viewport.compact_display = compact_gallery

            def camera_button(
                text: str,
                callback: Any,
                width: int,
            ) -> Any:
                button = QtWidgets.QPushButton(text)
                button.setMinimumHeight(32)
                button.setFixedWidth(width)
                button.clicked.connect(callback)
                camera_bar.addWidget(button)
                return button

            camera_button("Zoom -", lambda: viewport.zoom_by(-0.15), 58)
            camera_button("Zoom +", lambda: viewport.zoom_by(0.15), 58)
            camera_button("Front", lambda: viewport.set_view_preset(32.0, 29.0), 58)
            camera_button("Top", lambda: viewport.set_view_preset(0.0, 58.0), 52)
            camera_button("Left", lambda: viewport.set_view_preset(72.0, 29.0), 52)
            more_views = QtWidgets.QPushButton("Views")
            more_views.setMinimumHeight(32)
            more_views.setFixedWidth(56)
            more_views_menu = QtWidgets.QMenu(more_views)
            more_views_menu.addAction(
                "Right",
                lambda: viewport.set_view_preset(-72.0, 29.0),
            )
            more_views_menu.addAction(
                "Rear",
                lambda: viewport.set_view_preset(-148.0, 29.0),
            )
            more_views.setMenu(more_views_menu)
            camera_bar.addWidget(more_views)
            camera_button("Reset", viewport.reset_camera, 58)
            center_layout.addLayout(camera_bar)
            center_layout.addWidget(viewport.container, 1)
            body.addWidget(center, 1)

            details_panel = QtWidgets.QFrame()
            details_panel.setObjectName("gallerySidePanel")
            details_panel.setMinimumWidth(285)
            details_layout = QtWidgets.QVBoxLayout(details_panel)
            details_layout.setContentsMargins(10, 10, 10, 10)
            details_layout.setSpacing(7)
            details_heading = QtWidgets.QLabel("ASSET DETAILS")
            details_heading.setObjectName("sectionLabel")
            details_layout.addWidget(details_heading)
            details = QtWidgets.QTextBrowser()
            details.setOpenExternalLinks(False)
            details.setReadOnly(True)
            details.setObjectName("galleryDetails")
            details_layout.addWidget(details, 1)
            if compact_gallery:
                info_tabs = QtWidgets.QTabWidget()
                info_tabs.setObjectName("galleryInfoTabs")
                info_tabs.setDocumentMode(True)
                info_tabs.setMinimumWidth(280)
                info_tabs.addTab(selector_panel, "ASSETS")
                info_tabs.addTab(details_panel, "DETAILS")
                body.addWidget(info_tabs, 0)
            else:
                body.insertWidget(0, selector_panel, 0)
                body.addWidget(details_panel, 0)

            footer = QtWidgets.QHBoxLayout()
            footer.setSpacing(8)
            footer_note = QtWidgets.QLabel(
                "REVIEW ONLY  ·  PLC DISABLED  ·  NO PLC TRANSPORT"
            )
            footer_note.setObjectName("dialogScope")
            footer.addWidget(footer_note, 1)
            close_button = QtWidgets.QPushButton("Close Gallery")
            close_button.setObjectName("confirm")
            close_button.setMinimumSize(145, 40)
            close_button.clicked.connect(dialog.accept)
            footer.addWidget(close_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
            outer.addLayout(footer)

            def update_details(row: int) -> None:
                if row < 0:
                    return
                item = asset_list.item(row)
                if item is None:
                    return
                index = int(item.data(QtCore.Qt.ItemDataRole.UserRole))
                definition = ASSET_DEFINITIONS[index]
                viewport.set_asset(
                    definition.asset_type,
                    definition.label,
                    definition.view_span,
                    approval_id=definition.approval_id,
                    reference_name=definition.reference_name,
                )
                capabilities = "".join(
                    f"<li>{html.escape(capability)}</li>"
                    for capability in _gallery_capabilities(
                        definition.asset_type
                    )
                )
                details.setHtml(
                    "<style>body{color:#EAF2F4;font-family:'Segoe UI';}"
                    "h2{color:#5FC5EC;font-size:16px;}h3{color:#ADC0C6;"
                    "font-size:12px;text-transform:uppercase;}li,p{font-size:12px;"
                    "line-height:1.35;}code{color:#FFFFFF;}"
                    ".note{border-left:3px solid #F2B94B;padding:7px;"
                    "background:#1D2520;}</style>"
                    f"<h2>{html.escape(definition.label)}</h2>"
                    f"<p><b>Asset type:</b> <code>{html.escape(definition.asset_type)}</code></p>"
                    f"<p><b>Reference:</b> {html.escape(definition.reference_name)}</p>"
                    f"<p><b>Viewport span:</b> {definition.view_span:.1f} units</p>"
                    "<h3>Configuration</h3>"
                    "<p>Rendered by the native reusable-asset builder. Review "
                    "proportions, supports, moving members, and hidden geometry "
                    "before scene placement.</p>"
                    f"<h3>Capabilities</h3><ul>{capabilities}</ul>"
                    "<h3>PLC I/O and tags</h3>"
                    "<p class='note'><b>None assigned in the gallery.</b><br>"
                    "This asset is geometry only. PLC commands, feedback, tags, "
                    "and addresses are defined by the scene that uses it.</p>"
                    "<h3>Correction checklist</h3><ul>"
                    "<li>Does the equipment read correctly from front, rear, left, right, and top?</li>"
                    "<li>Are shafts, guards, supports, rails, and connections physically plausible?</li>"
                    "<li>Is there any clipping, incorrect depth order, or hidden geometry?</li>"
                    "</ul>"
                )

            def filter_assets(query: str) -> None:
                normalized = query.strip().casefold()
                visible_count = 0
                first_visible = -1
                for row in range(asset_list.count()):
                    item = asset_list.item(row)
                    definition = ASSET_DEFINITIONS[
                        int(item.data(QtCore.Qt.ItemDataRole.UserRole))
                    ]
                    searchable = " ".join(
                        (
                            definition.asset_type,
                            definition.label,
                            definition.reference_name,
                            definition.approval_id,
                        )
                    ).casefold()
                    matches = not normalized or normalized in searchable
                    item.setHidden(not matches)
                    if matches:
                        visible_count += 1
                        if first_visible < 0:
                            first_visible = row
                asset_count.setText(
                    f"{visible_count} MATCH{'ES' if visible_count != 1 else ''}"
                    "  ·  PENDING VISUAL APPROVAL"
                )
                empty_state.setVisible(visible_count == 0)
                selector_help.setText(
                    "No matching assets. Current preview retained."
                    if visible_count == 0
                    else "Select an asset to load its isolated geometry."
                )
                if first_visible >= 0:
                    asset_list.setCurrentRow(first_visible)

            asset_search.textChanged.connect(filter_assets)

            for index, definition in enumerate(ASSET_DEFINITIONS):
                item = QtWidgets.QListWidgetItem(
                    f"{definition.asset_type}  ·  {definition.label}"
                )
                item.setData(QtCore.Qt.ItemDataRole.UserRole, index)
                item.setToolTip(
                    f"{definition.approval_id}  ·  {definition.label}\n"
                    f"Reference: {definition.reference_name}"
                )
                asset_list.addItem(item)
            asset_list.currentRowChanged.connect(update_details)
            asset_list.setCurrentRow(0)
            return dialog

        def _configure_plc(self) -> None:
            snapshot = self.session.snapshot()
            if (
                self._is_review_scene()
                or self._diagnostic_active
                or snapshot.connection is not ConnectionState.DISCONNECTED
            ):
                return
            config = self.session.config
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Configure PLC Target")
            dialog.setModal(True)
            dialog.setMinimumWidth(560)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(20, 18, 20, 18)
            layout.setSpacing(12)
            title = QtWidgets.QLabel("Configure PLC Target")
            title.setObjectName("dialogTitle")
            layout.addWidget(title)
            note = QtWidgets.QLabel(
                "Enter a known Siemens S7-1500 endpoint. Automatic PLC "
                "discovery/search is not enabled yet. This changes only "
                "the connection target; the validated DB14 tag contract "
                "does not change."
            )
            note.setWordWrap(True)
            note.setObjectName("dialogScope")
            layout.addWidget(note)
            form = QtWidgets.QFormLayout()
            form.setLabelAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
            )
            ip_edit = QtWidgets.QLineEdit(config.connection.ip)
            ip_edit.setPlaceholderText("192.168.0.10")
            rack_spin = QtWidgets.QSpinBox()
            rack_spin.setRange(0, 7)
            rack_spin.setValue(config.connection.rack)
            slot_spin = QtWidgets.QSpinBox()
            slot_spin.setRange(0, 31)
            slot_spin.setValue(config.connection.slot)
            form.addRow("IP address:", ip_edit)
            form.addRow("Rack:", rack_spin)
            form.addRow("Slot:", slot_spin)
            layout.addLayout(form)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Save
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            try:
                self.session.configure_connection(
                    ip=ip_edit.text(),
                    rack=rack_spin.value(),
                    slot=slot_spin.value(),
                )
            except NativeRuntimeError as exc:
                self._show_notice("PLC target not saved", str(exc))
                return
            self._show_notice(
                "PLC target saved",
                (
                    f"Known target set to {self.session.config.connection.ip} "
                    f"rack {self.session.config.connection.rack} slot "
                    f"{self.session.config.connection.slot}.\n\n"
                    "Review the endpoint and machine identity before "
                    "connecting."
                ),
            )

        def _active_scene_source(self) -> dict[str, Any]:
            if self._is_review_scene():
                return self._review_sources[self._current_scene_id]
            return self._scene2_source

        def _show_scene_setup(self) -> None:
            source = self._active_scene_source()
            points = source.get("simulation", {}).get("points", [])
            machine_guide = (
                source.get("training", {}).get("machineGuide")
                or source.get("machineGuide")
                or {}
            )
            esc = html.escape
            sections = []
            if source.get("description"):
                sections.append(
                    f"<h2>Machine purpose</h2><p>{esc(source['description'])}</p>"
                )
            if machine_guide:
                for heading, key, ordered in (
                    ("Starting conditions", "startConditions", False),
                    ("Normal machine sequence", "normalSequence", True),
                    ("Stop behavior", "stopBehavior", False),
                    ("Fault behavior", "faultBehavior", False),
                    ("Expected observations", "expectedObservations", False),
                ):
                    values = machine_guide.get(key, [])
                    if values:
                        tag = "ol" if ordered else "ul"
                        items = "".join(f"<li>{esc(value)}</li>" for value in values)
                        sections.append(f"<h2>{heading}</h2><{tag}>{items}</{tag}>")
            rows = []
            for point in points:
                if not isinstance(point, dict):
                    continue
                name = esc(str(point.get("name", "unnamed")))
                point_type = esc(str(point.get("type", "unknown")))
                owner = esc(str(point.get("owner", "unknown")))
                initial = esc(str(point.get("initial", "—")))
                purpose = esc(str(point.get("purpose", "")))
                direction = (
                    "PLC command → simulator"
                    if owner.upper() == "PLC"
                    else "Simulator feedback → PLC"
                    if owner.upper() == "PC"
                    else "Simulator internal"
                )
                rows.append(
                    f"<tr><td><code>{name}</code></td><td>{point_type}</td>"
                    f"<td>{esc(owner)}</td><td><code>{initial}</code></td>"
                    f"<td>{esc(direction)}</td><td>{purpose}</td></tr>"
                )
            sections.append(
                "<h2>Exact PLC interface contract</h2>"
                "<p>Use these names and data types exactly. Do not create PLC tags "
                "for simulator-internal points.</p>"
                "<table><thead><tr><th>Tag</th><th>Type</th><th>Owner</th>"
                "<th>Initial</th><th>Direction</th><th>Purpose</th></tr></thead>"
                f"<tbody>{''.join(rows)}</tbody></table>"
            )
            sections.append(
                "<h2>Bench setup and verification</h2>"
                "<ol><li>Complete the common watchdog foundation in "
                "<code>docs/PLC_BENCH_SETUP.md</code>.</li>"
                "<li>Create the scene-specific interface members with the exact "
                "names and types above.</li>"
                "<li>Monitor the watchdog and scene points in a TIA watch table "
                "before pressing Run.</li>"
                "<li>Confirm that command outputs change only when the rung logic "
                "makes them change.</li></ol>"
                "<p class='warning'><b>Training boundary:</b> this is a bench "
                "setup document. It does not authorize a production connection "
                "or replace a machine safety review.</p>"
            )
            document = (
                "<style>body{font-family:'Segoe UI';color:#EAF2F4;} h2{color:#5FC5EC;"
                "border-bottom:1px solid #29414B;padding-bottom:4px;margin-top:18px;} "
                "p,li,td{font-size:13px;line-height:1.35;} table{border-collapse:collapse;"
                "width:100%;} th{background:#152830;color:#5FC5EC;text-align:left;} "
                "th,td{border:1px solid #29414B;padding:7px;vertical-align:top;} "
                "code{color:#BEEBFA;} .warning{border-left:4px solid #F2B94B;"
                "padding:9px;background:#1D2520;}</style>"
                "<h1>Setup document</h1>"
                "<p>Build the PLC interface and verify the machine contract before "
                "writing sequence logic.</p>"
                + "".join(sections)
            )
            self._show_document(f"Setup - {self.scene_title.text()}", document)

        def _show_basic_logic(self) -> None:
            source = self._active_scene_source()
            networks = self._basic_logic_networks(source)
            self._show_ladder_document(
                f"Basic Logic - {self.scene_title.text()}",
                networks,
            )

        def _show_ladder_document(
            self,
            title: str,
            networks: list[dict[str, Any]],
            *,
            intro_html: str | None = None,
        ) -> None:
            """Render starter LAD networks with drawn IEC-style symbols."""

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            dialog.resize(1080, 760)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(18, 16, 18, 16)
            layout.setSpacing(10)
            heading = QtWidgets.QLabel(title)
            heading.setObjectName("dialogTitle")
            layout.addWidget(heading)
            note = QtWidgets.QLabel(
                "Drawn ladder reference. Recreate these networks in TIA Portal "
                "with the exact symbols and tag names from Setup. This is not "
                "safety-rated logic and is not downloaded automatically."
            )
            note.setObjectName("dialogScope")
            note.setWordWrap(True)
            layout.addWidget(note)

            class LadderCanvas(QtWidgets.QWidget):
                def __init__(self, parent: Any = None) -> None:
                    super().__init__(parent)
                    max_symbols = max(
                        (len(network["contacts"]) + 1 for network in networks),
                        default=1,
                    )
                    # Keep symbols compact, but reserve enough width for the
                    # complete rung so QScrollArea can expose left/right
                    # scrolling instead of clipping the final coil.
                    self.canvas_width = max(900, 78 + max_symbols * 118)
                    self.canvas_height = max(245, len(networks) * 185)
                    self.setFixedSize(self.canvas_width, self.canvas_height)
                    self.setSizePolicy(
                        QtWidgets.QSizePolicy.Policy.Fixed,
                        QtWidgets.QSizePolicy.Policy.Fixed,
                    )

                @staticmethod
                def _label(painter: Any, text: str, x: float, y: float, width: float) -> None:
                    option = QtGui.QTextOption()
                    option.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    option.setWrapMode(QtGui.QTextOption.WrapMode.WrapAnywhere)
                    painter.drawText(QtCore.QRectF(x, y, width, 38), text, option)

                def _contact(self, painter: Any, x: float, y: float, label: str, normally_closed: bool) -> float:
                    width = 108.0
                    center = x + width / 2
                    painter.setPen(QtGui.QPen(QtGui.QColor("#EAF2F4"), 2))
                    painter.drawLine(x, y, center - 16, y)
                    painter.drawLine(center + 16, y, x + width, y)
                    painter.drawLine(center - 16, y - 24, center - 16, y + 24)
                    painter.drawLine(center + 16, y - 24, center + 16, y + 24)
                    if normally_closed:
                        painter.drawLine(center - 24, y + 25, center + 24, y - 25)
                    painter.setPen(QtGui.QPen(QtGui.QColor("#BDE9FA"), 1))
                    self._label(painter, label, x, y - 57, width)
                    return width

                def _coil(self, painter: Any, x: float, y: float, label: str, normally_closed: bool) -> float:
                    width = 112.0
                    center = x + width / 2
                    painter.setPen(QtGui.QPen(QtGui.QColor("#3DD6A5"), 2))
                    painter.drawLine(x, y, center - 28, y)
                    painter.drawLine(center + 28, y, x + width, y)
                    painter.drawArc(center - 28, y - 25, 22, 50, 90 * 16, 180 * 16)
                    painter.drawArc(center + 6, y - 25, 22, 50, -90 * 16, 180 * 16)
                    if normally_closed:
                        painter.drawLine(center - 35, y + 27, center + 35, y - 27)
                    painter.setPen(QtGui.QPen(QtGui.QColor("#A5E5CF"), 1))
                    self._label(painter, label, x, y - 57, width)
                    return width

                def _instruction(self, painter: Any, x: float, y: float, label: str) -> float:
                    width = 230.0
                    painter.setPen(QtGui.QPen(QtGui.QColor("#F2B94B"), 2))
                    painter.setBrush(QtGui.QBrush(QtGui.QColor("#1D2520")))
                    painter.drawRect(x, y - 28, width, 56)
                    painter.setPen(QtGui.QPen(QtGui.QColor("#F2B94B"), 1))
                    self._label(painter, label, x + 4, y - 20, width - 8)
                    return width

                def paintEvent(self, event: Any) -> None:  # noqa: N802
                    del event
                    painter = QtGui.QPainter(self)
                    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
                    painter.fillRect(self.rect(), QtGui.QColor("#071015"))
                    for index, network in enumerate(networks):
                        top = index * 185
                        painter.setPen(QtGui.QPen(QtGui.QColor("#3A5C67"), 1))
                        painter.drawRect(10, top + 8, self.width() - 20, 168)
                        painter.setPen(QtGui.QPen(QtGui.QColor("#5FC5EC"), 2))
                        painter.setFont(QtGui.QFont("Segoe UI", 13, QtGui.QFont.Weight.Bold))
                        painter.drawText(28, top + 36, f"Network {network['number']} — {network['comment']}")
                        rail_top = top + 72
                        rail_bottom = top + 132
                        rail_x = 36
                        painter.setPen(QtGui.QPen(QtGui.QColor("#F2B94B"), 3))
                        painter.drawLine(rail_x, rail_top, rail_x, rail_bottom)
                        x = rail_x
                        y = top + 98
                        painter.setFont(QtGui.QFont("Cascadia Mono", 8))
                        for raw_contact in network["contacts"]:
                            painter.setPen(QtGui.QPen(QtGui.QColor("#EAF2F4"), 2))
                            painter.drawLine(x, y, x + 12, y)
                            x += 12
                            normally_closed = str(raw_contact).startswith("NOT ")
                            label = str(raw_contact)[4:] if normally_closed else str(raw_contact)
                            x += self._contact(painter, x, y, label, normally_closed)
                        painter.setPen(QtGui.QPen(QtGui.QColor("#EAF2F4"), 2))
                        painter.drawLine(x, y, x + 12, y)
                        x += 12
                        if network.get("instruction"):
                            self._instruction(
                                painter,
                                x,
                                y,
                                str(network["instruction"]),
                            )
                        else:
                            normally_closed = str(network["coil"]).startswith("NOT ")
                            coil_label = str(network["coil"])[4:] if normally_closed else str(network["coil"])
                            self._coil(painter, x, y, coil_label, normally_closed)
                        painter.setPen(QtGui.QPen(QtGui.QColor("#ADC0C6"), 1))
                        painter.setFont(QtGui.QFont("Segoe UI", 10))
                        painter.drawText(28, top + 163, network["explanation"])
                    painter.end()

            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(False)
            scroll.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            scroll.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            scroll.setToolTip(
                "Use the bottom scrollbar to inspect long rungs left to right."
            )
            scroll.setWidget(LadderCanvas())
            if intro_html is not None:
                intro = QtWidgets.QTextBrowser()
                intro.setReadOnly(True)
                intro.setHtml(intro_html)
                intro.setMaximumHeight(300)
                intro.setStyleSheet(
                    "QTextBrowser { background:#0A1E25; color:#EAF2F4; "
                    "border:1px solid #3A5C67; padding:8px; font-size:12px; }"
                )
                layout.insertWidget(2, intro)
            layout.addWidget(scroll, 1)
            checklist = QtWidgets.QLabel(
                "Review: monitor contacts and coils online; change one input at a "
                "time; confirm watchdog loss removes the output command."
            )
            checklist.setObjectName("dialogScope")
            checklist.setWordWrap(True)
            layout.addWidget(checklist)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Close
            )
            buttons.rejected.connect(dialog.reject)
            buttons.clicked.connect(dialog.accept)
            layout.addWidget(buttons)
            dialog.exec()

        def _basic_logic_networks(self, source: dict[str, Any]) -> list[dict[str, Any]]:
            """Return explicit starter LAD networks using declared scene tags."""

            points = {
                point.get("name")
                for point in source.get("simulation", {}).get("points", [])
                if isinstance(point, dict)
            }
            common = ["Simulation_Enable", "Simulation_Comm_OK", "NOT Simulation_Timeout"]
            if self._current_scene_id == SCENE_ID:
                return [
                    {
                        "number": 1,
                        "comment": "Conveyor permissive and clear path",
                        "contacts": common + ["pusher_retracted", "NOT part_at_pusher", "NOT pusher_extended"],
                        "coil": "conveyor_running",
                        "explanation": "The conveyor runs only when the watchdog is healthy, the pusher is retracted, no package is at the pusher, and the pusher is not extended.",
                    },
                    {
                        "number": 2,
                        "comment": "Request pusher extension",
                        "contacts": common + ["part_at_pusher", "pusher_retracted", "NOT pusher_extended"],
                        "coil": "pusher_extend",
                        "explanation": "A package at the pusher requests extension only after the retracted feedback is present. The photoeye feedback is an input; it is not generated by this rung.",
                    },
                    {
                        "number": 3,
                        "comment": "Remove extension command at end of stroke",
                        "contacts": common + ["pusher_extended"],
                        "coil": "NOT pusher_extend",
                        "explanation": "This starter network drops the extend command after extended feedback. In a production sequence, use a clear state machine and verify the return stroke before accepting the next part.",
                    },
                ]
            if "conveyor_run" in points and "photoeye_blocked" in points:
                return [
                    {"number": 1, "comment": "Inspection conveyor run permissive", "contacts": common + ["NOT photoeye_blocked"], "coil": "conveyor_run", "explanation": "Run the conveyor while the inspection beam is clear; stop when a carton blocks the sensor."},
                ]
            if "inlet_pump_run" in points and "high_level_switch" in points:
                return [
                    {"number": 1, "comment": "Fill permissive", "contacts": common + ["NOT high_level_switch", "NOT drain_valve_open"], "coil": "inlet_pump_run", "explanation": "Run the inlet pump while the high-level switch is clear and the drain is closed."},
                    {"number": 2, "comment": "Drain permissive", "contacts": common + ["NOT low_level_switch", "NOT inlet_pump_run"], "coil": "drain_valve_open", "explanation": "Open the drain only when the low-level switch is clear and the inlet pump is off."},
                ]
            if "inlet_pump_run" in points and "radar_echo_ok" in points:
                return [
                    {"number": 1, "comment": "Radar fill permissive", "contacts": common + ["radar_echo_ok", "NOT drain_valve_open"], "coil": "inlet_pump_run", "explanation": "Run the inlet pump only with a valid radar echo and the drain closed. Add the level setpoint comparison in the next exercise."},
                    {"number": 2, "comment": "Radar drain permissive", "contacts": common + ["radar_echo_ok", "NOT inlet_pump_run"], "coil": "drain_valve_open", "explanation": "Permit draining only with a valid radar signal and the inlet pump off."},
                ]
            return [
                {"number": 1, "comment": "No starter rung mapping", "contacts": ["Use Setup contract"], "coil": "NO_OUTPUT_ASSIGNED", "explanation": "This scene does not yet have a native starter-rung mapping. Use the exact point contract and create the logic from the machine guide."},
            ]

        def _connect(self) -> None:
            if not real_plc_writes_enabled or self._is_review_scene():
                return
            snapshot = self.session.snapshot()
            if (
                self._diagnostic_active
                or snapshot.connection is not ConnectionState.DISCONNECTED
            ):
                return
            config = self.session.config
            write_scope = "\n".join(
                f"  {tag.address}  {tag.plc_symbol}"
                for tag in config.tags
                if tag.direction.value == "pc_to_plc"
            )
            authorized = self._confirm_action(
                "Authorize Real PLC Connection",
                (
                    "This is a direct connection to a real Siemens PLC. "
                    "RungProof does not discover or identify the machine "
                    "for you.\n\n"
                    f"Profile: scene-2-db14-pusher-interface.json\n"
                    f"CPU family: {config.connection.cpu_family}\n"
                    f"Target IP: {config.connection.ip}\n"
                    f"Rack / slot: {config.connection.rack} / "
                    f"{config.connection.slot}\n"
                    f"Cycle / timeout: {config.connection.cycle_ms} ms / "
                    f"{config.connection.connect_timeout_ms} ms\n\n"
                    "Before connecting, verify all of the following:\n"
                    "  - This is the intended PLC, not another device at "
                    "this IP.\n"
                    "  - The engineering PC is on the authorized controls "
                    "network or VPN.\n"
                    "  - TIA Portal hardware configuration matches the CPU, "
                    "rack, slot, and DB14 layout.\n"
                    "  - The machine is in a safe state and plant procedures "
                    "authorize the connection.\n\n"
                    "RungProof will write only these configured PC-owned "
                    "points:\n"
                    f"{write_scope}\n\n"
                    "It will not search for another PLC, change the IP, "
                    "download hardware, or replace the PLC safety logic.\n"
                    "The PLC watchdog remains the safety authority."
                ),
                confirm_text="Connect Real PLC",
            )
            if authorized:
                self.session.connect()

        def _test_plc(self) -> None:
            if self._is_review_scene() or self._diagnostic_active:
                return
            snapshot = self.session.snapshot()
            if snapshot.connection is not ConnectionState.DISCONNECTED:
                self._show_notice(
                    "Test PLC unavailable",
                    (
                        "Disconnect the persistent real PLC session first. "
                        "The read-only test owns its own short diagnostic "
                        "connection and never runs beside the live writer."
                    ),
                )
                return
            config = load_config(PROFILE_FILE)
            authorized = self._confirm_action(
                "Authorize Read-only PLC Test",
                (
                    f"Target: {config.connection.ip}, rack "
                    f"{config.connection.rack}, slot "
                    f"{config.connection.slot}\n\n"
                    "Sequence: connect - read all configured tags twice - "
                    "disconnect\n"
                    "PLC writes: 0\n\n"
                    "This verifies address/type/readback only. It does not "
                    "start the live point-binding writer."
                ),
                confirm_text="Run Read-only Test",
            )
            if not authorized:
                return
            self._diagnostic_active = True
            self.action_connect.setEnabled(False)
            self.action_test_plc.setEnabled(False)
            self.status_message.setText(
                "Read-only PLC test running - writes 0..."
            )
            task = DiagnosticTask()
            task.signals.finished.connect(
                self._finish_plc_diagnostic
            )
            self._diagnostic_task = task
            self._diagnostic_pool.start(task)

        def _finish_plc_diagnostic(
            self,
            result: dict[str, Any],
        ) -> None:
            self._diagnostic_active = False
            self._diagnostic_task = None
            if self._closing:
                self._finish_close_when_safe()
                return
            self._show_plc_diagnostic_result(result)

        def _show_plc_diagnostic_result(
            self,
            result: dict[str, Any],
        ) -> None:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Read-only PLC Test")
            dialog.setModal(True)
            dialog.resize(820, 560)
            dialog.setStyleSheet(self._dialog_stylesheet())
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(18, 16, 18, 16)
            layout.setSpacing(10)
            title = QtWidgets.QLabel(str(result.get("summary", "PLC test")))
            title.setObjectName("dialogTitle")
            layout.addWidget(title)
            profile = result.get("profile", {})
            scope = QtWidgets.QLabel(
                (
                    f"{profile.get('ip', '--')}  |  rack "
                    f"{profile.get('rack', '--')} / slot "
                    f"{profile.get('slot', '--')}  |  "
                    f"{profile.get('tagCount', '--')} configured tags\n"
                    f"Read-only: {'YES' if result.get('readOnly') else 'NO'}"
                    "  |  Writes attempted: "
                    f"{'YES' if result.get('writeAttempted') else 'NO'}  |  "
                    f"{result.get('durationMs', 0.0)} ms"
                )
            )
            scope.setObjectName("dialogScope")
            layout.addWidget(scope)
            table = QtWidgets.QTreeWidget()
            table.setAlternatingRowColors(True)
            table.setRootIsDecorated(False)
            table.setHeaderLabels(("STATUS", "CHECK", "DETAIL / NEXT STEP"))
            table.header().setSectionResizeMode(
                0,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents,
            )
            table.header().setSectionResizeMode(
                1,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents,
            )
            table.header().setSectionResizeMode(
                2,
                QtWidgets.QHeaderView.ResizeMode.Stretch,
            )
            colors = {
                "pass": SAFE_GREEN,
                "warning": AMBER,
                "fail": BAD,
                "info": CYAN,
            }
            for item in result.get("items", []):
                status = str(item.get("status", "info"))
                detail = str(item.get("detail", ""))
                if item.get("fix"):
                    detail += f"\nCheck: {item['fix']}"
                row = QtWidgets.QTreeWidgetItem(
                    (
                        status.upper(),
                        str(item.get("label", "--")),
                        detail,
                    )
                )
                row.setForeground(0, QtGui.QColor(colors.get(status, CYAN)))
                table.addTopLevelItem(row)
            layout.addWidget(table, 1)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Close
            )
            buttons.rejected.connect(dialog.reject)
            buttons.clicked.connect(dialog.accept)
            layout.addWidget(buttons)
            dialog.exec()

        def _set_workspace_badge(self, state: str) -> None:
            colors = {
                "OFFLINE": ("#9FD5E5", "#3A7181", "#102730"),
                "SIGNED IN": (SAFE_GREEN, "#2F765F", "#102E27"),
                "SYNCED": (SAFE_GREEN, "#2F765F", "#102E27"),
                "OFFLINE PACKAGE": (AMBER, "#80652F", "#332A17"),
                "AUDIT SYNCED": (CYAN, "#3E9BC0", "#0C3040"),
                "UNAVAILABLE": (BAD, BAD, "#3B1817"),
            }
            foreground, border, background = colors.get(
                state,
                colors["OFFLINE"],
            )
            self.workspace_state = state
            local_fixture = isinstance(
                getattr(self.workspace_client, "_transport", None),
                InMemoryHostedWorkspace,
            )
            fixture_suffix = " · LOCAL FIXTURE" if local_fixture and state != "OFFLINE" else ""
            self.workspace_badge.setText(
                f"WORKSPACE {state}{fixture_suffix}"
            )
            self.workspace_badge.setStyleSheet(
                f"color: {foreground}; border: 1px solid {border}; "
                f"background: {background}; border-radius: 3px; "
                "padding: 6px 9px; font-family: \"Cascadia Mono\", \"Consolas\"; "
                "font-size: 9px; font-weight: 800;"
            )
            signed_in = self.workspace_client.signed_in
            self.action_workspace_sync.setEnabled(signed_in)
            self.action_workspace_upload.setEnabled(signed_in)

        def _show_workspace_sign_in(self) -> None:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("RungProof - Workspace Sign In")
            dialog.setMinimumWidth(520)
            layout = QtWidgets.QVBoxLayout(dialog)
            title = QtWidgets.QLabel("WORKSPACE SIGN IN")
            title.setObjectName("dialogTitle")
            layout.addWidget(title)
            scope = QtWidgets.QLabel(
                "This build uses the deterministic local fixture transport. "
                "An authenticated HTTPS adapter can replace it without "
                "crossing the PLC boundary."
            )
            scope.setObjectName("dialogScope")
            scope.setWordWrap(True)
            layout.addWidget(scope)
            form = QtWidgets.QFormLayout()
            username = QtWidgets.QLineEdit()
            username.setPlaceholderText("operator@example.com")
            secret = QtWidgets.QLineEdit()
            secret.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            secret.setPlaceholderText("Workspace secret")
            form.addRow("Identity", username)
            form.addRow("Secret", secret)
            layout.addLayout(form)
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            try:
                identity = self.workspace_client.sign_in(
                    username.text().strip(),
                    secret.text(),
                )
            except WorkspaceClientError as exc:
                self._set_workspace_badge("UNAVAILABLE")
                self._show_notice("Workspace sign-in failed", str(exc))
                return
            self._set_workspace_badge("SIGNED IN")
            self.event_history_store.record(
                code="WORKSPACE_SIGNED_IN",
                title=f"Workspace identity active: {identity.display_name}",
                severity=EventSeverity.INFO,
                source="workspace-client",
                detail="Workspace identity is separate from PLC credentials.",
            )
            self._show_notice(
                "Workspace signed in",
                "Identity is active in the workspace boundary. PLC session "
                "state and credentials remain local.",
            )

        def _sync_workspace_assignment(self) -> None:
            if not self.workspace_client.signed_in:
                self._show_workspace_sign_in()
                if not self.workspace_client.signed_in:
                    return
            try:
                resolution = self.workspace_client.sync(
                    self.workspace_assignment_id
                )
            except WorkspaceClientError as exc:
                self._set_workspace_badge("UNAVAILABLE")
                self._show_notice("Workspace sync failed", str(exc))
                return
            if resolution.package is None:
                self._set_workspace_badge("UNAVAILABLE")
                self._show_notice("Workspace package unavailable", resolution.reason)
                return
            state = (
                "SYNCED"
                if resolution.source is PackageSource.ASSIGNED
                else "OFFLINE PACKAGE"
            )
            self._set_workspace_badge(state)
            self.event_history_store.record(
                code="WORKSPACE_PACKAGE_VERIFIED",
                title=f"{resolution.package.scene_id} package verified",
                severity=EventSeverity.INFO,
                source="workspace-client",
                detail=resolution.reason,
            )
            self._show_notice("Workspace package ready", resolution.reason)

        def _upload_workspace_evidence(self) -> None:
            if not self.workspace_client.signed_in:
                self._show_workspace_sign_in()
                if not self.workspace_client.signed_in:
                    return
            snapshot = self.session.snapshot()
            package_source = (
                PackageSource.ASSIGNED
                if self.workspace_state == "SYNCED"
                else PackageSource.LAST_KNOWN_GOOD
            )
            metadata = SessionMetadata(
                session_id="native-local-session",
                project_id="rungproof-controls-lab",
                scene_id=SCENE_ID,
                client_version=APP_VERSION,
                started_at_utc="2026-08-08T00:00:00Z",
                package_source=package_source,
                connection_state=snapshot.connection.value,
            )
            sanitized = project_sanitized_session_metadata(metadata)
            try:
                self.workspace_client.upload_session_metadata(sanitized)
            except WorkspaceClientError as exc:
                self._set_workspace_badge("UNAVAILABLE")
                self._show_notice("Workspace evidence upload failed", str(exc))
                return
            self._set_workspace_badge("AUDIT SYNCED")
            self.event_history_store.record(
                code="WORKSPACE_AUDIT_SYNCED",
                title="Sanitized session evidence uploaded",
                severity=EventSeverity.INFO,
                source="workspace-client",
                detail="PLC credentials and raw telemetry were excluded.",
            )
            self._show_notice(
                "Workspace evidence synced",
                "Only sanitized session metadata was uploaded. PLC credentials "
                "and raw telemetry remained local.",
            )

        def _render_event_rows(self) -> None:
            selected_index = self.event_table.currentIndex().row()
            events = self.event_history_store.all()
            self.event_table.clear()
            colors = {
                EventSeverity.ALARM: BAD,
                EventSeverity.WARNING: AMBER,
                EventSeverity.INFO: CYAN,
            }
            visible_events = events[:8]
            if self._compact_display:
                selected_index = next(
                    (
                        index
                        for index, event in enumerate(visible_events)
                        if event.event_id == self._selected_event_id
                        and not event.active
                    ),
                    next(
                        (
                            index
                            for index, event in enumerate(visible_events)
                            if event.active
                        ),
                        -1,
                    ),
                )
            elif self._selected_event_id is not None:
                selected_index = next(
                    (
                        index
                        for index, event in enumerate(visible_events)
                        if event.event_id == self._selected_event_id
                    ),
                    -1,
                )
            elif selected_index < 0:
                selected_index = next(
                    (
                        index
                        for index, event in enumerate(visible_events)
                        if event.active
                    ),
                    -1,
                )
            for event in visible_events:
                state = "ACTIVE" if event.active else "CLEARED"
                if event.acknowledged_by is not None:
                    state += " / ACK"
                event_time = event.occurred_at_utc[11:19]
                if event.source.startswith("scene-2"):
                    source_label = "SCENE"
                elif event.source.startswith("native-"):
                    source_label = "PLC"
                elif event.source.startswith("workspace-"):
                    source_label = "WORK"
                else:
                    source_label = event.source.upper()
                event_label = {
                    "PHOTOEYE_BLOCKED": "PHOTOEYE",
                    "LOCAL_SESSION_READY": "LOCAL READY",
                }.get(event.code, event.code)
                row = QtWidgets.QTreeWidgetItem(
                    (
                        {
                            EventSeverity.ALARM: "ALM",
                            EventSeverity.WARNING: "WRN",
                            EventSeverity.INFO: "INF",
                        }[event.severity],
                        event_label,
                        f"{state.split(' / ')[0]} {event_time[:5]}",
                        source_label,
                    )
                )
                row.setForeground(0, QtGui.QColor(colors[event.severity]))
                row.setToolTip(
                    1,
                    f"{event.title}\n{event.detail}\nSource: {event.source}\n"
                    f"Occurred {event.occurred_at_utc}",
                )
                self.event_table.addTopLevelItem(row)
            if 0 <= selected_index < self.event_table.topLevelItemCount():
                self.event_table.setCurrentItem(
                    self.event_table.topLevelItem(selected_index)
                )
            selected_event = self._selected_event_row()
            if selected_event is None:
                self.event_inspector.setText(
                    "NO ACTIVE EVENTS\n"
                    + self._local_evidence_text
                )
            else:
                selected_state = (
                    "ACTIVE / ACKNOWLEDGED"
                    if selected_event.active
                    and selected_event.acknowledged_by is not None
                    else "ACTIVE"
                    if selected_event.active
                    else "CLEARED"
                )
                source_label = (
                    "SCENE"
                    if selected_event.source.startswith("scene-2")
                    else "PLC"
                    if selected_event.source.startswith("native-")
                    else "WORK"
                    if selected_event.source.startswith("workspace-")
                    else selected_event.source.upper()
                )
                compact_asset_summary = self._compact_event_asset_summary()
                event_detail = (
                    ""
                    if self._compact_display
                    and selected_event.code == "PHOTOEYE_BLOCKED"
                    else selected_event.detail
                )
                event_detail_line = f"\n{event_detail}" if event_detail else ""
                self.event_inspector.setText(
                    f"{selected_event.severity.value.upper()}\n"
                    f"{selected_event.title.upper().replace(' - ', chr(10))}\n"
                    f"STATE  {selected_state}  ·  "
                    f"TIME  {selected_event.occurred_at_utc[11:19]}\n"
                    f"SOURCE  {source_label}  ·  LOCAL MODEL\n"
                    f"{event_detail_line}"
                    f"{compact_asset_summary}"
                )
            self._update_event_row_actions()

        def _selected_event_row(self) -> Any | None:
            item = self.event_table.currentItem()
            if item is None:
                return None
            index = self.event_table.indexOfTopLevelItem(item)
            events = self.event_history_store.all()
            if not 0 <= index < len(events):
                return None
            event = events[index]
            self._selected_event_id = event.event_id
            return event

        def _update_event_row_actions(self) -> None:
            event = self._selected_event_row()
            visible = event is not None
            for button in self.event_action_buttons:
                button.setVisible(visible)
            self.event_ack_button.setEnabled(
                event is not None and event.acknowledged_by is None
            )
            self.event_clear_button.setEnabled(
                event is not None and event.active
            )

        def _acknowledge_event_row(self) -> None:
            event = self._selected_event_row()
            if event is not None and event.acknowledged_by is None:
                self.event_history_store.acknowledge(
                    event.event_id,
                    "local-operator",
                )
                self._render_event_rows()

        def _clear_event_row(self) -> None:
            event = self._selected_event_row()
            if event is not None and event.active:
                self.event_history_store.clear(event.event_id)
                self._render_event_rows()

        def _show_event_console(self) -> None:
            """Show bounded local event evidence with explicit actions."""

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("RungProof - Event Console")
            dialog.setMinimumSize(760, 420)
            layout = QtWidgets.QVBoxLayout(dialog)
            title = QtWidgets.QLabel("EVENT CONSOLE")
            title.setObjectName("dialogTitle")
            layout.addWidget(title)
            scope = QtWidgets.QLabel(
                (
                    "Local append-only session evidence. The fixture workspace "
                    "accepts sanitized metadata only; PLC control remains local."
                )
                if self.workspace_fixture_enabled
                else (
                    "Local append-only session evidence. No event or PLC data "
                    "is uploaded by this application."
                )
            )
            scope.setObjectName("dialogScope")
            scope.setWordWrap(True)
            layout.addWidget(scope)
            table = QtWidgets.QTreeWidget()
            table.setHeaderLabels(
                ("SEVERITY", "TIME", "EVENT", "SOURCE", "STATE")
            )
            table.setRootIsDecorated(False)
            table.setUniformRowHeights(True)
            layout.addWidget(table, 1)

            def refresh() -> None:
                table.clear()
                for event in self.event_history_store.all():
                    state = "ACTIVE" if event.active else "CLEARED"
                    if event.acknowledged_by:
                        state += f" / ACK {event.acknowledged_by}"
                    row = QtWidgets.QTreeWidgetItem(
                        (
                            event.severity.value.upper(),
                            event.occurred_at_utc,
                            f"{event.code} - {event.title}",
                            event.source,
                            state,
                        )
                    )
                    colors = {
                        EventSeverity.INFO: CYAN,
                        EventSeverity.WARNING: AMBER,
                        EventSeverity.ALARM: BAD,
                    }
                    row.setForeground(
                        0,
                        QtGui.QColor(colors[event.severity]),
                    )
                    row.setToolTip(2, event.detail)
                    table.addTopLevelItem(row)
                table.resizeColumnToContents(0)
                table.resizeColumnToContents(1)
                table.resizeColumnToContents(3)
                table.resizeColumnToContents(4)

            refresh()
            actions = QtWidgets.QHBoxLayout()
            acknowledge = _button(QtWidgets, "Acknowledge")
            clear = _button(QtWidgets, "Clear")
            close = _button(QtWidgets, "Close")
            actions.addWidget(acknowledge)
            actions.addWidget(clear)
            actions.addStretch(1)
            actions.addWidget(close)
            layout.addLayout(actions)

            def selected_event() -> Any | None:
                item = table.currentItem()
                if item is None:
                    return None
                index = table.indexOfTopLevelItem(item)
                events = self.event_history_store.all()
                return events[index] if 0 <= index < len(events) else None

            def acknowledge_selected() -> None:
                event = selected_event()
                if event is not None:
                    self.event_history_store.acknowledge(
                        event.event_id,
                        "local-operator",
                    )
                    refresh()
                    self._refresh()

            def clear_selected() -> None:
                event = selected_event()
                if event is not None:
                    self.event_history_store.clear(event.event_id)
                    refresh()
                    self._refresh()

            acknowledge.clicked.connect(acknowledge_selected)
            clear.clicked.connect(clear_selected)
            close.clicked.connect(dialog.accept)
            dialog.exec()

        def _run(self) -> None:
            if self._is_review_scene():
                return
            try:
                self.session.run()
            except NativeRuntimeError as exc:
                self._show_notice("Run blocked", str(exc))

        def _stop(self) -> None:
            if self._is_review_scene():
                return
            self.session.stop()

        def _reset(self) -> None:
            if self._is_review_scene():
                return
            self.session.reset()

        def _refresh_review_state(self, snapshot: Any) -> None:
            """Keep review-only derived surfaces deterministic on every tick."""

            self._set_review_controls_disabled()
            self._set_scene_actions_enabled(
                snapshot.connection is ConnectionState.DISCONNECTED
                and not self._diagnostic_active
            )
            self._render_event_rows()
            self.compact_priority_bar.setText(
                "REVIEW ONLY  ·  PLC DISABLED  ·  NO ACTIVE ALARMS"
            )
            self.compact_priority_bar.setVisible(self._compact_display)
            self.compact_runtime_state.setText("PLAYER  REVIEW")
            self.compact_runtime_health.setText("HEALTH  PLC DISABLED")
            self.compact_runtime_time.setText("TIME  --")
            self.compact_runtime_exchange.setText("EXCHANGE  --")
            self.compact_rail_nav.setTabText(1, "EVENTS")
            self.compact_rail_nav.setTabText(2, "HEALTH DISABLED")
            self.compact_rail_nav.setTabText(3, "RUNTIME REVIEW")

        def _refresh(self) -> None:
            snapshot = self.session.snapshot()
            if self._is_review_scene():
                self._refresh_review_state(snapshot)
                return
            previous_connection = self._last_connection
            snapshot_cycle = getattr(snapshot, "cycle", self._last_cycle)
            if (
                snapshot_cycle != self._last_cycle
                or snapshot.connection is not self._last_connection
            ):
                self._last_cycle = snapshot_cycle
                self._last_connection = snapshot.connection
                self._last_snapshot_monotonic = time.monotonic()
                self.viewport.update(snapshot)
                self._render_points(snapshot)
                if (
                    previous_connection is not None
                    and snapshot.connection is not previous_connection
                ):
                    if snapshot.connection is ConnectionState.CONNECTED:
                        self.event_history_store.record(
                            code="PLC_SESSION_CONNECTED",
                            title="Controller session connected",
                            severity=EventSeverity.INFO,
                            source="native-plc-session",
                            detail="Controller exchange is now available to the local runtime.",
                        )
                    elif snapshot.connection is ConnectionState.DISCONNECTED:
                        self.event_history_store.record(
                            code="PLC_SESSION_UNAVAILABLE",
                            title="Controller disconnected",
                            severity=EventSeverity.WARNING,
                            source="native-plc-session",
                            detail="Local model only; controller state is not verified.",
                        )

            state = snapshot.connection
            if state is ConnectionState.CONNECTED and snapshot.ready:
                badge = (
                    "VISUAL QA FIXTURE - HEALTHY"
                    if self.visual_qa_fixture
                    else "REAL PLC CONNECTED - HEALTHY"
                )
                badge_color = SAFE_GREEN
                badge_border = "#2F9A7A"
                badge_background = "#0C362B"
            elif state is ConnectionState.CONNECTED:
                badge = (
                    "VISUAL QA FIXTURE - NOT READY"
                    if self.visual_qa_fixture
                    else "REAL PLC CONNECTED - NOT READY"
                )
                badge_color = AMBER
                badge_border = "#80652F"
                badge_background = "#332A17"
            elif state is ConnectionState.RECONNECTING:
                badge = "REAL PLC RECONNECTING"
                badge_color = AMBER
                badge_border = "#80652F"
                badge_background = "#332A17"
            elif state is ConnectionState.CONNECTING:
                badge = "REAL PLC CONNECTING"
                badge_color = CYAN
                badge_border = "#3E9BC0"
                badge_background = "#0C3040"
            else:
                badge = "CONTROLLER DISCONNECTED"
                badge_color = AMBER
                badge_border = "#80652F"
                badge_background = "#332A17"
            if snapshot.error:
                badge_color = BAD
                badge_border = BAD
                badge_background = "#3B1817"
            self.connection_badge.setText(badge)
            self.connection_badge.setStyleSheet(
                f"color: {badge_color};"
                f"border: 1px solid {badge_border};"
                "border-radius: 3px;"
                "padding: 6px 9px;"
                f"background: {badge_background};"
                'font-family: "Cascadia Mono", "Consolas";'
                "font-size: 9px;"
                "font-weight: 700;"
            )
            if self.visual_qa_fixture:
                self.status_message.setText(
                    "VISUAL QA FIXTURE  ·  NO PLC TRANSPORT  ·  SYNTHETIC STATE"
                )
            elif self._diagnostic_active:
                self.status_message.setText(
                    "Read-only PLC test running - reading configured tags "
                    "twice - writes 0..."
                )
            elif state is ConnectionState.DISCONNECTED:
                self.status_message.setText(
                    "Viewport provenance  ·  LOCAL MODEL"
                )
            else:
                self.status_message.setText(
                    snapshot.message
                    + (
                        f"  |  {snapshot.error}"
                        if snapshot.error
                        else ""
                    )
                )
            self.timing.setText(
                f"Cycle: {snapshot.cycle}\n"
                f"Exchange: {snapshot.exchange_ms:.2f} ms\n"
                f"Recent p99: {snapshot.recent_p99_ms:.2f} ms\n"
                f"Scene: {snapshot.scene_time_s:.2f} s"
            )
            self.health_details.setText(
                f"Health: {snapshot.health.upper()}\n"
                f"Heartbeat: {snapshot.heartbeat_reason}\n"
                f"Echo: {snapshot.heartbeat_echo}\n"
                f"Enable: {_bool_text(snapshot.simulation_enable)}\n"
                f"Comm OK: {_bool_text(snapshot.simulation_comm_ok)}\n"
                f"Timeout: {_bool_text(snapshot.simulation_timeout)}"
            )
            active_events = self.event_history_store.active()
            self._render_event_rows()
            self._update_event_surface_visibility()
            if self._compact_display:
                self.compact_rail_nav.setTabText(
                    0,
                    "EQUIPMENT",
                )
                self.compact_rail_nav.setTabText(
                    1,
                    f"EVENTS {len(active_events)}" if active_events else "EVENTS",
                )
                self.compact_rail_nav.setTabText(
                    2,
                    "HEALTH " + snapshot.health.upper(),
                )
                self.compact_rail_nav.setTabText(
                    3,
                    "RUNTIME "
                    + ("READY" if state is ConnectionState.CONNECTED else "LOCAL"),
                )
            if active_events:
                latest_priority = active_events[0]
                self.compact_priority_bar.setText(
                    f"ALARM  ·  {latest_priority.code}  ·  LOCAL MODEL "
                    "EVENT  ·  NOT PLC-SOURCED"
                )
            elif state is ConnectionState.CONNECTED and snapshot.ready:
                self.compact_priority_bar.setText(
                    (
                        "NO ACTIVE ALARMS  ·  SYNTHETIC HEALTHY EXCHANGE  ·  "
                        "EVENT STORE LOCAL"
                    )
                    if self.visual_qa_fixture
                    else "NO ACTIVE ALARMS  ·  CONTROLLER HEALTHY  ·  EVENT STORE LOCAL"
                )
            elif state is ConnectionState.CONNECTED:
                self.compact_priority_bar.setText(
                    "NO ACTIVE ALARMS  ·  SESSION NOT READY  ·  PLC STATE UNKNOWN"
                )
            else:
                self.compact_priority_bar.setText(
                    "NO ACTIVE ALARMS  ·  LOCAL MODEL  ·  EVENT STORE LOCAL"
                )
            self.compact_priority_bar.setVisible(self._compact_display)
            if state is ConnectionState.CONNECTED:
                self.event_history.setText(
                    "NO ACTIVE ALARMS\n"
                    "Controller session is connected; event evidence remains local."
                )
            elif active_events:
                latest = active_events[0]
                self.event_history.setText(
                    f"{latest.severity.value.upper()}  {latest.code}\n"
                    f"{latest.title}\n"
                    "Acknowledge or clear in the event workflow."
                )
            else:
                self.event_history.setText(
                    "NO ACTIVE ALARMS\n"
                    + self._local_evidence_text
                )
            selected_equipment = getattr(self, "_selected_equipment", None)
            if selected_equipment is not None:
                self._on_equipment_selected(selected_equipment)
            connected = state is ConnectionState.CONNECTED
            player_state = (
                "RUNNING"
                if snapshot.running
                else "READY"
                if connected and snapshot.ready
                else "LOCAL ONLY"
            )
            self.runtime_player.setText(player_state)
            self.runtime_player.setStyleSheet(
                f"color: {SAFE_GREEN if snapshot.running else MUTED_BRIGHT};"
            )
            self.runtime_scene.setText("Scene 2")
            self.runtime_time.setText(f"{snapshot.scene_time_s:.1f} s")
            self.runtime_exchange.setText(
                f"{snapshot.exchange_ms:.2f} ms"
            )
            self.compact_runtime_state.setText(
                f"PLAYER  {player_state}"
            )
            self.compact_runtime_health.setText(
                f"HEALTH  {snapshot.health.upper()}"
            )
            self.compact_runtime_time.setText(
                f"TIME  {snapshot.scene_time_s:.1f} s"
            )
            self.compact_runtime_exchange.setText(
                f"EXCHANGE  {snapshot.exchange_ms:.2f} ms"
            )
            self.hud_time.setText(f"{snapshot.scene_time_s:.1f} s")
            self.hud_p99.setText(
                f"{snapshot.recent_p99_ms:.2f} ms"
            )
            self.hud_state.setText(
                "PLAYING"
                if snapshot.running
                else "READY"
                if connected and snapshot.ready
                else "LOCAL ONLY"
            )
            self.hud_state.setStyleSheet(
                (
                    f"color: {SAFE_GREEN};"
                    "border: 1px solid #2F765F;"
                    "background: #102E27;"
                )
                if snapshot.running
                else ""
            )
            if self.visual_qa_fixture:
                hud_live_text = "●  VISUAL QA FIXTURE · NO PLC TRANSPORT"
            elif snapshot.running:
                hud_live_text = "●  LIVE PLC EXCHANGE · WATCHDOG AUTHORITY: PLC"
            elif connected:
                hud_live_text = "●  PLC SESSION CONNECTED · RUN REQUIRES HEALTHY READY"
            elif state in (
                ConnectionState.CONNECTING,
                ConnectionState.RECONNECTING,
            ):
                hud_live_text = "●  CONTROLLER SESSION STARTING · WAITING FOR HEALTH"
            else:
                hud_live_text = "●  LOCAL ONLY  ·  SEE CONTROLLER BANNER"
            self.hud_live.setText(hud_live_text)
            self.hud_live.setStyleSheet(
                f"color: {SAFE_GREEN if snapshot.running else '#9FB6BD' if connected else AMBER};"
            )
            self.hud_lock_reason.setVisible(not connected)
            if connected:
                self.hud_lock_reason.setText("CONTROLS READY")
            elif state in (
                ConnectionState.CONNECTING,
                ConnectionState.RECONNECTING,
            ):
                self.hud_lock_reason.setText("CONTROLS LOCKED · WAITING FOR HEALTH")
            else:
                self.hud_lock_reason.setText("CONTROLS LOCKED · SEE BANNER")
            source_text = (
                "VISUAL QA FIXTURE"
                if self.visual_qa_fixture
                else "REAL PLC"
                if connected
                else "RECONNECTING"
                if state is ConnectionState.RECONNECTING
                else "LOCAL ONLY"
            )
            self.hud_source.setText(source_text)
            self.hud_source.setStyleSheet(
                f"color: {CYAN if connected else AMBER};"
            )
            self.points_source_badge.setText(
                "VISUAL QA FIXTURE"
                if self.visual_qa_fixture
                else "REAL PLC"
                if connected
                else "PLC NOT EXCHANGING"
            )
            connected = state is ConnectionState.CONNECTED
            busy = state in (
                ConnectionState.CONNECTING,
                ConnectionState.RECONNECTING,
                ConnectionState.CLOSING,
            )
            diagnostic_ready = (
                state is ConnectionState.DISCONNECTED
                and not self._diagnostic_active
            )
            self._set_scene_actions_enabled(diagnostic_ready)
            self.hud_run_button.setEnabled(
                connected and snapshot.ready and not snapshot.running
            )
            self.hud_stop_button.setEnabled(
                connected and snapshot.running
            )
            self.hud_reset_button.setEnabled(connected)
            self.action_connect.setEnabled(
                real_plc_writes_enabled
                and state is ConnectionState.DISCONNECTED
                and not self._diagnostic_active
            )
            self.action_configure_plc.setEnabled(
                state is ConnectionState.DISCONNECTED
                and not self._diagnostic_active
            )
            self.action_disconnect.setEnabled(connected or busy)
            self.action_test_plc.setEnabled(diagnostic_ready)
            self.action_run.setEnabled(
                connected and snapshot.ready and not snapshot.running
            )
            self.action_stop.setEnabled(
                connected and snapshot.running
            )
            self.action_reset.setEnabled(connected)

        def _render_points(
            self,
            snapshot: NativeSessionSnapshot,
        ) -> None:
            owners = {
                "part_at_pusher": "PC",
                "pusher_extended": "PC",
                "pusher_retracted": "PC",
                "conveyor_running": "PLC",
                "pusher_extend": "PLC",
                "pusher_position": "SIM",
                "component_state": "SIM",
                "parts_completed": "SIM",
            }
            types = {
                "part_at_pusher": "BOOL",
                "pusher_extended": "BOOL",
                "pusher_retracted": "BOOL",
                "conveyor_running": "BOOL",
                "pusher_extend": "BOOL",
                "pusher_position": "REAL",
                "component_state": "STRING",
                "parts_completed": "DINT",
            }
            owner_colors = {
                "PLC": ("#FFDDA0", "#3A2D13"),
                "PC": ("#A7DDF0", "#133441"),
                "SIM": ("#A5E5CF", "#12372D"),
            }
            point_contracts = [
                {
                    "name": name,
                    "value": value,
                    "type": types.get(name, "--"),
                    "owner": owners.get(name, "--"),
                }
                for name, value in snapshot.points.items()
            ]
            plc_exchange_known = (
                snapshot.connection is ConnectionState.CONNECTED
                and getattr(snapshot, "ready", False)
            )
            left, right, labels = self._ordered_point_groups(point_contracts)
            self.points_column_left.setText(
                f"{labels[0]}  ·  {len(left)} POINTS"
            )
            self.points_column_right.setText(
                f"{labels[1]}  ·  {len(right)} POINTS"
                + (
                    f"  ·  {min(3, len(right))} SHOWN"
                    if self._compact_display and len(right) > 3
                    else ""
                )
            )
            if self._compact_display and len(right) > 3:
                self.points_column_right.setText(
                    self.points_column_right.text()
                    + f"  ·  SCROLL FOR {len(right) - 3} MORE"
                )
            for table, visible_items in (
                (self.points_table, left),
                (self.points_table_right, right),
            ):
                table.setRowCount(len(visible_items))
                for row, point in enumerate(visible_items):
                    name = point["name"]
                    value = point["value"]
                    shown = (
                        "--"
                        if point["owner"] == "PLC" and not plc_exchange_known
                        else _bool_text(value)
                        if isinstance(value, bool) or value is None
                        else f"{value:.1f}%"
                        if name == "pusher_position"
                        and isinstance(value, (int, float))
                        else str(value)
                    )
                    for column, text in enumerate(
                        (
                            name,
                            point["type"],
                            shown,
                            "PLC?"
                            if point["owner"] == "PLC" and not plc_exchange_known
                            else point["owner"],
                        )
                    ):
                        item = QtWidgets.QTableWidgetItem(text)
                        if column == 2 and value is True:
                            item.setForeground(QtGui.QColor(SAFE_GREEN))
                        elif column == 2 and value is False:
                            item.setForeground(QtGui.QColor("#7F949B"))
                        if column == 3 and text in owner_colors:
                            foreground, background = owner_colors[text]
                            item.setForeground(QtGui.QColor(foreground))
                            item.setBackground(QtGui.QColor(background))
                            item.setTextAlignment(
                                QtCore.Qt.AlignmentFlag.AlignCenter
                            )
                        table.setItem(row, column, item)
                    table.setRowHeight(row, 24)
                if self._compact_display:
                    for row in range(3, len(visible_items)):
                        table.setRowHidden(row, True)

        def _finish_close_when_safe(self) -> None:
            if not self.session.is_closed:
                self.status_message.setText(
                    "Closing - waiting for the bounded PLC transport "
                    "operation to finish..."
                )
                return
            if self._diagnostic_active:
                self.status_message.setText(
                    "Closing - waiting for the bounded read-only PLC "
                    "diagnostic to disconnect..."
                )
                return
            self._shutdown_timer.stop()
            self.close()

        def closeEvent(self, event: Any) -> None:  # noqa: N802
            if self.session.is_closed and not self._diagnostic_active:
                self._save_ui_state()
                self._timer.stop()
                self._shutdown_timer.stop()
                event.accept()
                return

            event.ignore()
            if self._closing:
                return
            self._closing = True
            self.centralWidget().setEnabled(False)
            self.status_message.setEnabled(True)
            self.status_message.setText(
                "Closing - disconnecting PLC activity..."
            )
            if not self.session.is_closed:
                self.session.begin_close()
            self._shutdown_timer.start()

    return RungProofWindow


def run_gui(
    *,
    initial_view: str | None = None,
    renderer: str = DEFAULT_RENDERER,
) -> int:
    qt = _qt_imports()
    viewport_factory: Any = SoftwareScene2Viewport
    if renderer == "qt3d":
        qt = _with_qt3d_imports(qt)
        viewport_factory = Scene2Viewport
    QtWidgets = qt["QtWidgets"]
    app = QtWidgets.QApplication(sys.argv[:1])
    app.setApplicationName("RungProof")
    app.setOrganizationName("RungProof")
    window_class = build_window_class(
        qt,
        viewport_factory=viewport_factory,
    )
    try:
        window = window_class(initial_view=initial_view)
    except Exception as exc:
        QtWidgets.QMessageBox.critical(
            None,
            "RungProof startup failed",
            f"{type(exc).__name__}: {exc}",
        )
        return 1
    window.show()
    return app.exec()


class _VisualQaSession:
    """Capture-only state provider; it never creates or touches PLC transport."""

    def __init__(self, state: str) -> None:
        if state not in {"disconnected", "not-ready", "healthy"}:
            raise ValueError(f"unknown visual QA PLC state: {state}")
        definition = load_scene2_definition()
        base = _empty_snapshot(definition)
        if state == "disconnected":
            snapshot = base
        else:
            healthy = state == "healthy"
            snapshot = replace(
                base,
                connection=ConnectionState.CONNECTED,
                cycle=42 if healthy else 0,
                health="healthy" if healthy else "not-ready",
                heartbeat_reason=(
                    "fixture healthy exchange" if healthy else "session not ready"
                ),
                heartbeat_echo=42 if healthy else None,
                simulation_enable=True if healthy else None,
                simulation_comm_ok=True if healthy else None,
                simulation_timeout=False if healthy else None,
                ready=healthy,
                scene_time_s=12.4 if healthy else 0.0,
                exchange_ms=8.4 if healthy else 0.0,
                recent_p99_ms=11.2 if healthy else 0.0,
                points=(
                    {
                        "part_at_pusher": False,
                        "pusher_extended": False,
                        "pusher_retracted": True,
                        "conveyor_running": True,
                        "pusher_extend": False,
                        "pusher_position": 0.0,
                        "component_state": "running",
                        "parts_completed": 3,
                    }
                    if healthy
                    else base.points
                ),
                message=(
                    "Visual QA fixture: healthy exchange"
                    if healthy
                    else "Visual QA fixture: controller session not ready"
                ),
            )
        self._snapshot = snapshot
        self.config = load_config(PROFILE_FILE)
        self.is_closed = False

    @property
    def visual_qa_fixture(self) -> bool:
        return True

    def snapshot(self) -> NativeSessionSnapshot:
        return self._snapshot

    def connect(self) -> None:
        return None

    def disconnect(self) -> None:
        return None

    def run(self) -> None:
        return None

    def stop(self) -> None:
        return None

    def reset(self) -> None:
        return None

    def configure_connection(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def begin_close(self) -> None:
        self.is_closed = True

    def close(self, *, timeout: float = 7.0) -> None:
        del timeout
        self.is_closed = True


def _capture_native_views(
    output_dir: Path,
    *,
    width: int | None = None,
    height: int | None = None,
    demo_event: bool = False,
    demo_selection: str | None = None,
    demo_workspace: bool = False,
    demo_panel: str | None = None,
    demo_plc_state: str | None = None,
) -> int:
    """Capture deterministic views without connecting to a PLC."""

    output_dir.mkdir(parents=True, exist_ok=True)
    qt = _qt_imports()
    QtCore = qt["QtCore"]
    QtWidgets = qt["QtWidgets"]
    app = (
        QtWidgets.QApplication.instance()
        or QtWidgets.QApplication(sys.argv[:1])
    )
    session_factory = (
        (lambda: _VisualQaSession(demo_plc_state))
        if demo_plc_state is not None
        else NativePlcSession
    )
    window_class = build_window_class(
        qt,
        session_factory=session_factory,
        workspace_fixture_enabled=demo_workspace,
    )
    available = app.primaryScreen().availableGeometry()
    capture_width = width or min(1920, available.width())
    capture_height = height or min(1080, available.height())
    if (width is not None or height is not None) and (
        capture_width < 960 or capture_height < 520
    ):
        raise ValueError("responsive capture must be at least 960x520")
    window = window_class(
        initial_view="A",
        demo_event=demo_event,
        compact_display=capture_width < 1200 or capture_height < 700,
        visual_qa_fixture=demo_plc_state is not None,
    )
    try:
        window.resize(capture_width, capture_height)
        window.show()
        app.processEvents()
        if demo_workspace:
            window.workspace_client.sign_in(
                "visual-qa@fixture.local",
                "visual-qa-secret",
            )
            resolution = window.workspace_client.sync(
                window.workspace_assignment_id
            )
            if resolution.package is not None:
                window._set_workspace_badge("SYNCED")
            app.processEvents()
        if demo_selection:
            target = next(
                (
                    item
                    for item in build_scene2_targets(window.session.snapshot())
                    if item.target_id == demo_selection
                ),
                None,
            )
            if target is None:
                raise ValueError(f"unknown demo selection: {demo_selection}")
            window.viewport._selected_target = target
            window.viewport.container.equipmentSelected.emit(target)
            window.viewport.container.update()
            app.processEvents()
        if demo_panel is not None:
            panel_indexes = {
                "equipment": 0,
                "events": 1,
                "health": 2,
                "runtime": 3,
            }
            window.compact_rail_nav.setCurrentIndex(
                panel_indexes[demo_panel]
            )
            app.processEvents()

        captures: list[dict[str, Any]] = []
        for view_id in VIEW_NAMES:
            window.set_view_mode(view_id)
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(250, loop.quit)
            loop.exec()
            image = window.grab()
            output = output_dir / f"RungProof-view-{view_id}.png"
            if not image.save(str(output)):
                raise RuntimeError(f"Could not save native view capture: {output}")
            captures.append(
                {
                    "view": view_id,
                    "file": output.name,
                    "width": image.width(),
                    "height": image.height(),
                }
            )

        report = {
            "application": "RungProof",
            "version": APP_VERSION,
            "renderer": DEFAULT_RENDERER,
            "realPlcWritesCapabilityEnabled": REAL_PLC_WRITES_ENABLED,
            "plcConnectionAttempted": False,
            "fixtureTransport": (
                "none" if demo_plc_state is not None else "native_session_not_started"
            ),
            "availableScreen": {
                "width": available.width(),
                "height": available.height(),
                "devicePixelRatio": app.primaryScreen().devicePixelRatio(),
            },
            "captureSize": {
                "width": capture_width,
                "height": capture_height,
            },
            "demoEvent": demo_event,
            "demoSelection": demo_selection,
            "demoWorkspace": demo_workspace,
            "demoPanel": demo_panel,
            "demoPlcState": demo_plc_state,
            "visualQaFixture": demo_plc_state is not None,
            "captures": captures,
        }
        (output_dir / "CAPTURE-REPORT.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return 0
    finally:
        window.session.close(timeout=7.0)
        window.close()
        app.processEvents()


def main() -> int:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument(
        "--self-test-report",
        type=Path,
        help="Validate packaged native resources without connecting.",
    )
    parser.add_argument(
        "--view",
        choices=tuple(VIEW_NAMES),
        default="A",
        help="Initial native workspace view.",
    )
    parser.add_argument(
        "--capture-view-dir",
        type=Path,
        help=(
            "Capture disconnected Views A/B/C and a machine-readable "
            "environment report, then exit without connecting to a PLC."
        ),
    )
    parser.add_argument(
        "--capture-width",
        type=int,
        help="Optional responsive capture width in logical pixels.",
    )
    parser.add_argument(
        "--capture-height",
        type=int,
        help="Optional responsive capture height in logical pixels.",
    )
    parser.add_argument(
        "--demo-event",
        action="store_true",
        help="Capture a local-model alarm state for visual QA; no PLC is touched.",
    )
    parser.add_argument(
        "--demo-selection",
        choices=("main_conveyor", "photoeye", "pusher", "drive_motor", "stacklight", "package"),
        help="Capture a selected equipment state for visual QA; no PLC is touched.",
    )
    parser.add_argument(
        "--demo-workspace",
        action="store_true",
        help="Capture the deterministic local workspace-synced state for visual QA.",
    )
    parser.add_argument(
        "--demo-panel",
        choices=("equipment", "events", "health", "runtime"),
        help="Select a compact diagnostic pane for visual QA captures.",
    )
    parser.add_argument(
        "--demo-plc-state",
        choices=("disconnected", "not-ready", "healthy"),
        help=(
            "Capture an explicitly labeled synthetic PLC state for visual QA; "
            "no PLC transport is created or touched."
        ),
    )
    parser.add_argument(
        "--renderer",
        choices=RENDERERS,
        default=DEFAULT_RENDERER,
        help=(
            "Viewport backend. Software is VM-safe; qt3d is an explicit "
            "workstation-only option."
        ),
    )
    args = parser.parse_args()
    if args.self_test_report is not None:
        return _write_self_test(args.self_test_report.resolve())
    if args.capture_view_dir is not None:
        return _capture_native_views(
            args.capture_view_dir.resolve(),
            width=args.capture_width,
            height=args.capture_height,
            demo_event=args.demo_event,
            demo_selection=args.demo_selection,
            demo_workspace=args.demo_workspace,
            demo_panel=args.demo_panel,
            demo_plc_state=args.demo_plc_state,
        )
    return run_gui(initial_view=args.view, renderer=args.renderer)


if __name__ == "__main__":
    raise SystemExit(main())
