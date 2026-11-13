"""Calculate an invoice quote in whole cents."""

from dataclasses import dataclass


BASIS_POINTS_PER_UNIT = 10_000


@dataclass(frozen=True)
class Line:
    unit_cents: int
    quantity: int

    @property
    def extended_cents(self) -> int:
        if self.unit_cents < 0 or self.quantity < 1:
            raise ValueError("price must be non-negative and quantity must be positive")
        return self.unit_cents * self.quantity


@dataclass(frozen=True)
class Quote:
    subtotal_cents: int
    discount_cents: int
    shipping_cents: int
    total_cents: int


def rate_amount_cents(base_cents: int, rate_basis_points: int) -> int:
    """Return the rate amount in cents, with half cents rounded up."""
    if base_cents < 0 or not 0 <= rate_basis_points <= BASIS_POINTS_PER_UNIT:
        raise ValueError("amount and rate are out of range")
    scaled_amount = base_cents * rate_basis_points
    return scaled_amount // BASIS_POINTS_PER_UNIT


def quote(
    lines: list[Line], discount_basis_points: int, shipping_cents: int
) -> Quote:
    """Apply the rate to the merchandise subtotal and then add shipping."""
    if shipping_cents < 0:
        raise ValueError("shipping cannot be negative")
    subtotal = sum(line.extended_cents for line in lines)
    discount = rate_amount_cents(subtotal + shipping_cents, discount_basis_points)
    return Quote(
        subtotal_cents=subtotal,
        discount_cents=discount,
        shipping_cents=shipping_cents,
        total_cents=subtotal - discount + shipping_cents,
    )
