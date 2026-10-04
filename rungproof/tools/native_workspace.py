"""Local-first workspace package contracts for the native RungProof client.

This module deliberately contains no Qt, PLC, transport, runtime, scene-loader,
or network dependencies.  It is a small seam for a future hosted workspace:
assigned scene packages may be fetched by an adapter, but the package itself
can contain only scene content and client compatibility metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence, TypeAlias


JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


class WorkspacePackageError(ValueError):
    """Raised when a workspace package is malformed or violates its boundary."""


class PackageCompatibilityError(WorkspacePackageError):
    """Raised when a valid package is not compatible with this client."""


class PackageSource(str, Enum):
    ASSIGNED = "assigned"
    LAST_KNOWN_GOOD = "last_known_good"
    UNAVAILABLE = "unavailable"


_FORBIDDEN_FIELD_MARKERS = (
    "plcprofile",
    "db14",
    "writescope",
    "connectionintent",
    "heartbeat",
    "controlcommand",
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _normalized_field_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.casefold())


def _reject_forbidden_fields(value: Any, path: str = "content") -> None:
    if isinstance(value, Mapping):
        for raw_key, nested in value.items():
            if not isinstance(raw_key, str):
                raise WorkspacePackageError(f"{path} contains a non-string field name")
            normalized = _normalized_field_name(raw_key)
            if any(marker in normalized for marker in _FORBIDDEN_FIELD_MARKERS):
                raise WorkspacePackageError(
                    f"{path}.{raw_key} is outside the workspace package boundary"
                )
            _reject_forbidden_fields(nested, f"{path}.{raw_key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            _reject_forbidden_fields(nested, f"{path}[{index}]")


def _freeze_json(value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(nested) for key, nested in value.items()})  # type: ignore[return-value]
    if isinstance(value, list):
        return tuple(_freeze_json(nested) for nested in value)  # type: ignore[return-value]
    return value


def _json_serializable(value: Any) -> Any:
    """Convert the immutable internal representation back to JSON containers."""
    if isinstance(value, Mapping):
        return {str(key): _json_serializable(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_serializable(nested) for nested in value]
    return value


def canonical_json_bytes(content: Mapping[str, JsonValue]) -> bytes:
    """Return the deterministic bytes used for package hashing."""
    try:
        return json.dumps(
            _json_serializable(content),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise WorkspacePackageError("package content must be finite JSON data") from exc


def content_sha256(content: Mapping[str, JsonValue]) -> str:
    return hashlib.sha256(canonical_json_bytes(content)).hexdigest()


@dataclass(frozen=True, slots=True)
class VersionedAssignedScenePackage:
    """An assigned, content-addressed scene package with no PLC authority."""

    package_id: str
    scene_id: str
    package_version: str
    client_schema_version: int
    compatible_client_versions: tuple[str, ...]
    content: Mapping[str, JsonValue]
    content_sha256: str
    assigned_at_utc: str

    def __post_init__(self) -> None:
        if not self.package_id or not self.scene_id or not self.package_version:
            raise WorkspacePackageError("package_id, scene_id, and package_version are required")
        if self.client_schema_version != 1:
            raise WorkspacePackageError("unsupported workspace package schema")
        if not self.compatible_client_versions:
            raise WorkspacePackageError("at least one compatible client version is required")
        if not _SHA256_RE.fullmatch(self.content_sha256):
            raise WorkspacePackageError("content_sha256 must be a lowercase SHA-256 digest")
        _reject_forbidden_fields(self.content)
        canonical_json_bytes(self.content)
        object.__setattr__(self, "content", _freeze_json(dict(self.content)))

    @classmethod
    def from_content(
        cls,
        *,
        package_id: str,
        scene_id: str,
        package_version: str,
        compatible_client_versions: tuple[str, ...],
        content: Mapping[str, JsonValue],
        assigned_at_utc: str = "2026-01-01T00:00:00Z",
    ) -> "VersionedAssignedScenePackage":
        return cls(
            package_id=package_id,
            scene_id=scene_id,
            package_version=package_version,
            client_schema_version=1,
            compatible_client_versions=compatible_client_versions,
            content=dict(content),
            content_sha256=content_sha256(content),
            assigned_at_utc=assigned_at_utc,
        )

    def verify_hash(self) -> bool:
        return content_sha256(self.content) == self.content_sha256

    def ensure_compatible(self, client_version: str) -> None:
        if client_version not in self.compatible_client_versions:
            raise PackageCompatibilityError(
                f"package {self.package_id} is not compatible with client {client_version}"
            )
        if not self.verify_hash():
            raise WorkspacePackageError(f"package {self.package_id} failed SHA-256 verification")


@dataclass(frozen=True, slots=True)
class WorkspacePackageResolution:
    package: VersionedAssignedScenePackage | None
    source: PackageSource
    reason: str


class LocalWorkspaceAdapter(Protocol):
    """Adapter seam for a future hosted workspace client."""

    def assigned_package(self, assignment_id: str) -> VersionedAssignedScenePackage | None: ...

    def last_known_good_package(self, assignment_id: str) -> VersionedAssignedScenePackage | None: ...


class DeterministicLocalFixtureAdapter:
    """Predictable offline adapter used by tests and local development."""

    def __init__(
        self,
        assigned: Mapping[str, VersionedAssignedScenePackage] | None = None,
        last_known_good: Mapping[str, VersionedAssignedScenePackage] | None = None,
        *,
        online: bool = True,
    ) -> None:
        self._assigned = dict(assigned or {})
        self._last_known_good = dict(last_known_good or {})
        self.online = online

    def assigned_package(self, assignment_id: str) -> VersionedAssignedScenePackage | None:
        if not self.online:
            return None
        return self._assigned.get(assignment_id)

    def last_known_good_package(self, assignment_id: str) -> VersionedAssignedScenePackage | None:
        return self._last_known_good.get(assignment_id)


def resolve_assigned_package(
    adapter: LocalWorkspaceAdapter,
    assignment_id: str,
    *,
    client_version: str,
) -> WorkspacePackageResolution:
    """Resolve online first, then fall back only to a verified compatible package."""
    assigned = adapter.assigned_package(assignment_id)
    if assigned is not None:
        assigned.ensure_compatible(client_version)
        return WorkspacePackageResolution(assigned, PackageSource.ASSIGNED, "assigned package verified")

    cached = adapter.last_known_good_package(assignment_id)
    if cached is not None:
        cached.ensure_compatible(client_version)
        return WorkspacePackageResolution(cached, PackageSource.LAST_KNOWN_GOOD, "offline last-known-good package")

    return WorkspacePackageResolution(None, PackageSource.UNAVAILABLE, "no assigned or last-known-good package")


@dataclass(frozen=True, slots=True)
class SessionMetadata:
    session_id: str
    project_id: str
    scene_id: str
    client_version: str
    started_at_utc: str
    package_source: PackageSource
    connection_state: str
    plc_credentials: Mapping[str, str] | None = None
    raw_telemetry: Mapping[str, JsonValue] | None = None


@dataclass(frozen=True, slots=True)
class SanitizedSessionMetadata:
    session_id: str
    project_id: str
    scene_id: str
    client_version: str
    started_at_utc: str
    package_source: PackageSource
    connection_state: str


def project_sanitized_session_metadata(metadata: SessionMetadata) -> SanitizedSessionMetadata:
    """Project only operational session identity; never export PLC secrets or telemetry."""
    return SanitizedSessionMetadata(
        session_id=metadata.session_id,
        project_id=metadata.project_id,
        scene_id=metadata.scene_id,
        client_version=metadata.client_version,
        started_at_utc=metadata.started_at_utc,
        package_source=metadata.package_source,
        connection_state=metadata.connection_state,
    )


def utc_now_iso() -> str:
    """Small helper for callers that need a real timestamp, kept out of fixtures."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
