"""Device operations."""

from typing import Any, AsyncIterator, Iterator

from .._core.pagination import Page
from .._endpoints import devices as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.devices import Device
from . import copy_doc


class DevicesAPI:
    """
    Device operations on a blocking client.

    Reached through :attr:`~irusdk.client.IruClient.devices` rather than constructed directly.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        *,
        blueprint_id: str | None = None,
        device_name: str | None = None,
        filevault_enabled: bool | None = None,
        mac_address: str | None = None,
        model: str | None = None,
        os_version: str | None = None,
        ordering: str | None = None,
        platform: str | None = None,
        serial_number: str | None = None,
        tag_id: str | None = None,
        tag_name: str | None = None,
        user_email: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        page_size: int = endpoints.MAX_DEVICE_PAGE_SIZE,
    ) -> Iterator[Device]:
        """
        Iterate every device matching the given filters, paginating transparently.

        :param blueprint_id: Only devices assigned to this blueprint.
        :type blueprint_id: str | None
        :param device_name: Devices whose name contains this string.
        :type device_name: str | None
        :param filevault_enabled: Only macOS devices with FileVault on or off.
        :type filevault_enabled: bool | None
        :param mac_address: The exact MAC address to search for.
        :type mac_address: str | None
        :param model: Devices whose model contains this string.
        :type model: str | None
        :param os_version: Devices whose OS version contains this string.
        :type os_version: str | None
        :param ordering: Sort field, optionally prefixed with ``-`` to reverse, and comma-separated
            for multiple fields — for example ``"-serial_number"`` or ``"serial_number,platform"``.
        :type ordering: str | None
        :param platform: ``Mac``, ``iPad``, ``iPhone``, ``AppleTV``, ``Android``, or ``Windows``.
        :type platform: str | None
        :param serial_number: The serial number to search for.
        :type serial_number: str | None
        :param tag_id: Only devices carrying this tag id.
        :type tag_id: str | None
        :param tag_name: Only devices carrying this tag name.
        :type tag_name: str | None
        :param user_email: Devices assigned to a user with this email.
        :type user_email: str | None
        :param user_id: Devices assigned to this user id.
        :type user_id: str | None
        :param user_name: Devices assigned to a user with this name.
        :type user_name: str | None
        :param page_size: Records per request, capped at 300 by the API.
        :type page_size: int
        :return: The matching devices.
        :rtype: Iterator[Device]
        """
        return self._transport.iterate(endpoints.list_devices(**_filters(locals())))

    def pages(
        self,
        *,
        prefetch: int | None = None,
        page_size: int = endpoints.MAX_DEVICE_PAGE_SIZE,
        **filters: Any,
    ) -> Iterator[Page[Device]]:
        """
        Iterate the device list one page at a time.

        The escape hatch from :meth:`list` for callers that want page boundaries, the reported
        total, or control over how many pages are in flight.

        :param prefetch: Pages fetched at once. Defaults to the client's ``max_concurrency``.
        :type prefetch: int | None
        :param page_size: Records per request, capped at 300 by the API.
        :type page_size: int
        :param filters: Any filter accepted by :meth:`list`.
        :rtype: Iterator[Page[Device]]
        """
        spec = endpoints.list_devices(page_size=page_size, **filters)
        return self._transport.pages(spec, prefetch=prefetch)

    def get(self, device_id: str) -> Device:
        """
        Retrieve a single device.

        :param device_id: The device's identifier.
        :type device_id: str
        :rtype: Device
        :raises NotFoundError: If no device has that identifier.
        """
        return self._transport.send(endpoints.get_device(device_id))

    def update(self, device_id: str, **fields: Any) -> Device:
        """
        Update a device's mutable fields.

        :param device_id: The device's identifier.
        :type device_id: str
        :param fields: Fields to set, such as ``blueprint_id`` or ``asset_tag``.
        :rtype: Device
        """
        return self._transport.send(endpoints.update_device(device_id, **fields))

    def delete(self, device_id: str) -> None:
        """
        Delete a device record.

        :param device_id: The device's identifier.
        :type device_id: str
        """
        self._transport.send(endpoints.delete_device(device_id))

    def details(self, device_id: str) -> dict[str, Any]:
        """
        Retrieve a device's full detail record.

        Returned as a dict rather than a model: the API's detail document is large and its shape
        varies by platform and agent version.

        :param device_id: The device's identifier.
        :type device_id: str
        :rtype: dict[str, Any]
        """
        return self._transport.send(endpoints.get_device_details(device_id))


class AsyncDevicesAPI:
    """
    Device operations on an asyncio client.

    Reached through :attr:`~irusdk.client.AsyncIruClient.devices` rather than constructed
    directly.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(DevicesAPI.list)
    def list(
        self,
        *,
        blueprint_id: str | None = None,
        device_name: str | None = None,
        filevault_enabled: bool | None = None,
        mac_address: str | None = None,
        model: str | None = None,
        os_version: str | None = None,
        ordering: str | None = None,
        platform: str | None = None,
        serial_number: str | None = None,
        tag_id: str | None = None,
        tag_name: str | None = None,
        user_email: str | None = None,
        user_id: str | None = None,
        user_name: str | None = None,
        page_size: int = endpoints.MAX_DEVICE_PAGE_SIZE,
    ) -> AsyncIterator[Device]:
        # Deliberately not `async def`: returning the async iterator directly keeps the call site
        # `async for d in client.devices.list()` rather than requiring an extra await.
        return self._transport.iterate(endpoints.list_devices(**_filters(locals())))

    @copy_doc(DevicesAPI.pages)
    def pages(
        self,
        *,
        prefetch: int | None = None,
        page_size: int = endpoints.MAX_DEVICE_PAGE_SIZE,
        **filters: Any,
    ) -> AsyncIterator[Page[Device]]:
        spec = endpoints.list_devices(page_size=page_size, **filters)
        return self._transport.pages(spec, prefetch=prefetch)

    @copy_doc(DevicesAPI.get)
    async def get(self, device_id: str) -> Device:
        return await self._transport.send(endpoints.get_device(device_id))

    @copy_doc(DevicesAPI.update)
    async def update(self, device_id: str, **fields: Any) -> Device:
        return await self._transport.send(endpoints.update_device(device_id, **fields))

    @copy_doc(DevicesAPI.delete)
    async def delete(self, device_id: str) -> None:
        await self._transport.send(endpoints.delete_device(device_id))

    @copy_doc(DevicesAPI.details)
    async def details(self, device_id: str) -> dict[str, Any]:
        return await self._transport.send(endpoints.get_device_details(device_id))


def _filters(scope: dict[str, Any]) -> dict[str, Any]:
    """Strip ``self`` out of a captured ``locals()`` so it can be forwarded to an endpoint."""
    return {k: v for k, v in scope.items() if k != "self"}
