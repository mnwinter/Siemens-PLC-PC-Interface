"""Unit tests for heartbeat generation and timeout behavior."""

from __future__ import annotations

import unittest

from siemens_plc_pc_interface.heartbeat import (
    HeartbeatCounter,
    HeartbeatMonitor,
)


class HeartbeatCounterTests(unittest.TestCase):
    def test_counter_increments(self) -> None:
        counter = HeartbeatCounter()

        self.assertEqual(counter.next(), 1)
        self.assertEqual(counter.next(), 2)

    def test_counter_rolls_to_one_at_dint_maximum(self) -> None:
        counter = HeartbeatCounter(2_147_483_647)

        self.assertEqual(counter.next(), 1)

    def test_counter_rejects_out_of_range_initial_value(self) -> None:
        with self.assertRaises(ValueError):
            HeartbeatCounter(-1)


class HeartbeatMonitorTests(unittest.TestCase):
    def test_monitor_waits_for_first_echo(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)

        status = monitor.status(0.5)

        self.assertFalse(status.healthy)
        self.assertEqual(status.reason, "waiting_for_first_echo")
        self.assertIsNone(status.last_echo)
        self.assertEqual(status.age_ms, 500)

    def test_first_echo_becomes_healthy(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)

        status = monitor.observe(echo=0, now=0.1)

        self.assertTrue(status.healthy)
        self.assertEqual(status.reason, "echo_progressing")
        self.assertEqual(status.last_echo, 0)
        self.assertEqual(status.age_ms, 0)

    def test_unchanged_echo_times_out(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)
        monitor.observe(echo=10, now=0.0)

        healthy = monitor.status(1.0)
        timed_out = monitor.status(1.001)

        self.assertTrue(healthy.healthy)
        self.assertFalse(timed_out.healthy)
        self.assertEqual(timed_out.reason, "echo_stalled")
        self.assertEqual(timed_out.last_echo, 10)

    def test_changed_echo_resets_timeout(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)
        monitor.observe(echo=10, now=0.0)
        monitor.observe(echo=11, now=0.9)

        status = monitor.status(1.8)

        self.assertTrue(status.healthy)
        self.assertEqual(status.age_ms, 900)

    def test_time_cannot_move_backwards(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)
        monitor.observe(echo=10, now=1.0)

        with self.assertRaisesRegex(ValueError, "backwards"):
            monitor.status(0.9)

    def test_echo_must_fit_dint(self) -> None:
        monitor = HeartbeatMonitor(timeout_ms=1_000)

        with self.assertRaisesRegex(ValueError, "DINT"):
            monitor.observe(echo=2_147_483_648, now=0.0)


if __name__ == "__main__":
    unittest.main()
