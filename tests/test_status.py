"""Tests for iopole_api.models.status.Status.send_invoice_payment_status."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


def test_defaults_the_vat_rate_to_zero(api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
    respond()
    api.send_invoice_payment_status("invoice-123", 100.0)
    http_request.assert_called_once_with(
        url="https://api.example.test/invoice/invoice-123/status",
        method="POST",
        headers=api.headers,
        json={"code": "PAYMENT_SENT", "payment": [{"vatRate": 0.0, "amount": 100.0, "currency": "EUR"}]},
    )


def test_sends_the_given_amount_and_vat_rate(api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
    respond()
    api.send_invoice_payment_status("invoice-123", 120.0, vat_rate=20.0)
    assert http_request.call_args.kwargs["json"] == {
        "code": "PAYMENT_SENT",
        "payment": [{"vatRate": 20.0, "amount": 120.0, "currency": "EUR"}],
    }


def test_wraps_http_errors_with_the_invoice_id_in_the_message(api: IopoleAPI, respond: RespondFn) -> None:
    respond(status_code=404, content=b"no such invoice")
    with pytest.raises(
        IopoleApiException, match="The payment status was not sent to Iopole for invoice invoice-123"
    ) as caught:
        api.send_invoice_payment_status("invoice-123", 100.0)
    assert caught.value.status_code == 404
