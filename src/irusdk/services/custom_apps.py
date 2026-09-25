"""Custom app operations."""

from typing import AsyncIterator, Iterator

from .._endpoints import custom_apps as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.custom_apps import CustomApp
from . import copy_doc


class CustomAppsAPI:
    """
    Custom app operations on a blocking client.

    Read-only: see :mod:`irusdk._endpoints.custom_apps` for why creating an app is not here.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> Iterator[CustomApp]:
        """
        Iterate every custom app, paginating transparently.

        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[CustomApp]
        """
        return self._transport.iterate(endpoints.list_custom_apps(page_size=page_size))

    def get(self, app_id: str) -> CustomApp:
        """
        Retrieve one custom app.

        :param app_id: The library item's identifier.
        :type app_id: str
        :rtype: CustomApp
        """
        return self._transport.send(endpoints.get_custom_app(app_id))


class AsyncCustomAppsAPI:
    """
    Custom app operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(CustomAppsAPI.list)
    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> AsyncIterator[CustomApp]:
        return self._transport.iterate(endpoints.list_custom_apps(page_size=page_size))

    @copy_doc(CustomAppsAPI.get)
    async def get(self, app_id: str) -> CustomApp:
        return await self._transport.send(endpoints.get_custom_app(app_id))
