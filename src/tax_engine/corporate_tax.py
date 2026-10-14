
"""Corporate Income Tax module for Uganda."""

from decimal import Decimal

from .money import Money
from .models import Tax, TaxContext, TaxResult
from .exceptions import InvalidIncomeError, TaxError


class CorporateIncomeTax(Tax):
    """Calculate standard corporate income tax in Uganda."""

    CIT_RATE = Decimal("0.30")

    def calculate(self, ctx: TaxContext) -> TaxResult:
        """Calculate CIT on chargeable income."""

        # Step 1: Get annual revenue
        revenue = ctx.income

        if not isinstance(revenue, Money):
            raise InvalidIncomeError(
                "Revenue must be a Money object."
            )

        if revenue.amount < 0:
            raise InvalidIncomeError(
                "Revenue cannot be negative."
            )

        # Step 2: Get allowable deductions
        deductions = ctx.details.get(
            "allowable_deductions",
            Money("0")
        )

        if not isinstance(deductions, Money):
            raise TaxError(
                "Allowable deductions must be a Money object."
            )

        if deductions.amount < 0:
            raise TaxError(
                "Allowable deductions cannot be negative."
            )

        # Step 3: Calculate profit or loss
        profit_or_loss = revenue.amount - deductions.amount

        # Step 4: Chargeable income cannot be negative
        chargeable_income = Money(
            max(Decimal("0"), profit_or_loss)
        )

        # Step 5: Calculate CIT
        tax_payable = chargeable_income * self.CIT_RATE

        # Step 6: Report excess deductions separately
        excess_deductions = Money(
            max(Decimal("0"), -profit_or_loss)
        )

        # Step 7: Return tax result
        return TaxResult(
            tax_name="Corporate Income Tax",
            amount=tax_payable,
            breakdown={
                "revenue": revenue,
                "allowable_deductions": deductions,
                "chargeable_income": chargeable_income,
                "tax_rate": self.CIT_RATE,
                "excess_deductions": excess_deductions,
                "tax_date": ctx.tax_date
            }
        )
