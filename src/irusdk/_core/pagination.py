"""Pagination strategies.

The Iru API pages several different ways, so each strategy owns the "what are the next page's
parameters, are we done, and can the remaining pages be fetched at once" logic. The strategies are
pure — no I/O — and both transports consume them unchanged.

Envelope shapes in the wild:

===============================================  ==================  ==========================
Envelope                                         Parameters          Endpoints
===============================================  ==================  ==========================
bare JSON array                                  ``limit``/``offset``  ``/devices``
``{count, next, previous, results}``             ``limit``/``offset``  blueprints, library activity
``{count, next, previous, results}``             ``page``              custom apps, scripts, ADE
``{offset, limit, total, cursor, data}``         ``limit``/``offset``  ``/prism/*``
``{total, page, size, results}``                 ``page``/``size``     vulnerability management
``{next, previous, results}``                    ``cursor``            users, admins, audit events
===============================================  ==================  ==========================
"""

import math
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar
from urllib.parse import parse_qsl, urlparse

T = TypeVar("T")


@dataclass(frozen=True)
class PageResult:
    """
    One decoded page, before its records are validated into models.

    :ivar items: The raw records on this page.
    :ivar total: The total record count when the envelope reports one, else ``None``.
    :ivar next_params: Query parameters for the following page, extracted from a ``next`` URL.
    :ivar raw: The full decoded body, kept so callers can reach envelope extras.
    """

    items: list[Any]
    total: int | None = None
    next_params: dict[str, Any] | None = None
    raw: Any = None


@dataclass(frozen=True)
class Page(Generic[T]):
    """
    A page of validated records, as handed to callers by a paginator.

    :ivar index: Zero-based position of this page in the sequence.
    :ivar items: The validated records.
    :ivar total: The total record count when the API reports one, else ``None``.
    """

    index: int
    items: list[T]
    total: int | None = None
    raw: Any = field(default=None, repr=False)

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)


class PaginationStrategy(Protocol):
    """The contract every pagination strategy implements."""

    def first_params(self, page_size: int) -> dict[str, Any]:
        """Query parameters for the first page."""
        ...

    def parse(self, body: Any) -> PageResult:
        """Decode a response body into a :class:`PageResult`."""
        ...

    def next_params(self, prev: PageResult, page_size: int, fetched: int) -> dict[str, Any] | None:
        """Parameters for the page after ``prev``, or ``None`` when the sequence is exhausted."""
        ...

    def plan(self, first: PageResult, page_size: int) -> list[dict[str, Any]] | None:
        """
        Parameters for every page after the first, when they can be computed up front.

        Returning ``None`` means the endpoint must be walked serially.
        """
        ...


def _extract_next_params(body: Any) -> dict[str, Any] | None:
    """Pull the query parameters out of an envelope's ``next`` URL, if it has one."""
    if not isinstance(body, dict):
        return None
    if not (nxt := body.get("next")):
        return None
    return dict(parse_qsl(urlparse(str(nxt)).query)) or None


class OffsetPagination:
    """
    ``limit`` / ``offset`` paging.

    Covers the bare-array device list, the ``{count, ..., results}`` envelope, and Prism's
    ``{total, ..., data}`` envelope, which differ only in where the records and the total live.

    :param results_key: Envelope key holding the records. ``None`` means the body is a bare array.
    :type results_key: str | None
    :param total_key: Envelope key holding the record count, when the API reports one.
    :type total_key: str | None
    """

    def __init__(self, results_key: str | None = None, total_key: str | None = None) -> None:
        self.results_key = results_key
        self.total_key = total_key

    def first_params(self, page_size: int) -> dict[str, Any]:
        return {"limit": page_size, "offset": 0}

    def parse(self, body: Any) -> PageResult:
        if self.results_key is None:
            items = body if isinstance(body, list) else []
            return PageResult(items=list(items), raw=body)

        envelope = body if isinstance(body, dict) else {}
        total = envelope.get(self.total_key) if self.total_key else None
        return PageResult(
            items=list(envelope.get(self.results_key) or []),
            total=total if isinstance(total, int) else None,
            next_params=_extract_next_params(envelope),
            raw=body,
        )

    def next_params(self, prev: PageResult, page_size: int, fetched: int) -> dict[str, Any] | None:
        # A short page is the only end-of-sequence signal when no total is reported.
        if not prev.items or len(prev.items) < page_size:
            return None
        if prev.total is not None and fetched >= prev.total:
            return None
        return {"limit": page_size, "offset": fetched}

    def plan(self, first: PageResult, page_size: int) -> list[dict[str, Any]] | None:
        if first.total is None or not first.items:
            return None
        stride = len(first.items)
        return [
            {"limit": stride, "offset": offset} for offset in range(stride, first.total, stride)
        ]


class PagePagination:
    """
    One-based ``page`` paging, optionally with an explicit page-size parameter.

    :param results_key: Envelope key holding the records.
    :type results_key: str
    :param total_key: Envelope key holding the record count.
    :type total_key: str
    :param size_param: Name of the page-size parameter, or ``None`` when the endpoint has none.
    :type size_param: str | None
    """

    def __init__(
        self,
        results_key: str = "results",
        total_key: str = "count",
        size_param: str | None = None,
    ) -> None:
        self.results_key = results_key
        self.total_key = total_key
        self.size_param = size_param

    def _page_params(self, page: int, page_size: int) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page}
        if self.size_param:
            params[self.size_param] = page_size
        return params

    def first_params(self, page_size: int) -> dict[str, Any]:
        return self._page_params(1, page_size)

    def parse(self, body: Any) -> PageResult:
        envelope = body if isinstance(body, dict) else {}
        total = envelope.get(self.total_key)
        return PageResult(
            items=list(envelope.get(self.results_key) or []),
            total=total if isinstance(total, int) else None,
            next_params=_extract_next_params(envelope),
            raw=body,
        )

    def next_params(self, prev: PageResult, page_size: int, fetched: int) -> dict[str, Any] | None:
        if not prev.items:
            return None
        if prev.total is not None and fetched >= prev.total:
            return None
        if prev.next_params:
            return prev.next_params
        if len(prev.items) < page_size:
            return None
        return self._page_params(fetched // len(prev.items) + 1, page_size)

    def plan(self, first: PageResult, page_size: int) -> list[dict[str, Any]] | None:
        if first.total is None or not first.items:
            return None
        size = len(first.items)
        last_page = math.ceil(first.total / size)
        return [self._page_params(page, size) for page in range(2, last_page + 1)]


class CursorPagination:
    """
    Opaque-cursor paging, where the envelope carries a ``next`` URL and no total.

    Inherently serial: the next cursor is only known once the current page has been fetched.

    Also the right choice for an endpoint that returns a ``next`` URL but documents no page
    parameter — following the server's own link is safer than guessing one it may ignore.

    :param results_key: Envelope key holding the records.
    :type results_key: str
    :param size_param: Name of the page-size parameter. The Iru API is inconsistent here:
        ``/users`` takes ``sizePerPage`` while ``/tags`` documents none at all.
    :type size_param: str | None
    """

    def __init__(self, results_key: str = "results", size_param: str | None = "limit") -> None:
        self.results_key = results_key
        self.size_param = size_param

    def first_params(self, page_size: int) -> dict[str, Any]:
        return {self.size_param: page_size} if self.size_param else {}

    def parse(self, body: Any) -> PageResult:
        envelope = body if isinstance(body, dict) else {}
        return PageResult(
            items=list(envelope.get(self.results_key) or []),
            next_params=_extract_next_params(envelope),
            raw=body,
        )

    def next_params(self, prev: PageResult, page_size: int, fetched: int) -> dict[str, Any] | None:
        return prev.next_params

    def plan(self, first: PageResult, page_size: int) -> list[dict[str, Any]] | None:
        return None
