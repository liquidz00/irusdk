"""Models for the device endpoints."""

from datetime import datetime

from . import Model
from .common import UserRef


class Device(Model):
    """
    A device record as returned by ``GET /api/v1/devices``.

    :ivar device_id: The device's unique identifier.
    :ivar device_name: The device's name.
    :ivar model: The hardware model, e.g. ``"MacBook Air (M1, 2020)"``.
    :ivar serial_number: The hardware serial number.
    :ivar platform: One of ``Mac``, ``iPad``, ``iPhone``, ``AppleTV``, ``Android``, ``Windows``.
    :ivar os_version: The installed OS version.
    :ivar supplemental_build_version: The supplemental build, for rapid security responses.
    :ivar supplemental_os_version_extra: The supplemental OS version suffix.
    :ivar last_check_in: When the agent last checked in.
    :ivar user: The assigned user, if any.
    :ivar asset_tag: The asset tag.
    :ivar blueprint_id: Identifier of the assigned blueprint.
    :ivar blueprint_name: Name of the assigned blueprint.
    :ivar mdm_enabled: Whether MDM is enabled on the device.
    :ivar agent_installed: Whether the Iru agent is installed.
    :ivar agent_version: The installed agent version.
    :ivar is_missing: Whether the device is flagged missing.
    :ivar is_removed: Whether the device has been removed.
    :ivar first_enrollment: When the device first enrolled.
    :ivar last_enrollment: When the device most recently enrolled.
    :ivar lost_mode_status: The current Lost Mode status, empty when not in Lost Mode.
    :ivar tags: Tag names applied to the device.
    """

    device_id: str | None = None
    device_name: str | None = None
    model: str | None = None
    serial_number: str | None = None
    platform: str | None = None
    os_version: str | None = None
    supplemental_build_version: str | None = None
    supplemental_os_version_extra: str | None = None
    last_check_in: datetime | None = None
    user: UserRef | None = None
    asset_tag: str | None = None
    blueprint_id: str | None = None
    blueprint_name: str | None = None
    mdm_enabled: bool | None = None
    agent_installed: bool | None = None
    agent_version: str | None = None
    is_missing: bool | None = None
    is_removed: bool | None = None
    first_enrollment: datetime | None = None
    last_enrollment: datetime | None = None
    lost_mode_status: str | None = None
    tags: list[str] | None = None
