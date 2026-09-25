"""Pydantic models for Iru API responses.

Every field is optional and unknown fields are preserved. Iru adds fields between releases, and a
model that rejected them would break the SDK on the vendor's schedule rather than ours.

Every model is re-exported here, so ``from irusdk.models import Device`` works without knowing
which submodule it lives in. The base classes and shared field types are in :mod:`.base`.

.. warning::
    These models describe responses; they are not input validation. Do not rely on them to
    guarantee a field is present.
"""

from .base import BlankAsNone, Model, UpstreamModel
from .blueprints import Blueprint, EnrollmentCode
from .common import BlueprintRef, UserRef
from .custom_apps import CustomApp, InstallEnforcement, InstallType
from .custom_profiles import CustomProfile
from .custom_scripts import CustomScript, ExecutionFrequency
from .devices import Device
from .library import LibraryItem
from .self_service import SelfServiceCategory
from .tags import Tag
from .users import User, UserIntegration

__all__ = [
    "BlankAsNone",
    "Blueprint",
    "BlueprintRef",
    "CustomApp",
    "CustomProfile",
    "CustomScript",
    "Device",
    "EnrollmentCode",
    "ExecutionFrequency",
    "InstallEnforcement",
    "InstallType",
    "LibraryItem",
    "Model",
    "SelfServiceCategory",
    "Tag",
    "UpstreamModel",
    "User",
    "UserIntegration",
    "UserRef",
]
