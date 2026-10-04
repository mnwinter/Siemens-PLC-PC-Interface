"""VM-safe isometric 3D renderer for the native RungProof Scene 2 view.

The live PLC path does not enter this module. This adapter consumes immutable
session snapshots and projects a small 3D equipment model through Qt's
raster-backed QPainter API. It therefore retains real depth and an orbitable
camera without the native child window or OpenGL context required by Qt 3D,
which are unreliable on some Windows VMs and Remote Desktop sessions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from pathlib import Path
from typing import Any

try:
    from .native_inspection import (
        InspectionTarget,
        build_scene2_targets,
        hit_test_targets,
        is_click_gesture,
        projected_target_polygons,
    )
except ImportError:
    from native_inspection import (  # type: ignore
        InspectionTarget,
        build_scene2_targets,
        hit_test_targets,
        is_click_gesture,
        projected_target_polygons,
    )


BACKGROUND_DEEP = "#071015"
BACKGROUND = "#0B171D"
GRID_MINOR = "#18333D"
GRID_MAJOR = "#31515D"
LINE = "#29414B"
TEXT = "#EAF2F4"
MUTED = "#88A0A9"
CYAN = "#5FC5EC"
PROOF_GREEN = "#16A34A"
SAFE_GREEN = "#3DD6A5"
AMBER = "#F2B94B"
BAD = "#EF6A61"
MATERIAL_EDGE_LIGHT = "#B9CDD1"
MATERIAL_EDGE_DARK = "#071116"
CONTACT_SHADOW = "#02070A"
MATERIAL_HIGHLIGHT = "#E5EEF0"
# These colors deliberately do not reuse proof/PLC colors.  They indicate a
# local model value without implying that the physical controller confirmed it.
LOCAL_ACTIVE = "#A5B3B6"
LOCAL_UNAVAILABLE = "#46575D"
LOCAL_AMBER = "#B68A3D"

SOFTWARE_RENDER_MODE = "isometric-3d"
# Keep the VM-safe renderer raster-backed, but do not make authored equipment
# look like a 14-sided CAD placeholder.  This is deliberately centralized so
# every asset gets the same visual-quality floor and the cost is easy to tune
# after measured VM performance testing.
DEFAULT_RADIAL_SEGMENTS = 24
DEFAULT_SPHERE_LONGITUDE_SEGMENTS = 24
DEFAULT_SPHERE_LATITUDE_SEGMENTS = 12
DEFAULT_YAW_DEGREES = 34.0
DEFAULT_PITCH_DEGREES = 28.0
MIN_YAW_DEGREES = 8.0
MAX_YAW_DEGREES = 72.0
MIN_PITCH_DEGREES = 12.0
MAX_PITCH_DEGREES = 65.0
MIN_ZOOM = 0.72
MAX_ZOOM = 1.42
MIN_PAN_PIXELS = -400.0
MAX_PAN_PIXELS = 400.0

Vec3 = tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class Primitive3D:
    """Renderer-neutral visual primitive used by the software 3D adapter."""

    role: str
    kind: str
    center: Vec3
    color: str
    size: Vec3 = (0.0, 0.0, 0.0)
    axis: str = "y"
    radius: float = 0.0
    top_radius: float = 0.0
    inner_radius: float = 0.0
    length: float = 0.0
    end_caps: bool = True
    opacity: int = 255
    rotation: Vec3 = (0.0, 0.0, 0.0)
    render_layer: int = 0


@dataclass(frozen=True, slots=True)
class RenderFace:
    """One painter-sorted polygonal face in world coordinates."""

    role: str
    points: tuple[Vec3, ...]
    color: str
    shade: float
    opacity: int
    render_layer: int = 0


def project_isometric(
    point: Vec3,
    *,
    yaw_degrees: float = DEFAULT_YAW_DEGREES,
    pitch_degrees: float = DEFAULT_PITCH_DEGREES,
) -> Vec3:
    """Project a world point to an orthographic orbit-camera plane.

    The returned X/Y values are unscaled scene coordinates. The third value is
    camera depth and is used for deterministic painter ordering.
    """

    x, y, z = point
    yaw = math.radians(yaw_degrees)
    pitch = math.radians(pitch_degrees)
    yaw_cos = math.cos(yaw)
    yaw_sin = math.sin(yaw)
    pitch_cos = math.cos(pitch)
    pitch_sin = math.sin(pitch)

    horizontal = x * yaw_cos - z * yaw_sin
    orbit_depth = x * yaw_sin + z * yaw_cos
    vertical = y * pitch_cos - orbit_depth * pitch_sin
    camera_depth = y * pitch_sin + orbit_depth * pitch_cos
    return horizontal, -vertical, camera_depth


def build_scene_geometry(
    model: Any | None = None,
    *,
    ready: bool = False,
    error: bool = False,
    telemetry_valid: bool | None = None,
) -> tuple[Primitive3D, ...]:
    """Build the Scene 2 equipment geometry consumed by the QPainter path."""

    geometry: list[Primitive3D] = []

    def add_box(
        role: str,
        center: Vec3,
        size: Vec3,
        color: str,
        *,
        opacity: int = 255,
        render_layer: int = 0,
    ) -> None:
        geometry.append(
            Primitive3D(
                role=role,
                kind="box",
                center=center,
                size=size,
                color=color,
                opacity=opacity,
                render_layer=render_layer,
            )
        )

    def add_cylinder(
        role: str,
        center: Vec3,
        radius: float,
        length: float,
        color: str,
        *,
        axis: str = "y",
        opacity: int = 255,
        end_caps: bool = True,
        render_layer: int = 0,
    ) -> None:
        geometry.append(
            Primitive3D(
                role=role,
                kind="cylinder",
                center=center,
                color=color,
                axis=axis,
                radius=radius,
                length=length,
                end_caps=end_caps,
                opacity=opacity,
                render_layer=render_layer,
            )
        )

    running = bool(getattr(model, "motor_running", False))
    # Keep the default compatible with geometry-only callers.  The live
    # viewport passes an explicit value derived from the session snapshot.
    controller_telemetry_valid = (
        bool(ready) if telemetry_valid is None else bool(telemetry_valid)
    )
    blocked = bool(getattr(model, "photoeye_blocked", False))
    pusher_position = max(
        0.0,
        min(1.0, float(getattr(model, "pusher_position", 0.0))),
    )

    # An open roller conveyor has crossmembers under the rollers, not a broad
    # solid belt. Small individual members also avoid the painter-order problem
    # caused by one deck face spanning nearly the entire machine.
    for index in range(14):
        x = -3.25 + index * 0.5
        is_drive = index == 13
        add_box(
            "conveyor_deck" if index == 0 else f"deck_crossmember_{index:02d}",
            (x, 0.79, 0.0),
            (0.14, 0.12, 1.50),
            "#273238",
        )
        add_cylinder(
            "drive_roller" if is_drive else f"roller_{index:02d}",
            (x, 1.04, 0.0),
            0.12 if is_drive else 0.10,
            1.34,
            "#26343C" if is_drive else "#AAB7BD",
            axis="z",
            end_caps=False,
        )
        add_box(
            f"roller_witness_{index:02d}",
            (x, 1.135, 0.0),
            (0.025, 0.025, 1.20),
            CYAN if running and index % 3 == 0 else "#34454C",
        )
    for z in (-0.84, 0.84):
        add_box(
            f"side_rail_{z:+.2f}",
            (0.0, 1.00, z),
            (7.18, 0.22, 0.14),
            "#5E6B73",
        )
    for x in (-2.66, 2.66):
        for z in (-0.63, 0.63):
            add_box(
                f"leg_{x:+.2f}_{z:+.2f}",
                (x, 0.45, z),
                (0.14, 0.90, 0.14),
                "#26343C",
            )
            add_box(
                f"foot_{x:+.2f}_{z:+.2f}",
                (x, 0.04, z),
                (0.42, 0.08, 0.32),
                "#5E6B73",
            )

    # Direct discharge-end head drive. Every component shares the drive
    # roller's X/Y centerline and extends outward along the cross-belt Z axis.
    drive_x = 3.25
    drive_y = 1.04
    add_cylinder(
        "drive_output_shaft",
        (drive_x, drive_y, 0.86),
        0.065,
        0.54,
        "#AAB7BD",
        axis="z",
        render_layer=20,
    )
    add_cylinder(
        "drive_coupling_guard",
        (drive_x, drive_y, 0.84),
        0.13,
        0.24,
        "#F2B705",
        axis="z",
        render_layer=20,
    )
    add_cylinder(
        "drive_bearing_flange",
        (drive_x, drive_y, 0.91),
        0.21,
        0.12,
        "#26343C",
        axis="z",
        render_layer=20,
    )
    add_box(
        "drive_adapter_plate",
        (drive_x, drive_y, 0.94),
        (0.70, 0.58, 0.08),
        "#5E6B73",
        render_layer=20,
    )
    add_box(
        "drive_gearbox",
        (drive_x, drive_y, 1.14),
        (0.58, 0.58, 0.42),
        "#26343C",
        render_layer=20,
    )
    add_box(
        "drive_mounting_bracket",
        (drive_x, drive_y - 0.35, 1.09),
        (0.72, 0.12, 0.60),
        "#5E6B73",
        render_layer=20,
    )
    add_cylinder(
        "drive_motor",
        (drive_x, drive_y, 1.86),
        0.25,
        0.95,
        "#1684A6" if running else "#176B87",
        axis="z",
        render_layer=20,
    )
    for index, z in enumerate((1.45, 2.27)):
        add_cylinder(
            f"drive_motor_end_bell_{index}",
            (drive_x, drive_y, z),
            0.21,
            0.13,
            "#26343C",
            axis="z",
            render_layer=20,
        )
    add_box(
        "drive_motor_terminal",
        (drive_x, drive_y + 0.34, 1.86),
        (0.34, 0.24, 0.42),
        "#26343C",
        render_layer=20,
    )
    add_cylinder(
        "drive_run_lamp",
        (drive_x, drive_y + 0.50, 1.86),
        0.075,
        0.06,
        SAFE_GREEN if running else "#17362D",
        render_layer=20,
    )

    # Product and tape. The no-snapshot preview deliberately shows the product
    # so the scene still reads as a working conveyor rather than an empty rig.
    object_present = (
        True if model is None else bool(getattr(model, "object_present", False))
    )
    leading = (
        0.10
        if model is None
        else getattr(model, "object_leading_edge_m", None)
    )
    if object_present and leading is not None:
        product_x = -3.5 + max(0.0, min(1.0, float(leading))) * 7.0
        add_box(
            "product_carton",
            (product_x, 1.50, 0.0),
            (0.85, 0.72, 0.72),
            "#C89242",
        )
        add_box(
            "product_tape",
            (product_x, 1.87, 0.0),
            (0.86, 0.018, 0.14),
            "#E6CF9A",
        )

    # Photoeye posts, housings, lenses, and beam.
    for index, z in enumerate((-1.05, 1.05)):
        add_box(
            f"photoeye_post_{index}",
            (0.0, 1.65, z),
            (0.16, 1.45, 0.16),
            "#26343C",
        )
        add_box(
            "photoeye_emitter" if index == 0 else "photoeye_receiver",
            (0.0, 1.46, z),
            (0.30, 0.24, 0.24),
            "#2E8BD1",
        )
        add_cylinder(
            f"photoeye_lens_{index}",
            (0.0, 1.46, z + (0.14 if z < 0 else -0.14)),
            0.07,
            0.04,
            (
                AMBER
                if controller_telemetry_valid and blocked
                else CYAN
                if controller_telemetry_valid
                else LOCAL_AMBER
                if blocked
                else LOCAL_UNAVAILABLE
            ),
            axis="z",
        )
    add_box(
        "photoeye_beam",
        # Align the beam centerline with the pusher plate center. The prior
        # 1.46/0.025 geometry made the visible upper edge appear to terminate
        # at the plate's top-right corner in the isometric projection.
        (0.0, 1.45, 0.0),
        (0.018, 0.012, 1.90),
        (
            AMBER
            if controller_telemetry_valid and blocked
            else CYAN
            if controller_telemetry_valid
            else LOCAL_AMBER
            if blocked
            else LOCAL_UNAVAILABLE
        ),
        opacity=220 if blocked else 150,
    )

    # Pneumatic pusher, rod, plate, manifold, and end-position indicators.
    add_cylinder(
        "pusher_body",
        (0.0, 1.45, -1.85),
        0.32,
        1.15,
        "#F58220",
        axis="z",
    )
    for index, z in enumerate((-2.37, -1.33)):
        add_cylinder(
            f"pusher_end_cap_{index}",
            (0.0, 1.45, z),
            0.36,
            0.12,
            "#26343C",
            axis="z",
        )
    add_cylinder(
        "pusher_rod",
        (0.0, 1.45, -0.86 + pusher_position),
        0.095,
        0.90,
        "#AAB7BD",
        axis="z",
    )
    add_box(
        "pusher_plate",
        (0.0, 1.45, -0.35 + pusher_position),
        (0.78, 0.72, 0.13),
        "#F2B705",
    )
    add_box(
        "pusher_manifold",
        (0.48, 0.30, -2.0),
        (0.55, 0.38, 0.50),
        "#176B87",
    )
    add_cylinder(
        "pusher_retracted_lamp",
        (-0.16, 1.85, -1.90),
        0.085,
        0.10,
        (
            PROOF_GREEN
            if controller_telemetry_valid
            and bool(getattr(model, "pusher_retracted", True))
            else LOCAL_ACTIVE
            if bool(getattr(model, "pusher_retracted", True))
            else LOCAL_UNAVAILABLE
        ),
    )
    add_cylinder(
        "pusher_extended_lamp",
        (0.16, 1.85, -1.90),
        0.085,
        0.10,
        (
            CYAN
            if controller_telemetry_valid
            and bool(getattr(model, "pusher_extended", False))
            else LOCAL_ACTIVE
            if bool(getattr(model, "pusher_extended", False))
            else LOCAL_UNAVAILABLE
        ),
    )

    # Stack light.
    add_box(
        "stacklight_pole",
        (3.0, 0.95, -1.8),
        (0.18, 1.90, 0.18),
        "#26343C",
    )
    add_cylinder(
        "stacklight_base",
        (3.0, 1.92, -1.8),
        0.30,
        0.12,
        "#26343C",
    )
    add_cylinder(
        "stacklight_red",
        (3.0, 2.05, -1.8),
        0.22,
        0.28,
        "#E53935" if error else "#5A1F24",
    )
    add_cylinder(
        "stacklight_amber",
        (3.0, 2.38, -1.8),
        0.22,
        0.28,
        # Amber communicates an idle/awaiting process state; green is reserved
        # for actual running motion below, while red remains a fault state.
        (
            AMBER
            if controller_telemetry_valid and not running and not error
            else LOCAL_ACTIVE
            if not running and not error
            else "#69501B"
        ),
    )
    add_cylinder(
        "stacklight_green",
        (3.0, 2.71, -1.8),
        0.22,
        0.28,
        # Communications readiness is not the same thing as a running
        # machine. Reserve green for actual process motion.
        (
            PROOF_GREEN
            if controller_telemetry_valid and running
            else LOCAL_ACTIVE
            if running
            else "#164C2A"
        ),
    )
    add_cylinder(
        "stacklight_cap",
        (3.0, 2.88, -1.8),
        0.24,
        0.08,
        "#26343C",
    )

    return tuple(geometry)


def _rotate_vector(point: Vec3, rotation: Vec3) -> Vec3:
    """Rotate a local-space point by X/Y/Z Euler angles in degrees."""

    x, y, z = point
    rx, ry, rz = (math.radians(value) for value in rotation)

    y, z = (
        y * math.cos(rx) - z * math.sin(rx),
        y * math.sin(rx) + z * math.cos(rx),
    )
    x, z = (
        x * math.cos(ry) + z * math.sin(ry),
        -x * math.sin(ry) + z * math.cos(ry),
    )
    x, y = (
        x * math.cos(rz) - y * math.sin(rz),
        x * math.sin(rz) + y * math.cos(rz),
    )
    return x, y, z


def _world_point(primitive: Primitive3D, local: Vec3) -> Vec3:
    rotated = _rotate_vector(local, primitive.rotation)
    return tuple(
        primitive.center[index] + rotated[index]
        for index in range(3)
    )  # type: ignore[return-value]


def _box_faces(primitive: Primitive3D) -> list[RenderFace]:
    sx, sy, sz = primitive.size
    x0, x1 = -sx / 2, sx / 2
    y0, y1 = -sy / 2, sy / 2
    z0, z1 = -sz / 2, sz / 2
    vertices = {
        "000": _world_point(primitive, (x0, y0, z0)),
        "001": _world_point(primitive, (x0, y0, z1)),
        "010": _world_point(primitive, (x0, y1, z0)),
        "011": _world_point(primitive, (x0, y1, z1)),
        "100": _world_point(primitive, (x1, y0, z0)),
        "101": _world_point(primitive, (x1, y0, z1)),
        "110": _world_point(primitive, (x1, y1, z0)),
        "111": _world_point(primitive, (x1, y1, z1)),
    }
    definitions = (
        (("010", "110", "111", "011"), 1.20),  # top
        (("000", "001", "101", "100"), 0.48),  # bottom
        (("000", "010", "011", "001"), 0.68),  # -X
        (("100", "101", "111", "110"), 0.88),  # +X
        (("000", "100", "110", "010"), 0.76),  # -Z
        (("001", "011", "111", "101"), 0.96),  # +Z
    )
    return [
        RenderFace(
            role=primitive.role,
            points=tuple(vertices[key] for key in keys),
            color=primitive.color,
            shade=shade,
            opacity=primitive.opacity,
        )
        for keys, shade in definitions
    ]


def _cylinder_point(
    primitive: Primitive3D,
    axial_offset: float,
    angle: float,
) -> Vec3:
    radial_a = math.cos(angle) * primitive.radius
    radial_b = math.sin(angle) * primitive.radius
    if primitive.axis == "x":
        local = (axial_offset, radial_a, radial_b)
    elif primitive.axis == "z":
        local = (radial_a, radial_b, axial_offset)
    else:
        local = (radial_a, axial_offset, radial_b)
    return _world_point(primitive, local)


def _cylinder_faces(
    primitive: Primitive3D,
    *,
    segments: int = DEFAULT_RADIAL_SEGMENTS,
) -> list[RenderFace]:
    half = primitive.length / 2
    start = [
        _cylinder_point(primitive, -half, index * math.tau / segments)
        for index in range(segments)
    ]
    end = [
        _cylinder_point(primitive, half, index * math.tau / segments)
        for index in range(segments)
    ]
    faces: list[RenderFace] = []
    if primitive.end_caps:
        faces.extend(
            (
                RenderFace(
                    role=f"{primitive.role}_end_start",
                    points=tuple(reversed(start)),
                    color=primitive.color,
                    shade=0.66,
                    opacity=primitive.opacity,
                ),
                RenderFace(
                    role=f"{primitive.role}_end_finish",
                    points=tuple(end),
                    color=primitive.color,
                    shade=1.02,
                    opacity=primitive.opacity,
                ),
            )
        )
    for index in range(segments):
        following = (index + 1) % segments
        shade = 0.68 + 0.30 * max(
            0.0,
            math.sin((index + 0.5) * math.tau / segments),
        )
        faces.append(
            RenderFace(
                role=f"{primitive.role}_side_{index:02d}",
                points=(
                    start[index],
                    start[following],
                    end[following],
                    end[index],
                ),
                color=primitive.color,
                shade=shade,
                opacity=primitive.opacity,
            )
        )
    return faces


def _frustum_faces(
    primitive: Primitive3D,
    *,
    segments: int = DEFAULT_RADIAL_SEGMENTS,
) -> list[RenderFace]:
    """Build a tapered cylinder used for readable measurement volumes."""

    if primitive.radius <= 0.0 or primitive.top_radius < 0.0:
        raise ValueError(
            f"Frustum {primitive.role!r} requires valid end radii."
        )

    def point(axial_offset: float, radius: float, angle: float) -> Vec3:
        radial_a = math.cos(angle) * radius
        radial_b = math.sin(angle) * radius
        if primitive.axis == "x":
            local = (axial_offset, radial_a, radial_b)
        elif primitive.axis == "z":
            local = (radial_a, radial_b, axial_offset)
        else:
            local = (radial_a, axial_offset, radial_b)
        return _world_point(primitive, local)

    half = primitive.length / 2
    angles = [index * math.tau / segments for index in range(segments)]
    bottom = [point(-half, primitive.radius, angle) for angle in angles]
    top = [point(half, primitive.top_radius, angle) for angle in angles]
    faces: list[RenderFace] = []
    if primitive.end_caps:
        faces.extend(
            (
                RenderFace(
                    role=f"{primitive.role}_end_bottom",
                    points=tuple(reversed(bottom)),
                    color=primitive.color,
                    shade=0.62,
                    opacity=primitive.opacity,
                ),
                RenderFace(
                    role=f"{primitive.role}_end_top",
                    points=tuple(top),
                    color=primitive.color,
                    shade=1.08,
                    opacity=primitive.opacity,
                ),
            )
        )
    for index in range(segments):
        following = (index + 1) % segments
        shade = 0.68 + 0.30 * max(
            0.0,
            math.sin((index + 0.5) * math.tau / segments),
        )
        faces.append(
            RenderFace(
                role=f"{primitive.role}_side_{index:02d}",
                points=(
                    bottom[index],
                    bottom[following],
                    top[following],
                    top[index],
                ),
                color=primitive.color,
                shade=shade,
                opacity=primitive.opacity,
            )
        )
    return faces


def _tube_faces(
    primitive: Primitive3D,
    *,
    segments: int = DEFAULT_RADIAL_SEGMENTS,
) -> list[RenderFace]:
    """Build a hollow cylinder with annular ends and a visible inner wall."""

    if not 0.0 < primitive.inner_radius < primitive.radius:
        raise ValueError(
            f"Tube {primitive.role!r} requires 0 < inner_radius < radius."
        )

    def point(radius: float, axial_offset: float, angle: float) -> Vec3:
        radial_a = math.cos(angle) * radius
        radial_b = math.sin(angle) * radius
        if primitive.axis == "x":
            local = (axial_offset, radial_a, radial_b)
        elif primitive.axis == "z":
            local = (radial_a, radial_b, axial_offset)
        else:
            local = (radial_a, axial_offset, radial_b)
        return _world_point(primitive, local)

    half = primitive.length / 2
    angles = [index * math.tau / segments for index in range(segments)]
    outer_start = [point(primitive.radius, -half, angle) for angle in angles]
    outer_end = [point(primitive.radius, half, angle) for angle in angles]
    inner_start = [point(primitive.inner_radius, -half, angle) for angle in angles]
    inner_end = [point(primitive.inner_radius, half, angle) for angle in angles]
    faces: list[RenderFace] = []

    for index in range(segments):
        following = (index + 1) % segments
        shade = 0.68 + 0.30 * max(
            0.0,
            math.sin((index + 0.5) * math.tau / segments),
        )
        faces.extend(
            (
                RenderFace(
                    role=f"{primitive.role}_outer_{index:02d}",
                    points=(
                        outer_start[index],
                        outer_start[following],
                        outer_end[following],
                        outer_end[index],
                    ),
                    color=primitive.color,
                    shade=shade,
                    opacity=primitive.opacity,
                ),
                RenderFace(
                    role=f"{primitive.role}_inner_{index:02d}",
                    points=(
                        inner_start[following],
                        inner_start[index],
                        inner_end[index],
                        inner_end[following],
                    ),
                    color=primitive.color,
                    shade=max(0.42, shade * 0.66),
                    opacity=primitive.opacity,
                ),
                RenderFace(
                    role=f"{primitive.role}_end_start_{index:02d}",
                    points=(
                        outer_start[following],
                        outer_start[index],
                        inner_start[index],
                        inner_start[following],
                    ),
                    color=primitive.color,
                    shade=0.72,
                    opacity=primitive.opacity,
                ),
                RenderFace(
                    role=f"{primitive.role}_end_finish_{index:02d}",
                    points=(
                        outer_end[index],
                        outer_end[following],
                        inner_end[following],
                        inner_end[index],
                    ),
                    color=primitive.color,
                    shade=1.04,
                    opacity=primitive.opacity,
                ),
            )
        )
    return faces


def _sphere_faces(
    primitive: Primitive3D,
    *,
    longitude_segments: int = DEFAULT_SPHERE_LONGITUDE_SEGMENTS,
    latitude_segments: int = DEFAULT_SPHERE_LATITUDE_SEGMENTS,
) -> list[RenderFace]:
    """Build a closed faceted sphere suitable for VM-safe joint rendering."""

    rings: list[list[Vec3]] = []
    for latitude_index in range(1, latitude_segments):
        latitude = -math.pi / 2 + math.pi * latitude_index / latitude_segments
        ring_radius = math.cos(latitude) * primitive.radius
        local_y = math.sin(latitude) * primitive.radius
        rings.append(
            [
                _world_point(
                    primitive,
                    (
                        math.cos(longitude) * ring_radius,
                        local_y,
                        math.sin(longitude) * ring_radius,
                    ),
                )
                for longitude in (
                    index * math.tau / longitude_segments
                    for index in range(longitude_segments)
                )
            ]
        )

    bottom = _world_point(primitive, (0.0, -primitive.radius, 0.0))
    top = _world_point(primitive, (0.0, primitive.radius, 0.0))
    faces: list[RenderFace] = []

    for longitude_index in range(longitude_segments):
        following = (longitude_index + 1) % longitude_segments
        shade = 0.72 + 0.28 * max(
            0.0,
            math.sin((longitude_index + 0.5) * math.tau / longitude_segments),
        )
        faces.append(
            RenderFace(
                role=f"{primitive.role}_bottom_{longitude_index:02d}",
                points=(bottom, rings[0][following], rings[0][longitude_index]),
                color=primitive.color,
                shade=shade * 0.82,
                opacity=primitive.opacity,
            )
        )
        for latitude_index in range(len(rings) - 1):
            faces.append(
                RenderFace(
                    role=(
                        f"{primitive.role}_band_{latitude_index:02d}_"
                        f"{longitude_index:02d}"
                    ),
                    points=(
                        rings[latitude_index][longitude_index],
                        rings[latitude_index][following],
                        rings[latitude_index + 1][following],
                        rings[latitude_index + 1][longitude_index],
                    ),
                    color=primitive.color,
                    shade=shade,
                    opacity=primitive.opacity,
                )
            )
        faces.append(
            RenderFace(
                role=f"{primitive.role}_top_{longitude_index:02d}",
                points=(rings[-1][longitude_index], rings[-1][following], top),
                color=primitive.color,
                shade=min(1.20, shade * 1.12),
                opacity=primitive.opacity,
            )
        )
    return faces


def scene_faces(geometry: tuple[Primitive3D, ...]) -> list[RenderFace]:
    """Convert scene primitives to painter-sortable polygonal faces."""

    faces: list[RenderFace] = []
    for primitive in geometry:
        if primitive.kind == "box":
            primitive_faces = _box_faces(primitive)
        elif primitive.kind == "cylinder":
            primitive_faces = _cylinder_faces(primitive)
        elif primitive.kind == "tube":
            primitive_faces = _tube_faces(primitive)
        elif primitive.kind == "sphere":
            primitive_faces = _sphere_faces(primitive)
        elif primitive.kind == "frustum":
            primitive_faces = _frustum_faces(primitive)
        else:
            raise ValueError(f"Unsupported software 3D primitive: {primitive.kind}")
        faces.extend(
            replace(face, render_layer=primitive.render_layer)
            for face in primitive_faces
        )
    return faces


def sort_faces_for_painter(
    faces: list[RenderFace],
    *,
    yaw_degrees: float = DEFAULT_YAW_DEGREES,
    pitch_degrees: float = DEFAULT_PITCH_DEGREES,
) -> list[RenderFace]:
    """Sort far-to-near while honoring physical conveyor assembly depth.

    A side channel cannot share one fixed layer with the opposite channel:
    one is behind the roller bed and the other is in front. Classifying the
    two channel roles from the active camera keeps that relationship correct
    across the supported orbit range.
    """

    def face_depth(face: RenderFace) -> float:
        return sum(
            project_isometric(
                point,
                yaw_degrees=yaw_degrees,
                pitch_degrees=pitch_degrees,
            )[2]
            for point in face.points
        ) / len(face.points)

    rail_faces_by_assembly: dict[str, list[RenderFace]] = {}
    for face in faces:
        assembly, separator, local_role = face.role.rpartition("::")
        if not separator:
            local_role = face.role
            assembly = ""
        if local_role.startswith("side_rail_"):
            rail_faces_by_assembly.setdefault(assembly, []).append(face)

    rail_layers: dict[str, int] = {}
    for rail_faces in rail_faces_by_assembly.values():
        rail_roles = {face.role for face in rail_faces}
        if len(rail_roles) != 2:
            continue
        rail_depths = {
            role: sum(
                face_depth(face)
                for face in rail_faces
                if face.role == role
            )
            / sum(1 for face in rail_faces if face.role == role)
            for role in rail_roles
        }
        rail_layers[min(rail_depths, key=rail_depths.get)] = -10
        rail_layers[max(rail_depths, key=rail_depths.get)] = 10

    def assembly_layer(face: RenderFace) -> int:
        return rail_layers.get(face.role, face.render_layer)

    return sorted(
        faces,
        key=lambda face: (
            assembly_layer(face),
            face_depth(face),
        ),
    )


class SoftwareScene2Viewport:
    """Orbitable isometric 3D QWidget with no native child window."""

    renderer_id = SOFTWARE_RENDER_MODE
    uses_native_child_window = False

    def __init__(self, qt: dict[str, Any]) -> None:
        self.qt = qt
        self.compact_display = False
        self._font_family = self._load_ui_font()
        QtCore = qt["QtCore"]
        QtWidgets = qt["QtWidgets"]
        owner = self
        Signal = QtCore.Signal

        class SceneCanvas(QtWidgets.QWidget):
            equipmentHovered = Signal(object)
            equipmentSelected = Signal(object)
            equipmentCleared = Signal()
            viewChanged = Signal()

            def __init__(self) -> None:
                super().__init__()
                self.setObjectName("softwareSceneViewport")
                self.setMinimumSize(520, 360)
                self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                self.setAutoFillBackground(False)
                self.setAttribute(
                    QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent,
                    True,
                )
                self.setMouseTracking(True)

            def paintEvent(self, event: Any) -> None:  # noqa: N802
                del event
                owner._paint(self)

            def mousePressEvent(self, event: Any) -> None:  # noqa: N802
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    owner._drag_origin = event.position()
                    owner._drag_moved = False
                    owner._drag_yaw = owner._yaw_degrees
                    owner._drag_pitch = owner._pitch_degrees
                    owner._drag_mode = "orbit"
                    self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
                    owner._drag_origin = event.position()
                    owner._drag_pan_x = owner._pan_x
                    owner._drag_pan_y = owner._pan_y
                    owner._drag_mode = "pan"
                    self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                super().mousePressEvent(event)

            def mouseMoveEvent(self, event: Any) -> None:  # noqa: N802
                if owner._drag_origin is not None:
                    delta_x = event.position().x() - owner._drag_origin.x()
                    delta_y = event.position().y() - owner._drag_origin.y()
                    owner._drag_moved = not is_click_gesture(delta_x, delta_y)
                    if owner._drag_mode == "orbit":
                        owner._yaw_degrees = max(
                            MIN_YAW_DEGREES,
                            min(MAX_YAW_DEGREES, owner._drag_yaw - delta_x / 8.0),
                        )
                        owner._pitch_degrees = max(
                            MIN_PITCH_DEGREES,
                            min(MAX_PITCH_DEGREES, owner._drag_pitch + delta_y / 8.0),
                        )
                    elif owner._drag_mode == "pan":
                        owner._pan_x = max(
                            MIN_PAN_PIXELS,
                            min(MAX_PAN_PIXELS, owner._drag_pan_x + delta_x),
                        )
                        owner._pan_y = max(
                            MIN_PAN_PIXELS,
                            min(MAX_PAN_PIXELS, owner._drag_pan_y + delta_y),
                        )
                    self.viewChanged.emit()
                    self.update()
                elif owner._targets:
                    target = owner._hit_test(event.position())
                    if target != owner._hovered_target:
                        owner._hovered_target = target
                        self.setCursor(
                            QtCore.Qt.CursorShape.PointingHandCursor
                            if target is not None
                            else QtCore.Qt.CursorShape.ArrowCursor
                        )
                        self.update()
                    self.equipmentHovered.emit(target)
                super().mouseMoveEvent(event)

            def mouseReleaseEvent(self, event: Any) -> None:  # noqa: N802
                if (
                    event.button() == QtCore.Qt.MouseButton.LeftButton
                    and not owner._drag_moved
                ):
                    target = owner._hit_test(event.position())
                    if target is None:
                        owner._selected_target = None
                        self.equipmentCleared.emit()
                    else:
                        owner._selected_target = target
                        self.equipmentSelected.emit(target)
                    self.update()
                owner._drag_origin = None
                owner._drag_mode = None
                owner._drag_moved = False
                self.unsetCursor()
                super().mouseReleaseEvent(event)

            def wheelEvent(self, event: Any) -> None:  # noqa: N802
                step = event.angleDelta().y() / 1200.0
                owner._zoom = max(MIN_ZOOM, min(MAX_ZOOM, owner._zoom + step))
                self.viewChanged.emit()
                self.update()
                event.accept()

            def keyPressEvent(self, event: Any) -> None:  # noqa: N802
                if event.key() == QtCore.Qt.Key.Key_Escape:
                    owner._selected_target = None
                    self.equipmentCleared.emit()
                    self.update()
                    event.accept()
                    return
                super().keyPressEvent(event)

        self.container = SceneCanvas()
        self._snapshot: Any | None = None
        self._yaw_degrees = DEFAULT_YAW_DEGREES
        self._pitch_degrees = DEFAULT_PITCH_DEGREES
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._drag_origin: Any | None = None
        self._drag_yaw = self._yaw_degrees
        self._drag_pitch = self._pitch_degrees
        self._drag_pan_x = self._pan_x
        self._drag_pan_y = self._pan_y
        self._drag_mode: str | None = None
        self._drag_moved = False
        self._targets: tuple[InspectionTarget, ...] = ()
        self._hovered_target: InspectionTarget | None = None
        self._selected_target: InspectionTarget | None = None

    def _load_ui_font(self) -> str:
        """Load a Windows UI font explicitly for frozen/offscreen Qt builds.

        Some PyInstaller/offscreen Qt configurations expose an empty font
        database. QPainter then substitutes missing-glyph boxes even though the
        font exists on the host. Loading the installed Windows font by filename
        keeps overlay text readable without redistributing a font file.
        """

        QtGui = self.qt["QtGui"]
        for font_path in (
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
        ):
            if not font_path.is_file():
                continue
            font_id = QtGui.QFontDatabase.addApplicationFont(str(font_path))
            if font_id < 0:
                continue
            families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return str(families[0])
        return "Sans Serif"

    def reset_camera(self) -> None:
        self._yaw_degrees = DEFAULT_YAW_DEGREES
        self._pitch_degrees = DEFAULT_PITCH_DEGREES
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self.container.viewChanged.emit()
        self.container.update()

    def frame_selected_target(self) -> None:
        """Center and size the selected inspection target for focused review."""

        target = self._selected_target
        if target is None:
            return
        bounds = self.container.rect()
        if bounds.width() <= 0 or bounds.height() <= 0:
            return
        points = target.outline_points or (
            (target.bounds[0], target.bounds[1], target.bounds[2]),
            (target.bounds[3], target.bounds[4], target.bounds[5]),
        )
        center = (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
            sum(point[2] for point in points) / len(points),
        )
        projected = [
            project_isometric(
                point,
                yaw_degrees=self._yaw_degrees,
                pitch_degrees=self._pitch_degrees,
            )
            for point in points
        ]
        projected_width = max(item[0] for item in projected) - min(item[0] for item in projected)
        projected_height = max(item[1] for item in projected) - min(item[1] for item in projected)
        compact_height = max(160.0, float(bounds.height()) - 16.0)
        base_scale = min(
            bounds.width() / 10.7,
            (compact_height if self.compact_display else bounds.height()) / 6.35,
        )
        if projected_width > 0.01 and projected_height > 0.01:
            desired_width = bounds.width() * 0.56
            desired_height = bounds.height() * (0.42 if self.compact_display else 0.48)
            self._zoom = max(
                0.72,
                min(
                    1.42,
                    min(
                        desired_width / (projected_width * base_scale),
                        desired_height / (projected_height * base_scale),
                    ),
                ),
            )
        scale = base_scale * self._zoom
        center_projected = project_isometric(
            center,
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )
        baseline_y = (
            bounds.height() * 0.52
            if self.compact_display
            else bounds.height() * 0.60
        )
        desired_y = bounds.height() * (0.53 if self.compact_display else 0.56)
        self._pan_x = max(-400.0, min(400.0, -center_projected[0] * scale))
        self._pan_y = max(
            -400.0,
            min(400.0, desired_y - baseline_y - center_projected[1] * scale),
        )
        self.container.viewChanged.emit()
        self.container.update()

    def selected_target(self) -> InspectionTarget | None:
        return self._selected_target

    def clear_selection(self) -> None:
        self._selected_target = None
        self.container.equipmentCleared.emit()
        self.container.update()

    def _hit_test(self, position: Any) -> InspectionTarget | None:
        bounds = self.container.rect()
        scale = self._scene_scale(bounds)
        return hit_test_targets(
            (float(position.x()), float(position.y())),
            self._targets,
            lambda point: (
                float(self._screen_point(point, bounds, scale).x()),
                float(self._screen_point(point, bounds, scale).y()),
            ),
        )

    def update(self, snapshot: Any) -> None:
        self._snapshot = snapshot
        self._targets = build_scene2_targets(self._model())
        if self._selected_target is not None:
            selected_id = self._selected_target.target_id
            self._selected_target = next(
                (target for target in self._targets if target.target_id == selected_id),
                None,
            )
        self.container.update()

    def _color(self, value: str, alpha: int = 255) -> Any:
        color = self.qt["QtGui"].QColor(value)
        color.setAlpha(alpha)
        return color

    def _pen(self, color: str, width: float = 1.0) -> Any:
        QtCore = self.qt["QtCore"]
        pen = self.qt["QtGui"].QPen(self._color(color), width)
        pen.setCosmetic(True)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        return pen

    def _model(self) -> Any | None:
        return getattr(self._snapshot, "model", None)

    def _ready(self) -> bool:
        return bool(getattr(self._snapshot, "ready", False))

    def _error(self) -> bool:
        return bool(getattr(self._snapshot, "error", None))

    def _telemetry_valid(self) -> bool:
        """Whether indicator colors may claim controller-confirmed state."""

        connection = getattr(
            getattr(self._snapshot, "connection", None),
            "value",
            "disconnected",
        )
        return (
            connection == "connected"
            and self._ready()
            and not self._error()
        )

    def _scene_scale(self, bounds: Any) -> float:
        usable_height = (
            max(160.0, float(bounds.height()) - 16.0)
            if self.compact_display
            else bounds.height()
        )
        return (
            min(bounds.width() / 10.7, usable_height / 6.35)
            * self._zoom
        )

    def _screen_point(
        self,
        point: Vec3,
        bounds: Any,
        scale: float,
    ) -> Any:
        projected = project_isometric(
            point,
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )
        return self.qt["QtCore"].QPointF(
            bounds.center().x() + projected[0] * scale + self._pan_x,
            (
                bounds.height() * 0.52
                if self.compact_display
                else bounds.height() * 0.60
            )
            + projected[1] * scale
            + self._pan_y,
        )

    def _shade_color(
        self,
        value: str,
        shade: float,
        opacity: int,
    ) -> Any:
        color = self._color(value, opacity)
        if shade >= 1.0:
            color = color.lighter(round(shade * 100))
        else:
            color = color.darker(round(100 / max(shade, 0.05)))
        color.setAlpha(opacity)
        return color

    def _material_name(self, role: str, color: str) -> str:
        """Classify the authored primitive into a restrained render material."""

        normalized = role.lower()
        if normalized.startswith(("roller_", "drive_roller")):
            return "aluminum"
        if normalized.startswith(("pusher_plate", "safety_", "guard_")):
            return "safety_yellow"
        if normalized.startswith(("photoeye", "stacklight", "sensor_")):
            return "plastic"
        if normalized.startswith(("product_carton", "package")):
            return "carton"
        if normalized.startswith(("witness", "laser", "beam")):
            return "indicator"
        if color.upper() in {"#167EA3", "#2E8BD1"}:
            return "painted_blue"
        return "painted_steel"

    def _face_normal(self, points: tuple[Vec3, ...]) -> Vec3:
        """Return a normalized world-space polygon normal for fixed lighting."""

        if len(points) < 3:
            return (0.0, 1.0, 0.0)
        first, second, third = points[:3]
        a = tuple(second[index] - first[index] for index in range(3))
        b = tuple(third[index] - first[index] for index in range(3))
        normal = (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )
        length = math.sqrt(sum(value * value for value in normal))
        if length <= 1e-6:
            return (0.0, 1.0, 0.0)
        return tuple(value / length for value in normal)  # type: ignore[return-value]

    def _material_shade(self, face: RenderFace) -> float:
        """Apply fixed key/fill lighting while retaining authored face contrast."""

        material = self._material_name(face.role, face.color)
        normal = self._face_normal(face.points)
        key = (0.48, 0.86, -0.32)
        key_length = math.sqrt(sum(value * value for value in key))
        lambert = max(
            0.0,
            sum(normal[index] * key[index] for index in range(3)) / key_length,
        )
        material_bias = {
            "aluminum": 1.08,
            "painted_steel": 0.96,
            "painted_blue": 0.94,
            "safety_yellow": 1.02,
            "plastic": 0.98,
            "carton": 0.99,
            "indicator": 1.04,
        }[material]
        directional = 0.48 + 0.68 * lambert
        return max(
            0.36,
            min(1.28, face.shade * 0.56 + directional * material_bias * 0.44),
        )

    def _should_outline(self, role: str) -> bool:
        """Keep outlines for fabricated seams, safety parts, and inspection cues."""

        normalized = role.lower()
        return normalized.startswith(
            (
                "side_rail_",
                "leg_",
                "foot_",
                "pusher_plate",
                "photoeye",
                "stacklight",
                "guard_",
            )
        )

    def _contact_shadow_points(
        self,
        primitive: Primitive3D,
        bounds: Any,
        scale: float,
        inset: float = 0.0,
    ) -> list[Any]:
        """Project a deterministic primitive footprint onto the floor plane."""

        cx, _cy, cz = primitive.center
        if primitive.kind == "box":
            sx, _sy, sz = primitive.size
            footprint = (
                (cx - sx / 2 - inset, 0.018, cz - sz / 2 - inset),
                (cx + sx / 2 + inset, 0.018, cz - sz / 2 - inset),
                (cx + sx / 2 + inset, 0.018, cz + sz / 2 + inset),
                (cx - sx / 2 - inset, 0.018, cz + sz / 2 + inset),
            )
        else:
            radius = max(primitive.radius + inset, 0.04)
            footprint = tuple(
                (
                    cx + math.cos(index * math.tau / 12) * radius,
                    0.018,
                    cz + math.sin(index * math.tau / 12) * radius,
                )
                for index in range(12)
            )
        return [self._screen_point(point, bounds, scale) for point in footprint]

    def _draw_contact_shadows(
        self,
        painter: Any,
        bounds: Any,
        scale: float,
        geometry: tuple[Primitive3D, ...],
    ) -> None:
        """Paint two restrained footprint layers beneath grounded assets."""

        QtGui = self.qt["QtGui"]
        painter.setPen(self.qt["QtCore"].Qt.PenStyle.NoPen)
        for primitive in geometry:
            if primitive.opacity < 220 or primitive.center[1] < 0.10:
                continue
            if primitive.role.startswith(("photoeye_beam", "roller_witness")):
                continue
            for inset, opacity in (
                (0.085, 10),
                (0.055, 16),
                (0.032, 24),
                (0.012, 44),
            ):
                footprint = self._contact_shadow_points(
                    primitive,
                    bounds,
                    scale,
                    inset=inset,
                )
                painter.setBrush(self._color(CONTACT_SHADOW, opacity))
                painter.drawPolygon(QtGui.QPolygonF(footprint))

    def _face_edge_pen(self, face: RenderFace) -> Any:
        """Return a material edge cue based on the existing face lighting."""

        if face.shade >= 1.0:
            return self._pen(MATERIAL_EDGE_LIGHT, 0.72)
        if face.shade <= 0.62:
            return self._pen(MATERIAL_EDGE_DARK, 0.90)
        return self._pen("#29434C", 0.58)

    def _draw_material_detail(
        self,
        painter: Any,
        face: RenderFace,
        points: list[Any],
    ) -> None:
        """Add sparse role-driven cues without changing scene geometry."""

        if not points or len(points) < 3:
            return
        role = face.role
        if role.startswith(("roller_", "drive_")) and face.shade >= 0.9:
            painter.setPen(self._pen("#D7E2E4", 0.42))
            painter.drawLine(points[0], points[-1])
        elif role.startswith(("side_rail_", "leg_", "foot_")):
            painter.setPen(self._pen("#758A90", 0.38))
            painter.drawLine(points[0], points[1])
        elif role.startswith("product_carton") and face.shade >= 1.0:
            painter.setPen(self._pen("#E5B66A", 0.46))
            painter.drawLine(points[0], points[1])
        elif role.startswith("pusher_plate") and face.shade >= 1.0:
            painter.setPen(self._pen("#FFE08A", 0.50))
            painter.drawLine(points[0], points[1])

    def _paint(self, canvas: Any) -> None:
        QtCore = self.qt["QtCore"]
        QtGui = self.qt["QtGui"]
        painter = QtGui.QPainter(canvas)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(
            QtGui.QPainter.RenderHint.TextAntialiasing,
            True,
        )

        bounds = QtCore.QRectF(canvas.rect())
        gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, bounds.height())
        gradient.setColorAt(0.0, self._color("#102832"))
        gradient.setColorAt(0.52, self._color(BACKGROUND))
        gradient.setColorAt(1.0, self._color(BACKGROUND_DEEP))
        painter.fillRect(bounds, gradient)

        scale = self._scene_scale(bounds)
        self._draw_floor(painter, bounds, scale)
        self._draw_scene(painter, bounds, scale)
        self._draw_overlay(painter, bounds)
        painter.end()

    def _draw_floor(self, painter: Any, bounds: Any, scale: float) -> None:
        QtGui = self.qt["QtGui"]
        floor_corners = [
            self._screen_point(point, bounds, scale)
            for point in (
                (-8.0, 0.0, -6.0),
                (8.0, 0.0, -6.0),
                (8.0, 0.0, 6.0),
                (-8.0, 0.0, 6.0),
            )
        ]
        painter.setPen(self._pen("#25414B", 1.0))
        painter.setBrush(self._color("#102730", 210))
        painter.drawPolygon(QtGui.QPolygonF(floor_corners))

        for x in range(-8, 9):
            major = x % 5 == 0
            painter.setPen(self._pen(GRID_MAJOR if major else GRID_MINOR))
            painter.drawLine(
                self._screen_point((float(x), 0.005, -6.0), bounds, scale),
                self._screen_point((float(x), 0.005, 6.0), bounds, scale),
            )
        for z in range(-6, 7):
            major = z % 5 == 0
            painter.setPen(self._pen(GRID_MAJOR if major else GRID_MINOR))
            painter.drawLine(
                self._screen_point((-8.0, 0.005, float(z)), bounds, scale),
                self._screen_point((8.0, 0.005, float(z)), bounds, scale),
            )

    def _draw_shadow(self, painter: Any, bounds: Any, scale: float) -> None:
        QtGui = self.qt["QtGui"]
        painter.setPen(self.qt["QtCore"].Qt.PenStyle.NoPen)
        for inset, opacity in ((0.28, 18), (0.14, 30), (0.0, 48)):
            points = [
                self._screen_point(point, bounds, scale)
                for point in (
                    (-3.9 - inset, 0.012, -1.35 - inset),
                    (3.9 + inset, 0.012, -1.35 - inset),
                    (3.9 + inset, 0.012, 2.45 + inset),
                    (-3.9 - inset, 0.012, 2.45 + inset),
                )
            ]
            painter.setBrush(self._color(CONTACT_SHADOW, opacity))
            painter.drawPolygon(QtGui.QPolygonF(points))

    def _draw_scene(self, painter: Any, bounds: Any, scale: float) -> None:
        QtCore = self.qt["QtCore"]
        QtGui = self.qt["QtGui"]
        geometry = build_scene_geometry(
            self._model(),
            ready=self._ready(),
            error=self._error(),
            telemetry_valid=self._telemetry_valid(),
        )
        self._draw_contact_shadows(painter, bounds, scale, geometry)
        faces = sort_faces_for_painter(
            scene_faces(geometry),
            yaw_degrees=self._yaw_degrees,
            pitch_degrees=self._pitch_degrees,
        )

        # Draw the photoeye as a laser-like dashed centerline. The solid box
        # primitive remains in the geometry contract, but is not painted so
        # its top face cannot visually aim at the pusher's corner.
        # Beam interruption is valid process feedback, not a fault. Reserve
        # the fault red for renderer/runtime errors so operators do not read a
        # normal detected part as an alarm.
        model = self._model()
        photoeye_blocked = bool(
            model is not None
            and getattr(model, "photoeye_blocked", False)
        )
        # The beam is a visual indicator of the local plant model.  It may
        # only use the proof/process colors after a connected, ready exchange
        # has confirmed the controller session.  This keeps a disconnected
        # or stale view from looking like physical PLC evidence.
        laser_color = (
            AMBER
            if self._telemetry_valid() and photoeye_blocked
            else CYAN
            if self._telemetry_valid()
            else LOCAL_AMBER
            if photoeye_blocked
            else LOCAL_UNAVAILABLE
        )
        laser_pen = QtGui.QPen(
            self._color(laser_color, 230),
            2.0,
        )
        laser_pen.setCosmetic(True)
        laser_pen.setStyle(QtCore.Qt.PenStyle.DashLine)
        laser_pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(laser_pen)
        painter.drawLine(
            self._screen_point((0.0, 1.45, -0.95), bounds, scale),
            self._screen_point((0.0, 1.45, 0.95), bounds, scale),
        )

        for face in faces:
            if face.role.startswith("photoeye_beam"):
                continue
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
            painter.drawPolygon(QtGui.QPolygonF(points))
            # A narrow orientation-aware outline acts as a stable bevel cue
            # for the flat primitives used by the software renderer.
            if self._should_outline(face.role):
                painter.setPen(self._face_edge_pen(face))
                painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
                painter.drawPolygon(QtGui.QPolygonF(points))
            self._draw_material_detail(painter, face, points)

        self._draw_inspection_overlay(painter, bounds, scale)

    def _draw_inspection_overlay(
        self,
        painter: Any,
        bounds: Any,
        scale: float,
    ) -> None:
        """Draw restrained semantic selection without recoloring plant state."""

        target = self._selected_target or self._hovered_target
        if target is None:
            return
        QtCore = self.qt["QtCore"]
        QtGui = self.qt["QtGui"]
        polygons = projected_target_polygons(
            (target,),
            lambda point: (
                float(self._screen_point(point, bounds, scale).x()),
                float(self._screen_point(point, bounds, scale).y()),
            ),
        )
        polygon = QtGui.QPolygonF(
            [QtCore.QPointF(x, y) for x, y in polygons[target.target_id]]
        )
        painter.setBrush(self._color("#55C7E8", 24 if self._selected_target is None else 58))
        painter.setPen(self._pen("#55C7E8", 1.8 if self._selected_target is None else 2.2))
        painter.drawPolygon(polygon)
        anchor = self._screen_point(
            ((target.bounds[0] + target.bounds[3]) / 2,
             target.bounds[4] + 0.12,
             (target.bounds[2] + target.bounds[5]) / 2),
            bounds,
            scale,
        )
        painter.setBrush(self._color("#0B171D", 242))
        painter.setPen(self._pen("#55C7E8", 2.0 if self._selected_target else 1.0))
        label = target.label.upper()
        if self._selected_target is None:
            label += "  |  " + getattr(
                self,
                "inspection_hover_label",
                "CLICK TO INSPECT",
            )
        else:
            label += "  |  " + getattr(
                self,
                "inspection_selected_label",
                "LOCAL MODEL",
            )
        # Keep the semantic callout inside the viewport at compact/high-DPI
        # sizes.  The inspector remains the authoritative detail surface;
        # this overlay must never become a clipped second source of truth.
        label_width = min(310, max(170, 9 * len(label) + 26))
        label_width = min(label_width, max(150, bounds.width() - 24))
        safe_margin = 28
        if getattr(self, "review_authoring_callout", False):
            preferred_x = anchor.x() - label_width / 2
        elif getattr(self, "review_handoff_callout", False):
            preferred_x = bounds.width() - label_width - safe_margin
        elif getattr(self, "short_inspection_leader", False):
            preferred_x = anchor.x() - label_width / 2
        else:
            preferred_x = anchor.x() + 22
        if preferred_x + label_width > bounds.width() - safe_margin:
            preferred_x = anchor.x() - label_width - 22
        label_x = max(
            safe_margin,
            min(bounds.width() - label_width - safe_margin, preferred_x),
        )
        preferred_y = (
            (max(48, anchor.y() - 94) if self.compact_display else max(116, anchor.y() - 110))
            if getattr(self, "review_authoring_callout", False)
            else (56 if self.compact_display else 122)
            if getattr(self, "review_handoff_callout", False)
            else
            max(100, anchor.y() - 44)
            if self.compact_display and getattr(self, "short_inspection_leader", False)
            else max(100, anchor.y() + 10)
            if self.compact_display
            else max(78, anchor.y() - 66)
        )
        label_y = max(12, min(bounds.height() - 32, preferred_y))
        if not getattr(self, "review_callout_no_leader", False):
            painter.drawLine(
                QtCore.QPointF(anchor.x(), anchor.y()),
                QtCore.QPointF(label_x, label_y + 12),
            )
        painter.drawRoundedRect(
            QtCore.QRectF(label_x, label_y, label_width, 26),
            4,
            4,
        )
        painter.setFont(self._font(self._font_family, 9, bold=True))
        painter.drawText(
            QtCore.QRectF(label_x + 10, label_y + 1, label_width - 16, 24),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
            label,
        )

    def _font(
        self,
        family: str,
        pixel_size: int,
        *,
        bold: bool = False,
    ) -> Any:
        QtGui = self.qt["QtGui"]
        font = QtGui.QFont(family)
        font.setPixelSize(pixel_size)
        if bold:
            font.setWeight(QtGui.QFont.Weight.DemiBold)
        return font

    def _draw_overlay(self, painter: Any, bounds: Any) -> None:
        QtCore = self.qt["QtCore"]
        model = self._model()
        state_value = getattr(getattr(model, "state", None), "value", None)
        state = str(state_value or "awaiting_plc").replace("_", " ").upper()
        connected = getattr(
            getattr(self._snapshot, "connection", None),
            "value",
            "disconnected",
        )

        # The compact shell already owns the scene title and orbit affordance
        # in scene_bar. Keep the canvas overlay to one concise state ribbon so
        # the plant geometry is not buried beneath duplicate chrome at 960 px.
        if self.compact_display:
            painter.setFont(self._font(self._font_family, 9, bold=True))
            painter.setPen(self._pen(LOCAL_AMBER))
            painter.setBrush(self._color("#0A1E25", 230))
            painter.drawRoundedRect(
                QtCore.QRectF(12, 8, max(bounds.width() - 24, 180), 24),
                4,
                4,
            )
            painter.drawText(
                QtCore.QRectF(22, 9, max(bounds.width() - 44, 160), 22),
                QtCore.Qt.AlignmentFlag.AlignLeft,
                "LOCAL MODEL  ·  CONTROLLER DISCONNECTED  ·  PLC TRANSPORT OFF",
            )
            return

        painter.setFont(self._font(self._font_family, 14, bold=True))
        painter.setPen(self._pen("#DDECEF"))
        painter.drawText(
            QtCore.QRectF(20, 16, bounds.width() - 40, 24),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            "CONVEYOR PUSHER CELL",
        )
        telemetry_valid = self._telemetry_valid()
        painter.setFont(self._font(self._font_family, 10, bold=True))
        painter.setPen(self._pen("#B9D6DB" if telemetry_valid else LOCAL_AMBER))
        status_text = (
            (
                f"{state}  ·  SYNTHETIC HEALTHY  ·  "
                "FIXTURE VERIFIED"
                if getattr(self, "visual_qa_fixture", False)
                else f"{state}  ·  CONTROLLER TELEMETRY VERIFIED  ·  "
                f"PLC SESSION {str(connected).upper()}"
            )
            if telemetry_valid
            else f"{state}  •  LOCAL MODEL  •  SEE CONTROLLER BANNER"
        )
        painter.setBrush(self._color("#0A1E25", 230))
        painter.drawRoundedRect(QtCore.QRectF(16, 42, min(bounds.width() - 32, 620), 28), 4, 4)
        painter.drawText(
            QtCore.QRectF(28, 44, min(bounds.width() - 56, 600), 24),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            status_text,
        )
        painter.setPen(self._pen("#6F8992"))
        painter.drawText(
            QtCore.QRectF(
                20,
                bounds.height() - 31,
                bounds.width() - 40,
                20,
            ),
            QtCore.Qt.AlignmentFlag.AlignRight,
            "CAD VIEW  |  LEFT DRAG ORBIT  |  MIDDLE DRAG PAN  |  WHEEL ZOOM",
        )
