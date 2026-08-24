"""Models for the tag endpoints."""

from .base import Model


class Tag(Model):
    """
    A tag as returned by ``GET /api/v1/tags``.

    :ivar id: The tag's identifier.
    :ivar name: The tag's name.
    """

    id: str | None = None
    name: str | None = None
