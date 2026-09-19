"""Custom script endpoint definitions."""

from typing import Any

from .._core.pagination import PagePagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.custom_scripts import CustomScript, ExecutionFrequency

DEFAULT_PAGE_SIZE = 100

_CUSTOM_SCRIPTS = "/api/v1/library/custom-scripts"

# The list endpoint returns {count, next, previous, results} and walks by `page`.
_ENVELOPE = PagePagination(results_key="results", total_key="count")


def _self_service(
    *,
    execution_frequency: str | None,
    show_in_self_service: bool | None,
    self_service_category_id: str | None,
    self_service_recommended: bool | None,
) -> dict[str, Any]:
    """
    Validate the Self Service combination and build its half of the payload.

    Iru rejects ``no_enforcement`` unless the script is offered in Self Service, and rejects a
    Self Service script with no category. Both are caught here rather than as a 400.

    :raises ValueError: When either constraint is violated.
    :rtype: dict[str, Any]
    """
    if execution_frequency == ExecutionFrequency.NO_ENFORCEMENT and not show_in_self_service:
        raise ValueError("execution_frequency 'no_enforcement' requires show_in_self_service=True")
    if not show_in_self_service:
        return {}
    if self_service_category_id is None:
        raise ValueError("show_in_self_service=True requires self_service_category_id")
    return drop_none(
        self_service_category_id=self_service_category_id,
        self_service_recommended=self_service_recommended,
    )


def list_custom_scripts(*, page_size: int = DEFAULT_PAGE_SIZE) -> PagedSpec[CustomScript]:
    """Build the spec for the paginated custom script list."""
    return PagedSpec(
        base=RequestSpec(method="GET", path=_CUSTOM_SCRIPTS, model=CustomScript),
        strategy=_ENVELOPE,
        page_size=page_size,
    )


def get_custom_script(script_id: str) -> RequestSpec[CustomScript]:
    """Build the spec for retrieving one custom script."""
    return RequestSpec(method="GET", path=f"{_CUSTOM_SCRIPTS}/{script_id}", model=CustomScript)


def create_custom_script(
    *,
    name: str,
    script: str,
    remediation_script: str | None = None,
    active: bool = False,
    execution_frequency: str = ExecutionFrequency.ONCE,
    restart: bool = False,
    show_in_self_service: bool = False,
    self_service_category_id: str | None = None,
    self_service_recommended: bool = False,
) -> RequestSpec[CustomScript]:
    """Build the spec for creating a custom script."""
    payload: dict[str, Any] = {
        "name": name,
        "script": script,
        "active": active,
        "execution_frequency": str(execution_frequency),
        "restart": restart,
        "show_in_self_service": show_in_self_service,
        **_self_service(
            execution_frequency=execution_frequency,
            show_in_self_service=show_in_self_service,
            self_service_category_id=self_service_category_id,
            self_service_recommended=self_service_recommended,
        ),
    }
    if remediation_script is not None:
        payload["remediation_script"] = remediation_script
    return RequestSpec(method="POST", path=_CUSTOM_SCRIPTS, json=payload, model=CustomScript)


def update_custom_script(
    script_id: str,
    *,
    name: str | None = None,
    script: str | None = None,
    remediation_script: str | None = None,
    active: bool | None = None,
    execution_frequency: str | None = None,
    restart: bool | None = None,
    show_in_self_service: bool | None = None,
    self_service_category_id: str | None = None,
    self_service_recommended: bool | None = None,
) -> RequestSpec[CustomScript]:
    """Build the spec for updating a custom script. Only the fields supplied are sent."""
    payload = drop_none(
        name=name,
        script=script,
        remediation_script=remediation_script,
        active=active,
        execution_frequency=None if execution_frequency is None else str(execution_frequency),
        restart=restart,
        show_in_self_service=show_in_self_service,
    )
    payload.update(
        _self_service(
            execution_frequency=execution_frequency,
            show_in_self_service=show_in_self_service,
            self_service_category_id=self_service_category_id,
            self_service_recommended=self_service_recommended,
        )
    )
    return RequestSpec(
        method="PATCH",
        path=f"{_CUSTOM_SCRIPTS}/{script_id}",
        json=payload,
        model=CustomScript,
    )


def delete_custom_script(script_id: str) -> RequestSpec[None]:
    """Build the spec for deleting a custom script."""
    return RequestSpec(method="DELETE", path=f"{_CUSTOM_SCRIPTS}/{script_id}")
