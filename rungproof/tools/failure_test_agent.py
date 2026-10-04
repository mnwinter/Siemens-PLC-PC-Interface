"""Deterministic failure tests for the native Scene 2 PLC boundary.

This is intentionally a small, agent-runnable harness.  It does not connect
to a real PLC and it does not write project files.  Each case injects one
failure at the PLC boundary, runs the real native Scene 2 cycle core, and
reports the expected safe response.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Callable

# Allow ``py tools\failure_test_agent.py`` from the repository root to use
# the same package imports as the unittest runner.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.native_runtime import (
    InterfaceRuntime,
    PROFILE_FILE,
    SCENE_FILE,
    Scene2CycleCore,
    SimulationUpdateLoop,
    load_config,
    load_scene2_definition,
    validate_native_profile,
)


class TraceTransport:
    """In-memory S7 transport that replays controller output traces.

    This class deliberately contains no PLC logic.  The trace is an explicit
    controller-under-test result supplied to the plant.  A future PLCSIM or
    live-S7 adapter can provide the same ``(Conveyor_Run, Pusher_Extend)``
    trace without changing the plant assertions.
    """

    def __init__(
        self,
        *,
        output_trace: Callable[[int], tuple[bool, bool]],
        feedback_mode: str | None = None,
    ) -> None:
        self.output_trace = output_trace
        self.feedback_mode = feedback_mode
        self.cycle = 0
        self.connected = False
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

    def connect(self, _connection: object) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def write_many(self, values: list[tuple[Any, object]]) -> None:
        if not self.connected:
            raise RuntimeError("write while disconnected")
        for tag, value in values:
            if (
                self.feedback_mode in {"photoeye_stuck_low", "photoeye_stuck_high"}
                and tag.name == "simulated_photoeye"
            ):
                continue
            self.values[tag.name] = value

    def read_many(self, tags: tuple[Any, ...]) -> dict[str, object]:
        if not self.connected:
            raise RuntimeError("read while disconnected")
        conveyor_running, pusher_extend = self.output_trace(self.cycle)
        self.values["conveyor_running"] = conveyor_running
        self.values["pusher_extend"] = pusher_extend
        self.values["plc_heartbeat_echo"] = self.values["pc_heartbeat"]
        result = {tag.name: self.values[tag.name] for tag in tags}
        self.cycle += 1
        return result


@dataclass(frozen=True)
class FailureResult:
    case: str
    passed: bool
    expected: str
    observed: str
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {
            "case": self.case,
            "passed": self.passed,
            "expected": self.expected,
            "observed": self.observed,
            "detail": self.detail,
        }


def _profile_missing_photoeye() -> FailureResult:
    document = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    document["tags"] = [
        tag
        for tag in document["tags"]
        if tag["name"] != "simulated_photoeye"
    ]
    with tempfile.TemporaryDirectory(prefix="rungproof-failure-") as folder:
        path = Path(folder) / PROFILE_FILE.name
        path.write_text(json.dumps(document), encoding="utf-8")
        try:
            validate_native_profile(load_config(path))
        except Exception as exc:  # expected fail-closed behavior
            return FailureResult(
                case="profile_missing_photoeye",
                passed=True,
                expected="Profile validation rejects the missing sensor tag.",
                observed="Profile rejected before a PLC session can start.",
                detail=f"{type(exc).__name__}: {exc}",
            )
    return FailureResult(
        case="profile_missing_photoeye",
        passed=False,
        expected="Profile validation rejects the missing sensor tag.",
        observed="Profile was accepted.",
        detail="The exact Scene 2 PLC contract did not fail closed.",
    )


def _trace_for_case(case: str) -> Callable[[int], tuple[bool, bool]]:
    """Return explicit PLC outputs; never derive them from sensor values."""

    def normal_sequence(cycle: int) -> tuple[bool, bool]:
        return (cycle < 60, False)

    fixed_outputs = {
        "photoeye_stuck_low": (True, False),
        "photoeye_stuck_high": (False, True),
        "conveyor_output_missing": (False, False),
        "pusher_without_part": (False, True),
        "both_outputs": (True, True),
        "conveyor_stopped": (False, False),
    }
    if case == "normal_sequence":
        return normal_sequence
    try:
        outputs = fixed_outputs[case]
    except KeyError as exc:
        raise ValueError(f"unknown I/O failure case: {case}") from exc
    return lambda _cycle: outputs


def _run_io_case(case: str, *, feedback_mode: str | None = None) -> FailureResult:
    config = load_config(PROFILE_FILE)
    definition = load_scene2_definition(SCENE_FILE)
    transport = TraceTransport(
        output_trace=_trace_for_case(case),
        feedback_mode=feedback_mode,
    )
    runtime = InterfaceRuntime(config, transport)
    runtime.connect()
    loop = SimulationUpdateLoop(runtime)
    core = Scene2CycleCore(definition, loop, exchange_s=0.02)
    final = None
    transfer_seen = False
    start = time.monotonic()
    for index in range(500):
        final = core.step(start + index * 0.02, running=True)
        transfer_seen = transfer_seen or final.model.object_transferred
        if index >= 249:
            break
    runtime.close()
    if final is None:
        raise RuntimeError("failure agent produced no cycle result")
    if case == "normal_sequence":
        passed = (
            final.model.photoeye_blocked
            and not final.update.plc_point_samples["conveyor_running"].value
            and not final.model.pusher_extended
        )
        expected = (
            "The package reaches the photoeye, the conveyor stops, and the "
            "pusher waits for its PLC command."
        )
    elif case == "photoeye_stuck_low":
        passed = (
            final.model.completed_count >= 1
            and not final.model.pusher_extended
        )
        expected = (
            "A photoeye that never asserts leaves the conveyor running; "
            "the part discharges and the pusher does not fire."
        )
    elif case in {"conveyor_output_missing", "conveyor_stopped"}:
        passed = (
            final.model.completed_count == 0
            and not final.model.motor_running
        )
        expected = (
            "A missing or false conveyor command leaves the package in place "
            "and never reports a transfer."
        )
    elif case == "pusher_without_part":
        passed = (
            final.model.completed_count == 0
            and final.model.pusher_extended
        )
        expected = (
            "A pusher command without a part moves the cylinder but cannot "
            "invent a transfer; ladder logic should interlock or alarm it."
        )
    elif case == "both_outputs":
        passed = not transfer_seen
        expected = (
            "Simultaneous conveyor and pusher commands must not silently "
            "report a valid transfer; the case requires a conflict alarm."
        )
    elif case == "photoeye_stuck_high":
        passed = (
            final.model.completed_count == 0
            and final.model.pusher_extended
        )
        expected = (
            "A false-high photoeye stops the conveyor and may extend the "
            "pusher, but must not report a transfer without a physical part."
        )
    else:
        raise ValueError(f"unknown I/O failure case: {case}")
    return FailureResult(
        case=case,
        passed=passed,
        expected=expected,
        observed=(
            f"completed_count={final.model.completed_count}, "
            f"state={final.model.state.value}, "
            f"pusher_extended={final.model.pusher_extended}, "
            f"motor_running={final.model.motor_running}, "
            f"photoeye_blocked={final.model.photoeye_blocked}, "
            f"transfer_seen={transfer_seen}"
        ),
        detail=(
            "This case validates equipment response to the injected PLC I/O. "
            "The PLC program must provide the alarm or interlock policy where "
            "the physical response alone cannot identify the programming fault."
        ),
    )


def run_failure_tests() -> list[FailureResult]:
    cases = [
        ("normal_sequence", None),
        ("photoeye_stuck_low", "photoeye_stuck_low"),
        ("photoeye_stuck_high", "photoeye_stuck_high"),
        ("conveyor_output_missing", None),
        ("pusher_without_part", None),
        ("both_outputs", None),
        ("conveyor_stopped", None),
    ]
    return [
        _profile_missing_photoeye(),
        *(_run_io_case(case, feedback_mode=mode) for case, mode in cases),
        _missing_pusher_command(),
    ]


def _missing_pusher_command() -> FailureResult:
    """Detect a ladder that stops at the photoeye but never advances."""

    result = _run_io_case("normal_sequence")
    stuck_at_sensor = "photoeye_blocked=True" in result.observed
    no_pusher_command = "pusher_extended=False" in result.observed
    return FailureResult(
        case="ladder_missing_pusher_command",
        passed=not (stuck_at_sensor and no_pusher_command),
        expected=(
            "After Part_At_Pusher becomes TRUE, the PLC must command "
            "Pusher_Extend or raise a sequence timeout/fault."
        ),
        observed=result.observed,
        detail=(
            "This is the failure found in the supplied ladder screenshots: "
            "the conveyor stop rung works, but no pusher-extension rung was "
            "present in the reviewed networks."
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()
    results = run_failure_tests()
    if args.json:
        print(json.dumps([result.as_dict() for result in results], indent=2))
    else:
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"{status} {result.case}: {result.observed}")
            print(f"  expected: {result.expected}")
            print(f"  detail: {result.detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
