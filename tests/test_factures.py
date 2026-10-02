"""Tests for iopole_api.models.factures.Factures."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


class TestSendInvoice:
    def test_returns_the_assigned_invoice_id(self, api: IopoleAPI, respond: RespondFn, tmp_path: Path) -> None:
        invoice_path = tmp_path / "invoice.pdf"
        invoice_path.write_bytes(b"%PDF-invoice")
        respond(json_body={"id": "invoice-123"})

        assert api.send_invoice(str(invoice_path)) == "invoice-123"

    def test_uploads_the_file_contents_and_closes_it_afterwards(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn, tmp_path: Path
    ) -> None:
        invoice_path = tmp_path / "invoice.pdf"
        invoice_path.write_bytes(b"%PDF-invoice")
        respond(json_body={"id": "invoice-123"})

        api.send_invoice(str(invoice_path))

        uploaded_file = http_request.call_args.kwargs["files"]["file"]
        assert uploaded_file.name == str(invoice_path)
        assert uploaded_file.closed
        http_request.assert_called_once_with(
            url="https://api.example.test/invoice", method="POST", headers=api.headers, files={"file": uploaded_file}
        )

    def test_closes_the_file_even_on_error(
        self, api: IopoleAPI, respond: RespondFn, tmp_path: Path, http_request: Mock
    ) -> None:
        invoice_path = tmp_path / "invoice.pdf"
        invoice_path.write_bytes(b"%PDF-invoice")
        respond(status_code=400, content=b"rejected")

        with pytest.raises(IopoleApiException):
            api.send_invoice(str(invoice_path))

        uploaded_file = http_request.call_args.kwargs["files"]["file"]
        assert uploaded_file.closed

    def test_wraps_http_errors_with_a_domain_specific_message(
        self, api: IopoleAPI, respond: RespondFn, tmp_path: Path
    ) -> None:
        invoice_path = tmp_path / "invoice.pdf"
        invoice_path.write_bytes(b"%PDF-invoice")
        respond(status_code=400, content=b"rejected")

        with pytest.raises(IopoleApiException, match="The invoice was not sent to Iopole") as caught:
            api.send_invoice(str(invoice_path))
        assert caught.value.status_code == 400
        assert isinstance(caught.value.__cause__, IopoleApiException)


class TestGetInvoice:
    def test_returns_the_raw_file_bytes(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(content=b"%PDF-invoice")
        assert api.get_invoice("invoice-123") == b"%PDF-invoice"

    def test_requests_the_download_endpoint(self, api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
        respond(content=b"%PDF-invoice")
        api.get_invoice("invoice-123")
        http_request.assert_called_once_with(
            url="https://api.example.test/invoice/invoice-123/download",
            method="GET",
            headers=api.headers,
            params={"invoice_id": "invoice-123"},
        )

    def test_wraps_http_errors_with_a_domain_specific_message(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=404, content=b"gone")
        with pytest.raises(IopoleApiException, match="The invoice couldn't be retrieved from Iopole") as caught:
            api.get_invoice("invoice-123")
        assert caught.value.status_code == 404


class TestGetInvoiceMetadata:
    def test_returns_the_metadata_list(self, api: IopoleAPI, respond: RespondFn) -> None:
        metadata = [{"id": "file-123", "name": "invoice.pdf"}]
        respond(json_body=metadata)
        assert api.get_invoice_metadata("invoice-123") == metadata

    def test_requests_the_files_endpoint(self, api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
        respond(json_body=[])
        api.get_invoice_metadata("invoice-123")
        http_request.assert_called_once_with(
            url="https://api.example.test/invoice/invoice-123/files", method="GET", headers=api.headers
        )

    def test_wraps_http_errors_with_a_domain_specific_message(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=404, content=b"gone")
        message = "The invoice's metadata couldn't be retrieved from Iopole"
        with pytest.raises(IopoleApiException, match=message) as caught:
            api.get_invoice_metadata("invoice-123")
        assert caught.value.status_code == 404
