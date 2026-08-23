"""Models for the blueprint endpoints."""

from typing import Any

from . import Model


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
    icon: str | None = None
    color: str | None = None
    description: str | None = None
    params: dict[str, Any] | None = None
    computers_count: int | None = None
    missing_computers_count: int | None = None
    enrollment_code: EnrollmentCode | None = None
    type: str | None = None
