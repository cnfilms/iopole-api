import datetime

import requests

from iopoleapi.exceptions.exception import IopoleApiException


class API:
    def __init__(self, client_id, client_secret, base_url, auth_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.auth_url = auth_url
        self.token = None
        self.token_type = None
        self.token_expiration_date = None

    def auth(self) -> str:
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

            token_data = response.json()
            self.token = token_data.get("access_token")
            self.token_expiration_date = datetime.datetime.now() + datetime.timedelta(
                seconds=token_data.get("expires_in", 0)
            )

        return self.token

    def make_headers(self):
        if not self.token:
            raise IopoleApiException("Pas de token, merci de vous authentifier.")

        return {
            "customer-id": f"{self.client_id}",
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
        }

    def is_token_expired(self):
        if self.token and self.token_expiration_date:
            return self.token_expiration_date < datetime.datetime.now()

        return True
