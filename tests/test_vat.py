
"""Automated tests for Uganda VAT calculations."""

from datetime import date
from decimal import Decimal

import pytest

from src.tax_engine.money import Money
from src.tax_engine.models import TaxContext
from src.tax_engine.vat import VATInvoice, VATTax
from src.tax_engine.exceptions import TaxError


TAX_DATE = date(2026, 10, 1)


def calculate_vat(invoices):
    """Calculate VAT for a list of invoices."""
    context = TaxContext(
        tax_date=TAX_DATE,
        details={"invoices": invoices}
    )
    return VATTax().calculate(context)


def make_invoice(number, kind, amount, supply, eligible=True):
    """Create an invoice for testing."""
    return VATInvoice(
        invoice_number=number,
        invoice_type=kind,
        amount=Money(amount),
        supply_type=supply,
        input_vat_eligible=eligible
    )


def test_standard_rated_sale():
    """Standard-rated sales attract 18% VAT."""
    invoice = make_invoice("S001", "sale", "1000000", "standard")
    result = calculate_vat([invoice])

    assert result.amount.amount == Decimal("180000")


def test_zero_rated_sale():
    """Zero-rated sales attract 0% output VAT."""
    invoice = make_invoice("S002", "sale", "1000000", "zero")
    result = calculate_vat([invoice])

    assert result.amount.amount == Decimal("0")


def test_exempt_sale():
    """Exempt sales have no output VAT."""
    invoice = make_invoice("S003", "sale", "1000000", "exempt")
    result = calculate_vat([invoice])

    assert result.amount.amount == Decimal("0")


def test_input_vat():
    """Eligible input VAT reduces VAT payable."""
    invoices = [
        make_invoice("S004", "sale", "5000000", "standard"),
        make_invoice("P001", "purchase", "2000000", "standard")
    ]

    result = calculate_vat(invoices)

    assert result.breakdown["output_vat"].amount == Decimal("900000")
    assert result.breakdown["input_vat"].amount == Decimal("360000")
    assert result.amount.amount == Decimal("540000")


def test_ineligible_input_vat():
    """Ineligible input VAT must not be claimed."""
    invoices = [
        make_invoice("S005", "sale", "1000000", "standard"),
        make_invoice(
            "P002", "purchase", "500000", "standard", False
        )
    ]

    result = calculate_vat(invoices)

    assert result.breakdown["input_vat"].amount == Decimal("0")
    assert result.amount.amount == Decimal("180000")


def test_excess_input_vat():
    """Excess input VAT is reported separately."""
    invoices = [
        make_invoice("S006", "sale", "1000000", "standard"),
        make_invoice("P003", "purchase", "2000000", "standard")
    ]

    result = calculate_vat(invoices)

    assert result.amount.amount == Decimal("0")
    assert result.breakdown["net_vat"].amount == Decimal("-180000")
    assert result.breakdown["excess_input_vat"].amount == Decimal("180000")


def test_empty_invoices():
    """An empty list produces zero VAT."""
    result = calculate_vat([])

    assert result.amount.amount == Decimal("0")
    assert result.breakdown["invoice_count"] == 0


def test_invalid_supply_type():
    """Reject an unsupported VAT classification."""
    with pytest.raises(TaxError):
        make_invoice("S007", "sale", "100000", "invalid")


def test_negative_invoice():
    """Reject negative invoice amounts."""
    with pytest.raises(TaxError):
        make_invoice("S008", "sale", "-100000", "standard")


def test_invalid_invoice_collection():
    """Reject data that is not a list of invoices."""
    context = TaxContext(
        tax_date=TAX_DATE,
        details={"invoices": "not a list"}
    )

    with pytest.raises(TaxError):
        VATTax().calculate(context)


def test_mixed_supplies():
    """Check VAT on standard, zero-rated and exempt sales."""
    invoices = [
        make_invoice("S009", "sale", "5000000", "standard"),
        make_invoice("S010", "sale", "1000000", "zero"),
        make_invoice("S011", "sale", "500000", "exempt"),
        make_invoice("P004", "purchase", "2000000", "standard")
    ]

    result = calculate_vat(invoices)

    assert result.amount.amount == Decimal("540000")
    assert result.breakdown["invoice_count"] == 4
