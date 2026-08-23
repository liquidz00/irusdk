"""Pydantic models for Iru API responses.

Every field is optional and unknown fields are preserved. Iru adds fields between releases, and a
model that rejected them would break the SDK on the vendor's schedule rather than ours.

.. warning::
    These models describe responses; they are not input validation. Do not rely on them to
    guarantee a field is present.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Model(BaseModel):
    """
    Base for every model in this package.

    :cvar model_config: Permits unknown fields so a new API field is carried through rather than
        raising.
    """

    model_config = ConfigDict(extra="allow")


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
