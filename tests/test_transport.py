"""Unit tests for the guarded python-snap7 transport boundary."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.config import parse_config
from siemens_plc_pc_interface.transport import (
    OwnershipError,
    Snap7Transport,
    TransportError,
)
from test_config import valid_config


class FakeSnap7Client:
    """Minimal python-snap7 stand-in; it never opens a network connection."""

    def __init__(self) -> None:
        self.is_connected = False
        self.connect_calls: list[tuple[str, int, int]] = []
        self.disconnect_calls = 0
        self.read_values: dict[str, object] = {}
        self.write_calls: list[tuple[str, object]] = []
        self.db_memory = bytearray(32)
        self.db_read_calls: list[tuple[int, int, int]] = []
        self.db_write_calls: list[tuple[int, int, bytes]] = []

    def connect(self, ip: str, rack: int, slot: int) -> None:
        self.connect_calls.append((ip, rack, slot))
        self.is_connected = True

    def get_connected(self) -> bool:
        return self.is_connected

    def disconnect(self) -> None:
        self.disconnect_calls += 1
        self.is_connected = False

    def read_tag(self, tag: str) -> object:
        return self.read_values[tag]

    def write_tag(self, tag: str, value: object) -> None:
        self.write_calls.append((tag, value))

    def db_read(
        self,
        db_number: int,
        start: int,
        size: int,
    ) -> bytearray:
        self.db_read_calls.append((db_number, start, size))
        return bytearray(self.db_memory[start:start + size])

    def db_write(
        self,
        db_number: int,
        start: int,
        data: bytearray,
    ) -> int:
        self.db_write_calls.append((db_number, start, bytes(data)))
        self.db_memory[start:start + len(data)] = data
        return 0


class Snap7TransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = parse_config(valid_config())
        self.client = FakeSnap7Client()
        self.transport = Snap7Transport(lambda: self.client)

    def test_connect_uses_configured_endpoint(self) -> None:
        self.transport.connect(self.config.connection)

        self.assertTrue(self.transport.connected)
        self.assertEqual(
            self.client.connect_calls,
            [("10.70.9.201", 0, 1)],
        )

    def test_read_and_write_use_typed_snap7_tags(self) -> None:
        self.transport.connect(self.config.connection)
        plc_tag = self.config.tag("plc_to_pc")
        pc_tag = self.config.tag("pc_to_plc")
        self.client.read_values[plc_tag.snap7_tag] = True

        self.assertIs(self.transport.read(plc_tag), True)
        self.transport.write(pc_tag, False)

        self.assertEqual(
            self.client.write_calls,
            [("DB14.DBX0.0:BOOL", False)],
        )

    def test_transport_rejects_operations_against_ownership(self) -> None:
        self.transport.connect(self.config.connection)

        with self.assertRaisesRegex(OwnershipError, "PC-owned"):
            self.transport.read(self.config.tag("pc_to_plc"))
        with self.assertRaisesRegex(OwnershipError, "PLC-owned"):
            self.transport.write(
                self.config.tag("plc_to_pc"),
                False,
            )

    def test_read_many_uses_one_contiguous_db_read(self) -> None:
        self.transport.connect(self.config.connection)
        self.client.db_memory[0] = 0b0000_0010
        self.client.db_memory[6:10] = (123).to_bytes(
            4,
            byteorder="big",
            signed=True,
        )
        self.client.db_memory[10] = 0b0000_0101
        plc_tags = tuple(
            tag
            for tag in self.config.tags
            if tag.direction.value == "plc_to_pc"
        )

        values = self.transport.read_many(plc_tags)

        self.assertEqual(
            values,
            {
                "plc_to_pc": True,
                "plc_heartbeat_echo": 123,
                "simulation_enable": True,
                "simulation_comm_ok": False,
                "simulation_timeout": True,
            },
        )
        self.assertEqual(self.client.db_read_calls, [(14, 0, 11)])

    def test_write_many_preserves_adjacent_plc_bit(self) -> None:
        self.transport.connect(self.config.connection)
        self.client.db_memory[0] = 0b0000_0010
        pc_bool = self.config.tag("pc_to_plc")
        heartbeat = self.config.tag("pc_heartbeat")

        self.transport.write_many(
            (
                (pc_bool, True),
                (heartbeat, 123),
            )
        )

        self.assertEqual(self.client.db_read_calls, [(14, 0, 1)])
        self.assertEqual(
            self.client.db_write_calls,
            [
                (14, 0, b"\x03"),
                (14, 2, b"\x00\x00\x00{"),
            ],
        )

    def test_failed_connection_is_cleaned_up(self) -> None:
        class FailedClient(FakeSnap7Client):
            def connect(self, ip: str, rack: int, slot: int) -> None:
                raise OSError("test connection failure")

        failed = FailedClient()
        transport = Snap7Transport(lambda: failed)

        with self.assertRaisesRegex(TransportError, "failed to connect"):
            transport.connect(self.config.connection)

        self.assertFalse(transport.connected)
        self.assertEqual(failed.disconnect_calls, 1)


if __name__ == "__main__":
    unittest.main()
