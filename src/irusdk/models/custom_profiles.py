"""Models for the custom profile endpoints."""

from .base import Model


class CustomProfile(Model):
    """
    A custom profile as returned by ``/api/v1/library/custom-profiles``.

    :ivar id: The library item's identifier. Iru assigns this on create and ignores any value
        sent with the request.
    :ivar name: The profile's name.
    :ivar active: Whether the profile is active.
    :ivar profile: The ``.mobileconfig`` payload, as XML. Iru owns three top-level keys and
        rewrites them on every write: ``PayloadIdentifier`` (from :attr:`id`),
        ``PayloadDisplayName`` (from :attr:`name`), and ``PayloadUUID``, which is regenerated
        even by a metadata-only update so macOS reinstalls the profile. Everything inside
        ``PayloadContent`` is stored verbatim, global-variable tokens included.
    :ivar mdm_identifier: The profile's top-level ``PayloadIdentifier``, which Iru derives from
        :attr:`id` as ``com.kandji.profile.custom.<id>``. It is assigned, not authored.
    :ivar created_at: When the profile was created.
    :ivar updated_at: When the profile was last modified.
    :ivar runs_on_mac: Whether the profile targets macOS.
    :ivar runs_on_iphone: Whether the profile targets iPhone.
    :ivar runs_on_ipad: Whether the profile targets iPad.
    :ivar runs_on_tv: Whether the profile targets Apple TV.
    :ivar runs_on_vision: Whether the profile targets Apple Vision Pro.
    :ivar runs_on_android: Always ``False``. Iru returns it from a serializer it shares with
        other library items; a ``.mobileconfig`` cannot target Android, so there is no
        matching argument on create or update.
    :ivar runs_on_windows: Always ``False``, for the same reason as :attr:`runs_on_android`.
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
    runs_on_android: bool | None = None
    runs_on_windows: bool | None = None
