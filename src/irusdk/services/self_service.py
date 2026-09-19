"""Self Service operations."""

from typing import Sequence

from .._endpoints import self_service as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.self_service import SelfServiceCategory
from . import copy_doc


class SelfServiceAPI:
    """
    Self Service operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def categories(self) -> Sequence[SelfServiceCategory]:
        """
        List every Self Service category in the tenant.

        A custom script offered in Self Service must name one of these by ``id``, so this is
        how you resolve a category name to the value
        :meth:`~irusdk.services.custom_scripts.CustomScriptsAPI.create` expects.

        :rtype: Sequence[SelfServiceCategory]
        """
        return self._transport.send(endpoints.list_self_service_categories())


class AsyncSelfServiceAPI:
    """
    Self Service operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(SelfServiceAPI.categories)
    async def categories(self) -> Sequence[SelfServiceCategory]:
        return await self._transport.send(endpoints.list_self_service_categories())
