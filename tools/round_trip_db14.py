"""
Legacy DB14 direct-echo proof for the original four-field PLC logic.

This diagnostic does not maintain the continuous heartbeat required by the
current PLC watchdog. Use ``siemens-plc-pc-interface run`` for the watchdog
configuration documented in ``docs/USER_SETUP.md``.

PC writes:
  DB14.DBX0.0  PC_To_PLC
  DB14.DBD2    PC_Heartbeat

PLC program echoes to:
  DB14.DBX0.1  PLC_To_PC
  DB14.DBD6    PLC_Heartbeat_Echo

The original PC-owned values are restored before disconnecting. This utility
does not write the PLC-owned echo fields or any physical I/O address.
"""

from __future__ import annotations

import argparse
import time

from snap7 import Client


PC_BOOL = "DB14.DBX0.0:BOOL"
PLC_BOOL = "DB14.DBX0.1:BOOL"
PC_HEARTBEAT = "DB14.DBD2:DINT"
PLC_HEARTBEAT = "DB14.DBD6:DINT"


def snapshot(client: Client) -> dict[str, bool | int]:
    """Read all four fields in the validated DB14 interface."""
    return {
        "PC_To_PLC": client.read_tag(PC_BOOL),
        "PLC_To_PC": client.read_tag(PLC_BOOL),
        "PC_Heartbeat": client.read_tag(PC_HEARTBEAT),
        "PLC_Heartbeat_Echo": client.read_tag(PLC_HEARTBEAT),
    }


def run_state(
    client: Client,
    label: str,
    bool_value: bool,
    heartbeat: int,
    hold_seconds: float,
) -> dict[str, bool | int]:
    """Write one PC-owned test state, hold it, and read the complete result."""
    client.write_tag(PC_BOOL, bool_value)
    client.write_tag(PC_HEARTBEAT, heartbeat)
    print(
        f"{label}_WRITTEN: PC_To_PLC={bool_value} "
        f"PC_Heartbeat={heartbeat}"
    )
    print(
        f"{label}_HOLD: {hold_seconds:.1f} seconds "
        "for TIA watch-table visibility"
    )
    time.sleep(hold_seconds)
    return snapshot(client)


def state_passed(state: dict[str, bool | int]) -> bool:
    """Return true when both PLC-owned echoes match the PC-owned fields."""
    return (
        state["PLC_To_PC"] == state["PC_To_PLC"]
        and state["PLC_Heartbeat_Echo"] == state["PC_Heartbeat"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Explicit-write DB14 round-trip proof for the isolated "
            "simulation interface"
        )
    )
    parser.add_argument("--ip", default="10.70.9.201", help="PLC IPv4 address")
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Allow writes only to DB14.DBX0.0 and DB14.DBD2, "
            "then restore them"
        ),
    )
    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=5.0,
        help=(
            "Seconds to hold each test state so TIA can display it "
            "(default: 5)"
        ),
    )
    args = parser.parse_args()

    if not 0.1 <= args.hold_seconds <= 60.0:
        parser.error("--hold-seconds must be between 0.1 and 60")

    print("MODE: LEGACY DB14 DIRECT-ECHO WRITE/READ/RESTORE")
    print(
        "WARNING: this tool does not service the current continuous "
        "heartbeat watchdog; use the configured runtime for that PLC logic"
    )
    print(f"TARGET: {args.ip}")
    print("RACK/SLOT: 0/1")
    print("WRITE SCOPE: DB14.DBX0.0 and DB14.DBD2 only")
    print(f"HOLD TIME: {args.hold_seconds:.1f} seconds per test state")

    if not args.execute:
        print("NOT RUN: add --execute to authorize the isolated DB14 write test")
        return 2

    client = Client()
    original: dict[str, bool | int] | None = None
    passed = False
    restore_confirmed = False

    try:
        client.connect(args.ip, 0, 1)
        print(f"S7_SESSION_CONNECTED: {client.get_connected()}")

        original = snapshot(client)
        print(f"ORIGINAL: {original}")

        state_a = run_state(
            client,
            "TEST_A",
            True,
            24_072_401,
            args.hold_seconds,
        )
        print(f"TEST_A: {state_a} PASS={state_passed(state_a)}")

        state_b = run_state(
            client,
            "TEST_B",
            False,
            24_072_402,
            args.hold_seconds,
        )
        print(f"TEST_B: {state_b} PASS={state_passed(state_b)}")

        passed = state_passed(state_a) and state_passed(state_b)
    except Exception as exc:
        print(f"TEST_ERROR: {type(exc).__name__}: {exc}")
    finally:
        if original is not None:
            try:
                client.write_tag(PC_BOOL, original["PC_To_PLC"])
                client.write_tag(
                    PC_HEARTBEAT,
                    original["PC_Heartbeat"],
                )
                time.sleep(0.100)
                restored = snapshot(client)
                print(f"RESTORED: {restored}")
                restore_confirmed = (
                    restored["PC_To_PLC"] == original["PC_To_PLC"]
                    and restored["PC_Heartbeat"]
                    == original["PC_Heartbeat"]
                )
                print(f"RESTORE_CONFIRMED: {restore_confirmed}")
            except Exception as exc:
                print(f"RESTORE_ERROR: {type(exc).__name__}: {exc}")
        try:
            client.disconnect()
        except Exception:
            pass

    proof_passed = passed and restore_confirmed
    print(f"ROUND_TRIP_PROOF: {'PASS' if proof_passed else 'FAIL'}")
    return 0 if proof_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
