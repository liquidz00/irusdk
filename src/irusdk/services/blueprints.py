"""Blueprint operations."""

from typing import Any, AsyncIterator, Iterator, Sequence

from .._core.pagination import Page
from .._endpoints import blueprints as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.blueprints import Blueprint
from ..models.library import LibraryItem
from . import copy_doc


class BlueprintsAPI:
    """
    Blueprint operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        *,
        name: str | None = None,
        blueprint_id: str | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
    ) -> Iterator[Blueprint]:
        """
        Iterate every blueprint, paginating transparently.

        :param name: Only blueprints whose name matches.
        :type name: str | None
        :param blueprint_id: Only the blueprint with this identifier.
        :type blueprint_id: str | None
        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[Blueprint]
        """
        return self._transport.iterate(
            endpoints.list_blueprints(name=name, blueprint_id=blueprint_id, page_size=page_size)
        )

    def pages(
        self,
        *,
        prefetch: int | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
        **filters: Any,
    ) -> Iterator[Page[Blueprint]]:
        """
        Iterate the blueprint list one page at a time.

        This endpoint reports a total, so pages after the first are fetched concurrently.

        :param prefetch: Pages fetched at once. Defaults to the client's ``max_concurrency``.
        :type prefetch: int | None
        :param page_size: Records per request.
        :type page_size: int
        :param filters: Any filter accepted by :meth:`list`.
        :rtype: Iterator[Page[Blueprint]]
        """
        spec = endpoints.list_blueprints(page_size=page_size, **filters)
        return self._transport.pages(spec, prefetch=prefetch)

    def get(self, blueprint_id: str) -> Blueprint:
        """
        Retrieve a single blueprint.

        :param blueprint_id: The blueprint's identifier.
        :type blueprint_id: str
        :rtype: Blueprint
        """
        return self._transport.send(endpoints.get_blueprint(blueprint_id))

    def create(self, name: str, **fields: Any) -> Blueprint:
        """
        Create a blueprint.

        :param name: The new blueprint's name.
        :type name: str
        :param fields: Any other writable field, such as ``description`` or ``icon``.
        :rtype: Blueprint
        """
        return self._transport.send(endpoints.create_blueprint(name, **fields))

    def update(self, blueprint_id: str, **fields: Any) -> Blueprint:
        """
        Update a blueprint's mutable fields.

        :param blueprint_id: The blueprint's identifier.
        :type blueprint_id: str
        :param fields: Fields to set.
        :rtype: Blueprint
        """
        return self._transport.send(endpoints.update_blueprint(blueprint_id, **fields))

    def delete(self, blueprint_id: str) -> None:
        """
        Delete a blueprint.

        :param blueprint_id: The blueprint's identifier.
        :type blueprint_id: str
        """
        self._transport.send(endpoints.delete_blueprint(blueprint_id))

    def library_items(self, blueprint_id: str) -> Sequence[LibraryItem]:
        """
        List the library items assigned to a blueprint.

        :param blueprint_id: The blueprint's identifier.
        :type blueprint_id: str
        :rtype: Sequence[LibraryItem]

        .. note::
            Annotated as a ``Sequence`` rather than a ``list`` on purpose: this class defines a
            method named ``list``, which shadows the builtin inside the class body and would make
            a ``list[...]`` annotation resolve to that method.
        """
        return self._transport.send(endpoints.list_blueprint_library_items(blueprint_id))

    def assign_library_item(self, blueprint_id: str, library_item_id: str) -> None:
        """
        Assign a library item to a blueprint.

        :param blueprint_id: The blueprint's identifier.
        :type blueprint_id: str
        :param library_item_id: The library item's identifier.
        :type library_item_id: str
        """
        self._transport.send(endpoints.assign_library_item(blueprint_id, library_item_id))

    def templates(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> Iterator[Blueprint]:
        """
        Iterate the blueprint templates available to the tenant.

        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[Blueprint]
        """
        return self._transport.iterate(endpoints.list_blueprint_templates(page_size=page_size))


class AsyncBlueprintsAPI:
    """
    Blueprint operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(BlueprintsAPI.list)
    def list(
        self,
        *,
        name: str | None = None,
        blueprint_id: str | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
    ) -> AsyncIterator[Blueprint]:
        return self._transport.iterate(
            endpoints.list_blueprints(name=name, blueprint_id=blueprint_id, page_size=page_size)
        )

    @copy_doc(BlueprintsAPI.pages)
    def pages(
        self,
        *,
        prefetch: int | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
        **filters: Any,
    ) -> AsyncIterator[Page[Blueprint]]:
        spec = endpoints.list_blueprints(page_size=page_size, **filters)
        return self._transport.pages(spec, prefetch=prefetch)

    @copy_doc(BlueprintsAPI.get)
    async def get(self, blueprint_id: str) -> Blueprint:
        return await self._transport.send(endpoints.get_blueprint(blueprint_id))

    @copy_doc(BlueprintsAPI.create)
    async def create(self, name: str, **fields: Any) -> Blueprint:
        return await self._transport.send(endpoints.create_blueprint(name, **fields))

    @copy_doc(BlueprintsAPI.update)
    async def update(self, blueprint_id: str, **fields: Any) -> Blueprint:
        return await self._transport.send(endpoints.update_blueprint(blueprint_id, **fields))

    @copy_doc(BlueprintsAPI.delete)
    async def delete(self, blueprint_id: str) -> None:
        await self._transport.send(endpoints.delete_blueprint(blueprint_id))

    @copy_doc(BlueprintsAPI.library_items)
    async def library_items(self, blueprint_id: str) -> Sequence[LibraryItem]:
        return await self._transport.send(endpoints.list_blueprint_library_items(blueprint_id))

    @copy_doc(BlueprintsAPI.assign_library_item)
    async def assign_library_item(self, blueprint_id: str, library_item_id: str) -> None:
        await self._transport.send(endpoints.assign_library_item(blueprint_id, library_item_id))

    @copy_doc(BlueprintsAPI.templates)
    def templates(
        self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE
    ) -> AsyncIterator[Blueprint]:
        return self._transport.iterate(endpoints.list_blueprint_templates(page_size=page_size))
