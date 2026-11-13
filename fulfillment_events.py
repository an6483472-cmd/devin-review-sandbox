"""Apply fulfillment events to an order snapshot."""

from dataclasses import dataclass, replace


NEXT_STATES = {
    "placed": frozenset({"paid", "cancelled"}),
    "paid": frozenset({"packed", "cancelled"}),
    "packed": frozenset({"shipped", "cancelled"}),
    "shipped": frozenset(),
    "cancelled": frozenset(),
}


@dataclass(frozen=True)
class Order:
    order_id: str
    status: str = "placed"
    last_sequence: int = 0


@dataclass(frozen=True)
class StatusEvent:
    order_id: str
    sequence: int
    status: str


def apply_event(order: Order, event: StatusEvent) -> Order:
    """Apply a newer event for this order if its status transition is allowed."""
    if event.order_id != order.order_id:
        raise ValueError("event belongs to a different order")
    if event.status not in NEXT_STATES:
        raise ValueError("unknown event status")
    if event.sequence == order.last_sequence:
        return order
    if event.status == order.status:
        return replace(order, last_sequence=event.sequence)
    if event.status not in NEXT_STATES[order.status] and order.status != "cancelled":
        return order
    return replace(order, status=event.status, last_sequence=event.sequence)


def apply_events(order: Order, events: list[StatusEvent]) -> Order:
    """Apply events in delivery order without changing the original snapshot."""
    for event in events:
        order = apply_event(order, event)
    return order
