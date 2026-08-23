"""Blueprint endpoint definitions."""

from typing import Any

from .._core.pagination import OffsetPagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.blueprints import Blueprint
from ..models.library import LibraryItem

DEFAULT_PAGE_SIZE = 100

_BLUEPRINTS = "/api/v1/blueprints"

# The list endpoint returns the standard {count, next, previous, results} envelope.
_ENVELOPE = OffsetPagination(results_key="results", total_key="count")


def list_blueprints(
    *,
    name: str | None = None,
    blueprint_id: str | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> PagedSpec[Blueprint]:
    """Build the spec for the paginated blueprint list."""
    return PagedSpec(
        base=RequestSpec(
            method="GET",
            path=_BLUEPRINTS,
            params=drop_none(name=name, id=blueprint_id),
            model=Blueprint,
        ),
        strategy=_ENVELOPE,
        page_size=page_size,
    )


def get_blueprint(blueprint_id: str) -> RequestSpec[Blueprint]:
    """Build the spec for retrieving one blueprint."""
    return RequestSpec(method="GET", path=f"{_BLUEPRINTS}/{blueprint_id}", model=Blueprint)


def create_blueprint(name: str, **fields: Any) -> RequestSpec[Blueprint]:
    """Build the spec for creating a blueprint."""
    return RequestSpec(
        method="POST", path=_BLUEPRINTS, json={"name": name, **fields}, model=Blueprint
    )


def update_blueprint(blueprint_id: str, **fields: Any) -> RequestSpec[Blueprint]:
    """Build the spec for updating a blueprint."""
    return RequestSpec(
        method="PATCH", path=f"{_BLUEPRINTS}/{blueprint_id}", json=fields, model=Blueprint
    )


def delete_blueprint(blueprint_id: str) -> RequestSpec[None]:
    """Build the spec for deleting a blueprint."""
    return RequestSpec(method="DELETE", path=f"{_BLUEPRINTS}/{blueprint_id}")


def list_blueprint_library_items(blueprint_id: str) -> RequestSpec[LibraryItem]:
    """Build the spec for the library items assigned to a blueprint."""
    return RequestSpec(
        method="GET",
        path=f"{_BLUEPRINTS}/{blueprint_id}/list-library-items",
        model=LibraryItem,
        unwrap="results",
    )


def assign_library_item(blueprint_id: str, library_item_id: str) -> RequestSpec[None]:
    """Build the spec for assigning a library item to a blueprint."""
    return RequestSpec(
        method="POST",
        path=f"{_BLUEPRINTS}/{blueprint_id}/assign-library-item",
        json={"library_item_id": library_item_id},
    )


def list_blueprint_templates(*, page_size: int = DEFAULT_PAGE_SIZE) -> PagedSpec[Blueprint]:
    """Build the spec for the paginated blueprint template list."""
    return PagedSpec(
        base=RequestSpec(method="GET", path=f"{_BLUEPRINTS}/templates/", model=Blueprint),
        strategy=_ENVELOPE,
        page_size=page_size,
    )
