import json
import requests
from iopoleapi.exceptions.exception import IopoleApiException

from iopoleapi.models.api import API


class Enrollment(API):
    def __init__(self, client_id, client_secret, base_url, auth_url):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_url=auth_url,
        )

    def get_enrollment_link(self, siren) -> str:
        """
        Get Iopole enrollment link from a society's SIREN.
        """
        headers = self.make_headers()
        url = f"{self.base_url}/config/french/enrollment"

        response = requests.put(url, headers=headers, json={"siren": str(siren)})

        if response.status_code == 400:
            raise IopoleApiException(response.status_code, "Tu ne peux pas faire ça.")
        onboarding_link = json.loads(response.content.decode("utf-8")).get(
            "onboardingUrl"
        )

        return onboarding_link
