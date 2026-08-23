"""Transport helpers with no I/O, shared by the sync and async transports."""

import json
import ssl
from typing import Any, Iterator

import httpx
import truststore

from .._core.config import IruConfig
from .._core.errors import PaginationError
from .._core.pagination import Page, PageResult
from .._core.spec import RequestSpec


def build_headers(token: str, config: IruConfig) -> dict[str, str]:
    """
    Build the headers sent on every request.

    :param token: The tenant API token.
    :type token: str
    :param config: The client configuration.
    :type config: IruConfig
    :rtype: dict[str, str]
    """
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": config.user_agent,
    }


def build_verify(config: IruConfig) -> ssl.SSLContext | str | bool:
    """
    Resolve the TLS verification setting into something httpx accepts.

    truststore.SSLContext is used intentionally to account for MacAdmins with security software
    and self-signed certificates.

    :param config: The client configuration.
    :type config: IruConfig
    :rtype: ssl.SSLContext | str | bool
    """
    if config.verify is True:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    return config.verify


def build_client_kwargs(base_url: str, token: str, config: IruConfig) -> dict[str, Any]:
    """
    Assemble the constructor arguments shared by ``httpx.Client`` and ``httpx.AsyncClient``.

    :rtype: dict[str, Any]
    """
    return {
        "base_url": base_url,
        "headers": build_headers(token, config),
        "timeout": httpx.Timeout(config.timeout),
        "limits": httpx.Limits(max_connections=config.max_concurrency),
        "verify": build_verify(config),
        "follow_redirects": True,
    }


def decode_json(response: httpx.Response) -> Any:
    """
    Decode a response body as JSON, tolerating an empty or non-JSON body.

    :return: The decoded body, or ``None`` when there is nothing to decode.
    """
    if not response.content:
        return None
    try:
        return response.json()
    except (json.JSONDecodeError, ValueError):
        return None


def build_result(spec: RequestSpec[Any], body: Any) -> Any:
    """
    Unwrap and validate a response body according to its spec.

    :param spec: The spec that produced the response.
    :param body: The decoded JSON body.
    :return: A validated model instance, a list of them, or the raw body when the spec names no
        model.
    """
    payload = body
    if spec.unwrap and isinstance(body, dict):
        payload = body.get(spec.unwrap)

    if spec.model is None or payload is None:
        return payload
    if isinstance(payload, list):
        return [spec.model.model_validate(item) for item in payload]
    return spec.model.model_validate(payload)


def validate_items(spec: RequestSpec[Any], items: list[Any]) -> list[Any]:
    """
    Validate a page's records against the spec's model.

    :rtype: list
    """
    if spec.model is None:
        return items
    return [spec.model.model_validate(item) for item in items]


class SerialGuard:
    """
    Termination guard for serial pagination.

    Endpoints that report no total give only a short page as an end-of-sequence signal. If one
    ever ignores its offset, a naive loop would re-fetch page one forever; this catches that.

    :param max_pages: Ceiling on pages walked in a single sequence.
    :type max_pages: int
    """

    def __init__(self, max_pages: int) -> None:
        self.max_pages = max_pages
        self._pages = 0
        self._last_fingerprint: Any = None

    def check(self, result: PageResult, path: str) -> None:
        """
        Record a page and raise if the sequence looks non-terminating.

        :raises PaginationError: On exceeding ``max_pages`` or seeing a repeated first record.
        """
        self._pages += 1
        if self._pages > self.max_pages:
            raise PaginationError(
                "Exceeded the maximum page count", path=path, max_pages=self.max_pages
            )

        fingerprint = _fingerprint(result)
        if fingerprint is not None and fingerprint == self._last_fingerprint:
            raise PaginationError(
                "Received the same first record twice; the endpoint may be ignoring its offset",
                path=path,
                page=self._pages,
            )
        self._last_fingerprint = fingerprint


def _fingerprint(result: PageResult) -> Any:
    """A cheap identity for a page's first record, used to spot a stuck cursor."""
    if not result.items:
        return None
    first = result.items[0]
    if isinstance(first, dict):
        for key in ("id", "device_id", "uuid", "_id"):
            if key in first:
                return first[key]
        return None
    return None


def to_page(spec: Any, index: int, raw: PageResult) -> Any:
    """
    Build a public :class:`~irusdk._core.pagination.Page` from a decoded page.

    :param spec: The :class:`~irusdk._core.spec.PagedSpec` being walked.
    :param index: Zero-based position of this page.
    :param raw: The decoded page.
    """
    return Page(
        index=index,
        items=validate_items(spec.base, raw.items),
        total=raw.total,
        raw=raw.raw,
    )


def chunked(items: list[Any], size: int) -> Iterator[list[Any]]:
    """Split a list into consecutive batches of at most ``size``."""
    for start in range(0, len(items), size):
        yield items[start : start + size]
