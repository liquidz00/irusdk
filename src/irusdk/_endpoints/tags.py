"""Tag endpoint definitions."""

from .._core.pagination import CursorPagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.tags import Tag

DEFAULT_PAGE_SIZE = 100

_TAGS = "/api/v1/tags"


def list_tags(*, search: str | None = None, page_size: int = DEFAULT_PAGE_SIZE) -> PagedSpec[Tag]:
    """
    Build the spec for the tag list.

    The endpoint returns a ``next`` URL but documents no page-size parameter, so pages are walked
    by following the server's own link rather than a parameter it may ignore.
    """
    return PagedSpec(
        base=RequestSpec(method="GET", path=_TAGS, params=drop_none(search=search), model=Tag),
        strategy=CursorPagination(size_param=None),
        page_size=page_size,
    )


def create_tag(name: str) -> RequestSpec[Tag]:
    """Build the spec for creating a tag."""
    return RequestSpec(method="POST", path=_TAGS, json={"name": name}, model=Tag)


def update_tag(tag_id: str, name: str) -> RequestSpec[Tag]:
    """Build the spec for renaming a tag."""
    return RequestSpec(method="PATCH", path=f"{_TAGS}/{tag_id}", json={"name": name}, model=Tag)


def delete_tag(tag_id: str) -> RequestSpec[None]:
    """Build the spec for deleting a tag."""
    return RequestSpec(method="DELETE", path=f"{_TAGS}/{tag_id}")
