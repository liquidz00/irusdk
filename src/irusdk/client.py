"""The blocking and asyncio clients.

Both live here, adjacent, so a change to one makes the missing change to the other obvious in
review.
"""

from ._core.config import IruConfig
from ._core.errors import ConfigurationError
from ._core.urls import Region, resolve_base_url
from ._transport.async_transport import AsyncTransport
from ._transport.sync_transport import SyncTransport
from .services.blueprints import AsyncBlueprintsAPI, BlueprintsAPI
from .services.custom_profiles import AsyncCustomProfilesAPI, CustomProfilesAPI
from .services.custom_scripts import AsyncCustomScriptsAPI, CustomScriptsAPI
from .services.devices import AsyncDevicesAPI, DevicesAPI
from .services.self_service import AsyncSelfServiceAPI, SelfServiceAPI
from .services.tags import AsyncTagsAPI, TagsAPI
from .services.users import AsyncUsersAPI, UsersAPI


class IruClient:
    """
    A blocking client for the Iru Endpoint Management API.

    Usable directly, with no ``with`` block required::

        client = IruClient(subdomain="mycompany", token="...")
        for device in client.devices.list():
            print(device.device_name)

    It is also a context manager, which closes the connection pool on exit::

        with IruClient(subdomain="mycompany", token="...") as client:
            ...

    When used directly, call :meth:`close` when finished to release the pool promptly. Skipping it
    is harmless in a short-lived script — the pool is reclaimed at interpreter exit — but matters
    in a long-running process that creates many clients.

    :param subdomain: The tenant subdomain, or the full API URL from Settings > Access.
    :type subdomain: str
    :param token: The tenant API token.
    :type token: str
    :param region: The tenant region. Ignored when ``subdomain`` is a full URL.
    :type region: Region | str
    :param config: Transport tuning. Defaults to :class:`~irusdk.IruConfig`.
    :type config: IruConfig | None
    :raises ConfigurationError: If the subdomain or token is missing or unusable.

    :ivar devices: Device operations.
    :ivar blueprints: Blueprint operations.
    :ivar users: User operations.
    :ivar tags: Tag operations.
    :ivar custom_scripts: Custom script operations.
    :ivar custom_profiles: Custom profile operations.
    :ivar self_service: Self Service operations.
    """

    def __init__(
        self,
        subdomain: str,
        token: str,
        *,
        region: Region | str = Region.US,
        config: IruConfig | None = None,
    ) -> None:
        if not token or not token.strip():
            raise ConfigurationError("An API token is required")

        self.config = config or IruConfig()
        self.base_url = resolve_base_url(subdomain, region)
        self._transport = SyncTransport(self.base_url, token.strip(), self.config)

        self.devices = DevicesAPI(self._transport)
        self.blueprints = BlueprintsAPI(self._transport)
        self.users = UsersAPI(self._transport)
        self.tags = TagsAPI(self._transport)
        self.custom_scripts = CustomScriptsAPI(self._transport)
        self.custom_profiles = CustomProfilesAPI(self._transport)
        self.self_service = SelfServiceAPI(self._transport)

    def close(self) -> None:
        """Release the underlying connection pool. Idempotent, and optional."""
        self._transport.close()

    def __enter__(self) -> "IruClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={self.base_url!r})"


class AsyncIruClient:
    """
    An asyncio client for the Iru Endpoint Management API.

    Usable directly, with no ``async with`` block required::

        client = AsyncIruClient(subdomain="mycompany", token="...")
        async for device in client.devices.list():
            print(device.device_name)
        await client.aclose()

    It is also an async context manager, which closes the connection pool on exit::

        async with AsyncIruClient(subdomain="mycompany", token="...") as client:
            ...

    When used directly, call :meth:`aclose` when finished. Unlike the blocking client this is
    worth doing consistently, since an unclosed ``httpx.AsyncClient`` can emit warnings when the
    event loop shuts down.

    :param subdomain: The tenant subdomain, or the full API URL from Settings > Access.
    :type subdomain: str
    :param token: The tenant API token.
    :type token: str
    :param region: The tenant region. Ignored when ``subdomain`` is a full URL.
    :type region: Region | str
    :param config: Transport tuning. Defaults to :class:`~irusdk.IruConfig`.
    :type config: IruConfig | None
    :raises ConfigurationError: If the subdomain or token is missing or unusable.

    :ivar devices: Device operations.
    :ivar blueprints: Blueprint operations.
    :ivar users: User operations.
    :ivar tags: Tag operations.
    :ivar custom_scripts: Custom script operations.
    :ivar custom_profiles: Custom profile operations.
    :ivar self_service: Self Service operations.
    """

    def __init__(
        self,
        subdomain: str,
        token: str,
        *,
        region: Region | str = Region.US,
        config: IruConfig | None = None,
    ) -> None:
        if not token or not token.strip():
            raise ConfigurationError("An API token is required")

        self.config = config or IruConfig()
        self.base_url = resolve_base_url(subdomain, region)
        self._transport = AsyncTransport(self.base_url, token.strip(), self.config)

        self.devices = AsyncDevicesAPI(self._transport)
        self.blueprints = AsyncBlueprintsAPI(self._transport)
        self.users = AsyncUsersAPI(self._transport)
        self.tags = AsyncTagsAPI(self._transport)
        self.custom_scripts = AsyncCustomScriptsAPI(self._transport)
        self.custom_profiles = AsyncCustomProfilesAPI(self._transport)
        self.self_service = AsyncSelfServiceAPI(self._transport)

    async def aclose(self) -> None:
        """Release the underlying connection pool. Idempotent, and optional."""
        await self._transport.aclose()

    async def __aenter__(self) -> "AsyncIruClient":
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={self.base_url!r})"
