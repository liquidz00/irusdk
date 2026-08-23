"""User operations."""

from typing import AsyncIterator, Iterator

from .._endpoints import users as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.users import User
from . import copy_doc


class UsersAPI:
    """
    User operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        *,
        email: str | None = None,
        user_id: str | None = None,
        integration_id: str | None = None,
        archived: bool | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
    ) -> Iterator[User]:
        """
        Iterate every user, paginating transparently.

        This endpoint is cursor-paginated, so pages are fetched one at a time rather than
        concurrently.

        :param email: Only the user with this email address.
        :type email: str | None
        :param user_id: Only the user with this identifier.
        :type user_id: str | None
        :param integration_id: Only users sourced from this directory integration.
        :type integration_id: str | None
        :param archived: Whether to return archived users.
        :type archived: bool | None
        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[User]
        """
        return self._transport.iterate(
            endpoints.list_users(
                email=email,
                user_id=user_id,
                integration_id=integration_id,
                archived=archived,
                page_size=page_size,
            )
        )

    def get(self, user_id: str) -> User:
        """
        Retrieve a single user.

        :param user_id: The user's identifier.
        :type user_id: str
        :rtype: User
        """
        return self._transport.send(endpoints.get_user(user_id))

    def delete(self, user_id: str) -> None:
        """
        Delete a user.

        :param user_id: The user's identifier.
        :type user_id: str
        """
        self._transport.send(endpoints.delete_user(user_id))


class AsyncUsersAPI:
    """
    User operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(UsersAPI.list)
    def list(
        self,
        *,
        email: str | None = None,
        user_id: str | None = None,
        integration_id: str | None = None,
        archived: bool | None = None,
        page_size: int = endpoints.DEFAULT_PAGE_SIZE,
    ) -> AsyncIterator[User]:
        return self._transport.iterate(
            endpoints.list_users(
                email=email,
                user_id=user_id,
                integration_id=integration_id,
                archived=archived,
                page_size=page_size,
            )
        )

    @copy_doc(UsersAPI.get)
    async def get(self, user_id: str) -> User:
        return await self._transport.send(endpoints.get_user(user_id))

    @copy_doc(UsersAPI.delete)
    async def delete(self, user_id: str) -> None:
        await self._transport.send(endpoints.delete_user(user_id))
