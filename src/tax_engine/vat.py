
"""VAT calculator for the Uganda Tax Engine."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from .money import Money
from .models import Tax, TaxContext, TaxResult
from .exceptions import TaxError


STANDARD_VAT_RATE = Decimal("0.18")

SupplyType = Literal["standard", "zero", "exempt"]
InvoiceType = Literal["sale", "purchase"]


@dataclass
class VATInvoice:
    """Represent a VAT-exclusive sales or purchase invoice."""

    invoice_number: str
    invoice_type: InvoiceType
    amount: Money
    supply_type: SupplyType
    input_vat_eligible: bool = True

    def __post_init__(self):
        """Validate invoice information."""

        if not self.invoice_number.strip():
            raise TaxError("Invoice number is required.")

        if self.invoice_type not in ("sale", "purchase"):
            raise TaxError("Invalid invoice type.")

        if self.supply_type not in (
            "standard", "zero", "exempt"
        ):
            raise TaxError("Invalid supply type.")

        if not isinstance(self.amount, Money):
            raise TaxError("Amount must be a Money object.")

        if self.amount.amount < 0:
            raise TaxError("Invoice amount cannot be negative.")

        if not isinstance(self.input_vat_eligible, bool):
            raise TaxError(
                "Input VAT eligibility must be True or False."
            )

    def vat_amount(self) -> Money:
        """Calculate VAT for this invoice."""

        if self.supply_type == "standard":
            return self.amount * STANDARD_VAT_RATE

        return Money("0")


class VATTax(Tax):
    """Calculate VAT payable from sales and purchases."""

    def calculate(self, ctx: TaxContext) -> TaxResult:
        """Calculate output VAT and eligible input VAT."""

        invoices = ctx.details.get("invoices", [])

        if not isinstance(invoices, list):
            raise TaxError("Invoices must be supplied as a list.")

        if not all(
            isinstance(invoice, VATInvoice)
            for invoice in invoices
        ):
            raise TaxError(
                "Every invoice must be a VATInvoice object."
            )

        output_vat = Money("0")
        input_vat = Money("0")

        for invoice in invoices:

            vat = invoice.vat_amount()

            # VAT charged on taxable sales
            if invoice.invoice_type == "sale":
                output_vat = output_vat + vat

            # Eligible VAT paid on purchases
            elif (
                invoice.invoice_type == "purchase"
                and invoice.input_vat_eligible
            ):
                input_vat = input_vat + vat

        # Net VAT position
        net_vat = Money(
            output_vat.amount - input_vat.amount
        )

        # Amount payable cannot be negative
        vat_payable = Money(
            max(Decimal("0"), net_vat.amount)
        )

        # Potential excess credit (not an approved refund)
        excess_input_vat = Money(
            max(Decimal("0"), -net_vat.amount)
        )

        return TaxResult(
            tax_name="VAT",
            amount=vat_payable,
            breakdown={
                "output_vat": output_vat,
                "input_vat": input_vat,
                "net_vat": net_vat,
                "excess_input_vat": excess_input_vat,
                "invoice_count": len(invoices)
            }
        )
