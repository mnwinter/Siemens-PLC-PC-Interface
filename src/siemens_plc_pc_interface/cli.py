"""Command-line entry point for safe, offline project operations."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .config import ConfigError, Direction, load_config


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
    return parser


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
    print(
        "HEARTBEAT: "
        f"{config.heartbeat.pc_tag} -> "
        f"{config.heartbeat.echo_tag} "
        f"timeout={config.heartbeat.timeout_ms}ms"
    )
    print("PLC_CONNECTION_ATTEMPTED: False")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run one requested command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _run_validate(args.config)

    parser.error(f"unsupported command: {args.command}")
    return 2
