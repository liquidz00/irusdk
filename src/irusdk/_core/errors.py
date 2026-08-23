"""The irusdk exception hierarchy and the shared status-code mapping."""

from typing import Any, Mapping

# Status codes that indicate the tenant's request quota is exhausted.
RATE_LIMIT_STATUS = 429

# Keys pulled from an error body, in priority order. The Iru API is inconsistent
# about which one it uses.
_ERROR_BODY_KEYS = ("detail", "error", "errors", "message")


class IruError(Exception):
    """
    Base exception for every error raised by this SDK.

    Carries arbitrary keyword context (``status_code=401``, ``url=...``) and renders it into the
    formatted message as ``message (key1: val1 | key2: val2)``. Each keyword is also set as an
    instance attribute so callers can branch on it.

    :param message: The human-readable error message. Falls back to :attr:`default_message`.
    :type message: str | None
    :param kwargs: Arbitrary context attached to the exception.
    """

    default_message = "An error occurred"

    def __init__(self, message: str | None = None, **kwargs: Any) -> None:
        self.message = message or self.default_message
        self.context = kwargs
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
        self.formatted_message = self.format_message()
        super().__init__(self.formatted_message)

    def format_message(self) -> str:
        """
        Render the message with its context appended.

        :return: The message, followed by ``(key: value | ...)`` when context is present.
        :rtype: str
        """
        details = " | ".join(f"{k}: {v}" for k, v in self.context.items() if v is not None)
        return f"{self.message} ({details})" if details else self.message

    def __str__(self) -> str:
        return self.formatted_message


class ConfigurationError(IruError):
    """Raised when the client is constructed with invalid or missing configuration."""

    default_message = "Invalid client configuration"


class APIResponseError(IruError):
    """Raised when the API returns an unsuccessful status code."""

    default_message = "The Iru API returned an error"


class AuthenticationError(APIResponseError):
    """Raised on ``401`` or ``403`` — the API token is missing, invalid, or lacks permission."""

    default_message = "Authentication failed"


class NotFoundError(APIResponseError):
    """Raised on ``404`` — the requested resource does not exist."""

    default_message = "Requested resource was not found"


class RateLimitError(APIResponseError):
    """
    Raised on ``429`` once the retry policy has given up.

    Iru enforces 50 requests/second and 10,000 requests/hour per tenant. Seeing this means the
    client exhausted its retries; ``retry_after`` carries the server's hint when one was sent.
    """

    default_message = "Rate limit exceeded"


class ServerError(APIResponseError):
    """Raised on ``5xx`` — the API failed to process an otherwise valid request."""

    default_message = "The Iru API encountered a server error"


class PaginationError(IruError):
    """
    Raised when pagination cannot terminate safely.

    Guards against an endpoint that ignores its offset parameter, which would otherwise loop
    forever re-fetching the first page.
    """

    default_message = "Pagination did not terminate"


def extract_error_detail(body: Any) -> str | None:
    """
    Pull a human-readable detail string out of an error response body.

    :param body: The decoded JSON body, or ``None`` when the body was not JSON.
    :return: The first populated known error key, or ``None``.
    :rtype: str | None
    """
    if not isinstance(body, Mapping):
        return None
    for key in _ERROR_BODY_KEYS:
        if value := body.get(key):
            return str(value)
    return None


def raise_for_response(
    status_code: int,
    *,
    url: str | None = None,
    body: Any = None,
    retry_after: float | None = None,
) -> None:
    """
    Map an HTTP status code onto the exception hierarchy. A 2xx status is a no-op.

    This is the single status handler shared by both transports, so the sync and async clients
    cannot diverge in what they raise.

    :param status_code: The HTTP status code of the response.
    :type status_code: int
    :param url: The request URL, attached to the exception as context.
    :type url: str | None
    :param body: The decoded JSON body, used to extract an error detail.
    :param retry_after: Seconds the server asked the client to wait, for ``429`` responses.
    :type retry_after: float | None
    :raises APIResponseError: Or one of its subclasses, for any non-2xx status.
    """
    if 200 <= status_code < 300:
        return

    detail = extract_error_detail(body)
    context: dict[str, Any] = {"status_code": status_code, "url": url, "detail": detail}

    if status_code in (401, 403):
        raise AuthenticationError(**context)
    if status_code == 404:
        raise NotFoundError(**context)
    if status_code == RATE_LIMIT_STATUS:
        raise RateLimitError(retry_after=retry_after, **context)
    if 500 <= status_code < 600:
        raise ServerError(**context)
    raise APIResponseError(**context)
