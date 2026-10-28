from typing import Any

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API

# Only French entities are supported so far by Iopole
SIREN_SCHEME = "0002"


class Ereporting(API):
    def _send_report(
        self, method: str, endpoint: str, report: dict[str, Any] | None, report_identifier: str | None = None
    ) -> str | None:
        """Send an e-reporting payload and return the submission identifier given back by Iopole."""
        params = {"reportIdentifier": report_identifier} if report_identifier else None
        try:
            response = self.call(method=method, endpoint=endpoint, json=report, params=params)
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                f"The report was not sent to Iopole: {iopole_api_exception}",
            ) from iopole_api_exception

        if not response.content:
            return None
        submission_id: str | None = response.json().get("id")
        return submission_id

    def send_report_flux_10_1(
        self, report: dict[str, Any], siren: str, report_identifier: str | None = None
    ) -> str | None:
        """E-reporting of a B2B invoice transaction (flux 10.1): invoices that must be reported but are not
        transmitted via e-invoicing (at least one party located outside France).

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_1.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The identifier of the submission (type INVOICE)

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        return self._send_report(
            "POST", f"reporting/transaction/invoice/scheme/{SIREN_SCHEME}/value/{siren}", report, report_identifier
        )

    def send_report_flux_10_3(
        self, report: dict[str, Any], siren: str, report_identifier: str | None = None
    ) -> str | None:
        """E-reporting of a daily summary of B2C transactions (flux 10.3).

        Args:
            report: Report to be transmitted to Iopole (ReportFlux10_3.to_dict())
            siren: SIREN of the declaring company
            report_identifier: Id of an existing Iopole report to associate this submission with

        Returns:
            The identifier of the submission (type TRANSACTION)

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        return self._send_report(
            "POST", f"reporting/transaction/scheme/{SIREN_SCHEME}/value/{siren}", report, report_identifier
        )

    def update_report_flux_10_1(self, transaction_id: str, report: dict[str, Any]) -> str | None:
        """Replace a B2B invoice transaction previously sent with send_report_flux_10_1."""
        return self._send_report("PUT", f"reporting/transaction/{transaction_id}/invoice", report)

    def update_report_flux_10_3(self, transaction_id: str, report: dict[str, Any]) -> str | None:
        """Replace a B2C transaction summary previously sent with send_report_flux_10_3."""
        return self._send_report("PUT", f"reporting/transaction/{transaction_id}", report)

    def delete_report_transaction(self, transaction_id: str) -> None:
        """Delete a transaction (flux 10.1 or 10.3)."""
        self._send_report("DELETE", f"reporting/transaction/{transaction_id}", None)

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
