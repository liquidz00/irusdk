"""Models for the user endpoints."""

from datetime import datetime

from .base import BlankAsNone, Model


class UserIntegration(Model):
    """
    The directory integration a user was sourced from.

    :ivar id: The integration's identifier.
    :ivar name: The integration's name.
    :ivar type: The integration type, such as ``"google"`` or ``"office365"``.
    """

    id: str | None = None
    name: str | None = None
    type: str | None = None


class User(Model):
    """
    A user as returned by ``GET /api/v1/users``.

    :ivar id: The user's identifier.
    :ivar name: The user's display name.
    :ivar email: The user's email address.
    :ivar active: Whether the user is active.
    :ivar archived: Whether the user has been archived.
    :ivar department: The user's department, when the directory supplies one.
    :ivar job_title: The user's job title, when the directory supplies one.
    :ivar device_count: How many devices are assigned to the user.
    :ivar integration: The directory integration the user came from.
    :ivar deprecated_user_id: The legacy numeric identifier, retained by the API.
    :ivar created_at: When the user record was created.
    :ivar updated_at: When the user record last changed.
    """

    id: str | None = None
    name: str | None = None
    email: str | None = None
    active: bool | None = None
    archived: bool | None = None
    department: BlankAsNone = None
    job_title: BlankAsNone = None
    device_count: int | None = None
    integration: UserIntegration | None = None
    deprecated_user_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
