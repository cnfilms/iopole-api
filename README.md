[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
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

| Method                             | Description                                          |
| ---------------------------------- | ---------------------------------------------------- |
| `auth()`                           | Obtain / refresh the OAuth2 access token             |
| `send_invoice(path)`               | Upload an invoice PDF; returns the Iopole invoice ID |
| `get_invoice(invoice_id)`          | Download the invoice file as `bytes`                 |
| `get_invoice_metadata(invoice_id)` | Retrieve invoice metadata as a `list`                |
| `get_enrollment_link(siren)`       | Return the onboarding URL for a company              |
| `get_electronic_addresses(siren)`  | Return Peppol identifiers for a company              |

### E-reporting

Payloads are built with the dataclasses of `iopole_api.models.dataclasses` (`ReportFlux10_1` and
`ReportFlux10_3`) and passed as `report.to_dict()`. Every `send_*` method accepts an optional
`report_identifier` and returns the Iopole submission ID.

| Method                                             | Description                              |
| -------------------------------------------------- | ---------------------------------------- |
| `send_report_flux_10_1(report, siren)`             | B2B international invoice / credit note  |
| `send_report_flux_10_3(report, siren)`             | Daily summary of B2C transactions        |
| `update_report_flux_10_1(transaction_id, report)`  | Replace an invoice transaction           |
| `update_report_flux_10_3(transaction_id, report)`  | Replace a B2C transaction summary        |
| `delete_report_transaction(transaction_id)`        | Delete a transaction (flux 10.1 / 10.3)  |
| `search_reports(siren, **params)`                  | Search e-reporting folders over a period |
| `get_report_transmission_content(transmission_id)` | Download the XML flux of a transmission  |

`search_reports` takes the Iopole query parameters: `from` (required) and `to` as `YYYY-MM`, `offset`, `limit`
(pass `**{"from": "2026-09"}`, `from` being a Python keyword).

> The `update_*` and `delete_*` endpoints are still under construction at Iopole and currently answer
> `501 Not Implemented`.
