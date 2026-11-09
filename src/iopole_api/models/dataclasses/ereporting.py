from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class VatCategoryCode(StrEnum):
    """UNTDID 5305 VAT category codes accepted by the e-reporting endpoints."""

    STANDARD = "S"  # Taux de TVA standard (taux normal, intermédiaire ou réduit)
    ZERO_RATED = "Z"  # Taux zéro
    EXEMPT = "E"  # Exonéré de TVA
    REVERSE_CHARGE = "AE"  # Autoliquidation
    INTRA_COMMUNITY = "K"  # Livraison intracommunautaire de biens
    EXPORT = "G"  # Exonéré pour export hors UE
    NOT_SUBJECT = "O"  # Hors du champ d'application de la TVA
    CANARY_ISLANDS = "L"
    CEUTA_MELILLA = "M"


def drop_none(data: dict[str, Any]) -> dict[str, Any]:
    """Leave optional fields out of the payload instead of sending explicit nulls."""
    return {key: value for key, value in data.items() if value is not None}


@dataclass
class MonetaryAmount:
    """An amount, optionally qualified with a currency.

    Zero is a legitimate amount (0% VAT, reverse charge) and aggregated B2C
    transactions can be negative once credit notes are netted.
    """

    amount: float
    currency: str | None = None

    def __post_init__(self) -> None:
        if self.amount is None or not math.isfinite(self.amount):
            raise ValueError(f"amount must be a finite number, got {self.amount}")
        if self.currency and len(self.currency) != 3:
            raise ValueError(f"currency must be 3 chars, got {self.currency}")

    def to_dict(self) -> dict[str, Any]:
        return drop_none({"amount": round(float(self.amount), 2), "currency": self.currency})


@dataclass
class Monetary:
    invoice_currency: str
    tax_basis_total_amount: MonetaryAmount  # excluding VAT
    tax_total_amount: MonetaryAmount  # VAT amount

    def __post_init__(self) -> None:
        if len(self.invoice_currency) != 3:
            raise ValueError(f"invoice_currency must be 3 chars, got {self.invoice_currency}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "invoiceCurrency": self.invoice_currency,
            "taxBasisTotalAmount": self.tax_basis_total_amount.to_dict(),
            "taxTotalAmount": self.tax_total_amount.to_dict(),
        }


@dataclass
class TaxDetail:
    """VAT rate breakdown line.

    `code` is required by the invoice e-reporting (flux 10.1) and is not part of
    the B2C transaction payload (flux 10.3).
    """

    taxable_amount: MonetaryAmount
    tax_amount: MonetaryAmount
    percent: float
    code: VatCategoryCode | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.percent <= 100:
            raise ValueError(f"percent must be 0–100, got {self.percent}")

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "taxableAmount": self.taxable_amount.to_dict(),
                "taxAmount": self.tax_amount.to_dict(),
                "percent": round(float(self.percent), 2),
                "code": self.code,
            }
        )
