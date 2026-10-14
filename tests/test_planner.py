
"""Tests for the TaxPlanner extension."""

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.paye import PAYETax
from src.tax_engine.corporate_tax import CorporateIncomeTax
from src.tax_engine.planner import TaxPlanner
from src.tax_engine.exceptions import TaxError


TAX_DATE = date(2026, 10, 1)


def company_context(revenue, deductions):
    """Create a corporate tax scenario."""
    return TaxContext(
        tax_date=TAX_DATE,
        income=Money(revenue),
        details={
            "allowable_deductions": Money(deductions)
        }
    )


def employee_context(income):
    """Create a resident PAYE scenario."""
    return TaxContext(
        tax_date=TAX_DATE,
        income=Money(income),
        residency="resident"
    )


def test_corporate_tax_comparison():
    """Compare two corporate income tax scenarios."""

    planner = TaxPlanner(CorporateIncomeTax())

    scenario_a = company_context(
        "250000000", "150000000"
    )

    scenario_b = company_context(
        "250000000", "180000000"
    )

    result = planner.compare(scenario_a, scenario_b)

    assert result.scenario_a.amount.amount == Decimal("30000000")
    assert result.scenario_b.amount.amount == Decimal("21000000")
    assert result.difference.amount == Decimal("9000000")
    assert result.lower_tax_scenario == "Scenario B"


def test_paye_comparison():
    """Compare PAYE on two different salaries."""

    planner = TaxPlanner(PAYETax())

    scenario_a = employee_context("1500000")
    scenario_b = employee_context("1000000")

    result = planner.compare(scenario_a, scenario_b)

    assert result.scenario_a.amount.amount == Decimal("338250")
    assert result.scenario_b.amount.amount == Decimal("188250")
    assert result.difference.amount == Decimal("150000")
    assert result.lower_tax_scenario == "Scenario B"


def test_equal_tax_scenarios():
    """Equal scenarios should produce equal tax."""

    planner = TaxPlanner(CorporateIncomeTax())

    scenario_a = company_context(
        "100000000", "50000000"
    )

    scenario_b = company_context(
        "100000000", "50000000"
    )

    result = planner.compare(scenario_a, scenario_b)

    assert result.difference.amount == Decimal("0")
    assert result.lower_tax_scenario == "Equal tax"


def test_scenario_a_has_lower_tax():
    """Identify when Scenario A has lower tax."""

    planner = TaxPlanner(CorporateIncomeTax())

    scenario_a = company_context(
        "100000000", "80000000"
    )

    scenario_b = company_context(
        "100000000", "50000000"
    )

    result = planner.compare(scenario_a, scenario_b)

    assert result.difference.amount == Decimal("-9000000")
    assert result.lower_tax_scenario == "Scenario A"


def test_invalid_calculator():
    """Reject objects that do not implement Tax."""

    with pytest.raises(TaxError):
        TaxPlanner("not a tax calculator")


def test_invalid_context():
    """Reject an invalid scenario context."""

    planner = TaxPlanner(CorporateIncomeTax())

    with pytest.raises(TaxError):
        planner.compare(
            "invalid context",
            company_context("100000000", "50000000")
        )


def test_different_tax_dates():
    """Reject scenarios with different tax dates."""

    planner = TaxPlanner(CorporateIncomeTax())

    scenario_a = company_context(
        "100000000", "50000000"
    )

    scenario_b = TaxContext(
        tax_date=date(2026, 11, 1),
        income=Money("100000000"),
        details={
            "allowable_deductions": Money("50000000")
        }
    )

    with pytest.raises(TaxError):
        planner.compare(scenario_a, scenario_b)
