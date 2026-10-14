
"""Automated tests for Uganda Corporate Income Tax."""

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.corporate_tax import CorporateIncomeTax
from src.tax_engine.exceptions import (
    InvalidIncomeError,
    TaxError
)


TAX_DATE = date(2026, 10, 1)


def calculate_cit(revenue, deductions="0"):
    """Calculate corporate income tax."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money(revenue),
        details={
            "allowable_deductions": Money(deductions)
        }
    )

    return CorporateIncomeTax().calculate(context)


def test_standard_cit():
    """Check the standard 30% corporate tax calculation."""

    result = calculate_cit("250000000", "150000000")

    assert result.breakdown[
        "chargeable_income"
    ].amount == Decimal("100000000")

    assert result.amount.amount == Decimal("30000000")


def test_zero_profit():
    """Zero chargeable income should produce zero CIT."""

    result = calculate_cit("100000000", "100000000")

    assert result.amount.amount == Decimal("0")


def test_company_loss():
    """Excess deductions should be reported separately."""

    result = calculate_cit("80000000", "100000000")

    assert result.amount.amount == Decimal("0")
    assert result.breakdown[
        "excess_deductions"
    ].amount == Decimal("20000000")


def test_no_deductions():
    """CIT should equal 30% when deductions are zero."""

    result = calculate_cit("100000000")

    assert result.amount.amount == Decimal("30000000")


def test_small_profit():
    """Check CIT on a relatively small profit."""

    result = calculate_cit("10000000", "9000000")

    assert result.amount.amount == Decimal("300000")


def test_negative_revenue():
    """Negative revenue must be rejected."""

    with pytest.raises(InvalidIncomeError):
        calculate_cit("-1000000")


def test_negative_deductions():
    """Negative deductions must be rejected."""

    with pytest.raises(TaxError):
        calculate_cit("10000000", "-500000")


def test_invalid_revenue_type():
    """Revenue must be represented by Money."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income="10000000"
    )

    with pytest.raises(InvalidIncomeError):
        CorporateIncomeTax().calculate(context)


def test_invalid_deduction_type():
    """Deductions must be represented by Money."""

    context = TaxContext(
        tax_date=TAX_DATE,
        income=Money("10000000"),
        details={
            "allowable_deductions": "2000000"
        }
    )

    with pytest.raises(TaxError):
        CorporateIncomeTax().calculate(context)


@pytest.mark.parametrize(
    "revenue, deductions, expected",
    [
        ("1000000", "0", "300000"),
        ("5000000", "2000000", "900000"),
        ("10000000", "5000000", "1500000"),
        ("20000000", "10000000", "3000000")
    ]
)
def test_multiple_cit_scenarios(revenue, deductions, expected):
    """Test corporate tax across different scenarios."""

    result = calculate_cit(revenue, deductions)

    assert result.amount.amount == Decimal(expected)
