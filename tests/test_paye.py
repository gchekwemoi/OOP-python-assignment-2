
"""Tests for Uganda PAYE calculations."""

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.paye import PAYETax
from src.tax_engine.exceptions import (
    InvalidIncomeError,
    NoScheduleForDateError
)


TAX_DATE = date(2026, 10, 1)


def calculate_paye(income, residency="resident"):
    """Calculate monthly PAYE and return its amount."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money(income),
        residency=residency
    )

    result = PAYETax().calculate(context)

    return result.amount.amount


# 1. RESIDENT PAYE BOUNDARY TESTS

@pytest.mark.parametrize(
    "income, expected",
    [
        ("0", "0"),
        ("335000", "0"),
        ("335001", "0"),
        ("410000", "15000"),
        ("410001", "15000"),
        ("485000", "33750"),
        ("485001", "33750"),
        ("1000000", "188250"),
        ("1500000", "338250"),
        ("10000000", "2888250"),
        ("10000001", "2888250")
    ]
)
def test_resident_paye(income, expected):
    """Check PAYE at resident income boundaries."""

    assert calculate_paye(income) == Decimal(expected)


# 2. NON-RESIDENT PAYE TESTS

@pytest.mark.parametrize(
    "income, expected",
    [
        ("0", "0"),
        ("100000", "10000"),
        ("335000", "33500"),
        ("335001", "33500"),
        ("410000", "48500"),
        ("410001", "48500"),
        ("1000000", "225500"),
        ("10000000", "2925500"),
        ("10000001", "2925500")
    ]
)
def test_non_resident_paye(income, expected):
    """Check PAYE using non-resident tax rates."""

    assert calculate_paye(
        income,
        "non-resident"
    ) == Decimal(expected)


# 3. ALLOWANCE TEST

def test_taxable_allowances():
    """Check that taxable allowances increase income."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money("1000000"),
        residency="resident",
        details={
            "allowances": Money("500000")
        }
    )

    result = PAYETax().calculate(context)

    assert result.amount.amount == Decimal("338250")


# 4. INVALID INCOME TEST

def test_negative_income():
    """Reject negative employment income."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money("-100000")
    )

    with pytest.raises(InvalidIncomeError):
        PAYETax().calculate(context)


# 5. INVALID ALLOWANCES TEST

def test_negative_allowances():
    """Reject negative taxable allowances."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money("1000000"),
        details={
            "allowances": Money("-50000")
        }
    )

    with pytest.raises(InvalidIncomeError):
        PAYETax().calculate(context)


# 6. MISSING TAX SCHEDULE TEST

def test_missing_schedule():
    """Reject dates with no configured PAYE schedule."""

    context = TaxContext(
        tax_date=date(2025, 1, 1),
        income=Money("1000000")
    )

    with pytest.raises(NoScheduleForDateError):
        PAYETax().calculate(context)


# 7. HYPOTHESIS: NON-NEGATIVE TAX

@given(
    income=st.integers(
        min_value=0,
        max_value=100_000_000
    )
)
@settings(max_examples=100)
def test_tax_non_negative(income):
    """PAYE must never be negative."""

    tax = calculate_paye(str(income))

    assert tax >= Decimal("0")


# 8. HYPOTHESIS: TAX NOT GREATER THAN INCOME

@given(
    income=st.integers(
        min_value=0,
        max_value=100_000_000
    )
)
@settings(max_examples=100)
def test_tax_not_above_income(income):
    """PAYE must not exceed taxable income."""

    tax = calculate_paye(str(income))

    assert tax <= Decimal(income)


# 9. HYPOTHESIS: MONOTONICITY

@given(
    income1=st.integers(
        min_value=0,
        max_value=100_000_000
    ),
    income2=st.integers(
        min_value=0,
        max_value=100_000_000
    )
)
@settings(max_examples=100)
def test_tax_monotonic(income1, income2):
    """Increasing income must not reduce PAYE."""

    lower_income = min(income1, income2)
    higher_income = max(income1, income2)

    lower_tax = calculate_paye(str(lower_income))
    higher_tax = calculate_paye(str(higher_income))

    assert higher_tax >= lower_tax
