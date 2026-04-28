from __future__ import annotations

import datetime

import requests

from iopoleapi.exceptions.exception import IopoleApiException


class API:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        auth_url: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.auth_url = auth_url
        self.token: str | None = None
        self.token_expiration_date: datetime.datetime | None = None

    def auth(self) -> str:
        """Obtain (or reuse) a valid OAuth2 client-credentials token."""
        if self.is_token_expired():
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(self.auth_url, data=data, headers=headers)
            if response.status_code != 200:
                raise IopoleApiException(response.status_code, response.text)

            token_data: dict[str, object] = response.json()
            self.token = str(token_data["access_token"])
            expires_in = token_data.get("expires_in", 0)
            self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(
                seconds=float(expires_in)  # type: ignore[arg-type]
            )

        assert self.token is not None
        return self.token

    def make_headers(self) -> dict[str, str]:
        """Build the HTTP headers required for authenticated API calls.

        Raises:
            IopoleApiException: if no token has been obtained yet.
        """
        if not self.token:
            raise IopoleApiException(
                401, "No token available — please call auth() first."
            )

        return {
            "customer-id": self.client_id,
            "Authorization": f"Bearer {self.token}",
            "accept": "*/*",
            "Content-Type": "application/json",
        }

    def is_token_expired(self) -> bool:
        """Return True when the current token is absent or past its expiry."""
        if self.token and self.token_expiration_date:
            return self.token_expiration_date < datetime.datetime.now()
        return True
