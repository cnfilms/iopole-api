from iopoleapi.models.enrollment import Enrollment
from iopoleapi.models.factures import Factures
from iopoleapi.models.societe import Societe


class IopoleAPI(Factures, Enrollment, Societe):
    def __init__(self, client_id, client_secret, base_url, auth_url):
        super().__init__(client_id=client_id,
                         client_secret=client_secret,
                         base_url=base_url,
                         auth_url=auth_url)
