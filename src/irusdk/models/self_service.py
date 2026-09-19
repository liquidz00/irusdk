"""Models for the Self Service endpoints."""

from .base import Model


class SelfServiceCategory(Model):
    """
    A Self Service category as returned by ``GET /api/v1/self-service/categories``.

    :ivar id: The category's identifier, which is what a library item references.
    :ivar name: The category's display name.
    """

    id: str | None = None
    name: str | None = None
