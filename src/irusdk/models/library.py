"""Models for library items as they appear from the fleet side.

This SDK does not author library content — see the scope note in the documentation. What remains
here is the read-only shape used when reporting what is assigned to a blueprint or installed on a
device.
"""

from .base import Model


class LibraryItem(Model):
    """
    A library item as summarised on a blueprint or device.

    :ivar id: The item's identifier.
    :ivar name: The item's name.
    :ivar type: The item type, such as ``"Custom App"``.
    :ivar active: Whether the item is active.
    """

    id: str | None = None
    name: str | None = None
    type: str | None = None
    active: bool | None = None
