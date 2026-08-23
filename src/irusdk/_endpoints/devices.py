"""Device endpoint definitions.

Written once and consumed by both the sync and async device services.
"""

from typing import Any

from .._core.pagination import OffsetPagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.devices import Device

# The API caps the device list at 300 records per page.
MAX_DEVICE_PAGE_SIZE = 300

_DEVICES = "/api/v1/devices"


def list_devices(
    *,
    blueprint_id: str | None = None,
    device_name: str | None = None,
    filevault_enabled: bool | None = None,
    mac_address: str | None = None,
    model: str | None = None,
    os_version: str | None = None,
    ordering: str | None = None,
    platform: str | None = None,
    serial_number: str | None = None,
    tag_id: str | None = None,
    tag_name: str | None = None,
    user_email: str | None = None,
    user_id: str | None = None,
    user_name: str | None = None,
    page_size: int = MAX_DEVICE_PAGE_SIZE,
) -> PagedSpec[Device]:
    """Build the spec for the paginated device list."""
    return PagedSpec(
        base=RequestSpec(
            method="GET",
            path=_DEVICES,
            params=drop_none(
                blueprint_id=blueprint_id,
                device_name=device_name,
                filevault_enabled=filevault_enabled,
                mac_address=mac_address,
                model=model,
                os_version=os_version,
                ordering=ordering,
                platform=platform,
                serial_number=serial_number,
                tag_id=tag_id,
                tag_name=tag_name,
                user_email=user_email,
                user_id=user_id,
                user_name=user_name,
            ),
            model=Device,
        ),
        # The device list is a bare JSON array with no total, so pages are walked serially.
        strategy=OffsetPagination(),
        page_size=min(page_size, MAX_DEVICE_PAGE_SIZE),
    )


def get_device(device_id: str) -> RequestSpec[Device]:
    """Build the spec for retrieving one device."""
    return RequestSpec(method="GET", path=f"{_DEVICES}/{device_id}", model=Device)


def update_device(device_id: str, **fields: Any) -> RequestSpec[Device]:
    """Build the spec for updating one device's mutable fields."""
    return RequestSpec(method="PATCH", path=f"{_DEVICES}/{device_id}", json=fields, model=Device)


def delete_device(device_id: str) -> RequestSpec[None]:
    """Build the spec for deleting one device."""
    return RequestSpec(method="DELETE", path=f"{_DEVICES}/{device_id}")


def get_device_details(device_id: str) -> RequestSpec[None]:
    """
    Build the spec for a device's full detail record.

    The API returns a large, loosely-specified document here, so it comes back as a dict rather
    than a model.
    """
    return RequestSpec(method="GET", path=f"{_DEVICES}/{device_id}/details")
