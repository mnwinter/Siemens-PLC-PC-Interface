"""Direct native Scene 2 runtime for RungProof.

The live path is intentionally short:

    ConveyorPusher -> SimulationUpdateLoop -> InterfaceRuntime -> Snap7Transport

There is no HTTP server, JSON serialization, browser event loop, or renderer in
that path.  The Qt application only reads immutable snapshots published by the
worker that owns the S7 connection.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import Enum
import ipaddress
import json
import math
from pathlib import Path
import sys
import threading
import time
from types import MappingProxyType
from typing import Any, Callable


FROZEN = bool(getattr(sys, "frozen", False))
APPLICATION_DIR = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else Path(__file__).resolve().parents[1] / "prototype"
)
RESOURCE_ROOT = (
    APPLICATION_DIR
    if FROZEN
    else APPLICATION_DIR.parent
)
INTERFACE_SOURCE_ROOT = (
    RESOURCE_ROOT / "vendor" / "siemens-plc-pc-interface"
)
if INTERFACE_SOURCE_ROOT.is_dir():
    interface_source = str(INTERFACE_SOURCE_ROOT)
    if interface_source not in sys.path:
        sys.path.insert(0, interface_source)

from siemens_plc_pc_interface.components import (  # noqa: E402
    ConveyorPhotoeyeConfig,
    ConveyorPusher,
    ConveyorPusherConfig,
    ConveyorPusherInputs,
    ConveyorPusherPointBinding,
    ConveyorPusherSnapshot,
)
from siemens_plc_pc_interface.config import (  # noqa: E402
    ConnectionConfig,
    DataType,
    DigitalPointConfig,
    Direction,
    InterfaceConfig,
    load_config,
)
from siemens_plc_pc_interface.runtime import (  # noqa: E402
    InterfaceRuntime,
    SafeStatePolicy,
)
from siemens_plc_pc_interface.transport import (  # noqa: E402
    Snap7Transport,
)
from siemens_plc_pc_interface.update_loop import (  # noqa: E402
    LoopHealth,
    SimulationUpdateLoop,
    UpdateResult,
)


SCENE_ID = "scene-2-conveyor-pusher"
SCENE2_CONNECTION_CONTRACT = (
    "s7-1500",
    "10.70.9.201",
    0,
    1,
    20,
    2000,
)
SCENE2_HEARTBEAT_TIMEOUT_MS = 1000
SCENE_FILE = (
    RESOURCE_ROOT / "prototype" / "scenes"
    / "scene-2-conveyor-pusher.plcscene"
)
PROFILE_FILE = (
    APPLICATION_DIR / "plc-profiles"
    / "scene-2-db14-pusher-interface.json"
)
class NativeRuntimeError(RuntimeError):
    """The native scene runtime could not safely continue."""


class ConnectionState(str, Enum):
    """Actual S7 transport state, separate from scene playback."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    CLOSING = "closing"


@dataclass(frozen=True)
class Scene2Definition:
    """Validated Scene 2 physics and typed point binding."""

    model: ConveyorPusherConfig
    binding: ConveyorPusherPointBinding
    physics_step_s: float
    repeat_load_s: float


@dataclass(frozen=True)
class NativeCycleSnapshot:
    """One immutable plant and PLC exchange result."""

    scene_time_s: float
    running: bool
    ready: bool
    model: ConveyorPusherSnapshot
    update: UpdateResult

    @property
    def point_values(self) -> dict[str, bool | int | float | str]:
        plc = self.update.plc_point_samples
        return {
            "part_at_pusher": self.model.photoeye_blocked,
            "pusher_extended": self.model.pusher_extended,
            "pusher_retracted": self.model.pusher_retracted,
            "conveyor_running": bool(
                plc["conveyor_running"].value
            ),
            "pusher_extend": bool(plc["pusher_extend"].value),
            "pusher_position": self.model.pusher_position * 100.0,
            "component_state": self.model.state.value,
            "parts_completed": self.model.completed_count,
        }


@dataclass(frozen=True)
class NativeSessionSnapshot:
    """Thread-safe UI projection of connection, PLC, and plant state."""

    connection: ConnectionState
    running: bool
    cycle: int
    health: str
    heartbeat_reason: str
    heartbeat_echo: int | None
    simulation_enable: bool | None
    simulation_comm_ok: bool | None
    simulation_timeout: bool | None
    ready: bool
    scene_time_s: float
    exchange_ms: float
    recent_p99_ms: float
    points: Mapping[str, bool | int | float | str | None]
    model: ConveyorPusherSnapshot | None
    message: str
    error: str | None


def _require_number(
    mapping: dict[str, Any],
    key: str,
    *,
    minimum: float,
) -> float:
    value = mapping.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < minimum
    ):
        raise NativeRuntimeError(
            f"Scene 2 simulation.{key} must be a finite number "
            f"greater than or equal to {minimum}."
        )
    return float(value)


def load_scene2_definition(path: Path = SCENE_FILE) -> Scene2Definition:
    """Load the existing .plcscene as the authoritative plant definition."""

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NativeRuntimeError(
            f"Could not load Scene 2 from {path}: {exc}"
        ) from exc
    if document.get("id") != SCENE_ID:
        raise NativeRuntimeError(
            f"Expected scene id {SCENE_ID!r} in {path}."
        )
    simulation = document.get("simulation")
    if (
        not isinstance(simulation, dict)
        or simulation.get("type") != "conveyorPusher"
    ):
        raise NativeRuntimeError(
            "Scene 2 must use the conveyorPusher simulation."
        )

    model = ConveyorPusherConfig(
        conveyor=ConveyorPhotoeyeConfig(
            length_m=_require_number(
                simulation, "lengthM", minimum=0.001
            ),
            speed_m_per_s=_require_number(
                simulation, "speedMps", minimum=0.001
            ),
            object_length_m=_require_number(
                simulation, "objectLengthM", minimum=0.001
            ),
            photoeye_position_m=_require_number(
                simulation, "photoeyePositionM", minimum=0.0
            ),
            minimum_photoeye_on_s=_require_number(
                simulation, "minimumPhotoeyeOnS", minimum=0.0
            ),
        ),
        pusher_stroke_time_s=_require_number(
            simulation, "pusherStrokeTimeS", minimum=0.001
        ),
        transfer_position_fraction=_require_number(
            simulation, "transferPositionFraction", minimum=0.001
        ),
    )
    return Scene2Definition(
        model=model,
        binding=ConveyorPusherPointBinding(
            run_command_point="conveyor_running",
            extend_command_point="pusher_extend",
            photoeye_point="part_at_pusher",
            extended_sensor_point="pusher_extended",
            retracted_sensor_point="pusher_retracted",
        ),
        physics_step_s=0.01,
        repeat_load_s=_require_number(
            simulation, "repeatLoadSeconds", minimum=0.0
        ),
    )


def validate_native_profile(
    config: InterfaceConfig,
    *,
    allow_endpoint_override: bool = False,
) -> None:
    """Fail closed unless the exact Scene 2 live contract is present."""

    connection_contract = (
        config.connection.cpu_family,
        config.connection.ip,
        config.connection.rack,
        config.connection.slot,
        config.connection.cycle_ms,
        config.connection.connect_timeout_ms,
    )
    fixed_connection_contract = (
        config.connection.cpu_family,
        config.connection.cycle_ms,
        config.connection.connect_timeout_ms,
    )
    expected_fixed_connection = (
        SCENE2_CONNECTION_CONTRACT[0],
        SCENE2_CONNECTION_CONTRACT[4],
        SCENE2_CONNECTION_CONTRACT[5],
    )
    endpoint_is_valid = False
    try:
        ipaddress.ip_address(config.connection.ip)
        endpoint_is_valid = (
            0 <= config.connection.rack <= 7
            and 0 <= config.connection.slot <= 31
        )
    except ValueError:
        endpoint_is_valid = False
    connection_valid = (
        fixed_connection_contract == expected_fixed_connection
        and endpoint_is_valid
        and (
            allow_endpoint_override
            or connection_contract == SCENE2_CONNECTION_CONTRACT
        )
    )
    if config.version != 2 or not connection_valid:
        raise NativeRuntimeError(
            "Scene 2 requires profile version 2, an S7-1500 CPU, a valid "
            "IP/rack/slot, a 20 ms cycle, and a 2000 ms transport timeout. "
            "The packaged profile default is 10.70.9.201 rack 0 slot 1."
        )

    expected_tags = {
        "simulated_photoeye": (
            "DB_SimulationProof.Part_At_Pusher",
            "DB14.DBX0.0",
            DataType.BOOL,
            Direction.PC_TO_PLC,
            False,
        ),
        "simulated_pusher_extended": (
            "DB_SimulationProof.Pusher_Extended",
            "DB14.DBX0.1",
            DataType.BOOL,
            Direction.PC_TO_PLC,
            False,
        ),
        "simulated_pusher_retracted": (
            "DB_SimulationProof.Pusher_Retracted",
            "DB14.DBX0.2",
            DataType.BOOL,
            Direction.PC_TO_PLC,
            True,
        ),
        "conveyor_running": (
            "DB_SimulationProof.Conveyor_Run",
            "DB14.DBX1.0",
            DataType.BOOL,
            Direction.PLC_TO_PC,
            None,
        ),
        "pusher_extend": (
            "DB_SimulationProof.Pusher_Extend",
            "DB14.DBX1.1",
            DataType.BOOL,
            Direction.PLC_TO_PC,
            None,
        ),
        "pc_heartbeat": (
            "DB_SimulationProof.PC_Heartbeat",
            "DB14.DBD2",
            DataType.DINT,
            Direction.PC_TO_PLC,
            0,
        ),
        "plc_heartbeat_echo": (
            "DB_SimulationProof.PLC_Heartbeat_Echo",
            "DB14.DBD6",
            DataType.DINT,
            Direction.PLC_TO_PC,
            None,
        ),
        "simulation_enable": (
            "DB_SimulationProof.Simulation_Enable",
            "DB14.DBX10.0",
            DataType.BOOL,
            Direction.PLC_TO_PC,
            None,
        ),
        "simulation_comm_ok": (
            "DB_SimulationProof.Simulation_Comm_OK",
            "DB14.DBX10.1",
            DataType.BOOL,
            Direction.PLC_TO_PC,
            None,
        ),
        "simulation_timeout": (
            "DB_SimulationProof.Simulation_Timeout",
            "DB14.DBX10.2",
            DataType.BOOL,
            Direction.PLC_TO_PC,
            None,
        ),
    }
    tag_names = {tag.name for tag in config.tags}
    if tag_names != set(expected_tags):
        missing = sorted(set(expected_tags) - tag_names)
        extra = sorted(tag_names - set(expected_tags))
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("extra " + ", ".join(extra))
        raise NativeRuntimeError(
            "Scene 2 profile must contain the exact DB14 tag contract: "
            + "; ".join(details)
        )
    for name, (
        plc_symbol,
        address,
        data_type,
        direction,
        safe_value,
    ) in expected_tags.items():
        tag = config.tag(name)
        if (
            tag.plc_symbol != plc_symbol
            or tag.address != address
            or tag.data_type is not data_type
            or tag.direction is not direction
            or tag.safe_value != safe_value
        ):
            raise NativeRuntimeError(
                f"Scene 2 tag {name!r} must be {direction.value} "
                f"{data_type.value} at {address}, symbol {plc_symbol!r}, "
                f"safe value {safe_value!r}."
            )
    if (
        config.heartbeat.pc_tag != "pc_heartbeat"
        or config.heartbeat.echo_tag != "plc_heartbeat_echo"
        or config.heartbeat.timeout_ms != SCENE2_HEARTBEAT_TIMEOUT_MS
    ):
        raise NativeRuntimeError(
            "Scene 2 heartbeat must use pc_heartbeat and "
            "plc_heartbeat_echo with a 1000 ms timeout."
        )

    required_points = {
        "part_at_pusher": (
            "simulated_photoeye", Direction.PC_TO_PLC
        ),
        "pusher_extended": (
            "simulated_pusher_extended", Direction.PC_TO_PLC
        ),
        "pusher_retracted": (
            "simulated_pusher_retracted", Direction.PC_TO_PLC
        ),
        "conveyor_running": (
            "conveyor_running", Direction.PLC_TO_PC
        ),
        "pusher_extend": ("pusher_extend", Direction.PLC_TO_PC),
    }
    point_names = {point.name for point in config.points}
    missing_points = sorted(set(required_points) - point_names)
    if missing_points:
        raise NativeRuntimeError(
            "Scene 2 profile is missing point(s): "
            + ", ".join(missing_points)
        )
    if point_names != set(required_points):
        extra_points = sorted(point_names - set(required_points))
        raise NativeRuntimeError(
            "Scene 2 profile contains unexpected point(s): "
            + ", ".join(extra_points)
        )
    for name, (tag_name, direction) in required_points.items():
        point = config.point(name)
        tag = config.tag(point.tag)
        if (
            not isinstance(point, DigitalPointConfig)
            or point.tag != tag_name
            or point.group != "pusher_one"
            or point.inverted
            or tag.data_type is not DataType.BOOL
            or tag.direction is not direction
        ):
            raise NativeRuntimeError(
                f"Scene 2 point {name!r} must map to {tag_name!r} as "
                f"a non-inverted pusher_one digital {direction.value} BOOL."
            )


def _controller_ready(result: UpdateResult) -> bool:
    """Require heartbeat health and all three exact PLC status values."""

    status = result.cycle.plc_values_read
    return (
        result.health in (LoopHealth.HEALTHY, LoopHealth.DEGRADED)
        and status.get("simulation_enable") is True
        and status.get("simulation_comm_ok") is True
        and status.get("simulation_timeout") is False
    )


def next_cycle_deadline(
    previous_deadline: float,
    finished: float,
    period_s: float,
) -> float:
    """Schedule the next exchange without issuing catch-up bursts."""

    if period_s <= 0:
        raise ValueError("period_s must be greater than zero")
    scheduled = previous_deadline + period_s
    return scheduled if finished < scheduled else finished + period_s


class Scene2CycleCore:
    """Deep, renderer-neutral implementation of one Scene 2 cycle."""

    def __init__(
        self,
        definition: Scene2Definition,
        update_loop: SimulationUpdateLoop,
        *,
        exchange_s: float,
    ) -> None:
        if exchange_s <= 0:
            raise ValueError("exchange_s must be greater than zero")
        self.definition = definition
        self.update_loop = update_loop
        self.exchange_s = exchange_s
        self._physics_steps = max(
            1, round(exchange_s / definition.physics_step_s)
        )
        self._model = ConveyorPusher(definition.model)
        self._inputs = ConveyorPusherInputs(False, False)
        self._scene_time_s = 0.0
        self._reload_elapsed_s = 0.0
        self._model.load_object()

    @property
    def model_snapshot(self) -> ConveyorPusherSnapshot:
        return self._model.snapshot

    def reset(self) -> ConveyorPusherSnapshot:
        """Reset only plant playback; the caller keeps the S7 session."""

        self._model = ConveyorPusher(self.definition.model)
        self._inputs = ConveyorPusherInputs(False, False)
        self._scene_time_s = 0.0
        self._reload_elapsed_s = 0.0
        return self._model.load_object()

    def replace_update_loop(
        self,
        update_loop: SimulationUpdateLoop,
    ) -> None:
        """Replace only the failed S7 runtime; preserve physical plant state."""

        self.update_loop = update_loop
        self._inputs = ConveyorPusherInputs(False, False)

    def step(
        self,
        now: float,
        *,
        running: bool,
        reset_scene: bool = False,
    ) -> NativeCycleSnapshot:
        """Advance physics, exchange DB14, then stage next-cycle commands."""

        if reset_scene:
            self.reset()

        snapshot = self._model.snapshot
        if running:
            for _ in range(self._physics_steps):
                snapshot = self._model.step(
                    self.definition.physics_step_s,
                    self._inputs,
                )
                self._scene_time_s += self.definition.physics_step_s
                if snapshot.object_transferred:
                    self._reload_elapsed_s = 0.0
                elif not snapshot.object_present:
                    self._reload_elapsed_s += (
                        self.definition.physics_step_s
                    )
                if (
                    not snapshot.object_present
                    and snapshot.pusher_retracted
                    and self._reload_elapsed_s
                    >= self.definition.repeat_load_s
                ):
                    snapshot = self._model.load_object()
                    self._reload_elapsed_s = 0.0

        pc_points = self.definition.binding.pc_point_values(snapshot)
        update = self.update_loop.step(now, pc_points)
        ready = _controller_ready(update)
        self._inputs = (
            self.definition.binding.inputs_from_update(update)
            if ready and running
            else ConveyorPusherInputs(False, False)
        )
        return NativeCycleSnapshot(
            scene_time_s=self._scene_time_s,
            running=running,
            ready=ready,
            model=snapshot,
            update=update,
        )


def _empty_snapshot(
    definition: Scene2Definition,
) -> NativeSessionSnapshot:
    model = ConveyorPusher(definition.model)
    model.load_object()
    snapshot = model.snapshot
    return NativeSessionSnapshot(
        connection=ConnectionState.DISCONNECTED,
        running=False,
        cycle=0,
        health="disconnected",
        heartbeat_reason="not connected",
        heartbeat_echo=None,
        simulation_enable=None,
        simulation_comm_ok=None,
        simulation_timeout=None,
        ready=False,
        scene_time_s=0.0,
        exchange_ms=0.0,
        recent_p99_ms=0.0,
        points=MappingProxyType(
            {
                "part_at_pusher": snapshot.photoeye_blocked,
                "pusher_extended": snapshot.pusher_extended,
                "pusher_retracted": snapshot.pusher_retracted,
                "conveyor_running": False,
                "pusher_extend": False,
                "pusher_position": 0.0,
                "component_state": snapshot.state.value,
                "parts_completed": 0,
            }
        ),
        model=snapshot,
        message="Real PLC disconnected",
        error=None,
    )


class NativePlcSession:
    """Own one direct S7 worker until Disconnect or application exit."""

    def __init__(
        self,
        *,
        profile_path: Path = PROFILE_FILE,
        scene_path: Path = SCENE_FILE,
        transport_factory: Callable[[], Any] = Snap7Transport,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        try:
            self.config = load_config(profile_path)
        except Exception as exc:
            raise NativeRuntimeError(
                f"Could not load PLC profile {profile_path}: {exc}"
            ) from exc
        validate_native_profile(self.config)
        self.definition = load_scene2_definition(scene_path)
        self._transport_factory = transport_factory
        self._monotonic = monotonic
        self._lock = threading.RLock()
        self._wake = threading.Event()
        self._desired_connected = False
        self._running = False
        self._step_requested = False
        self._reset_requested = False
        self._shutdown = False
        self._snapshot = _empty_snapshot(self.definition)
        self._thread = threading.Thread(
            target=self._worker,
            name="rungproof-plc-worker",
            daemon=False,
        )
        self._thread.start()

    def configure_connection(self, *, ip: str, rack: int, slot: int) -> None:
        """Change only the known S7 endpoint while fully disconnected."""

        with self._lock:
            if (
                self._shutdown
                or self._desired_connected
                or self._snapshot.connection
                is not ConnectionState.DISCONNECTED
            ):
                raise NativeRuntimeError(
                    "Disconnect the PLC before changing the connection "
                    "target."
                )
            try:
                normalized_ip = str(ipaddress.ip_address(ip.strip()))
            except ValueError as exc:
                raise NativeRuntimeError(
                    f"Invalid PLC IP address: {ip!r}."
                ) from exc
            if not 0 <= rack <= 7 or not 0 <= slot <= 31:
                raise NativeRuntimeError(
                    "Rack must be 0-7 and slot must be 0-31."
                )
            self.config = replace(
                self.config,
                connection=replace(
                    self.config.connection,
                    ip=normalized_ip,
                    rack=rack,
                    slot=slot,
                ),
            )
            validate_native_profile(
                self.config,
                allow_endpoint_override=True,
            )

    def snapshot(self) -> NativeSessionSnapshot:
        with self._lock:
            return self._snapshot

    def connect(self) -> None:
        with self._lock:
            if self._shutdown:
                raise NativeRuntimeError("Native PLC session is closed.")
            self._desired_connected = True
            self._snapshot = replace(
                self._snapshot,
                connection=ConnectionState.CONNECTING,
                message="Connecting directly to the real PLC...",
                error=None,
            )
        self._wake.set()

    def disconnect(self) -> None:
        with self._lock:
            self._desired_connected = False
            self._running = False
            self._step_requested = False
            self._set_connection(
                ConnectionState.CLOSING,
                "Disconnecting from the real PLC...",
            )
        self._wake.set()

    def run(self) -> None:
        with self._lock:
            if (
                self._snapshot.connection is not ConnectionState.CONNECTED
                or not self._snapshot.ready
            ):
                raise NativeRuntimeError(
                    "The real PLC must be connected and safely ready "
                    "before starting the scene."
                )
            self._running = True
            self._step_requested = False

    def stop(self) -> None:
        """Stop plant playback without closing or timing out the S7 session."""

        with self._lock:
            self._running = False
            self._step_requested = False

    def step(self) -> None:
        """Advance one PLC exchange while continuous playback stays stopped."""

        with self._lock:
            if (
                self._snapshot.connection is not ConnectionState.CONNECTED
                or not self._snapshot.ready
            ):
                raise NativeRuntimeError(
                    "The real PLC must be connected and safely ready "
                    "before stepping the scene."
                )
            self._running = False
            self._step_requested = True
        self._wake.set()

    def reset(self) -> None:
        """Reset plant state without closing the S7 session."""

        with self._lock:
            self._running = False
            self._step_requested = False
            self._reset_requested = True

    def close(self, timeout: float = 5.0) -> None:
        self.begin_close()
        self.wait_closed(timeout)

    def begin_close(self) -> None:
        """Request shutdown without hiding a UI that still owns the worker."""

        with self._lock:
            self._shutdown = True
            self._desired_connected = False
            self._running = False
            self._step_requested = False
        self._wake.set()

    @property
    def is_closed(self) -> bool:
        return not self._thread.is_alive()

    def wait_closed(self, timeout: float = 5.0) -> None:
        """Wait for bounded transport cleanup after ``begin_close``."""

        self._thread.join(timeout)
        if self._thread.is_alive():
            raise NativeRuntimeError(
                "PLC worker did not stop within the shutdown timeout."
            )

    def _set_connection(
        self,
        state: ConnectionState,
        message: str,
        *,
        error: str | None = None,
    ) -> None:
        with self._lock:
            points = dict(self._snapshot.points)
            if state is not ConnectionState.CONNECTED:
                # PLC-owned samples are valid only for the connected exchange
                # that produced them. Preserve local plant state, but never
                # project a cached PLC command or health value as current once
                # that transport session is unavailable.
                points[self.definition.binding.run_command_point] = None
                points[self.definition.binding.extend_command_point] = None
            self._snapshot = replace(
                self._snapshot,
                connection=state,
                running=self._running,
                ready=False,
                health=state.value,
                heartbeat_reason=(
                    "not connected"
                    if state is ConnectionState.DISCONNECTED
                    else "PLC telemetry unavailable"
                ),
                heartbeat_echo=None,
                simulation_enable=None,
                simulation_comm_ok=None,
                simulation_timeout=None,
                points=MappingProxyType(points),
                message=message,
                error=error,
            )

    def _publish_cycle(
        self,
        cycle: NativeCycleSnapshot,
        *,
        duration_ms: float,
        recent_p99_ms: float,
    ) -> None:
        update = cycle.update
        heartbeat = update.cycle.heartbeat
        status = update.cycle.plc_values_read
        with self._lock:
            if not self._desired_connected or self._shutdown:
                # Disconnect may be selected while an exchange is already in
                # flight. Its late result must not overwrite the truthful
                # Closing/Disconnected projection with Connected telemetry.
                return
            if not cycle.ready:
                self._running = False
            published_running = self._running and cycle.ready
            self._snapshot = NativeSessionSnapshot(
                connection=ConnectionState.CONNECTED,
                running=published_running,
                cycle=update.cycle.cycle_number,
                health=update.health.value,
                heartbeat_reason=heartbeat.reason,
                heartbeat_echo=heartbeat.last_echo,
                simulation_enable=status.get("simulation_enable"),
                simulation_comm_ok=status.get("simulation_comm_ok"),
                simulation_timeout=status.get("simulation_timeout"),
                ready=cycle.ready,
                scene_time_s=cycle.scene_time_s,
                exchange_ms=duration_ms,
                recent_p99_ms=recent_p99_ms,
                points=MappingProxyType(cycle.point_values),
                model=cycle.model,
                message=(
                    "Real PLC connected - healthy"
                    if cycle.ready
                    else (
                        "Real PLC connected - playback stopped; "
                        "waiting for safe readiness"
                    )
                ),
                error=None,
            )

    def _commands(self) -> tuple[bool, bool, bool, bool]:
        with self._lock:
            running = self._running
            step_requested = self._step_requested
            self._step_requested = False
            reset_requested = self._reset_requested
            self._reset_requested = False
            return (
                self._desired_connected,
                running,
                step_requested,
                reset_requested,
            )

    def _should_shutdown(self) -> bool:
        with self._lock:
            return self._shutdown

    def _worker(self) -> None:
        reconnect_delay_s = 0.25
        core: Scene2CycleCore | None = None
        while not self._should_shutdown():
            desired, _running, _step, _reset = self._commands()
            if not desired:
                self._set_connection(
                    ConnectionState.DISCONNECTED,
                    "Real PLC disconnected",
                )
                self._wake.clear()
                self._wake.wait(0.25)
                continue

            runtime: InterfaceRuntime | None = None
            try:
                self._set_connection(
                    ConnectionState.CONNECTING,
                    "Connecting directly to the real PLC...",
                )
                runtime = InterfaceRuntime(
                    self.config,
                    self._transport_factory(),
                    safe_state_policy=SafeStatePolicy.PLC_WATCHDOG_ONLY,
                    start_time=self._monotonic(),
                )
                runtime.connect()
                update_loop = SimulationUpdateLoop(runtime)
                if core is None:
                    core = Scene2CycleCore(
                        self.definition,
                        update_loop,
                        exchange_s=(
                            self.config.connection.cycle_ms / 1_000
                        ),
                    )
                else:
                    core.replace_update_loop(update_loop)
                recent_durations: deque[float] = deque(maxlen=1_000)
                recent_p99_ms = 0.0
                deadline = self._monotonic()
                period_s = self.config.connection.cycle_ms / 1_000

                while not self._should_shutdown():
                    (
                        desired,
                        running,
                        step_requested,
                        reset_requested,
                    ) = self._commands()
                    if not desired:
                        break
                    started = self._monotonic()
                    cycle = core.step(
                        started,
                        running=running or step_requested,
                        reset_scene=reset_requested,
                    )
                    finished = self._monotonic()
                    duration_ms = (finished - started) * 1_000
                    recent_durations.append(duration_ms)
                    cycle_number = cycle.update.cycle.cycle_number
                    if cycle_number == 1 or cycle_number % 50 == 0:
                        ordered = sorted(recent_durations)
                        rank = max(
                            0,
                            math.ceil(0.99 * len(ordered)) - 1,
                        )
                        recent_p99_ms = ordered[rank]
                    self._publish_cycle(
                        cycle,
                        duration_ms=duration_ms,
                        recent_p99_ms=recent_p99_ms,
                    )

                    deadline = next_cycle_deadline(
                        deadline,
                        finished,
                        period_s,
                    )
                    delay = deadline - self._monotonic()
                    self._wake.clear()
                    if delay > 0:
                        self._wake.wait(delay)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                with self._lock:
                    self._running = False
                desired, _running, _step, _reset = self._commands()
                if desired and not self._should_shutdown():
                    self._set_connection(
                        ConnectionState.RECONNECTING,
                        "Real PLC exchange failed - reconnecting...",
                        error=error,
                    )
                    self._wake.clear()
                    self._wake.wait(reconnect_delay_s)
                else:
                    self._set_connection(
                        ConnectionState.DISCONNECTED,
                        "Real PLC disconnected",
                        error=error,
                    )
            finally:
                if runtime is not None:
                    runtime.close()

        self._set_connection(
            ConnectionState.DISCONNECTED,
            "Real PLC disconnected",
        )
