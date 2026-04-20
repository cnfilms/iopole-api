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
from iopoleapi.client import IopoleAPI

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

