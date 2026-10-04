"""Bounded native event history for operator evidence and audit projection.

This module has no Qt, PLC, transport, or raw-telemetry dependency.  It owns
only presentation-level event identity, lifecycle, acknowledgement, retention,
and a sanitized export suitable for the workspace client.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ALARM = "alarm"


@dataclass(frozen=True, slots=True)
class NativeEvent:
    event_id: str
    code: str
    title: str
    severity: EventSeverity
    source: str
    detail: str
    occurred_at_utc: str
    cleared_at_utc: str | None = None
    acknowledged_by: str | None = None
    acknowledged_at_utc: str | None = None

    @property
    def active(self) -> bool:
        return self.cleared_at_utc is None


class EventHistory:
    """Retain a bounded, deterministic event list without control authority."""

    def __init__(self, *, max_events: int = 100) -> None:
        if max_events < 1:
            raise ValueError("max_events must be positive")
        self.max_events = max_events
        self._events: list[NativeEvent] = []
        self._sequence = 0

    @staticmethod
    def _now() -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

    def record(
        self,
        *,
        code: str,
        title: str,
        severity: EventSeverity,
        source: str,
        detail: str,
        occurred_at_utc: str | None = None,
    ) -> NativeEvent:
        if not all(isinstance(value, str) and value.strip() for value in (code, title, source, detail)):
            raise ValueError("event code, title, source, and detail are required")
        self._sequence += 1
        event = NativeEvent(
            event_id=f"evt-{self._sequence:06d}",
            code=code.strip(),
            title=title.strip(),
            severity=EventSeverity(severity),
            source=source.strip(),
            detail=detail.strip(),
            occurred_at_utc=occurred_at_utc or self._now(),
        )
        self._events.append(event)
        del self._events[:-self.max_events]
        return event

    def _replace(self, event_id: str, **changes: Any) -> NativeEvent:
        for index, event in enumerate(self._events):
            if event.event_id == event_id:
                updated = replace(event, **changes)
                self._events[index] = updated
                return updated
        raise KeyError(f"unknown event: {event_id}")

    def clear(self, event_id: str, *, cleared_at_utc: str | None = None) -> NativeEvent:
        event = self.get(event_id)
        if not event.active:
            return event
        return self._replace(event_id, cleared_at_utc=cleared_at_utc or self._now())

    def acknowledge(self, event_id: str, operator: str, *, acknowledged_at_utc: str | None = None) -> NativeEvent:
        if not operator.strip():
            raise ValueError("operator is required")
        return self._replace(
            event_id,
            acknowledged_by=operator.strip(),
            acknowledged_at_utc=acknowledged_at_utc or self._now(),
        )

    def get(self, event_id: str) -> NativeEvent:
        for event in self._events:
            if event.event_id == event_id:
                return event
        raise KeyError(f"unknown event: {event_id}")

    def all(self) -> tuple[NativeEvent, ...]:
        return tuple(reversed(self._events))

    def active(self) -> tuple[NativeEvent, ...]:
        return tuple(event for event in self.all() if event.active)

    def export_sanitized(self) -> tuple[dict[str, str | bool], ...]:
        """Export event evidence without credentials, addresses, or telemetry."""
        return tuple(
            {
                "event_id": event.event_id,
                "code": event.code,
                "title": event.title,
                "severity": event.severity.value,
                "source": event.source,
                "occurred_at_utc": event.occurred_at_utc,
                "active": event.active,
                "acknowledged": event.acknowledged_by is not None,
            }
            for event in self.all()
        )
