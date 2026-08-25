import requests

from iopole_api.exceptions.exception import IopoleApiException
from iopole_api.models.api import API


class Enrollment(API):
    def get_enrollment_link(self, siren: str) -> str:
        """Return the Iopole onboarding URL for a company identified by its SIREN.

        Args:
            siren: The 9-digit French company identifier (SIREN).

        Returns:
            The onboarding URL string.

        Raises:
            IopoleApiException: on any HTTP error response.
        """
        headers = self.make_headers()
        url = f"{self.base_url}/config/french/enrollment"

        response = requests.put(
            url,
            headers=headers,
            json={"siren": str(siren), "operatorRelation": {"direction": "OUTBOUND"}},
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise IopoleApiException(
                response.status_code,
                "Could not retrieve the enrollment link from Iopole",
            ) from e

        onboarding_link: str = response.json()["onboardingUrl"]
        return onboarding_link
