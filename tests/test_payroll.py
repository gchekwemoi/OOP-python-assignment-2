
"""Automated tests for the Uganda payroll calculator."""

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.payroll import PayrollCalculator
from src.tax_engine.exceptions import InvalidIncomeError


TAX_DATE = date(2026, 10, 1)


def calculate_payroll(
    salary="1500000",
    allowances="0",
    residency="resident",
    lst="0"
):
    """Create a payroll result for testing."""

    calculator = PayrollCalculator()

    return calculator.calculate(
        basic_salary=Money(salary),
        allowances=Money(allowances),
        residency=residency,
        tax_date=TAX_DATE,
        local_service_tax=Money(lst)
    )


def test_basic_payroll():
    """Check a resident employee earning UGX 1.5 million."""

    result = calculate_payroll()

    assert result.gross_pay.amount == Decimal("1500000")
    assert result.paye.amount == Decimal("338250")
    assert result.employee_nssf.amount == Decimal("75000")
    assert result.employer_nssf.amount == Decimal("150000")
    assert result.net_pay.amount == Decimal("1086750")


def test_payroll_with_allowances():
    """Check that allowances increase gross taxable pay."""

    result = calculate_payroll(
        salary="1500000",
        allowances="200000"
    )

    assert result.gross_pay.amount == Decimal("1700000")
    assert result.paye.amount == Decimal("398250")
    assert result.employee_nssf.amount == Decimal("85000")
    assert result.net_pay.amount == Decimal("1216750")


def test_local_service_tax():
    """Check that configured LST reduces take-home pay."""

    result = calculate_payroll(lst="10000")

    assert result.local_service_tax.amount == Decimal("10000")
    assert result.net_pay.amount == Decimal("1076750")


def test_non_resident_payroll():
    """Check non-resident employee payroll."""

    result = calculate_payroll(residency="non-resident")

    assert result.paye.amount == Decimal("375500")
    assert result.net_pay.amount == Decimal("1049500")


def test_negative_salary():
    """Reject negative basic salary."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(salary="-100000")


def test_negative_allowances():
    """Reject negative allowances."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(allowances="-50000")


def test_negative_lst():
    """Reject negative Local Service Tax."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(lst="-10000")


def test_excessive_deductions():
    """Reject payroll deductions exceeding gross salary."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(
            salary="500000",
            lst="600000"
        )
