
"""Money value object for the Uganda Tax Engine."""

from decimal import Decimal, ROUND_HALF_UP


class Money:
    """Represent an amount in Uganda shillings."""

    def __init__(self, amount: str | int | Decimal):
        """Create a Money object with an exact UGX amount."""

        if isinstance(amount, float):
            raise TypeError("Use str, int or Decimal, not float.")

        value = Decimal(str(amount))

        if not value.is_finite():
            raise ValueError("Money amount must be finite.")

        self.amount = value.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects."""

        if not isinstance(other, Money):
            return NotImplemented

        return Money(self.amount + other.amount)

    def __mul__(self, factor: str | int | Decimal) -> "Money":
        """Multiply money by a numeric factor."""

        if isinstance(factor, float):
            raise TypeError("Float multiplication is not allowed.")

        return Money(self.amount * Decimal(str(factor)))

    def __lt__(self, other: "Money") -> bool:
        """Check whether one amount is less than another."""

        if not isinstance(other, Money):
            return NotImplemented

        return self.amount < other.amount

    def __repr__(self) -> str:
        """Display the amount in UGX."""

        return f"UGX {self.amount:,.0f}"
