from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class DispatchPolicy:
    """Daily dispatch settings expressed in the warehouse's local time."""

    pickup_cutoff: time
    quiet_start: time
    quiet_end: time


def pickup_slot(policy: DispatchPolicy, placed_at: time, in_stock: bool) -> str:
    """Return 'today', 'next_day', or 'unavailable' for a pickup order."""
    if not in_stock:
        return "unavailable"
    if placed_at > policy.pickup_cutoff:
        return "next_day"
    return "today"


def quiet_hours(policy: DispatchPolicy, current_time: time) -> bool:
    """Return whether local time is inside the half-open quiet-hours window."""
    start = policy.quiet_start
    end = policy.quiet_end
    if start == end:
        return False
    if start < end:
        return start <= current_time < end
    return current_time >= start and current_time < end


def delivery_notice(policy: DispatchPolicy, current_time: time, ready: bool) -> str:
    """Choose whether a ready-for-pickup notice should be sent now."""
    if not ready:
        return "skip"
    if quiet_hours(policy, current_time):
        return "defer"
    return "send"
