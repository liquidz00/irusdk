"""User endpoint definitions."""

from .._core.pagination import CursorPagination
from .._core.spec import PagedSpec, RequestSpec, drop_none
from ..models.users import User

DEFAULT_PAGE_SIZE = 100

_USERS = "/api/v1/users"


def list_users(
    *,
    email: str | None = None,
    user_id: str | None = None,
    integration_id: str | None = None,
    archived: bool | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> PagedSpec[User]:
    """
    Build the spec for the paginated user list.

    Unlike most list endpoints this one is cursor-based, and its page-size parameter is
    ``sizePerPage`` rather than ``limit``.
    """
    return PagedSpec(
        base=RequestSpec(
            method="GET",
            path=_USERS,
            params=drop_none(
                email=email, id=user_id, integration_id=integration_id, archived=archived
            ),
            model=User,
        ),
        strategy=CursorPagination(size_param="sizePerPage"),
        page_size=page_size,
    )


def get_user(user_id: str) -> RequestSpec[User]:
    """Build the spec for retrieving one user."""
    return RequestSpec(method="GET", path=f"{_USERS}/{user_id}", model=User)


def delete_user(user_id: str) -> RequestSpec[None]:
    """Build the spec for deleting a user."""
    return RequestSpec(method="DELETE", path=f"{_USERS}/{user_id}")
