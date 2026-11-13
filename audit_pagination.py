from bisect import bisect_right
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AuditEvent:
    event_id: int
    category: str
    message: str


@dataclass(frozen=True)
class AuditPage:
    events: tuple[AuditEvent, ...]
    next_cursor: int | None


class AuditLog:
    """Read from an immutable snapshot with unique, positive event IDs."""

    def __init__(self, events: Iterable[AuditEvent]):
        self._events = sorted(events, key=lambda event: event.event_id)
        self._ids = [event.event_id for event in self._events]
        if len(self._ids) != len(set(self._ids)) or any(event_id < 1 for event_id in self._ids):
            raise ValueError("Event IDs must be unique positive integers")

    def page(self, *, cursor: int = 0, limit: int = 20) -> AuditPage:
        """Return at most limit events with IDs greater than the cursor."""
        if cursor < 0 or not 1 <= limit <= 100:
            raise ValueError("Cursor must be nonnegative and limit must be between 1 and 100")
        start = bisect_right(self._ids, cursor)
        end = start + limit
        events = tuple(self._events[start:end])
        next_cursor = events[-1].event_id if end < len(self._events) else None
        return AuditPage(events=events, next_cursor=next_cursor)
