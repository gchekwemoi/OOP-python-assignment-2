
"""Automated tests for Uganda payroll and Local Service Tax."""

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
    """Create an employee payroll calculation for testing."""

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
    """No LST is deducted in October."""

    result = calculate_payroll(month=10)

    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.paye.amount == Decimal("338250")
    assert result.net_pay.amount == Decimal("1086750")


def test_payroll_with_allowances():
    """Allowances increase gross pay and deductions."""

    result = calculate_payroll(
        salary="1500000",
        allowances="200000"
    )

    assert result.gross_pay.amount == Decimal("1700000")
    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("100000")
    assert result.paye.amount == Decimal("368250")
    assert result.employee_nssf.amount == Decimal("85000")
    assert result.employer_nssf.amount == Decimal("170000")
    assert result.net_pay.amount == Decimal("1146750")


def test_lst_exemption():
    """LST-exempt employees have no LST deduction."""

    result = calculate_payroll(lst_exempt=True)

    assert result.annual_local_service_tax.amount == Decimal("0")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.paye.amount == Decimal("338250")
    assert result.net_pay.amount == Decimal("1086750")


def test_non_resident_payroll():
    """Calculate non-resident payroll under configured rules."""

    result = calculate_payroll(
        residency="non-resident"
    )

    assert result.annual_local_service_tax.amount == Decimal("100000")
    assert result.local_service_tax.amount == Decimal("100000")
    assert result.paye.amount == Decimal("345500")
    assert result.employee_nssf.amount == Decimal("75000")
    assert result.net_pay.amount == Decimal("979500")


@pytest.mark.parametrize(
    "assessment_income, expected_lst",
    [
        ("0", "0"),
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
    """Check annual LST across all configured income bands."""

    result = PayrollCalculator.calculate_annual_lst(
        Money(assessment_income)
    )

    assert result.amount == Decimal(expected_lst)


def test_no_lst_outside_july():
    """Annual LST is not deducted again outside July."""

    for month in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12):
        result = calculate_payroll(month=month)

        assert result.local_service_tax.amount == Decimal("0")


def test_negative_salary():
    """Reject negative basic salary."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(salary="-100000")


def test_negative_allowances():
    """Reject negative allowances."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(allowances="-50000")


def test_invalid_lst_exemption():
    """LST exemption flag must be Boolean."""

    with pytest.raises(InvalidIncomeError):
        calculate_payroll(lst_exempt="yes")


def test_negative_lst_assessment():
    """Reject negative LST assessment income."""

    with pytest.raises(InvalidIncomeError):
        PayrollCalculator.calculate_annual_lst(
            Money("-100000")
        )


def test_zero_salary():
    """Zero earnings should produce zero deductions."""

    result = calculate_payroll(salary="0")

    assert result.gross_pay.amount == Decimal("0")
    assert result.paye.amount == Decimal("0")
    assert result.employee_nssf.amount == Decimal("0")
    assert result.employer_nssf.amount == Decimal("0")
    assert result.local_service_tax.amount == Decimal("0")
    assert result.net_pay.amount == Decimal("0")
