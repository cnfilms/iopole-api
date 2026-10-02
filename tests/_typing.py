from __future__ import annotations

from collections.abc import Callable

import requests

RespondFn = Callable[..., requests.Response]
