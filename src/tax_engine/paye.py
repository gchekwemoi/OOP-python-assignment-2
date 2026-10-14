
"""PAYE calculator for the Uganda Tax Engine."""

from decimal import Decimal

from .money import Money
from .models import Tax, TaxContext, TaxResult
from .schedules import get_paye_schedule
from .exceptions import InvalidIncomeError


class PAYETax(Tax):
    """Calculate monthly PAYE for employees in Uganda."""

    def calculate(self, ctx: TaxContext) -> TaxResult:
        """Calculate PAYE using the appropriate tax schedule."""

        # Step 1: Validate income
        if not isinstance(ctx.income, Money):
            raise InvalidIncomeError(
                "Income must be a Money object."
            )

        if ctx.income.amount < 0:
            raise InvalidIncomeError(
                "Income cannot be negative."
            )

        # Step 2: Obtain taxable allowances
        allowances = ctx.details.get(
            "allowances", Money("0")
        )

        if not isinstance(allowances, Money):
            raise InvalidIncomeError(
                "Allowances must be a Money object."
            )

        if allowances.amount < 0:
            raise InvalidIncomeError(
                "Allowances cannot be negative."
            )

        # Step 3: Calculate total taxable income
        taxable_income = ctx.income + allowances
        income = taxable_income.amount

        # Step 4: Select the appropriate PAYE schedule
        schedule = get_paye_schedule(
            ctx.tax_date,
            ctx.residency
        )

        # Step 5: Apply progressive tax bands
        if income <= schedule.threshold_1:
            tax = income * (
                Decimal("0")
                if schedule.residency == "resident"
                else schedule.rate_1
            )

        elif income <= schedule.threshold_2:
            if schedule.residency == "resident":
                tax = (
                    income - schedule.threshold_1
                ) * schedule.rate_1
            else:
                tax = (
                    schedule.threshold_2 * schedule.rate_1
                    + (income - schedule.threshold_2)
                    * schedule.rate_2
                )

        elif income <= schedule.threshold_3:
            if schedule.residency == "resident":
                tax = (
                    schedule.base_tax_2
                    + (income - schedule.threshold_2)
                    * schedule.rate_2
                )
            else:
                tax = (
                    schedule.base_tax_2
                    + (income - schedule.threshold_2)
                    * schedule.rate_2
                )

        else:
            tax = (
                schedule.base_tax_3
                + (income - schedule.threshold_3)
                * schedule.rate_3
            )

        # Step 6: Apply high-income surcharge
        if income > schedule.surcharge_threshold:
            surcharge = (
                income - schedule.surcharge_threshold
            ) * schedule.surcharge_rate

            tax += surcharge
        else:
            surcharge = Decimal("0")

        # Step 7: Return the result
        return TaxResult(
            tax_name="PAYE",
            amount=Money(tax),
            breakdown={
                "taxable_income": taxable_income,
                "residency": schedule.residency,
                "base_paye": Money(tax - surcharge),
                "surcharge": Money(surcharge),
                "tax_date": ctx.tax_date
            }
        )
