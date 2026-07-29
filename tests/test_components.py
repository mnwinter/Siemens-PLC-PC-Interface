"""Unit tests for reusable offline equipment components."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.components import (
    ComponentError,
    ConveyorInputs,
    ConveyorPhotoeye,
    ConveyorPhotoeyeConfig,
    ConveyorPointBinding,
    ConveyorPusher,
    ConveyorPusherConfig,
    ConveyorPusherInputs,
    ConveyorPusherPointBinding,
    ConveyorPusherState,
    ConveyorState,
)
from siemens_plc_pc_interface.heartbeat import HeartbeatStatus
from siemens_plc_pc_interface.points import PointQuality, PointSample
from siemens_plc_pc_interface.runtime import CycleResult
from siemens_plc_pc_interface.update_loop import LoopHealth, UpdateResult


def conveyor_config(**overrides: float) -> ConveyorPhotoeyeConfig:
    values = {
        "length_m": 1.0,
        "speed_m_per_s": 0.5,
        "object_length_m": 0.2,
        "photoeye_position_m": 0.5,
        "minimum_photoeye_on_s": 0.1,
    }
    values.update(overrides)
    return ConveyorPhotoeyeConfig(**values)


def update_result(
    *,
    health: LoopHealth,
    command: bool | float = True,
    extend_command: bool | float = True,
    quality: PointQuality = PointQuality.GOOD,
) -> UpdateResult:
    heartbeat_healthy = health in (
        LoopHealth.HEALTHY,
        LoopHealth.DEGRADED,
    )
    heartbeat = HeartbeatStatus(
        healthy=heartbeat_healthy,
        reason=(
            "echo_progressing"
            if heartbeat_healthy
            else "waiting_for_first_echo"
        ),
        last_echo=1 if heartbeat_healthy else None,
        age_ms=0,
    )
    cycle = CycleResult(
        cycle_number=1,
        pc_values_written={},
        plc_values_read={},
        heartbeat=heartbeat,
    )
    command_sample = PointSample(
        point_name="conveyor_running",
        tag_name="conveyor_running_raw",
        value=command,
        raw_value=command,
        quality=quality,
        unit=None,
    )
    extend_sample = PointSample(
        point_name="pusher_extend",
        tag_name="pusher_extend_raw",
        value=extend_command,
        raw_value=extend_command,
        quality=quality,
        unit=None,
    )
    return UpdateResult(
        cycle=cycle,
        health=health,
        pc_point_samples={},
        plc_point_samples={
            "conveyor_running": command_sample,
            "pusher_extend": extend_sample,
        },
        diagnostics=(),
    )


class ConveyorPhotoeyeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.conveyor = ConveyorPhotoeye(conveyor_config())

    def test_config_rejects_impossible_physical_values(self) -> None:
        invalid = (
            {"length_m": 0.0},
            {"speed_m_per_s": -1.0},
            {"object_length_m": 1.1},
            {"photoeye_position_m": 1.1},
            {"minimum_photoeye_on_s": -0.1},
            {"speed_m_per_s": float("inf")},
        )

        for override in invalid:
            with self.subTest(override=override):
                with self.assertRaises(ComponentError):
                    conveyor_config(**override)

    def test_loaded_object_is_stopped_at_the_infeed(self) -> None:
        snapshot = self.conveyor.load_object()

        self.assertIs(snapshot.state, ConveyorState.STOPPED_LOADED)
        self.assertFalse(snapshot.motor_running)
        self.assertTrue(snapshot.object_present)
        self.assertEqual(snapshot.object_leading_edge_m, 0.0)
        self.assertFalse(snapshot.photoeye_blocked)

    def test_run_command_moves_object_into_photoeye(self) -> None:
        self.conveyor.load_object()
        first = self.conveyor.step(
            0.5,
            ConveyorInputs(run_command=True),
        )
        second = self.conveyor.step(
            0.5,
            ConveyorInputs(run_command=True),
        )

        self.assertIs(first.state, ConveyorState.RUNNING_LOADED)
        self.assertEqual(first.object_leading_edge_m, 0.25)
        self.assertFalse(first.photoeye_blocked)
        self.assertEqual(second.object_leading_edge_m, 0.5)
        self.assertTrue(second.photoeye_blocked)

    def test_stop_freezes_position_and_keeps_physical_sensor(self) -> None:
        self.conveyor.load_object()
        moving = self.conveyor.step(
            1.0,
            ConveyorInputs(run_command=True),
        )
        stopped = self.conveyor.step(
            2.0,
            ConveyorInputs(run_command=False),
        )

        self.assertEqual(stopped.object_leading_edge_m, 0.5)
        self.assertEqual(
            stopped.object_leading_edge_m,
            moving.object_leading_edge_m,
        )
        self.assertIs(stopped.state, ConveyorState.STOPPED_LOADED)
        self.assertTrue(stopped.photoeye_blocked)

    def test_minimum_on_time_captures_sensor_crossing(self) -> None:
        conveyor = ConveyorPhotoeye(
            conveyor_config(
                length_m=2.0,
                speed_m_per_s=1.0,
            )
        )
        conveyor.load_object()

        crossed = conveyor.step(
            1.0,
            ConveyorInputs(run_command=True),
        )
        cleared = conveyor.step(
            0.1,
            ConveyorInputs(run_command=False),
        )

        self.assertEqual(crossed.object_leading_edge_m, 1.0)
        self.assertTrue(crossed.photoeye_blocked)
        self.assertFalse(cleared.photoeye_blocked)

    def test_discharge_is_one_cycle_event_and_increments_count(self) -> None:
        conveyor = ConveyorPhotoeye(
            conveyor_config(speed_m_per_s=1.0)
        )
        conveyor.load_object()

        discharged = conveyor.step(
            1.2,
            ConveyorInputs(run_command=True),
        )
        next_cycle = conveyor.step(
            0.1,
            ConveyorInputs(run_command=True),
        )

        self.assertTrue(discharged.object_discharged)
        self.assertFalse(discharged.object_present)
        self.assertEqual(discharged.completed_count, 1)
        self.assertIs(discharged.state, ConveyorState.RUNNING_EMPTY)
        self.assertFalse(next_cycle.object_discharged)
        self.assertEqual(next_cycle.completed_count, 1)

    def test_reset_overrides_run_and_returns_safe_empty_state(self) -> None:
        self.conveyor.load_object()
        self.conveyor.step(1.0, ConveyorInputs(run_command=True))

        reset = self.conveyor.step(
            0.1,
            ConveyorInputs(run_command=True, reset_scene=True),
        )
        idle = self.conveyor.step(
            0.0,
            ConveyorInputs(run_command=False),
        )

        self.assertIs(reset.state, ConveyorState.RESET)
        self.assertFalse(reset.motor_running)
        self.assertFalse(reset.object_present)
        self.assertFalse(reset.photoeye_blocked)
        self.assertEqual(reset.completed_count, 0)
        self.assertIs(idle.state, ConveyorState.STOPPED_EMPTY)

    def test_invalid_time_and_input_type_are_rejected(self) -> None:
        with self.assertRaisesRegex(ComponentError, "non-negative"):
            self.conveyor.step(
                -0.1,
                ConveyorInputs(run_command=False),
            )
        with self.assertRaisesRegex(ComponentError, "finite"):
            self.conveyor.step(
                float("nan"),
                ConveyorInputs(run_command=False),
            )
        with self.assertRaisesRegex(ComponentError, "ConveyorInputs"):
            self.conveyor.step(0.1, object())  # type: ignore[arg-type]

    def test_second_object_cannot_overlap_first(self) -> None:
        self.conveyor.load_object()

        with self.assertRaisesRegex(ComponentError, "another object"):
            self.conveyor.load_object()


class ConveyorPointBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.binding = ConveyorPointBinding(
            run_command_point="conveyor_running",
            photoeye_point="simulated_photoeye",
        )

    def test_healthy_or_degraded_result_can_run_conveyor(self) -> None:
        healthy = self.binding.inputs_from_update(
            update_result(health=LoopHealth.HEALTHY)
        )
        degraded = self.binding.inputs_from_update(
            update_result(health=LoopHealth.DEGRADED)
        )

        self.assertTrue(healthy.run_command)
        self.assertTrue(degraded.run_command)

    def test_starting_fault_or_bad_quality_forces_run_false(self) -> None:
        starting = self.binding.inputs_from_update(
            update_result(health=LoopHealth.STARTING)
        )
        fault = self.binding.inputs_from_update(
            update_result(health=LoopHealth.FAULT)
        )
        bad_quality = self.binding.inputs_from_update(
            update_result(
                health=LoopHealth.HEALTHY,
                quality=PointQuality.FAULT_HIGH,
            )
        )

        self.assertFalse(starting.run_command)
        self.assertFalse(fault.run_command)
        self.assertFalse(bad_quality.run_command)

    def test_binding_rejects_missing_or_non_boolean_command(self) -> None:
        missing = update_result(health=LoopHealth.HEALTHY)
        missing.plc_point_samples.clear()

        with self.assertRaisesRegex(ComponentError, "missing"):
            self.binding.inputs_from_update(missing)
        with self.assertRaisesRegex(ComponentError, "Boolean"):
            self.binding.inputs_from_update(
                update_result(
                    health=LoopHealth.HEALTHY,
                    command=1.0,
                )
            )

    def test_snapshot_maps_to_pc_owned_photoeye_point(self) -> None:
        conveyor = ConveyorPhotoeye(conveyor_config())
        conveyor.load_object()
        snapshot = conveyor.step(
            1.0,
            ConveyorInputs(run_command=True),
        )

        values = self.binding.pc_point_values(snapshot)

        self.assertEqual(values, {"simulated_photoeye": True})

    def test_binding_requires_distinct_nonempty_point_names(self) -> None:
        with self.assertRaises(ComponentError):
            ConveyorPointBinding("", "simulated_photoeye")
        with self.assertRaisesRegex(ComponentError, "different"):
            ConveyorPointBinding("same", "same")


class ConveyorPusherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pusher = ConveyorPusher(
            ConveyorPusherConfig(
                conveyor=conveyor_config(),
                pusher_stroke_time_s=0.3,
                transfer_position_fraction=0.8,
            )
        )

    def test_safe_initial_state_reports_retracted_limit(self) -> None:
        snapshot = self.pusher.snapshot

        self.assertIs(snapshot.state, ConveyorPusherState.STOPPED_EMPTY)
        self.assertTrue(snapshot.pusher_retracted)
        self.assertFalse(snapshot.pusher_extended)
        self.assertEqual(snapshot.pusher_position, 0.0)

    def test_product_is_transferred_when_pusher_crosses_threshold(self) -> None:
        self.pusher.load_object()
        at_sensor = self.pusher.step(
            1.0,
            ConveyorPusherInputs(
                run_command=True,
                extend_command=False,
            ),
        )
        partway = self.pusher.step(
            0.15,
            ConveyorPusherInputs(
                run_command=False,
                extend_command=True,
            ),
        )
        transferred = self.pusher.step(
            0.09,
            ConveyorPusherInputs(
                run_command=False,
                extend_command=True,
            ),
        )

        self.assertTrue(at_sensor.photoeye_blocked)
        self.assertAlmostEqual(partway.pusher_position, 0.5)
        self.assertTrue(partway.object_present)
        self.assertTrue(transferred.object_transferred)
        self.assertFalse(transferred.object_present)
        self.assertFalse(transferred.photoeye_blocked)
        self.assertEqual(transferred.completed_count, 1)

    def test_single_solenoid_pusher_retracts_when_command_clears(self) -> None:
        extended = self.pusher.step(
            0.3,
            ConveyorPusherInputs(
                run_command=False,
                extend_command=True,
            ),
        )
        retracted = self.pusher.step(
            0.3,
            ConveyorPusherInputs(
                run_command=False,
                extend_command=False,
            ),
        )

        self.assertTrue(extended.pusher_extended)
        self.assertIs(extended.state, ConveyorPusherState.EXTENDED)
        self.assertTrue(retracted.pusher_retracted)
        self.assertIs(
            retracted.state,
            ConveyorPusherState.STOPPED_EMPTY,
        )

    def test_reset_clears_product_count_and_retracts_pusher(self) -> None:
        self.pusher.load_object()
        self.pusher.step(
            0.3,
            ConveyorPusherInputs(
                run_command=False,
                extend_command=True,
            ),
        )

        reset = self.pusher.step(
            0.01,
            ConveyorPusherInputs(
                run_command=True,
                extend_command=True,
                reset_scene=True,
            ),
        )

        self.assertIs(reset.state, ConveyorPusherState.RESET)
        self.assertFalse(reset.object_present)
        self.assertTrue(reset.pusher_retracted)
        self.assertEqual(reset.completed_count, 0)


class ConveyorPusherPointBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.binding = ConveyorPusherPointBinding(
            run_command_point="conveyor_running",
            extend_command_point="pusher_extend",
            photoeye_point="part_at_pusher",
            extended_sensor_point="pusher_extended",
            retracted_sensor_point="pusher_retracted",
        )

    def test_binding_accepts_two_healthy_boolean_commands(self) -> None:
        inputs = self.binding.inputs_from_update(
            update_result(health=LoopHealth.HEALTHY)
        )

        self.assertTrue(inputs.run_command)
        self.assertTrue(inputs.extend_command)

    def test_binding_forces_both_commands_safe_on_fault(self) -> None:
        inputs = self.binding.inputs_from_update(
            update_result(health=LoopHealth.FAULT)
        )

        self.assertFalse(inputs.run_command)
        self.assertFalse(inputs.extend_command)

    def test_binding_maps_all_three_pc_owned_sensors(self) -> None:
        snapshot = ConveyorPusher(
            ConveyorPusherConfig(
                conveyor=conveyor_config(),
                pusher_stroke_time_s=0.3,
            )
        ).snapshot

        values = self.binding.pc_point_values(snapshot)

        self.assertEqual(
            values,
            {
                "part_at_pusher": False,
                "pusher_extended": False,
                "pusher_retracted": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
