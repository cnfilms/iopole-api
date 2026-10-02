[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Coverage](https://codecov.io/gh/cnfilms/iopole-api/graph/badge.svg)](https://codecov.io/gh/cnfilms/iopole-api)
[![pypi](https://img.shields.io/pypi/v/iopole-api.svg)](https://pypi.org/project/iopole-api/)
[![Downloads](https://img.shields.io/pypi/dd/iopole-api.svg)](https://pypi.org/project/iopole-api/)

![img](https://www.iopole.com/assets/logo.svg)

# iopole-api

Python connector for the [Iopole](https://www.iopole.com) e-invoicing platform.

## Installation

```bash
pip install iopole-api
```

## Quick start 🔧

```python
from iopole_api.client import IopoleAPI

api = IopoleAPI(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    base_url="IOPOLE_BASE_URL",
    auth_url="IOPOLE_AUTH_URL",
)

api.auth()
```

## Available methods

| Method | Description |
|---|---|
| `auth()` | Obtain / refresh the OAuth2 access token |
| `send_invoice(path)` | Upload an invoice PDF; returns the Iopole invoice ID |
| `get_invoice(invoice_id)` | Download the invoice file as `bytes` |
| `get_invoice_metadata(invoice_id)` | Retrieve invoice metadata as a `list` |
| `get_enrollment_link(siren)` | Return the onboarding URL for a company |
| `get_electronic_addresses(siren)` | Return Peppol identifiers for a company |
| `send_report_flux_10_1(report, address)` | Submit a B2B invoice e-report |
| `send_report_flux_10_3(report, address)` | Submit a daily B2C transaction report |
| `send_invoice_payment_status(uuid_presta, amount, vat_rate=0.0)` | Notify Iopole of an invoice payment |

## Tests and coverage

```bash
uv sync --locked --group dev
uv run pytest
```

The tests mock HTTP requests, so no Iopole credentials or network access are needed.
They cover every client endpoint, authentication, HTTP errors, and report serialization
and validation. Each run measures line and branch coverage across the entire package,
requires 100% coverage, and writes `coverage.xml`.

GitHub Actions runs the suite on Python 3.9 and 3.14 for pushes and pull requests.
After a successful push to the default branch, CI uploads coverage to Codecov to
update the badge. Enable `cnfilms/iopole-api` in Codecov once; the workflow uses
[GitHub OIDC authentication](https://github.com/codecov/codecov-action#using-oidc)
and does not require a `CODECOV_TOKEN` secret. The badge will show coverage after
the first successful upload.
