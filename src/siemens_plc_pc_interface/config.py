"""Load and validate the PLC interface JSON configuration."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from enum import Enum
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """A configuration value is missing, inconsistent, or unsafe."""


class Direction(str, Enum):
    """The only component allowed to write a configured PLC tag."""

    PC_TO_PLC = "pc_to_plc"
    PLC_TO_PC = "plc_to_pc"


class DataType(str, Enum):
    """PLC data types supported by the first configuration format."""

    BOOL = "BOOL"
    BYTE = "BYTE"
    WORD = "WORD"
    DWORD = "DWORD"
    INT = "INT"
    DINT = "DINT"
    REAL = "REAL"


@dataclass(frozen=True)
class ConnectionConfig:
    """S7 endpoint and timing settings."""

    cpu_family: str
    ip: str
    rack: int
    slot: int
    cycle_ms: int
    connect_timeout_ms: int


@dataclass(frozen=True)
class TagConfig:
    """One typed tag in the dedicated PLC simulation data block."""

    name: str
    plc_symbol: str
    address: str
    data_type: DataType
    direction: Direction
    safe_value: bool | int | float | None

    @property
    def snap7_tag(self) -> str:
        """Return the tag string consumed by python-snap7."""
        return f"{self.address}:{self.data_type.value}"


@dataclass(frozen=True)
class HeartbeatConfig:
    """Names of the PC heartbeat and PLC echo tags."""

    pc_tag: str
    echo_tag: str
    timeout_ms: int


@dataclass(frozen=True)
class InterfaceConfig:
    """Complete, validated interface configuration."""

    version: int
    connection: ConnectionConfig
    heartbeat: HeartbeatConfig
    tags: tuple[TagConfig, ...]

    def tag(self, name: str) -> TagConfig:
        """Return a tag by configured name."""
        for tag in self.tags:
            if tag.name == name:
                return tag
        raise KeyError(name)


_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_ADDRESS_PATTERN = re.compile(
    r"^DB(?P<db>\d+)\."
    r"(?P<area>DBX|DBB|DBW|DBD)"
    r"(?P<byte>\d+)"
    r"(?:\.(?P<bit>[0-7]))?$"
)

_SUPPORTED_CPU_FAMILIES = {"s7-1200", "s7-1500"}
_AREA_TYPES: dict[str, set[DataType]] = {
    "DBX": {DataType.BOOL},
    "DBB": {DataType.BYTE},
    "DBW": {DataType.WORD, DataType.INT},
    "DBD": {DataType.DWORD, DataType.DINT, DataType.REAL},
}
_TYPE_BITS: dict[DataType, int] = {
    DataType.BOOL: 1,
    DataType.BYTE: 8,
    DataType.WORD: 16,
    DataType.DWORD: 32,
    DataType.INT: 16,
    DataType.DINT: 32,
    DataType.REAL: 32,
}


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{path} must be a JSON object")
    return value


def _list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigError(f"{path} must be a JSON array")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{path} must be a non-empty string")
    return value.strip()


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{path} must be an integer")
    return value


def _required(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise ConfigError(f"{path}.{key} is required")
    return mapping[key]


def _reject_unknown(
    mapping: dict[str, Any],
    allowed: set[str],
    path: str,
) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        joined = ", ".join(unknown)
        raise ConfigError(f"{path} has unknown field(s): {joined}")


def _bounded_integer(
    value: Any,
    path: str,
    minimum: int,
    maximum: int,
) -> int:
    parsed = _integer(value, path)
    if not minimum <= parsed <= maximum:
        raise ConfigError(
            f"{path} must be between {minimum} and {maximum}"
        )
    return parsed


def _parse_connection(value: Any) -> ConnectionConfig:
    path = "connection"
    raw = _mapping(value, path)
    _reject_unknown(
        raw,
        {
            "cpu_family",
            "ip",
            "rack",
            "slot",
            "cycle_ms",
            "connect_timeout_ms",
        },
        path,
    )

    cpu_family = _string(
        _required(raw, "cpu_family", path),
        f"{path}.cpu_family",
    ).lower()
    if cpu_family not in _SUPPORTED_CPU_FAMILIES:
        supported = ", ".join(sorted(_SUPPORTED_CPU_FAMILIES))
        raise ConfigError(
            f"{path}.cpu_family must be one of: {supported}"
        )

    ip = _string(_required(raw, "ip", path), f"{path}.ip")
    try:
        IPv4Address(ip)
    except ValueError as exc:
        raise ConfigError(f"{path}.ip must be a valid IPv4 address") from exc

    rack = _bounded_integer(
        _required(raw, "rack", path),
        f"{path}.rack",
        0,
        7,
    )
    slot = _bounded_integer(
        _required(raw, "slot", path),
        f"{path}.slot",
        0,
        31,
    )
    cycle_ms = _bounded_integer(
        _required(raw, "cycle_ms", path),
        f"{path}.cycle_ms",
        10,
        5_000,
    )
    connect_timeout_ms = _bounded_integer(
        _required(raw, "connect_timeout_ms", path),
        f"{path}.connect_timeout_ms",
        100,
        30_000,
    )

    return ConnectionConfig(
        cpu_family=cpu_family,
        ip=ip,
        rack=rack,
        slot=slot,
        cycle_ms=cycle_ms,
        connect_timeout_ms=connect_timeout_ms,
    )


def _parse_data_type(value: Any, path: str) -> DataType:
    text = _string(value, path).upper()
    try:
        return DataType(text)
    except ValueError as exc:
        supported = ", ".join(item.value for item in DataType)
        raise ConfigError(f"{path} must be one of: {supported}") from exc


def _parse_direction(value: Any, path: str) -> Direction:
    text = _string(value, path).lower()
    try:
        return Direction(text)
    except ValueError as exc:
        supported = ", ".join(item.value for item in Direction)
        raise ConfigError(f"{path} must be one of: {supported}") from exc


def validate_data_value(
    value: Any,
    data_type: DataType,
    path: str,
) -> bool | int | float:
    """Validate one Python value against a configured PLC scalar type."""
    if data_type is DataType.BOOL:
        if not isinstance(value, bool):
            raise ConfigError(f"{path} must be true or false for BOOL")
        return value

    if isinstance(value, bool):
        raise ConfigError(f"{path} must be numeric for {data_type.value}")

    if data_type is DataType.REAL:
        if not isinstance(value, (int, float)):
            raise ConfigError(f"{path} must be numeric for REAL")
        parsed = float(value)
        if not math.isfinite(parsed) or abs(parsed) > 3.402_823_5e38:
            raise ConfigError(
                f"{path} must be a finite 32-bit REAL value"
            )
        return parsed

    if not isinstance(value, int):
        raise ConfigError(f"{path} must be an integer for {data_type.value}")

    ranges: dict[DataType, tuple[int, int]] = {
        DataType.BYTE: (0, 255),
        DataType.WORD: (0, 65_535),
        DataType.DWORD: (0, 4_294_967_295),
        DataType.INT: (-32_768, 32_767),
        DataType.DINT: (-2_147_483_648, 2_147_483_647),
    }
    minimum, maximum = ranges[data_type]
    if not minimum <= value <= maximum:
        raise ConfigError(
            f"{path} must be between {minimum} and {maximum} "
            f"for {data_type.value}"
        )
    return value


def _address_interval(
    address: str,
    data_type: DataType,
    path: str,
) -> tuple[int, int, int]:
    match = _ADDRESS_PATTERN.fullmatch(address)
    if match is None:
        raise ConfigError(
            f"{path} must use an absolute DB address such as "
            "DB14.DBX0.0 or DB14.DBD2"
        )

    db_number = int(match.group("db"))
    byte_offset = int(match.group("byte"))
    area = match.group("area")
    bit_text = match.group("bit")

    if db_number < 1:
        raise ConfigError(f"{path} must use DB number 1 or greater")

    if data_type not in _AREA_TYPES[area]:
        allowed = ", ".join(
            item.value for item in sorted(
                _AREA_TYPES[area],
                key=lambda item: item.value,
            )
        )
        raise ConfigError(
            f"{path} area {area} requires data type: {allowed}"
        )

    if area == "DBX":
        if bit_text is None:
            raise ConfigError(f"{path} BOOL address requires a bit number")
        start_bit = byte_offset * 8 + int(bit_text)
    else:
        if bit_text is not None:
            raise ConfigError(
                f"{path} must not include a bit number for {data_type.value}"
            )
        start_bit = byte_offset * 8

    return db_number, start_bit, start_bit + _TYPE_BITS[data_type]


def _parse_tag(value: Any, index: int) -> tuple[TagConfig, tuple[int, int, int]]:
    path = f"tags[{index}]"
    raw = _mapping(value, path)
    _reject_unknown(
        raw,
        {
            "name",
            "plc_symbol",
            "address",
            "data_type",
            "direction",
            "safe_value",
        },
        path,
    )

    name = _string(_required(raw, "name", path), f"{path}.name").lower()
    if _NAME_PATTERN.fullmatch(name) is None:
        raise ConfigError(
            f"{path}.name must start with a lowercase letter and contain "
            "only lowercase letters, digits, and underscores"
        )

    plc_symbol = _string(
        _required(raw, "plc_symbol", path),
        f"{path}.plc_symbol",
    )
    address = _string(
        _required(raw, "address", path),
        f"{path}.address",
    ).upper()
    data_type = _parse_data_type(
        _required(raw, "data_type", path),
        f"{path}.data_type",
    )
    direction = _parse_direction(
        _required(raw, "direction", path),
        f"{path}.direction",
    )
    interval = _address_interval(address, data_type, f"{path}.address")

    if direction is Direction.PC_TO_PLC:
        if "safe_value" not in raw:
            raise ConfigError(
                f"{path}.safe_value is required for pc_to_plc tags"
            )
        safe_value = validate_data_value(
            raw["safe_value"],
            data_type,
            f"{path}.safe_value",
        )
    else:
        if "safe_value" in raw and raw["safe_value"] is not None:
            raise ConfigError(
                f"{path}.safe_value must be omitted or null "
                "for plc_to_pc tags"
            )
        safe_value = None

    return (
        TagConfig(
            name=name,
            plc_symbol=plc_symbol,
            address=address,
            data_type=data_type,
            direction=direction,
            safe_value=safe_value,
        ),
        interval,
    )


def _validate_unique_and_non_overlapping(
    tags: list[TagConfig],
    intervals: list[tuple[int, int, int]],
) -> None:
    names: set[str] = set()
    symbols: set[str] = set()
    addresses: set[str] = set()

    for index, tag in enumerate(tags):
        for value, seen, label in (
            (tag.name, names, "name"),
            (tag.plc_symbol, symbols, "plc_symbol"),
            (tag.address, addresses, "address"),
        ):
            if value in seen:
                raise ConfigError(
                    f"tags[{index}].{label} duplicates {value!r}"
                )
            seen.add(value)

    occupied: list[tuple[int, int, int, str]] = []
    for tag, interval in zip(tags, intervals, strict=True):
        db_number, start_bit, end_bit = interval
        for used_db, used_start, used_end, used_name in occupied:
            overlaps = (
                db_number == used_db
                and start_bit < used_end
                and used_start < end_bit
            )
            if overlaps:
                raise ConfigError(
                    f"tag {tag.name!r} overlaps tag {used_name!r} "
                    f"in DB{db_number}"
                )
        occupied.append((db_number, start_bit, end_bit, tag.name))


def _parse_heartbeat(
    value: Any,
    connection: ConnectionConfig,
    tags_by_name: dict[str, TagConfig],
) -> HeartbeatConfig:
    path = "heartbeat"
    raw = _mapping(value, path)
    _reject_unknown(raw, {"pc_tag", "echo_tag", "timeout_ms"}, path)

    pc_tag_name = _string(
        _required(raw, "pc_tag", path),
        f"{path}.pc_tag",
    ).lower()
    echo_tag_name = _string(
        _required(raw, "echo_tag", path),
        f"{path}.echo_tag",
    ).lower()
    timeout_ms = _bounded_integer(
        _required(raw, "timeout_ms", path),
        f"{path}.timeout_ms",
        20,
        60_000,
    )

    if timeout_ms < connection.cycle_ms * 2:
        raise ConfigError(
            "heartbeat.timeout_ms must be at least twice "
            "connection.cycle_ms"
        )

    if pc_tag_name == echo_tag_name:
        raise ConfigError("heartbeat.pc_tag and echo_tag must be different")

    try:
        pc_tag = tags_by_name[pc_tag_name]
    except KeyError as exc:
        raise ConfigError(
            f"heartbeat.pc_tag references unknown tag {pc_tag_name!r}"
        ) from exc
    try:
        echo_tag = tags_by_name[echo_tag_name]
    except KeyError as exc:
        raise ConfigError(
            f"heartbeat.echo_tag references unknown tag {echo_tag_name!r}"
        ) from exc

    if (
        pc_tag.direction is not Direction.PC_TO_PLC
        or pc_tag.data_type is not DataType.DINT
    ):
        raise ConfigError(
            "heartbeat.pc_tag must reference a pc_to_plc DINT tag"
        )
    if (
        echo_tag.direction is not Direction.PLC_TO_PC
        or echo_tag.data_type is not DataType.DINT
    ):
        raise ConfigError(
            "heartbeat.echo_tag must reference a plc_to_pc DINT tag"
        )

    return HeartbeatConfig(
        pc_tag=pc_tag_name,
        echo_tag=echo_tag_name,
        timeout_ms=timeout_ms,
    )


def parse_config(value: Any) -> InterfaceConfig:
    """Validate a decoded JSON value and return an immutable configuration."""
    root = _mapping(value, "config")
    _reject_unknown(
        root,
        {"version", "connection", "heartbeat", "tags"},
        "config",
    )

    version = _integer(_required(root, "version", "config"), "version")
    if version != 1:
        raise ConfigError("version must be 1")

    connection = _parse_connection(
        _required(root, "connection", "config")
    )

    raw_tags = _list(_required(root, "tags", "config"), "tags")
    if not raw_tags:
        raise ConfigError("tags must contain at least one tag")

    parsed_tags: list[TagConfig] = []
    intervals: list[tuple[int, int, int]] = []
    for index, raw_tag in enumerate(raw_tags):
        tag, interval = _parse_tag(raw_tag, index)
        parsed_tags.append(tag)
        intervals.append(interval)

    _validate_unique_and_non_overlapping(parsed_tags, intervals)
    tags_by_name = {tag.name: tag for tag in parsed_tags}
    heartbeat = _parse_heartbeat(
        _required(root, "heartbeat", "config"),
        connection,
        tags_by_name,
    )

    return InterfaceConfig(
        version=version,
        connection=connection,
        heartbeat=heartbeat,
        tags=tuple(parsed_tags),
    )


def load_config(path: str | Path) -> InterfaceConfig:
    """Read, decode, and validate a configuration file."""
    config_path = Path(path)
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(
            f"cannot read configuration file {config_path}: {exc}"
        ) from exc

    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc

    return parse_config(decoded)
