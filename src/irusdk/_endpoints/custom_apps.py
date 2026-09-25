"""Custom app endpoint definitions.

Read-only for now. Creating or updating an app means uploading an installer, which goes
through a presigned POST to object storage rather than this API, and is a larger piece of
surface than the rest of this package put together.
"""

from .._core.pagination import PagePagination
from .._core.spec import PagedSpec, RequestSpec
from ..models.custom_apps import CustomApp

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
