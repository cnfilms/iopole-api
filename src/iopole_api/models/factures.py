from __future__ import annotations

from typing import Any

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API


class Factures(API):
    def send_invoice(self, path: str) -> str:
        """Send an invoice file to Iopole.

        Args:
            path: Filesystem path to the invoice PDF.

        Returns:
            The Iopole invoice ID assigned to the uploaded file.

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        try:
            with open(path, "rb") as invoice:
                response = self.call(method="POST", endpoint="invoice", files={"file": invoice})
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, "The invoice was not sent to Iopole."
            ) from iopole_api_exception

        invoice_id: str = response.json()["id"]
        return invoice_id

    def get_invoice(self, invoice_id: str) -> bytes:
        """Download the original invoice file.

        Args:
            invoice_id: The Iopole invoice ID.

        Returns:
            Raw bytes of the invoice file.

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        try:
            response = self.call(
                method="GET", endpoint=f"invoice/{invoice_id}/download", params={"invoice_id": invoice_id}
            )
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, "The invoice couldn't be retrieved from Iopole."
            ) from iopole_api_exception

        return response.content

    def get_invoice_metadata(self, invoice_id: str) -> list[Any]:
        """Retrieve metadata for an invoice.

        Args:
            invoice_id: The Iopole invoice ID.

        Returns:
            List of metadata objects returned by the API.

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        try:
            response = self.call(method="GET", endpoint=f"invoice/{invoice_id}/files")
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                "The invoice's metadata couldn't be retrieved from Iopole.",
            ) from iopole_api_exception

        result: list[Any] = response.json()
        return result
