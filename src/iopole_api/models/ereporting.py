from typing import Any

from iopole_api.exceptions.exception import IopoleApiException, IopoleMissingIdException
from iopole_api.models.api import API


class Ereporting(API):
    def send_report_flux_10_1(self, report: dict[str, Any], siren: str, report_identifier: str | None = None) -> str:
        """E-reporting of a B2B invoice transaction (flux 10.1).

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_1.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The transactionId (type INVOICE), from `202 {"type": "INVOICE", "id": "<uuid>"}`. The transaction is
            validated asynchronously by Iopole (EREPORTING_TRANSACTION_ATTACHED / EREPORTING_ERROR webhook events).

        Raises:
            IopoleApiException: on any HTTP error response, the transaction was not accepted.
            IopoleMissingIdException: the transaction was accepted but no identifier was returned. It must not
                be sent again: Iopole does not deduplicate transactions and would count it twice.
        """
        try:
            response = self.call(
                method="POST",
                endpoint=f"reporting/transaction/invoice/scheme/0002/value/{siren}",
                json=report,
                params={"reportIdentifier": report_identifier} if report_identifier else None,
            )
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, f"The report was not sent to Iopole: {iopole_api_exception}"
            ) from iopole_api_exception

        # An empty body still means the transaction was accepted
        transaction_id = response.json().get("id") if response.content else None
        if not transaction_id:
            raise IopoleMissingIdException(
                f"Iopole accepted the transaction but returned no identifier (response: {response.text[:500]!r})"
            )
        return str(transaction_id)

    def send_report_flux_10_3(self, report: dict[str, Any], siren: str, report_identifier: str | None = None) -> str:
        """E-reporting of a summary of B2C transactions (flux 10.3).

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_3.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The transactionId (type TRANSACTION), from `202 {"type": "TRANSACTION", "id": "<uuid>"}`.

        Raises:
            IopoleApiException: on any HTTP error response, the transaction was not accepted.
            IopoleMissingIdException: the transaction was accepted but no identifier was returned. It must not
                be sent again: the submission would be counted twice.
        """
        try:
            response = self.call(
                method="POST",
                endpoint=f"reporting/transaction/scheme/0002/value/{siren}",
                json=report,
                params={"reportIdentifier": report_identifier} if report_identifier else None,
            )
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code, f"The report was not sent to Iopole: {iopole_api_exception}"
            ) from iopole_api_exception

        # An empty body still means the transaction was accepted
        transaction_id = response.json().get("id") if response.content else None
        if not transaction_id:
            raise IopoleMissingIdException(
                f"Iopole accepted the transaction but returned no identifier (response: {response.text[:500]!r})"
            )
        return str(transaction_id)
