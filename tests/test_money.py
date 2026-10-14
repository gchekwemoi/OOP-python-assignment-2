
"""Tests for the Money class."""

from decimal import Decimal

import pytest

from src.tax_engine.money import Money


def test_money_creation():
    """Money should store the correct UGX amount."""
    amount = Money("1500000")

    assert amount.amount == Decimal("1500000")


def test_money_addition():
    """Two Money objects should be added correctly."""
    salary = Money("1500000")
    allowance = Money("200000")

    result = salary + allowance

    assert result.amount == Decimal("1700000")


def test_money_multiplication():
    """Money should support multiplication by a rate."""
    salary = Money("1500000")

    result = salary * Decimal("0.05")

    assert result.amount == Decimal("75000")


def test_money_comparison():
    """Compare two amounts."""
    smaller = Money("200000")
    larger = Money("1500000")

    assert smaller < larger


def test_money_rounding():
    """Amounts should round to whole shillings."""
    amount = Money("1500.50")

    assert amount.amount == Decimal("1501")


def test_money_representation():
    """Money should display UGX correctly."""
    amount = Money("1500000")

    assert repr(amount) == "UGX 1,500,000"


def test_float_rejected():
    """Floating-point inputs should not be accepted."""
    with pytest.raises(TypeError):
        Money(1500.50)


def test_invalid_money():
    """Invalid numerical values should be rejected."""
    with pytest.raises(ValueError):
        Money("NaN")
