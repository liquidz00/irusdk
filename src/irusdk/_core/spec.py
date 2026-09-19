"""Declarative descriptions of an API call.

Endpoints are defined once as pure functions returning a :class:`RequestSpec` or
:class:`PagedSpec`. The sync and async transports are thin executors over these descriptions, so
endpoint logic is never written twice.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from .pagination import PaginationStrategy

T = TypeVar("T")

# Methods safe to replay when a request fails partway through.
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})


def drop_none(**kwargs: Any) -> dict[str, Any]:
    """
    Build a query-parameter dict from keyword arguments, omitting the ``None`` values.

    :return: The populated parameters.
    :rtype: dict[str, Any]
    """
    return {k: v for k, v in kwargs.items() if v is not None}


@dataclass(frozen=True)
class RequestSpec(Generic[T]):
    """
    A single API call, described but not performed.

    :ivar method: The HTTP method.
    :ivar path: The path below the tenant base URL, beginning with a slash.
    :ivar params: Query parameters.
    :ivar json: The request body, serialized as JSON. Mutually exclusive with ``data``/``files``.
    :ivar data: Form fields, for the endpoints that take multipart rather than JSON.
    :ivar files: File parts, in any shape httpx accepts. Iru takes the custom profile payload
        this way rather than as a JSON string.
    :ivar model: A Pydantic model to validate the response against. When ``None`` the decoded
        JSON is returned as-is.
    :ivar unwrap: The envelope key holding the payload. ``None`` means the body is the payload.
    :ivar idempotent: Whether the call is safe to retry. Defaults from the method; override it for
        the occasional vendor endpoint whose POST is genuinely replayable.
    """

    method: str
    path: str
    params: dict[str, Any] | None = None
    json: Any | None = None
    data: dict[str, Any] | None = None
    files: Any | None = None
    model: type[T] | None = None
    unwrap: str | None = None
    idempotent: bool | None = None

    def __post_init__(self) -> None:
        if self.json is not None and (self.data is not None or self.files is not None):
            raise ValueError("RequestSpec takes either json or data/files, not both")

    @property
    def is_idempotent(self) -> bool:
        """
        Whether this call may be retried.

        :rtype: bool
        """
        if self.idempotent is not None:
            return self.idempotent
        return self.method.upper() in _IDEMPOTENT_METHODS

    def with_params(self, extra: dict[str, Any]) -> "RequestSpec[T]":
        """
        Return a copy with additional query parameters merged in.

        Used by the paginators to layer page coordinates onto the caller's filters.

        :param extra: Parameters to merge over the existing ones.
        :type extra: dict[str, Any]
        :rtype: RequestSpec
        """
        return RequestSpec(
            method=self.method,
            path=self.path,
            params={**(self.params or {}), **extra},
            json=self.json,
            data=self.data,
            files=self.files,
            model=self.model,
            unwrap=self.unwrap,
            idempotent=self.idempotent,
        )


@dataclass(frozen=True)
class PagedSpec(Generic[T]):
    """
    A list endpoint, described but not performed.

    :ivar base: The underlying request, without page coordinates.
    :ivar strategy: How to page this endpoint and whether pages may be fetched concurrently.
    :ivar page_size: Records requested per page.
    """

    base: RequestSpec[T]
    strategy: "PaginationStrategy" = field(repr=False)
    page_size: int = 100
