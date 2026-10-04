"""Pure-Python checks for the deterministic PLC-free Review Player runtime."""

from __future__ import annotations

import unittest

from tools.native_draft_runtime import DraftRuntimeError, NativeDraftReviewRuntime


SCENARIO = {
    "sequence": [
        {"id": "ready", "label": "Ready / safe state"},
        {"id": "cycle", "label": "Local cycle / asset outputs active"},
        {"id": "complete", "label": "Cycle complete / reset required"},
    ],
    "alarm": {
        "id": "review_interlock",
        "message": "Review interlock raised locally; acknowledge before clear.",
    },
}


class NativeDraftRuntimeTests(unittest.TestCase):
    def test_run_advances_to_deterministic_complete_state(self) -> None:
        runtime = NativeDraftReviewRuntime(SCENARIO)
        self.assertEqual(runtime.snapshot().state, "ready")
        self.assertTrue(runtime.run().cycle_active)
        runtime.advance()
        snapshot = runtime.advance()
        self.assertTrue(snapshot.cycle_complete)
        self.assertTrue(snapshot.points["review_cycle_complete"])

    def test_stop_and_reset_are_safe_and_reproducible(self) -> None:
        runtime = NativeDraftReviewRuntime(SCENARIO)
        runtime.run()
        stopped = runtime.stop()
        self.assertFalse(stopped.cycle_active)
        self.assertEqual(runtime.reset().state, "ready")
        self.assertEqual(runtime.snapshot().points["review_run"], False)

    def test_alarm_requires_acknowledge_before_clear(self) -> None:
        runtime = NativeDraftReviewRuntime(SCENARIO)
        self.assertTrue(runtime.raise_fault().fault_active)
        self.assertTrue(runtime.clear_fault().fault_active)
        self.assertTrue(runtime.acknowledge_fault().fault_acknowledged)
        self.assertFalse(runtime.clear_fault().fault_active)
        self.assertEqual(runtime.snapshot().state, "ready")

    def test_missing_scenario_fails_closed(self) -> None:
        with self.assertRaises(DraftRuntimeError):
            NativeDraftReviewRuntime({})


if __name__ == "__main__":
    unittest.main()
