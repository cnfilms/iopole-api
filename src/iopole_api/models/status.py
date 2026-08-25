from __future__ import annotations

from typing import Any

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API


class Status(API):
    def send_invoice_payment_status(self, uuid_presta: str, amount: float, vat_rate: float = 0.0) -> None:
        """Send PAYMENT_SENT status to Iopole for an invoice.

        This endpoint notifies Iopole that an invoice has been paid (encaissée).

        Args:
            uuid_presta: The UUID of the invoice from Iopole
            amount: The amount being paid
            vat_rate: The VAT rate applied (default 0.0)
        """
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

        try:
            self.call(method="POST", endpoint=f"invoice/{uuid_presta}/status", json=payload)
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                f"The payment status was not sent to Iopole for invoice {uuid_presta}.",
            ) from iopole_api_exception
