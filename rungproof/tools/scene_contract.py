"""Versioned server-side validation for persisted RungProof scene files.

JSON Schema owns the cross-language document envelope and allocation bounds.
These semantic checks add references and point typing that JSON Schema cannot
express portably. Browser/server parity fixtures exercise both adapters.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


class SceneContractError(ValueError):
    """A scene is unsafe or cannot be executed by the current runtime."""


CONFIG_KEYS_BY_TYPE: dict[str, frozenset[str]] = {
    "motor": frozenset(("length", "diameter", "color", "running")),
    "conveyor": frozenset(
        ("length", "width", "deckHeight", "beltColor", "running")
    ),
    "box": frozenset(("size", "color")),
    "photoeye": frozenset(("span", "height", "beamCenterHeightM", "blocked")),
    "switch": frozenset(("style", "color", "active", "action")),
    "indicator": frozenset(("colors", "active")),
    "pump": frozenset(("color", "running")),
    "fan": frozenset(
        ("diameter", "centerHeight", "bladeCount", "bladeColor", "running")
    ),
    "pusher": frozenset(("stroke", "centerHeight", "initialPosition", "travelAxis")),
    "tank": frozenset(("height", "diameter", "initialLevel", "fluidColor")),
    "levelSensor": frozenset(
        (
            "sensorType",
            "threshold",
            "mode",
            "range",
            "engineeringRange",
            "active",
        )
    ),
    "radarLevelSensor": frozenset(
        (
            "initialLevel",
            "mountSpan",
            "beamRadius",
            "range",
            "engineeringRange",
            "measurement",
        )
    ),
    "pipe": frozenset(
        ("length", "diameter", "axis", "color", "showSupport", "supportHeight")
    ),
    "rotarySwitch": frozenset(
        (
            "positionCount",
            "initialPosition",
            "minimumAngleDeg",
            "maximumAngleDeg",
            "action",
        )
    ),
    "liftTable": frozenset(
        ("width", "depth", "minimumHeight", "travel", "initialPosition")
    ),
    "valve": frozenset(("initialPosition",)),
    "drillPress": frozenset(
        ("travel", "initialPosition", "running", "color")
    ),
    "robotArm": frozenset(("initialPosition", "running")),
    "rollerShutter": frozenset(("width", "height", "initialPosition")),
    "rotaryTable": frozenset(("radius", "angleRangeDeg", "initialPosition")),
    "machine": frozenset(("size", "color", "running")),
    "palletLoad": frozenset(("caseWidthM", "caseHeightM", "caseDepthM", "layers", "color")),
    "containerReceiver": frozenset(("size", "color", "running")),
    "toteFiller": frozenset(("initialPosition",)),
    "toteCapper": frozenset(("size", "color", "running")),
    "toteLabeler": frozenset(("size", "color", "running")),
    "toteVision": frozenset(("size", "color", "running")),
    "meteringSkid": frozenset(("size", "color", "running")),
    "sizeSensorBank": frozenset(("span", "beamHeightsM", "blocked")),
}

EQUIPMENT_REFERENCES: dict[str, dict[str, tuple[str, ...]]] = {
    "conveyor": {
        "conveyorId": ("conveyor",),
        "photoeyeId": ("photoeye",),
        "indicatorId": ("indicator",),
        "productIds": ("box",),
    },
    "conveyorStop": {
        "conveyorId": ("conveyor",),
        "photoeyeId": ("photoeye",),
        "productId": ("box",),
        "indicatorId": ("indicator",),
    },
    "conveyorPusher": {
        "conveyorId": ("conveyor",),
        "photoeyeId": ("photoeye",),
        "productId": ("box",),
        "pusherId": ("pusher",),
        "indicatorId": ("indicator",),
    },
    "tank": {
        "tankId": ("tank",),
        "pumpId": ("pump",),
        "lowSensorId": ("levelSensor",),
        "highSensorId": ("levelSensor",),
        "transmitterId": ("levelSensor", "radarLevelSensor"),
        "indicatorId": ("indicator",),
    },
}

OPTIONAL_REFERENCES = {"lowSensorId", "highSensorId", "transmitterId"}
ACTION_TYPES = {
    "toggle",
    "set",
    "pulse",
    "cycle",
    "start",
    "run",
    "stop",
    "reset",
    "togglePoint",
}
BINDING_MODES = {
    "switch",
    "indicator",
    "selector",
    "running",
    "photoeye",
    "position",
    "levelSensor",
}


def _path(error: Any) -> str:
    parts = [str(part) for part in error.absolute_path]
    return ".".join(parts) if parts else "scene"


def _mapping(value: object, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SceneContractError(f"{path} must be an object.")
    return value


def _sequence(value: object, path: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise SceneContractError(f"{path} must be an array.")
    return value


def _point_value(point: Mapping[str, Any], value: object, path: str) -> None:
    point_type = point["type"]
    valid = (
        (point_type == "BOOL" and type(value) is bool)
        or (
            point_type == "DINT"
            and isinstance(value, int)
            and not isinstance(value, bool)
        )
        or (
            point_type == "REAL"
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
        )
        or (point_type == "STRING" and isinstance(value, str))
    )
    if not valid:
        raise SceneContractError(
            f"{path} has the wrong value type for {point['name']} "
            f"({point_type})."
        )


def _point_map(
    value: object,
    points: Mapping[str, Mapping[str, Any]],
    path: str,
) -> None:
    for name, point_value in _mapping(value, path).items():
        point = points.get(name)
        if point is None:
            raise SceneContractError(f'{path} references unknown point "{name}".')
        _point_value(point, point_value, f"{path}.{name}")


def _validate_training_contract(document: Mapping[str, Any]) -> None:
    training = document.get("training")
    if training is None:
        return
    guide = _mapping(training, "scene.training")
    machine = _mapping(guide.get("machineGuide"), "scene.training.machineGuide")
    purpose = machine.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        raise SceneContractError(
            "scene.training.machineGuide.purpose must be non-empty."
        )
    for field in (
        "startConditions",
        "normalSequence",
        "stopBehavior",
        "faultBehavior",
        "expectedObservations",
    ):
        values = _sequence(
            machine.get(field),
            f"scene.training.machineGuide.{field}",
        )
        if not values or any(not isinstance(value, str) or not value.strip() for value in values):
            raise SceneContractError(
                f"scene.training.machineGuide.{field} must contain text."
            )
    sequence_number = guide.get("sequenceNumber")
    if sequence_number is not None and (
        type(sequence_number) is not int or not 1 <= sequence_number <= 999
    ):
        raise SceneContractError(
            "scene.training.sequenceNumber must be a positive integer."
        )
    for field in ("retainedTags", "addedTags", "previousAcceptance"):
        values = guide.get(field, [])
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise SceneContractError(f"scene.training.{field} must contain names.")
    changed = guide.get("changedTags", [])
    if not isinstance(changed, list):
        raise SceneContractError("scene.training.changedTags must be an array.")
    for index, item in enumerate(changed):
        changed_item = _mapping(item, f"scene.training.changedTags[{index}]")
        if not isinstance(changed_item.get("name"), str) or not isinstance(
            changed_item.get("reason"), str
        ):
            raise SceneContractError(
                f"scene.training.changedTags[{index}] requires name and reason."
            )


def _equipment_reference(
    equipment: Mapping[str, Mapping[str, Any]],
    reference: object,
    expected_types: tuple[str, ...],
    path: str,
    *,
    optional: bool = False,
) -> None:
    if reference is None and optional:
        return
    if not isinstance(reference, str):
        raise SceneContractError(f"{path} must be an equipment id.")
    candidate = equipment.get(reference)
    if candidate is None:
        raise SceneContractError(
            f'{path} references missing equipment "{reference}".'
        )
    if candidate["type"] not in expected_types:
        raise SceneContractError(
            f"{path} must reference {' or '.join(expected_types)}, "
            f'not "{candidate["type"]}".'
        )


def _validate_semantics(document: Mapping[str, Any]) -> None:
    equipment_items = _sequence(document["equipment"], "scene.equipment")
    equipment: dict[str, Mapping[str, Any]] = {}
    complexity = 0
    for index, raw_item in enumerate(equipment_items):
        item = _mapping(raw_item, f"scene.equipment[{index}]")
        item_id = item["id"]
        if item_id in equipment:
            raise SceneContractError(f'Duplicate equipment id "{item_id}".')
        equipment[item_id] = item
        item_type = item["type"]
        config = _mapping(item.get("config", {}), f"equipment[{index}].config")
        unsupported = set(config) - CONFIG_KEYS_BY_TYPE[item_type]
        if unsupported:
            key = sorted(unsupported)[0]
            raise SceneContractError(
                f'equipment[{index}].config.{key} is not supported for "{item_type}".'
            )
        if (
            "initialPosition" in config
            and item_type != "rotarySwitch"
            and config["initialPosition"] > 1
        ):
            raise SceneContractError(
                f"equipment[{index}].config.initialPosition must be 0 to 1."
            )
        if item_type == "conveyor":
            complexity += 12 + int((config.get("length", 7) / 0.55) + 0.999) * 2
        elif item_type == "fan":
            complexity += 12 + config.get("bladeCount", 6) * 2
        elif item_type == "rollerShutter":
            complexity += 12 + max(8, round(config.get("height", 3) / 0.22))
        else:
            complexity += 24
    if complexity > 4_000:
        raise SceneContractError(
            f"Scene geometry complexity {complexity} exceeds 4000."
        )

    simulation = _mapping(document["simulation"], "scene.simulation")
    point_items = simulation.get("points", [])
    points: dict[str, Mapping[str, Any]] = {}
    for index, raw_point in enumerate(point_items):
        point = _mapping(raw_point, f"scene.simulation.points[{index}]")
        name = point["name"]
        if name in points:
            raise SceneContractError(f'Duplicate simulation point "{name}".')
        points[name] = point
        _point_value(point, point["initial"], f"point {name}.initial")
        if "safe" in point:
            _point_value(point, point["safe"], f"point {name}.safe")

    simulation_type = simulation["type"]
    if simulation_type != "static" and not points:
        raise SceneContractError(
            f'scene.simulation.points must declare points for "{simulation_type}".'
        )
    _validate_training_contract(document)

    for property_name, expected_types in EQUIPMENT_REFERENCES.get(
        simulation_type, {}
    ).items():
        reference = simulation.get(property_name)
        if property_name == "productIds":
            references = _sequence(
                reference, f"scene.simulation.{property_name}"
            )
            if not references:
                raise SceneContractError(
                    f"scene.simulation.{property_name} cannot be empty."
                )
            for index, item_id in enumerate(references):
                _equipment_reference(
                    equipment,
                    item_id,
                    expected_types,
                    f"scene.simulation.{property_name}[{index}]",
                )
        else:
            _equipment_reference(
                equipment,
                reference,
                expected_types,
                f"scene.simulation.{property_name}",
                optional=property_name in OPTIONAL_REFERENCES,
            )

    sequences = _mapping(
        simulation.get("sequences", {}),
        "scene.simulation.sequences",
    )
    if simulation_type == "sequence":
        if not sequences:
            raise SceneContractError(
                "scene.simulation.sequences must not be empty."
            )
        default_sequence = simulation.get("defaultSequence")
        if default_sequence is not None and default_sequence not in sequences:
            raise SceneContractError(
                "scene.simulation.defaultSequence is not defined."
            )
        for sequence_name, raw_states in sequences.items():
            states = _sequence(
                raw_states,
                f"scene.simulation.sequences.{sequence_name}",
            )
            if not 1 <= len(states) <= 128:
                raise SceneContractError(
                    f'Sequence "{sequence_name}" must contain 1-128 states.'
                )
            for state_index, raw_state in enumerate(states):
                state_path = (
                    f"scene.simulation.sequences.{sequence_name}"
                    f"[{state_index}]"
                )
                state = _mapping(raw_state, state_path)
                _point_map(state.get("set", {}), points, f"{state_path}.set")
                duration = state.get("durationS")
                if (
                    not isinstance(duration, (int, float))
                    or isinstance(duration, bool)
                    or not 0 <= duration <= 3_600
                ):
                    raise SceneContractError(
                        f"{state_path}.durationS must be 0 to 3600."
                    )
                for motion_index, raw_motion in enumerate(
                    state.get("motions", [])
                ):
                    motion_path = f"{state_path}.motions[{motion_index}]"
                    motion = _mapping(raw_motion, motion_path)
                    _equipment_reference(
                        equipment,
                        motion.get("equipmentId"),
                        tuple(
                            item["type"]
                            for item in equipment.values()
                        ),
                        f"{motion_path}.equipmentId",
                    )
                    if motion.get("type") not in {
                        "translate",
                        "position",
                        "tankLevel",
                    }:
                        raise SceneContractError(
                            f"{motion_path}.type is unsupported."
                        )
                    if (
                        motion.get("type") == "translate"
                        and motion.get("axis") not in {"x", "y", "z"}
                    ):
                        raise SceneContractError(
                            f"{motion_path}.axis must be x, y, or z."
                        )
                    for property_name in ("from", "to"):
                        number = motion.get(property_name)
                        if (
                            not isinstance(number, (int, float))
                            or isinstance(number, bool)
                            or abs(number) > 10_000
                        ):
                            raise SceneContractError(
                                f"{motion_path}.{property_name} must be bounded."
                            )
        _point_map(
            simulation.get("safeState", {}),
            points,
            "scene.simulation.safeState",
        )
        _point_map(
            simulation.get("completionState", {}),
            points,
            "scene.simulation.completionState",
        )

    action_ids: set[str] = set()
    for index, raw_action in enumerate(simulation.get("actions", [])):
        path = f"scene.simulation.actions[{index}]"
        action = _mapping(raw_action, path)
        action_id = action.get("id")
        if action_id in action_ids:
            raise SceneContractError(f'Duplicate simulation action "{action_id}".')
        action_ids.add(action_id)
        if action.get("type") not in ACTION_TYPES:
            raise SceneContractError(f"{path}.type is unsupported.")
        point_name = action.get("point")
        if point_name is not None:
            point = points.get(point_name)
            if point is None:
                raise SceneContractError(
                    f'{path}.point references unknown point "{point_name}".'
                )
            if "value" in action:
                _point_value(point, action["value"], f"{path}.value")
            for value_index, item in enumerate(action.get("values", [])):
                _point_value(
                    point,
                    item,
                    f"{path}.values[{value_index}]",
                )
        if "requires" in action:
            _point_map(action["requires"], points, f"{path}.requires")
        if (
            "sequence" in action
            and action["sequence"] not in sequences
        ):
            raise SceneContractError(
                f'{path}.sequence references unknown sequence "{action["sequence"]}".'
            )

    for index, raw_binding in enumerate(simulation.get("pointBindings", [])):
        path = f"scene.simulation.pointBindings[{index}]"
        binding = _mapping(raw_binding, path)
        if binding.get("point") not in points:
            raise SceneContractError(f"{path}.point is unknown.")
        if binding.get("equipmentId") not in equipment:
            raise SceneContractError(f"{path}.equipmentId is unknown.")
        if binding.get("mode") not in BINDING_MODES:
            raise SceneContractError(f"{path}.mode is unsupported.")

    for index, raw_rule in enumerate(simulation.get("rules", [])):
        path = f"scene.simulation.rules[{index}]"
        rule = _mapping(raw_rule, path)
        _point_map(rule.get("when", {}), points, f"{path}.when")
        _point_map(rule.get("set", {}), points, f"{path}.set")
    for index, raw_rule in enumerate(simulation.get("edgeRules", [])):
        path = f"scene.simulation.edgeRules[{index}]"
        rule = _mapping(raw_rule, path)
        rising = points.get(rule.get("rising"))
        if rising is None or rising["type"] != "BOOL":
            raise SceneContractError(f"{path}.rising must reference a BOOL point.")
        _point_map(rule.get("set", {}), points, f"{path}.set")
        for toggle_name in rule.get("toggle", []):
            point = points.get(toggle_name)
            if point is None or point["type"] != "BOOL":
                raise SceneContractError(
                    f"{path}.toggle must reference BOOL points."
                )

    for index, raw_alarm in enumerate(document.get("alarmRules", [])):
        alarm = _mapping(raw_alarm, f"scene.alarmRules[{index}]")
        point = points.get(alarm.get("point"))
        if point is None:
            raise SceneContractError(
                f"scene.alarmRules[{index}].point is unknown."
            )
        if "value" in alarm:
            _point_value(
                point,
                alarm["value"],
                f"scene.alarmRules[{index}].value",
            )


def validate_scene_document(
    document: object,
    schema_path: Path,
) -> Mapping[str, Any]:
    """Validate a scene for persistence and return the original mapping."""

    if not isinstance(document, Mapping):
        raise SceneContractError("Scene document must be an object.")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SceneContractError(f"Scene schema is unavailable: {exc}") from exc
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        raise SceneContractError(f"{_path(first)}: {first.message}")
    _validate_semantics(document)
    return document
