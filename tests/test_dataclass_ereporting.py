"""Tests for the shared monetary dataclasses in iopole_api.models.dataclasses.ereporting."""

from __future__ import annotations

import pytest

from iopole_api.models.dataclasses.ereporting import Monetary, MonetaryAmount, TaxDetail


class TestMonetaryAmount:
    def test_to_dict_includes_the_currency(self) -> None:
        assert MonetaryAmount(100, "EUR").to_dict() == {"amount": 100.0, "currency": "EUR"}

    def test_to_dict_allows_a_missing_currency(self) -> None:
        assert MonetaryAmount(100).to_dict() == {"amount": 100.0, "currency": None}

    def test_rejects_a_non_positive_amount(self) -> None:
        with pytest.raises(ValueError, match="amount must be > 0, got 0"):
            MonetaryAmount(0)

    def test_rejects_a_currency_code_of_the_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="currency must be 3 chars, got EURO"):
            MonetaryAmount(100, "EURO")


class TestMonetary:
    def test_to_dict(self) -> None:
        monetary = Monetary("EUR", MonetaryAmount(100, "EUR"), MonetaryAmount(20, "EUR"))
        assert monetary.to_dict() == {
            "invoiceCurrency": "EUR",
            "taxBasisTotalAmount": {"amount": 100.0, "currency": "EUR"},
            "taxTotalAmount": {"amount": 20.0, "currency": "EUR"},
        }

    def test_rejects_an_invoice_currency_of_the_wrong_length(self) -> None:
        with pytest.raises(ValueError, match="invoice_currency must be 3 chars, got EURO"):
            Monetary("EURO", MonetaryAmount(100), MonetaryAmount(20))


class TestTaxDetail:
    def test_to_dict(self) -> None:
        detail = TaxDetail(MonetaryAmount(100), MonetaryAmount(20), 20)
        assert detail.to_dict() == {
            "taxableAmount": {"amount": 100.0, "currency": None},
            "taxAmount": {"amount": 20.0, "currency": None},
            "percent": 20.0,
        }

    @pytest.mark.parametrize("percent", [-1, 101])
    def test_rejects_a_percent_outside_zero_to_a_hundred(self, percent: float) -> None:
        with pytest.raises(ValueError, match="percent must be 0–100"):
            TaxDetail(MonetaryAmount(100), MonetaryAmount(20), percent)

    @pytest.mark.parametrize("percent", [0, 100])
    def test_accepts_the_boundary_percentages(self, percent: float) -> None:
        detail = TaxDetail(MonetaryAmount(100), MonetaryAmount(20), percent)
        assert detail.percent == percent
