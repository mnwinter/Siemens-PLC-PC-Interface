"""Command-line entry point for offline validation and guarded runtime work."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Sequence
from typing import Any

from .config import (
    AnalogPointConfig,
    ConfigError,
    DigitalPointConfig,
    Direction,
    load_config,
)
from .points import build_address_groups
from .runtime import InterfaceRuntime, SafeStatePolicy
from .transport import Snap7Transport


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="siemens-plc-pc-interface",
        description="Siemens PLC-PC Interface utilities",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate",
        help="validate a JSON interface configuration without connecting",
    )
    validate.add_argument("config", help="path to the JSON configuration")

    run = commands.add_parser(
        "run",
        help="run the configured PLC exchange loop with explicit write approval",
    )
    run.add_argument("config", help="path to the JSON configuration")
    run.add_argument(
        "--execute",
        action="store_true",
        help="authorize writes only to configured pc_to_plc DB tags",
    )
    run.add_argument(
        "--cycles",
        type=_positive_integer,
        help="stop after this many cycles; omit to run until Ctrl+C",
    )
    run.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="NAME=JSON_VALUE",
        help=(
            "set a non-heartbeat PC-owned value, for example "
            "--set pc_to_plc=true"
        ),
    )
    run.add_argument(
        "--write-safe-state-on-exit",
        action="store_true",
        help=(
            "best-effort write configured safe values before disconnecting; "
            "the PLC watchdog remains authoritative"
        ),
    )
    return parser


def _positive_integer(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return value


def _run_validate(path: str) -> int:
    try:
        config = load_config(path)
    except ConfigError as exc:
        print(f"CONFIG_INVALID: {exc}", file=sys.stderr)
        return 2

    pc_tags = [
        tag for tag in config.tags
        if tag.direction is Direction.PC_TO_PLC
    ]
    plc_tags = [
        tag for tag in config.tags
        if tag.direction is Direction.PLC_TO_PC
    ]
    digital_points = [
        point
        for point in config.points
        if isinstance(point, DigitalPointConfig)
    ]
    analog_points = [
        point
        for point in config.points
        if isinstance(point, AnalogPointConfig)
    ]
    address_groups = build_address_groups(config)

    print("CONFIG_VALID: True")
    print(f"VERSION: {config.version}")
    print(
        "CONNECTION: "
        f"{config.connection.cpu_family} "
        f"{config.connection.ip} "
        f"rack={config.connection.rack} "
        f"slot={config.connection.slot}"
    )
    print(f"CYCLE_MS: {config.connection.cycle_ms}")
    print(f"PC_TO_PLC_TAGS: {len(pc_tags)}")
    print(f"PLC_TO_PC_TAGS: {len(plc_tags)}")
    print(f"DIGITAL_POINTS: {len(digital_points)}")
    print(f"ANALOG_POINTS: {len(analog_points)}")
    print(f"ADDRESS_GROUPS: {len(address_groups)}")
    print(
        "MIXED_OWNER_BYTE_GROUPS: "
        f"{sum(group.shares_byte_with_opposite_owner for group in address_groups)}"
    )
    print(
        "HEARTBEAT: "
        f"{config.heartbeat.pc_tag} -> "
        f"{config.heartbeat.echo_tag} "
        f"timeout={config.heartbeat.timeout_ms}ms"
    )
    print("PLC_CONNECTION_ATTEMPTED: False")
    return 0


def _load_for_command(path: str) -> Any:
    try:
        return load_config(path)
    except ConfigError as exc:
        print(f"CONFIG_INVALID: {exc}", file=sys.stderr)
        return None


def _apply_assignments(
    runtime: InterfaceRuntime,
    assignments: list[str],
) -> None:
    seen: set[str] = set()
    for assignment in assignments:
        name, separator, raw_value = assignment.partition("=")
        name = name.strip()
        if not separator or not name or not raw_value.strip():
            raise ConfigError(
                f"invalid --set {assignment!r}; expected NAME=JSON_VALUE"
            )
        if name in seen:
            raise ConfigError(f"duplicate --set for tag {name!r}")
        seen.add(name)
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"invalid JSON value in --set {assignment!r}: {exc.msg}"
            ) from exc
        runtime.set_pc_value(name, value)


def _scope_text(runtime: InterfaceRuntime) -> str:
    return ", ".join(
        f"{tag.name}={tag.snap7_tag}"
        for tag in runtime.write_scope
    )


def _cycle_text(
    result: Any,
    pc_heartbeat_name: str,
    echo_name: str,
) -> str:
    heartbeat = result.pc_values_written.get(pc_heartbeat_name)
    echo = result.plc_values_read.get(echo_name)
    plc_values = json.dumps(
        result.plc_values_read,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (
        f"CYCLE {result.cycle_number}: "
        f"heartbeat={heartbeat} echo={echo} "
        f"healthy={result.heartbeat.healthy} "
        f"reason={result.heartbeat.reason} "
        f"age_ms={result.heartbeat.age_ms} "
        f"plc={plc_values}"
    )


def _run_interface(args: argparse.Namespace) -> int:
    config = _load_for_command(args.config)
    if config is None:
        return 2

    policy = (
        SafeStatePolicy.BEST_EFFORT_WRITE
        if args.write_safe_state_on_exit
        else SafeStatePolicy.PLC_WATCHDOG_ONLY
    )
    runtime = InterfaceRuntime(
        config,
        Snap7Transport(),
        safe_state_policy=policy,
        start_time=time.monotonic(),
    )
    try:
        _apply_assignments(runtime, args.set)
    except ConfigError as exc:
        print(f"RUNTIME_CONFIG_INVALID: {exc}", file=sys.stderr)
        print("PLC_CONNECTION_ATTEMPTED: False")
        return 2

    print("MODE: CONFIGURED PLC RUNTIME")
    print(
        f"TARGET: {config.connection.ip} "
        f"rack={config.connection.rack} "
        f"slot={config.connection.slot}"
    )
    print(f"CYCLE_MS: {config.connection.cycle_ms}")
    print(f"WRITE_SCOPE: {_scope_text(runtime)}")
    print(
        "SAFE_STATE_POLICY: "
        f"{runtime.safe_state_policy.value}"
    )

    if not args.execute:
        print("PLC_CONNECTION_ATTEMPTED: False")
        print(
            "NOT RUN: add --execute to authorize only the listed "
            "configured DB writes"
        )
        return 2

    exit_code = 0
    try:
        runtime.connect()
        print("S7_SESSION_CONNECTED: True")

        deadline = time.monotonic()
        completed_cycles = 0
        saw_healthy_heartbeat = False
        last_result = None
        while (
            args.cycles is None
            or completed_cycles < args.cycles
        ):
            result = runtime.cycle(time.monotonic())
            last_result = result
            saw_healthy_heartbeat = (
                saw_healthy_heartbeat or result.heartbeat.healthy
            )
            completed_cycles += 1
            print(
                _cycle_text(
                    result,
                    config.heartbeat.pc_tag,
                    config.heartbeat.echo_tag,
                )
            )

            deadline += config.connection.cycle_ms / 1_000
            delay = deadline - time.monotonic()
            if delay > 0:
                time.sleep(delay)

        heartbeat_passed = (
            saw_healthy_heartbeat
            and last_result is not None
            and last_result.heartbeat.healthy
        )
        print(
            "HEARTBEAT_PROOF: "
            f"{'PASS' if heartbeat_passed else 'FAIL'}"
        )
        if not heartbeat_passed:
            exit_code = 1
    except KeyboardInterrupt:
        print("STOP_REQUESTED: Ctrl+C")
    except Exception as exc:
        print(
            f"RUNTIME_ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        exit_code = 1
    finally:
        shutdown = runtime.close()
        if shutdown.safe_state_attempted:
            print(
                "SAFE_STATE_WRITE: "
                f"{'PASS' if shutdown.safe_state_succeeded else 'FAIL'}"
            )
        else:
            print("SAFE_STATE_WRITE: NOT_REQUESTED")
        if shutdown.safe_state_error is not None:
            print(
                f"SAFE_STATE_ERROR: {shutdown.safe_state_error}",
                file=sys.stderr,
            )
            exit_code = 1
        if shutdown.disconnect_error is not None:
            print(
                f"DISCONNECT_ERROR: {shutdown.disconnect_error}",
                file=sys.stderr,
            )
            exit_code = 1

    return exit_code


def main(argv: Sequence[str] | None = None) -> int:
    """Run one requested command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _run_validate(args.config)
    if args.command == "run":
        return _run_interface(args)

    parser.error(f"unsupported command: {args.command}")
    return 2
