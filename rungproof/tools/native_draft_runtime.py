"""Deterministic, PLC-free runtime for validated static-draft review."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class DraftRuntimeError(ValueError):
    """Raised when a review scenario is missing or unsafe to execute."""


@dataclass(frozen=True)
class ReviewRuntimeSnapshot:
    state: str
    step_index: int
    step_label: str
    cycle_active: bool
    cycle_complete: bool
    fault_active: bool
    fault_acknowledged: bool
    fault_message: str
    points: dict[str, bool]
    notice: str


class NativeDraftReviewRuntime:
    """Small deterministic state machine used only by the Review Player.

    It deliberately has no transport, PLC profile, wall-clock dependency, or
    arbitrary code execution. The UI advances it through explicit ticks so a
    reviewer can reproduce the same Run/Stop/Reset/alarm behavior every time.
    """

    def __init__(self, scenario: Mapping[str, Any]) -> None:
        if not isinstance(scenario, Mapping):
            raise DraftRuntimeError("reviewScenario must be an object.")
        raw_steps = scenario.get("sequence")
        if not isinstance(raw_steps, list) or not raw_steps:
            raise DraftRuntimeError("reviewScenario.sequence must contain steps.")
        steps: list[tuple[str, str]] = []
        for index, raw_step in enumerate(raw_steps):
            if not isinstance(raw_step, Mapping):
                raise DraftRuntimeError(f"reviewScenario.sequence[{index}] must be an object.")
            step_id = raw_step.get("id")
            label = raw_step.get("label")
            if not isinstance(step_id, str) or not step_id.strip():
                raise DraftRuntimeError(f"reviewScenario.sequence[{index}].id is required.")
            if not isinstance(label, str) or not label.strip():
                raise DraftRuntimeError(f"reviewScenario.sequence[{index}].label is required.")
            steps.append((step_id.strip(), label.strip()))
        if len(steps) < 2:
            raise DraftRuntimeError("reviewScenario.sequence needs READY and RUNNING steps.")
        raw_alarm = scenario.get("alarm")
        if not isinstance(raw_alarm, Mapping):
            raise DraftRuntimeError("reviewScenario.alarm is required.")
        alarm_id = raw_alarm.get("id")
        alarm_message = raw_alarm.get("message")
        if not isinstance(alarm_id, str) or not alarm_id.strip():
            raise DraftRuntimeError("reviewScenario.alarm.id is required.")
        if not isinstance(alarm_message, str) or not alarm_message.strip():
            raise DraftRuntimeError("reviewScenario.alarm.message is required.")
        self._steps = tuple(steps)
        self._alarm_id = alarm_id.strip()
        self._alarm_message = alarm_message.strip()
        self._duration = max(len(self._steps) - 1, 1)
        self._state = self._steps[0][0]
        self._step_index = 0
        self._tick_count = 0
        self._fault_active = False
        self._fault_acknowledged = False
        self._notice = "READY | LOCAL REVIEW SCENARIO"

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "NativeDraftReviewRuntime":
        scenario = document.get("reviewScenario")
        return cls(scenario if isinstance(scenario, Mapping) else {})

    def run(self) -> ReviewRuntimeSnapshot:
        if self._fault_active:
            self._notice = "RUN BLOCKED | ACKNOWLEDGE AND CLEAR THE REVIEW ALARM"
        elif self._state == self._steps[-1][0]:
            self._notice = "CYCLE COMPLETE | RESET TO RUN AGAIN"
        else:
            self._state = self._steps[1][0]
            self._step_index = 1
            self._tick_count = 0
            self._notice = "RUNNING | LOCAL REVIEW ONLY"
        return self.snapshot()

    def stop(self) -> ReviewRuntimeSnapshot:
        if not self._fault_active:
            self._state = "STOPPED"
        self._notice = "STOPPED | OUTPUTS SAFE | LOCAL REVIEW ONLY"
        return self.snapshot()

    def reset(self) -> ReviewRuntimeSnapshot:
        self._state = self._steps[0][0]
        self._step_index = 0
        self._tick_count = 0
        self._notice = "RESET | READY FOR LOCAL REVIEW"
        return self.snapshot()

    def advance(self) -> ReviewRuntimeSnapshot:
        if self._fault_active or self._state != self._steps[1][0]:
            return self.snapshot()
        self._tick_count += 1
        if self._tick_count >= self._duration:
            self._state = self._steps[-1][0]
            self._step_index = len(self._steps) - 1
            self._notice = "CYCLE COMPLETE | LOCAL REVIEW ONLY"
        return self.snapshot()

    def raise_fault(self) -> ReviewRuntimeSnapshot:
        self._fault_active = True
        self._fault_acknowledged = False
        self._state = "FAULTED"
        self._notice = f"ALARM ACTIVE | {self._alarm_id}"
        return self.snapshot()

    def acknowledge_fault(self) -> ReviewRuntimeSnapshot:
        if not self._fault_active:
            self._notice = "NO ACTIVE REVIEW ALARM"
        else:
            self._fault_acknowledged = True
            self._notice = "ALARM ACKNOWLEDGED | CLEAR CONDITION TO RESET"
        return self.snapshot()

    def clear_fault(self) -> ReviewRuntimeSnapshot:
        if not self._fault_active:
            self._notice = "NO ACTIVE REVIEW ALARM"
        elif not self._fault_acknowledged:
            self._notice = "CLEAR BLOCKED | ACKNOWLEDGE THE REVIEW ALARM FIRST"
        else:
            self._fault_active = False
            self._fault_acknowledged = False
            self._state = self._steps[0][0]
            self._step_index = 0
            self._tick_count = 0
            self._notice = "ALARM CLEARED | READY FOR LOCAL REVIEW"
        return self.snapshot()

    def snapshot(self) -> ReviewRuntimeSnapshot:
        complete = self._state == self._steps[-1][0]
        return ReviewRuntimeSnapshot(
            state=self._state,
            step_index=self._step_index,
            step_label=self._step_label(),
            cycle_active=self._state == self._steps[1][0] and not self._fault_active,
            cycle_complete=complete,
            fault_active=self._fault_active,
            fault_acknowledged=self._fault_acknowledged,
            fault_message=self._alarm_message if self._fault_active else "",
            points={
                "review_run": self._state == self._steps[1][0] and not self._fault_active,
                "review_cycle_complete": complete,
                "review_fault": self._fault_active,
            },
            notice=self._notice,
        )

    def _step_label(self) -> str:
        if self._state == "STOPPED":
            return "Stopped / safe state"
        if self._state == "FAULTED":
            return "Faulted / outputs safe"
        for step_id, label in self._steps:
            if step_id == self._state:
                return label
        return self._state
