"""Tests for iopole_api.models.ereporting.Ereporting (flux 10.1 and 10.3 reports)."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


class TestSendReportFlux10_1:
    def test_posts_the_report_to_the_invoice_scheme_endpoint(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        respond()
        report = {"invoice": {"invoiceId": "INV-1"}}

        api.send_report_flux_10_1(report, "123456789")

        http_request.assert_called_once_with(
            url="https://api.example.test/reporting/transaction/invoice/scheme/0002/value/123456789",
            method="POST",
            headers=api.headers,
            data=report,
        )

    def test_wraps_http_errors_with_a_domain_specific_message(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=400, content=b"rejected")
        with pytest.raises(IopoleApiException, match="The report was not sent to Iopole") as caught:
            api.send_report_flux_10_1({}, "123456789")
        assert caught.value.status_code == 400


class TestSendReportFlux10_3:
    def test_posts_the_report_to_the_transaction_scheme_endpoint(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        respond()
        report = {"transactionDate": "2026-04-01", "transactions": []}

        api.send_report_flux_10_3(report, "123456789")

        http_request.assert_called_once_with(
            url="https://api.example.test/reporting/transaction/scheme/0002/value/123456789",
            method="POST",
            headers=api.headers,
            data=report,
        )

    def test_wraps_http_errors_with_a_domain_specific_message(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=400, content=b"rejected")
        with pytest.raises(IopoleApiException, match="The report was not sent to Iopole") as caught:
            api.send_report_flux_10_3({}, "123456789")
        assert caught.value.status_code == 400
