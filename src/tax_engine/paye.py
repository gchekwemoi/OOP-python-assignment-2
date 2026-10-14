
"""PAYE calculations for the Uganda Tax Engine."""

from decimal import Decimal

from .money import Money
from .models import Tax, TaxContext, TaxResult
from .schedules import get_paye_schedule
from .exceptions import InvalidIncomeError


class PAYETax(Tax):
    """Calculate monthly PAYE for resident and non-resident employees."""

    def calculate(self, ctx: TaxContext) -> TaxResult:
        """Calculate PAYE using the applicable tax schedule."""

        # Step 1: Validate income
        if not isinstance(ctx.income, Money):
            raise InvalidIncomeError(
                "Income must be a Money object."
            )

        if ctx.income.amount < 0:
            raise InvalidIncomeError(
                "Income cannot be negative."
            )

        # Step 2: Get taxable allowances
        allowances = ctx.details.get(
            "allowances",
            Money("0")
        )

        if not isinstance(allowances, Money):
            raise InvalidIncomeError(
                "Allowances must be a Money object."
            )

        if allowances.amount < 0:
            raise InvalidIncomeError(
                "Allowances cannot be negative."
            )

        # Step 3: Calculate taxable income
        taxable_income = ctx.income + allowances
        income = taxable_income.amount

        # Step 4: Retrieve the applicable PAYE schedule
        schedule = get_paye_schedule(
            ctx.tax_date,
            ctx.residency
        )

        # Step 5: Calculate PAYE
        if schedule.residency == "resident":

            if income <= schedule.threshold_1:
                base_tax = Decimal("0")

            elif income <= schedule.threshold_2:
                base_tax = (
                    (income - schedule.threshold_1)
                    * schedule.rate_1
                )

            elif income <= schedule.threshold_3:
                base_tax = (
                    schedule.base_tax_2
                    + (income - schedule.threshold_2)
                    * schedule.rate_2
                )

            else:
                base_tax = (
                    schedule.base_tax_3
                    + (income - schedule.threshold_3)
                    * schedule.rate_3
                )

        else:
            # Non-resident PAYE
            if income <= schedule.threshold_2:
                base_tax = income * schedule.rate_1

            elif income <= schedule.threshold_3:
                base_tax = (
                    schedule.base_tax_2
                    + (income - schedule.threshold_2)
                    * schedule.rate_2
                )

            else:
                base_tax = (
                    schedule.base_tax_3
                    + (income - schedule.threshold_3)
                    * schedule.rate_3
                )

        # Step 6: Calculate additional tax above UGX 10 million
        if income > schedule.surcharge_threshold:
            surcharge = (
                (income - schedule.surcharge_threshold)
                * schedule.surcharge_rate
            )
        else:
            surcharge = Decimal("0")

        # Step 7: Calculate total PAYE
        total_paye = base_tax + surcharge

        # Step 8: Return results
        return TaxResult(
            tax_name="PAYE",
            amount=Money(total_paye),
            breakdown={
                "taxable_income": taxable_income,
                "residency": schedule.residency,
                "base_paye": Money(base_tax),
                "surcharge": Money(surcharge),
                "tax_date": ctx.tax_date
            }
        )
