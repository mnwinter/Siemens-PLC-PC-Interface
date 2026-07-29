"""Unit tests for deterministic scene execution and timing."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.config import parse_config
from siemens_plc_pc_interface.runtime import InterfaceRuntime
from siemens_plc_pc_interface.scene import (
    SceneEngine,
    SceneRunner,
    SceneRuntimeError,
)
from siemens_plc_pc_interface.scene_config import parse_scene_config
from siemens_plc_pc_interface.update_loop import (
    LoopHealth,
    SimulationUpdateLoop,
)
from test_runtime import FakeTransport, initial_plc_values
from test_scene_config import valid_scene, valid_scene_interface


class ManualClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleep_calls: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, duration: float) -> None:
        self.sleep_calls.append(duration)
        self.now += duration


class SceneEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = parse_config(valid_scene_interface())
        self.scene = parse_scene_config(valid_scene(), self.interface)
        self.transport = FakeTransport(initial_plc_values())
        self.runtime = InterfaceRuntime(
            self.interface,
            self.transport,
            start_time=0.0,
        )
        self.runtime.connect()
        self.engine = SceneEngine(
            self.scene,
            SimulationUpdateLoop(self.runtime),
        )

    def test_object_loads_at_zero_and_stays_stopped_during_startup(self) -> None:
        result = self.engine.step(0.0)
        conveyor = result.components["conveyor_1"]

        self.assertEqual(result.scene_time_ms, 20)
        self.assertEqual(result.physics_steps, 2)
        self.assertTrue(conveyor.object_present)
        self.assertEqual(conveyor.object_leading_edge_m, 0.0)
        self.assertFalse(conveyor.motor_running)
        self.assertIs(result.update.health, LoopHealth.STARTING)
        self.assertIn(("pc_to_plc", False), self.transport.writes)

    def test_healthy_plc_command_is_applied_on_following_exchange(self) -> None:
        self.engine.step(0.0)
        self.transport.plc_values["plc_heartbeat_echo"] = 1
        self.transport.plc_values["plc_to_pc"] = True

        accepted = self.engine.step(0.02)
        moved = self.engine.step(0.04)

        self.assertIs(accepted.update.health, LoopHealth.HEALTHY)
        self.assertEqual(
            accepted.components["conveyor_1"].object_leading_edge_m,
            0.0,
        )
        self.assertAlmostEqual(
            moved.components["conveyor_1"].object_leading_edge_m,
            0.01,
        )

    def test_overlapping_load_event_fails_with_actionable_context(self) -> None:
        raw = valid_scene()
        raw["events"].append(
            {
                "at_ms": 10,
                "component": "conveyor_1",
                "action": "load_object",
            }
        )
        engine = SceneEngine(
            parse_scene_config(raw, self.interface),
            SimulationUpdateLoop(self.runtime),
        )

        with self.assertRaisesRegex(
            SceneRuntimeError,
            "load_object.*10 ms failed",
        ):
            engine.step(0.0)

    def test_runner_uses_exchange_period_and_reports_bounded_timing(self) -> None:
        clock = ManualClock()
        runner = SceneRunner(
            self.engine,
            clock=clock,
            sleeper=clock.sleep,
        )
        reports = []

        timing = runner.run(cycles=3, on_cycle=reports.append)

        self.assertEqual(timing.cycles, 3)
        self.assertEqual(timing.deadline_overruns, 0)
        self.assertEqual(timing.schedule_resyncs, 0)
        self.assertEqual(clock.sleep_calls, [0.02, 0.02])
        self.assertEqual(len(reports), 3)
        self.assertEqual(timing.p99_ms, 0.0)

    def test_runner_stops_before_the_next_exchange_when_requested(self) -> None:
        clock = ManualClock()
        runner = SceneRunner(
            self.engine,
            clock=clock,
            sleeper=clock.sleep,
        )
        reports = []

        timing = runner.run(
            cycles=None,
            on_cycle=reports.append,
            should_stop=lambda: len(reports) >= 2,
        )

        self.assertEqual(timing.cycles, 2)
        self.assertEqual(len(reports), 2)
        self.assertEqual(clock.sleep_calls, [0.02])

    def test_runner_reports_overrun_and_resynchronizes_large_lag(self) -> None:
        clock = ManualClock()

        class SlowTransport(FakeTransport):
            def read(self, tag: object) -> object:
                value = super().read(tag)
                clock.now += 0.02
                return value

            def write(self, tag: object, value: object) -> None:
                super().write(tag, value)
                clock.now += 0.02

        transport = SlowTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            self.interface,
            transport,
            start_time=0.0,
        )
        runtime.connect()
        engine = SceneEngine(
            self.scene,
            SimulationUpdateLoop(runtime),
        )
        runner = SceneRunner(
            engine,
            clock=clock,
            sleeper=clock.sleep,
        )

        timing = runner.run(cycles=2)

        self.assertEqual(timing.cycles, 2)
        self.assertEqual(timing.deadline_overruns, 2)
        self.assertEqual(timing.schedule_resyncs, 1)
        self.assertGreaterEqual(timing.maximum_ms, 120.0)
        self.assertGreaterEqual(timing.p99_ms, 120.0)


if __name__ == "__main__":
    unittest.main()
