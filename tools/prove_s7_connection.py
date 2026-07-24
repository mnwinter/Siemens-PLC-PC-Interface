"""
Read-only S7 connection diagnostic.

Question being answered:
Can this computer establish a real S7 session with the configured PLC and
retrieve controller information without changing PLC memory?

This utility does not call any PLC write, start, stop, download, or
memory-modification operation.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from snap7 import Client


def print_query(label: str, query: Callable[[], Any]) -> None:
    """Run one read-only query without hiding results from other queries."""
    try:
        print(f"{label}: {query()}")
    except Exception as exc:
        print(f"{label}: UNAVAILABLE ({type(exc).__name__}: {exc})")


def format_order_code(client: Client) -> str:
    """Format the order number and firmware fields returned by the PLC."""
    result = client.get_order_code()
    order_code = (
        bytes(result.OrderCode)
        .split(b"\0", 1)[0]
        .decode(errors="replace")
        .strip()
    )
    return f"{order_code}, firmware V{result.V1}.{result.V2}.{result.V3}"


def format_bytes(data: bytearray) -> str:
    """Format a byte array for readable diagnostic output."""
    return " ".join(f"{value:02X}" for value in data)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Siemens S7 connection proof"
    )
    parser.add_argument("--ip", default="10.70.9.201", help="PLC IPv4 address")
    args = parser.parse_args()

    client = Client()

    print("MODE: READ-ONLY")
    print(f"TARGET: {args.ip}")
    print("RACK/SLOT: 0/1")

    try:
        client.connect(args.ip, 0, 1)
        print(f"S7_SESSION_CONNECTED: {client.get_connected()}")

        print_query("CPU_INFO", client.get_cpu_info)
        print_query(
            "ORDER_CODE_AND_FIRMWARE",
            lambda: format_order_code(client),
        )
        print_query(
            "PROCESS_INPUT_BYTE_0",
            lambda: format_bytes(client.eb_read(0, 1)),
        )
        print_query(
            "PROCESS_OUTPUT_BYTE_0",
            lambda: format_bytes(client.ab_read(0, 1)),
        )
        print_query("CPU_STATE", client.get_cpu_state)
        print_query("COMM_PROCESSOR_INFO", client.get_cp_info)
        print_query("NEGOTIATED_PDU", client.get_pdu_length)
        print_query("PLC_CLOCK", client.get_plc_datetime)
        print_query("PROTECTION", client.get_protection)
    except Exception as exc:
        print("S7_SESSION_CONNECTED: False")
        print(f"CONNECTION_ERROR: {type(exc).__name__}: {exc}")
        return 1
    finally:
        try:
            client.disconnect()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
