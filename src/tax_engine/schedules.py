
"""Dated PAYE schedules for the Uganda Tax Engine."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .exceptions import NoScheduleForDateError


@dataclass(frozen=True)
class PAYESchedule:
    """Store monthly PAYE thresholds and rates."""

    effective_from: date
    residency: str
    threshold_1: Decimal
    threshold_2: Decimal
    threshold_3: Decimal
    surcharge_threshold: Decimal

    rate_1: Decimal
    rate_2: Decimal
    rate_3: Decimal
    surcharge_rate: Decimal

    base_tax_2: Decimal
    base_tax_3: Decimal


# Resident PAYE schedule effective 1 July 2026
RESIDENT_2026 = PAYESchedule(
    effective_from=date(2026, 7, 1),
    residency="resident",
    threshold_1=Decimal("335000"),
    threshold_2=Decimal("410000"),
    threshold_3=Decimal("485000"),
    surcharge_threshold=Decimal("10000000"),
    rate_1=Decimal("0.20"),
    rate_2=Decimal("0.25"),
    rate_3=Decimal("0.30"),
    surcharge_rate=Decimal("0.10"),
    base_tax_2=Decimal("15000"),
    base_tax_3=Decimal("33750")
)


# Non-resident PAYE schedule
NON_RESIDENT_2026 = PAYESchedule(
    effective_from=date(2026, 7, 1),
    residency="non-resident",
    threshold_1=Decimal("0"),
    threshold_2=Decimal("335000"),
    threshold_3=Decimal("410000"),
    surcharge_threshold=Decimal("10000000"),
    rate_1=Decimal("0.10"),
    rate_2=Decimal("0.20"),
    rate_3=Decimal("0.30"),
    surcharge_rate=Decimal("0.10"),
    base_tax_2=Decimal("33500"),
    base_tax_3=Decimal("48500")
)


def get_paye_schedule(
    tax_date: date,
    residency: str
) -> PAYESchedule:
    """Return the PAYE schedule for a date and residency."""

    if not isinstance(tax_date, date):
        raise TypeError("tax_date must be a date object.")

    residency = residency.strip().lower()

    if residency not in ("resident", "non-resident"):
        raise ValueError("Invalid residency status.")

    if tax_date < date(2026, 7, 1):
        raise NoScheduleForDateError(
            "No PAYE schedule configured before 1 July 2026."
        )

    if residency == "resident":
        return RESIDENT_2026

    return NON_RESIDENT_2026
