
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
    """Store an employee's payroll calculations."""

    gross_pay: Money
    paye: Money
    employee_nssf: Money
    employer_nssf: Money
    local_service_tax: Money
    net_pay: Money


class PayrollCalculator:
    """Calculate payroll deductions and net salary."""

    EMPLOYEE_NSSF_RATE = Decimal("0.05")
    EMPLOYER_NSSF_RATE = Decimal("0.10")

    def calculate(
        self,
        basic_salary: Money,
        allowances: Money,
        residency: str,
        tax_date: date,
        local_service_tax: Money | None = None
    ) -> PayrollResult:
        """Calculate PAYE, NSSF, LST and net pay."""

        # Validate inputs
        if not isinstance(basic_salary, Money):
            raise InvalidIncomeError(
                "Basic salary must be a Money object."
            )

        if not isinstance(allowances, Money):
            raise InvalidIncomeError(
                "Allowances must be a Money object."
            )

        if basic_salary.amount < 0 or allowances.amount < 0:
            raise InvalidIncomeError(
                "Salary and allowances cannot be negative."
            )

        if local_service_tax is None:
            local_service_tax = Money("0")

        if not isinstance(local_service_tax, Money):
            raise InvalidIncomeError(
                "Local Service Tax must be a Money object."
            )

        if local_service_tax.amount < 0:
            raise InvalidIncomeError(
                "Local Service Tax cannot be negative."
            )

        # Calculate gross pay
        gross_pay = basic_salary + allowances

        # Calculate PAYE
        paye_context = TaxContext(
            tax_date=tax_date,
            income=basic_salary,
            residency=residency,
            details={"allowances": allowances}
        )

        paye_result = PAYETax().calculate(paye_context)

        paye = paye_result.amount

        # Calculate NSSF
        employee_nssf = gross_pay * self.EMPLOYEE_NSSF_RATE
        employer_nssf = gross_pay * self.EMPLOYER_NSSF_RATE

        # Calculate net pay
        net_pay = Money(
            gross_pay.amount
            - paye.amount
            - employee_nssf.amount
            - local_service_tax.amount
        )

        if net_pay.amount < 0:
            raise InvalidIncomeError(
                "Total deductions exceed gross pay."
            )

        return PayrollResult(
            gross_pay=gross_pay,
            paye=paye,
            employee_nssf=employee_nssf,
            employer_nssf=employer_nssf,
            local_service_tax=local_service_tax,
            net_pay=net_pay
        )
