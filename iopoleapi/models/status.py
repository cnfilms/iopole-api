from __future__ import annotations

from typing import Any

import requests

from iopoleapi.exceptions.exception import IopoleApiException
from iopoleapi.models.api import API


class Status(API):
    def send_invoice_payment_status(
        self, uuid_presta: str, amount: float, vat_rate: float = 0.0
    ) -> None:
        """Send PAYMENT_SENT status to Iopole for an invoice.

        This endpoint notifies Iopole that an invoice has been paid (encaissée).

        Args:
            uuid_presta: The UUID of the invoice from Iopole
            amount: The amount being paid
            vat_rate: The VAT rate applied (default 0.0)
        """
        headers = self.make_headers()
        url = f"{self.base_url}/invoice/{uuid_presta}/status"

        payload: dict[str, Any] = {
            "code": "PAYMENT_SENT",
            "payment": [
                {
                    "vatRate": vat_rate,
                    "amount": amount,
                    "currency": "EUR",
                }
            ],
        }

        response = requests.post(url, headers=headers, json=payload)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code,
                f"The payment status was not sent to Iopole for invoice {uuid_presta}.",
            ) from e
