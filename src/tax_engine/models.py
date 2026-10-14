
"""Core models for the Uganda Tax Engine."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .money import Money


@dataclass
class TaxContext:
    """Hold the inputs required for a tax calculation."""

    tax_date: date
    income: Money | None = None
    residency: str = "resident"
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaxResult:
    """Hold the result of a tax calculation."""

    tax_name: str
    amount: Money
    breakdown: dict[str, Any] = field(default_factory=dict)


class Tax(ABC):
    """Abstract base class for all tax calculators."""

    @abstractmethod
    def calculate(self, ctx: TaxContext) -> TaxResult:
        """Calculate a tax using the supplied context."""
        pass
