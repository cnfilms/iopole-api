"""Tests for iopole_api.models.dataclasses.ereporting_flux_10_3 (the B2C daily summary report)."""

from __future__ import annotations

from iopole_api.models.dataclasses.ereporting import Monetary, MonetaryAmount, TaxDetail
from iopole_api.models.dataclasses.ereporting_flux_10_3 import ReportFlux10_3, Transaction, TransactionCategory


def _transaction() -> Transaction:
    return Transaction(
        category_code=TransactionCategory.TLB1,
        currency="EUR",
        monetary=Monetary("EUR", MonetaryAmount(100, "EUR"), MonetaryAmount(20, "EUR")),
        tax_details=[TaxDetail(MonetaryAmount(100), MonetaryAmount(20), 20)],
    )


def test_transaction_to_dict() -> None:
    assert _transaction().to_dict() == {
        "categoryCode": TransactionCategory.TLB1,
        "currency": "EUR",
        "monetary": {
            "invoiceCurrency": "EUR",
            "taxBasisTotalAmount": {"amount": 100.0, "currency": "EUR"},
            "taxTotalAmount": {"amount": 20.0, "currency": "EUR"},
        },
        "taxDetails": [{"taxableAmount": {"amount": 100.0, "currency": None},
                        "taxAmount": {"amount": 20.0, "currency": None}, "percent": 20.0}],
    }


def test_report_to_dict_serializes_every_transaction() -> None:
    report = ReportFlux10_3("2026-04-01", [_transaction(), _transaction()])
    as_dict = report.to_dict()
    assert as_dict["transactionDate"] == "2026-04-01"
    assert as_dict["transactions"] == [_transaction().to_dict(), _transaction().to_dict()]
