"""Tag operations."""

from typing import AsyncIterator, Iterator

from .._endpoints import tags as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.tags import Tag
from . import copy_doc


class TagsAPI:
    """
    Tag operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self, *, search: str | None = None, page_size: int = endpoints.DEFAULT_PAGE_SIZE
    ) -> Iterator[Tag]:
        """
        Iterate every tag, paginating transparently.

        :param search: Only tags whose name matches this string.
        :type search: str | None
        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[Tag]
        """
        return self._transport.iterate(endpoints.list_tags(search=search, page_size=page_size))

    def create(self, name: str) -> Tag:
        """
        Create a tag.

        :param name: The new tag's name.
        :type name: str
        :rtype: Tag
        """
        return self._transport.send(endpoints.create_tag(name))

    def update(self, tag_id: str, name: str) -> Tag:
        """
        Rename a tag.

        :param tag_id: The tag's identifier.
        :type tag_id: str
        :param name: The new name.
        :type name: str
        :rtype: Tag
        """
        return self._transport.send(endpoints.update_tag(tag_id, name))

    def delete(self, tag_id: str) -> None:
        """
        Delete a tag.

        :param tag_id: The tag's identifier.
        :type tag_id: str
        """
        self._transport.send(endpoints.delete_tag(tag_id))


class AsyncTagsAPI:
    """
    Tag operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(TagsAPI.list)
    def list(
        self, *, search: str | None = None, page_size: int = endpoints.DEFAULT_PAGE_SIZE
    ) -> AsyncIterator[Tag]:
        return self._transport.iterate(endpoints.list_tags(search=search, page_size=page_size))

    @copy_doc(TagsAPI.create)
    async def create(self, name: str) -> Tag:
        return await self._transport.send(endpoints.create_tag(name))

    @copy_doc(TagsAPI.update)
    async def update(self, tag_id: str, name: str) -> Tag:
        return await self._transport.send(endpoints.update_tag(tag_id, name))

    @copy_doc(TagsAPI.delete)
    async def delete(self, tag_id: str) -> None:
        await self._transport.send(endpoints.delete_tag(tag_id))
