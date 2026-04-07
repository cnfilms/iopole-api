import json
import requests

from iopoleapi.constants.constants import HTTP_ERRORS
from iopoleapi.exceptions.exception import IopoleApiException
from iopoleapi.models.api import API


class Factures(API):
    def __init__(self, client_id, client_secret, base_url, auth_url):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_url=auth_url,
        )

    def send_invoice(self, path) -> str:
        """
        Send an invoice.
        """
        headers = self.make_headers()
        invoice = {"file": open(path, "rb")}
        url = f"{self.base_url}/invoice"

        response = requests.post(url, headers=headers, files=invoice)
        if response.status_code in HTTP_ERRORS:
            raise IopoleApiException(
                response.status_code, "The invoice was not sent to Iopole"
            )

        invoice_id = json.loads(response.content.decode("utf-8")).get("id")

        return invoice_id

    def get_invoice(self, invoice_id) -> bytes:
        """
        Get an invoice from its invoice id.
        """
        headers = self.make_headers()
        url = f"{self.base_url}/invoice/{invoice_id}/download"

        response = requests.get(url, headers=headers)
        if response.status_code in HTTP_ERRORS:
            raise IopoleApiException(
                response.status_code, "The invoice was not received from Iopole"
            )

        invoice = response.content

        return invoice

    def get_invoice_metadata(self, invoice_id) -> list:
        """
        Get an invoice's metadata from its invoice id.
        """
        headers = self.make_headers()
        url = f"{self.base_url}/invoice/{invoice_id}/files"

        response = requests.get(url, headers=headers)
        if response.status_code in HTTP_ERRORS:
            raise IopoleApiException(
                response.status_code,
                "The invoice's metadata was not received from Iopole",
            )

        metadata = json.loads(response.content.decode("utf-8"))

        return metadata
