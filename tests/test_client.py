"""Tests for iopole_api.client.IopoleAPI — the public entry point combining all mixins."""

from __future__ import annotations

import iopole_api
from iopole_api import IopoleAPI
from iopole_api.client import IopoleAPI as ClientIopoleAPI
from iopole_api.models.enrollment import Enrollment
from iopole_api.models.ereporting import Ereporting
from iopole_api.models.factures import Factures
from iopole_api.models.societe import Societe
from iopole_api.models.status import Status


def test_is_re_exported_from_the_top_level_package() -> None:
    assert IopoleAPI is ClientIopoleAPI


def test_top_level_package_exports_the_public_api() -> None:
    assert iopole_api.__all__ == ["IopoleAPI", "IopoleApiException", "IopoleStatus", "Status"]


def test_combines_every_endpoint_mixin() -> None:
    assert issubclass(IopoleAPI, Factures)
    assert issubclass(IopoleAPI, Enrollment)
    assert issubclass(IopoleAPI, Societe)
    assert issubclass(IopoleAPI, Ereporting)
    assert issubclass(IopoleAPI, Status)


def test_stores_the_constructor_arguments() -> None:
    client = IopoleAPI(
        client_id="client-id",
        client_secret="client-secret",
        base_url="https://api.example.test",
        auth_url="https://auth.example.test",
    )
    assert client.client_id == "client-id"
    assert client.client_secret == "client-secret"
    assert client.base_url == "https://api.example.test"
    assert client.auth_url == "https://auth.example.test"
    assert client.token is None
    assert client.token_expiration_date is None
