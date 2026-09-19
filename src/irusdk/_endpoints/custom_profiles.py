"""Custom profile endpoint definitions.

Unlike every other endpoint here, create and update send multipart rather than JSON: the
``.mobileconfig`` goes up as a file part. The payload is taken as ``bytes`` rather than a path
because ``_endpoints`` performs no I/O — the caller reads the file.
"""

from typing import Any

from .._core.pagination import PagePagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.custom_profiles import CustomProfile

DEFAULT_PAGE_SIZE = 100

_CUSTOM_PROFILES = "/api/v1/library/custom-profiles"

# The list endpoint returns {count, next, previous, results} and walks by `page`.
_ENVELOPE = PagePagination(results_key="results", total_key="count")


def _file_part(profile: bytes, filename: str) -> dict[str, Any]:
    """Build the multipart file part carrying the ``.mobileconfig``."""
    return {"file": (filename, profile, "application/octet-stream")}


def _runs_on(
    *,
    runs_on_mac: bool | None,
    runs_on_iphone: bool | None,
    runs_on_ipad: bool | None,
    runs_on_tv: bool | None,
    runs_on_vision: bool | None,
    require_one: bool,
) -> dict[str, Any]:
    """
    Collect the platform flags that were set.

    :param require_one: Whether to reject the call when no platform is enabled. Iru refuses a
        profile that targets nothing, which matters on create and not on a partial update.
    :raises ValueError: When ``require_one`` is set and no platform is enabled.
    :rtype: dict[str, Any]
    """
    flags = drop_none(
        runs_on_mac=runs_on_mac,
        runs_on_iphone=runs_on_iphone,
        runs_on_ipad=runs_on_ipad,
        runs_on_tv=runs_on_tv,
        runs_on_vision=runs_on_vision,
    )
    if require_one and not any(flags.values()):
        raise ValueError("a custom profile must target at least one platform")
    return flags


def list_custom_profiles(*, page_size: int = DEFAULT_PAGE_SIZE) -> PagedSpec[CustomProfile]:
    """Build the spec for the paginated custom profile list."""
    return PagedSpec(
        base=RequestSpec(method="GET", path=_CUSTOM_PROFILES, model=CustomProfile),
        strategy=_ENVELOPE,
        page_size=page_size,
    )


def get_custom_profile(profile_id: str) -> RequestSpec[CustomProfile]:
    """Build the spec for retrieving one custom profile."""
    return RequestSpec(method="GET", path=f"{_CUSTOM_PROFILES}/{profile_id}", model=CustomProfile)


def create_custom_profile(
    *,
    name: str,
    profile: bytes,
    filename: str | None = None,
    active: bool = False,
    runs_on_mac: bool | None = None,
    runs_on_iphone: bool | None = None,
    runs_on_ipad: bool | None = None,
    runs_on_tv: bool | None = None,
    runs_on_vision: bool | None = None,
) -> RequestSpec[CustomProfile]:
    """Build the spec for creating a custom profile."""
    data: dict[str, Any] = {
        "name": name,
        "active": active,
        **_runs_on(
            runs_on_mac=runs_on_mac,
            runs_on_iphone=runs_on_iphone,
            runs_on_ipad=runs_on_ipad,
            runs_on_tv=runs_on_tv,
            runs_on_vision=runs_on_vision,
            require_one=True,
        ),
    }
    return RequestSpec(
        method="POST",
        path=_CUSTOM_PROFILES,
        data=data,
        files=_file_part(profile, filename or f"{name}.mobileconfig"),
        model=CustomProfile,
    )


def update_custom_profile(
    profile_id: str,
    *,
    name: str | None = None,
    profile: bytes | None = None,
    filename: str | None = None,
    active: bool | None = None,
    runs_on_mac: bool | None = None,
    runs_on_iphone: bool | None = None,
    runs_on_ipad: bool | None = None,
    runs_on_tv: bool | None = None,
    runs_on_vision: bool | None = None,
) -> RequestSpec[CustomProfile]:
    """
    Build the spec for updating a custom profile.

    Only the fields supplied are sent. Omitting ``profile`` leaves the deployed ``.mobileconfig``
    alone, which is how a rename or a platform change is made without reuploading it.
    """
    data = drop_none(name=name, active=active)
    data.update(
        _runs_on(
            runs_on_mac=runs_on_mac,
            runs_on_iphone=runs_on_iphone,
            runs_on_ipad=runs_on_ipad,
            runs_on_tv=runs_on_tv,
            runs_on_vision=runs_on_vision,
            require_one=False,
        )
    )
    files = None
    if profile is not None:
        files = _file_part(profile, filename or f"{name or profile_id}.mobileconfig")
    return RequestSpec(
        method="PATCH",
        path=f"{_CUSTOM_PROFILES}/{profile_id}",
        data=data,
        files=files,
        model=CustomProfile,
    )


def delete_custom_profile(profile_id: str) -> RequestSpec[None]:
    """Build the spec for deleting a custom profile."""
    return RequestSpec(method="DELETE", path=f"{_CUSTOM_PROFILES}/{profile_id}")
