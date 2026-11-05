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

### Authentication

| Method   | Description                              |
| -------- | ---------------------------------------- |
| `auth()` | Obtain / refresh the OAuth2 access token |

### Invoices

| Method                                                | Description                                          |
| ----------------------------------------------------- | ---------------------------------------------------- |
| `send_invoice(path)`                                  | Upload an invoice PDF; returns the Iopole invoice ID |
| `get_invoice(invoice_id)`                             | Download the invoice file as `bytes`                 |
| `get_invoice_metadata(invoice_id)`                    | Retrieve invoice metadata as a `list`                |
| `get_invoice_status_history(invoice_id)`              | Full status history of an invoice (low rate limit)   |
| `send_invoice_payment_status(uuid_presta, amount, …)` | Notify Iopole that an invoice has been paid          |

### Companies

| Method                            | Description                             |
| --------------------------------- | --------------------------------------- |
| `get_enrollment_link(siren)`      | Return the onboarding URL for a company |
| `get_electronic_addresses(siren)` | Return Peppol identifiers for a company |

### E-reporting

| Method                                 | Description                                            |
| -------------------------------------- | ------------------------------------------------------ |
| `send_report_flux_10_1(report, siren)` | Flux 10.1: one B2B international invoice / credit note |
| `send_report_flux_10_3(report, siren)` | Flux 10.3: daily summary of B2C transactions           |

`report` is built with the `ReportFlux10_1` / `ReportFlux10_3` dataclasses of
`iopole_api.models.dataclasses` and passed as `report.to_dict()`. Both methods return the
`transactionId` given by Iopole. The transaction is then validated asynchronously, through the
`EREPORTING_TRANSACTION_ATTACHED` / `EREPORTING_ERROR` webhook events.

> [!WARNING]
> Iopole does not deduplicate transactions, and flux 10.3 submissions for the same day are added
> together: a transaction accepted by Iopole must never be sent again.

```python
from iopole_api import IopoleApiException, IopoleMissingIdException

try:
    transaction_id = api.send_report_flux_10_3(report.to_dict(), siren="123456789")
except IopoleMissingIdException:
    ...  # accepted by Iopole but no transactionId returned: do NOT send it again
except IopoleApiException:
    ...  # refused by Iopole: can be sent again once fixed
```

## Errors

| Exception                  | Raised when                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| `IopoleApiException`       | Iopole returns an HTTP error (`status_code` holds the HTTP code)   |
| `IopoleMissingIdException` | Iopole accepts an e-reporting transaction without returning its id |
