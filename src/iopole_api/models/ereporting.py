from typing import Any

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

        try:
            self.call(method="POST", endpoint=f"reporting/transaction/invoice/scheme/0002/value/{address}", data=report)
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, "The report was not sent to Iopole."
            ) from iopole_api_exception

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
        try:
            self.call(method="POST", endpoint=f"reporting/transaction/scheme/0002/value/{address}", data=report)
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, "The report was not sent to Iopole."
            ) from iopole_api_exception
