"""Self Service endpoint definitions."""

from .._core.spec import RequestSpec
from ..models.self_service import SelfServiceCategory

_CATEGORIES = "/api/v1/self-service/categories"


def list_self_service_categories() -> RequestSpec[SelfServiceCategory]:
    """
    Build the spec for the Self Service category list.

    The endpoint returns a bare JSON array with no envelope and takes no pagination
    parameters, so this is a plain request rather than a :class:`~irusdk._core.spec.PagedSpec`.
    """
    return RequestSpec(method="GET", path=_CATEGORIES, model=SelfServiceCategory)
