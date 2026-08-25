class IopoleApiException(Exception):
    """Raised when the Iopole API returns an error response."""

    ERROR_MESSAGES: dict[int, str] = {
        400: "Request validation failure",
        401: "Authentication is required and has failed or has not yet been provided.",
        403: "The server understood the request, but it refuses to authorize it.",
        404: "Entity not found.",
        409: "The request could not be completed.",
    }

    def __init__(self, status_code: int, msg: str) -> None:
        error_text = self.ERROR_MESSAGES.get(status_code, "Unknown error")
        super().__init__(f"Iopole API (Error {status_code} - {error_text}): {msg}.")
        self.status_code = status_code
