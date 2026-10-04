"""Deterministic hosted-workspace client seam for the native RungProof app.

This module is deliberately an in-memory transport, not an online service.  It
models the narrow boundary that a future HTTPS adapter must preserve:

* workspace authentication produces a fake workspace token, never a PLC
  credential or PLC session;
* the workspace assigns only versioned, content-addressed scene packages;
* package hash and client compatibility checks happen before caching or use;
* an unavailable transport falls back only to the client's verified
  last-known-good package; and
* uploads accept only :class:`SanitizedSessionMetadata`.

The service's payload checks are intentionally independent of the facade's
type checks.  A future HTTPS implementation should call the same validation
before serializing requests and reject any payload containing PLC profiles,
DB14/write scope, connection intent, heartbeat, or control-command fields.
No PLC/runtime/scene-loader or network dependency belongs in this seam.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
from types import MappingProxyType
from typing import Any, Mapping, Protocol

try:  # Package import when tools is imported as a package.
    from .native_workspace import (
        PackageSource,
        SanitizedSessionMetadata,
        VersionedAssignedScenePackage,
        WorkspacePackageError,
        WorkspacePackageResolution,
        _reject_forbidden_fields,
    )
except ImportError:  # Direct module execution from the repository root.
    from native_workspace import (  # type: ignore[no-redef]
        PackageSource,
        SanitizedSessionMetadata,
        VersionedAssignedScenePackage,
        WorkspacePackageError,
        WorkspacePackageResolution,
        _reject_forbidden_fields,
    )


class WorkspaceClientError(RuntimeError):
    """Base error for the local workspace transport/client seam."""


class WorkspaceAuthenticationError(WorkspaceClientError):
    """Raised when a workspace token is absent or invalid."""


class WorkspaceTransportError(WorkspaceClientError):
    """Raised when the hosted transport is unavailable."""


class WorkspaceBoundaryError(WorkspaceClientError):
    """Raised when data crosses the workspace boundary outside its contract."""


@dataclass(frozen=True, slots=True)
class FakeWorkspaceToken:
    """Opaque test token; it is not accepted by any PLC or runtime adapter."""

    subject: str
    value: str
    token_type: str = "fake-workspace-token"


@dataclass(frozen=True, slots=True)
class WorkspaceIdentity:
    subject: str
    display_name: str


@dataclass(frozen=True, slots=True)
class AssignedPackage:
    assignment_id: str
    package: VersionedAssignedScenePackage


_SANITIZED_METADATA_FIELDS = frozenset(
    {
        "session_id",
        "project_id",
        "scene_id",
        "client_version",
        "started_at_utc",
        "package_source",
        "connection_state",
    }
)


def _metadata_payload(metadata: SanitizedSessionMetadata) -> dict[str, str]:
    return {
        "session_id": metadata.session_id,
        "project_id": metadata.project_id,
        "scene_id": metadata.scene_id,
        "client_version": metadata.client_version,
        "started_at_utc": metadata.started_at_utc,
        "package_source": metadata.package_source.value,
        "connection_state": metadata.connection_state,
    }


def _validate_metadata_payload(payload: Mapping[str, Any]) -> dict[str, str]:
    """Validate the wire-shaped upload independently of the facade."""
    try:
        _reject_forbidden_fields(payload, "session_metadata")
    except WorkspacePackageError as exc:
        raise WorkspaceBoundaryError(str(exc)) from exc
    keys = frozenset(payload)
    if keys != _SANITIZED_METADATA_FIELDS:
        extra = sorted(keys - _SANITIZED_METADATA_FIELDS)
        missing = sorted(_SANITIZED_METADATA_FIELDS - keys)
        detail = []
        if extra:
            detail.append(f"unexpected fields: {', '.join(extra)}")
        if missing:
            detail.append(f"missing fields: {', '.join(missing)}")
        raise WorkspaceBoundaryError("session metadata is not sanitized (" + "; ".join(detail) + ")")
    if any(not isinstance(value, str) or not value for value in payload.values()):
        raise WorkspaceBoundaryError("sanitized session metadata values must be non-empty strings")
    try:
        PackageSource(payload["package_source"])
    except ValueError as exc:
        raise WorkspaceBoundaryError("package_source is not a known workspace source") from exc
    return {key: payload[key] for key in sorted(payload)}


class WorkspaceTransport(Protocol):
    """Transport contract replaceable by an authenticated HTTPS adapter."""

    def sign_in(self, username: str, secret: str) -> tuple[FakeWorkspaceToken, WorkspaceIdentity]: ...

    def list_assigned_packages(self, token: FakeWorkspaceToken) -> tuple[AssignedPackage, ...]: ...

    def assigned_package(self, token: FakeWorkspaceToken, assignment_id: str) -> VersionedAssignedScenePackage | None: ...

    def upload_session_metadata(self, token: FakeWorkspaceToken, payload: Mapping[str, Any]) -> None: ...


class InMemoryHostedWorkspace:
    """Deterministic hosted-workspace double with an explicit HTTPS seam."""

    def __init__(self, assignments: Mapping[str, VersionedAssignedScenePackage] | None = None) -> None:
        self.available = True
        self._assignments = dict(assignments or {})
        self._tokens: dict[str, WorkspaceIdentity] = {}
        self._uploads: list[Mapping[str, str]] = []

    @property
    def uploads(self) -> tuple[Mapping[str, str], ...]:
        return tuple(self._uploads)

    @property
    def issued_token_values(self) -> tuple[str, ...]:
        """Expose deterministic token fingerprints for test assertions only."""
        return tuple(sorted(self._tokens))

    def replace_assignment(self, assignment_id: str, package: VersionedAssignedScenePackage) -> None:
        self._assignments[assignment_id] = package

    def sign_in(self, username: str, secret: str) -> tuple[FakeWorkspaceToken, WorkspaceIdentity]:
        if not self.available:
            raise WorkspaceTransportError("workspace transport unavailable")
        if not username or not secret:
            raise WorkspaceAuthenticationError("workspace username and secret are required")
        subject = username.casefold().strip()
        digest = hmac.new(b"rungproof-in-memory-workspace", f"{subject}\0{secret}".encode(), hashlib.sha256).hexdigest()
        token = FakeWorkspaceToken(subject=subject, value=f"fws_{digest}")
        identity = WorkspaceIdentity(subject=subject, display_name=subject)
        self._tokens[token.value] = identity
        return token, identity

    def _require_token(self, token: FakeWorkspaceToken) -> WorkspaceIdentity:
        if not isinstance(token, FakeWorkspaceToken):
            raise WorkspaceAuthenticationError("invalid workspace token type")
        identity = self._tokens.get(getattr(token, "value", ""))
        if identity is None or token.token_type != "fake-workspace-token":
            raise WorkspaceAuthenticationError("invalid workspace token")
        return identity

    def list_assigned_packages(self, token: FakeWorkspaceToken) -> tuple[AssignedPackage, ...]:
        self._require_token(token)
        if not self.available:
            raise WorkspaceTransportError("workspace transport unavailable")
        return tuple(AssignedPackage(key, self._assignments[key]) for key in sorted(self._assignments))

    def assigned_package(self, token: FakeWorkspaceToken, assignment_id: str) -> VersionedAssignedScenePackage | None:
        self._require_token(token)
        if not self.available:
            raise WorkspaceTransportError("workspace transport unavailable")
        return self._assignments.get(assignment_id)

    def upload_session_metadata(self, token: FakeWorkspaceToken, payload: Mapping[str, Any]) -> None:
        self._require_token(token)
        if not self.available:
            raise WorkspaceTransportError("workspace transport unavailable")
        self._uploads.append(MappingProxyType(_validate_metadata_payload(payload)))


class NativeWorkspaceClient:
    """Small facade for native UI code; it has no PLC/runtime authority."""

    def __init__(self, transport: WorkspaceTransport, *, client_version: str) -> None:
        self._transport = transport
        self.client_version = client_version
        self.identity: WorkspaceIdentity | None = None
        self._token: FakeWorkspaceToken | None = None
        self._last_known_good: dict[str, VersionedAssignedScenePackage] = {}

    @property
    def signed_in(self) -> bool:
        return self._token is not None

    def sign_in(self, username: str, secret: str) -> WorkspaceIdentity:
        token, identity = self._transport.sign_in(username, secret)
        if token.token_type != "fake-workspace-token":
            raise WorkspaceBoundaryError("workspace transport returned a non-workspace token")
        self._token = token
        self.identity = identity
        return identity

    def _require_sign_in(self) -> FakeWorkspaceToken:
        if self._token is None:
            raise WorkspaceAuthenticationError("sign in to the workspace first")
        return self._token

    def list_assigned_packages(self) -> tuple[AssignedPackage, ...]:
        return self._transport.list_assigned_packages(self._require_sign_in())

    def sync(self, assignment_id: str) -> WorkspacePackageResolution:
        token = self._require_sign_in()
        try:
            assigned = self._transport.assigned_package(token, assignment_id)
        except WorkspaceTransportError:
            assigned = None
        if assigned is not None:
            assigned.ensure_compatible(self.client_version)
            self._last_known_good[assignment_id] = assigned
            return WorkspacePackageResolution(assigned, PackageSource.ASSIGNED, "assigned package hash and compatibility verified")
        cached = self._last_known_good.get(assignment_id)
        if cached is not None:
            cached.ensure_compatible(self.client_version)
            return WorkspacePackageResolution(cached, PackageSource.LAST_KNOWN_GOOD, "offline last-known-good package verified")
        return WorkspacePackageResolution(None, PackageSource.UNAVAILABLE, "no assigned or last-known-good package")

    def upload_session_metadata(self, metadata: SanitizedSessionMetadata) -> None:
        if not isinstance(metadata, SanitizedSessionMetadata):
            raise WorkspaceBoundaryError("workspace uploads require SanitizedSessionMetadata")
        self._transport.upload_session_metadata(self._require_sign_in(), _metadata_payload(metadata))
