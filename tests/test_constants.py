"""Tests for iopole_api.constants.constants.IopoleStatus."""

from __future__ import annotations

from iopole_api.constants.constants import IopoleStatus


def test_values_match_the_iopole_status_codes() -> None:
    assert IopoleStatus.SUBMITTED.value == 200
    assert IopoleStatus.PAYMENT_SENT.value == 211
    assert IopoleStatus.REJECTED.value == 213


def test_members_are_constructible_from_their_int_value() -> None:
    assert IopoleStatus(205) is IopoleStatus.APPROVED
