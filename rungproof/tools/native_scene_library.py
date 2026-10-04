"""Renderer-neutral native scene compositions awaiting visual approval.

The legacy scene files remain the source contracts. This module places the
approved native asset geometry into complete machine cells without importing
Qt, Snap7, or the PLC runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from pathlib import Path
import sys
from typing import Callable

try:
    from .native_asset_library import GeometryBuilder, build_asset_geometry
    from .native_software_viewport import Primitive3D, Vec3
except ImportError:
    from native_asset_library import GeometryBuilder, build_asset_geometry
    from native_software_viewport import Primitive3D, Vec3


PROJECT_ROOT = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parents[1]
)
SOURCE_SCENE_ROOT = PROJECT_ROOT / "prototype" / "scenes"
SETUP_DOCUMENT_ROOT = PROJECT_ROOT / "docs" / "scenes"


@dataclass(frozen=True, slots=True)
class NativeSceneDefinition:
    approval_id: str
    scene_id: str
    label: str
    description: str
    source_file: Path
    setup_file: Path
    builder: Callable[[], tuple[Primitive3D, ...]]
    view_span: float


def _rotate_y(point: Vec3, yaw_degrees: float) -> Vec3:
    yaw = math.radians(yaw_degrees)
    x, y, z = point
    return (
        x * math.cos(yaw) + z * math.sin(yaw),
        y,
        -x * math.sin(yaw) + z * math.cos(yaw),
    )


def place_asset(
    asset_type: str,
    instance_id: str,
    position: Vec3,
    *,
    scale: float = 1.0,
    yaw_degrees: float = 0.0,
) -> tuple[Primitive3D, ...]:
    """Place one isolated native asset into a world-space scene."""

    if scale <= 0.0:
        raise ValueError("Scene asset scale must be greater than zero.")
    placed: list[Primitive3D] = []
    for primitive in build_asset_geometry(asset_type):
        local_center = tuple(value * scale for value in primitive.center)
        rotated = _rotate_y(local_center, yaw_degrees)
        placed.append(
            replace(
                primitive,
                role=f"{instance_id}::{primitive.role}",
                center=tuple(
                    rotated[index] + position[index]
                    for index in range(3)
                ),
                size=tuple(value * scale for value in primitive.size),
                radius=primitive.radius * scale,
                top_radius=primitive.top_radius * scale,
                inner_radius=primitive.inner_radius * scale,
                length=primitive.length * scale,
                rotation=(
                    primitive.rotation[0],
                    primitive.rotation[1] + yaw_degrees,
                    primitive.rotation[2],
                ),
            )
        )
    return tuple(placed)


def _with_indicator_state(
    geometry: tuple[Primitive3D, ...],
    *,
    active: str,
) -> tuple[Primitive3D, ...]:
    active_colors = {
        "red": "#E53935",
        "amber": "#F2B94B",
        "green": "#16A34A",
    }
    inactive_colors = {
        "red": "#5A1F24",
        "amber": "#69501B",
        "green": "#164C2A",
    }
    result: list[Primitive3D] = []
    for primitive in geometry:
        module = next(
            (
                name
                for name in ("red", "amber", "green")
                if primitive.role.endswith(f"::{name}_module")
            ),
            None,
        )
        result.append(
            replace(
                primitive,
                color=(
                    active_colors[module]
                    if module == active
                    else inactive_colors[module]
                ),
            )
            if module is not None
            else primitive
        )
    return tuple(result)


def _build_conveyor_inspection_cell() -> tuple[Primitive3D, ...]:
    geometry: list[Primitive3D] = []
    geometry.extend(
        place_asset("conveyor", "main_conveyor", (0.0, 0.0, 0.0), scale=1.15)
    )
    carton_colors = ("#C89242", "#B98B4B", "#D9A943")
    for index, (x, color) in enumerate(
        zip((-1.90, 0.15, 1.90), carton_colors, strict=True),
        1,
    ):
        carton = place_asset(
            "box",
            f"carton_{index}",
            (x, 1.10, 0.0),
            scale=0.52,
        )
        geometry.extend(
            replace(primitive, color=color)
            if primitive.role.endswith("::carton_body")
            else primitive
            for primitive in carton
        )
    geometry.extend(
        place_asset(
            "photoeye",
            "inspection_photoeye",
            (0.80, 0.0, 0.0),
            scale=1.22,
        )
    )
    geometry.extend(
        place_asset(
            "switch",
            "operator_station",
            (-3.70, 0.0, 2.55),
            scale=0.78,
        )
    )
    geometry.extend(
        _with_indicator_state(
            place_asset(
                "indicator",
                "cell_stacklight",
                (3.45, 0.0, -2.15),
                scale=0.88,
            ),
            active="amber",
        )
    )
    return tuple(geometry)


def _tank_at_level(
    instance_id: str,
    *,
    level: float,
    position: Vec3 = (0.0, 0.0, 0.0),
    scale: float = 1.18,
) -> tuple[Primitive3D, ...]:
    """Place a process tank with a truthful external level indication."""

    clamped = max(0.0, min(1.0, level))
    filled_count = round(clamped * 10)
    placed = place_asset(
        "tank",
        instance_id,
        position,
        scale=scale,
    )
    segment_centers = sorted(
        primitive.center[1]
        for primitive in placed
        if f"{instance_id}::sight_glass_segment_" in primitive.role
    )
    meniscus_y = (
        segment_centers[0]
        + clamped * (segment_centers[-1] - segment_centers[0])
    )
    fluid_bottom = position[1] + 0.50 * scale
    fluid_length = max(0.04, 2.65 * scale * clamped)
    result: list[Primitive3D] = []
    for primitive in placed:
        local_role = primitive.role.rsplit("::", 1)[-1]
        if local_role.startswith("sight_glass_segment_"):
            index = int(local_role.rsplit("_", 1)[-1])
            primitive = replace(
                primitive,
                color="#00C8F0" if index < filled_count else "#D5EEF2",
            )
        elif local_role == "sight_glass_meniscus":
            primitive = replace(
                primitive,
                center=(primitive.center[0], meniscus_y, primitive.center[2]),
            )
        elif local_role == "fluid_level":
            primitive = replace(
                primitive,
                center=(
                    primitive.center[0],
                    fluid_bottom + fluid_length / 2,
                    primitive.center[2],
                ),
                length=fluid_length,
            )
        result.append(primitive)
    return tuple(result)


def _process_piping() -> tuple[Primitive3D, ...]:
    g = GeometryBuilder()
    pipe = "#6E8189"
    flange = "#536873"
    g.cylinder(
        "inlet_riser::pipe_spool",
        (-3.35, 2.42, 0.0),
        0.15,
        2.45,
        pipe,
    )
    g.cylinder(
        "inlet_riser::lower_flange",
        (-3.35, 1.20, 0.0),
        0.27,
        0.12,
        flange,
    )
    g.cylinder(
        "inlet_riser::upper_elbow",
        (-3.35, 3.66, 0.0),
        0.27,
        0.18,
        flange,
    )
    g.cylinder(
        "inlet_header::pipe_spool",
        (-1.72, 3.66, 0.0),
        0.15,
        3.25,
        pipe,
        axis="x",
    )
    g.cylinder(
        "inlet_header::tank_flange",
        (-0.08, 3.66, 0.0),
        0.28,
        0.14,
        flange,
        axis="x",
    )
    g.cylinder(
        "outlet_header::pipe_spool",
        (2.25, 0.86, 0.0),
        0.16,
        1.65,
        pipe,
        axis="x",
    )
    g.cylinder(
        "outlet_header::end_flange",
        (3.10, 0.86, 0.0),
        0.29,
        0.14,
        flange,
        axis="x",
    )
    return g.done()


def _level_switch(
    instance_id: str,
    *,
    y: float,
    active: bool,
) -> tuple[Primitive3D, ...]:
    g = GeometryBuilder()
    g.cylinder(
        f"{instance_id}::process_nozzle",
        (1.45, y, 0.0),
        0.20,
        0.36,
        "#536873",
        axis="x",
    )
    g.cylinder(
        f"{instance_id}::sensor_body",
        (1.82, y, 0.0),
        0.17,
        0.42,
        "#87989F",
        axis="x",
    )
    g.cylinder(
        f"{instance_id}::sensor_head",
        (2.12, y, 0.0),
        0.23,
        0.22,
        "#2F6D92",
        axis="x",
    )
    g.cylinder(
        f"{instance_id}::status_led",
        (2.12, y + 0.22, 0.0),
        0.05,
        0.04,
        "#3DD6A5" if active else "#17362D",
    )
    return g.done()


def _analog_level_transmitter() -> tuple[Primitive3D, ...]:
    g = GeometryBuilder()
    g.box(
        "level_transmitter::mounting_bracket",
        (1.38, 2.20, 0.72),
        (0.16, 0.90, 0.55),
        "#536873",
    )
    g.box(
        "level_transmitter::electronics_housing",
        (1.68, 2.20, 0.72),
        (0.50, 0.68, 0.58),
        "#2F6D92",
    )
    g.box(
        "level_transmitter::local_display",
        (1.96, 2.22, 0.72),
        (0.04, 0.34, 0.34),
        "#80E8F4",
    )
    g.cylinder(
        "level_transmitter::process_connection",
        (1.38, 2.20, 0.72),
        0.13,
        0.38,
        "#AAB7BD",
        axis="x",
    )
    return g.done()


def _build_analog_tank_scene() -> tuple[Primitive3D, ...]:
    geometry: list[Primitive3D] = []
    geometry.extend(_tank_at_level("process_tank", level=0.42))
    geometry.extend(
        place_asset(
            "pump",
            "inlet_pump",
            (-4.15, 0.0, 0.0),
            scale=0.82,
        )
    )
    geometry.extend(_process_piping())
    geometry.extend(
        _level_switch("low_level_switch", y=1.15, active=False)
    )
    geometry.extend(
        _level_switch("high_level_switch", y=3.05, active=False)
    )
    geometry.extend(_analog_level_transmitter())
    geometry.extend(
        place_asset(
            "switch",
            "pump_station",
            (-3.50, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        place_asset(
            "switch",
            "drain_station",
            (-2.45, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        _with_indicator_state(
            place_asset(
                "indicator",
                "tank_stacklight",
                (3.40, 0.0, -2.05),
                scale=0.86,
            ),
            active="amber",
        )
    )
    return tuple(geometry)


def _build_high_low_tank_scene() -> tuple[Primitive3D, ...]:
    geometry: list[Primitive3D] = []
    geometry.extend(_tank_at_level("water_tank_hl", level=0.50))
    geometry.extend(
        place_asset(
            "pump",
            "hl_inlet_pump",
            (-4.15, 0.0, 0.0),
            scale=0.82,
        )
    )
    geometry.extend(_process_piping())
    geometry.extend(_level_switch("hl_low_switch", y=1.25, active=False))
    geometry.extend(_level_switch("hl_high_switch", y=3.00, active=False))
    geometry.extend(
        place_asset(
            "switch",
            "hl_pump_station",
            (-3.50, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        place_asset(
            "switch",
            "hl_drain_station",
            (-2.45, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        _with_indicator_state(
            place_asset(
                "indicator",
                "hl_stacklight",
                (3.40, 0.0, -2.05),
                scale=0.86,
            ),
            active="amber",
        )
    )
    return tuple(geometry)


def _radar_measurement_cone(
    *,
    liquid_surface_y: float,
    antenna_y: float,
) -> tuple[Primitive3D, ...]:
    g = GeometryBuilder()
    length = antenna_y - liquid_surface_y
    g.frustum(
        "radar_transmitter::measurement_cone_00",
        (0.0, liquid_surface_y + length / 2, 0.0),
        0.80,
        0.12,
        length,
        "#43C7F4",
        opacity=66,
        end_caps=False,
        render_layer=15,
    )
    return g.done()


def _build_radar_tank_scene() -> tuple[Primitive3D, ...]:
    geometry: list[Primitive3D] = []
    tank = _tank_at_level("water_tank_radar", level=0.35)
    geometry.extend(
        primitive
        for primitive in tank
        if not primitive.role.endswith(
            ("::top_nozzle", "::top_flange")
        )
    )
    geometry.extend(
        place_asset(
            "pump",
            "radar_inlet_pump",
            (-4.15, 0.0, 0.0),
            scale=0.82,
        )
    )
    geometry.extend(_process_piping())
    geometry.extend(
        place_asset(
            "radarLevelSensor",
            "radar_transmitter",
            (0.0, 4.08, 0.0),
            scale=0.80,
        )
    )
    liquid_surface_y = 0.50 * 1.18 + 2.65 * 1.18 * 0.35
    geometry.extend(
        _radar_measurement_cone(
            liquid_surface_y=liquid_surface_y,
            antenna_y=4.80,
        )
    )
    geometry.extend(
        place_asset(
            "switch",
            "radar_pump_station",
            (-3.50, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        place_asset(
            "switch",
            "radar_drain_station",
            (-2.45, 0.0, 2.45),
            scale=0.70,
        )
    )
    geometry.extend(
        _with_indicator_state(
            place_asset(
                "indicator",
                "radar_stacklight",
                (3.40, 0.0, -2.05),
                scale=0.86,
            ),
            active="amber",
        )
    )
    return tuple(geometry)


def _build_equipment_gallery() -> tuple[Primitive3D, ...]:
    """Build the isolated reusable-equipment review gallery.

    Gallery placement is intentionally independent from production scenes so
    each asset can be inspected and corrected without changing machine-cell
    topology.  The asset factory remains the single source for geometry.
    """

    entries = (
        ("motor", "gallery_motor", (-5.5, 0.0, -3.7), 1.0),
        ("conveyor", "gallery_conveyor", (1.7, 0.0, -3.7), 0.72),
        ("box", "gallery_box", (5.3, 0.0, -3.7), 1.0),
        ("photoeye", "gallery_photoeye", (-5.2, 0.0, -0.3), 1.0),
        ("switch", "gallery_switch", (-2.7, 0.0, -0.3), 1.0),
        ("switch", "gallery_estop", (-0.8, 0.0, -0.3), 1.0),
        ("indicator", "gallery_indicator", (1.2, 0.0, -0.3), 1.0),
        ("pump", "gallery_pump", (4.7, 0.0, -0.3), 1.0),
        ("tank", "gallery_tank", (-3.8, 0.0, 4.0), 0.72),
        ("levelSensor", "gallery_low_sensor", (-1.9, 0.65, 4.0), 0.9),
        ("levelSensor", "gallery_transmitter", (0.2, 0.65, 4.0), 0.9),
        ("pipe", "gallery_pipe", (1.9, 0.9, 4.0), 1.0),
        ("fan", "gallery_fan", (5.15, 0.0, 3.65), 1.0, -18.0),
        ("rotarySwitch", "gallery_selector", (-6.0, 0.0, 7.2), 1.0),
        ("liftTable", "gallery_lift", (-2.7, 0.0, 7.2), 0.72),
        ("valve", "gallery_valve", (0.6, 0.0, 7.2), 1.0),
        ("drillPress", "gallery_drill", (3.6, 0.0, 7.2), 0.75),
        ("robotArm", "gallery_robot", (7.0, 0.0, 7.2), 0.8),
        ("rollerShutter", "gallery_shutter", (-4.7, 0.0, 12.2), 0.72),
        ("rotaryTable", "gallery_turntable", (0.0, 0.0, 12.2), 1.0),
        ("machine", "gallery_machine", (4.5, 0.0, 12.2), 0.8),
    )
    geometry: list[Primitive3D] = []
    for entry in entries:
        asset_type, instance_id, position, scale, *rotation = entry
        geometry.extend(
            place_asset(
                asset_type,
                instance_id,
                position,
                scale=scale,
                yaw_degrees=rotation[0] if rotation else 0.0,
            )
        )
    return tuple(geometry)


NATIVE_SCENE_DEFINITIONS = (
    NativeSceneDefinition(
        approval_id="S03",
        scene_id="conveyor-cell",
        label="Conveyor Inspection Cell",
        description=(
            "Three cartons circulate through an opposed through-beam "
            "inspection photoeye on an end-driven roller conveyor."
        ),
        source_file=SOURCE_SCENE_ROOT / "conveyor-cell.json",
        setup_file=(
            SETUP_DOCUMENT_ROOT / "S03_CONVEYOR_INSPECTION_CELL_SETUP.md"
        ),
        builder=_build_conveyor_inspection_cell,
        view_span=10.2,
    ),
    NativeSceneDefinition(
        approval_id="S04",
        scene_id="tank-level",
        label="Tank Level / 4-20 mA",
        description=(
            "Pump-fed process tank with discrete low/high switches, an "
            "analog level transmitter, connected piping, and visible level."
        ),
        source_file=SOURCE_SCENE_ROOT / "tank-level.json",
        setup_file=(
            SETUP_DOCUMENT_ROOT / "S04_TANK_LEVEL_4_20MA_SETUP.md"
        ),
        builder=_build_analog_tank_scene,
        view_span=10.5,
    ),
    NativeSceneDefinition(
        approval_id="S05",
        scene_id="tank-high-low",
        label="Water Tank - High/Low Switches",
        description=(
            "Discrete level-control tank with separate low and high point "
            "switches, a connected inlet pump, and drain piping."
        ),
        source_file=SOURCE_SCENE_ROOT / "tank-high-low.json",
        setup_file=(
            SETUP_DOCUMENT_ROOT / "S05_WATER_TANK_HIGH_LOW_SETUP.md"
        ),
        builder=_build_high_low_tank_scene,
        view_span=10.5,
    ),
    NativeSceneDefinition(
        approval_id="S06",
        scene_id="tank-radar",
        label="Water Tank - Radar Level",
        description=(
            "Pump-fed water tank with a top-mounted non-contact radar "
            "transmitter and measurement cone terminating at the liquid."
        ),
        source_file=SOURCE_SCENE_ROOT / "tank-radar.json",
        setup_file=(
            SETUP_DOCUMENT_ROOT / "S06_WATER_TANK_RADAR_SETUP.md"
        ),
        builder=_build_radar_tank_scene,
        view_span=10.8,
    ),
)

EQUIPMENT_GALLERY_DEFINITION = NativeSceneDefinition(
    approval_id="GALLERY",
    scene_id="equipment-gallery",
    label="Reusable Equipment Gallery",
    description=(
        "Inspect reusable equipment assets one at a time before placing them "
        "into a production scene. Geometry corrections belong here first."
    ),
    source_file=SOURCE_SCENE_ROOT / "equipment-gallery.json",
    setup_file=SETUP_DOCUMENT_ROOT / "EQUIPMENT_GALLERY_REVIEW.md",
    builder=_build_equipment_gallery,
    view_span=20.5,
)

NATIVE_SCENE_BY_ID = {
    definition.scene_id: definition
    for definition in NATIVE_SCENE_DEFINITIONS
}


def build_native_scene_geometry(scene_id: str) -> tuple[Primitive3D, ...]:
    if scene_id == EQUIPMENT_GALLERY_DEFINITION.scene_id:
        return EQUIPMENT_GALLERY_DEFINITION.builder()
    try:
        definition = NATIVE_SCENE_BY_ID[scene_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported native review scene: {scene_id}") from exc
    return definition.builder()
