"""Manufacturer-referenced native asset geometry for RungProof review.

The builders return the same renderer-neutral ``Primitive3D`` records used by
the VM-safe isometric scene. Assets are intentionally isolated at the origin
so they can be rendered and approved independently before scenes reuse them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

from tools.native_software_viewport import Primitive3D, Vec3


STEEL = "#536873"
DARK_STEEL = "#26343C"
LIGHT_STEEL = "#AAB7BD"
ALUMINUM = "#BBC7CC"
SAFETY_YELLOW = "#F2B705"
MOTOR_BLUE = "#167EA3"
SENSOR_BLUE = "#2E8BD1"
GREEN = "#16A34A"
AMBER = "#F2B94B"
RED = "#E53935"
FASTENER = "#1A252A"
EDGE_HIGHLIGHT = "#D5E0E3"
LABEL_DARK = "#263B43"


@dataclass(frozen=True, slots=True)
class NativeAssetDefinition:
    approval_id: str
    asset_type: str
    label: str
    reference_name: str
    reference_url: str
    builder: Callable[[], tuple[Primitive3D, ...]]
    view_span: float = 4.8
    category: str = "general"
    tags: tuple[str, ...] = ()


class GeometryBuilder:
    """Small construction API shared by all asset builders."""

    def __init__(self) -> None:
        self.geometry: list[Primitive3D] = []

    def box(
        self,
        role: str,
        center: Vec3,
        size: Vec3,
        color: str,
        *,
        rotation: Vec3 = (0.0, 0.0, 0.0),
        opacity: int = 255,
        render_layer: int = 0,
    ) -> None:
        self.geometry.append(
            Primitive3D(
                role=role,
                kind="box",
                center=center,
                size=size,
                color=color,
                rotation=rotation,
                opacity=opacity,
                render_layer=render_layer,
            )
        )

    def cylinder(
        self,
        role: str,
        center: Vec3,
        radius: float,
        length: float,
        color: str,
        *,
        axis: str = "y",
        rotation: Vec3 = (0.0, 0.0, 0.0),
        opacity: int = 255,
        end_caps: bool = True,
        render_layer: int = 0,
    ) -> None:
        self.geometry.append(
            Primitive3D(
                role=role,
                kind="cylinder",
                center=center,
                radius=radius,
                length=length,
                end_caps=end_caps,
                axis=axis,
                color=color,
                rotation=rotation,
                opacity=opacity,
                render_layer=render_layer,
            )
        )

    def tube(
        self,
        role: str,
        center: Vec3,
        radius: float,
        inner_radius: float,
        length: float,
        color: str,
        *,
        axis: str = "y",
        rotation: Vec3 = (0.0, 0.0, 0.0),
        opacity: int = 255,
    ) -> None:
        self.geometry.append(
            Primitive3D(
                role=role,
                kind="tube",
                center=center,
                radius=radius,
                inner_radius=inner_radius,
                length=length,
                axis=axis,
                color=color,
                rotation=rotation,
                opacity=opacity,
            )
        )

    def sphere(
        self,
        role: str,
        center: Vec3,
        radius: float,
        color: str,
        *,
        rotation: Vec3 = (0.0, 0.0, 0.0),
        opacity: int = 255,
    ) -> None:
        self.geometry.append(
            Primitive3D(
                role=role,
                kind="sphere",
                center=center,
                radius=radius,
                color=color,
                rotation=rotation,
                opacity=opacity,
            )
        )

    def frustum(
        self,
        role: str,
        center: Vec3,
        bottom_radius: float,
        top_radius: float,
        length: float,
        color: str,
        *,
        axis: str = "y",
        rotation: Vec3 = (0.0, 0.0, 0.0),
        opacity: int = 255,
        end_caps: bool = True,
        render_layer: int = 0,
    ) -> None:
        self.geometry.append(
            Primitive3D(
                role=role,
                kind="frustum",
                center=center,
                radius=bottom_radius,
                top_radius=top_radius,
                length=length,
                end_caps=end_caps,
                axis=axis,
                color=color,
                rotation=rotation,
                opacity=opacity,
                render_layer=render_layer,
            )
        )

    def done(self) -> tuple[Primitive3D, ...]:
        return tuple(self.geometry)


def _add_edge_trim(
    g: GeometryBuilder,
    role: str,
    center: Vec3,
    size: Vec3,
    color: str = EDGE_HIGHLIGHT,
    *,
    render_layer: int = 1,
) -> None:
    """Add a restrained raised edge highlight without changing the renderer.

    The software renderer has no material or bevel channel. Thin trim is the
    smallest safe geometry-only cue for a folded panel or machined edge.
    """

    g.box(role, center, size, color, render_layer=render_layer)


def _add_flange_fasteners(
    g: GeometryBuilder,
    prefix: str,
    x: float,
    y: float,
    z: float,
    *,
    radius: float = 0.055,
    length: float = 0.24,
    axis: str = "x",
    render_layer: int = 1,
) -> None:
    """Place a readable eight-bolt pattern on an x-axis flange."""

    bolt_circle = 0.34
    for index in range(8):
        angle = math.radians(index * 45.0)
        g.cylinder(
            f"{prefix}_bolt_{index:02d}",
            (x, y + bolt_circle * math.cos(angle), z + bolt_circle * math.sin(angle)),
            radius,
            length,
            FASTENER,
            axis=axis,
            render_layer=render_layer,
        )


def _add_legend_surface(
    g: GeometryBuilder,
    prefix: str,
    center: Vec3,
    size: Vec3,
) -> None:
    """Build a framed, blank legend surface for later text annotation."""

    x, y, z = center
    sx, sy, sz = size
    g.box(
        f"{prefix}_frame",
        center,
        (sx + 0.08, sy + 0.08, sz + 0.02),
        LABEL_DARK,
    )
    g.box(f"{prefix}_plate", center, size, "#F5F2DF", render_layer=1)
    # Raised text bars keep the plate readable in the asset gallery without
    # baking an equipment tag into reusable geometry.
    bar_z = z + sz / 2 + 0.012
    for index, width in enumerate((sx * 0.62, sx * 0.38)):
        g.box(
            f"{prefix}_mark_{index}",
            (x - sx * 0.08, y + (index - 0.5) * sy * 0.30, bar_z),
            (width, max(0.018, sy * 0.10), 0.012),
            LABEL_DARK,
            render_layer=2,
        )


def _add_panel_fasteners(
    g: GeometryBuilder,
    prefix: str,
    points: tuple[Vec3, ...],
    *,
    axis: str = "z",
    radius: float = 0.032,
    length: float = 0.06,
    render_layer: int = 2,
) -> None:
    """Add restrained visible fasteners to a panel or inspection cover.

    Fasteners are deliberately separate primitives rather than baked into a
    panel so the renderer can preserve material contrast and depth ordering.
    The helper is limited to gallery readability; it does not add interaction
    or alter any asset's process geometry.
    """

    for index, point in enumerate(points):
        g.cylinder(
            f"{prefix}_fastener_{index:02d}",
            point,
            radius,
            length,
            FASTENER,
            axis=axis,
            render_layer=render_layer,
        )


def _add_panel_seam(
    g: GeometryBuilder,
    role: str,
    center: Vec3,
    size: Vec3,
    *,
    color: str = DARK_STEEL,
    render_layer: int = 2,
) -> None:
    """Add a thin shadow seam where two fabricated panels meet."""

    g.box(role, center, size, color, render_layer=render_layer)


def _build_motor() -> tuple[Primitive3D, ...]:
    """Foot-mounted IC411 induction motor based on SIMOTICS GP/SD."""

    g = GeometryBuilder()
    axis_y = 0.84
    g.cylinder(
        "motor_frame",
        (0.0, axis_y, 0.0),
        0.54,
        1.55,
        MOTOR_BLUE,
        axis="x",
    )
    # IC411 cooling fins run along the motor axis. Circumferential rings read
    # as artificial banding and are not representative of a cast motor frame.
    for index, angle in enumerate(range(0, 360, 45)):
        radians = math.radians(angle)
        g.box(
            f"cooling_rib_{index:02d}",
            (
                0.0,
                axis_y + 0.56 * math.cos(radians),
                0.56 * math.sin(radians),
            ),
            (1.38, 0.08, 0.16),
            "#126D8C",
            rotation=(float(angle), 0.0, 0.0),
        )
    g.cylinder(
        "drive_end_bell",
        (0.84, axis_y, 0.0),
        0.50,
        0.18,
        "#31515D",
        axis="x",
    )
    g.cylinder(
        "fan_end_bell",
        (-0.86, axis_y, 0.0),
        0.50,
        0.20,
        "#31515D",
        axis="x",
    )
    g.cylinder(
        "fan_cover",
        (-1.05, axis_y, 0.0),
        0.48,
        0.24,
        "#263F49",
        axis="x",
    )
    g.cylinder(
        "output_shaft",
        (1.08, axis_y, 0.0),
        0.12,
        0.42,
        LIGHT_STEEL,
        axis="x",
    )
    g.box(
        "terminal_box",
        (0.18, 1.40, 0.0),
        (0.58, 0.32, 0.46),
        DARK_STEEL,
    )
    g.box(
        "terminal_box_lid",
        (0.18, 1.575, 0.0),
        (0.62, 0.05, 0.50),
        "#41545D",
    )
    g.cylinder(
        "cable_gland",
        (0.18, 1.41, 0.30),
        0.08,
        0.16,
        "#151E22",
        axis="z",
    )
    for index, x in enumerate((-0.50, 0.50)):
        for z in (-0.36, 0.36):
            g.box(
                f"mounting_foot_{index}_{'n' if z < 0 else 'p'}",
                (x, 0.23, z),
                (0.52, 0.16, 0.28),
                "#31515D",
            )
            g.cylinder(
                f"foot_hole_{index}_{'n' if z < 0 else 'p'}",
                (x, 0.32, z),
                0.045,
                0.19,
                "#10181C",
                axis="y",
            )
    g.box(
        "nameplate",
        (0.24, 1.10, 0.50),
        (0.44, 0.20, 0.025),
        "#D3DBDE",
        rotation=(0.0, 0.0, 0.0),
    )
    _add_panel_seam(g, "nameplate_border", (0.24, 1.10, 0.518), (0.48, 0.018, 0.018), color=FASTENER)
    _add_panel_fasteners(
        g,
        "nameplate",
        ((0.07, 1.10, 0.522), (0.41, 1.10, 0.522)),
        radius=0.022,
        length=0.025,
    )
    _add_panel_fasteners(
        g,
        "terminal_box",
        ((-0.02, 1.615, -0.16), (0.38, 1.615, -0.16), (-0.02, 1.615, 0.16), (0.38, 1.615, 0.16)),
        axis="y",
        radius=0.022,
        length=0.025,
    )
    _add_edge_trim(
        g,
        "terminal_box_lid_edge",
        (0.18, 1.61, 0.0),
        (0.62, 0.018, 0.50),
        EDGE_HIGHLIGHT,
    )
    _add_flange_fasteners(
        g,
        "drive_end",
        0.94,
        axis_y,
        0.0,
        radius=0.035,
        length=0.08,
    )
    return g.done()


def _build_conveyor() -> tuple[Primitive3D, ...]:
    """Supported roller conveyor with a guarded direct discharge head drive."""

    g = GeometryBuilder()
    for index in range(11):
        x = -2.50 + index * 0.50
        g.box(
            f"crossmember_{index:02d}",
            (x, 0.70, 0.0),
            (0.12, 0.12, 1.55),
            DARK_STEEL,
        )
        g.cylinder(
            "drive_roller" if index == 10 else f"roller_{index:02d}",
            (x, 0.94, 0.0),
            0.12 if index == 10 else 0.10,
            1.08,
            "#60737C" if index == 10 else ALUMINUM,
            axis="z",
            end_caps=False,
        )
    for z in (-0.86, 0.86):
        g.box(
            f"side_rail_{'left' if z < 0 else 'right'}",
            (0.0, 0.90, z),
            (5.35, 0.24, 0.14),
            STEEL,
        )
        g.box(
            f"wear_strip_{'left' if z < 0 else 'right'}",
            (0.0, 0.90, z - (0.075 if z > 0 else -0.075)),
            (5.18, 0.035, 0.025),
            LIGHT_STEEL,
            render_layer=1,
        )
    for x in (-1.90, 1.90):
        for z in (-0.65, 0.65):
            g.box(
                f"leg_{x}_{z}",
                (x, 0.40, z),
                (0.14, 0.80, 0.14),
                DARK_STEEL,
            )
            g.box(
                f"foot_{x}_{z}",
                (x, 0.07, z),
                (0.48, 0.10, 0.28),
                STEEL,
            )
            g.cylinder(
                f"foot_anchor_{x}_{z}",
                (x, 0.135, z),
                0.035,
                0.025,
                FASTENER,
                axis="y",
                render_layer=1,
            )
    drive_x = 2.50
    drive_y = 0.94
    g.cylinder(
        "drive_shaft",
        (drive_x, drive_y, 0.87),
        0.07,
        0.32,
        LIGHT_STEEL,
        axis="z",
        render_layer=20,
    )
    g.box(
        "coupling_guard",
        (drive_x, drive_y, 1.08),
        (0.46, 0.46, 0.42),
        SAFETY_YELLOW,
        render_layer=20,
    )
    _add_edge_trim(
        g,
        "coupling_guard_top_edge",
        (drive_x, drive_y, 1.30),
        (0.46, 0.46, 0.025),
        SAFETY_YELLOW,
        render_layer=21,
    )
    g.cylinder(
        "bearing_flange",
        (drive_x, drive_y, 1.29),
        0.23,
        0.12,
        "#31515D",
        axis="z",
        render_layer=20,
    )
    for index, (x_offset, y_offset) in enumerate(
        ((0.16, 0.16), (-0.16, 0.16), (0.16, -0.16), (-0.16, -0.16))
    ):
        g.cylinder(
            f"bearing_fastener_{index}",
            (drive_x + x_offset, drive_y + y_offset, 1.36),
            0.035,
            0.08,
            FASTENER,
            axis="z",
            render_layer=21,
        )
    g.box(
        "gearbox",
        (drive_x, drive_y, 1.53),
        (0.72, 0.70, 0.48),
        "#40515A",
        render_layer=20,
    )
    g.box(
        "drive_bracket",
        (drive_x, 0.42, 1.50),
        (0.95, 0.12, 0.95),
        STEEL,
        render_layer=20,
    )
    g.cylinder(
        "gearmotor_frame",
        (drive_x, drive_y, 2.05),
        0.39,
        0.85,
        MOTOR_BLUE,
        axis="z",
        render_layer=20,
    )
    for z in (1.69, 2.41):
        g.cylinder(
            f"gearmotor_end_bell_{z}",
            (drive_x, drive_y, z),
            0.36,
            0.14,
            DARK_STEEL,
            axis="z",
            render_layer=20,
        )
    g.box(
        "gearmotor_terminal",
        (drive_x, 1.35, 2.05),
        (0.42, 0.24, 0.36),
        DARK_STEEL,
        render_layer=20,
    )
    return g.done()


def _build_box() -> tuple[Primitive3D, ...]:
    """FEFCO 0201 regular slotted corrugated shipping case."""

    g = GeometryBuilder()
    g.box("carton_body", (0.0, 0.62, 0.0), (1.45, 1.24, 1.05), "#C89242")
    g.box("top_tape", (0.0, 1.255, 0.0), (1.46, 0.03, 0.20), "#E6CF9A")
    g.box("top_seam", (0.0, 1.272, 0.0), (1.46, 0.012, 0.025), "#6D4A1E")
    for x in (-0.71, 0.71):
        g.box(
            f"vertical_edge_{x}",
            (x, 0.62, 0.51),
            (0.025, 1.20, 0.025),
            "#9D6B2F",
        )
    g.box(
        "shipping_label",
        (0.0, 0.72, 0.535),
        (0.62, 0.36, 0.025),
        "#E8E3D5",
    )
    g.box("shipping_label_border", (0.0, 0.72, 0.552), (0.66, 0.018, 0.018), LABEL_DARK, render_layer=1)
    for index, (x, width) in enumerate(((-0.18, 0.24), (0.09, 0.38))):
        g.box(
            f"shipping_label_mark_{index}",
            (x, 0.72 + (0.07 if index == 0 else -0.08), 0.556),
            (width, 0.025, 0.012),
            LABEL_DARK,
            render_layer=2,
        )
    _add_panel_seam(g, "carton_front_seam", (0.0, 0.62, 0.547), (0.018, 1.12, 0.018), color="#6D4A1E")
    g.box("pallet_contact_shadow", (0.0, 0.03, 0.0), (1.40, 0.06, 1.0), "#70491F")
    return g.done()


def _build_photoeye() -> tuple[Primitive3D, ...]:
    """Opposed SICK-style through-beam sender and receiver pair."""

    g = GeometryBuilder()
    for index, z in enumerate((-0.92, 0.92)):
        side = "sender" if index == 0 else "receiver"
        g.box(f"{side}_base", (0.0, 0.06, z), (0.52, 0.12, 0.42), STEEL)
        g.box(f"{side}_post", (0.0, 0.66, z), (0.16, 1.18, 0.16), DARK_STEEL)
        g.box(
            f"{side}_bracket",
            (0.0, 1.08, z),
            (0.50, 0.12, 0.36),
            STEEL,
        )
        g.box(
            f"{side}_housing",
            (0.0, 1.22, z),
            (0.38, 0.42, 0.32),
            SENSOR_BLUE,
        )
        lens_z = z + (0.19 if z < 0 else -0.19)
        g.cylinder(
            f"{side}_lens",
            (0.0, 1.22, lens_z),
            0.105,
            0.08,
            RED,
            axis="z",
        )
        g.cylinder(
            f"{side}_status_led",
            (0.13, 1.38, z),
            0.04,
            0.035,
            GREEN,
            axis="x",
        )
        _add_panel_fasteners(
            g,
            side,
            ((-0.16, 1.08, z - (0.18 if z < 0 else -0.18)), (0.16, 1.08, z - (0.18 if z < 0 else -0.18))),
            axis="y",
            radius=0.022,
            length=0.025,
        )
        _add_panel_seam(
            g,
            f"{side}_housing_face_seam",
            (0.0, 1.445, z),
            (0.30, 0.018, 0.26),
            color="#1E5879",
        )
    g.box(
        "beam",
        (0.0, 1.22, 0.0),
        (0.028, 0.028, 1.65),
        "#43C7F4",
        opacity=150,
    )
    return g.done()


def _build_switch() -> tuple[Primitive3D, ...]:
    """Single 22 mm industrial pushbutton in a local station."""

    g = GeometryBuilder()
    g.box("station_enclosure", (0.0, 0.62, 0.0), (0.82, 1.24, 0.48), "#D7DEE0")
    g.box("station_lid", (0.0, 0.62, 0.255), (0.76, 1.16, 0.05), "#EDF1F2")
    g.cylinder("operator_bezel", (0.0, 0.70, 0.315), 0.27, 0.10, "#909DA3", axis="z")
    g.cylinder("operator_cap", (0.0, 0.70, 0.405), 0.23, 0.14, GREEN, axis="z")
    # The approval camera presents the opposite enclosure face; keep the
    # operator visible from either supported orbit direction.
    g.cylinder("operator_bezel_front", (0.0, 0.70, -0.315), 0.24, 0.10, "#909DA3", axis="z", render_layer=8)
    g.cylinder("operator_cap_front", (0.0, 0.70, -0.405), 0.19, 0.12, GREEN, axis="z", render_layer=9)
    _add_legend_surface(g, "legend", (0.0, 1.06, 0.30), (0.56, 0.18, 0.035))
    _add_edge_trim(g, "station_lid_edge", (0.0, 0.62, 0.285), (0.76, 1.16, 0.018), EDGE_HIGHLIGHT)
    g.cylinder("cable_gland", (0.0, 0.04, 0.0), 0.10, 0.16, DARK_STEEL)
    g.box("mounting_post", (0.0, 0.36, -0.36), (0.20, 0.72, 0.20), DARK_STEEL)
    g.box("mounting_foot", (0.0, 0.05, -0.36), (0.62, 0.10, 0.54), STEEL)
    return g.done()


def _build_indicator() -> tuple[Primitive3D, ...]:
    """PATLITE-style three-module signal tower."""

    g = GeometryBuilder()
    g.box("mounting_foot", (0.0, 0.05, 0.0), (0.66, 0.10, 0.66), STEEL)
    g.cylinder("pole", (0.0, 0.82, 0.0), 0.08, 1.50, DARK_STEEL)
    g.cylinder("tower_base", (0.0, 1.58, 0.0), 0.31, 0.20, DARK_STEEL)
    module_data = (
        ("red_module", 1.82, RED),
        ("amber_module", 2.18, AMBER),
        ("green_module", 2.54, GREEN),
    )
    for role, y, color in module_data:
        g.cylinder(role, (0.0, y, 0.0), 0.27, 0.30, color)
        g.cylinder(f"{role}_separator", (0.0, y - 0.18, 0.0), 0.285, 0.06, DARK_STEEL)
    g.cylinder("top_cap", (0.0, 2.74, 0.0), 0.29, 0.10, DARK_STEEL)
    return g.done()


def _build_pusher() -> tuple[Primitive3D, ...]:
    """Festo DSBC-style ISO profile cylinder with transfer plate."""

    g = GeometryBuilder()
    g.box("mounting_base", (0.0, 0.08, 0.0), (2.70, 0.16, 1.05), STEEL)
    g.cylinder("cylinder_barrel", (-0.35, 0.72, 0.0), 0.35, 1.35, ALUMINUM, axis="x")
    for x in (-1.05, 0.35):
        g.box(
            f"end_cap_{x}",
            (x, 0.72, 0.0),
            (0.18, 0.82, 0.82),
            DARK_STEEL,
        )
    for y in (0.45, 0.99):
        for z in (-0.31, 0.31):
            g.cylinder(
                f"tie_rod_{y}_{z}",
                (-0.35, y, z),
                0.035,
                1.42,
                "#687A82",
                axis="x",
            )
    g.cylinder("piston_rod", (0.85, 0.72, 0.0), 0.11, 1.05, LIGHT_STEEL, axis="x")
    g.box("rod_clevis", (1.39, 0.72, 0.0), (0.25, 0.30, 0.32), STEEL)
    g.box("pusher_plate", (1.63, 0.92, 0.0), (0.18, 1.05, 1.10), SAFETY_YELLOW)
    for x in (-0.92, 0.22):
        g.cylinder(
            f"air_port_{x}",
            (x, 1.18, 0.0),
            0.07,
            0.16,
            "#176B87",
        )
    g.box("rear_mount", (-1.20, 0.38, 0.0), (0.30, 0.60, 0.72), STEEL)
    return g.done()


def _build_pump() -> tuple[Primitive3D, ...]:
    """Close-coupled end-suction centrifugal pump package."""

    g = GeometryBuilder()
    g.box("baseplate", (0.0, 0.08, 0.0), (3.40, 0.16, 1.25), STEEL)
    _add_panel_fasteners(
        g,
        "baseplate",
        ((-1.45, 0.19, -0.48), (-1.45, 0.19, 0.48), (1.45, 0.19, -0.48), (1.45, 0.19, 0.48)),
        axis="y",
        radius=0.04,
        length=0.035,
    )
    motor_x = -0.78
    axis_y = 0.72
    g.cylinder("pump_motor_frame", (motor_x, axis_y, 0.0), 0.48, 1.38, MOTOR_BLUE, axis="x")
    for index, x in enumerate((-1.30, -1.08, -0.86, -0.64, -0.42, -0.20)):
        g.cylinder(
            f"pump_motor_rib_{index:02d}",
            (x, axis_y, 0.0),
            0.51,
            0.035,
            "#126D8C",
            axis="x",
        )
    g.cylinder("pump_motor_fan_cover", (-1.56, axis_y, 0.0), 0.43, 0.22, DARK_STEEL, axis="x")
    g.box("motor_stool", (0.08, 0.62, 0.0), (0.38, 0.86, 0.74), "#3E5963")
    g.cylinder("pump_volute", (0.58, 0.72, 0.0), 0.66, 0.52, "#285E70", axis="x")
    g.cylinder("volute_cover", (0.88, 0.72, 0.0), 0.55, 0.12, "#34778C", axis="x")
    g.cylinder("suction_neck", (1.30, 0.72, 0.0), 0.28, 0.72, "#285E70", axis="x")
    g.cylinder("suction_flange", (1.68, 0.72, 0.0), 0.43, 0.12, STEEL, axis="x")
    _add_flange_fasteners(g, "suction", 1.68, 0.72, 0.0)
    g.cylinder("discharge_neck", (0.58, 1.30, 0.0), 0.23, 0.54, "#285E70")
    g.cylinder("discharge_flange", (0.58, 1.61, 0.0), 0.38, 0.12, STEEL)
    for index, (x, z) in enumerate(
        ((0.18, 0.18), (-0.18, 0.18), (0.18, -0.18), (-0.18, -0.18))
    ):
        g.cylinder(
            f"discharge_bolt_{index}",
            (0.58 + x, 1.61, z),
            0.045,
            0.08,
            FASTENER,
            axis="y",
            render_layer=1,
        )
    for x in (-1.12, -0.42):
        for z in (-0.34, 0.34):
            g.box(f"motor_foot_{x}_{z}", (x, 0.20, z), (0.46, 0.16, 0.25), "#31515D")
    g.box("volute_foot", (0.58, 0.22, 0.0), (0.72, 0.28, 0.76), "#31515D")
    g.box("terminal_box", (-0.74, 1.24, 0.0), (0.48, 0.28, 0.42), DARK_STEEL)
    g.box("pump_nameplate", (-0.78, 0.72, 0.49), (0.46, 0.22, 0.025), "#D3DBDE", render_layer=1)
    _add_panel_seam(g, "pump_nameplate_border", (-0.78, 0.72, 0.508), (0.50, 0.018, 0.018), color=FASTENER)
    _add_panel_fasteners(
        g,
        "pump_nameplate",
        ((-0.98, 0.72, 0.512), (-0.58, 0.72, 0.512)),
        radius=0.022,
        length=0.025,
    )
    return g.done()


def _build_fan() -> tuple[Primitive3D, ...]:
    """Greenheck-style tubular axial inline fan."""

    g = GeometryBuilder()
    g.tube(
        "tubular_housing",
        (0.0, 1.16, 0.0),
        1.05,
        0.86,
        0.78,
        "#526974",
        axis="x",
    )
    for x in (-0.43, 0.43):
        g.tube(
            f"housing_flange_{x}",
            (x, 1.16, 0.0),
            1.20,
            0.84,
            0.10,
            STEEL,
            axis="x",
        )
    # A brighter camera-facing guard ring makes the open tubular housing read
    # as an inline fan rather than a generic framed rotor in the isometric QA
    # view. The bore remains open so all six blades stay inspectable.
    g.tube(
        "front_guard_ring",
        (0.58, 1.16, 0.0),
        1.22,
        0.84,
        0.14,
        "#B9C8CD",
        axis="x",
    )
    g.tube(
        "rear_guard_ring",
        (-0.58, 1.16, 0.0),
        1.20,
        0.84,
        0.12,
        "#82969D",
        axis="x",
    )
    g.cylinder("impeller_hub", (0.50, 1.16, 0.0), 0.24, 0.20, DARK_STEEL, axis="x")
    for index in range(6):
        angle = index * 60.0
        radians = math.radians(angle)
        y = 1.16 + 0.54 * math.cos(radians)
        z = 0.54 * math.sin(radians)
        g.box(
            f"impeller_blade_{index:02d}",
            (0.51, y, z),
            (0.10, 0.64, 0.24),
            "#B7E0E8",
            rotation=(angle + 24.0, 0.0, 0.0),
        )
    for x in (-0.55, 0.55):
        for z in (-0.68, 0.68):
            g.box(f"support_leg_{x}_{z}", (x, 0.43, z), (0.16, 0.76, 0.16), DARK_STEEL)
            g.box(f"support_foot_{x}_{z}", (x, 0.07, z), (0.48, 0.10, 0.34), STEEL)
    g.box("belt_guard", (-0.05, 2.25, 0.0), (0.95, 0.38, 0.48), DARK_STEEL)
    g.cylinder("external_motor", (-0.05, 2.55, 0.0), 0.30, 0.90, MOTOR_BLUE, axis="x")
    g.box("motor_mount", (-0.05, 2.10, 0.0), (1.10, 0.12, 0.62), STEEL)
    return g.done()


def _build_tank() -> tuple[Primitive3D, ...]:
    """Freestanding stainless process vessel with hygienic accessories."""

    g = GeometryBuilder()
    g.cylinder("tank_shell", (0.0, 1.82, 0.0), 1.06, 2.65, "#A8B7BD")
    # Stepped rings produce readable dished heads in the faceted renderer.
    for index, (y, radius) in enumerate(((3.20, 0.92), (3.36, 0.70), (3.49, 0.40))):
        g.cylinder(f"top_head_{index}", (0.0, y, 0.0), radius, 0.18, "#B9C4C8")
    for index, (y, radius) in enumerate(((0.43, 0.92), (0.27, 0.68), (0.15, 0.38))):
        g.cylinder(f"bottom_head_{index}", (0.0, y, 0.0), radius, 0.18, "#92A4AB")
    g.cylinder("top_nozzle", (0.0, 3.78, 0.0), 0.19, 0.45, LIGHT_STEEL)
    g.cylinder("top_flange", (0.0, 3.58, 0.0), 0.32, 0.10, STEEL)
    g.cylinder("relief_vent", (-0.48, 3.65, 0.10), 0.12, 0.38, "#536873")
    g.cylinder("side_outlet", (1.20, 0.72, 0.0), 0.20, 0.52, LIGHT_STEEL, axis="x")
    g.cylinder("outlet_flange", (1.48, 0.72, 0.0), 0.32, 0.10, STEEL, axis="x")
    _add_flange_fasteners(g, "outlet", 1.48, 0.72, 0.0, radius=0.045, length=0.08)
    _add_panel_seam(g, "tank_shell_seam", (0.0, 1.82, 1.065), (0.025, 0.035, 0.025), color=EDGE_HIGHLIGHT)
    _add_panel_fasteners(
        g,
        "access_cover",
        ((1.075, 2.07, -0.23), (1.075, 2.07, 0.23), (1.075, 2.49, -0.23), (1.075, 2.49, 0.23)),
        axis="x",
        radius=0.032,
        length=0.035,
    )
    g.cylinder("access_cover", (1.02, 2.28, 0.0), 0.42, 0.10, "#D1DADD", axis="x")
    g.cylinder("fluid_level", (0.0, 1.52, 0.0), 0.94, 1.95, "#159BC0", opacity=105)
    # An opaque stainless shell cannot communicate process level by itself.
    # The external full-height sight window makes the liquid/empty boundary
    # readable without implying that the entire vessel is transparent.
    sight_z = 1.30
    g.box(
        "sight_glass_liquid_band",
        (0.0, 1.50, sight_z + 0.145),
        (0.18, 1.36, 0.025),
        "#00C8F0",
        opacity=120,
        render_layer=3,
    )
    g.box(
        "sight_glass_meniscus",
        (0.0, 2.075, sight_z + 0.155),
        (0.36, 0.055, 0.035),
        "#F2FBFC",
    )
    for index in range(10):
        g.box(
            f"sight_glass_segment_{index:02d}",
            (0.0, 0.82 + index * 0.225, sight_z + 0.22),
            (0.32, 0.16, 0.055),
            "#00D8FF" if index < 6 else "#86AEB6",
            render_layer=4,
        )
    for side, x in (("left", -0.25), ("right", 0.25)):
        g.box(
            f"sight_glass_frame_{side}",
            (x, 1.83, sight_z + 0.08),
            (0.08, 2.46, 0.10),
            DARK_STEEL,
        )
    for end, y in (("bottom", 0.60), ("top", 3.06)):
        g.box(
            f"sight_glass_frame_{end}",
            (0.0, y, sight_z + 0.08),
            (0.58, 0.10, 0.10),
            DARK_STEEL,
        )
    for end, y in (("bottom", 0.68), ("top", 2.98)):
        g.cylinder(
            f"sight_glass_{end}_connection",
            (0.0, y, 1.17),
            0.08,
            0.38,
            LIGHT_STEEL,
            axis="z",
        )
    for index, y in enumerate((1.20, 1.83, 2.46)):
        g.box(
            f"sight_glass_tick_{index}",
            (0.32, y, sight_z + 0.16),
            (0.18, 0.035, 0.04),
            LIGHT_STEEL,
        )
    for index, (x, z) in enumerate(((-0.72, -0.62), (-0.72, 0.62), (0.72, -0.62), (0.72, 0.62))):
        g.box(f"tank_leg_{index}", (x, 0.34, z), (0.16, 0.66, 0.16), STEEL)
        g.box(f"tank_foot_{index}", (x, 0.06, z), (0.38, 0.10, 0.38), "#667981")
    _add_legend_surface(g, "nameplate", (1.07, 2.74, 0.0), (0.025, 0.48, 0.64))
    return g.done()


def _build_level_sensor() -> tuple[Primitive3D, ...]:
    """Side-mounted ifm LMT point-level switch and process connection."""

    g = GeometryBuilder()
    g.tube("tank_wall_coupon", (-0.58, 0.86, 0.0), 0.82, 0.62, 0.16, "#A8B7BD", axis="x")
    g.cylinder("welded_process_nozzle", (-0.38, 0.90, 0.0), 0.30, 0.36, STEEL, axis="x")
    g.cylinder("threaded_process_connection", (-0.05, 0.90, 0.0), 0.22, 0.34, LIGHT_STEEL, axis="x")
    for index, x in enumerate((-0.02, 0.08, 0.18)):
        g.tube(f"process_thread_{index}", (x, 0.90, 0.0), 0.24, 0.18, 0.035, "#C5D1D4", axis="x")
    g.cylinder("wetted_tip", (-0.46, 0.90, 0.0), 0.10, 0.38, "#E8E2C8", axis="x")
    g.cylinder("sensor_body", (0.34, 0.90, 0.0), 0.19, 0.50, "#87989F", axis="x")
    g.cylinder("sensor_head", (0.68, 0.90, 0.0), 0.25, 0.26, "#2F6D92", axis="x")
    g.cylinder("m12_connector", (0.92, 0.90, 0.0), 0.12, 0.24, DARK_STEEL, axis="x")
    g.cylinder("m12_connector_collar", (0.99, 0.90, 0.0), 0.15, 0.06, LIGHT_STEEL, axis="x", render_layer=5)
    g.cylinder("m12_cable_exit", (1.12, 0.90, 0.0), 0.08, 0.18, "#26343C", axis="x", render_layer=5)
    g.cylinder("status_led", (0.70, 1.12, 0.0), 0.045, 0.035, GREEN)
    g.box("support_base", (-0.58, 0.05, 0.0), (0.72, 0.10, 1.90), STEEL)
    return g.done()


def _build_radar_level_sensor() -> tuple[Primitive3D, ...]:
    """Top-mounted non-contact radar transmitter with measurement cone."""

    g = GeometryBuilder()
    g.cylinder("tank_roof_coupon", (0.0, 0.12, 0.0), 1.20, 0.20, "#A8B7BD")
    g.cylinder("process_nozzle", (0.0, 0.42, 0.0), 0.30, 0.50, LIGHT_STEEL)
    g.cylinder("process_flange", (0.0, 0.72, 0.0), 0.52, 0.12, STEEL)
    for index, (x, z) in enumerate(
        ((0.34, 0.0), (-0.34, 0.0), (0.0, 0.34), (0.0, -0.34))
    ):
        g.cylinder(
            f"process_bolt_{index}",
            (x, 0.72, z),
            0.055,
            0.08,
            FASTENER,
            axis="y",
            render_layer=1,
        )
    g.cylinder("antenna_horn", (0.0, 0.93, 0.0), 0.26, 0.34, "#87989F")
    g.cylinder("electronics_neck", (0.0, 1.24, 0.0), 0.18, 0.30, DARK_STEEL)
    g.cylinder("electronics_housing", (0.0, 1.62, 0.0), 0.50, 0.52, "#F0A02B")
    g.cylinder("housing_lid", (0.0, 1.92, 0.0), 0.53, 0.10, DARK_STEEL)
    g.box("local_display_bezel", (0.0, 1.66, 0.50), (0.62, 0.30, 0.06), LIGHT_STEEL, render_layer=3)
    g.box("local_display", (0.0, 1.66, 0.54), (0.50, 0.20, 0.035), "#19A7C7", render_layer=4)
    g.box("local_display_readout", (0.0, 1.66, 0.565), (0.30, 0.035, 0.018), "#D8F7FA", render_layer=5)
    g.cylinder("cable_gland", (0.50, 1.58, 0.0), 0.11, 0.24, DARK_STEEL, axis="x")
    # A single tapered, transparent volume makes the non-contact measuring
    # path legible in the isolated approval gallery as well as in S06.
    g.frustum(
        "radar_measurement_cone",
        (0.0, 0.58, 0.0),
        0.78,
        0.12,
        0.78,
        "#43C7F4",
        opacity=72,
        end_caps=False,
        render_layer=15,
    )
    return g.done()


def _build_pipe() -> tuple[Primitive3D, ...]:
    """Supported ASME-style raised-face flanged pipe spool."""

    g = GeometryBuilder()
    g.cylinder("pipe_spool", (0.0, 1.00, 0.0), 0.27, 3.00, "#6E8189", axis="x")
    for side, x in (("left", -1.55), ("right", 1.55)):
        g.cylinder(f"{side}_flange", (x, 1.00, 0.0), 0.56, 0.18, STEEL, axis="x")
        face_x = x + (0.11 if x > 0 else -0.11)
        g.cylinder(f"{side}_raised_face", (face_x, 1.00, 0.0), 0.38, 0.06, "#DDE7E9", axis="x")
        g.cylinder(f"{side}_bore", (face_x + (0.035 if x > 0 else -0.035), 1.00, 0.0), 0.25, 0.025, "#18282F", axis="x", render_layer=3)
        _add_flange_fasteners(g, side, x, 1.00, 0.0, radius=0.038, length=0.12)
    g.box("support_column", (0.0, 0.43, 0.0), (0.24, 0.70, 0.24), DARK_STEEL)
    g.cylinder("support_saddle_roller", (0.0, 0.77, 0.0), 0.34, 0.72, STEEL, axis="x", render_layer=2)
    g.box("support_saddle", (0.0, 0.82, 0.0), (0.78, 0.12, 0.62), DARK_STEEL, render_layer=3)
    g.box("support_foot", (0.0, 0.06, 0.0), (0.88, 0.12, 0.70), STEEL)
    return g.done()


def _build_valve() -> tuple[Primitive3D, ...]:
    """Bray-style wafer butterfly valve between two pipe flanges."""

    g = GeometryBuilder()
    for side, x in (("left", -0.64), ("right", 0.64)):
        g.tube(
            f"{side}_pipe",
            (x, 0.90, 0.0),
            0.60,
            0.52,
            0.58,
            "#6E8189",
            axis="x",
            opacity=0 if side == "right" else 255,
        )
        g.tube(
            f"{side}_flange",
            (x * 0.55, 0.90, 0.0),
            0.78,
            0.60,
            0.18,
            STEEL,
            axis="x",
            opacity=0 if side == "right" else 255,
        )
    g.tube(
        "valve_body",
        (0.0, 0.90, 0.0),
        0.76,
        0.56,
        0.24,
        "#315A72",
        axis="x",
    )
    for side, x in (("left", -0.64), ("right", 0.64)):
        if side == "left":
            _add_flange_fasteners(
                g,
                f"{side}_flange",
                x,
                0.90,
                0.0,
                radius=0.045,
                length=0.12,
                render_layer=1,
            )
    # The review view shows the disc just proud of the wafer face. This is an
    # intentional exploded/readability offset, not a physical second disc.
    g.cylinder(
        "valve_disc",
        (0.18, 0.90, 0.0),
        0.48,
        0.06,
        SAFETY_YELLOW,
        axis="x",
    )
    g.box("disc_stem_witness", (0.22, 0.90, 0.0), (0.035, 0.90, 0.10), DARK_STEEL)
    g.cylinder("valve_stem", (0.0, 1.58, 0.0), 0.10, 0.52, LIGHT_STEEL)
    g.box("body_lug_top", (0.0, 1.65, 0.0), (0.34, 0.18, 0.26), "#315A72")
    g.box("body_lug_bottom", (0.0, 0.15, 0.0), (0.34, 0.18, 0.26), "#315A72")
    g.box("body_lug_front", (0.0, 0.90, 0.73), (0.34, 0.24, 0.18), "#315A72")
    g.box("body_lug_rear", (0.0, 0.90, -0.73), (0.34, 0.24, 0.18), "#315A72")
    g.box("iso_mount_pad", (0.0, 1.78, 0.0), (0.52, 0.16, 0.48), DARK_STEEL)
    g.box("manual_lever", (0.52, 1.96, 0.0), (1.22, 0.14, 0.18), SAFETY_YELLOW, rotation=(0.0, 0.0, 16.0))
    g.box("lever_grip", (1.10, 2.12, 0.0), (0.32, 0.22, 0.24), DARK_STEEL, rotation=(0.0, 0.0, 16.0))
    g.box("support_base", (0.0, 0.05, 0.0), (2.20, 0.10, 1.30), STEEL)
    return g.done()


def _build_rotary_switch() -> tuple[Primitive3D, ...]:
    """Three-position 22 mm selector operator in a metal station."""

    g = GeometryBuilder()
    g.box("selector_enclosure", (0.0, 0.62, 0.0), (0.86, 1.24, 0.48), "#D7DEE0")
    g.box("selector_lid", (0.0, 0.62, 0.255), (0.80, 1.16, 0.05), "#EDF1F2")
    g.cylinder("selector_bezel", (0.0, 0.70, 0.315), 0.16, 0.08, "#7D8B92", axis="z")
    g.box("selector_knob", (0.0, 0.70, 0.40), (0.06, 0.20, 0.07), DARK_STEEL, rotation=(0.0, 0.0, -28.0), render_layer=6)
    for index, x in enumerate((-0.24, 0.0, 0.24)):
        g.box(f"position_mark_{index}", (x * 0.62, 0.91, 0.30), (0.045, 0.08, 0.025), "#D4E5E8", render_layer=5)
        g.box(
            f"position_witness_front_{index}",
            (x * 0.62, 0.91, -0.265),
            (0.04, 0.08, 0.025),
            "#26343C",
            render_layer=5,
        )
    _add_legend_surface(g, "legend", (0.0, 1.16, 0.30), (0.62, 0.16, 0.035))
    g.box("mounting_post", (0.0, 0.36, -0.36), (0.20, 0.72, 0.20), DARK_STEEL)
    g.box("mounting_foot", (0.0, 0.05, -0.36), (0.62, 0.10, 0.54), STEEL)
    return g.done()


def _build_lift_table() -> tuple[Primitive3D, ...]:
    """Hydraulic scissor lift with supported deck and pinned arms."""

    g = GeometryBuilder()
    g.box("lift_base", (0.0, 0.10, 0.0), (2.70, 0.20, 1.55), DARK_STEEL)
    g.box("lift_platform", (0.0, 2.00, 0.0), (2.85, 0.20, 1.65), "#657A83")
    for z in (-0.54, 0.54):
        g.box(
            f"scissor_arm_rising_{z}",
            (0.0, 0.98, z),
            (2.35, 0.18, 0.16),
            SAFETY_YELLOW,
            rotation=(0.0, 0.0, 38.0),
        )
        g.box(
            f"scissor_arm_falling_{z}",
            (0.0, 0.98, z),
            (2.35, 0.18, 0.16),
            SAFETY_YELLOW,
            rotation=(0.0, 0.0, -38.0),
        )
        g.cylinder(f"center_pivot_{z}", (0.0, 0.98, z), 0.14, 0.26, LIGHT_STEEL, axis="z")
        for x, y in ((-0.93, 0.24), (0.93, 0.24), (-0.93, 1.72), (0.93, 1.72)):
            g.cylinder(f"arm_pin_{z}_{x}_{y}", (x, y, z), 0.10, 0.24, LIGHT_STEEL, axis="z")
    # Keep the actuator on the camera-facing side, with a visible barrel,
    # polished rod, and end clevises so it reads as a real hydraulic package.
    g.cylinder("hydraulic_cylinder", (-0.42, 0.62, 0.72), 0.12, 0.92, "#2186A3", axis="x", rotation=(0.0, 0.0, -25.0), render_layer=5)
    g.cylinder("hydraulic_rod", (0.10, 0.88, 0.72), 0.06, 0.48, LIGHT_STEEL, axis="x", rotation=(0.0, 0.0, -25.0), render_layer=6)
    g.cylinder("hydraulic_barrel_cap", (-0.88, 0.40, 0.72), 0.15, 0.08, DARK_STEEL, axis="x", rotation=(0.0, 0.0, -25.0), render_layer=6)
    g.box("hydraulic_rod_clevis", (0.34, 1.05, 0.72), (0.16, 0.12, 0.16), DARK_STEEL, render_layer=6)
    g.cylinder("hydraulic_base_pin", (-0.88, 0.40, 0.72), 0.09, 0.22, LIGHT_STEEL, axis="z", render_layer=7)
    g.cylinder("hydraulic_platform_pin", (0.34, 1.05, 0.72), 0.09, 0.22, LIGHT_STEEL, axis="z", render_layer=7)
    g.box("power_unit", (-1.00, 0.38, 0.0), (0.62, 0.56, 0.62), MOTOR_BLUE)
    return g.done()


def _build_drill_press() -> tuple[Primitive3D, ...]:
    """Clausing-style floor drill press with variable-speed head."""

    g = GeometryBuilder()
    g.box("drill_base", (0.0, 0.09, 0.0), (1.30, 0.18, 1.12), DARK_STEEL)
    for index, (x, z) in enumerate(
        ((-0.46, -0.38), (0.46, -0.38), (-0.46, 0.38), (0.46, 0.38))
    ):
        g.cylinder(
            f"base_anchor_bolt_{index}",
            (x, 0.205, z),
            0.055,
            0.08,
            FASTENER,
            axis="y",
            render_layer=4,
        )
    g.cylinder("drill_column", (0.0, 1.75, -0.28), 0.16, 3.25, "#566A73")
    g.box("work_table", (0.0, 1.30, 0.45), (1.42, 0.16, 0.70), "#657A83")
    for x in (-0.42, 0.0, 0.42):
        g.box(f"table_t_slot_{x}", (x, 1.39, 0.45), (0.055, 0.025, 0.56), "#26343C")
    g.box("table_support_arm", (0.0, 1.24, -0.02), (0.58, 0.22, 0.18), DARK_STEEL)
    g.box("head_casting", (0.18, 2.92, -0.06), (1.38, 0.78, 0.88), "#315A72")
    g.box("belt_guard", (-0.26, 3.39, -0.06), (1.16, 0.20, 0.82), "#456573")
    g.cylinder("head_motor", (-0.50, 3.02, -0.50), 0.28, 0.76, MOTOR_BLUE)
    g.cylinder("quill", (0.52, 2.48, 0.08), 0.12, 0.58, LIGHT_STEEL)
    g.cylinder("spindle", (0.52, 2.03, 0.08), 0.07, 0.30, "#D5DCDE")
    g.cylinder("chuck", (0.52, 1.78, 0.08), 0.13, 0.18, DARK_STEEL)
    g.cylinder(
        "drill_bit",
        (0.52, 1.54, 0.08),
        0.07,
        0.29,
        "#F2F7F8",
        render_layer=7,
    )
    handle_origin = (1.00, 2.60, 0.08)
    g.cylinder("feed_hub", (0.93, 2.60, 0.08), 0.12, 0.18, DARK_STEEL, axis="x")
    for index, angle in enumerate((-55.0, 10.0, 75.0)):
        radians = math.radians(angle)
        direction_y = math.cos(radians)
        direction_z = math.sin(radians)
        rod_length = 0.62
        g.cylinder(
            f"feed_handle_rod_{index}",
            (
                handle_origin[0],
                handle_origin[1] + direction_y * rod_length / 2,
                handle_origin[2] + direction_z * rod_length / 2,
            ),
            0.055,
            rod_length,
            LIGHT_STEEL,
            axis="y",
            rotation=(angle, 0.0, 0.0),
        )
        g.sphere(
            f"feed_handle_knob_{index}",
            (
                handle_origin[0],
                handle_origin[1] + direction_y * rod_length,
                handle_origin[2] + direction_z * rod_length,
            ),
            0.10,
            DARK_STEEL,
        )
    g.box("starter_station", (0.78, 3.02, 0.40), (0.32, 0.44, 0.18), "#D7DEE0")
    g.cylinder("start_button", (0.78, 3.10, 0.51), 0.07, 0.08, GREEN, axis="z")
    g.cylinder("stop_button", (0.78, 2.90, 0.51), 0.07, 0.08, RED, axis="z")
    return g.done()


def _build_robot_arm() -> tuple[Primitive3D, ...]:
    """Pedestal-mounted six-axis handling robot based on FANUC M-20iD."""

    g = GeometryBuilder()
    orange = "#E69B21"
    g.box("robot_anchor_plate", (0.0, 0.06, 0.0), (1.10, 0.12, 1.10), STEEL)
    g.cylinder("axis_1_base", (0.0, 0.34, 0.0), 0.50, 0.56, DARK_STEEL)
    g.cylinder("axis_1_turret", (0.0, 0.70, 0.0), 0.42, 0.34, orange)
    g.sphere("axis_2_shoulder", (0.0, 1.03, 0.0), 0.34, DARK_STEEL)
    g.cylinder(
        "upper_arm",
        (0.46, 1.555, 0.0),
        0.18,
        0.88,
        orange,
        rotation=(0.0, 0.0, -41.1),
    )
    g.sphere("axis_3_elbow", (0.92, 2.08, 0.0), 0.31, DARK_STEEL)
    g.cylinder(
        "forearm",
        (1.29, 2.45, 0.0),
        0.16,
        0.62,
        orange,
        rotation=(0.0, 0.0, -45.0),
    )
    g.sphere("axis_4_wrist", (1.66, 2.82, 0.0), 0.23, DARK_STEEL)
    g.sphere("axis_5_wrist", (1.97, 2.82, 0.0), 0.16, orange)
    g.cylinder("axis_6_tool_flange", (2.20, 2.82, 0.0), 0.18, 0.18, LIGHT_STEEL, axis="x")
    g.cylinder("tool_flange_disc", (2.31, 2.82, 0.0), 0.29, 0.12, LIGHT_STEEL, axis="x")
    for index, (y, z) in enumerate(
        ((2.82 - 0.15, -0.15), (2.82 + 0.15, -0.15),
         (2.82 - 0.15, 0.15), (2.82 + 0.15, 0.15))
    ):
        g.cylinder(
            f"tool_flange_bolt_{index}",
            (2.39, y, z),
            0.035,
            0.08,
            FASTENER,
            axis="x",
        )
    g.box("tooling_plate", (2.38, 2.82, 0.0), (0.14, 0.50, 0.50), DARK_STEEL)
    g.box("gripper_backplate", (2.48, 2.82, 0.0), (0.10, 0.42, 0.42), LIGHT_STEEL, render_layer=6)
    g.box("gripper_finger_upper", (2.68, 2.82, 0.16), (0.34, 0.18, 0.10), LIGHT_STEEL, render_layer=7)
    g.box("gripper_finger_lower", (2.68, 2.82, -0.16), (0.34, 0.18, 0.10), LIGHT_STEEL, render_layer=7)
    g.box("gripper_finger_tip_upper", (2.86, 2.82, 0.10), (0.12, 0.22, 0.10), DARK_STEEL, render_layer=7)
    g.box("gripper_finger_tip_lower", (2.86, 2.82, -0.10), (0.12, 0.22, 0.10), DARK_STEEL, render_layer=7)
    # Short surface strips communicate protected cable routing without adding
    # long parallel cylinders that intersect the joint housings.
    g.box(
        "internal_cable_route_upper",
        (0.46, 1.555, -0.19),
        (0.62, 0.05, 0.05),
        "#6D8188",
        rotation=(0.0, 0.0, 48.9),
    )
    g.box(
        "protected_cable_cover_upper",
        (0.46, 1.555, -0.24),
        (0.70, 0.10, 0.10),
        "#B2C2C6",
        rotation=(0.0, 0.0, 48.9),
    )
    g.box(
        "protected_cable_cover_upper_front",
        (0.46, 1.555, 0.20),
        (0.76, 0.11, 0.08),
        "#718990",
        rotation=(0.0, 0.0, 48.9),
        render_layer=6,
    )
    g.box(
        "internal_cable_route_forearm",
        (1.29, 2.45, -0.17),
        (0.43, 0.05, 0.05),
        "#6D8188",
        rotation=(0.0, 0.0, 45.0),
    )
    g.box(
        "protected_cable_cover_forearm",
        (1.29, 2.45, -0.22),
        (0.50, 0.10, 0.10),
        "#B2C2C6",
        rotation=(0.0, 0.0, 45.0),
    )
    g.box(
        "protected_cable_cover_forearm_front",
        (1.29, 2.45, 0.18),
        (0.56, 0.11, 0.08),
        "#718990",
        rotation=(0.0, 0.0, 45.0),
        render_layer=6,
    )
    g.box("protected_cable_cover_upper_clamp_a", (0.13, 1.23, 0.20), (0.14, 0.16, 0.12), DARK_STEEL, rotation=(0.0, 0.0, 48.9), render_layer=7)
    g.box("protected_cable_cover_upper_clamp_b", (0.79, 1.88, 0.20), (0.14, 0.16, 0.12), DARK_STEEL, rotation=(0.0, 0.0, 48.9), render_layer=7)
    g.box("protected_cable_cover_forearm_clamp_a", (1.08, 2.24, 0.18), (0.12, 0.15, 0.11), DARK_STEEL, rotation=(0.0, 0.0, 45.0), render_layer=7)
    g.box("protected_cable_cover_forearm_clamp_b", (1.50, 2.66, 0.18), (0.12, 0.15, 0.11), DARK_STEEL, rotation=(0.0, 0.0, 45.0), render_layer=7)
    g.box("robot_nameplate", (0.0, 0.72, 0.40), (0.44, 0.18, 0.025), "#F6E8B6")
    return g.done()


def _build_roller_shutter() -> tuple[Primitive3D, ...]:
    """High-speed fabric roll-up door with operator and side guides."""

    g = GeometryBuilder()
    for x in (-1.65, 1.65):
        g.box(f"side_column_{x}", (x, 1.65, 0.0), (0.28, 3.30, 0.42), STEEL)
        g.box(f"column_foot_{x}", (x, 0.07, 0.0), (0.62, 0.14, 0.72), DARK_STEEL)
    g.box("top_header", (0.0, 3.28, 0.0), (3.60, 0.54, 0.62), DARK_STEEL)
    g.cylinder("curtain_roll", (0.0, 3.28, 0.0), 0.28, 3.05, "#315A72", axis="x")
    g.box("fabric_curtain", (0.0, 1.78, 0.0), (3.05, 2.72, 0.10), "#1C7FA6")
    for index, y in enumerate((0.55, 0.95, 1.35, 1.75, 2.15, 2.55, 2.95)):
        g.box(f"curtain_witness_{index}", (0.0, y, 0.065), (3.00, 0.035, 0.03), "#5FC5EC")
    g.box("bottom_bar", (0.0, 0.40, 0.0), (3.16, 0.18, 0.24), SAFETY_YELLOW)
    g.box("operator_gearbox", (2.02, 3.03, 0.0), (0.58, 0.68, 0.62), "#40515A")
    g.cylinder("operator_motor", (2.02, 2.46, 0.0), 0.28, 0.82, MOTOR_BLUE)
    g.box("control_box", (2.18, 1.48, 0.0), (0.68, 0.90, 0.44), "#D7DEE0")
    g.cylinder("control_green", (2.18, 1.66, 0.25), 0.07, 0.06, GREEN, axis="z")
    g.cylinder("control_red", (2.18, 1.42, 0.25), 0.07, 0.06, RED, axis="z")
    return g.done()


def _build_rotary_table() -> tuple[Primitive3D, ...]:
    """WEISS-style low-profile freely programmable indexing table."""

    g = GeometryBuilder()
    g.box("indexer_base", (0.0, 0.08, 0.0), (2.85, 0.16, 2.85), STEEL)
    g.cylinder("indexer_housing", (0.0, 0.40, 0.0), 1.22, 0.62, DARK_STEEL)
    g.cylinder("rotary_plate", (0.0, 0.78, 0.0), 1.42, 0.16, "#7E9097")
    g.cylinder("center_opening", (0.0, 0.88, 0.0), 0.38, 0.05, "#0A151A")
    for index in range(8):
        angle = index * math.pi / 4.0
        x = 0.96 * math.cos(angle)
        z = 0.96 * math.sin(angle)
        g.cylinder(f"fixture_hole_{index}", (x, 0.89, z), 0.07, 0.05, "#172329")
        g.cylinder(f"station_index_mark_{index}", (x, 0.92, z), 0.11, 0.035, "#D3DEE0", axis="y", render_layer=4)
    g.box("side_gearbox", (1.52, 0.48, 0.0), (0.72, 0.76, 0.72), "#40515A")
    g.cylinder("indexer_motor", (2.05, 0.48, 0.0), 0.34, 0.86, MOTOR_BLUE, axis="x")
    g.box("motor_terminal", (2.06, 0.89, 0.0), (0.38, 0.24, 0.34), DARK_STEEL)
    g.box("status_board", (0.0, 0.47, 1.22), (0.72, 0.18, 0.05), "#16A34A")
    return g.done()


def _build_machine() -> tuple[Primitive3D, ...]:
    """Guarded CNC-style process machine based on a Haas VF enclosure."""

    g = GeometryBuilder()
    g.box("machine_plinth", (0.0, 0.18, 0.0), (3.35, 0.36, 2.65), DARK_STEEL)
    # Keep the large enclosure body behind the independently rendered front
    # doors. A single full-depth front face would otherwise overpaint the
    # farther window in an orthographic painter-sorted view.
    g.box("machine_enclosure", (0.0, 1.75, -0.34), (3.20, 2.95, 1.78), "#B9C1C4")
    g.box("left_side_return", (-1.50, 1.75, 0.72), (0.20, 2.82, 0.52), "#A8B2B6")
    g.box("right_side_return", (1.50, 1.75, 0.72), (0.20, 2.82, 0.52), "#A8B2B6")
    g.box("front_header", (0.0, 3.12, 0.95), (3.00, 0.22, 0.62), "#B9C1C4")
    g.box("left_front_door", (-0.78, 1.65, 1.30), (1.52, 2.50, 0.06), "#687980")
    g.box("right_front_door", (0.78, 1.65, 1.30), (1.52, 2.50, 0.06), "#6F7F86")
    for side, x in (("left", -0.78), ("right", 0.78)):
        g.box(f"{side}_window", (x, 2.08, 1.35), (1.02, 0.84, 0.04), "#255465", opacity=245, render_layer=4)
        g.box(f"{side}_window_reflection", (x - 0.18, 2.22, 1.385), (0.06, 0.52, 0.018), "#5BC4D9", opacity=150, render_layer=5)
        _add_panel_seam(g, f"{side}_window_top_seam", (x, 2.52, 1.385), (1.12, 0.035, 0.035), color=EDGE_HIGHLIGHT)
        _add_panel_seam(g, f"{side}_window_bottom_seam", (x, 1.64, 1.385), (1.12, 0.035, 0.035), color=FASTENER)
        _add_panel_fasteners(
            g,
            f"{side}_door",
            ((x - 0.48, 1.42, 1.385), (x + 0.48, 1.42, 1.385)),
            radius=0.028,
            length=0.025,
        )
        g.box(f"{side}_handle", (x + (0.56 if x < 0 else -0.56), 1.48, 1.38), (0.08, 0.70, 0.10), DARK_STEEL)
    _add_panel_seam(g, "door_center_seam", (0.0, 1.65, 1.35), (0.035, 2.50, 0.035), color=FASTENER)
    g.box("safety_label", (2.08, 2.68, 1.05), (0.54, 0.20, 0.035), "#F5F2DF", render_layer=1)
    g.box("safety_label_mark", (2.08, 2.68, 1.075), (0.34, 0.025, 0.012), LABEL_DARK, render_layer=2)
    g.box("top_spindle_housing", (0.0, 3.36, -0.20), (1.25, 0.42, 1.12), "#87989F")
    g.box("coolant_tank", (-0.92, 0.36, -1.12), (1.22, 0.48, 0.54), "#315A72")
    g.box("chip_chute", (1.04, 0.42, -1.20), (0.82, 0.62, 0.42), "#536873")
    g.box("pendant_arm", (1.78, 2.35, 0.62), (0.72, 0.14, 0.14), DARK_STEEL)
    g.box("control_pendant", (2.08, 1.92, 0.82), (0.72, 1.18, 0.44), "#26343C", rotation=(0.0, -10.0, 0.0))
    g.box("control_screen", (2.08, 2.16, 1.06), (0.48, 0.36, 0.035), "#1A637B", render_layer=4)
    g.box("control_screen_status", (2.08, 2.28, 1.085), (0.28, 0.035, 0.018), "#7DE3E8", render_layer=5)
    g.box("keypad", (2.08, 1.72, 1.06), (0.48, 0.32, 0.035), "#667981")
    g.cylinder("emergency_stop", (2.29, 1.46, 1.08), 0.10, 0.08, RED, axis="z")
    g.cylinder("stacklight_pole", (1.26, 3.66, -0.68), 0.06, 0.56, DARK_STEEL)
    for role, y, color in (("red", 3.98, RED), ("amber", 4.18, AMBER), ("green", 4.38, GREEN)):
        g.cylinder(f"machine_stacklight_{role}", (1.26, y, -0.68), 0.13, 0.17, color)
    return g.done()


def _build_geared_motor() -> tuple[Primitive3D, ...]:
    """Inline helical gearmotor with a separate reducer and output shaft."""

    g = GeometryBuilder()
    axis_y = 0.82
    g.cylinder("motor_frame", (-0.72, axis_y, 0.0), 0.43, 1.18, MOTOR_BLUE, axis="x")
    for index, angle in enumerate(range(0, 360, 30)):
        radians = math.radians(angle)
        g.box(
            f"motor_cooling_rib_{index:02d}",
            (-0.72, axis_y + 0.45 * math.cos(radians), 0.45 * math.sin(radians)),
            (1.02, 0.055, 0.12),
            "#126D8C",
            rotation=(float(angle), 0.0, 0.0),
        )
    g.cylinder("fan_cover", (-1.40, axis_y, 0.0), 0.39, 0.22, DARK_STEEL, axis="x")
    g.box("terminal_box", (-0.70, 1.28, 0.0), (0.48, 0.28, 0.40), DARK_STEEL)
    g.box("gearbox_housing", (0.30, axis_y, 0.0), (0.82, 1.02, 0.92), "#536873")
    g.cylinder("gearbox_input_flange", (-0.13, axis_y, 0.0), 0.46, 0.12, "#40545D", axis="x")
    g.cylinder("gearbox_output_bearing", (0.76, axis_y, 0.0), 0.30, 0.18, "#40545D", axis="x")
    g.cylinder("output_shaft", (1.05, axis_y, 0.0), 0.14, 0.48, LIGHT_STEEL, axis="x")
    g.box("shaft_key", (1.12, axis_y + 0.13, 0.0), (0.28, 0.05, 0.08), SAFETY_YELLOW)
    g.box("ratio_nameplate", (0.30, 0.82, 0.48), (0.44, 0.24, 0.025), "#D3DBDE", render_layer=2)
    for x in (-0.88, 0.32):
        for z in (-0.34, 0.34):
            g.box(f"mounting_foot_{x}_{z}", (x, 0.18, z), (0.46, 0.16, 0.24), "#31515D")
            g.cylinder(f"anchor_{x}_{z}", (x, 0.27, z), 0.035, 0.19, FASTENER, axis="y")
    return g.done()


def _build_belt_conveyor() -> tuple[Primitive3D, ...]:
    """Slider-bed belt conveyor with crowned pulleys and guarded head drive."""

    g = GeometryBuilder()
    g.box("belt_carry_run", (0.0, 1.02, 0.0), (5.60, 0.12, 1.30), "#202A2F")
    g.box("belt_return_run", (0.0, 0.72, 0.0), (5.30, 0.08, 1.18), "#151C20")
    for z in (-0.73, 0.73):
        g.box(f"side_frame_{z}", (0.0, 0.84, z), (5.85, 0.34, 0.12), STEEL)
        g.box(f"wear_strip_{z}", (0.0, 1.10, z * 0.91), (5.55, 0.05, 0.06), LIGHT_STEEL)
    for side, x in (("tail", -2.72), ("head", 2.72)):
        g.cylinder(f"{side}_pulley", (x, 0.99, 0.0), 0.25, 1.26, "#87979D", axis="z")
        g.cylinder(f"{side}_bearing_left", (x, 0.99, -0.76), 0.18, 0.12, DARK_STEEL, axis="z")
        g.cylinder(f"{side}_bearing_right", (x, 0.99, 0.76), 0.18, 0.12, DARK_STEEL, axis="z")
    for x in (-2.15, 0.0, 2.15):
        for z in (-0.55, 0.55):
            g.box(f"leg_{x}_{z}", (x, 0.43, z), (0.14, 0.82, 0.14), DARK_STEEL)
            g.box(f"foot_{x}_{z}", (x, 0.06, z), (0.42, 0.10, 0.32), STEEL)
    g.box("drive_guard", (2.72, 0.70, 1.02), (0.70, 0.92, 0.42), SAFETY_YELLOW)
    g.box("drive_guard_mesh", (2.72, 0.70, 1.245), (0.46, 0.58, 0.025), DARK_STEEL, render_layer=2)
    g.cylinder("drive_motor", (2.72, 0.58, 1.65), 0.30, 0.88, MOTOR_BLUE, axis="z")
    g.box("belt_direction_marker", (0.75, 1.095, 0.0), (0.72, 0.018, 0.22), SAFETY_YELLOW, render_layer=2)
    return g.done()


def _build_pallet_conveyor() -> tuple[Primitive3D, ...]:
    """Twin-chain pallet conveyor with sprockets, guides, and a loaded pallet."""

    g = GeometryBuilder()
    for z in (-0.48, 0.48):
        g.box(f"chain_bed_{z}", (0.0, 0.82, z), (5.40, 0.24, 0.30), DARK_STEEL)
        g.box(f"chain_run_{z}", (0.0, 0.98, z), (5.20, 0.10, 0.18), "#65777E")
        for end, x in (("tail", -2.55), ("head", 2.55)):
            g.cylinder(f"{end}_sprocket_{z}", (x, 0.91, z), 0.22, 0.24, LIGHT_STEEL, axis="z")
    for z in (-0.78, 0.78):
        g.box(f"pallet_guide_{z}", (0.0, 1.10, z), (5.45, 0.18, 0.10), STEEL)
    for x in (-2.10, 0.0, 2.10):
        g.box(f"crossmember_{x}", (x, 0.66, 0.0), (0.18, 0.20, 1.55), STEEL)
        for z in (-0.60, 0.60):
            g.box(f"leg_{x}_{z}", (x, 0.34, z), (0.14, 0.64, 0.14), DARK_STEEL)
    g.box("pallet_load_deck", (0.0, 1.13, 0.0), (1.45, 0.14, 1.15), "#A86F32")
    for x in (-0.55, 0.0, 0.55):
        g.box(f"pallet_load_runner_{x}", (x, 1.02, 0.0), (0.18, 0.20, 1.05), "#7B4C25")
    g.box("drive_guard", (2.55, 0.62, 1.02), (0.66, 0.82, 0.40), SAFETY_YELLOW)
    g.cylinder("gearmotor", (2.55, 0.58, 1.52), 0.28, 0.72, MOTOR_BLUE, axis="z")
    return g.done()


def _build_pneumatic_cylinder() -> tuple[Primitive3D, ...]:
    """ISO profile pneumatic cylinder with ports, sensors, and clevis."""

    g = GeometryBuilder()
    g.box("profile_barrel", (-0.15, 0.72, 0.0), (1.70, 0.58, 0.62), ALUMINUM)
    for x in (-1.04, 0.74):
        g.box(f"end_cap_{x}", (x, 0.72, 0.0), (0.18, 0.72, 0.76), DARK_STEEL)
    for y in (0.45, 0.99):
        for z in (-0.28, 0.28):
            g.cylinder(f"tie_rod_{y}_{z}", (-0.15, y, z), 0.026, 1.82, STEEL, axis="x")
    g.cylinder("piston_rod", (1.15, 0.72, 0.0), 0.10, 0.78, LIGHT_STEEL, axis="x")
    g.box("rod_clevis", (1.60, 0.72, 0.0), (0.30, 0.36, 0.38), STEEL)
    for index, x in enumerate((-0.82, 0.52)):
        g.cylinder(f"air_port_{index}", (x, 1.13, 0.0), 0.07, 0.18, SENSOR_BLUE)
        g.box(f"reed_sensor_{index}", (x, 0.36, 0.33), (0.32, 0.10, 0.08), "#202A2F")
        g.box(f"sensor_led_{index}", (x + 0.08, 0.36, 0.38), (0.06, 0.04, 0.018), GREEN, render_layer=2)
    g.box("rear_clevis", (-1.28, 0.72, 0.0), (0.30, 0.54, 0.46), STEEL)
    return g.done()


def _build_parallel_gripper() -> tuple[Primitive3D, ...]:
    """Two-jaw pneumatic parallel gripper with replaceable fingers."""

    g = GeometryBuilder()
    g.box("gripper_body", (0.0, 0.48, 0.0), (0.92, 0.72, 0.72), DARK_STEEL)
    g.box("mounting_plate", (0.0, 0.10, 0.0), (1.08, 0.14, 0.90), STEEL)
    for x in (-0.31, 0.31):
        side = "left" if x < 0 else "right"
        g.box(f"{side}_jaw", (x, 0.93, 0.0), (0.28, 0.34, 0.64), "#667981")
        g.box(f"{side}_finger", (x, 1.32, 0.0), (0.18, 0.58, 0.28), LIGHT_STEEL)
        g.box(f"{side}_grip_pad", (x - math.copysign(0.105, x), 1.42, 0.0), (0.05, 0.34, 0.30), "#202A2F")
        g.cylinder(f"{side}_jaw_fastener", (x, 1.00, 0.34), 0.035, 0.08, FASTENER, axis="z")
    g.cylinder("open_port", (-0.25, 0.48, 0.40), 0.06, 0.16, SENSOR_BLUE, axis="z")
    g.cylinder("close_port", (0.25, 0.48, 0.40), 0.06, 0.16, SENSOR_BLUE, axis="z")
    g.box("position_sensor", (0.0, 0.48, 0.39), (0.28, 0.12, 0.05), GREEN, render_layer=2)
    return g.done()


def _build_pallet() -> tuple[Primitive3D, ...]:
    """Reusable four-way wooden pallet with deck boards and blocks."""

    g = GeometryBuilder()
    wood = "#A86F32"
    dark_wood = "#7B4C25"
    for index, z in enumerate((-0.48, -0.24, 0.0, 0.24, 0.48)):
        g.box(f"top_deck_{index}", (0.0, 0.34, z), (1.50, 0.12, 0.18), wood)
    for x in (-0.58, 0.0, 0.58):
        for z in (-0.45, 0.0, 0.45):
            g.box(f"support_block_{x}_{z}", (x, 0.20, z), (0.24, 0.22, 0.24), dark_wood)
    for z in (-0.45, 0.0, 0.45):
        g.box(f"bottom_runner_{z}", (0.0, 0.06, z), (1.50, 0.10, 0.18), wood)
    for index, x in enumerate((-0.58, 0.0, 0.58)):
        g.cylinder(f"deck_nail_{index}", (x, 0.41, 0.48), 0.022, 0.025, FASTENER, axis="y", render_layer=2)
    return g.done()


def _build_tote() -> tuple[Primitive3D, ...]:
    """Stackable industrial tote with reinforced rim, ribs, and label pocket."""

    g = GeometryBuilder()
    body = "#2C78A0"
    g.box("tote_body", (0.0, 0.55, 0.0), (1.40, 0.92, 0.94), body)
    g.box("tote_inner_shadow", (0.0, 1.02, 0.0), (1.18, 0.05, 0.72), "#122C38")
    for z in (-0.54, 0.54):
        g.box(f"rim_long_{z}", (0.0, 1.03, z), (1.52, 0.14, 0.14), "#1E5879")
    for x in (-0.76, 0.76):
        g.box(f"rim_short_{x}", (x, 1.03, 0.0), (0.14, 0.14, 1.08), "#1E5879")
        g.box(f"handle_{x}", (x + math.copysign(0.025, x), 0.78, 0.0), (0.06, 0.22, 0.46), "#122C38", render_layer=2)
    for index, x in enumerate((-0.48, -0.16, 0.16, 0.48)):
        g.box(f"front_rib_{index}", (x, 0.52, 0.49), (0.055, 0.70, 0.05), "#1E5879", render_layer=2)
    _add_legend_surface(g, "label_pocket", (0.0, 0.54, 0.505), (0.46, 0.24, 0.025))
    return g.done()


def _build_hopper() -> tuple[Primitive3D, ...]:
    """Four-leg bulk hopper with tapered bin, outlet slide gate, and vibrator."""

    g = GeometryBuilder()
    g.frustum("hopper_bin", (0.0, 2.30, 0.0), 0.56, 1.42, 1.75, "#87989F", opacity=245)
    g.box("top_rim", (0.0, 3.20, 0.0), (2.95, 0.16, 2.95), STEEL)
    g.box("top_opening", (0.0, 3.30, 0.0), (2.55, 0.08, 2.55), "#152127")
    g.box("outlet_transition", (0.0, 1.30, 0.0), (0.72, 0.34, 0.72), DARK_STEEL)
    g.box("slide_gate", (0.0, 1.08, 0.0), (0.96, 0.12, 0.82), STEEL)
    g.box("gate_actuator", (0.82, 1.08, 0.0), (0.72, 0.20, 0.24), SENSOR_BLUE)
    for index, (x, z) in enumerate(((-1.18, -1.18), (-1.18, 1.18), (1.18, -1.18), (1.18, 1.18))):
        g.box(f"leg_{index}", (x, 1.20, z), (0.16, 2.28, 0.16), DARK_STEEL)
        g.box(f"foot_{index}", (x, 0.06, z), (0.44, 0.10, 0.44), STEEL)
    g.cylinder("bin_vibrator", (1.05, 2.20, 0.0), 0.20, 0.42, MOTOR_BLUE, axis="x")
    return g.done()


def _build_silo() -> tuple[Primitive3D, ...]:
    """Vertical storage silo with cone bottom, ladder, roof vent, and load cells."""

    g = GeometryBuilder()
    g.cylinder("silo_shell", (0.0, 3.00, 0.0), 1.28, 3.40, "#A8B7BD")
    g.frustum("cone_bottom", (0.0, 0.98, 0.0), 0.34, 1.28, 1.25, "#92A4AB")
    g.frustum("roof", (0.0, 4.95, 0.0), 1.28, 0.20, 0.50, "#B9C4C8")
    g.cylinder("fill_nozzle", (0.0, 5.42, 0.0), 0.18, 0.48, LIGHT_STEEL)
    g.cylinder("roof_vent", (-0.62, 5.25, 0.15), 0.15, 0.42, STEEL)
    g.cylinder("discharge_spout", (0.0, 0.22, 0.0), 0.20, 0.52, DARK_STEEL)
    for index, (x, z) in enumerate(((-0.82, -0.72), (-0.82, 0.72), (0.82, -0.72), (0.82, 0.72))):
        g.box(f"support_leg_{index}", (x, 0.64, z), (0.18, 1.18, 0.18), DARK_STEEL)
        g.box(f"load_cell_{index}", (x, 0.12, z), (0.32, 0.14, 0.32), SENSOR_BLUE)
    g.box("ladder_left_rail", (-1.34, 3.08, 0.0), (0.08, 4.20, 0.08), DARK_STEEL)
    g.box("ladder_right_rail", (-1.34, 3.08, 0.46), (0.08, 4.20, 0.08), DARK_STEEL)
    for index in range(12):
        g.box(f"ladder_rung_{index:02d}", (-1.34, 1.18 + index * 0.34, 0.23), (0.08, 0.06, 0.48), LIGHT_STEEL)
    return g.done()


def _build_safety_fence() -> tuple[Primitive3D, ...]:
    """Modular perimeter guard panel with posts, mesh, feet, and kickplate."""

    g = GeometryBuilder()
    for x in (-1.55, 1.55):
        g.box(f"post_{x}", (x, 1.20, 0.0), (0.16, 2.40, 0.16), DARK_STEEL)
        g.box(f"post_foot_{x}", (x, 0.05, 0.0), (0.48, 0.10, 0.48), STEEL)
        for z in (-0.16, 0.16):
            g.cylinder(f"anchor_{x}_{z}", (x, 0.12, z), 0.035, 0.16, FASTENER, axis="y")
    for y in (0.35, 2.12):
        g.box(f"frame_rail_{y}", (0.0, y, 0.0), (2.98, 0.12, 0.12), SAFETY_YELLOW)
    for index in range(13):
        x = -1.38 + index * 0.23
        g.box(f"mesh_vertical_{index:02d}", (x, 1.24, 0.0), (0.025, 1.68, 0.025), "#71848C")
    for index in range(8):
        y = 0.46 + index * 0.22
        g.box(f"mesh_horizontal_{index:02d}", (0.0, y, 0.0), (2.76, 0.025, 0.025), "#71848C")
    g.box("kickplate", (0.0, 0.18, 0.0), (2.98, 0.25, 0.08), "#C89A22")
    return g.done()


def _build_safety_gate() -> tuple[Primitive3D, ...]:
    """Hinged machine guard gate with trapped-key switch and latch."""

    g = GeometryBuilder()
    for x in (-1.45, 1.45):
        g.box(f"gate_post_{x}", (x, 1.25, 0.0), (0.18, 2.50, 0.18), DARK_STEEL)
        g.box(f"gate_post_foot_{x}", (x, 0.05, 0.0), (0.50, 0.10, 0.50), STEEL)
    for y in (0.34, 2.20):
        g.box(f"gate_frame_horizontal_{y}", (0.0, y, 0.0), (2.66, 0.14, 0.14), SAFETY_YELLOW)
    for x in (-1.24, 1.24):
        g.box(f"gate_frame_vertical_{x}", (x, 1.27, 0.0), (0.14, 1.98, 0.14), SAFETY_YELLOW)
    for index in range(11):
        x = -1.08 + index * 0.216
        g.box(f"gate_mesh_vertical_{index:02d}", (x, 1.27, 0.0), (0.025, 1.72, 0.025), "#71848C")
    for index in range(7):
        y = 0.52 + index * 0.24
        g.box(f"gate_mesh_horizontal_{index:02d}", (0.0, y, 0.0), (2.28, 0.025, 0.025), "#71848C")
    for y in (0.72, 1.78):
        g.cylinder(f"hinge_{y}", (-1.32, y, 0.0), 0.08, 0.28, FASTENER)
    g.box("latch_handle", (0.98, 1.30, 0.12), (0.18, 0.52, 0.12), DARK_STEEL)
    g.box("safety_switch", (1.44, 1.62, 0.0), (0.30, 0.46, 0.28), SENSOR_BLUE)
    g.box("trapped_key", (1.28, 1.62, 0.18), (0.10, 0.24, 0.08), RED, render_layer=2)
    return g.done()


def _build_light_curtain() -> tuple[Primitive3D, ...]:
    """Paired safety light curtain with beam field and status indicators."""

    g = GeometryBuilder()
    for side, x in (("sender", -1.15), ("receiver", 1.15)):
        g.box(f"{side}_housing", (x, 1.28, 0.0), (0.18, 2.32, 0.20), SAFETY_YELLOW)
        g.box(f"{side}_black_face", (x, 1.28, 0.115), (0.10, 2.10, 0.035), "#172126", render_layer=2)
        g.box(f"{side}_base", (x, 0.06, 0.0), (0.48, 0.12, 0.48), STEEL)
        g.box(f"{side}_status_green", (x, 2.30, 0.14), (0.06, 0.10, 0.025), GREEN, render_layer=3)
        g.box(f"{side}_status_red", (x, 2.16, 0.14), (0.06, 0.10, 0.025), RED, render_layer=3)
    for index in range(16):
        y = 0.34 + index * 0.12
        g.box(f"safety_beam_{index:02d}", (0.0, y, 0.13), (2.18, 0.018, 0.018), RED, opacity=125, render_layer=4)
    return g.done()


def _build_proximity_sensor() -> tuple[Primitive3D, ...]:
    """Threaded M18 inductive proximity sensor with locknuts and cable."""

    g = GeometryBuilder()
    g.cylinder("threaded_barrel", (0.0, 0.78, 0.0), 0.18, 1.24, "#B6C3C8")
    for index, y in enumerate((0.38, 1.12)):
        g.cylinder(f"locknut_{index}", (0.0, y, 0.0), 0.27, 0.12, STEEL)
    g.cylinder("sensing_face", (0.0, 1.44, 0.0), 0.17, 0.10, SENSOR_BLUE)
    g.cylinder("status_ring", (0.0, 1.25, 0.0), 0.19, 0.08, GREEN)
    g.cylinder("m12_connector", (0.0, 0.10, 0.0), 0.12, 0.24, DARK_STEEL)
    g.cylinder("cable", (0.0, -0.14, 0.0), 0.055, 0.28, "#10181C")
    g.box("mounting_bracket", (0.38, 0.76, 0.0), (0.58, 0.12, 0.58), STEEL)
    g.cylinder("bracket_hole", (0.62, 0.76, 0.0), 0.06, 0.14, FASTENER, axis="y")
    return g.done()


def _build_control_panel() -> tuple[Primitive3D, ...]:
    """Floor-standing industrial control enclosure with operator devices."""

    g = GeometryBuilder()
    g.box("enclosure", (0.0, 1.45, 0.0), (1.72, 2.80, 0.72), "#C6CFD2")
    g.box("door", (0.0, 1.48, 0.385), (1.58, 2.62, 0.06), "#DDE4E6", render_layer=1)
    _add_panel_seam(g, "door_gasket", (0.0, 1.48, 0.422), (1.46, 2.50, 0.018), color=DARK_STEEL)
    for y in (0.38, 1.45, 2.50):
        g.cylinder(f"hinge_{y}", (-0.84, y, 0.38), 0.055, 0.20, DARK_STEEL)
    g.box("hmi_bezel", (0.15, 1.98, 0.44), (0.82, 0.62, 0.08), DARK_STEEL, render_layer=2)
    g.box("hmi_screen", (0.15, 1.98, 0.49), (0.66, 0.46, 0.025), "#1A637B", render_layer=3)
    g.cylinder("start_button", (-0.36, 1.15, 0.47), 0.11, 0.10, GREEN, axis="z", render_layer=3)
    g.cylinder("stop_button", (0.0, 1.15, 0.47), 0.11, 0.10, RED, axis="z", render_layer=3)
    g.cylinder("reset_button", (0.36, 1.15, 0.47), 0.11, 0.10, SENSOR_BLUE, axis="z", render_layer=3)
    g.box("main_disconnect", (0.54, 0.55, 0.45), (0.30, 0.46, 0.12), SAFETY_YELLOW, render_layer=2)
    g.box("disconnect_handle", (0.54, 0.55, 0.54), (0.10, 0.34, 0.10), RED, rotation=(0.0, 0.0, -35.0), render_layer=3)
    for index in range(8):
        g.box(f"vent_slot_{index:02d}", (-0.36 + index * 0.10, 0.28, 0.44), (0.06, 0.16, 0.025), DARK_STEEL, render_layer=2)
    g.box("plinth", (0.0, 0.08, 0.0), (1.82, 0.16, 0.82), DARK_STEEL)
    return g.done()


def _build_vfd_cabinet() -> tuple[Primitive3D, ...]:
    """Drive cabinet with local keypad, cooling path, and cable entry."""

    g = GeometryBuilder()
    g.box("cabinet", (0.0, 1.28, 0.0), (1.35, 2.46, 0.78), "#BFC9CD")
    g.box("cabinet_door", (0.0, 1.30, 0.415), (1.23, 2.32, 0.06), "#D8E0E2", render_layer=1)
    g.box("drive_keypad_bezel", (0.0, 1.72, 0.46), (0.58, 0.72, 0.08), DARK_STEEL, render_layer=2)
    g.box("drive_display", (0.0, 1.92, 0.51), (0.38, 0.18, 0.025), "#63C7D7", render_layer=3)
    for row in range(3):
        for column in range(3):
            g.box(f"key_{row}_{column}", (-0.16 + column * 0.16, 1.58 - row * 0.14, 0.51), (0.10, 0.08, 0.025), "#65777E", render_layer=3)
    for index in range(9):
        g.box(f"intake_louver_{index:02d}", (-0.42 + index * 0.105, 0.50, 0.46), (0.07, 0.18, 0.025), DARK_STEEL, render_layer=2)
    g.cylinder("cooling_fan", (0.0, 2.22, -0.43), 0.28, 0.08, DARK_STEEL, axis="z")
    for index in range(6):
        angle = index * 60.0
        radians = math.radians(angle)
        g.box(f"fan_blade_{index:02d}", (0.18 * math.cos(radians), 2.22 + 0.18 * math.sin(radians), -0.48), (0.24, 0.07, 0.025), "#71848C", rotation=(0.0, 0.0, angle), render_layer=2)
    g.box("door_handle", (0.52, 1.20, 0.49), (0.12, 0.46, 0.12), DARK_STEEL, render_layer=3)
    g.box("cable_gland_plate", (0.0, 0.08, 0.0), (1.08, 0.10, 0.58), STEEL)
    for x in (-0.35, 0.0, 0.35):
        g.cylinder(f"cable_gland_{x}", (x, 0.02, 0.0), 0.08, 0.16, DARK_STEEL)
    return g.done()


def _build_air_compressor() -> tuple[Primitive3D, ...]:
    """Enclosed rotary-screw compressor package with service panels."""

    g = GeometryBuilder()
    g.box("compressor_enclosure", (0.0, 1.15, 0.0), (2.70, 2.18, 1.42), "#D6C52D")
    g.box("service_door", (0.52, 1.18, 0.735), (1.42, 1.88, 0.06), "#E3D94A", render_layer=1)
    _add_panel_seam(g, "service_door_seam", (0.52, 1.18, 0.77), (1.30, 1.76, 0.018))
    g.box("controller_bezel", (-0.72, 1.58, 0.76), (0.48, 0.54, 0.08), DARK_STEEL, render_layer=2)
    g.box("controller_screen", (-0.72, 1.68, 0.81), (0.32, 0.18, 0.025), "#63C7D7", render_layer=3)
    for index in range(8):
        g.box(f"cooling_louver_{index:02d}", (-0.72 + index * 0.18, 0.46, 0.76), (0.11, 0.30, 0.025), DARK_STEEL, render_layer=2)
    g.cylinder("discharge_connection", (1.48, 1.54, 0.0), 0.15, 0.34, STEEL, axis="x")
    g.box("base_skid", (0.0, 0.08, 0.0), (2.92, 0.16, 1.62), DARK_STEEL)
    return g.done()


def _build_air_receiver() -> tuple[Primitive3D, ...]:
    """Vertical compressed-air receiver with relief and drain hardware."""

    g = GeometryBuilder()
    g.cylinder("receiver_shell", (0.0, 1.82, 0.0), 0.78, 2.65, "#9FB0B6")
    g.frustum("top_head", (0.0, 3.24, 0.0), 0.78, 0.12, 0.30, "#B7C3C7")
    g.frustum("bottom_head", (0.0, 0.40, 0.0), 0.12, 0.78, 0.30, "#87999F")
    g.cylinder("inlet", (-0.94, 2.18, 0.0), 0.15, 0.46, STEEL, axis="x")
    g.cylinder("outlet", (0.94, 2.18, 0.0), 0.15, 0.46, STEEL, axis="x")
    g.cylinder("relief_valve", (-0.28, 3.58, 0.0), 0.08, 0.34, RED)
    g.cylinder("pressure_gauge", (0.32, 3.48, 0.0), 0.18, 0.10, "#F5F2DF", axis="z")
    g.cylinder("automatic_drain", (0.0, 0.12, 0.0), 0.10, 0.34, SENSOR_BLUE)
    for index, (x, z) in enumerate(((-0.50, -0.42), (-0.50, 0.42), (0.50, -0.42), (0.50, 0.42))):
        g.box(f"leg_{index}", (x, 0.38, z), (0.14, 0.70, 0.14), DARK_STEEL)
        g.box(f"foot_{index}", (x, 0.05, z), (0.36, 0.10, 0.32), STEEL)
    return g.done()


def _build_air_dryer() -> tuple[Primitive3D, ...]:
    """Twin-tower desiccant air dryer with switching manifold."""

    g = GeometryBuilder()
    for side, x in (("left", -0.58), ("right", 0.58)):
        g.cylinder(f"{side}_tower", (x, 1.65, 0.0), 0.42, 2.45, "#A8B7BD")
        g.frustum(f"{side}_top_head", (x, 2.96, 0.0), 0.42, 0.12, 0.20, LIGHT_STEEL)
        g.frustum(f"{side}_bottom_head", (x, 0.34, 0.0), 0.12, 0.42, 0.20, STEEL)
        g.box(f"{side}_status", (x, 1.64, 0.44), (0.18, 0.34, 0.035), GREEN if x < 0 else AMBER, render_layer=2)
    g.box("upper_manifold", (0.0, 3.18, 0.0), (1.70, 0.18, 0.26), DARK_STEEL)
    g.box("lower_manifold", (0.0, 0.16, 0.0), (1.70, 0.18, 0.26), DARK_STEEL)
    for x in (-0.28, 0.28):
        g.cylinder(f"switching_valve_{x}", (x, 0.16, 0.0), 0.16, 0.28, SENSOR_BLUE)
    g.box("dryer_controller", (1.25, 1.55, 0.0), (0.62, 0.92, 0.46), DARK_STEEL)
    g.box("controller_display", (1.25, 1.72, 0.245), (0.38, 0.20, 0.025), "#63C7D7", render_layer=2)
    return g.done()


def _build_hydraulic_power_unit() -> tuple[Primitive3D, ...]:
    """Hydraulic reservoir skid with pump, motor, filters, and valve manifold."""

    g = GeometryBuilder()
    g.box("reservoir", (0.0, 0.62, 0.0), (2.65, 1.12, 1.46), "#315A72")
    g.box("reservoir_lid", (0.0, 1.22, 0.0), (2.78, 0.10, 1.58), STEEL)
    g.cylinder("motor", (-0.72, 1.66, 0.0), 0.34, 0.98, MOTOR_BLUE, axis="x")
    g.cylinder("pump", (0.06, 1.66, 0.0), 0.26, 0.46, DARK_STEEL, axis="x")
    g.box("valve_manifold", (0.82, 1.68, 0.0), (0.76, 0.52, 0.58), ALUMINUM)
    for index, x in enumerate((0.56, 0.82, 1.08)):
        g.cylinder(f"solenoid_{index}", (x, 2.06, 0.0), 0.10, 0.30, SENSOR_BLUE)
    g.cylinder("return_filter", (0.74, 1.34, -0.52), 0.18, 0.52, "#D6C52D")
    g.cylinder("breather_cap", (-1.00, 1.42, 0.42), 0.14, 0.24, DARK_STEEL)
    g.box("level_gauge", (-1.34, 0.62, 0.0), (0.04, 0.62, 0.18), "#43C7F4", opacity=170, render_layer=2)
    return g.done()


def _build_heat_exchanger() -> tuple[Primitive3D, ...]:
    """Gasketed plate-and-frame heat exchanger with four process ports."""

    g = GeometryBuilder()
    for x in (-0.72, 0.72):
        g.box(f"frame_plate_{x}", (x, 1.30, 0.0), (0.18, 2.35, 1.52), DARK_STEEL)
        g.box(f"frame_foot_{x}", (x, 0.08, 0.0), (0.62, 0.16, 1.78), STEEL)
    for index in range(13):
        x = -0.54 + index * 0.09
        g.box(f"heat_transfer_plate_{index:02d}", (x, 1.32, 0.0), (0.035, 2.05, 1.32), "#AAB7BD")
    for y in (0.38, 2.22):
        for z in (-0.58, 0.58):
            g.cylinder(f"tie_bolt_{y}_{z}", (0.0, y, z), 0.035, 1.64, FASTENER, axis="x")
    for index, (y, z) in enumerate(((0.62, -0.82), (2.02, -0.82), (0.62, 0.82), (2.02, 0.82))):
        g.cylinder(f"process_port_{index}", (-0.82, y, z), 0.18, 0.36, STEEL, axis="x")
    return g.done()


def _build_mixer_agitator() -> tuple[Primitive3D, ...]:
    """Top-entry tank agitator with gearbox, shaft, and pitched blades."""

    g = GeometryBuilder()
    g.cylinder("mixing_vessel", (0.0, 1.55, 0.0), 1.02, 2.40, "#A8B7BD", opacity=170)
    g.cylinder("top_flange", (0.0, 2.84, 0.0), 0.46, 0.12, STEEL)
    g.box("gearbox", (0.0, 3.18, 0.0), (0.72, 0.58, 0.72), DARK_STEEL)
    g.cylinder("agitator_motor", (0.0, 3.78, 0.0), 0.34, 0.78, MOTOR_BLUE)
    g.cylinder("agitator_shaft", (0.0, 1.76, 0.0), 0.07, 2.70, LIGHT_STEEL)
    g.cylinder("impeller_hub", (0.0, 0.78, 0.0), 0.16, 0.28, DARK_STEEL)
    for index in range(4):
        angle = index * 90.0
        radians = math.radians(angle)
        g.box(f"impeller_blade_{index}", (0.48 * math.cos(radians), 0.78, 0.48 * math.sin(radians)), (0.78, 0.10, 0.26), LIGHT_STEEL, rotation=(0.0, -18.0, angle))
    for index, (x, z) in enumerate(((-0.68, -0.60), (-0.68, 0.60), (0.68, -0.60), (0.68, 0.60))):
        g.box(f"vessel_leg_{index}", (x, 0.32, z), (0.14, 0.62, 0.14), DARK_STEEL)
    return g.done()


def _build_weigh_scale() -> tuple[Primitive3D, ...]:
    """Low-profile platform scale with four load cells and indicator."""

    g = GeometryBuilder()
    g.box("scale_platform", (0.0, 0.24, 0.0), (2.20, 0.18, 1.75), LIGHT_STEEL)
    g.box("scale_frame", (0.0, 0.11, 0.0), (2.34, 0.12, 1.89), DARK_STEEL)
    for index, (x, z) in enumerate(((-0.88, -0.68), (-0.88, 0.68), (0.88, -0.68), (0.88, 0.68))):
        g.box(f"load_cell_{index}", (x, 0.05, z), (0.28, 0.10, 0.22), SENSOR_BLUE)
    g.box("indicator_post", (1.45, 0.90, 0.0), (0.12, 1.42, 0.12), DARK_STEEL)
    g.box("weight_indicator", (1.45, 1.56, 0.0), (0.72, 0.52, 0.34), "#D8E0E2")
    g.box("weight_display", (1.45, 1.66, 0.18), (0.48, 0.18, 0.025), "#63C7D7", render_layer=2)
    return g.done()


def _build_barcode_scanner() -> tuple[Primitive3D, ...]:
    """Fixed-mount barcode reader with aiming beam and adjustable bracket."""

    g = GeometryBuilder()
    g.box("scanner_base", (0.0, 0.06, 0.0), (0.70, 0.12, 0.64), STEEL)
    g.box("scanner_post", (0.0, 0.72, 0.0), (0.12, 1.26, 0.12), DARK_STEEL)
    g.box("adjustable_bracket", (0.0, 1.26, 0.0), (0.62, 0.16, 0.22), STEEL)
    g.box("scanner_housing", (0.0, 1.48, 0.0), (0.58, 0.42, 0.46), SENSOR_BLUE, rotation=(0.0, 0.0, -12.0))
    g.box("scanner_window", (0.0, 1.48, 0.25), (0.38, 0.22, 0.035), "#172126", render_layer=2)
    g.box("aiming_beam", (0.0, 1.12, 0.70), (0.025, 0.025, 1.05), RED, opacity=130, rotation=(0.0, 0.0, -12.0), render_layer=3)
    g.box("status_led", (0.20, 1.62, 0.24), (0.06, 0.08, 0.025), GREEN, render_layer=3)
    return g.done()


def _build_vision_camera() -> tuple[Primitive3D, ...]:
    """Industrial smart camera with lens, illumination ring, and mount."""

    g = GeometryBuilder()
    g.box("camera_base", (0.0, 0.06, 0.0), (0.78, 0.12, 0.68), STEEL)
    g.box("camera_post", (0.0, 0.92, 0.0), (0.14, 1.62, 0.14), DARK_STEEL)
    g.box("camera_arm", (0.38, 1.62, 0.0), (0.82, 0.14, 0.18), STEEL)
    g.box("camera_body", (0.82, 1.48, 0.0), (0.52, 0.52, 0.58), SENSOR_BLUE)
    g.cylinder("lens_barrel", (0.82, 1.48, 0.40), 0.18, 0.30, DARK_STEEL, axis="z")
    g.tube("illumination_ring", (0.82, 1.48, 0.58), 0.31, 0.22, 0.10, "#F2FBFC", axis="z")
    g.frustum("field_of_view", (0.82, 0.88, 1.38), 0.58, 0.12, 1.55, "#43C7F4", axis="z", opacity=50, end_caps=False)
    g.box("camera_status", (1.09, 1.62, 0.18), (0.025, 0.08, 0.10), GREEN, render_layer=3)
    return g.done()


def _build_roller_transfer() -> tuple[Primitive3D, ...]:
    """Pop-up chain transfer module integrated into a roller conveyor bed."""

    g = GeometryBuilder()
    for index in range(9):
        x = -2.0 + index * 0.5
        g.cylinder(f"roller_{index:02d}", (x, 0.94, 0.0), 0.10, 1.46, LIGHT_STEEL, axis="z")
    for z in (-0.82, 0.82):
        g.box(f"side_frame_{z}", (0.0, 0.82, z), (4.36, 0.28, 0.14), STEEL)
    for z in (-0.42, 0.0, 0.42):
        g.box(f"popup_chain_{z}", (0.0, 1.06, z), (2.20, 0.12, 0.12), DARK_STEEL)
    g.box("lift_carriage", (0.0, 0.60, 0.0), (2.40, 0.18, 1.20), SAFETY_YELLOW)
    g.cylinder("lift_cylinder", (0.0, 0.30, 0.0), 0.16, 0.46, ALUMINUM)
    g.box("transfer_drive", (0.0, 0.62, 1.08), (0.78, 0.54, 0.42), DARK_STEEL)
    return g.done()


def _build_conveyor_turntable() -> tuple[Primitive3D, ...]:
    """Powered roller turntable for ninety-degree pallet routing."""

    g = GeometryBuilder()
    g.cylinder("turntable_base", (0.0, 0.26, 0.0), 1.65, 0.46, DARK_STEEL)
    g.cylinder("rotating_deck", (0.0, 0.56, 0.0), 1.50, 0.18, STEEL)
    for index in range(7):
        x = -1.20 + index * 0.40
        g.cylinder(f"deck_roller_{index:02d}", (x, 0.74, 0.0), 0.09, 1.90, LIGHT_STEEL, axis="z")
    g.cylinder("center_bearing", (0.0, 0.40, 0.0), 0.38, 0.34, "#172126")
    g.box("index_drive", (1.76, 0.38, 0.0), (0.72, 0.58, 0.56), MOTOR_BLUE)
    for angle in (0, 90, 180, 270):
        radians = math.radians(angle)
        g.box(f"index_marker_{angle}", (1.34 * math.cos(radians), 0.68, 1.34 * math.sin(radians)), (0.16, 0.04, 0.16), SAFETY_YELLOW, render_layer=2)
    return g.done()


def _build_vertical_lift() -> tuple[Primitive3D, ...]:
    """Guarded vertical conveyor lift with carriage and counterweight."""

    g = GeometryBuilder()
    for x in (-1.18, 1.18):
        g.box(f"mast_{x}", (x, 2.50, 0.0), (0.20, 5.00, 0.24), DARK_STEEL)
        g.box(f"mast_foot_{x}", (x, 0.06, 0.0), (0.58, 0.12, 0.70), STEEL)
    g.box("top_crossbeam", (0.0, 4.88, 0.0), (2.58, 0.22, 0.34), STEEL)
    g.box("lift_carriage", (0.0, 1.72, 0.0), (2.05, 0.22, 1.58), SAFETY_YELLOW)
    for index in range(5):
        x = -0.80 + index * 0.40
        g.cylinder(f"carriage_roller_{index}", (x, 1.88, 0.0), 0.08, 1.36, LIGHT_STEEL, axis="z")
    g.box("counterweight", (0.82, 3.18, -0.42), (0.42, 1.15, 0.32), "#536873")
    for x in (-0.82, 0.82):
        g.cylinder(f"top_sheave_{x}", (x, 4.58, 0.0), 0.24, 0.16, LIGHT_STEEL, axis="z")
    g.box("hoist_motor", (0.0, 4.52, -0.58), (0.82, 0.52, 0.48), MOTOR_BLUE)
    g.box("lower_gate", (0.0, 0.86, 0.88), (2.10, 1.62, 0.08), "#71848C", opacity=155)
    return g.done()


def _build_diverter_arm() -> tuple[Primitive3D, ...]:
    """Pneumatic swing-arm conveyor diverter with impact rollers."""

    g = GeometryBuilder()
    g.box("mounting_base", (-0.82, 0.12, 0.0), (0.82, 0.24, 0.92), STEEL)
    g.cylinder("pivot_column", (-0.82, 0.92, 0.0), 0.16, 1.52, DARK_STEEL)
    g.box("diverter_arm", (0.18, 1.48, 0.0), (2.12, 0.22, 0.26), SAFETY_YELLOW, rotation=(0.0, 25.0, 0.0))
    for index in range(6):
        x = -0.58 + index * 0.34
        g.cylinder(f"impact_roller_{index}", (x, 1.48, 0.18), 0.09, 0.30, "#202A2F", axis="z")
    g.cylinder("swing_cylinder", (-0.20, 0.70, -0.34), 0.12, 1.18, ALUMINUM, axis="x", rotation=(0.0, 0.0, 22.0))
    g.box("extended_sensor", (-0.72, 1.20, 0.24), (0.22, 0.10, 0.08), SENSOR_BLUE)
    g.box("retracted_sensor", (-0.72, 0.72, 0.24), (0.22, 0.10, 0.08), SENSOR_BLUE)
    return g.done()


def _build_amr() -> tuple[Primitive3D, ...]:
    """Low-profile autonomous mobile robot with safety scanners and lift deck."""

    g = GeometryBuilder()
    g.box("amr_chassis", (0.0, 0.34, 0.0), (2.10, 0.52, 1.35), "#D6C52D")
    g.box("lift_deck", (0.0, 0.66, 0.0), (1.72, 0.14, 1.10), DARK_STEEL)
    for x in (-0.72, 0.72):
        g.cylinder(f"drive_wheel_{x}", (x, 0.26, 0.0), 0.23, 0.18, "#151C20", axis="z")
    for x in (-0.86, 0.86):
        for z in (-0.48, 0.48):
            g.sphere(f"caster_{x}_{z}", (x, 0.16, z), 0.10, "#65777E")
    for side, x in (("front", 1.08), ("rear", -1.08)):
        g.cylinder(f"{side}_safety_scanner", (x, 0.40, 0.0), 0.20, 0.16, SENSOR_BLUE, axis="x")
        g.frustum(f"{side}_scanner_field", (x + (0.70 if x > 0 else -0.70), 0.34, 0.0), 0.78, 0.10, 1.20, "#43C7F4", axis="x", opacity=40, end_caps=False)
    g.box("status_light", (0.0, 0.80, 0.0), (0.62, 0.08, 0.18), GREEN, render_layer=3)
    g.box("emergency_stop", (0.62, 0.62, 0.70), (0.18, 0.12, 0.08), RED, render_layer=3)
    return g.done()


ASSET_DEFINITIONS: tuple[NativeAssetDefinition, ...] = (
    NativeAssetDefinition(
        approval_id="A01",
        asset_type="motor",
        label="Foot-mounted AC induction motor",
        reference_name="Siemens SIMOTICS GP/SD",
        reference_url=(
            "https://cache.industry.siemens.com/dl/files/197/109749197/"
            "att_1122986/v1/Motors-D81-1-complete-English-12-2022.pdf"
        ),
        builder=_build_motor,
        view_span=3.4,
    ),
    NativeAssetDefinition(
        "A02",
        "conveyor",
        "End-driven roller conveyor",
        "Dorner 2200 end drive",
        "https://www.dornerconveyors.com/europe/products/2200-series/"
        "2200-belted-conveyor/flat-belt-end-drive",
        _build_conveyor,
        7.2,
    ),
    NativeAssetDefinition(
        "A03",
        "box",
        "FEFCO 0201 product carton",
        "FEFCO regular slotted case",
        "https://www.fefco.org/node/656",
        _build_box,
        3.0,
    ),
    NativeAssetDefinition(
        "A04",
        "photoeye",
        "Through-beam photoeye pair",
        "SICK W4 WSE4-3",
        "https://www.sick.com/media/pdf/5/85/085/"
        "dataSheet_WSE4-3P2130_1028163_en.pdf",
        _build_photoeye,
        3.5,
    ),
    NativeAssetDefinition(
        "A05",
        "switch",
        "22 mm operator pushbutton station",
        "Allen-Bradley 800F",
        "https://www.rockwellautomation.com/en-us/products/hardware/"
        "push-buttons-and-signaling-devices/800f-round-push-buttons.html",
        _build_switch,
        2.7,
    ),
    NativeAssetDefinition(
        "A06",
        "indicator",
        "Three-color modular stacklight",
        "PATLITE LR series",
        "https://shop.patlite.com/Articles.asp?=&ID=266",
        _build_indicator,
        4.6,
    ),
    NativeAssetDefinition(
        "A07",
        "pump",
        "Close-coupled end-suction pump",
        "Grundfos NB/NBE",
        "https://www.grundfos.com/au/learn/ecademy/all-courses/"
        "grundfos-end-suction-pumps/introduction-to-end-suction-pumps",
        _build_pump,
        4.9,
    ),
    NativeAssetDefinition(
        "A08",
        "fan",
        "Tubular industrial axial fan",
        "Greenheck TBI-CA",
        "https://www.greenheck.com/products/fans/inline/tbi-ca",
        _build_fan,
        5.0,
    ),
    NativeAssetDefinition(
        "A09",
        "pusher",
        "ISO profile pneumatic pusher",
        "Festo DSBC",
        "https://festo.com/rep/en-us_us/assets/pdf/Standard_Cylinders_DSBC.pdf",
        _build_pusher,
        4.5,
    ),
    NativeAssetDefinition(
        "A10",
        "tank",
        "Freestanding stainless process tank",
        "Alfa Laval tank equipment",
        "https://www.alfalaval.com/products/process-solutions/"
        "brewery-solutions/tank-top-systems/",
        _build_tank,
        5.8,
    ),
    NativeAssetDefinition(
        "A11",
        "levelSensor",
        "Side-mounted point level switch",
        "ifm LMT/LM",
        "https://www.ifm.com/in/en/shared/products/level/lm/"
        "point-level-detection",
        _build_level_sensor,
        3.2,
    ),
    NativeAssetDefinition(
        "A12",
        "radarLevelSensor",
        "Top-mounted radar level transmitter",
        "VEGA VEGAPULS",
        "https://www.vega.com/en-us/products/product-catalog/level/"
        "radar/vegapuls-67",
        _build_radar_level_sensor,
        4.1,
    ),
    NativeAssetDefinition(
        "A13",
        "pipe",
        "Raised-face flanged pipe spool",
        "ASME B16.5",
        "https://www.asme.org/codes-standards/find-codes-standards/"
        "b16-5-pipe-flanges-flanged-fittings-nps-1-2-nps-24-"
        "metric-inch-standard/2025",
        _build_pipe,
        4.8,
    ),
    NativeAssetDefinition(
        "A14",
        "rotarySwitch",
        "Three-position selector station",
        "Allen-Bradley 800F selector",
        "https://www.rockwellautomation.com/en-us/products/details."
        "800FM-HR32CR.html",
        _build_rotary_switch,
        2.8,
    ),
    NativeAssetDefinition(
        "A15",
        "liftTable",
        "Hydraulic scissor lift table",
        "Southworth lift tables",
        "https://www.southworthproducts.com/scissor-lift-tables/",
        _build_lift_table,
        4.5,
    ),
    NativeAssetDefinition(
        "A16",
        "valve",
        "Cutaway wafer butterfly valve",
        "Bray Series 3-Cx",
        "https://www.bray.com/cx-line/3-cx-resilient-seated-"
        "butterfly-valve",
        _build_valve,
        4.0,
    ),
    NativeAssetDefinition(
        "A17",
        "drillPress",
        "Floor drill press",
        "Clausing 2277",
        "https://clausing-industrial.com/product/2277/",
        _build_drill_press,
        5.8,
    ),
    NativeAssetDefinition(
        "A18",
        "robotArm",
        "Six-axis handling robot",
        "FANUC M-20iD/25",
        "https://www.fanucamerica.com/products/robot/m-20id-25",
        _build_robot_arm,
        5.1,
    ),
    NativeAssetDefinition(
        "A19",
        "rollerShutter",
        "High-speed roll-up door",
        "Rytec Fast-Seal",
        "https://www.rytecdoors.com/high-performance-doors/fabric-doors/"
        "fast-seal",
        _build_roller_shutter,
        5.9,
    ),
    NativeAssetDefinition(
        "A20",
        "rotaryTable",
        "Programmable rotary indexing table",
        "WEISS Generation 5 CR-N",
        "https://gen5.weiss-world.com/en-us/",
        _build_rotary_table,
        5.0,
    ),
    NativeAssetDefinition(
        "A21",
        "machine",
        "Guarded CNC process machine",
        "Haas VF-2",
        "https://www.haascnc.com/machines/vertical-mills/vf-series/"
        "models/small/vf-2.html",
        _build_machine,
        6.4,
    ),
    NativeAssetDefinition(
        "A22",
        "gearedMotor",
        "Inline helical gearmotor",
        "SEW-EURODRIVE helical gearmotors",
        "https://www.sew-eurodrive.com/products/gearmotors/gearmotors.html",
        _build_geared_motor,
        3.8,
        "drives",
        ("motor", "gearbox", "drive", "rotary"),
    ),
    NativeAssetDefinition(
        "A23",
        "beltConveyor",
        "Slider-bed belt conveyor",
        "Dorner industrial belt conveyors",
        "https://www.dornerconveyors.com/products/belt-conveyors",
        _build_belt_conveyor,
        7.0,
        "material-handling",
        ("conveyor", "belt", "transport", "package"),
    ),
    NativeAssetDefinition(
        "A24",
        "palletConveyor",
        "Twin-chain pallet conveyor",
        "Interroll pallet handling",
        "https://www.interroll.com/products/conveyors-sorters/pallet-conveyors/",
        _build_pallet_conveyor,
        6.8,
        "material-handling",
        ("conveyor", "pallet", "chain", "transport"),
    ),
    NativeAssetDefinition(
        "A25",
        "pneumaticCylinder",
        "ISO profile pneumatic cylinder",
        "Festo DSBC standard cylinder",
        "https://www.festo.com/us/en/p/standard-cylinder-id_DSBC/",
        _build_pneumatic_cylinder,
        4.2,
        "pneumatics",
        ("cylinder", "linear", "actuator", "air"),
    ),
    NativeAssetDefinition(
        "A26",
        "parallelGripper",
        "Two-jaw parallel gripper",
        "Festo parallel grippers",
        "https://www.festo.com/us/en/c/products/industrial-automation/grippers-id_pim119/",
        _build_parallel_gripper,
        3.1,
        "robotics",
        ("gripper", "end-effector", "pneumatic", "robot"),
    ),
    NativeAssetDefinition(
        "A27",
        "pallet",
        "Four-way wooden pallet",
        "EPAL Euro pallet construction",
        "https://www.epal-pallets.org/eu-en/load-carriers/epal-euro-pallet",
        _build_pallet,
        3.0,
        "loads",
        ("pallet", "load", "carrier", "warehouse"),
    ),
    NativeAssetDefinition(
        "A28",
        "tote",
        "Stackable industrial tote",
        "SSI SCHAEFER reusable containers",
        "https://www.ssi-schaefer.com/en-us/products/storage/reusable-containers",
        _build_tote,
        3.0,
        "loads",
        ("tote", "container", "bin", "warehouse"),
    ),
    NativeAssetDefinition(
        "A29",
        "hopper",
        "Bulk material hopper",
        "Flexicon bulk handling hoppers",
        "https://www.flexicon.com/",
        _build_hopper,
        5.2,
        "process",
        ("hopper", "bulk", "powder", "gate"),
    ),
    NativeAssetDefinition(
        "A30",
        "silo",
        "Vertical storage silo",
        "Coperion bulk material storage",
        "https://www.coperion.com/en/products-services/process-equipment/storage",
        _build_silo,
        7.0,
        "process",
        ("silo", "storage", "bulk", "level"),
    ),
    NativeAssetDefinition(
        "A31",
        "safetyFence",
        "Modular machine perimeter guard",
        "Troax machine guarding",
        "https://www.troax.com/en-us/solutions/machine-guarding",
        _build_safety_fence,
        4.5,
        "safety",
        ("fence", "guard", "perimeter", "cell"),
    ),
    NativeAssetDefinition(
        "A32",
        "safetyGate",
        "Interlocked machine guard gate",
        "Troax machine guarding doors",
        "https://www.troax.com/en-us/products/machine-guarding/doors",
        _build_safety_gate,
        4.5,
        "safety",
        ("gate", "guard", "interlock", "access"),
    ),
    NativeAssetDefinition(
        "A33",
        "lightCurtain",
        "Safety light curtain pair",
        "SICK deTec safety light curtains",
        "https://www.sick.com/us/en/catalog/products/safety/safety-light-curtains/c/g185751",
        _build_light_curtain,
        4.2,
        "safety",
        ("light-curtain", "presence", "safety", "beam"),
    ),
    NativeAssetDefinition(
        "A34",
        "proximitySensor",
        "M18 inductive proximity sensor",
        "ifm inductive sensors",
        "https://www.ifm.com/us/en/category/010/010_010",
        _build_proximity_sensor,
        2.8,
        "sensors",
        ("proximity", "inductive", "sensor", "m18"),
    ),
    NativeAssetDefinition(
        "A35",
        "controlPanel",
        "Floor-standing control enclosure",
        "Rittal VX SE enclosure system",
        "https://www.rittal.com/us-en_US/products/PG20231215SCH101/PG20240304SCH001",
        _build_control_panel,
        4.7,
        "electrical",
        ("panel", "enclosure", "hmi", "controls"),
    ),
    NativeAssetDefinition(
        "A36",
        "vfdCabinet",
        "Variable-frequency-drive cabinet",
        "Siemens SINAMICS cabinet modules",
        "https://www.siemens.com/global/en/products/drives/sinamics.html",
        _build_vfd_cabinet,
        4.3,
        "electrical",
        ("vfd", "drive", "cabinet", "motor-control"),
    ),
    NativeAssetDefinition("A37", "airCompressor", "Rotary-screw air compressor", "Atlas Copco rotary screw compressors", "https://www.atlascopco.com/en-us/compressors/products/air-compressor/rotary-screw-compressor", _build_air_compressor, 4.8, "utilities", ("compressor", "air", "utility", "screw")),
    NativeAssetDefinition("A38", "airReceiver", "Vertical compressed-air receiver", "Kaeser air receivers", "https://us.kaeser.com/products-and-solutions/compressed-air-storage-and-pressure-control/air-receivers/", _build_air_receiver, 4.9, "utilities", ("receiver", "air", "pressure", "vessel")),
    NativeAssetDefinition("A39", "airDryer", "Twin-tower desiccant dryer", "Parker desiccant air dryers", "https://ph.parker.com/us/en/desiccant-air-dryers", _build_air_dryer, 4.8, "utilities", ("dryer", "air", "desiccant", "dewpoint")),
    NativeAssetDefinition("A40", "hydraulicPowerUnit", "Hydraulic power unit", "Bosch Rexroth hydraulic power units", "https://www.boschrexroth.com/en/us/products/product-groups/industrial-hydraulics/topics/hydraulic-power-units/", _build_hydraulic_power_unit, 4.8, "utilities", ("hydraulic", "pump", "reservoir", "manifold")),
    NativeAssetDefinition("A41", "heatExchanger", "Plate-and-frame heat exchanger", "Alfa Laval gasketed plate heat exchangers", "https://www.alfalaval.com/products/heat-transfer/plate-heat-exchangers/gasketed-plate-and-frame-heat-exchangers/", _build_heat_exchanger, 4.5, "process", ("heat", "exchanger", "plate", "temperature")),
    NativeAssetDefinition("A42", "mixerAgitator", "Top-entry mixer agitator", "SPX FLOW top-entry mixers", "https://www.spxflow.com/lightnin/products/top-entry-mixers/", _build_mixer_agitator, 5.5, "process", ("mixer", "agitator", "tank", "impeller")),
    NativeAssetDefinition("A43", "weighScale", "Industrial platform scale", "METTLER TOLEDO floor scales", "https://www.mt.com/us/en/home/products/Industrial_Weighing_Solutions/floor-scales-heavy-duty.html", _build_weigh_scale, 4.3, "inspection", ("scale", "weigh", "load-cell", "mass")),
    NativeAssetDefinition("A44", "barcodeScanner", "Fixed-mount barcode scanner", "Cognex DataMan fixed-mount readers", "https://www.cognex.com/products/barcode-readers/fixed-mount-barcode-readers", _build_barcode_scanner, 3.7, "inspection", ("barcode", "scanner", "reader", "traceability")),
    NativeAssetDefinition("A45", "visionCamera", "Industrial smart vision camera", "Cognex In-Sight vision systems", "https://www.cognex.com/products/machine-vision/2d-machine-vision-systems", _build_vision_camera, 4.0, "inspection", ("vision", "camera", "inspection", "quality")),
    NativeAssetDefinition("A46", "rollerTransfer", "Pop-up chain transfer", "Dorner transfer conveyors", "https://www.dornerconveyors.com/solutions/transfers", _build_roller_transfer, 5.8, "material-handling", ("transfer", "chain", "roller", "popup")),
    NativeAssetDefinition("A47", "conveyorTurntable", "Powered conveyor turntable", "Interroll pallet handling modules", "https://www.interroll.com/products/conveyors-sorters/pallet-conveyors/", _build_conveyor_turntable, 4.9, "material-handling", ("turntable", "conveyor", "rotate", "pallet")),
    NativeAssetDefinition("A48", "verticalLift", "Guarded vertical conveyor lift", "NERAK vertical conveyors", "https://www.nerak-systems.com/vertical-conveyors/", _build_vertical_lift, 6.8, "material-handling", ("lift", "vertical", "conveyor", "elevator")),
    NativeAssetDefinition("A49", "diverterArm", "Pneumatic swing-arm diverter", "Dorner conveyor diverters", "https://www.dornerconveyors.com/solutions/diverters", _build_diverter_arm, 4.4, "material-handling", ("diverter", "sort", "pneumatic", "conveyor")),
    NativeAssetDefinition("A50", "amr", "Autonomous mobile robot", "MiR autonomous mobile robots", "https://mobile-industrial-robots.com/products/robots", _build_amr, 4.6, "mobile-robotics", ("amr", "mobile", "robot", "warehouse", "scanner")),
)

ASSET_BY_TYPE = {
    definition.asset_type: definition
    for definition in ASSET_DEFINITIONS
}


def build_asset_geometry(asset_type: str) -> tuple[Primitive3D, ...]:
    """Build one isolated asset or fail clearly for an unknown type."""

    try:
        definition = ASSET_BY_TYPE[asset_type]
    except KeyError as exc:
        raise ValueError(f"Unknown native asset type: {asset_type}") from exc
    return definition.builder()
