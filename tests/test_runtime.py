"""Unit tests for one configuration-driven PLC exchange cycle."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.config import (
    ConfigError,
    ConnectionConfig,
    Direction,
    TagConfig,
    parse_config,
)
from siemens_plc_pc_interface.runtime import (
    InterfaceRuntime,
    SafeStatePolicy,
)
from siemens_plc_pc_interface.transport import TagValue, TransportError
from test_config import valid_config


class FakeTransport:
    """In-memory transport used to prove runtime scope and failure behavior."""

    def __init__(self, plc_values: dict[str, TagValue]) -> None:
        self._connected = False
        self.plc_values = plc_values
        self.connect_calls: list[ConnectionConfig] = []
        self.reads: list[str] = []
        self.writes: list[tuple[str, TagValue]] = []
        self.disconnect_calls = 0
        self.fail_writes = False

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self, connection: ConnectionConfig) -> None:
        self.connect_calls.append(connection)
        self._connected = True

    def disconnect(self) -> None:
        self.disconnect_calls += 1
        self._connected = False

    def read(self, tag: TagConfig) -> TagValue:
        if tag.direction is not Direction.PLC_TO_PC:
            raise AssertionError(f"test caught invalid read: {tag.name}")
        self.reads.append(tag.name)
        return self.plc_values[tag.name]

    def write(self, tag: TagConfig, value: TagValue) -> None:
        if tag.direction is not Direction.PC_TO_PLC:
            raise AssertionError(f"test caught invalid write: {tag.name}")
        if self.fail_writes:
            raise TransportError("test write failure")
        self.writes.append((tag.name, value))


def initial_plc_values() -> dict[str, TagValue]:
    return {
        "plc_to_pc": False,
        "plc_heartbeat_echo": 0,
        "simulation_enable": True,
        "simulation_comm_ok": False,
        "simulation_timeout": True,
    }


class InterfaceRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = parse_config(valid_config())
        self.transport = FakeTransport(initial_plc_values())
        self.runtime = InterfaceRuntime(
            self.config,
            self.transport,
            start_time=0.0,
        )
        self.runtime.connect()

    def test_cycle_reads_only_plc_tags_and_writes_only_pc_tags(self) -> None:
        result = self.runtime.cycle(now=0.0)

        self.assertEqual(
            self.transport.reads,
            [
                "plc_to_pc",
                "plc_heartbeat_echo",
                "simulation_enable",
                "simulation_comm_ok",
                "simulation_timeout",
            ],
        )
        self.assertEqual(
            self.transport.writes,
            [
                ("pc_to_plc", False),
                ("pc_heartbeat", 1),
            ],
        )
        self.assertEqual(result.cycle_number, 1)
        self.assertFalse(result.heartbeat.healthy)
        self.assertEqual(
            result.heartbeat.reason,
            "waiting_for_first_echo",
        )

    def test_cycle_prefers_batched_transport_when_available(self) -> None:
        class BatchTransport(FakeTransport):
            def __init__(self) -> None:
                super().__init__(initial_plc_values())
                self.batch_reads: list[list[str]] = []
                self.batch_writes: list[
                    list[tuple[str, TagValue]]
                ] = []

            def read(self, tag: TagConfig) -> TagValue:
                raise AssertionError("scalar read should not be used")

            def write(self, tag: TagConfig, value: TagValue) -> None:
                raise AssertionError("scalar write should not be used")

            def read_many(
                self,
                tags: tuple[TagConfig, ...],
            ) -> dict[str, TagValue]:
                self.batch_reads.append([tag.name for tag in tags])
                return {
                    tag.name: self.plc_values[tag.name]
                    for tag in tags
                }

            def write_many(
                self,
                values: list[tuple[TagConfig, TagValue]],
            ) -> None:
                self.batch_writes.append(
                    [(tag.name, value) for tag, value in values]
                )

        transport = BatchTransport()
        runtime = InterfaceRuntime(
            self.config,
            transport,
            start_time=0.0,
        )
        runtime.connect()

        result = runtime.cycle(now=0.0)

        self.assertEqual(
            transport.batch_reads,
            [[
                "plc_to_pc",
                "plc_heartbeat_echo",
                "simulation_enable",
                "simulation_comm_ok",
                "simulation_timeout",
            ]],
        )
        self.assertEqual(
            transport.batch_writes,
            [[
                ("pc_to_plc", False),
                ("pc_heartbeat", 1),
            ]],
        )
        self.assertEqual(result.pc_values_written["pc_heartbeat"], 1)

    def test_scene_value_and_progressing_echo_become_healthy(self) -> None:
        self.runtime.cycle(now=0.0)
        self.runtime.set_pc_value("pc_to_plc", True)
        self.transport.plc_values["plc_heartbeat_echo"] = 1

        result = self.runtime.cycle(now=0.1)

        self.assertTrue(result.heartbeat.healthy)
        self.assertEqual(result.heartbeat.reason, "echo_progressing")
        self.assertEqual(
            self.transport.writes[-2:],
            [
                ("pc_to_plc", True),
                ("pc_heartbeat", 2),
            ],
        )

    def test_typed_digital_point_sets_its_backing_tag(self) -> None:
        raw = valid_config()
        raw["version"] = 2
        raw["points"] = [
            {
                "name": "simulated_photoeye",
                "kind": "digital",
                "tag": "pc_to_plc",
                "group": "proof",
                "inverted": True,
            }
        ]
        transport = FakeTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            parse_config(raw),
            transport,
            start_time=0.0,
        )
        runtime.connect()

        sample = runtime.set_pc_point("simulated_photoeye", False)
        runtime.cycle(now=0.0)

        self.assertIs(sample.value, False)
        self.assertIs(sample.raw_value, True)
        self.assertEqual(
            transport.writes[:2],
            [
                ("pc_to_plc", True),
                ("pc_heartbeat", 1),
            ],
        )

    def test_unchanged_scene_value_is_not_rewritten_every_cycle(self) -> None:
        self.runtime.cycle(now=0.0)
        self.transport.plc_values["plc_heartbeat_echo"] = 1

        result = self.runtime.cycle(now=0.1)

        self.assertEqual(
            result.pc_values_written,
            {"pc_heartbeat": 2},
        )
        self.assertEqual(
            self.transport.writes,
            [
                ("pc_to_plc", False),
                ("pc_heartbeat", 1),
                ("pc_heartbeat", 2),
            ],
        )

    def test_stalled_echo_becomes_unhealthy(self) -> None:
        self.runtime.cycle(now=0.0)
        self.transport.plc_values["plc_heartbeat_echo"] = 1
        self.runtime.cycle(now=0.1)

        result = self.runtime.cycle(now=1.101)

        self.assertFalse(result.heartbeat.healthy)
        self.assertEqual(result.heartbeat.reason, "echo_stalled")

    def test_plc_owned_and_generated_heartbeat_values_cannot_be_set(self) -> None:
        with self.assertRaisesRegex(ConfigError, "PLC-owned"):
            self.runtime.set_pc_value("plc_to_pc", True)
        with self.assertRaisesRegex(ConfigError, "generated internally"):
            self.runtime.set_pc_value("pc_heartbeat", 5)

    def test_default_close_relies_on_plc_watchdog(self) -> None:
        self.runtime.cycle(now=0.0)
        writes_before_close = list(self.transport.writes)

        result = self.runtime.close()

        self.assertFalse(result.safe_state_attempted)
        self.assertEqual(self.transport.writes, writes_before_close)
        self.assertEqual(self.transport.disconnect_calls, 1)

    def test_opt_in_close_writes_safe_values_then_disconnects(self) -> None:
        transport = FakeTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            self.config,
            transport,
            safe_state_policy=SafeStatePolicy.BEST_EFFORT_WRITE,
        )
        runtime.connect()
        runtime.set_pc_value("pc_to_plc", True)
        runtime.cycle(now=0.0)

        result = runtime.close()

        self.assertTrue(result.safe_state_attempted)
        self.assertTrue(result.safe_state_succeeded)
        self.assertEqual(
            transport.writes[-2:],
            [
                ("pc_to_plc", False),
                ("pc_heartbeat", 0),
            ],
        )
        self.assertEqual(transport.disconnect_calls, 1)

    def test_safe_write_failure_is_reported_and_disconnect_still_runs(self) -> None:
        transport = FakeTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            self.config,
            transport,
            safe_state_policy=SafeStatePolicy.BEST_EFFORT_WRITE,
        )
        runtime.connect()
        transport.fail_writes = True

        result = runtime.close()

        self.assertTrue(result.safe_state_attempted)
        self.assertFalse(result.safe_state_succeeded)
        self.assertIn("test write failure", result.safe_state_error or "")
        self.assertEqual(transport.disconnect_calls, 1)


if __name__ == "__main__":
    unittest.main()
