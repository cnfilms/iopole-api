from __future__ import annotations

import datetime
import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests

from iopole_api.client import IopoleAPI
from tests._typing import RespondFn


@pytest.fixture
def api() -> IopoleAPI:
    """An authenticated client, ready to make calls without needing auth() first."""
    client = IopoleAPI(
        client_id="client-id",
        client_secret="client-secret",
        base_url="https://api.example.test",
        auth_url="https://auth.example.test",
    )
    client.token = "access-token"
    client.token_expiration_date = datetime.datetime.now() + datetime.timedelta(hours=1)
    return client


@pytest.fixture
def http_request() -> Iterator[Mock]:
    """Patch the HTTP transport so no test ever hits the network."""
    with patch("iopole_api.models.api.requests.request") as request:
        yield request


@pytest.fixture
def respond(http_request: Mock) -> RespondFn:
    """Factory fixture to script the next response returned by the mocked transport.

    Usage: respond(status_code=400, json_body={"error": "boom"})
    """

    def _respond(status_code: int = 200, json_body: Any = None, content: bytes | None = None) -> requests.Response:
        if content is None:
            content = json.dumps(json_body if json_body is not None else {}).encode()
        response = requests.Response()
        response.status_code = status_code
        response._content = content
        http_request.return_value = response
        return response

    return _respond
