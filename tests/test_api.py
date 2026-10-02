"""Tests for iopole_api.models.api.API — the shared HTTP/auth base class."""

from __future__ import annotations

import datetime
from unittest.mock import Mock

import pytest
import requests

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


class TestHeaders:
    def test_raises_without_a_token(self, api: IopoleAPI) -> None:
        api.token = None
        with pytest.raises(IopoleApiException, match="please call auth"):
            _ = api.headers

    def test_includes_bearer_token_and_customer_id(self, api: IopoleAPI) -> None:
        assert api.headers == {
            "customer-id": "client-id",
            "Authorization": "Bearer access-token",
            "accept": "*/*",
        }


class TestIsTokenExpired:
    def test_true_when_there_is_no_token(self, api: IopoleAPI) -> None:
        api.token = None
        assert api.is_token_expired is True

    def test_true_when_there_is_no_expiration_date(self, api: IopoleAPI) -> None:
        api.token_expiration_date = None
        assert api.is_token_expired is True

    def test_true_once_past_the_expiration_date(self, api: IopoleAPI) -> None:
        api.token_expiration_date = datetime.datetime.now() - datetime.timedelta(seconds=1)
        assert api.is_token_expired is True

    def test_false_before_the_expiration_date(self, api: IopoleAPI) -> None:
        api.token_expiration_date = datetime.datetime.now() + datetime.timedelta(hours=1)
        assert api.is_token_expired is False


class TestCall:
    def test_returns_the_response_on_success(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=200, json_body={"ok": True})
        response = api.call("invoice", method="GET")
        assert response.json() == {"ok": True}

    def test_wraps_http_errors(self, api: IopoleAPI, respond: RespondFn) -> None:
        respond(status_code=404, content=b"Invoice not found")
        with pytest.raises(IopoleApiException, match="Invoice not found") as caught:
            api.call("invoice/missing", method="GET")
        assert caught.value.status_code == 404
        assert isinstance(caught.value.__cause__, requests.HTTPError)

    def test_sends_the_request_with_the_given_arguments(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        respond(status_code=200)
        api.call("invoice/123/files", method="GET", params={"invoice_id": "123"})
        http_request.assert_called_once_with(
            url="https://api.example.test/invoice/123/files",
            method="GET",
            headers=api.headers,
            params={"invoice_id": "123"},
        )

    def test_can_target_a_different_base_url(self, api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
        respond(status_code=200)
        api.call("token", base_url="https://other.example.test", headers={"X-Test": "1"}, method="GET")
        http_request.assert_called_once_with(
            url="https://other.example.test/token", method="GET", headers={"X-Test": "1"}
        )


class TestAuth:
    def test_fetches_a_new_token_when_none_is_held(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        api.token = None
        api.token_expiration_date = None
        respond(status_code=200, json_body={"access_token": "new-token", "expires_in": 3600})

        before = datetime.datetime.now()
        token, expiration = api.auth()
        after = datetime.datetime.now()

        assert token == "new-token"
        assert api.token == "new-token"
        assert before + datetime.timedelta(seconds=3600) <= expiration <= after + datetime.timedelta(seconds=3600)
        assert api.token_expiration_date == expiration

    def test_refreshes_an_expired_token(self, api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
        api.token_expiration_date = datetime.datetime.now() - datetime.timedelta(minutes=1)
        respond(status_code=200, json_body={"access_token": "refreshed-token", "expires_in": 60})

        api.auth()

        assert api.token == "refreshed-token"
        http_request.assert_called_once()

    def test_reuses_a_still_valid_token_without_calling_out(self, api: IopoleAPI, http_request: Mock) -> None:
        expected_expiration = api.token_expiration_date
        assert api.auth() == ("access-token", expected_expiration)
        http_request.assert_not_called()

    def test_defaults_expires_in_to_zero_when_absent(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        api.token = None
        respond(status_code=200, json_body={"access_token": "new-token"})

        before = datetime.datetime.now()
        _, expiration = api.auth()

        assert before <= expiration <= datetime.datetime.now()

    def test_sends_client_credentials_to_the_auth_url(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        api.token = None
        respond(status_code=200, json_body={"access_token": "new-token", "expires_in": 3600})

        api.auth()

        http_request.assert_called_once_with(
            url="https://auth.example.test/realms/iopole/protocol/openid-connect/token",
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": "client-id",
                "client_secret": "client-secret",
            },
        )

    def test_propagates_auth_failures_without_setting_a_token(
        self, api: IopoleAPI, http_request: Mock, respond: RespondFn
    ) -> None:
        api.token = None
        respond(status_code=401, content=b"Invalid credentials")

        with pytest.raises(IopoleApiException, match="Invalid credentials") as caught:
            api.auth()

        assert caught.value.status_code == 401
        assert api.token is None
