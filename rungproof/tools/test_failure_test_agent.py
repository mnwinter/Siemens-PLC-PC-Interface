from __future__ import annotations

import unittest

from tools.failure_test_agent import run_failure_tests


class FailureTestAgentTests(unittest.TestCase):
    def test_failure_cases_fail_closed_or_pass_through_safely(self) -> None:
        results = run_failure_tests()
        self.assertEqual(
            [result.case for result in results],
            [
                "profile_missing_photoeye",
                "normal_sequence",
                "photoeye_stuck_low",
                "photoeye_stuck_high",
                "conveyor_output_missing",
                "pusher_without_part",
                "both_outputs",
                "conveyor_stopped",
                "ladder_missing_pusher_command",
            ],
        )
        missing_pusher = next(
            result
            for result in results
            if result.case == "ladder_missing_pusher_command"
        )
        self.assertFalse(missing_pusher.passed)
        self.assertIn("no pusher-extension rung", missing_pusher.detail)


if __name__ == "__main__":
    unittest.main()
