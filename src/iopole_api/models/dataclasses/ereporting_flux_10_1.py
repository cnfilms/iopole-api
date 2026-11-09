from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from iopole_api.models.dataclasses.ereporting import Monetary, MonetaryAmount, TaxDetail, drop_none


class InvoiceTypeCode(StrEnum):
    """UNTDID 1001 invoice type codes relevant to French e-reporting."""

    COMMERCIAL_INVOICE = "380"
    CREDIT_NOTE = "381"
    DEBIT_NOTE = "383"
    CORRECTED_INVOICE = "384"
    PREPAYMENT_INVOICE = "386"
    SELF_BILLED_INVOICE = "389"


class ProcessType(StrEnum):
    """Cadre de facturation (BT-23), as accepted by Iopole.

    B = biens, S = services, M = facture double (biens et services non accessoires).
    """

    B1 = "B1"  # Dépôt d'une facture de biens
    S1 = "S1"  # Dépôt d'une facture de services
    M1 = "M1"  # Dépôt d'une facture double
    B2 = "B2"  # Dépôt d'une facture déjà payée (biens)
    S2 = "S2"  # Dépôt d'une facture déjà payée (services)
    M2 = "M2"  # Dépôt d'une facture double déjà payée
    S3 = "S3"  # Dépôt d'une facture de services à valider par un tiers
    B4 = "B4"  # Dépôt d'une facture définitive après acompte (biens)
    S4 = "S4"  # Dépôt d'une facture définitive après acompte (services)
    M4 = "M4"  # Dépôt d'une facture double définitive après acompte
    S5 = "S5"  # Dépôt par un sous-traitant
    S6 = "S6"  # Dépôt par un cotraitant
    B7 = "B7"  # Facture de biens déjà e-reportée (TVA déjà collectée)
    S7 = "S7"  # Facture de services déjà e-reportée (TVA déjà collectée)


class TaxPaymentIopCode(StrEnum):
    """Iopole shorthand codes for VAT exigibility (when VAT becomes due)."""

    INVOICE_DATE = "INVOICE_DATE"  # TVA sur les débits
    DELIVERY_DATE = "DELIVERY_DATE"  # TVA à la livraison (biens)
    PAYMENT_DATE = "PAYMENT_DATE"  # TVA sur les encaissements (services)


class TaxPaymentUntdidCode(StrEnum):
    """UNTDID 2005 — standard payment means timing codes."""

    INVOICE_DATE = "3"
    DELIVERY_DATE = "35"
    PAYMENT_DATE = "72"


@dataclass
class TaxPaymentOption:
    """Exactly one of iopCode or code must be provided."""

    iop_code: TaxPaymentIopCode | None = None
    code: TaxPaymentUntdidCode | None = None

    def __post_init__(self) -> None:
        if self.iop_code is None and self.code is None:
            raise ValueError("Provide either 'iop_code' or 'code'.")
        if self.iop_code is not None and self.code is not None:
            raise ValueError("Provide only one of 'iop_code' or 'code', not both.")

    def to_dict(self) -> dict[str, Any]:
        if self.iop_code:
            return {"iopCode": self.iop_code}
        # The UNTDID code is an integer in the Iopole schema
        return {"code": int(self.code)}  # type: ignore[arg-type]


class IdentifierScheme(StrEnum):
    """ICD schemes used to identify parties in French e-reporting."""

    SIREN = "0002"
    SIRET = "0009"
    EU_VAT_NUMBER = "0223"  # Entité UE hors France : numéro de TVA intracommunautaire
    INDIVIDUAL = "0226"  # Particulier
    NON_EU = "0227"  # Entité hors UE
    RIDET = "0228"  # Nouvelle-Calédonie
    TAHITI = "0229"  # Polynésie française


@dataclass
class PartyIdentifier:
    """ICD scheme + value pair."""

    scheme: str  # ICD code, e.g. "0002"
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError(f"identifier value is required (scheme {self.scheme})")

    def to_dict(self) -> dict[str, Any]:
        return {"scheme": self.scheme, "value": self.value}


@dataclass
class PostalAddress:
    country: str

    def __post_init__(self) -> None:
        if len(self.country) != 2:
            raise ValueError(f"country must be 2 chars, got {self.country}")

    def to_dict(self) -> dict[str, Any]:
        return {"country": self.country.upper()}


@dataclass
class Seller:
    identifier: PartyIdentifier
    postal_address: PostalAddress
    name: str | None = None
    vat_number: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "name": self.name,
                "vatNumber": self.vat_number,
                "identifier": self.identifier.to_dict(),
                "postalAddress": self.postal_address.to_dict(),
            }
        )


@dataclass
class Buyer:
    identifier: PartyIdentifier
    postal_address: PostalAddress
    name: str | None = None
    vat_number: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "identifier": self.identifier.to_dict(),
                "postalAddress": self.postal_address.to_dict(),
                "name": self.name,
                "vatNumber": self.vat_number,
            }
        )


@dataclass
class InvoiceLine:
    line_id: str | None = None
    description: str | None = None
    quantity: float | None = None
    unit_code: str | None = None
    net_amount: MonetaryAmount | None = None
    tax_percent: float | None = None

    def __post_init__(self) -> None:
        if self.tax_percent is not None and not 0 <= self.tax_percent <= 100:
            raise ValueError(f"tax_percent must be 0–100, got {self.tax_percent}")

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "lineId": self.line_id,
                "description": self.description,
                "quantity": self.quantity,
                "unitCode": self.unit_code,
                "netAmount": self.net_amount.to_dict() if self.net_amount else None,
                "taxPercent": float(self.tax_percent) if self.tax_percent is not None else None,
            }
        )


@dataclass
class Invoice:
    invoice_id: str
    invoice_date: str
    invoice_type: InvoiceTypeCode
    process_type: ProcessType
    monetary: Monetary
    tax_details: list[TaxDetail]
    seller: Seller
    buyer: Buyer
    # Omit when nothing remains due (e.g. invoice already paid)
    invoice_due_date: str | None = None
    tax_payment_option: TaxPaymentOption | None = None
    lines: list[InvoiceLine] | None = None

    def __post_init__(self) -> None:
        if len(self.invoice_id) > 20:
            raise ValueError(f"invoice_id max 20 chars, got {len(self.invoice_id)}")
        if not self.tax_details:
            raise ValueError("tax_details must have at least one entry")
        if any(tax.code is None for tax in self.tax_details):
            raise ValueError("every tax_details entry needs a VAT category code")
        if self.invoice_due_date is not None and self.invoice_due_date < self.invoice_date:
            raise ValueError(
                f"invoice_due_date ({self.invoice_due_date}) must not be before invoiceDate ({self.invoice_date})"
            )

    def to_dict(self) -> dict[str, Any]:
        return drop_none(
            {
                "invoiceId": self.invoice_id,
                "invoiceDate": self.invoice_date,
                "invoiceDueDate": self.invoice_due_date,
                "type": self.invoice_type,
                "processType": self.process_type,
                "taxPaymentOption": self.tax_payment_option.to_dict() if self.tax_payment_option else None,
                "monetary": self.monetary.to_dict(),
                "taxDetails": [tax.to_dict() for tax in self.tax_details],
                "seller": self.seller.to_dict(),
                "buyer": self.buyer.to_dict(),
                "lines": [line.to_dict() for line in self.lines] if self.lines else None,
            }
        )


@dataclass
class ReportFlux10_1:
    invoice: Invoice

    def to_dict(self) -> dict[str, Any]:
        return {"invoice": self.invoice.to_dict()}
