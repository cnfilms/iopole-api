from typing import Any

import requests

from iopole_api.exceptions.exception import IopoleApiException, IopoleMissingIdException
from iopole_api.models.api import API

# Only French entities are supported so far by Iopole
SIREN_SCHEME = "0002"


class Ereporting(API):
    def _call_report(
        self, method: str, endpoint: str, report: dict[str, Any] | None = None, report_identifier: str | None = None
    ) -> requests.Response:
        params = {"reportIdentifier": report_identifier} if report_identifier else None
        try:
            return self.call(method=method, endpoint=endpoint, json=report, params=params)
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                f"The report was not sent to Iopole: {iopole_api_exception}",
            ) from iopole_api_exception

    def _submit_transaction(self, endpoint: str, report: dict[str, Any], report_identifier: str | None = None) -> str:
        """POST an e-reporting transaction and return the transactionId given back synchronously by Iopole
        (`202 {"type": "INVOICE" | "TRANSACTION", "id": "<uuid>"}`).

        Raises:
            IopoleApiException: on any HTTP error response, the transaction was not accepted.
            IopoleMissingIdException: the transaction was accepted but no identifier was returned. It must not
                be sent again: Iopole does not deduplicate transactions and would count it twice.
        """
        response = self._call_report("POST", endpoint, report, report_identifier)
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {}
        transaction_id = data.get("id") if isinstance(data, dict) else None
        if not transaction_id:
            raise IopoleMissingIdException(
                f"Iopole accepted the transaction but returned no identifier (response: {response.text[:500]!r})"
            )
        return str(transaction_id)

    def send_report_flux_10_1(self, report: dict[str, Any], siren: str, report_identifier: str | None = None) -> str:
        """E-reporting of a B2B invoice transaction (flux 10.1): invoices that must be reported but are not
        transmitted via e-invoicing (at least one party located outside France).

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_1.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The transactionId (type INVOICE). The transaction is validated asynchronously by Iopole
            (EREPORTING_TRANSACTION_ATTACHED / EREPORTING_ERROR webhook events).
        """
        return self._submit_transaction(
            f"reporting/transaction/invoice/scheme/{SIREN_SCHEME}/value/{siren}", report, report_identifier
        )

    def send_report_flux_10_3(self, report: dict[str, Any], siren: str, report_identifier: str | None = None) -> str:
        """E-reporting of a summary of B2C transactions (flux 10.3).

        Submissions are cumulative at Iopole: two submissions for the same day are added together, the second
        one does not replace the first.

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_3.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The transactionId (type TRANSACTION).
        """
        return self._submit_transaction(
            f"reporting/transaction/scheme/{SIREN_SCHEME}/value/{siren}", report, report_identifier
        )

    def correct_report_flux_10_1(self, transaction_id: str, report: dict[str, Any]) -> str:
        """Correct a B2B invoice transaction previously sent with send_report_flux_10_1.

        Returns:
            The identifier returned by Iopole for the correction (referenced by the webhook events).
        """
        return self._submit_transaction(f"reporting/transaction/{transaction_id}/invoice/correction", report)

    def correct_report_flux_10_3(self, transaction_id: str, report: dict[str, Any]) -> str:
        """Correct a B2C transaction summary previously sent with send_report_flux_10_3.

        Returns:
            The identifier returned by Iopole for the correction (referenced by the webhook events).
        """
        return self._submit_transaction(f"reporting/transaction/{transaction_id}/correction", report)

    def delete_report_transaction(self, transaction_id: str) -> None:
        """Delete a transaction (flux 10.1 or 10.3).

        Raises:
            IopoleApiException: 404 unknown transaction, 409 report being transmitted to the PPF, 501 not available
                yet.
        """
        self._call_report("DELETE", f"reporting/transaction/{transaction_id}")

    def search_reports(self, siren: str, **params: Any) -> Any:
        """Search e-reporting folders of a business entity over a period (query params as documented by Iopole)."""
        response = self.call(
            method="GET", endpoint=f"reporting/report/scheme/{SIREN_SCHEME}/value/{siren}", params=params or None
        )
        return response.json()

    def get_report_transmission_content(self, transmission_id: str) -> bytes:
        """Download the full XML flux of an e-reporting transmission."""
        response = self.call(method="GET", endpoint=f"reporting/report/transmission/{transmission_id}/content")
        return response.content
