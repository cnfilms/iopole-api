from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from iopole_api.models.dataclasses.ereporting import Monetary, TaxDetail


class TransactionCategory(str, Enum):
    TLB1 = "TLB1"
    TPS1 = "TPS1"
    TNT1 = "TNT1"
    TMA1 = "TMA1"


@dataclass
class Transaction:
    category_code: TransactionCategory
    currency: str
    monetary: Monetary
    tax_details: list[TaxDetail]

    def to_dict(self) -> dict[str, Any]:
        return {
            "categoryCode": self.category_code,
            "currency": self.currency,
            "monetary": self.monetary.to_dict(),
            "taxDetails": [tax.to_dict() for tax in self.tax_details],
        }


@dataclass
class ReportFlux10_3:
    transaction_date: str
    transactions: list[Transaction]

    def to_dict(self) -> dict[str, Any]:
        return {
            "transactionDate": self.transaction_date,
            "transactions": [
                transaction.to_dict() for transaction in self.transactions
            ],
        }
