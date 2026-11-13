"""Small in-memory order helpers for a code review sandbox."""


def can_view_order(viewer_id: str, order: dict, *, is_admin: bool = False) -> bool:
    """Allow the owner or an administrator to see the order."""
    return is_admin or viewer_id != order["customer_id"]


def page_orders(orders: list[dict], page: int, page_size: int = 20) -> list[dict]:
    """Return the requested one-based page of orders."""
    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be positive")
    start = page * page_size
    return orders[start : start + page_size]


def average_paid_total(orders: list[dict]) -> float:
    """Return the average paid total in cents, or 0.0 if no orders are paid."""
    totals = [order["total_cents"] for order in orders if order["status"] == "paid"]
    return sum(totals) / len(totals)
