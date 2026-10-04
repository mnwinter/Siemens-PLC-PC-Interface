"""Render isolated native assets for Matt's approval workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from tools.native_asset_library import (
    ASSET_BY_TYPE,
    ASSET_DEFINITIONS,
    NativeAssetDefinition,
    build_asset_geometry,
)
from tools.native_software_viewport import (
    SoftwareScene2Viewport,
    project_isometric,
    scene_faces,
    sort_faces_for_painter,
)
from tools.rungproof_native import _qt_imports


class AssetReviewViewport(SoftwareScene2Viewport):
    """One-asset review card using the supported software 3D renderer."""

    def __init__(
        self,
        qt: dict[str, Any],
        definition: NativeAssetDefinition,
    ) -> None:
        self.definition = definition
        self.geometry = build_asset_geometry(definition.asset_type)
        super().__init__(qt)

    def _scene_scale(self, bounds: Any) -> float:
        return (
            min(
                bounds.width() / self.definition.view_span,
                bounds.height() / (self.definition.view_span * 0.72),
            )
            * 0.72
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
        return self.qt["QtCore"].QPointF(
            bounds.center().x() + projected[0] * scale,
            bounds.height() * 0.66 + projected[1] * scale,
        )

    def _draw_shadow(self, painter: Any, bounds: Any, scale: float) -> None:
        QtGui = self.qt["QtGui"]
        xs = [primitive.center[0] for primitive in self.geometry]
        zs = [primitive.center[2] for primitive in self.geometry]
        margin = 0.75
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
            if face.opacity <= 0:
                continue
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

    def _draw_overlay(self, painter: Any, bounds: Any) -> None:
        QtCore = self.qt["QtCore"]
        painter.setFont(self._font(self._font_family, 14, bold=True))
        painter.setPen(self._pen("#DDECEF"))
        painter.drawText(
            QtCore.QRectF(20, 16, bounds.width() - 40, 24),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"{self.definition.approval_id}  {self.definition.label.upper()}",
        )
        painter.setFont(self._font(self._font_family, 10))
        painter.setPen(self._pen("#9DB4BB"))
        painter.drawText(
            QtCore.QRectF(20, 42, bounds.width() - 40, 20),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            f"REFERENCE: {self.definition.reference_name}",
        )
        painter.setPen(self._pen("#F2B94B"))
        painter.drawText(
            QtCore.QRectF(20, bounds.height() - 52, bounds.width() - 40, 20),
            QtCore.Qt.AlignmentFlag.AlignRight,
            "REVIEW ONLY  |  PLC DISABLED  |  NO PLC TRANSPORT",
        )
        painter.drawText(
            QtCore.QRectF(
                20,
                bounds.height() - 31,
                bounds.width() - 40,
                20,
            ),
            QtCore.Qt.AlignmentFlag.AlignRight,
            "PENDING APPROVAL  |  DRAG TO ORBIT  |  WHEEL TO ZOOM",
        )


def export_asset_cards(
    output_dir: Path,
    *,
    asset_types: tuple[str, ...] | None = None,
    width: int = 900,
    height: int = 620,
) -> tuple[Path, ...]:
    """Export deterministic PNG approval cards without contacting the PLC."""

    qt = _qt_imports()
    app = (
        qt["QtWidgets"].QApplication.instance()
        or qt["QtWidgets"].QApplication([])
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = (
        tuple(ASSET_BY_TYPE[asset_type] for asset_type in asset_types)
        if asset_types
        else ASSET_DEFINITIONS
    )
    outputs: list[Path] = []
    for definition in selected:
        viewport = AssetReviewViewport(qt, definition)
        viewport.container.resize(width, height)
        viewport.container.show()
        app.processEvents()
        output = (
            output_dir
            / f"{definition.approval_id}-{definition.asset_type}.png"
        ).resolve()
        if not viewport.container.grab().save(str(output)):
            raise RuntimeError(f"Could not save asset review card: {output}")
        viewport.container.close()
        outputs.append(output)
    return tuple(outputs)


def export_contact_sheets(
    card_paths: tuple[Path, ...],
    output_dir: Path,
    *,
    columns: int = 2,
    rows: int = 3,
) -> tuple[Path, ...]:
    """Compose readable review sheets while retaining individual PNG cards."""

    qt = _qt_imports()
    QtCore = qt["QtCore"]
    QtGui = qt["QtGui"]
    margin = 18
    gap = 14
    card_width = 430
    card_height = 296
    sheet_width = margin * 2 + columns * card_width + (columns - 1) * gap
    sheet_height = margin * 2 + rows * card_height + (rows - 1) * gap
    page_size = columns * rows
    outputs: list[Path] = []
    for page_index in range(0, len(card_paths), page_size):
        image = QtGui.QImage(
            sheet_width,
            sheet_height,
            QtGui.QImage.Format.Format_ARGB32,
        )
        image.fill(QtGui.QColor("#071015"))
        painter = QtGui.QPainter(image)
        painter.setRenderHint(
            QtGui.QPainter.RenderHint.SmoothPixmapTransform,
            True,
        )
        for slot, card_path in enumerate(
            card_paths[page_index : page_index + page_size]
        ):
            row, column = divmod(slot, columns)
            target = QtCore.QRectF(
                margin + column * (card_width + gap),
                margin + row * (card_height + gap),
                card_width,
                card_height,
            )
            card = QtGui.QImage(str(card_path))
            if card.isNull():
                raise RuntimeError(f"Could not load asset card: {card_path}")
            painter.drawImage(target, card)
        painter.end()
        output = (
            output_dir
            / f"approval-sheet-{page_index // page_size + 1:02d}.png"
        ).resolve()
        if not image.save(str(output)):
            raise RuntimeError(f"Could not save contact sheet: {output}")
        outputs.append(output)
    return tuple(outputs)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/asset-review"),
    )
    parser.add_argument(
        "--asset",
        action="append",
        choices=tuple(ASSET_BY_TYPE),
    )
    parser.add_argument(
        "--sheets",
        action="store_true",
        help="Also compose contact sheets for a selected asset subset.",
    )
    arguments = parser.parse_args()
    outputs = export_asset_cards(
        arguments.output,
        asset_types=tuple(arguments.asset) if arguments.asset else None,
    )
    for output in outputs:
        print(output)
    if not arguments.asset or arguments.sheets:
        for sheet in export_contact_sheets(outputs, arguments.output):
            print(sheet)
    print("PLC_CONNECTION_ATTEMPTED: FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
