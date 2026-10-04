"""Validated header-menu catalog for native RungProof scenes.

The catalog lists every packaged scene document, but availability is supplied
by native code. A scene file can never make itself live or borrow another
scene's PLC profile.
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


PRODUCTION_SCENE_ORDER = (
    "scene-1-conveyor-stop",
    "scene-2-conveyor-pusher",
    "conveyor-cell",
    "tank-level",
    "tank-high-low",
    "tank-radar",
    "equipment-gallery",
)

REVIEW_SCENE_ORDER = (
    "conveyor-cell",
    "tank-level",
    "tank-high-low",
    "tank-radar",
)

TOOL_SCENE_IDS = frozenset({"equipment-gallery"})


class NativeSceneCatalogError(ValueError):
    """A packaged scene cannot be represented safely in the native menu."""


def _lab_sort_key(path: Path) -> tuple[int, int, str]:
    match = re.match(r"lab-(\d+)-(\d+)-", path.name.lower())
    if match:
        return (int(match.group(1)), int(match.group(2)), path.name.lower())
    return (9999, 9999, path.name.lower())


@dataclass(frozen=True, slots=True)
class NativeSceneMenuEntry:
    scene_id: str
    name: str
    source_file: Path
    category: str
    live_available: bool
    review_available: bool

    @property
    def selectable(self) -> bool:
        return self.live_available or self.review_available

    @property
    def menu_text(self) -> str:
        if self.selectable:
            return self.name
        return f"{self.name}  (pending native runtime)"

    @property
    def status_tip(self) -> str:
        if self.live_available:
            return "Live native plant runtime and exact PLC profile available."
        if self.review_available:
            return "Static native visual review only; PLC commands are disabled."
        return "Listed for migration; native runtime and PLC profile are pending."


def _required_text(
    document: dict[str, Any],
    field: str,
    source_file: Path,
) -> str:
    value = document.get(field)
    if not isinstance(value, str) or not value.strip():
        raise NativeSceneCatalogError(
            f"{source_file.name} must contain a non-empty string {field!r}."
        )
    return value.strip()


def load_native_scene_catalog(
    scene_root: Path,
    *,
    live_scene_ids: Collection[str] = (),
    review_scene_ids: Collection[str] = (),
) -> tuple[NativeSceneMenuEntry, ...]:
    """Load packaged names while keeping support authority in native code."""

    root = Path(scene_root)
    if not root.is_dir():
        raise NativeSceneCatalogError(
            f"Native scene catalog directory is missing: {root}"
        )

    live_ids = frozenset(live_scene_ids)
    review_ids = frozenset(review_scene_ids)
    overlap = live_ids & review_ids
    if overlap:
        raise NativeSceneCatalogError(
            "A scene cannot be both live and review-only: "
            + ", ".join(sorted(overlap))
        )

    paths = sorted(
        (
            path
            for path in root.iterdir()
            if path.is_file() and path.suffix.lower() in {".json", ".plcscene"}
        ),
        key=lambda path: path.name.lower(),
    )
    entries: list[NativeSceneMenuEntry] = []
    seen_ids: set[str] = set()
    for path in paths:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise NativeSceneCatalogError(
                f"Cannot read native scene catalog entry {path.name}: {exc}"
            ) from exc
        if not isinstance(document, dict):
            raise NativeSceneCatalogError(
                f"{path.name} must contain a JSON object."
            )
        scene_id = _required_text(document, "id", path)
        name = _required_text(document, "name", path)
        if scene_id in seen_ids:
            raise NativeSceneCatalogError(
                f"Duplicate scene id in native catalog: {scene_id}"
            )
        seen_ids.add(scene_id)
        if scene_id in TOOL_SCENE_IDS:
            category = "tool"
        elif scene_id in review_ids:
            category = "review"
        elif scene_id.startswith("lab-"):
            category = "lab"
        else:
            category = "production"
        entries.append(
            NativeSceneMenuEntry(
                scene_id=scene_id,
                name=name,
                source_file=path,
                category=category,
                live_available=scene_id in live_ids,
                review_available=scene_id in review_ids,
            )
        )

    unknown_supported = (live_ids | review_ids) - seen_ids
    if unknown_supported:
        raise NativeSceneCatalogError(
            "Native support references missing scene documents: "
            + ", ".join(sorted(unknown_supported))
        )

    production_rank = {
        scene_id: index
        for index, scene_id in enumerate(PRODUCTION_SCENE_ORDER)
    }
    entries.sort(
        key=lambda entry: (
            {"production": 0, "review": 1, "tool": 2, "lab": 3}.get(
                entry.category,
                9,
            ),
            (
                _lab_sort_key(entry.source_file)
                if entry.category == "lab"
                else (
                    f"{REVIEW_SCENE_ORDER.index(entry.scene_id):03d}-"
                    f"{entry.source_file.name.lower()}"
                    if entry.category == "review"
                    and entry.scene_id in REVIEW_SCENE_ORDER
                    else f"{production_rank.get(entry.scene_id, 999):03d}-"
                    f"{entry.source_file.name.lower()}"
                )
            ),
        )
    )
    return tuple(entries)
