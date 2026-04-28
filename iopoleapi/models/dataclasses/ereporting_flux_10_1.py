from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Any

from iopoleapi.models.dataclasses.ereporting import MonetaryAmount, Monetary, TaxDetail


class InvoiceTypeCode(str, Enum):
    """UNTDID 1001 invoice type codes relevant to French e-reporting."""

    COMMERCIAL_INVOICE = "380"
    CREDIT_NOTE = "381"
    DEBIT_NOTE = "383"
    CORRECTED_INVOICE = "384"
    PREPAYMENT_INVOICE = "386"
    SELF_BILLED_INVOICE = "389"


class ProcessType(str, Enum):
    """
    Business process type codes.
    B1/B2/B3 = B2Bi (FR seller → foreign buyer).
    S1/S2/S3 = Bi2B (foreign seller → FR buyer).
    """

    B1 = "B1"  # Standard B2Bi sale
    B2 = "B2"  # B2Bi with reverse charge
    B3 = "B3"  # B2Bi export / exemption
    S1 = "S1"  # Standard Bi2B acquisition
    S2 = "S2"  # Bi2B with reverse charge
    S3 = "S3"  # Bi2B import / exemption


class TaxPaymentIopCode(str, Enum):
    """Iopole shorthand codes for VAT exigibility (when VAT becomes due)."""

    INVOICE_DATE = "INVOICE_DATE"  # VAT due on invoice date (default for goods)
    DELIVERY_DATE = "DELIVERY_DATE"  # VAT due on delivery
    PAYMENT_DATE = "PAYMENT_DATE"  # VAT due on collection (services)


class TaxPaymentUntdidCode(str, Enum):
    """UNTDID 2005 — standard payment means timing codes."""

    INVOICE_DATE = "3"
    DELIVERY_DATE = "35"
    PAYMENT_DATE = "72"


@dataclass
class TaxPaymentOption:
    """Exactly one of iopCode or code must be provided."""

    iop_code: Optional[TaxPaymentIopCode] = None
    code: Optional[TaxPaymentUntdidCode] = None

    def __post_init__(self) -> None:
        if self.iop_code is None and self.code is None:
            raise ValueError("Provide either 'iop_code' or 'code'.")
        if self.iop_code is not None and self.code is not None:
            raise ValueError("Provide only one of 'iop_code' or 'code', not both.")

    def to_dict(self) -> dict[str, Any]:
        if self.iop_code:
            return {"iopCode": self.iop_code}
        return {"code": self.code}


@dataclass
class PartyIdentifier:
    """ICD scheme + value pair."""

    scheme: str  # ICD code, e.g. "0009"
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"scheme": self.scheme, "value": self.value}


@dataclass
class PostalAddress:
    country: str

    def __post_init__(self) -> None:
        if len(self.country) != 2:
            raise ValueError(f"country must be 2 chars, got {self.country}")

    def to_dict(self) -> dict[str, Any]:
        return {"country": self.country}


@dataclass
class Seller:
    name: str
    vat_number: str
    identifier: PartyIdentifier
    postal_address: PostalAddress

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "vatNumber": self.vat_number,
            "identifier": self.identifier.to_dict(),
            "postalAddress": self.postal_address.to_dict(),
        }


@dataclass
class Buyer:
    identifier: PartyIdentifier
    postal_address: PostalAddress
    name: Optional[str] = None
    vat_number: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier.to_dict(),
            "postalAddress": self.postal_address.to_dict(),
            "name": self.name,
            "vatNumber": self.vat_number,
        }


@dataclass
class InvoiceLine:
    line_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_code: Optional[str] = None
    net_amount: Optional[MonetaryAmount] = None
    tax_percent: Optional[float] = None

    def __post_init__(self) -> None:
        if self.tax_percent is not None and not 0 <= self.tax_percent <= 100:
            raise ValueError(f"tax_percent must be 0–100, got {self.tax_percent}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineId": self.line_id,
            "description": self.description,
            "quantity": self.quantity,
            "unitCode": self.unit_code,
            "netAmount": self.net_amount.to_dict() if self.net_amount else {},
            "taxPercent": float(self.tax_percent) if self.tax_percent else None,
        }


@dataclass
class Invoice:
    invoice_id: str
    invoice_date: str
    invoice_due_date: str
    invoice_type: InvoiceTypeCode
    process_type: ProcessType
    tax_payment_option: TaxPaymentOption
    monetary: Monetary
    tax_details: List[TaxDetail]
    seller: Seller
    buyer: Buyer
    lines: Optional[List[InvoiceLine]] = None

    def __post_init__(self) -> None:
        if len(self.invoice_id) > 20:
            raise ValueError(f"invoice_id max 20 chars, got {len(self.invoice_id)}")
        if not self.tax_details:
            raise ValueError("tax_details must have at least one entry")
        if self.invoice_due_date < self.invoice_date:
            raise ValueError(
                f"invoice_due_date ({self.invoice_due_date}) must not be before "
                f"invoiceDate ({self.invoice_date})"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "invoiceId": self.invoice_id,
            "invoiceDate": self.invoice_date,
            "invoiceDueDate": self.invoice_due_date,
            "type": self.invoice_type,
            "processType": self.process_type,
            "taxPaymentOption": self.tax_payment_option.to_dict(),
            "monetary": self.monetary.to_dict(),
            "taxDetails": [tax.to_dict() for tax in self.tax_details],
            "seller": self.seller.to_dict(),
            "buyer": self.buyer.to_dict(),
        }


@dataclass
class ReportFlux10_1:
    invoice: Invoice

    def to_dict(self) -> dict[str, Any]:
        return {"invoice": self.invoice.to_dict()}
