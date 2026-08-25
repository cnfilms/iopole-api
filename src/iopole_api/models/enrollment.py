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

        try:
            response = self.call(
                method="PUT",
                endpoint="config/french/enrollment",
                json={"siren": siren, "operatorRelation": {"direction": "OUTBOUND"}},
            )
        except IopoleApiException as iopole_api_exception:
            raise IopoleApiException(
                iopole_api_exception.status_code,
                "Could not retrieve the enrollment link from Iopole",
            ) from iopole_api_exception

        onboarding_link: str = response.json()["onboardingUrl"]
        return onboarding_link
