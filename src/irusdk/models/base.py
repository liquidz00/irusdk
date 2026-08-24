"""Base classes and shared field types for every model in this package.

These live here rather than in ``__init__.py`` so that the package's ``__init__`` can be nothing
but re-exports. A submodule importing its base from the package it is re-exported into is a
circular import waiting to happen.
"""

from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel


def _blank_to_none(value: Any) -> Any:
    """Collapse a blank string into ``None``, leaving everything else untouched."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


# Defined ahead of the classes because the annotation below needs it at import time.
BlankAsNone = Annotated[str | None, BeforeValidator(_blank_to_none)]
"""A string field where the API sends ``""`` instead of ``null`` for an absent value."""


class Model(BaseModel):
    """
    Base for every model in this package.

    :cvar model_config: Permits unknown fields so a new API field is carried through rather than
        raising.
    """

    model_config = ConfigDict(extra="allow")

    @property
    def unknown_fields(self) -> dict[str, Any]:
        """
        Fields the API returned that this model does not declare.

        Empty in the normal case. A non-empty result means Iru has added something, which is the
        cue to widen the model.

        :rtype: dict[str, Any]
        """
        return dict(self.model_extra or {})


class UpstreamModel(Model):
    """
    Base for the handful of endpoints that return camelCase.

    Most of the Iru API is snake_case and needs only :class:`Model`. Where an endpoint deviates,
    this base keeps Python attributes snake_case while accepting the camelCase wire names.
    """

    model_config = ConfigDict(
        extra="allow",
        alias_generator=to_camel,
        populate_by_name=True,
    )
