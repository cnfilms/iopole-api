import json

import requests

from iopoleapi.models.api import API


class Societe(API):
    def __init__(self, client_id, client_secret, base_url, auth_url):
        super().__init__(client_id=client_id, client_secret=client_secret, base_url=base_url, auth_url=auth_url)

    def get_electronic_addresses(self, siren) -> list:
        """
        Get a society's electronic addresses from its SIREN
        """
        headers = self.make_headers()
        url = f"{self.base_url}/directory/french?q=siren%3A%22{siren}%22"

        response = json.loads(requests.get(url, headers=headers).text).get('data')

        if isinstance(response, list) and len(response):
            return response[0].get('identifiers')
        return []
