from __future__ import annotations

import datetime
from typing import Any

import requests

from iopole_api.exceptions.exception import IopoleApiException


class API:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        auth_url: str,
        token: str | None = None,
        token_expiration_date: datetime.datetime | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.auth_url = auth_url
        self.token = token
        self.token_expiration_date = token_expiration_date

    @property
    def headers(self) -> dict[str, str]:
        """Build the HTTP headers required for authenticated API calls.

        Raises:
            IopoleApiException: if no token has been obtained yet.
        """
        if not self.token:
            raise IopoleApiException(401, "No token available — please call auth() first.")

        return {
            "customer-id": self.client_id,
            "Authorization": f"Bearer {self.token}",
            "accept": "*/*",
        }

    @property
    def is_token_expired(self) -> bool:
        """Return True when the current token is absent or past its expiry."""
        if self.token and self.token_expiration_date:
            return self.token_expiration_date < datetime.datetime.now()
        return True

    def call(
        self, endpoint: str, base_url: str | None = None, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> requests.Response:
        try:
            response = requests.request(
                url=f"{base_url or self.base_url}/{endpoint}", headers=headers or self.headers, **kwargs
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise IopoleApiException(error.response.status_code, error.response.text) from error

        return response

    def auth(self) -> tuple[str, datetime.datetime]:
        """Obtain (or reuse) a valid OAuth2 client-credentials token.

        Returns:
            tuple: (access_token, token_expiration_date)
        """
        if self.is_token_expired:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

            response = self.call(
                method="POST",
                endpoint="realms/iopole/protocol/openid-connect/token",
                base_url=self.auth_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data,
            )

            token_data: dict[str, str | int] = response.json()
            self.token = str(token_data["access_token"])
            expires_in = token_data.get("expires_in", 0)
            self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=float(expires_in))

        assert self.token is not None and self.token_expiration_date is not None
        return self.token, self.token_expiration_date
