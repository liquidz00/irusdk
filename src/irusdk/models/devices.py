"""Models for the device endpoints."""

from datetime import datetime, timezone

from pydantic import computed_field

from .base import BlankAsNone, Model
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
    :ivar lost_mode_status: The current Lost Mode status, ``None`` when not in Lost Mode.
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
    asset_tag: BlankAsNone = None
    blueprint_id: str | None = None
    blueprint_name: str | None = None
    mdm_enabled: bool | None = None
    agent_installed: bool | None = None
    agent_version: str | None = None
    is_missing: bool | None = None
    is_removed: bool | None = None
    first_enrollment: datetime | None = None
    last_enrollment: datetime | None = None
    lost_mode_status: BlankAsNone = None
    tags: list[str] | None = None

    @computed_field
    @property
    def os_major(self) -> int | None:
        """
        The major version of :attr:`os_version`, as an integer.

        String comparison on version numbers is the classic fleet-reporting bug — ``"9.2"`` sorts
        above ``"15.1"`` — so anything counting devices by OS should reach for this instead.

        :return: The major version, or ``None`` when the API reported no parseable version.
        :rtype: int | None
        """
        parts = self.os_version_info
        return parts[0] if parts else None

    @property
    def os_version_info(self) -> tuple[int, ...]:
        """
        :attr:`os_version` split into comparable integers, in the style of ``sys.version_info``.

        Supports ordering comparisons — ``device.os_version_info >= (14, 4)`` — which the raw
        string does not. Non-numeric segments end the tuple, so a build suffix cannot poison it.

        :return: The version segments, empty when there is nothing parseable.
        :rtype: tuple[int, ...]
        """
        if not self.os_version:
            return ()

        parts: list[int] = []
        for segment in self.os_version.strip().split("."):
            if not segment.isdigit():
                break
            parts.append(int(segment))
        return tuple(parts)

    @property
    def days_since_check_in(self) -> int | None:
        """
        Whole days since :attr:`last_check_in`.

        Deliberately not a serialized field: it depends on the current time, so freezing it into
        ``model_dump()`` output would make a dump stale the moment it was written.

        :return: The elapsed days, or ``None`` when the device has never checked in.
        :rtype: int | None
        """
        if self.last_check_in is None:
            return None

        seen = self.last_check_in
        if seen.tzinfo is None:
            seen = seen.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - seen).days)
