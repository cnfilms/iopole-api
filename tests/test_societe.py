"""Tests for iopole_api.models.societe.Societe.get_electronic_addresses."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


def test_returns_the_identifiers_of_the_first_matching_company(api: IopoleAPI, respond: RespondFn) -> None:
    respond(json_body={"data": [{"identifiers": [{"scheme": "0002", "value": "123456789"}]}]})
    assert api.get_electronic_addresses("123456789") == [{"scheme": "0002", "value": "123456789"}]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="no-data-key"),
        pytest.param({"data": []}, id="no-matching-company"),
        pytest.param({"data": [{}]}, id="company-without-identifiers"),
    ],
)
def test_returns_an_empty_list_when_nothing_is_found(
    api: IopoleAPI, respond: RespondFn, payload: dict[str, Any]
) -> None:
    respond(json_body=payload)
    assert api.get_electronic_addresses("123456789") == []


def test_searches_the_french_directory_by_siren(api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
    respond(json_body={"data": []})
    api.get_electronic_addresses("123456789")
    http_request.assert_called_once_with(
        url="https://api.example.test/directory/french",
        method="GET",
        headers=api.headers,
        params={"q": 'siren:"123456789"'},
    )


def test_wraps_http_errors_with_a_domain_specific_message(api: IopoleAPI, respond: RespondFn) -> None:
    respond(status_code=500, content=b"boom")
    with pytest.raises(IopoleApiException, match="Could not retrieve electronic addresses from Iopole") as caught:
        api.get_electronic_addresses("123456789")
    assert caught.value.status_code == 500
