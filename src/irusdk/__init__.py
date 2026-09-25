"""A Python SDK for the Iru (formerly Kandji) Endpoint Management API."""

from .__about__ import __title__, __version__
from ._core.config import IruConfig
from ._core.errors import (
    APIResponseError,
    AuthenticationError,
    ConfigurationError,
    IruError,
    NotFoundError,
    PaginationError,
    PayloadTransferError,
    RateLimitError,
    ServerError,
)
from ._core.pagination import Page
from ._core.urls import Region
from .client import AsyncIruClient, IruClient

__all__ = [
    "APIResponseError",
    "AsyncIruClient",
    "AuthenticationError",
    "ConfigurationError",
    "IruClient",
    "IruConfig",
    "IruError",
    "NotFoundError",
    "Page",
    "PaginationError",
    "PayloadTransferError",
    "RateLimitError",
    "Region",
    "ServerError",
    "__title__",
    "__version__",
]
