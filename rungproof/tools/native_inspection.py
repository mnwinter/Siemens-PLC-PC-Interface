"""Presentation-only semantic inspection targets for the native viewport.

This module deliberately has no Qt, PLC, or plant-runtime dependencies.  It
turns the visible Scene 2 composition into stable equipment targets and tests
pointer positions against projected world envelopes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


Point2 = tuple[float, float]
Point3 = tuple[float, float, float]
Bounds3 = tuple[float, float, float, float, float, float]


@dataclass(frozen=True, slots=True)
class InspectionTarget:
    target_id: str
    label: str
    equipment_type: str
    bounds: Bounds3
    status: str = "LOCAL MODEL"
    detail: str = "PLC state is not verified while disconnected."
    priority: int = 0
    outline_points: tuple[Point3, ...] = ()


def is_click_gesture(delta_x: float, delta_y: float, threshold: float = 5.0) -> bool:
    """Keep small pointer noise clickable while rejecting orbit drags."""

    return abs(delta_x) < threshold and abs(delta_y) < threshold


def inspection_source_text(disconnected: bool) -> str:
    return (
        "LOCAL MODEL / PLC STATE NOT VERIFIED"
        if disconnected
        else "LOCAL MODEL / CONTROLLER SESSION ACTIVE"
    )


def _bounds_corners(bounds: Bounds3) -> tuple[Point3, ...]:
    min_x, min_y, min_z, max_x, max_y, max_z = bounds
    return tuple(
        (x, y, z)
        for x in (min_x, max_x)
        for y in (min_y, max_y)
        for z in (min_z, max_z)
    )


def _convex_hull(points: Iterable[Point2]) -> tuple[Point2, ...]:
    unique = sorted(set(points))
    if len(unique) <= 2:
        return tuple(unique)

    def cross(o: Point2, a: Point2, b: Point2) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[1] - o[1])

    lower: list[Point2] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[Point2] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return tuple(lower[:-1] + upper[:-1])


def _contains_convex(point: Point2, polygon: tuple[Point2, ...]) -> bool:
    if len(polygon) < 3:
        return False
    signs = []
    for index, current in enumerate(polygon):
        nxt = polygon[(index + 1) % len(polygon)]
        cross = (nxt[0] - current[0]) * (point[1] - current[1]) - (
            nxt[1] - current[1]
        ) * (point[0] - current[0])
        if abs(cross) > 1e-7:
            signs.append(cross > 0)
    return not signs or all(sign == signs[0] for sign in signs)


def build_scene2_targets(model: object | None = None) -> tuple[InspectionTarget, ...]:
    """Return explicit semantic envelopes for the six Scene 2 assets."""

    pusher_position = max(
        0.0,
        min(1.0, float(getattr(model, "pusher_position", 0.0))),
    )
    targets = [
        InspectionTarget(
            "main_conveyor",
            "Main conveyor",
            "Roller conveyor",
            (-3.7, 0.0, -1.0, 3.7, 1.35, 1.0),
            priority=10,
        ),
        InspectionTarget(
            "photoeye",
            "Photoeye",
            "Through-beam sensor",
            (-0.22, 1.35, -1.18, 0.22, 2.45, 1.18),
            priority=60,
        ),
        InspectionTarget(
            "pusher",
            "Pneumatic pusher",
            "Pneumatic cylinder",
            (-0.48, 0.95, -2.55, 0.48, 2.05, -0.22 + pusher_position),
            priority=70,
        ),
        InspectionTarget(
            "drive_motor",
            "Drive motor",
            "Direct-head drive",
            (2.82, 0.72, 0.58, 3.68, 2.45, 2.52),
            priority=80,
        ),
        InspectionTarget(
            "stacklight",
            "Stack light",
            "Three-segment indicator",
            (2.70, 0.0, -2.05, 3.30, 3.05, -1.55),
            priority=60,
        ),
    ]
    if model is None or bool(getattr(model, "object_present", True)):
        leading = 0.10 if model is None else getattr(model, "object_leading_edge_m", None)
        if leading is not None:
            product_x = -3.5 + max(0.0, min(1.0, float(leading))) * 7.0
            targets.append(
                InspectionTarget(
                    "package",
                    "Package",
                    "Product carton",
                    (product_x - 0.48, 1.35, -0.48, product_x + 0.48, 2.05, 0.48),
                    priority=90,
                )
            )
    return tuple(targets)


def projected_target_polygons(
    targets: Iterable[InspectionTarget],
    project: Callable[[Point3], Point2],
) -> dict[str, tuple[Point2, ...]]:
    return {
        target.target_id: _convex_hull(
            project(point)
            for point in (
                target.outline_points
                if target.outline_points
                else _bounds_corners(target.bounds)
            )
        )
        for target in targets
    }


def hit_test_targets(
    screen_point: Point2,
    targets: Iterable[InspectionTarget],
    project: Callable[[Point3], Point2],
) -> InspectionTarget | None:
    """Return the highest-priority target under a camera-projected pointer."""

    target_list = tuple(targets)
    polygons = projected_target_polygons(target_list, project)
    matches = [
        target
        for target in target_list
        if _contains_convex(screen_point, polygons[target.target_id])
    ]
    return max(matches, key=lambda target: target.priority, default=None)
