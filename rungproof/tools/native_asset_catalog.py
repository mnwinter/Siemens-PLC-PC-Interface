"""Symbolic control contracts for the reusable native asset portfolio.

This module describes what a plant runtime may command or report for an asset.
It intentionally contains no Siemens addresses, DB offsets, or transport code.
Those belong to the guarded scene/profile adapter, never to an asset model.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.native_asset_library import ASSET_BY_TYPE, ASSET_DEFINITIONS


@dataclass(frozen=True, slots=True)
class AssetPoint:
    name: str
    type: str
    direction: str
    unit: str = ""


@dataclass(frozen=True, slots=True)
class AssetControlContract:
    asset_type: str
    commands: tuple[AssetPoint, ...]
    feedback: tuple[AssetPoint, ...]
    interlocks: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AssetCatalogItem:
    """Searchable catalog metadata independent of any one UI."""

    approval_id: str
    asset_type: str
    label: str
    category: str
    tags: tuple[str, ...]
    reference_name: str
    reference_url: str
    view_span: float


def _bool(name: str, direction: str) -> AssetPoint:
    return AssetPoint(name, "BOOL", direction)


def _real(name: str, direction: str, unit: str = "") -> AssetPoint:
    return AssetPoint(name, "REAL", direction, unit)


def _int(name: str, direction: str) -> AssetPoint:
    return AssetPoint(name, "INT", direction)


def _points(value: AssetPoint | tuple[AssetPoint, ...]) -> tuple[AssetPoint, ...]:
    """Accept one point or a tuple so compact catalog rows stay readable."""

    if isinstance(value, AssetPoint):
        return (value,)
    return tuple(value)


def _contract(asset_type: str, commands: AssetPoint | tuple[AssetPoint, ...], feedback: AssetPoint | tuple[AssetPoint, ...], *interlocks: str) -> AssetControlContract:
    return AssetControlContract(asset_type, _points(commands), _points(feedback), interlocks)


ASSET_CONTROL_CONTRACTS: tuple[AssetControlContract, ...] = (
    _contract("motor", (_bool("run", "PLC -> plant"),), (_bool("running", "plant -> PLC"), _real("speed", "plant -> PLC", "rpm"), _bool("fault", "plant -> PLC")), "overload_reset"),
    _contract("conveyor", (_bool("run", "PLC -> plant"), _real("speed_setpoint", "PLC -> plant", "m/s")), (_bool("running", "plant -> PLC"), _bool("photoeye_blocked", "plant -> PLC"), _real("material_position", "plant -> PLC", "m")), "guard_closed", "estop_reset"),
    _contract("box", (), (_bool("present", "plant -> PLC"), _real("position", "plant -> PLC", "m"))),
    _contract("photoeye", (), (_bool("blocked", "plant -> PLC"), _bool("healthy", "plant -> PLC"))),
    _contract("switch", (_bool("pressed", "PLC -> plant"),), (_bool("active", "plant -> PLC"))),
    _contract("indicator", (_bool("red", "PLC -> plant"), _bool("amber", "PLC -> plant"), _bool("green", "PLC -> plant")), ()),
    _contract("pump", (_bool("run", "PLC -> plant"),), (_bool("running", "plant -> PLC"), _real("flow", "plant -> PLC", "L/min"), _bool("fault", "plant -> PLC")), "suction_available", "discharge_open"),
    _contract("fan", (_bool("run", "PLC -> plant"),), (_bool("running", "plant -> PLC"), _real("speed", "plant -> PLC", "rpm"), _bool("fault", "plant -> PLC")), "guard_closed"),
    _contract("pusher", (_bool("extend", "PLC -> plant"),), (_bool("extended", "plant -> PLC"), _bool("retracted", "plant -> PLC")), "air_available"),
    _contract("tank", (), (_real("level", "plant -> PLC", "%"), _real("volume", "plant -> PLC", "L"))),
    _contract("levelSensor", (), (_bool("level_reached", "plant -> PLC"),)),
    _contract("radarLevelSensor", (), (_real("level", "plant -> PLC", "%"), _real("distance", "plant -> PLC", "m"), _real("signal", "plant -> PLC", "mA"), _bool("echo_ok", "plant -> PLC"))),
    _contract("pipe", (_bool("flow_enabled", "PLC -> plant"),), (_real("flow", "plant -> PLC", "L/min"), _bool("blocked", "plant -> PLC"))),
    _contract("rotarySwitch", (_int("position_setpoint", "PLC -> plant"),), (_int("position", "plant -> PLC"),)),
    _contract("liftTable", (_bool("raise", "PLC -> plant"), _bool("lower", "PLC -> plant")), (_real("position", "plant -> PLC", "%"), _bool("top_limit", "plant -> PLC"), _bool("bottom_limit", "plant -> PLC")), "safe_to_move"),
    _contract("valve", (_real("position_setpoint", "PLC -> plant", "%"),), (_real("position", "plant -> PLC", "%"), _bool("open_limit", "plant -> PLC"), _bool("closed_limit", "plant -> PLC"))),
    _contract("drillPress", (_bool("run", "PLC -> plant"), _bool("feed", "PLC -> plant")), (_bool("running", "plant -> PLC"), _real("quill_position", "plant -> PLC", "%")), "guard_closed", "part_present"),
    _contract("robotArm", (_bool("run", "PLC -> plant"), _int("program", "PLC -> plant")), (_bool("running", "plant -> PLC"), _bool("at_home", "plant -> PLC"), _bool("fault", "plant -> PLC")), "guard_closed", "servo_ready"),
    _contract("rollerShutter", (_bool("open", "PLC -> plant"), _bool("close", "PLC -> plant")), (_real("position", "plant -> PLC", "%"), _bool("open_limit", "plant -> PLC"), _bool("closed_limit", "plant -> PLC")), "safety_edge_clear"),
    _contract("rotaryTable", (_bool("index", "PLC -> plant"),), (_int("index_position", "plant -> PLC"), _bool("in_position", "plant -> PLC")), "guard_closed"),
    _contract("machine", (_bool("run", "PLC -> plant"), _bool("reset", "PLC -> plant")), (_bool("running", "plant -> PLC"), _bool("door_closed", "plant -> PLC"), _bool("fault", "plant -> PLC")), "door_closed", "estop_reset"),
    _contract("gearedMotor", (_bool("run", "PLC -> plant"), _real("speed_setpoint", "PLC -> plant", "rpm")), (_bool("running", "plant -> PLC"), _real("output_speed", "plant -> PLC", "rpm"), _bool("fault", "plant -> PLC")), "overload_reset"),
    _contract("beltConveyor", (_bool("run", "PLC -> plant"), _real("speed_setpoint", "PLC -> plant", "m/s")), (_bool("running", "plant -> PLC"), _real("belt_speed", "plant -> PLC", "m/s"), _bool("fault", "plant -> PLC")), "guard_closed", "estop_reset"),
    _contract("palletConveyor", (_bool("run", "PLC -> plant"),), (_bool("running", "plant -> PLC"), _bool("pallet_present", "plant -> PLC"), _bool("jammed", "plant -> PLC")), "downstream_clear", "estop_reset"),
    _contract("pneumaticCylinder", (_bool("extend", "PLC -> plant"), _bool("retract", "PLC -> plant")), (_real("position", "plant -> PLC", "%"), _bool("extended", "plant -> PLC"), _bool("retracted", "plant -> PLC")), "air_available"),
    _contract("parallelGripper", (_bool("close", "PLC -> plant"),), (_bool("open", "plant -> PLC"), _bool("closed", "plant -> PLC"), _bool("part_gripped", "plant -> PLC")), "air_available"),
    _contract("pallet", (), (_bool("present", "plant -> PLC"), _real("load_mass", "plant -> PLC", "kg"))),
    _contract("tote", (), (_bool("present", "plant -> PLC"), _bool("full", "plant -> PLC"))),
    _contract("hopper", (_real("gate_setpoint", "PLC -> plant", "%"), _bool("vibrator_run", "PLC -> plant")), (_real("level", "plant -> PLC", "%"), _real("gate_position", "plant -> PLC", "%"), _bool("bridged", "plant -> PLC")), "downstream_available"),
    _contract("silo", (_bool("discharge_enable", "PLC -> plant"),), (_real("level", "plant -> PLC", "%"), _real("mass", "plant -> PLC", "kg"), _bool("high_level", "plant -> PLC")), "downstream_available"),
    _contract("safetyFence", (), (_bool("installed", "plant -> PLC"),)),
    _contract("safetyGate", (_bool("unlock", "PLC -> plant"),), (_bool("closed", "plant -> PLC"), _bool("locked", "plant -> PLC")), "safe_to_unlock"),
    _contract("lightCurtain", (), (_bool("clear", "plant -> PLC"), _bool("ossd_1", "plant -> PLC"), _bool("ossd_2", "plant -> PLC"))),
    _contract("proximitySensor", (), (_bool("detected", "plant -> PLC"), _bool("healthy", "plant -> PLC"))),
    _contract("controlPanel", (_bool("start", "PLC -> plant"), _bool("stop", "PLC -> plant"), _bool("reset", "PLC -> plant")), (_bool("power_on", "plant -> PLC"), _bool("door_closed", "plant -> PLC"))),
    _contract("vfdCabinet", (_bool("run_enable", "PLC -> plant"), _real("speed_reference", "PLC -> plant", "Hz"), _bool("fault_reset", "PLC -> plant")), (_bool("running", "plant -> PLC"), _real("output_frequency", "plant -> PLC", "Hz"), _real("motor_current", "plant -> PLC", "A"), _bool("fault", "plant -> PLC")), "drive_ready", "motor_available"),
    _contract("airCompressor", (_bool("run", "PLC -> plant"), _real("pressure_setpoint", "PLC -> plant", "bar")), (_bool("running", "plant -> PLC"), _real("discharge_pressure", "plant -> PLC", "bar"), _real("temperature", "plant -> PLC", "degC"), _bool("fault", "plant -> PLC")), "oil_level_ok"),
    _contract("airReceiver", (_bool("drain", "PLC -> plant"),), (_real("pressure", "plant -> PLC", "bar"), _bool("high_pressure", "plant -> PLC"))),
    _contract("airDryer", (_bool("run", "PLC -> plant"),), (_bool("running", "plant -> PLC"), _real("dew_point", "plant -> PLC", "degC"), _bool("left_tower_active", "plant -> PLC"), _bool("fault", "plant -> PLC"))),
    _contract("hydraulicPowerUnit", (_bool("run", "PLC -> plant"), _bool("unload", "PLC -> plant")), (_bool("running", "plant -> PLC"), _real("pressure", "plant -> PLC", "bar"), _real("oil_temperature", "plant -> PLC", "degC"), _bool("fault", "plant -> PLC")), "oil_level_ok"),
    _contract("heatExchanger", (_real("hot_flow_setpoint", "PLC -> plant", "%"), _real("cold_flow_setpoint", "PLC -> plant", "%")), (_real("hot_outlet_temperature", "plant -> PLC", "degC"), _real("cold_outlet_temperature", "plant -> PLC", "degC"), _real("differential_pressure", "plant -> PLC", "bar"))),
    _contract("mixerAgitator", (_bool("run", "PLC -> plant"), _real("speed_setpoint", "PLC -> plant", "rpm")), (_bool("running", "plant -> PLC"), _real("speed", "plant -> PLC", "rpm"), _bool("fault", "plant -> PLC")), "minimum_level", "access_closed"),
    _contract("weighScale", (_bool("tare", "PLC -> plant"),), (_real("weight", "plant -> PLC", "kg"), _bool("stable", "plant -> PLC"), _bool("overload", "plant -> PLC"))),
    _contract("barcodeScanner", (_bool("trigger", "PLC -> plant"),), (_bool("good_read", "plant -> PLC"), _bool("no_read", "plant -> PLC"), _int("code_index", "plant -> PLC"))),
    _contract("visionCamera", (_bool("trigger", "PLC -> plant"), _int("job", "PLC -> plant")), (_bool("pass", "plant -> PLC"), _bool("fail", "plant -> PLC"), _bool("busy", "plant -> PLC"))),
    _contract("rollerTransfer", (_bool("raise", "PLC -> plant"), _bool("transfer_run", "PLC -> plant")), (_bool("raised", "plant -> PLC"), _bool("lowered", "plant -> PLC"), _bool("load_present", "plant -> PLC")), "downstream_clear"),
    _contract("conveyorTurntable", (_int("target_index", "PLC -> plant"), _bool("run_rollers", "PLC -> plant")), (_int("index_position", "plant -> PLC"), _bool("in_position", "plant -> PLC"), _bool("load_present", "plant -> PLC")), "rotation_clear"),
    _contract("verticalLift", (_real("position_setpoint", "PLC -> plant", "%"), _bool("conveyor_run", "PLC -> plant")), (_real("position", "plant -> PLC", "%"), _bool("top_limit", "plant -> PLC"), _bool("bottom_limit", "plant -> PLC"), _bool("load_present", "plant -> PLC")), "gates_closed", "overtravel_clear"),
    _contract("diverterArm", (_bool("divert", "PLC -> plant"),), (_bool("extended", "plant -> PLC"), _bool("retracted", "plant -> PLC")), "air_available", "destination_clear"),
    _contract("amr", (_bool("mission_start", "PLC -> plant"), _int("destination", "PLC -> plant")), (_bool("moving", "plant -> PLC"), _bool("at_destination", "plant -> PLC"), _real("battery", "plant -> PLC", "%"), _bool("safety_stop", "plant -> PLC")), "path_clear", "mission_valid"),
)

ASSET_CONTROL_BY_TYPE = {item.asset_type: item for item in ASSET_CONTROL_CONTRACTS}


_LEGACY_CATEGORIES = {
    "motor": "drives",
    "conveyor": "material-handling",
    "box": "loads",
    "photoeye": "sensors",
    "switch": "operator-controls",
    "indicator": "operator-controls",
    "pump": "process",
    "fan": "process",
    "pusher": "pneumatics",
    "tank": "process",
    "levelSensor": "sensors",
    "radarLevelSensor": "sensors",
    "pipe": "process",
    "rotarySwitch": "operator-controls",
    "liftTable": "material-handling",
    "valve": "process",
    "drillPress": "machines",
    "robotArm": "robotics",
    "rollerShutter": "access",
    "rotaryTable": "material-handling",
    "machine": "machines",
}


CATALOG_ITEMS: tuple[AssetCatalogItem, ...] = tuple(
    AssetCatalogItem(
        approval_id=definition.approval_id,
        asset_type=definition.asset_type,
        label=definition.label,
        category=(
            definition.category
            if definition.category != "general"
            else _LEGACY_CATEGORIES[definition.asset_type]
        ),
        tags=definition.tags or tuple(
            token.lower()
            for token in definition.label.replace("-", " ").split()
        ),
        reference_name=definition.reference_name,
        reference_url=definition.reference_url,
        view_span=definition.view_span,
    )
    for definition in ASSET_DEFINITIONS
)

CATALOG_ITEM_BY_TYPE = {item.asset_type: item for item in CATALOG_ITEMS}


def search_asset_catalog(query: str = "", *, category: str | None = None) -> tuple[AssetCatalogItem, ...]:
    """Return deterministic catalog matches for palettes and scene editors."""

    needle = query.strip().casefold()
    matches: list[AssetCatalogItem] = []
    for item in CATALOG_ITEMS:
        if category is not None and item.category != category:
            continue
        searchable = " ".join((item.asset_type, item.label, item.category, *item.tags)).casefold()
        if needle and needle not in searchable:
            continue
        matches.append(item)
    return tuple(matches)


def validate_asset_control_catalog() -> None:
    """Fail fast if a renderable asset has no typed control contract."""

    asset_types = set(ASSET_BY_TYPE)
    contract_types = set(ASSET_CONTROL_BY_TYPE)
    if asset_types != contract_types:
        missing = sorted(asset_types - contract_types)
        unknown = sorted(contract_types - asset_types)
        raise ValueError(f"asset control catalog mismatch; missing={missing}, unknown={unknown}")
    for contract in ASSET_CONTROL_CONTRACTS:
        for point in (*contract.commands, *contract.feedback):
            if point.direction not in {"PLC -> plant", "plant -> PLC"}:
                raise ValueError(f"invalid symbolic direction for {contract.asset_type}.{point.name}")
            name_tokens = set(point.name.lower().replace("-", "_").split("_"))
            if (
                "%i" in point.name.lower()
                or "%q" in point.name.lower()
                or name_tokens & {"db", "offset", "ip", "address"}
            ):
                raise ValueError(f"physical PLC detail leaked into asset point {point.name}")
    if len(CATALOG_ITEMS) != len(ASSET_DEFINITIONS):
        raise ValueError("asset catalog contains duplicate asset types")
    if set(CATALOG_ITEM_BY_TYPE) != asset_types:
        raise ValueError("asset search metadata does not cover every renderable asset")
    expected_approval_ids = [f"A{index:02d}" for index in range(1, len(ASSET_DEFINITIONS) + 1)]
    actual_approval_ids = [item.approval_id for item in CATALOG_ITEMS]
    if actual_approval_ids != expected_approval_ids:
        raise ValueError("asset approval IDs must be sequential and deterministic")


validate_asset_control_catalog()
