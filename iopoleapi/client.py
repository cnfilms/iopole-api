from iopoleapi.models.enrollment import Enrollment
from iopoleapi.models.factures import Factures
from iopoleapi.models.societe import Societe


class IopoleAPI(Factures, Enrollment, Societe):
    """Iopole API client.

    Combines invoice management (Factures), company enrollment (Enrollment),
    and directory lookups (Societe) into a single entry-point class.

    Args:
        client_id: OAuth2 client identifier.
        client_secret: OAuth2 client secret.
        base_url: Base URL of the Iopole REST API (trailing slash is stripped).
        auth_url: Token endpoint URL.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        auth_url: str,
    ) -> None:
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
            auth_url=auth_url,
        )
