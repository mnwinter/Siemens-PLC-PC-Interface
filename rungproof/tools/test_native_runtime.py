"""Regression tests for the direct native RungProof PLC path."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace
from typing import Callable
import unittest

from tools.native_runtime import (
    ConnectionState,
    InterfaceRuntime,
    NativePlcSession,
    NativeRuntimeError,
    PROFILE_FILE,
    SCENE_FILE,
    Scene2CycleCore,
    Snap7Transport,
    SimulationUpdateLoop,
    load_config,
    load_scene2_definition,
    next_cycle_deadline,
    validate_native_profile,
)


class LadderTransport:
    """In-memory DB14 behavior used only to prove the native seam."""

    instances: list["LadderTransport"] = []

    def __init__(self) -> None:
        self.connected = False
        self.disconnect_count = 0
        self.values: dict[str, object] = {
            "simulated_photoeye": False,
            "simulated_pusher_extended": False,
            "simulated_pusher_retracted": True,
            "pc_heartbeat": 0,
            "plc_heartbeat_echo": 0,
            "conveyor_running": False,
            "pusher_extend": False,
            "simulation_enable": True,
            "simulation_comm_ok": True,
            "simulation_timeout": False,
        }
        self.photoeye_true_cycles = 0
        self.pusher_command_cycles = 0
        self.writes: list[tuple[str, object]] = []
        self.read_times: list[float] = []
        self.fail_next_read = False
        self.freeze_echo = False
        self.force_conveyor_stop = False
        self.__class__.instances.append(self)

    def connect(self, _connection: object) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.disconnect_count += 1
        self.connected = False

    def read_many(self, tags: tuple[object, ...]) -> dict[str, object]:
        if not self.connected:
            raise AssertionError("PLC read occurred while disconnected")
        self.read_times.append(time.monotonic())
        if self.fail_next_read:
            self.fail_next_read = False
            raise RuntimeError("injected transport failure")

        part = self.values["simulated_photoeye"] is True
        extended = self.values["simulated_pusher_extended"] is True
        if part:
            self.values["conveyor_running"] = False
            self.values["pusher_extend"] = not extended
            self.photoeye_true_cycles += 1
        else:
            self.values["conveyor_running"] = True
            self.values["pusher_extend"] = False
        if self.force_conveyor_stop:
            self.values["conveyor_running"] = False
        if self.values["pusher_extend"] is True:
            self.pusher_command_cycles += 1
        if not self.freeze_echo:
            self.values["plc_heartbeat_echo"] = (
                self.values["pc_heartbeat"]
            )
        return {tag.name: self.values[tag.name] for tag in tags}

    def write_many(
        self,
        values: list[tuple[object, object]],
    ) -> None:
        if not self.connected:
            raise AssertionError("PLC write occurred while disconnected")
        for tag, value in values:
            self.values[tag.name] = value
            self.writes.append((tag.name, value))


class SlowOnceTransport(LadderTransport):
    """Inject one 90 ms exchange to prove missed slots are skipped."""

    instances: list["SlowOnceTransport"] = []

    def read_many(self, tags: tuple[object, ...]) -> dict[str, object]:
        if len(self.read_times) == 3:
            time.sleep(0.09)
        return super().read_many(tags)


class BlockingConnectTransport(LadderTransport):
    """Hold connect so shutdown ownership can be observed deterministically."""

    instances: list["BlockingConnectTransport"] = []
    started = False
    release = False

    def connect(self, _connection: object) -> None:
        self.__class__.started = True
        deadline = time.monotonic() + 2.0
        while (
            not self.__class__.release
            and time.monotonic() < deadline
        ):
            time.sleep(0.005)
        self.connected = True


class FakeSocket:
    def __init__(self) -> None:
        self.timeout: float | None = None

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout


class FakeRawConnection:
    def __init__(self) -> None:
        self.timeout = 5.0
        self.socket = FakeSocket()


class TimeoutAwareClient:
    def __init__(self) -> None:
        self.parameters: list[tuple[object, int]] = []
        self.connection = FakeRawConnection()
        self.connected = False

    def set_param(self, parameter: object, value: int) -> None:
        self.parameters.append((parameter, value))

    def connect(self, _ip: str, _rack: int, _slot: int) -> None:
        self.connected = True

    def get_connected(self) -> bool:
        return self.connected

    def disconnect(self) -> None:
        self.connected = False


def wait_until(
    predicate: Callable[[], bool],
    *,
    timeout_s: float = 2.0,
) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("condition did not become true before timeout")


class NativeCycleCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        LadderTransport.instances.clear()
        config = load_config(PROFILE_FILE)
        self.transport = LadderTransport()
        self.runtime = InterfaceRuntime(
            config,
            self.transport,
            start_time=0.0,
        )
        self.runtime.connect()
        self.core = Scene2CycleCore(
            load_scene2_definition(SCENE_FILE),
            SimulationUpdateLoop(self.runtime),
            exchange_s=config.connection.cycle_ms / 1_000,
        )

    def tearDown(self) -> None:
        self.runtime.close()

    def test_photoeye_reaches_plc_and_plc_command_moves_pusher(self) -> None:
        latest = None
        for cycle in range(220):
            latest = self.core.step(
                cycle * 0.02,
                running=True,
            )
            if latest.model.completed_count >= 1:
                break

        self.assertIsNotNone(latest)
        assert latest is not None
        self.assertGreaterEqual(
            self.transport.photoeye_true_cycles,
            5,
            "part_at_pusher must remain visible to the PLC for at least "
            "five 20 ms exchanges",
        )
        self.assertGreater(
            self.transport.pusher_command_cycles,
            0,
            "the PLC pusher_extend output must feed the plant model",
        )
        self.assertGreaterEqual(latest.model.completed_count, 1)
        self.assertIn(
            ("simulated_photoeye", True),
            self.transport.writes,
        )

    def test_simulator_run_does_not_bypass_false_plc_conveyor_command(self) -> None:
        self.transport.force_conveyor_stop = True
        latest = None
        for cycle in range(50):
            latest = self.core.step(cycle * 0.02, running=True)

        self.assertIsNotNone(latest)
        assert latest is not None
        self.assertFalse(latest.model.motor_running)
        self.assertEqual(latest.model.completed_count, 0)
        self.assertEqual(latest.model.object_leading_edge_m, 0.0)

    def test_not_ready_forces_commands_safe_without_disconnect(self) -> None:
        for cycle in range(10):
            self.core.step(cycle * 0.02, running=True)
        self.transport.values["simulation_comm_ok"] = False
        result = self.core.step(0.22, running=True)
        next_result = self.core.step(0.24, running=True)

        self.assertFalse(result.ready)
        self.assertFalse(next_result.model.motor_running)
        self.assertTrue(self.transport.connected)
        self.assertEqual(self.transport.disconnect_count, 0)

    def test_unrelated_changing_echo_does_not_prove_heartbeat_health(self) -> None:
        self.transport.freeze_echo = True

        first = self.runtime.cycle(0.0)
        self.assertFalse(first.heartbeat.healthy)
        self.assertEqual(first.heartbeat.reason, "waiting_for_matching_echo")

        self.transport.values["plc_heartbeat_echo"] = 900
        second = self.runtime.cycle(0.02)
        self.assertFalse(second.heartbeat.healthy)
        self.assertEqual(second.heartbeat.reason, "waiting_for_matching_echo")

        expected = self.transport.values["pc_heartbeat"]
        self.transport.values["plc_heartbeat_echo"] = expected
        acknowledged = self.runtime.cycle(0.04)
        self.assertTrue(acknowledged.heartbeat.healthy)
        self.assertEqual(
            acknowledged.heartbeat.reason,
            "heartbeat_acknowledged",
        )


class NativeProfileTests(unittest.TestCase):
    def test_status_tag_with_write_direction_is_rejected(self) -> None:
        document = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        status_tag = next(
            tag
            for tag in document["tags"]
            if tag["name"] == "simulation_comm_ok"
        )
        status_tag["direction"] = "pc_to_plc"
        status_tag["safe_value"] = False

        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / PROFILE_FILE.name
            path.write_text(json.dumps(document), encoding="utf-8")
            config = load_config(path)
            with self.assertRaisesRegex(
                NativeRuntimeError,
                "plc_to_pc BOOL",
            ):
                validate_native_profile(config)

    def test_extra_write_or_remapped_address_is_rejected(self) -> None:
        source = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        extra = json.loads(json.dumps(source))
        extra["tags"].append(
            {
                "name": "unexpected_write",
                "plc_symbol": "DB_SimulationProof.Unexpected",
                "address": "DB14.DBX0.3",
                "data_type": "BOOL",
                "direction": "pc_to_plc",
                "safe_value": False,
            }
        )
        remapped = json.loads(json.dumps(source))
        next(
            tag
            for tag in remapped["tags"]
            if tag["name"] == "simulated_photoeye"
        )["address"] = "DB14.DBX0.3"

        for document, expected in (
            (extra, "exact DB14 tag contract"),
            (remapped, "DB14.DBX0.0"),
        ):
            with self.subTest(expected=expected):
                with TemporaryDirectory() as temp_dir:
                    path = Path(temp_dir) / PROFILE_FILE.name
                    path.write_text(
                        json.dumps(document),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        NativeRuntimeError,
                        expected,
                    ):
                        validate_native_profile(load_config(path))

    def test_snap7_operation_timeout_is_configured(self) -> None:
        client = TimeoutAwareClient()
        transport = Snap7Transport(client_factory=lambda: client)
        connection = load_config(PROFILE_FILE).connection

        transport.connect(connection)

        self.assertEqual(len(client.parameters), 3)
        self.assertEqual(
            {value for _parameter, value in client.parameters},
            {connection.connect_timeout_ms},
        )
        self.assertEqual(
            client.connection.timeout,
            connection.connect_timeout_ms / 1_000,
        )
        self.assertEqual(
            client.connection.socket.timeout,
            connection.connect_timeout_ms / 1_000,
        )
        transport.disconnect()

    def test_behavior_changing_profile_values_are_rejected(self) -> None:
        source = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        inverted = json.loads(json.dumps(source))
        inverted["points"][0]["inverted"] = True
        slow_cycle = json.loads(json.dumps(source))
        slow_cycle["connection"]["cycle_ms"] = 250
        slow_heartbeat = json.loads(json.dumps(source))
        slow_heartbeat["heartbeat"]["timeout_ms"] = 2000

        for document, expected in (
            (inverted, "non-inverted"),
            (slow_cycle, "20 ms cycle"),
            (slow_heartbeat, "1000 ms timeout"),
        ):
            with self.subTest(expected=expected):
                with TemporaryDirectory() as temp_dir:
                    path = Path(temp_dir) / PROFILE_FILE.name
                    path.write_text(
                        json.dumps(document),
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(
                        NativeRuntimeError,
                        expected,
                    ):
                        validate_native_profile(load_config(path))

    def test_overrun_deadline_skips_missed_slots(self) -> None:
        self.assertAlmostEqual(
            next_cycle_deadline(1.0, 1.09, 0.02),
            1.11,
        )
        self.assertAlmostEqual(
            next_cycle_deadline(1.0, 1.01, 0.02),
            1.02,
        )


class NativeSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        LadderTransport.instances.clear()
        self.session = NativePlcSession(
            transport_factory=LadderTransport,
        )

    def tearDown(self) -> None:
        self.session.close()

    def test_stop_and_reset_preserve_connection_until_disconnect(self) -> None:
        self.session.connect()
        wait_until(
            lambda: (
                self.session.snapshot().connection
                is ConnectionState.CONNECTED
            )
        )
        wait_until(lambda: self.session.snapshot().ready)
        self.session.run()
        wait_until(lambda: self.session.snapshot().cycle >= 5)
        cycle_before_stop = self.session.snapshot().cycle

        self.session.stop()
        wait_until(
            lambda: self.session.snapshot().cycle > cycle_before_stop
        )
        stopped = self.session.snapshot()
        self.assertEqual(stopped.connection, ConnectionState.CONNECTED)
        self.assertFalse(stopped.running)
        self.assertTrue(LadderTransport.instances[-1].connected)

        cycle_before_reset = stopped.cycle
        self.session.reset()
        wait_until(
            lambda: self.session.snapshot().cycle > cycle_before_reset
        )
        reset = self.session.snapshot()
        self.assertEqual(reset.connection, ConnectionState.CONNECTED)
        self.assertEqual(reset.scene_time_s, 0.0)
        self.assertTrue(LadderTransport.instances[-1].connected)

        self.session.disconnect()
        closing = self.session.snapshot()
        self.assertEqual(closing.connection, ConnectionState.CLOSING)
        self.assertEqual(closing.health, "closing")
        self.assertIsNone(closing.simulation_comm_ok)
        self.assertIsNone(closing.simulation_timeout)
        self.assertIsNone(closing.points["conveyor_running"])
        self.assertIsNone(closing.points["pusher_extend"])
        prior = reset
        late_cycle = SimpleNamespace(
            ready=True,
            scene_time_s=prior.scene_time_s,
            model=prior.model,
            point_values=dict(prior.points),
            update=SimpleNamespace(
                health=SimpleNamespace(value="healthy"),
                cycle=SimpleNamespace(
                    cycle_number=prior.cycle + 1,
                    heartbeat=SimpleNamespace(
                        reason="heartbeat_acknowledged",
                        last_echo=prior.heartbeat_echo,
                    ),
                    plc_values_read={
                        "simulation_enable": True,
                        "simulation_comm_ok": True,
                        "simulation_timeout": False,
                    },
                ),
            ),
        )
        self.session._publish_cycle(
            late_cycle,
            duration_ms=1.0,
            recent_p99_ms=1.0,
        )
        self.assertEqual(
            self.session.snapshot().connection,
            ConnectionState.CLOSING,
        )
        wait_until(
            lambda: (
                self.session.snapshot().connection
                is ConnectionState.DISCONNECTED
            )
        )
        disconnected = self.session.snapshot()
        self.assertEqual(disconnected.health, "disconnected")
        self.assertEqual(disconnected.heartbeat_reason, "not connected")
        self.assertIsNone(disconnected.heartbeat_echo)
        self.assertIsNone(disconnected.simulation_enable)
        self.assertIsNone(disconnected.simulation_comm_ok)
        self.assertIsNone(disconnected.simulation_timeout)
        self.assertIsNone(disconnected.points["conveyor_running"])
        self.assertIsNone(disconnected.points["pusher_extend"])
        self.assertFalse(LadderTransport.instances[-1].connected)
        self.assertEqual(
            LadderTransport.instances[-1].disconnect_count,
            1,
        )

    def test_step_advances_one_exchange_without_starting_continuous_run(
        self,
    ) -> None:
        self.session.connect()
        wait_until(lambda: self.session.snapshot().ready)
        before = self.session.snapshot()

        self.session.step()
        wait_until(
            lambda: (
                self.session.snapshot().scene_time_s
                > before.scene_time_s
            )
        )
        stepped = self.session.snapshot()

        self.assertAlmostEqual(
            stepped.scene_time_s - before.scene_time_s,
            self.session.config.connection.cycle_ms / 1_000,
            places=6,
        )
        self.assertFalse(stepped.running)
        time.sleep(self.session.config.connection.cycle_ms / 500)
        self.assertAlmostEqual(
            self.session.snapshot().scene_time_s,
            stepped.scene_time_s,
            places=6,
        )

    def test_native_runtime_contains_no_browser_or_http_server(self) -> None:
        source = (
            Path(__file__).resolve().parent / "native_runtime.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "http.server",
            "webbrowser",
            "selenium",
            "playwright",
            "QtWebEngine",
        ):
            self.assertNotIn(forbidden, source)

    def test_readiness_loss_requires_a_fresh_run_after_recovery(self) -> None:
        self.session.connect()
        wait_until(lambda: self.session.snapshot().ready)
        transport = LadderTransport.instances[-1]

        unsafe_states = (
            ("simulation_enable", False),
            ("simulation_comm_ok", False),
            ("simulation_timeout", True),
        )
        for name, unsafe_value in unsafe_states:
            with self.subTest(status=name):
                self.session.run()
                wait_until(lambda: self.session.snapshot().running)
                transport.values[name] = unsafe_value
                wait_until(
                    lambda: (
                        not self.session.snapshot().ready
                        and not self.session.snapshot().running
                    )
                )
                with self.assertRaisesRegex(
                    NativeRuntimeError,
                    "safely ready",
                ):
                    self.session.run()
                stopped_time = self.session.snapshot().scene_time_s
                transport.values[name] = not unsafe_value
                wait_until(lambda: self.session.snapshot().ready)
                time.sleep(0.06)
                recovered = self.session.snapshot()
                self.assertFalse(recovered.running)
                self.assertAlmostEqual(
                    recovered.scene_time_s,
                    stopped_time,
                    places=6,
                )

        self.session.run()
        wait_until(lambda: self.session.snapshot().running)
        transport.freeze_echo = True
        wait_until(
            lambda: (
                self.session.snapshot().health == "fault"
                and not self.session.snapshot().running
            ),
            timeout_s=2.0,
        )
        stopped_time = self.session.snapshot().scene_time_s
        transport.freeze_echo = False
        wait_until(lambda: self.session.snapshot().ready)
        time.sleep(0.06)
        recovered = self.session.snapshot()
        self.assertFalse(recovered.running)
        self.assertAlmostEqual(
            recovered.scene_time_s,
            stopped_time,
            places=6,
        )

    def test_transport_reconnect_requires_a_fresh_run(self) -> None:
        self.session.connect()
        wait_until(lambda: self.session.snapshot().ready)
        self.session.run()
        wait_until(lambda: self.session.snapshot().running)
        first = LadderTransport.instances[-1]
        first.fail_next_read = True

        wait_until(lambda: len(LadderTransport.instances) >= 2)
        wait_until(lambda: self.session.snapshot().ready)

        self.assertFalse(self.session.snapshot().running)
        self.assertFalse(first.connected)
        self.assertTrue(LadderTransport.instances[-1].connected)

    def test_transport_reconnect_preserves_plant_state(self) -> None:
        self.session.connect()
        wait_until(lambda: self.session.snapshot().ready)
        self.session.run()
        wait_until(lambda: self.session.snapshot().scene_time_s >= 0.14)
        self.session.stop()
        wait_until(lambda: not self.session.snapshot().running)
        before = self.session.snapshot()
        assert before.model is not None
        self.assertGreater(before.model.object_leading_edge_m or 0.0, 0.0)

        first = LadderTransport.instances[-1]
        first.fail_next_read = True
        wait_until(lambda: len(LadderTransport.instances) >= 2)
        wait_until(
            lambda: (
                self.session.snapshot().connection
                is ConnectionState.CONNECTED
                and self.session.snapshot().ready
            )
        )
        after = self.session.snapshot()
        assert after.model is not None

        self.assertFalse(after.running)
        self.assertAlmostEqual(after.scene_time_s, before.scene_time_s)
        self.assertAlmostEqual(
            after.model.object_leading_edge_m or 0.0,
            before.model.object_leading_edge_m or 0.0,
        )

    def test_worker_skips_catch_up_bursts_after_slow_exchange(self) -> None:
        self.session.close()
        SlowOnceTransport.instances.clear()
        self.session = NativePlcSession(
            transport_factory=SlowOnceTransport,
        )
        self.session.connect()
        wait_until(
            lambda: (
                SlowOnceTransport.instances
                and len(SlowOnceTransport.instances[-1].read_times) >= 9
            )
        )
        timestamps = SlowOnceTransport.instances[-1].read_times
        intervals = [
            right - left
            for left, right in zip(timestamps, timestamps[1:])
        ]
        slow_index = next(
            index
            for index, interval in enumerate(intervals)
            if interval > 0.07
        )
        after_slow = intervals[slow_index + 1:slow_index + 3]
        self.assertEqual(len(after_slow), 2)
        self.assertGreaterEqual(
            min(after_slow),
            0.012,
            f"catch-up burst intervals observed: {intervals}",
        )

    def test_begin_close_reports_worker_until_transport_returns(self) -> None:
        self.session.close()
        BlockingConnectTransport.instances.clear()
        BlockingConnectTransport.started = False
        BlockingConnectTransport.release = False
        self.session = NativePlcSession(
            transport_factory=BlockingConnectTransport,
        )
        self.session.connect()
        wait_until(lambda: BlockingConnectTransport.started)

        self.session.begin_close()
        time.sleep(0.05)
        self.assertFalse(self.session.is_closed)

        BlockingConnectTransport.release = True
        wait_until(lambda: self.session.is_closed)


if __name__ == "__main__":
    unittest.main()
