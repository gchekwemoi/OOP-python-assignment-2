
"""Automated tests for Uganda payroll calculations."""

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.payroll import PayrollCalculator
from src.tax_engine.exceptions import InvalidIncomeError


def calculate_payroll(
    salary="1500000",
    allowances="0",
    residency="resident",
    month=7,
    lst_exempt=False
):
    """Calculate payroll for a test employee."""

    calculator = PayrollCalculator()

    return calculator.calculate(
        basic_salary=Money(salary),
        allowances=Money(allowances),
        residency=residency,
        tax_date=date(2026, month, 1),
        lst_exempt=lst_exempt
    )


def test_july_payroll():
    """Full annual LST is deducted once in July."""

    result = calculate_payroll()

    assert result.gross_pay.amount == Decimal("1500000")
    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("100000")
    assert result.paye.amount == Decimal("308250")
    assert result.employee_nssf.amount == Decimal("75000")
    assert result.employer_nssf.amount == Decimal("150000")
    assert result.net_pay.amount == Decimal("1016750")


def test_october_payroll():
    """No LST deduction occurs in October."""

    result = calculate_payroll(month=10)

    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.paye.amount == Decimal("338250")
    assert result.net_pay.amount == Decimal("1086750")


def test_payroll_with_allowances():
    """Allowances increase gross pay and taxable income."""

    result = calculate_payroll(
        salary="1500000",
        allowances="200000"
    )

    assert result.gross_pay.amount == Decimal("1700000")
    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("100000")
    assert result.paye.amount == Decimal("368250")
    assert result.employee_nssf.amount == Decimal("85000")
    assert result.net_pay.amount == Decimal("1146750")


def test_lst_exemption():
    """LST-exempt employees should not pay LST."""

    result = calculate_payroll(lst_exempt=True)

    assert result.annual_local_service_tax.amount == Decimal("0")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.paye.amount == Decimal("338250")
    assert result.net_pay.amount == Decimal("1086750")


def test_non_resident_payroll():
    """Check PAYE, NSSF and LST for a non-resident."""

    result = calculate_payroll(residency="non-resident")

    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("100000")
    assert result.paye.amount == Decimal("345500")
    assert result.net_pay.amount == Decimal("979500")


@pytest.mark.parametrize(
    "assessment_income, expected_lst",
    [
        ("100000", "0"),
        ("100001", "5000"),
        ("200000", "5000"),
        ("200001", "10000"),
        ("300000", "10000"),
        ("400000", "20000"),
        ("500000", "30000"),
        ("600000", "40000"),
        ("700000", "60000"),
        ("800000", "70000"),
        ("900000", "80000"),
        ("1000000", "90000"),
        ("1000001", "100000")
    ]
)
def test_lst_bands(assessment_income, expected_lst):
    """Verify LST rates and income band boundaries."""

    result = PayrollCalculator.calculate_annual_lst(
        Money(assessment_income)
    )

    assert result.amount == Decimal(expected_lst)


def test_negative_salary():
    """Reject negative basic salary."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(salary="-100000")


def test_negative_allowances():
    """Reject negative allowances."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(allowances="-50000")


def test_invalid_lst_exemption():
    """The exemption flag must be a Boolean."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(lst_exempt="yes")


def test_zero_salary():
    """Zero income should produce zero payroll deductions."""

    result = calculate_payroll(salary="0")

    assert result.paye.amount == Decimal("0")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.employee_nssf.amount == Decimal("0")
    assert result.net_pay.amount == Decimal("0")
