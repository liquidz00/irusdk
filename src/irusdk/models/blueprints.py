"""Models for the blueprint endpoints."""

from typing import Any

from pydantic import computed_field

from .base import BlankAsNone, Model


class EnrollmentCode(Model):
    """
    A blueprint's manual enrollment code.

    :ivar code: The enrollment code itself.
    :ivar is_active: Whether the code currently accepts enrollments.
    """

    code: str | None = None
    is_active: bool | None = None


class Blueprint(Model):
    """
    A blueprint as returned by ``GET /api/v1/blueprints``.

    :ivar id: The blueprint's identifier.
    :ivar name: The blueprint's name.
    :ivar icon: The icon slug shown in the Iru console.
    :ivar color: The colour token shown in the Iru console.
    :ivar description: The blueprint's description.
    :ivar params: Parameter settings attached to the blueprint.
    :ivar computers_count: How many devices are assigned.
    :ivar missing_computers_count: How many assigned devices are flagged missing.
    :ivar enrollment_code: The manual enrollment code, when one is configured.
    :ivar type: The blueprint type, such as ``"standard"``.
    """

    id: str | None = None
    name: str | None = None
    icon: BlankAsNone = None
    color: BlankAsNone = None
    description: BlankAsNone = None
    params: dict[str, Any] | None = None
    computers_count: int | None = None
    missing_computers_count: int | None = None
    enrollment_code: EnrollmentCode | None = None
    type: str | None = None

    @computed_field
    @property
    def present_count(self) -> int | None:
        """
        Assigned devices not flagged missing.

        :return: The count, or ``None`` when the API reported no assignment count.
        :rtype: int | None
        """
        if self.computers_count is None:
            return None
        return max(0, self.computers_count - (self.missing_computers_count or 0))

    @computed_field
    @property
    def present_percent(self) -> float | None:
        """
        :attr:`present_count` as a percentage of assigned devices, rounded to two places.

        Named for what it measures — devices reporting in — rather than "compliance", which in MDM
        already means profile and policy state and would mislead.

        :return: The percentage, or ``None`` when no devices are assigned.
        :rtype: float | None
        """
        if not self.computers_count:
            return None
        return round((self.present_count or 0) / self.computers_count * 100, 2)
