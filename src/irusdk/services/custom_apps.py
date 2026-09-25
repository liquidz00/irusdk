"""Custom app operations."""

from pathlib import Path
from typing import Any, AsyncIterator, Iterator

import httpx

from .._core.errors import PayloadTransferError
from .._endpoints import custom_apps as endpoints
from .._transport._common import build_verify
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.custom_apps import CustomApp, CustomAppUpload
from . import copy_doc

# The store answers a successful presigned POST with an empty 204.
_UPLOAD_SUCCESS = 204

_OCTET_STREAM = "application/octet-stream"

# The client default governs an API call, not a multi-hundred-megabyte body. `write=None`
# lets a slow link finish rather than failing an upload most of the way through.
_UPLOAD_TIMEOUT = httpx.Timeout(connect=30.0, read=300.0, write=None, pool=30.0)


def _storage_kwargs(transport: SyncTransport | AsyncTransport) -> dict[str, Any]:
    """Build a bare client for the object store, carrying no Iru credentials.

    The presigned policy authenticates the upload by itself. Sending the tenant token to a
    host that is not the tenant would hand it to a third party for nothing.
    """
    return {
        "timeout": _UPLOAD_TIMEOUT,
        "verify": build_verify(transport.config),
        # Not followed: the body is a consumed file stream, so a replay would send nothing.
        "follow_redirects": False,
    }


def _upload_parts(reservation: CustomAppUpload, file: Path, stream: Any) -> dict[str, Any]:
    """Assemble the multipart body for a presigned POST.

    The policy fields must precede the file part or the store rejects the upload; httpx emits
    `data` before `files`, which is what makes this correct.
    """
    return {
        "data": reservation.post_data,
        "files": {"file": (file.name, stream, _OCTET_STREAM)},
    }


def _transferred(reservation: CustomAppUpload, response: httpx.Response) -> str:
    """Return the stored object's key, or raise with what the store said."""
    if response.status_code != _UPLOAD_SUCCESS:
        raise PayloadTransferError(
            f"Object storage rejected the installer (HTTP {response.status_code}): {response.text}"
        )
    if not reservation.file_key:
        raise PayloadTransferError("The upload reservation carried no file_key")
    return reservation.file_key


class CustomAppsAPI:
    """
    Custom app operations on a blocking client.

    Writing an app is three steps; :meth:`upload` explains the one that leaves the tenant.

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

    def upload(self, file: Path, *, name: str | None = None) -> str:
        """
        Send an installer to object storage and return the key identifying it.

        The bytes never pass through the Iru API. This reserves a presigned POST, streams the
        file straight to the store, and hands back the ``file_key`` that :meth:`create` and
        :meth:`update` take. Iru appends a token to the stored name, so the same binary
        uploaded twice is two objects with two keys.

        :param file: The installer on disk.
        :type file: Path
        :param name: The filename to register, when it should differ from the file's own.
        :type name: str | None
        :raises PayloadTransferError: When the store refuses or the reservation is unusable.
        :rtype: str
        """
        reservation = self._transport.send(endpoints.request_upload(name or file.name))
        with httpx.Client(**_storage_kwargs(self._transport)) as storage, file.open("rb") as body:
            response = storage.post(
                reservation.post_url or "", **_upload_parts(reservation, file, body)
            )
        return _transferred(reservation, response)

    def create(self, **fields: Any) -> CustomApp:
        """
        Create a custom app around an installer already in object storage.

        Takes the keywords of :func:`~irusdk._endpoints.custom_apps.create_custom_app`, of which
        ``name`` and ``file_key`` are required; pass :meth:`upload`'s result as ``file_key``.

        :raises ValueError: When the field combination is one Iru rejects.
        :rtype: CustomApp
        """
        return self._transport.send(endpoints.create_custom_app(**fields))

    def update(self, app_id: str, **fields: Any) -> CustomApp:
        """
        Update a custom app. Only the fields supplied are sent.

        Pass ``file_key`` from :meth:`upload` to point the app at a new installer; omit it to
        change metadata alone.

        :param app_id: The library item's identifier.
        :type app_id: str
        :raises ValueError: When the field combination is one Iru rejects.
        :rtype: CustomApp
        """
        return self._transport.send(endpoints.update_custom_app(app_id, **fields))


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

    @copy_doc(CustomAppsAPI.upload)
    async def upload(self, file: Path, *, name: str | None = None) -> str:
        reservation = await self._transport.send(endpoints.request_upload(name or file.name))
        async with httpx.AsyncClient(**_storage_kwargs(self._transport)) as storage:
            with file.open("rb") as body:
                response = await storage.post(
                    reservation.post_url or "", **_upload_parts(reservation, file, body)
                )
        return _transferred(reservation, response)

    @copy_doc(CustomAppsAPI.create)
    async def create(self, **fields: Any) -> CustomApp:
        return await self._transport.send(endpoints.create_custom_app(**fields))

    @copy_doc(CustomAppsAPI.update)
    async def update(self, app_id: str, **fields: Any) -> CustomApp:
        return await self._transport.send(endpoints.update_custom_app(app_id, **fields))
