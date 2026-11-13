from dataclasses import dataclass


@dataclass(frozen=True)
class ShipmentEvent:
    carrier: str
    event_id: str
    sku: str
    quantity: int


class ShipmentLedger:
    """Apply carrier callbacks to the inventory on hand."""

    def __init__(self, stock: dict[str, int]):
        self._stock = dict(stock)
        self._processed: set[str] = set()

    def remaining(self, sku: str) -> int:
        return self._stock[sku]

    def record(self, event: ShipmentEvent) -> str:
        """Return 'applied' for a new event or 'duplicate' for a replay."""
        event_key = event.event_id
        if event_key in self._processed:
            return "duplicate"
        if event.quantity <= 0:
            raise ValueError("Shipment quantity must be positive")
        available = self._stock[event.sku]
        self._processed.add(event_key)
        if event.quantity > available:
            raise ValueError("Shipment exceeds stock on hand")
        self._stock[event.sku] = available - event.quantity
        return "applied"

    def receive_stock(self, sku: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Receipt quantity must be positive")
        self._stock[sku] = self._stock.get(sku, 0) + quantity
