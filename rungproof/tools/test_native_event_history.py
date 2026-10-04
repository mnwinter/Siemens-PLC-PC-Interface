import unittest

try:
    from .native_event_history import EventHistory, EventSeverity
except ImportError:
    from native_event_history import EventHistory, EventSeverity


class NativeEventHistoryTests(unittest.TestCase):
    def test_alarm_lifecycle_and_sanitized_export(self) -> None:
        history = EventHistory()
        event = history.record(
            code="PLC_SESSION_UNAVAILABLE",
            title="Controller disconnected",
            severity=EventSeverity.WARNING,
            source="workspace-session",
            detail="Local model only; controller state is not verified.",
            occurred_at_utc="2026-08-08T00:00:00Z",
        )
        self.assertEqual(len(history.active()), 1)
        acknowledged = history.acknowledge(event.event_id, "operator-1", acknowledged_at_utc="2026-08-08T00:01:00Z")
        self.assertEqual(acknowledged.acknowledged_by, "operator-1")
        cleared = history.clear(event.event_id, cleared_at_utc="2026-08-08T00:02:00Z")
        self.assertFalse(cleared.active)
        exported = history.export_sanitized()[0]
        self.assertEqual(exported["severity"], "warning")
        self.assertNotIn("detail", exported)
        self.assertNotIn("operator-1", repr(exported))

    def test_retention_is_bounded_and_newest_first(self) -> None:
        history = EventHistory(max_events=2)
        for index in range(3):
            history.record(
                code=f"E{index}",
                title=f"Event {index}",
                severity=EventSeverity.INFO,
                source="test",
                detail="detail",
                occurred_at_utc=f"2026-08-08T00:0{index}:00Z",
            )
        self.assertEqual([event.code for event in history.all()], ["E2", "E1"])

    def test_invalid_acknowledgement_and_unknown_events_fail(self) -> None:
        history = EventHistory()
        with self.assertRaises(KeyError):
            history.clear("missing")
        event = history.record(
            code="INFO",
            title="Ready",
            severity=EventSeverity.INFO,
            source="local",
            detail="Ready",
        )
        with self.assertRaises(ValueError):
            history.acknowledge(event.event_id, " ")


if __name__ == "__main__":
    unittest.main()
