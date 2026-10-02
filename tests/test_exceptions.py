"""Tests for iopole_api.exceptions.exception.IopoleApiException."""

from __future__ import annotations

import pytest

from iopole_api.exceptions.exception import IopoleApiException


@pytest.mark.parametrize(
    "status_code,expected_text",
    [
        pytest.param(400, "Request validation failure", id="400-bad-request"),
        pytest.param(
            401, "Authentication is required and has failed or has not yet been provided.", id="401-unauthorized"
        ),
        pytest.param(
            403, "The server understood the request, but it refuses to authorize it.", id="403-forbidden"
        ),
        pytest.param(404, "Entity not found.", id="404-not-found"),
        pytest.param(409, "The request could not be completed.", id="409-conflict"),
        pytest.param(500, "Unknown error", id="unmapped-status-code"),
    ],
)
def test_message_includes_the_known_error_text(status_code: int, expected_text: str) -> None:
    error = IopoleApiException(status_code, "some details")
    assert str(error) == f"Iopole API (Error {status_code} - {expected_text}): some details."


def test_exposes_the_status_code() -> None:
    error = IopoleApiException(404, "not found")
    assert error.status_code == 404
