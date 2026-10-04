"""VM-safe player viewport for a static native scene under review."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

try:
    from .native_scene_library import (
        NativeSceneDefinition,
        build_asset_geometry,
        build_native_scene_geometry,
    )
    from .native_software_viewport import (
        SoftwareScene2Viewport,
        project_isometric,
        scene_faces,
        sort_faces_for_painter,
    )
except ImportError:
    from native_scene_library import (
        NativeSceneDefinition,
        build_asset_geometry,
        build_native_scene_geometry,
    )
    from native_software_viewport import (
        SoftwareScene2Viewport,
        project_isometric,
        scene_faces,
        sort_faces_for_painter,
    )


class NativeSceneReviewViewport(SoftwareScene2Viewport):
    """Render one complete scene without constructing a PLC session."""

    def __init__(
        self,
        qt: dict[str, Any],
        definition: NativeSceneDefinition,
    ) -> None:
        self.definition = definition
        self.compact_display = False
        self.geometry = build_native_scene_geometry(definition.scene_id)
        self._projection_center = (0.0, 0.0)
        super().__init__(qt)

    def _scene_scale(self, bounds: Any) -> float:
        projected = [
            project_isometric(
                point,
                yaw_degrees=self._yaw_degrees,
                pitch_degrees=self._pitch_degrees,
            )
            for face in scene_faces(self.geometry)
            for point in face.points
        ]
        x_values = [point[0] for point in projected]
        y_values = [point[1] for point in projected]
        x_span = max(max(x_values) - min(x_values), 1.0)
        y_span = max(max(y_values) - min(y_values), 1.0)
        self._projection_center = (
            (min(x_values) + max(x_values)) / 2.0,
            (min(y_values) + max(y_values)) / 2.0,
        )
        compact_available_height = max(bounds.height() - 60.0, 80.0)
        usable_height = (
            compact_available_height
            if self.compact_display
            else bounds.height() * 0.78
        )
        return (
            min(
                (bounds.width() - 28.0) / x_span,
                usable_height / y_span,
            )
            * (
                0.72
                if self.compact_display
                and getattr(self, "review_handoff_compact", False)
                else 0.62
                if self.compact_display
                else 0.68
            )
            * self._zoom
        )

    def _screen_point(
        self,
        point: tuple[float, float, float],
        bounds: Any,
        scale: float,
    ) -> Any:
        projected = project_isometric(
            point,
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )
        projected = (
            projected[0] - self._projection_center[0],
            projected[1] - self._projection_center[1],
        )
        compact_available_height = max(bounds.height() - 110.0, 80.0)
        compact_anchor = 10.0 + compact_available_height * 0.50
        return self.qt["QtCore"].QPointF(
            bounds.center().x() + projected[0] * scale + self._pan_x,
            (compact_anchor if self.compact_display else bounds.height() * 0.55)
            + projected[1] * scale
            + self._pan_y,
        )

    def _draw_shadow(self, painter: Any, bounds: Any, scale: float) -> None:
        QtGui = self.qt["QtGui"]
        xs = [primitive.center[0] for primitive in self.geometry]
        zs = [primitive.center[2] for primitive in self.geometry]
        margin = 0.85
        corners = (
            (min(xs) - margin, 0.01, min(zs) - margin),
            (max(xs) + margin, 0.01, min(zs) - margin),
            (max(xs) + margin, 0.01, max(zs) + margin),
            (min(xs) - margin, 0.01, max(zs) + margin),
        )
        painter.setPen(self.qt["QtCore"].Qt.PenStyle.NoPen)
        painter.setBrush(self._color("#02070A", 130))
        painter.drawPolygon(
            QtGui.QPolygonF(
                [
                    self._screen_point(point, bounds, scale)
                    for point in corners
                ]
            )
        )

    def _draw_scene(self, painter: Any, bounds: Any, scale: float) -> None:
        QtCore = self.qt["QtCore"]
        QtGui = self.qt["QtGui"]
        self._draw_contact_shadows(painter, bounds, scale, self.geometry)
        faces = sort_faces_for_painter(
            scene_faces(self.geometry),
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )
        for face in faces:
            points = [
                self._screen_point(point, bounds, scale)
                for point in face.points
            ]
            painter.setPen(self._pen("#344A53", 0.75))
            painter.setBrush(
                self._shade_color(
                    face.color,
                    self._material_shade(face),
                    face.opacity,
                )
            )
            polygon = QtGui.QPolygonF(points)
            painter.drawPolygon(polygon)
            if self._should_outline(face.role):
                painter.setPen(self._face_edge_pen(face))
                painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
                painter.drawPolygon(polygon)
            self._draw_material_detail(painter, face, points)
        self._draw_inspection_overlay(painter, bounds, scale)

    def _draw_overlay(self, painter: Any, bounds: Any) -> None:
        QtCore = self.qt["QtCore"]
        if self.compact_display:
            # Compact handoffs still need enough provenance to remain safe and
            # reviewable when the surrounding authoring shell is no longer
            # visible. Other compact shells may opt into the legacy ribbon.
            handoff_compact = getattr(self, "review_handoff_compact", False)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(self._color("#0B181E", 210))
            overlay_height = 42 if handoff_compact else 24
            painter.drawRoundedRect(QtCore.QRectF(8, 6, max(bounds.width() - 16, 180), overlay_height), 4, 4)
            painter.setFont(self._font(self._font_family, 9, bold=True))
            painter.setPen(self._pen("#F2B94B"))
            painter.drawText(
                QtCore.QRectF(18, 7, max(bounds.width() - 36, 160), 18),
                QtCore.Qt.AlignmentFlag.AlignLeft,
                (
                    f"DRAFT {self.definition.label}  |  ID {self.definition.scene_id}"
                    if handoff_compact
                    else "REVIEW ONLY  |  PLC DISABLED  |  NO PLC TRANSPORT"
                ),
            )
            if handoff_compact:
                painter.setFont(self._font(self._font_family, 8))
                painter.setPen(self._pen("#9DB4BB"))
                painter.drawText(
                    QtCore.QRectF(18, 24, max(bounds.width() - 36, 160), 17),
                    QtCore.Qt.AlignmentFlag.AlignLeft,
                    "UNSAVED SOURCE  |  REVIEW ONLY  |  PLC DISABLED",
                )
            painter.setPen(self._pen("#6F8992"))
            painter.drawText(
                QtCore.QRectF(16, bounds.height() - 27, bounds.width() - 32, 18),
                QtCore.Qt.AlignmentFlag.AlignRight,
                (
                    "CLICK SELECT  |  LEFT ORBIT  |  MIDDLE PAN  |  WHEEL ZOOM"
                    if handoff_compact
                    else "DRAG TO ORBIT  |  WHEEL TO ZOOM"
                ),
            )
            snapshot = getattr(self, "review_runtime_snapshot", None)
            if snapshot is not None and (snapshot.cycle_active or snapshot.fault_active):
                painter.setPen(self._pen("#071015"))
                painter.setBrush(
                    self._color("#F2B94B" if snapshot.fault_active else "#55C7E8", 225)
                )
                painter.drawRoundedRect(
                    QtCore.QRectF(18, bounds.height() - 30, 190, 20), 4, 4
                )
                painter.setFont(self._font(self._font_family, 8, bold=True))
                painter.drawText(
                    QtCore.QRectF(26, bounds.height() - 29, 174, 18),
                    QtCore.Qt.AlignmentFlag.AlignLeft,
                    (
                        "ALARM ACKNOWLEDGED"
                        if snapshot.fault_acknowledged
                        else "ALARM ACTIVE"
                    )
                    if snapshot.fault_active
                    else "LOCAL OUTPUTS ACTIVE",
                )
            return

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(self._color("#0B181E", 220))
        painter.drawRect(
            QtCore.QRectF(
                0,
                0,
                bounds.width(),
                108,
            )
        )
        painter.setFont(self._font(self._font_family, 14, bold=True))
        painter.setPen(self._pen("#DDECEF"))
        title_text = (
            "STATIC DRAFT"
            if self.definition.approval_id == "DRAFT"
            else f"{self.definition.approval_id}  {self.definition.label.upper()}"
        )
        painter.drawText(
            QtCore.QRectF(20, 16, bounds.width() - 40, 24),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            title_text,
        )
        painter.setFont(self._font(self._font_family, 10))
        painter.setPen(self._pen("#9DB4BB"))
        painter.drawText(
            QtCore.QRectF(20, 42, bounds.width() - 40, 20),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"SCENE ID: {self.definition.scene_id}  |  "
            f"SOURCE: {self.definition.source_file.name}",
        )
        setup_label = (
            f"SETUP DOC: {self.definition.approval_id}_SETUP"
            if self.compact_display
            else f"SETUP: {self.definition.setup_file.name}"
        )
        painter.drawText(
            QtCore.QRectF(20, 62, bounds.width() - 40, 20),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"{setup_label}  |  REVISION: "
            f"{'STATIC-AUTHORING-V1' if self.definition.approval_id == 'DRAFT' else 'NATIVE-SCENE-V1'}",
        )
        painter.setPen(self._pen("#F2B94B"))
        painter.drawText(
            QtCore.QRectF(
                20,
                82,
                bounds.width() - 40,
                20,
            ),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            "STATIC DRAFT  |  REVIEW ONLY  |  PLC DISABLED  |  NO PLC TRANSPORT"
            if self.definition.approval_id == "DRAFT"
            else "REVIEW ONLY  |  PLC DISABLED  |  NO PLC TRANSPORT",
        )
        painter.drawText(
            QtCore.QRectF(
                20,
                bounds.height() - 31,
                bounds.width() - 40,
                20,
            ),
            QtCore.Qt.AlignmentFlag.AlignRight,
            "DRAFT NOT FOR RUNTIME  |  CLICK SELECT  |  LEFT-DRAG ORBIT  |  MIDDLE-DRAG PAN  |  WHEEL ZOOM"
            if self.definition.approval_id == "DRAFT"
            else "PENDING SCENE APPROVAL  |  LEFT-DRAG ORBIT  |  MIDDLE-DRAG PAN  |  WHEEL ZOOM",
        )
        snapshot = getattr(self, "review_runtime_snapshot", None)
        if snapshot is not None and (snapshot.cycle_active or snapshot.fault_active):
            painter.setPen(self._pen("#071015"))
            painter.setBrush(
                self._color("#F2B94B" if snapshot.fault_active else "#55C7E8", 225)
            )
            painter.drawRoundedRect(
                QtCore.QRectF(22, bounds.height() - 34, 210, 22), 4, 4
            )
            painter.setFont(self._font(self._font_family, 9, bold=True))
            painter.drawText(
                QtCore.QRectF(32, bounds.height() - 33, 190, 20),
                QtCore.Qt.AlignmentFlag.AlignLeft,
                (
                    "ALARM ACKNOWLEDGED"
                    if snapshot.fault_acknowledged
                    else "ALARM ACTIVE"
                )
                if snapshot.fault_active
                else "LOCAL OUTPUTS ACTIVE",
            )


class NativeEquipmentAssetViewport(NativeSceneReviewViewport):
    """Large single-asset viewport used by the dedicated Equipment Gallery."""

    def _scene_scale(self, bounds: Any) -> float:
        projected = [
            project_isometric(
                point,
                yaw_degrees=self._yaw_degrees,
                pitch_degrees=self._pitch_degrees,
            )
            for face in scene_faces(self.geometry)
            for point in face.points
        ]
        x_values = [point[0] for point in projected]
        y_values = [point[1] for point in projected]
        x_span = max(max(x_values) - min(x_values), 1.0)
        y_span = max(max(y_values) - min(y_values), 1.0)
        self._projection_center = (
            (min(x_values) + max(x_values)) / 2.0,
            (min(y_values) + max(y_values)) / 2.0,
        )
        layout_height = 260.0 if self.compact_display else bounds.height()
        reserved_height = 100.0 if self.compact_display else 125.0
        compact_factor = (
            1.28
            if self.compact_display
            and self.asset_type == "tank"
            else 1.55
            if self.compact_display and self.asset_type == "drillPress"
            else 1.10
            if self.compact_display
            else 0.86
        )
        return (
            min(
                (bounds.width() - 24.0) / x_span,
                max(layout_height - reserved_height, 120.0) / y_span,
            )
            * compact_factor
            * self._zoom
        )

    def _screen_point(
        self,
        point: tuple[float, float, float],
        bounds: Any,
        scale: float,
    ) -> Any:
        projected = project_isometric(
            point,
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )
        projected = (
            projected[0] - self._projection_center[0],
            projected[1] - self._projection_center[1],
        )
        return self.qt["QtCore"].QPointF(
            bounds.center().x() + projected[0] * scale + self._pan_x,
            ((260.0 if self.compact_display else bounds.height()) - 45.0) / 2.0
            + (
                28.0
                if self.compact_display and self.asset_type == "tank"
                else 15.0
                if self.compact_display
                else 40.0
            )
            + projected[1] * scale
            + self._pan_y,
        )

    def __init__(
        self,
        qt: dict[str, Any],
        definition: NativeSceneDefinition,
        asset_type: str,
        asset_label: str,
        view_span: float,
        approval_id: str = "ASSET",
        reference_name: str = "",
    ) -> None:
        super().__init__(qt, definition)
        self.set_asset(
            asset_type,
            asset_label,
            view_span,
            approval_id=approval_id,
            reference_name=reference_name,
            reset=False,
        )

    def set_asset(
        self,
        asset_type: str,
        asset_label: str,
        view_span: float,
        *,
        approval_id: str = "ASSET",
        reference_name: str = "",
        reset: bool = True,
    ) -> None:
        self.geometry = build_asset_geometry(asset_type)
        self.asset_type = asset_type
        self.definition = replace(
            self.definition,
            approval_id=approval_id,
            label=asset_label,
            description=reference_name,
            view_span=view_span,
        )
        if reset:
            self.reset_camera()
        else:
            self.container.update()

    def zoom_by(self, amount: float) -> None:
        self._zoom = max(0.55, min(2.4, self._zoom + amount))
        self.container.update()

    def set_view_preset(self, yaw: float, pitch: float) -> None:
        self._yaw_degrees = yaw
        self._pitch_degrees = max(12.0, min(65.0, pitch))
        self._pan_x = 0.0
        self._pan_y = 0.0
        self.container.update()

    def _draw_overlay(self, painter: Any, bounds: Any) -> None:
        QtCore = self.qt["QtCore"]
        painter.setFont(self._font(self._font_family, 16, bold=True))
        painter.setPen(self._pen("#EAF2F4"))
        painter.drawText(
            QtCore.QRectF(22, 18, bounds.width() - 44, 28),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"{self.definition.approval_id}  ·  "
            f"{self.definition.label.upper()}",
        )
        painter.setFont(self._font(self._font_family, 11))
        painter.setPen(self._pen("#9DB4BB"))
        painter.drawText(
            QtCore.QRectF(22, 48, bounds.width() - 44, 22),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"REFERENCE  {self.definition.description}",
        )
        painter.setPen(self._pen("#5FC5EC"))
        painter.drawText(
            QtCore.QRectF(22, bounds.height() - 33, bounds.width() - 44, 22),
            QtCore.Qt.AlignmentFlag.AlignRight,
            "LEFT DRAG ORBIT  ·  MIDDLE DRAG PAN  ·  WHEEL ZOOM",
        )
