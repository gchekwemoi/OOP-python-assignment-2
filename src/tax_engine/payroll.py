
"""Payroll calculations for the Uganda Tax Engine."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from .money import Money
from .models import TaxContext
from .paye import PAYETax
from .exceptions import InvalidIncomeError


@dataclass
class PayrollResult:
    """Store monthly employee payroll results."""

    gross_pay: Money
    paye: Money
    employee_nssf: Money
    employer_nssf: Money
    local_service_tax: Money
    annual_local_service_tax: Money
    net_pay: Money


class PayrollCalculator:
    """Calculate PAYE, NSSF, LST and net salary."""

    EMPLOYEE_NSSF_RATE = Decimal("0.05")
    EMPLOYER_NSSF_RATE = Decimal("0.10")

    # Monthly assessment income limits and annual LST in UGX.
    LST_BANDS = [
        (Decimal("100000"), Decimal("0")),
        (Decimal("200000"), Decimal("5000")),
        (Decimal("300000"), Decimal("10000")),
        (Decimal("400000"), Decimal("20000")),
        (Decimal("500000"), Decimal("30000")),
        (Decimal("600000"), Decimal("40000")),
        (Decimal("700000"), Decimal("60000")),
        (Decimal("800000"), Decimal("70000")),
        (Decimal("900000"), Decimal("80000")),
        (Decimal("1000000"), Decimal("90000"))
    ]

    @classmethod
    def calculate_annual_lst(
        cls,
        assessment_income: Money
    ) -> Money:
        """Determine annual LST from monthly assessment income."""

        if not isinstance(assessment_income, Money):
            raise InvalidIncomeError(
                "LST assessment income must be Money."
            )

        if assessment_income.amount < 0:
            raise InvalidIncomeError(
                "LST assessment income cannot be negative."
            )

        for upper_limit, annual_tax in cls.LST_BANDS:
            if assessment_income.amount <= upper_limit:
                return Money(annual_tax)

        return Money("100000")

    def calculate(
        self,
        basic_salary: Money,
        allowances: Money,
        residency: str,
        tax_date: date,
        lst_exempt: bool = False
    ) -> PayrollResult:
        """Calculate payroll with annual LST deducted in July."""

        # Validate inputs
        if not isinstance(basic_salary, Money):
            raise InvalidIncomeError(
                "Basic salary must be a Money object."
            )

        if not isinstance(allowances, Money):
            raise InvalidIncomeError(
                "Allowances must be a Money object."
            )

        if basic_salary.amount < 0:
            raise InvalidIncomeError(
                "Basic salary cannot be negative."
            )

        if allowances.amount < 0:
            raise InvalidIncomeError(
                "Allowances cannot be negative."
            )

        if not isinstance(lst_exempt, bool):
            raise InvalidIncomeError(
                "lst_exempt must be True or False."
            )

        # Calculate gross salary
        gross_pay = basic_salary + allowances

        # Reuse the existing PAYE calculator
        paye_calculator = PAYETax()

        # Initial PAYE for determining LST assessment income
        initial_context = TaxContext(
            tax_date=tax_date,
            income=gross_pay,
            residency=residency
        )

        initial_paye = paye_calculator.calculate(
            initial_context
        ).amount

        # LST assessment income = gross salary - initial PAYE
        assessment_income = Money(
            gross_pay.amount - initial_paye.amount
        )

        # Determine annual LST liability
        if lst_exempt:
            annual_lst = Money("0")
        else:
            annual_lst = self.calculate_annual_lst(
                assessment_income
            )

        # Assignment assumption:
        # Deduct the entire annual LST once, in July.
        if tax_date.month == 7:
            lst_deduction = annual_lst
        else:
            lst_deduction = Money("0")

        # Adjust taxable pay for the current LST deduction
        taxable_pay = Money(
            max(
                Decimal("0"),
                gross_pay.amount - lst_deduction.amount
            )
        )

        # Calculate final PAYE
        paye_context = TaxContext(
            tax_date=tax_date,
            income=taxable_pay,
            residency=residency
        )

        paye = paye_calculator.calculate(
            paye_context
        ).amount

        # Calculate employee and employer NSSF
        employee_nssf = (
            gross_pay * self.EMPLOYEE_NSSF_RATE
        )

        employer_nssf = (
            gross_pay * self.EMPLOYER_NSSF_RATE
        )

        # Calculate net salary
        net_pay = Money(
            gross_pay.amount
            - paye.amount
            - employee_nssf.amount
            - lst_deduction.amount
        )

        if net_pay.amount < 0:
            raise InvalidIncomeError(
                "Total deductions exceed gross salary."
            )

        return PayrollResult(
            gross_pay=gross_pay,
            paye=paye,
            employee_nssf=employee_nssf,
            employer_nssf=employer_nssf,
            local_service_tax=lst_deduction,
            annual_local_service_tax=annual_lst,
            net_pay=net_pay
        )
