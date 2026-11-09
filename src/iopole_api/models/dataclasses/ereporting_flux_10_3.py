from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from iopole_api.models.dataclasses.ereporting import MonetaryAmount, TaxDetail, drop_none
from iopole_api.models.dataclasses.ereporting_flux_10_1 import TaxPaymentOption


class TransactionCategory(StrEnum):
    TLB1 = "TLB1"  # Livraisons de biens soumises à la TVA
    TPS1 = "TPS1"  # Prestations de services soumises à la TVA
    TNT1 = "TNT1"  # Opérations non soumises à la TVA en France
    TMA1 = "TMA1"  # Opérations relevant du régime de la marge


@dataclass
class TransactionMonetary:
    tax_basis_total_amount: MonetaryAmount  # excluding VAT
    tax_total_amount: MonetaryAmount  # VAT amount

    def to_dict(self) -> dict[str, Any]:
        return {
            "taxBasisTotalAmount": self.tax_basis_total_amount.to_dict(),
            "taxTotalAmount": self.tax_total_amount.to_dict(),
        }


@dataclass
class Transaction:
    category_code: TransactionCategory
    currency: str
    monetary: TransactionMonetary
    tax_details: list[TaxDetail]
    # VAT exigibility, required by Iopole for services (TPS1)
    tax_payment_option: TaxPaymentOption | None = None

    def __post_init__(self) -> None:
        if len(self.currency) != 3:
            raise ValueError(f"currency must be 3 chars, got {self.currency}")
        if self.category_code == TransactionCategory.TPS1 and self.tax_payment_option is None:
            raise ValueError("tax_payment_option is required for TPS1 transactions")

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "categoryCode": self.category_code,
                "currency": self.currency,
                "taxPaymentOption": self.tax_payment_option.to_dict() if self.tax_payment_option else None,
                "monetary": self.monetary.to_dict(),
                "taxDetails": [tax.to_dict() for tax in self.tax_details],
            }
        )


@dataclass
class ReportFlux10_3:
    """Daily summary of B2C transactions, one entry per category code."""

    transaction_date: str
    transactions: list[Transaction]
    store_id: str | None = None
    register_id: str | None = None
    closure_id: str | None = None

    def __post_init__(self) -> None:
        if not self.transactions:
            raise ValueError("transactions must have at least one entry")
        categories = [transaction.category_code for transaction in self.transactions]
        if len(categories) != len(set(categories)):
            raise ValueError(f"each categoryCode must be unique within transactions, got {categories}")

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "transactionDate": self.transaction_date,
                "storeId": self.store_id,
                "registerId": self.register_id,
                "closureId": self.closure_id,
                "transactions": [transaction.to_dict() for transaction in self.transactions],
            }
        )
