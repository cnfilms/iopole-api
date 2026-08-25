from typing import Any

import requests

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API


class Ereporting(API):
    def send_report_flux_10_1(self, report: dict[str, Any], address: str) -> None:
        """Submit an invoice for B2B e-reporting.
        This endpoint fulfills the e-reporting obligation for invoices where at least one of the parties is located
        outside France.

        Args:
            report: Report to be transmitted to Iopole
            address: SIREN of the company

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        headers = self.make_headers()
        url = (
            f"{self.base_url}/reporting/transaction/invoice/scheme/0002/value/{address}"
        )

        response = requests.post(url, headers=headers, data=report)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code, "The report was not sent to Iopole."
            ) from e

    def send_report_flux_10_3(self, report: dict[str, Any], address: str) -> None:
        """Submit an invoice for B2B e-reporting.
        Submit a daily summary of B2C (business-to-consumer) transactions for a given cash register closure (Z report).
        This endpoint fulfills the French e-reporting obligation for transactions that are not subject
        to B2B e-invoicing.

        Args:
            report: Report to be transmitted to Iopole
            address: SIREN of the company

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        headers = self.make_headers()
        url = f"{self.base_url}/reporting/transaction/scheme/0002/value/{address}"

        response = requests.post(url, headers=headers, data=report)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code, "The report was not sent to Iopole."
            ) from e
