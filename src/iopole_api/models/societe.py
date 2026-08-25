from __future__ import annotations

from typing import Any

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API


class Societe(API):
    def get_electronic_addresses(self, siren: str) -> list[Any]:
        """Return the electronic (Peppol) addresses registered for a company.

        Args:
            siren: The 9-digit French company identifier (SIREN).

        Returns:
            A list of identifier objects, or an empty list when none are found.

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        try:
            response = self.call(method="GET", endpoint="directory/french", params={"q": f'siren:"{siren}"'})
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                "Could not retrieve electronic addresses from Iopole",
            ) from iopole_api_exception

        payload: dict[str, Any] = response.json()
        data: list[Any] = payload.get("data", [])
        if data:
            identifiers: list[Any] = data[0].get("identifiers", [])
            return identifiers
        return []
