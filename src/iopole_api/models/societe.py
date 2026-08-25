from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import requests

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
        headers = self.make_headers()
        query = urlencode({"q": f'siren:"{siren}"'})
        url = f"{self.base_url}/directory/french?{query}"

        response = requests.get(url, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code,
                "Could not retrieve electronic addresses from Iopole",
            ) from e

        payload: dict[str, Any] = response.json()
        data: list[Any] = payload.get("data", [])
        if data:
            identifiers: list[Any] = data[0].get("identifiers", [])
            return identifiers
        return []
