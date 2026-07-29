"""Tests for renderer-neutral graphical scene projection."""

from __future__ import annotations

import unittest
from pathlib import Path

from siemens_plc_pc_interface.config import load_config, parse_config
from siemens_plc_pc_interface.runtime import InterfaceRuntime
from siemens_plc_pc_interface.scene import (
    SceneCycleReport,
    SceneEngine,
    TimingSnapshot,
)
from siemens_plc_pc_interface.scene_config import (
    load_scene_config,
    parse_scene_config,
)
from siemens_plc_pc_interface.update_loop import SimulationUpdateLoop
from siemens_plc_pc_interface.visualizer import (
    project_conveyor_pushers,
    project_conveyors,
)
from test_runtime import FakeTransport, initial_plc_values
from test_scene_config import valid_scene, valid_scene_interface


class VisualProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.interface = parse_config(valid_scene_interface())
        self.scene = parse_scene_config(valid_scene(), self.interface)
        transport = FakeTransport(initial_plc_values())
        runtime = InterfaceRuntime(
            self.interface,
            transport,
            start_time=0.0,
        )
        runtime.connect()
        self.engine = SceneEngine(
            self.scene,
            SimulationUpdateLoop(runtime),
        )

    def _report(self) -> SceneCycleReport:
        return SceneCycleReport(
            snapshot=self.engine.step(0.0),
            cycle_duration_ms=3.0,
            deadline_overrun=False,
            timing=TimingSnapshot(
                cycles=1,
                deadline_overruns=0,
                schedule_resyncs=0,
                average_ms=3.0,
                maximum_ms=3.0,
                p99_ms=3.0,
            ),
        )

    def test_new_product_is_projected_partly_outside_the_infeed(self) -> None:
        state = project_conveyors(self.scene, self._report())[0]

        self.assertEqual(state.component_id, "conveyor_1")
        self.assertTrue(state.object_present)
        self.assertEqual(state.object_leading_fraction, 0.0)
        self.assertAlmostEqual(state.object_trailing_fraction, -0.2)
        self.assertAlmostEqual(state.photoeye_fraction, 0.5)

    def test_projection_uses_authoritative_component_state(self) -> None:
        state = project_conveyors(self.scene, self._report())[0]

        self.assertEqual(state.state, "stopped_loaded")
        self.assertFalse(state.motor_running)
        self.assertFalse(state.photoeye_blocked)
        self.assertEqual(state.completed_count, 0)


class ConveyorPusherVisualProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        examples = Path(__file__).resolve().parents[1] / "examples"
        self.interface = load_config(
            examples / "scene-2-db14-pusher-interface.json"
        )
        self.scene = load_scene_config(
            examples / "scene-2-conveyor-pusher.json",
            self.interface,
        )
        transport = FakeTransport(
            {
                "conveyor_running": False,
                "pusher_extend": False,
                "plc_heartbeat_echo": 0,
                "simulation_enable": True,
                "simulation_comm_ok": False,
                "simulation_timeout": True,
            }
        )
        runtime = InterfaceRuntime(
            self.interface,
            transport,
            start_time=0.0,
        )
        runtime.connect()
        self.engine = SceneEngine(
            self.scene,
            SimulationUpdateLoop(runtime),
        )

    def _report(self) -> SceneCycleReport:
        return SceneCycleReport(
            snapshot=self.engine.step(0.0),
            cycle_duration_ms=3.0,
            deadline_overrun=False,
            timing=TimingSnapshot(
                cycles=1,
                deadline_overruns=0,
                schedule_resyncs=0,
                average_ms=3.0,
                maximum_ms=3.0,
                p99_ms=3.0,
            ),
        )

    def test_pusher_projection_includes_retracted_limit(self) -> None:
        states = project_conveyor_pushers(self.scene, self._report())

        self.assertEqual(len(states), 1)
        state = states[0]
        self.assertEqual(state.component_id, "conveyor_pusher_1")
        self.assertEqual(state.pusher_position, 0.0)
        self.assertTrue(state.pusher_retracted)
        self.assertFalse(state.pusher_extended)
        self.assertFalse(state.pusher_extending)

    def test_pusher_scene_is_not_projected_as_basic_conveyor(self) -> None:
        self.assertEqual(project_conveyors(self.scene, self._report()), ())


if __name__ == "__main__":
    unittest.main()
