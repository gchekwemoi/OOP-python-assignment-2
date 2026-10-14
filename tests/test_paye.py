
"""Automated tests for Uganda PAYE calculations."""

from hypothesis import given, settings, strategies as st

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.paye import PAYETax
from src.tax_engine.exceptions import (
    InvalidIncomeError,
    NoScheduleForDateError
)


TAX_DATE = date(2026, 10, 1)


def calculate_paye(income, residency="resident"):
    """Calculate PAYE for a given monthly income."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money(income),
        residency=residency
    )

    return PAYETax().calculate(context).amount.amount


# Test resident PAYE at important boundaries
@pytest.mark.parametrize(
    "income, expected",
    [
        ("0", "0"),
        ("335000", "0"),
        ("335001", "0"),
        ("410000", "15000"),
        ("485000", "33750"),
        ("1000000", "188250"),
        ("1500000", "338250"),
        ("10000000", "2888250"),
        ("10000001", "2888250")
    ]
)
def test_resident_paye(income, expected):
    """Verify PAYE at selected income thresholds."""

    assert calculate_paye(income) == Decimal(expected)


# Test non-resident PAYE
@pytest.mark.parametrize(
    "income, expected",
    [
        ("0", "0"),
        ("335000", "33500"),
        ("410000", "48500")
    ]
)
def test_non_resident_paye(income, expected):

    assert calculate_paye(
        income, "non-resident"
    ) == Decimal(expected)


# Test invalid income
def test_negative_income():

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money("-100000"),
        residency="resident"
    )

    with pytest.raises(InvalidIncomeError):
        PAYETax().calculate(context)


# Test unsupported schedule date
def test_missing_schedule():

    context = TaxContext(
        tax_date=date(2025, 1, 1),
        income=Money("1000000"),
        residency="resident"
    )

    with pytest.raises(NoScheduleForDateError):
        PAYETax().calculate(context)


# Test non-negative tax
@pytest.mark.parametrize(
    "income",
    ["0", "335000", "1000000", "5000000"]
)
def test_tax_non_negative(income):

    assert calculate_paye(income) >= Decimal("0")


# Test tax never exceeds income
@pytest.mark.parametrize(
    "income",
    ["100000", "500000", "1500000", "10000000"]
)
def test_tax_not_above_income(income):

    assert calculate_paye(income) <= Decimal(income)


# Test monotonicity
def test_tax_monotonic():

    incomes = [
        "0",
        "335000",
        "410000",
        "485000",
        "1000000",
        "5000000",
        "10000000"
    ]

    taxes = [calculate_paye(x) for x in incomes]

    assert taxes == sorted(taxes)


# PROPERTY-BASED TESTS USING HYPOTHESIS


@given(
    income=st.integers(
        min_value=0,
        max_value=100_000_000
    )
)
@settings(max_examples=100)
def test_paye_never_negative(income):
    """PAYE must never be negative."""

    tax = calculate_paye(str(income))

    assert tax >= Decimal("0")


@given(
    income=st.integers(
        min_value=0,
        max_value=100_000_000
    )
)
@settings(max_examples=100)
def test_paye_never_exceeds_income(income):
    """PAYE must not exceed taxable income."""

    tax = calculate_paye(str(income))

    assert tax <= Decimal(income)


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
def test_paye_monotonic_property(income1, income2):
    """Higher income must not produce lower PAYE."""

    lower_income = min(income1, income2)
    higher_income = max(income1, income2)

    lower_tax = calculate_paye(str(lower_income))
    higher_tax = calculate_paye(str(higher_income))

    assert higher_tax >= lower_tax

