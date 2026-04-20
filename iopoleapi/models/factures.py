from __future__ import annotations

from typing import Any

import requests

from iopoleapi.exceptions.exception import IopoleApiException
from iopoleapi.models.api import API


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
        headers = self.make_headers()
        url = f"{self.base_url}/invoice"

        with open(path, "rb") as invoice:
            response = requests.post(url, headers=headers, files={"file": invoice})

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code, "The invoice was not sent to Iopole."
            ) from e

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
        headers = self.make_headers()
        url = f"{self.base_url}/invoice/{invoice_id}/download"

        response = requests.get(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code, "The invoice couldn't be retrieved from Iopole."
            ) from e

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
        headers = self.make_headers()
        url = f"{self.base_url}/invoice/{invoice_id}/files"

        response = requests.get(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code,
                "The invoice's metadata couldn't be retrieved from Iopole.",
            ) from e

        result: list[Any] = response.json()
        return result
