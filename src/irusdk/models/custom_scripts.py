"""Models for the custom script endpoints."""

from enum import StrEnum

from .base import BlankAsNone, Model


class ExecutionFrequency(StrEnum):
    """How often Iru runs a custom script."""

    ONCE = "once"
    EVERY_15_MIN = "every_15_min"
    EVERY_DAY = "every_day"
    NO_ENFORCEMENT = "no_enforcement"


class CustomScript(Model):
    """
    A custom script as returned by ``/api/v1/library/custom-scripts``.

    :ivar id: The library item's identifier. Iru assigns this on create and ignores any value
        sent with the request.
    :ivar name: The script's name.
    :ivar active: Whether the script is active.
    :ivar execution_frequency: How often the script runs. Typed as a string rather than
        :class:`ExecutionFrequency` so a frequency Iru adds later is carried through instead of
        raising; compare against the enum's values.
    :ivar restart: Whether the device restarts after the script runs.
    :ivar script: The audit script's contents.
    :ivar remediation_script: The remediation script's contents. The API sends ``""`` when
        there is none, which :data:`~irusdk.models.base.BlankAsNone` collapses to ``None``.
    :ivar created_at: When the script was created.
    :ivar updated_at: When the script was last modified.
    :ivar show_in_self_service: Whether the script is offered in Self Service.
    :ivar self_service_category_id: The Self Service category the script appears under.
    :ivar self_service_recommended: Whether the script is featured in Self Service.
    """

    id: str | None = None
    name: str | None = None
    active: bool | None = None
    execution_frequency: str | None = None
    restart: bool | None = None
    script: str | None = None
    remediation_script: BlankAsNone = None
    created_at: str | None = None
    updated_at: str | None = None
    show_in_self_service: bool | None = None
    self_service_category_id: str | None = None
    self_service_recommended: bool | None = None
