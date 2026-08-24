"""Small models shared across several endpoint families."""

from .base import Model


class UserRef(Model):
    """
    A user as embedded in another record.

    :ivar id: The user's identifier.
    :ivar name: The user's display name.
    :ivar email: The user's email address.
    :ivar is_archived: Whether the user has been archived.
    """

    id: str | None = None
    name: str | None = None
    email: str | None = None
    is_archived: bool | None = None


class BlueprintRef(Model):
    """
    A blueprint as embedded in another record.

    :ivar id: The blueprint's identifier.
    :ivar name: The blueprint's name.
    """

    id: str | None = None
    name: str | None = None
