"""Custom app endpoint definitions.

Writing an app is two calls to this API with a third, to object storage, in between: ask for
a presigned POST, send the bytes there, then hand the resulting ``file_key`` back on a create
or update. The middle step is the one thing here that does not go to the tenant, and it must
not carry the tenant's token -- see the service layer.
"""

from typing import Any

from .._core.pagination import PagePagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.custom_apps import CustomApp, CustomAppUpload, InstallEnforcement, InstallType

DEFAULT_PAGE_SIZE = 100

_CUSTOM_APPS = "/api/v1/library/custom-apps"

# The list endpoint returns {count, next, previous, results} and walks by `page`.
_ENVELOPE = PagePagination(results_key="results", total_key="count")


def list_custom_apps(*, page_size: int = DEFAULT_PAGE_SIZE) -> PagedSpec[CustomApp]:
    """Build the spec for the paginated custom app list."""
    return PagedSpec(
        base=RequestSpec(method="GET", path=_CUSTOM_APPS, model=CustomApp),
        strategy=_ENVELOPE,
        page_size=page_size,
    )


def get_custom_app(app_id: str) -> RequestSpec[CustomApp]:
    """Build the spec for retrieving one custom app."""
    return RequestSpec(method="GET", path=f"{_CUSTOM_APPS}/{app_id}", model=CustomApp)


def _validated(
    *,
    install_type: str | None,
    install_enforcement: str | None,
    unzip_location: str | None,
    audit_script: str | None,
    show_in_self_service: bool | None,
    self_service_category_id: str | None,
    self_service_recommended: bool | None,
) -> dict[str, Any]:
    """
    Check the combinations Iru rejects, and build the Self Service half of the payload.

    Each of these comes back as a 400 with a message that does not always name the field, so
    they are caught here instead.

    :raises ValueError: When a constraint is violated.
    :rtype: dict[str, Any]
    """
    # Each check is skipped when the field governing it was not supplied. On a partial update
    # that means Iru still holds the old value, and guessing it here rejects valid calls.
    if install_enforcement is not None:
        if audit_script and install_enforcement != InstallEnforcement.CONTINUOUSLY_ENFORCE:
            raise ValueError("audit_script requires install_enforcement 'continuously_enforce'")
        if install_enforcement == InstallEnforcement.NO_ENFORCEMENT and not show_in_self_service:
            raise ValueError(
                "install_enforcement 'no_enforcement' requires show_in_self_service=True"
            )
    if install_type == InstallType.ZIP and unzip_location is None:
        raise ValueError("install_type 'zip' requires unzip_location")
    if not show_in_self_service:
        return {}
    if self_service_category_id is None:
        raise ValueError("show_in_self_service=True requires self_service_category_id")
    return drop_none(
        self_service_category_id=self_service_category_id,
        self_service_recommended=self_service_recommended,
    )


def request_upload(name: str) -> RequestSpec[CustomAppUpload]:
    """Build the spec for reserving a presigned POST for an installer named ``name``."""
    return RequestSpec(
        method="POST",
        path=f"{_CUSTOM_APPS}/upload",
        json={"name": name},
        model=CustomAppUpload,
    )


def create_custom_app(
    *,
    name: str,
    file_key: str,
    install_type: str = InstallType.PACKAGE,
    install_enforcement: str = InstallEnforcement.CONTINUOUSLY_ENFORCE,
    audit_script: str | None = None,
    preinstall_script: str | None = None,
    postinstall_script: str | None = None,
    restart: bool = False,
    active: bool = False,
    unzip_location: str | None = None,
    show_in_self_service: bool = False,
    self_service_category_id: str | None = None,
    self_service_recommended: bool | None = None,
) -> RequestSpec[CustomApp]:
    """Build the spec for creating a custom app around an already-uploaded ``file_key``."""
    payload: dict[str, Any] = {
        "name": name,
        "file_key": file_key,
        "install_type": str(install_type),
        "install_enforcement": str(install_enforcement),
        "audit_script": audit_script or "",
        "preinstall_script": preinstall_script or "",
        "postinstall_script": postinstall_script or "",
        "restart": restart,
        "active": active,
        "show_in_self_service": show_in_self_service,
        **_validated(
            install_type=install_type,
            install_enforcement=install_enforcement,
            unzip_location=unzip_location,
            audit_script=audit_script,
            show_in_self_service=show_in_self_service,
            self_service_category_id=self_service_category_id,
            self_service_recommended=self_service_recommended,
        ),
    }
    if unzip_location is not None:
        payload["unzip_location"] = unzip_location
    return RequestSpec(method="POST", path=_CUSTOM_APPS, json=payload, model=CustomApp)


def update_custom_app(
    app_id: str,
    *,
    name: str | None = None,
    file_key: str | None = None,
    install_type: str | None = None,
    install_enforcement: str | None = None,
    audit_script: str | None = None,
    preinstall_script: str | None = None,
    postinstall_script: str | None = None,
    restart: bool | None = None,
    active: bool | None = None,
    unzip_location: str | None = None,
    show_in_self_service: bool | None = None,
    self_service_category_id: str | None = None,
    self_service_recommended: bool | None = None,
) -> RequestSpec[CustomApp]:
    """Build the spec for updating a custom app. Only the fields supplied are sent.

    A blank script is a value, not an absence: passing ``""`` clears that slot, and leaving it
    ``None`` keeps whatever Iru holds.
    """
    payload = drop_none(
        name=name,
        file_key=file_key,
        install_type=None if install_type is None else str(install_type),
        install_enforcement=None if install_enforcement is None else str(install_enforcement),
        audit_script=audit_script,
        preinstall_script=preinstall_script,
        postinstall_script=postinstall_script,
        restart=restart,
        active=active,
        unzip_location=unzip_location,
        show_in_self_service=show_in_self_service,
    )
    payload.update(
        _validated(
            install_type=install_type,
            install_enforcement=install_enforcement,
            unzip_location=unzip_location,
            audit_script=audit_script,
            show_in_self_service=show_in_self_service,
            self_service_category_id=self_service_category_id,
            self_service_recommended=self_service_recommended,
        )
    )
    return RequestSpec(
        method="PATCH", path=f"{_CUSTOM_APPS}/{app_id}", json=payload, model=CustomApp
    )
