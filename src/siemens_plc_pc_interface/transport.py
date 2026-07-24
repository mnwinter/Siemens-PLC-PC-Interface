"""PLC transport boundary and the python-snap7 implementation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from .config import ConnectionConfig, Direction, TagConfig


TagValue = bool | int | float


class TransportError(RuntimeError):
    """A PLC connection, read, write, or disconnect operation failed."""


class OwnershipError(TransportError):
    """A caller attempted an operation contrary to configured ownership."""


class PlcTransport(Protocol):
    """Small client contract used by the runtime and fake unit-test clients."""

    @property
    def connected(self) -> bool:
        """Return whether this transport currently has an S7 session."""

    def connect(self, connection: ConnectionConfig) -> None:
        """Connect using validated endpoint settings."""

    def disconnect(self) -> None:
        """Close the current S7 session."""

    def read(self, tag: TagConfig) -> TagValue:
        """Read one PLC-owned configured tag."""

    def write(self, tag: TagConfig, value: TagValue) -> None:
        """Write one PC-owned configured tag."""


class Snap7Transport:
    """
    Adapt python-snap7 behind the narrow runtime transport contract.

    The dependency is imported lazily so offline configuration validation and
    unit tests cannot connect merely by importing this package.
    """

    def __init__(
        self,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._client_factory = client_factory
        self._client: Any | None = None

    @property
    def connected(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(self._client.get_connected())
        except Exception:
            return False

    def _make_client(self) -> Any:
        if self._client_factory is not None:
            return self._client_factory()

        try:
            from snap7 import Client
        except ImportError as exc:
            raise TransportError(
                "python-snap7 is not installed; install requirements.txt"
            ) from exc
        return Client()

    def connect(self, connection: ConnectionConfig) -> None:
        if self._client is not None:
            raise TransportError("transport is already connected or in use")

        client = self._make_client()
        self._client = client
        try:
            client.connect(
                connection.ip,
                connection.rack,
                connection.slot,
            )
            if not client.get_connected():
                raise TransportError(
                    "python-snap7 returned without an active S7 session"
                )
        except Exception as exc:
            try:
                client.disconnect()
            except Exception:
                pass
            self._client = None
            if isinstance(exc, TransportError):
                raise
            raise TransportError(
                f"failed to connect to {connection.ip} "
                f"rack={connection.rack} slot={connection.slot}: {exc}"
            ) from exc

    def disconnect(self) -> None:
        client = self._client
        self._client = None
        if client is None:
            return
        try:
            client.disconnect()
        except Exception as exc:
            raise TransportError(f"failed to disconnect cleanly: {exc}") from exc

    def _require_client(self) -> Any:
        if self._client is None or not self.connected:
            raise TransportError("transport is not connected")
        return self._client

    def read(self, tag: TagConfig) -> TagValue:
        if tag.direction is not Direction.PLC_TO_PC:
            raise OwnershipError(
                f"refusing to read PC-owned tag {tag.name!r}; "
                "runtime reads are limited to plc_to_pc tags"
            )

        try:
            return self._require_client().read_tag(tag.snap7_tag)
        except OwnershipError:
            raise
        except Exception as exc:
            raise TransportError(
                f"failed to read {tag.name} at {tag.snap7_tag}: {exc}"
            ) from exc

    def write(self, tag: TagConfig, value: TagValue) -> None:
        if tag.direction is not Direction.PC_TO_PLC:
            raise OwnershipError(
                f"refusing to write PLC-owned tag {tag.name!r}; "
                "runtime writes are limited to pc_to_plc tags"
            )

        try:
            self._require_client().write_tag(tag.snap7_tag, value)
        except OwnershipError:
            raise
        except Exception as exc:
            raise TransportError(
                f"failed to write {tag.name} at {tag.snap7_tag}: {exc}"
            ) from exc
