"""Models for the custom profile endpoints."""

from .base import Model


class CustomProfile(Model):
    """
    A custom profile as returned by ``/api/v1/library/custom-profiles``.

    :ivar id: The library item's identifier. Iru assigns this on create and ignores any value
        sent with the request.
    :ivar name: The profile's name.
    :ivar active: Whether the profile is active.
    :ivar profile: The ``.mobileconfig`` payload, as XML.
    :ivar mdm_identifier: The profile's top-level ``PayloadIdentifier``, which Iru derives from
        :attr:`id` as ``com.kandji.profile.custom.<id>``. It is assigned, not authored.
    :ivar created_at: When the profile was created.
    :ivar updated_at: When the profile was last modified.
    :ivar runs_on_mac: Whether the profile targets macOS.
    :ivar runs_on_iphone: Whether the profile targets iPhone.
    :ivar runs_on_ipad: Whether the profile targets iPad.
    :ivar runs_on_tv: Whether the profile targets Apple TV.
    :ivar runs_on_vision: Whether the profile targets Apple Vision Pro.
    """

    id: str | None = None
    name: str | None = None
    active: bool | None = None
    profile: str | None = None
    mdm_identifier: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    runs_on_mac: bool | None = None
    runs_on_iphone: bool | None = None
    runs_on_ipad: bool | None = None
    runs_on_tv: bool | None = None
    runs_on_vision: bool | None = None
