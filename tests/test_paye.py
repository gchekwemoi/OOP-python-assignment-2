
"""Tests for Uganda PAYE calculations."""

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, strategies as st

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.paye import PAYETax
from src.tax_engine.exceptions import (
    InvalidIncomeError,
    NoScheduleForDateError
)


TAX_DATE = date(2026, 10, 1)


def calculate_paye(
    income,
    residency="resident",
    allowances="0",
    tax_date=TAX_DATE
):
    """Calculate PAYE for a sample employee."""

    context = TaxContext(
        tax_date=tax_date,
        income=Money(income),
        residency=residency,
        details={
            "allowances": Money(allowances)
        }
    )

    return PAYETax().calculate(context).amount.amount


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
    """Verify resident PAYE and tax-band boundaries."""

    result = calculate_paye(income)

    assert result == Decimal(expected)


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
        ("1500000", "375500"),
        ("10000000", "2925500"),
        ("10000001", "2925500")
    ]
)
def test_non_resident_paye(income, expected):
    """Verify non-resident PAYE calculations."""

    result = calculate_paye(
        income,
        residency="non-resident"
    )

    assert result == Decimal(expected)


def test_taxable_allowances():
    """Taxable allowances increase PAYE income."""

    result = calculate_paye(
        income="1000000",
        allowances="500000"
    )

    assert result == Decimal("338250")


def test_negative_income():
    """Negative employment income must be rejected."""

    with pytest.raises(InvalidIncomeError):
        calculate_paye("-100000")


def test_negative_allowances():
    """Negative allowances must be rejected."""

    with pytest.raises(InvalidIncomeError):
        calculate_paye(
            "1000000",
            allowances="-50000"
        )


def test_invalid_income_type():
    """PAYE requires a Money object."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income="1000000",
        residency="resident"
    )

    with pytest.raises(InvalidIncomeError):
        PAYETax().calculate(context)


def test_unsupported_schedule_date():
    """Reject dates before the configured PAYE schedule."""

    with pytest.raises(NoScheduleForDateError):
        calculate_paye(
            "1000000",
            tax_date=date(2025, 1, 1)
        )


@given(income=st.integers(min_value=0, max_value=100000000))
def test_resident_tax_non_negative(income):
    """Resident PAYE must never be negative."""

    tax = calculate_paye(income)

    assert tax >= Decimal("0")


@given(income=st.integers(min_value=0, max_value=100000000))
def test_resident_tax_not_above_income(income):
    """PAYE must not exceed the taxable income."""

    tax = calculate_paye(income)

    assert tax <= Decimal(income)


@given(
    income_a=st.integers(min_value=0, max_value=100000000),
    income_b=st.integers(min_value=0, max_value=100000000)
)
def test_resident_paye_monotonic(income_a, income_b):
    """Higher taxable income cannot result in lower PAYE."""

    lower = min(income_a, income_b)
    higher = max(income_a, income_b)

    assert calculate_paye(lower) <= calculate_paye(higher)
