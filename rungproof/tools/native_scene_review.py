"""Render complete native scenes for Matt's visual approval."""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.native_scene_library import (
    NATIVE_SCENE_BY_ID,
    NATIVE_SCENE_DEFINITIONS,
)
from tools.native_review_viewport import NativeSceneReviewViewport
from tools.rungproof_native import _qt_imports


def export_scene_cards(
    output_dir: Path,
    *,
    scene_ids: tuple[str, ...] | None = None,
    width: int = 1100,
    height: int = 700,
) -> tuple[Path, ...]:
    """Export scene cards without constructing a PLC session."""

    qt = _qt_imports()
    app = (
        qt["QtWidgets"].QApplication.instance()
        or qt["QtWidgets"].QApplication([])
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = (
        tuple(NATIVE_SCENE_BY_ID[scene_id] for scene_id in scene_ids)
        if scene_ids
        else NATIVE_SCENE_DEFINITIONS
    )
    outputs: list[Path] = []
    for definition in selected:
        viewport = NativeSceneReviewViewport(qt, definition)
        viewport.container.resize(width, height)
        viewport.container.show()
        app.processEvents()
        output = (
            output_dir
            / f"{definition.approval_id}-{definition.scene_id}.png"
        ).resolve()
        if not viewport.container.grab().save(str(output)):
            raise RuntimeError(f"Could not save native scene card: {output}")
        viewport.container.close()
        outputs.append(output)
    return tuple(outputs)


def export_contact_sheet(
    card_paths: tuple[Path, ...],
    output_dir: Path,
) -> Path:
    qt = _qt_imports()
    QtCore = qt["QtCore"]
    QtGui = qt["QtGui"]
    margin = 18
    gap = 14
    card_width = 520
    card_height = 331
    image = QtGui.QImage(
        margin * 2 + card_width * 2 + gap,
        margin * 2 + card_height * 2 + gap,
        QtGui.QImage.Format.Format_ARGB32,
    )
    image.fill(QtGui.QColor("#071015"))
    painter = QtGui.QPainter(image)
    painter.setRenderHint(
        QtGui.QPainter.RenderHint.SmoothPixmapTransform,
        True,
    )
    for slot, card_path in enumerate(card_paths[:4]):
        row, column = divmod(slot, 2)
        target = QtCore.QRectF(
            margin + column * (card_width + gap),
            margin + row * (card_height + gap),
            card_width,
            card_height,
        )
        card = QtGui.QImage(str(card_path))
        if card.isNull():
            raise RuntimeError(f"Could not load scene card: {card_path}")
        painter.drawImage(target, card)
    painter.end()
    output = (output_dir / "scene-approval-sheet-01.png").resolve()
    if not image.save(str(output)):
        raise RuntimeError(f"Could not save scene approval sheet: {output}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/scene-review"),
    )
    parser.add_argument(
        "--scene",
        action="append",
        choices=tuple(NATIVE_SCENE_BY_ID),
    )
    parser.add_argument("--sheet", action="store_true")
    arguments = parser.parse_args()
    outputs = export_scene_cards(
        arguments.output,
        scene_ids=tuple(arguments.scene) if arguments.scene else None,
    )
    for output in outputs:
        print(output)
    if arguments.sheet or not arguments.scene:
        print(export_contact_sheet(outputs, arguments.output))
    print("PLC_CONNECTION_ATTEMPTED: FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
