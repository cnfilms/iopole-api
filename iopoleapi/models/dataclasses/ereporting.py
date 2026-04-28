from dataclasses import dataclass
from typing import Optional


@dataclass
class MonetaryAmount:
    """An amount, optionally qualified with a currency."""
    amount: float
    currency: Optional[str] = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError(f"amount must be > 0, got {self.amount}")
        if self.currency and len(self.currency) != 3:
            raise ValueError(f"currency must be 3 chars, got {self.currency}")

    def to_dict(self):
        return {
            "amount": float(self.amount),
            "currency": self.currency
        }


@dataclass
class Monetary:
    invoice_currency: str
    tax_basis_total_amount: MonetaryAmount  # excluding VAT
    tax_total_amount: MonetaryAmount  # VAT amount

    def __post_init__(self):
        if len(self.invoice_currency) != 3:
            raise ValueError(f"invoice_currency must be 3 chars, got {self.invoice_currency}")

    def to_dict(self):
        return {
            "invoiceCurrency": self.invoice_currency,
            "taxBasisTotalAmount": self.tax_basis_total_amount.to_dict(),
            "taxTotalAmount": self.tax_total_amount.to_dict()
        }


@dataclass
class TaxDetail:
    """VAT rate breakdown line."""
    taxable_amount: MonetaryAmount
    tax_amount: MonetaryAmount
    percent: float

    def __post_init__(self):
        if not 0 <= self.percent <= 100:
            raise ValueError(f"percent must be 0–100, got {self.percent}")

    def to_dict(self):
        return {
            "taxableAmount": self.taxable_amount.to_dict(),
            "taxAmount": self.tax_amount.to_dict(),
            "percent": float(self.percent)
        }
