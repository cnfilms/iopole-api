"""Tests for iopole_api.models.dataclasses.ereporting_flux_10_1 (the B2B e-reporting report)."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from iopole_api.models.dataclasses.ereporting import Monetary, MonetaryAmount, TaxDetail
from iopole_api.models.dataclasses.ereporting_flux_10_1 import (
    Buyer,
    Invoice,
    InvoiceLine,
    InvoiceTypeCode,
    PartyIdentifier,
    PostalAddress,
    ProcessType,
    ReportFlux10_1,
    Seller,
    TaxPaymentIopCode,
    TaxPaymentOption,
    TaxPaymentUntdidCode,
)


@pytest.fixture
def invoice() -> Invoice:
    return Invoice(
        invoice_id="INV-1",
        invoice_date="2026-04-01",
        invoice_due_date="2026-04-30",
        invoice_type=InvoiceTypeCode.COMMERCIAL_INVOICE,
        process_type=ProcessType.B1,
        tax_payment_option=TaxPaymentOption(iop_code=TaxPaymentIopCode.INVOICE_DATE),
        monetary=Monetary("EUR", MonetaryAmount(100, "EUR"), MonetaryAmount(20, "EUR")),
        tax_details=[TaxDetail(MonetaryAmount(100), MonetaryAmount(20), 20)],
        seller=Seller("Seller", "FR123456789", PartyIdentifier("0002", "123456789"), PostalAddress("FR")),
        buyer=Buyer(PartyIdentifier("0009", "987654321"), PostalAddress("DE")),
    )


class TestPartyIdentifier:
    def test_to_dict(self) -> None:
        assert PartyIdentifier("0002", "123456789").to_dict() == {"scheme": "0002", "value": "123456789"}


class TestPostalAddress:
    def test_to_dict(self) -> None:
        assert PostalAddress("FR").to_dict() == {"country": "FR"}

    def test_rejects_a_country_code_of_the_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="country must be 2 chars, got FRA"):
            PostalAddress("FRA")


class TestSeller:
    def test_to_dict(self) -> None:
        seller = Seller("Seller", "FR123456789", PartyIdentifier("0002", "123456789"), PostalAddress("FR"))
        assert seller.to_dict() == {
            "name": "Seller",
            "vatNumber": "FR123456789",
            "identifier": {"scheme": "0002", "value": "123456789"},
            "postalAddress": {"country": "FR"},
        }


class TestBuyer:
    def test_to_dict_with_only_the_required_fields(self) -> None:
        buyer = Buyer(PartyIdentifier("0009", "987654321"), PostalAddress("DE"))
        assert buyer.to_dict() == {
            "identifier": {"scheme": "0009", "value": "987654321"},
            "postalAddress": {"country": "DE"},
            "name": None,
            "vatNumber": None,
        }

    def test_to_dict_with_the_optional_fields(self) -> None:
        buyer = Buyer(PartyIdentifier("0009", "987654321"), PostalAddress("DE"), name="Buyer", vat_number="DE999")
        assert buyer.to_dict()["name"] == "Buyer"
        assert buyer.to_dict()["vatNumber"] == "DE999"


class TestTaxPaymentOption:
    def test_to_dict_with_an_iop_code(self) -> None:
        option = TaxPaymentOption(iop_code=TaxPaymentIopCode.DELIVERY_DATE)
        assert option.to_dict() == {"iopCode": TaxPaymentIopCode.DELIVERY_DATE}

    def test_to_dict_with_an_untdid_code(self) -> None:
        option = TaxPaymentOption(code=TaxPaymentUntdidCode.PAYMENT_DATE)
        assert option.to_dict() == {"code": "72"}

    def test_rejects_neither_code_being_given(self) -> None:
        with pytest.raises(ValueError, match="Provide either 'iop_code' or 'code'"):
            TaxPaymentOption()

    def test_rejects_both_codes_being_given(self) -> None:
        with pytest.raises(ValueError, match="Provide only one of 'iop_code' or 'code', not both"):
            TaxPaymentOption(iop_code=TaxPaymentIopCode.INVOICE_DATE, code=TaxPaymentUntdidCode.INVOICE_DATE)


class TestInvoiceLine:
    def test_to_dict_with_every_field_set(self) -> None:
        line = InvoiceLine(
            line_id="1", description="Service", quantity=1, unit_code="C62", net_amount=MonetaryAmount(100, "EUR"),
            tax_percent=20,
        )
        assert line.to_dict() == {
            "lineId": "1",
            "description": "Service",
            "quantity": 1,
            "unitCode": "C62",
            "netAmount": {"amount": 100.0, "currency": "EUR"},
            "taxPercent": 20.0,
        }

    def test_to_dict_with_no_field_set(self) -> None:
        assert InvoiceLine().to_dict() == {
            "lineId": None,
            "description": None,
            "quantity": None,
            "unitCode": None,
            "netAmount": {},
            "taxPercent": None,
        }

    @pytest.mark.parametrize("tax_percent", [-1, 101])
    def test_rejects_a_tax_percent_outside_zero_to_a_hundred(self, tax_percent: float) -> None:
        with pytest.raises(ValueError, match="tax_percent must be 0–100"):
            InvoiceLine(tax_percent=tax_percent)


class TestInvoice:
    def test_to_dict(self, invoice: Invoice) -> None:
        assert invoice.to_dict() == {
            "invoiceId": "INV-1",
            "invoiceDate": "2026-04-01",
            "invoiceDueDate": "2026-04-30",
            "type": InvoiceTypeCode.COMMERCIAL_INVOICE,
            "processType": ProcessType.B1,
            "taxPaymentOption": {"iopCode": TaxPaymentIopCode.INVOICE_DATE},
            "monetary": {
                "invoiceCurrency": "EUR",
                "taxBasisTotalAmount": {"amount": 100.0, "currency": "EUR"},
                "taxTotalAmount": {"amount": 20.0, "currency": "EUR"},
            },
            "taxDetails": [{"taxableAmount": {"amount": 100.0, "currency": None},
                            "taxAmount": {"amount": 20.0, "currency": None}, "percent": 20.0}],
            "seller": {
                "name": "Seller",
                "vatNumber": "FR123456789",
                "identifier": {"scheme": "0002", "value": "123456789"},
                "postalAddress": {"country": "FR"},
            },
            "buyer": {
                "identifier": {"scheme": "0009", "value": "987654321"},
                "postalAddress": {"country": "DE"},
                "name": None,
                "vatNumber": None,
            },
        }

    def test_rejects_an_invoice_id_longer_than_twenty_characters(self, invoice: Invoice) -> None:
        with pytest.raises(ValueError, match="invoice_id max 20 chars, got 21"):
            replace(invoice, invoice_id="x" * 21)

    def test_rejects_having_no_tax_details(self, invoice: Invoice) -> None:
        with pytest.raises(ValueError, match="tax_details must have at least one entry"):
            replace(invoice, tax_details=[])

    def test_rejects_a_due_date_before_the_invoice_date(self, invoice: Invoice) -> None:
        with pytest.raises(ValueError, match="must not be before invoiceDate"):
            replace(invoice, invoice_due_date="2026-03-31")

    @pytest.mark.parametrize("changes", [{}, {"invoice_due_date": "2026-04-01"}])
    def test_allows_a_due_date_on_or_after_the_invoice_date(self, invoice: Invoice, changes: dict[str, Any]) -> None:
        replace(invoice, **changes)


class TestReportFlux10_1:
    def test_to_dict_wraps_the_invoice(self, invoice: Invoice) -> None:
        assert ReportFlux10_1(invoice).to_dict() == {"invoice": invoice.to_dict()}
