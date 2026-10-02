"""Tests for iopole_api.models.enrollment.Enrollment.get_enrollment_link."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from iopole_api.client import IopoleAPI
from iopole_api.exceptions.exception import IopoleApiException
from tests._typing import RespondFn


def test_returns_the_onboarding_url(api: IopoleAPI, respond: RespondFn) -> None:
    respond(json_body={"onboardingUrl": "https://onboard.example.test/abc"})
    assert api.get_enrollment_link("123456789") == "https://onboard.example.test/abc"


def test_requests_enrollment_for_the_given_siren(api: IopoleAPI, http_request: Mock, respond: RespondFn) -> None:
    respond(json_body={"onboardingUrl": "https://onboard.example.test/abc"})
    api.get_enrollment_link("123456789")
    http_request.assert_called_once_with(
        url="https://api.example.test/config/french/enrollment",
        method="PUT",
        headers=api.headers,
        json={"siren": "123456789", "operatorRelation": {"direction": "OUTBOUND"}},
    )


def test_wraps_http_errors_with_a_domain_specific_message(api: IopoleAPI, respond: RespondFn) -> None:
    respond(status_code=404, content=b"no such company")
    with pytest.raises(IopoleApiException, match="Could not retrieve the enrollment link from Iopole") as caught:
        api.get_enrollment_link("123456789")
    assert caught.value.status_code == 404
    assert isinstance(caught.value.__cause__, IopoleApiException)
