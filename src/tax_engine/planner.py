
"""Tax scenario comparison for the Uganda Tax Engine."""

from dataclasses import dataclass

from .money import Money
from .models import Tax, TaxContext, TaxResult
from .exceptions import TaxError


@dataclass
class TaxComparison:
    """Store the results of two tax scenarios."""

    scenario_a: TaxResult
    scenario_b: TaxResult
    difference: Money
    lower_tax_scenario: str


class TaxPlanner:
    """Compare two scenarios using an existing tax calculator."""

    def __init__(self, tax_calculator: Tax):
        """Accept a tax calculator implementing the Tax interface."""

        if not isinstance(tax_calculator, Tax):
            raise TaxError(
                "TaxPlanner requires a valid Tax calculator."
            )

        self.tax_calculator = tax_calculator

    def compare(
        self,
        context_a: TaxContext,
        context_b: TaxContext
    ) -> TaxComparison:
        """Compare the calculated taxes of two scenarios."""

        if not isinstance(context_a, TaxContext):
            raise TaxError("Scenario A requires a TaxContext.")

        if not isinstance(context_b, TaxContext):
            raise TaxError("Scenario B requires a TaxContext.")

        if context_a.tax_date != context_b.tax_date:
            raise TaxError(
                "Scenarios must use the same tax date."
            )

        # Reuse the existing tax calculator
        result_a = self.tax_calculator.calculate(context_a)
        result_b = self.tax_calculator.calculate(context_b)

        # Compare tax amounts
        difference = Money(
            result_a.amount.amount - result_b.amount.amount
        )

        if result_a.amount.amount < result_b.amount.amount:
            lower_tax = "Scenario A"

        elif result_b.amount.amount < result_a.amount.amount:
            lower_tax = "Scenario B"

        else:
            lower_tax = "Equal tax"

        return TaxComparison(
            scenario_a=result_a,
            scenario_b=result_b,
            difference=difference,
            lower_tax_scenario=lower_tax
        )
