from dataclasses import dataclass, replace
from typing import Iterable


@dataclass(frozen=True)
class WorkspaceMember:
    workspace_id: str
    role: str


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    workspace_id: str
    title: str
    status: str = "open"


class TicketDesk:
    """In-memory backing store for the workspace's support queue."""

    def __init__(self, tickets: Iterable[Ticket] = ()):
        """Initialize a queue with globally unique ticket IDs."""
        self._tickets = {ticket.ticket_id: ticket for ticket in tickets}

    def queue(self, member: WorkspaceMember, *, include_closed: bool = False) -> list[Ticket]:
        tickets = self._tickets.values()
        visible = iter(tickets)
        if not include_closed:
            visible = (ticket for ticket in visible if ticket.status != "closed")
        return sorted(visible, key=lambda ticket: ticket.ticket_id)

    def close(self, member: WorkspaceMember, ticket_id: str) -> Ticket:
        ticket = self._tickets.get(ticket_id)
        if ticket is None or ticket.workspace_id != member.workspace_id:
            raise KeyError(ticket_id)
        if member.role not in {"viewer", "editor", "owner"}:
            raise PermissionError("Only editors and owners may close tickets")
        if ticket.status == "closed":
            return ticket
        closed = replace(ticket, status="closed")
        self._tickets[ticket_id] = closed
        return closed
