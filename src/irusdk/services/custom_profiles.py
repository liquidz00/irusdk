"""Custom profile operations."""

from typing import AsyncIterator, Iterator

from .._endpoints import custom_profiles as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.custom_profiles import CustomProfile
from . import copy_doc


class CustomProfilesAPI:
    """
    Custom profile operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> Iterator[CustomProfile]:
        """
        Iterate every custom profile, paginating transparently.

        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[CustomProfile]
        """
        return self._transport.iterate(endpoints.list_custom_profiles(page_size=page_size))

    def get(self, profile_id: str) -> CustomProfile:
        """
        Retrieve one custom profile.

        :param profile_id: The library item's identifier.
        :type profile_id: str
        :rtype: CustomProfile
        """
        return self._transport.send(endpoints.get_custom_profile(profile_id))

    def create(
        self,
        *,
        name: str,
        profile: bytes,
        filename: str | None = None,
        active: bool = False,
        runs_on_mac: bool | None = None,
        runs_on_iphone: bool | None = None,
        runs_on_ipad: bool | None = None,
        runs_on_tv: bool | None = None,
        runs_on_vision: bool | None = None,
    ) -> CustomProfile:
        """
        Create a custom profile.

        The ``.mobileconfig`` is uploaded as a file part, so ``profile`` is its bytes and reading
        it is the caller's business. Iru assigns the new profile's ``id`` and derives its
        ``mdm_identifier`` from that, so read both back from the returned model.

        :param name: The profile's name.
        :type name: str
        :param profile: The ``.mobileconfig`` contents.
        :type profile: bytes
        :param filename: The name to upload under. Defaults to ``<name>.mobileconfig``.
        :type filename: str | None
        :param active: Whether the profile is active.
        :type active: bool
        :param runs_on_mac: Whether the profile targets macOS.
        :type runs_on_mac: bool | None
        :param runs_on_iphone: Whether the profile targets iPhone.
        :type runs_on_iphone: bool | None
        :param runs_on_ipad: Whether the profile targets iPad.
        :type runs_on_ipad: bool | None
        :param runs_on_tv: Whether the profile targets Apple TV.
        :type runs_on_tv: bool | None
        :param runs_on_vision: Whether the profile targets Apple Vision Pro.
        :type runs_on_vision: bool | None
        :raises ValueError: When no platform is enabled.
        :rtype: CustomProfile
        """
        return self._transport.send(
            endpoints.create_custom_profile(
                name=name,
                profile=profile,
                filename=filename,
                active=active,
                runs_on_mac=runs_on_mac,
                runs_on_iphone=runs_on_iphone,
                runs_on_ipad=runs_on_ipad,
                runs_on_tv=runs_on_tv,
                runs_on_vision=runs_on_vision,
            )
        )

    def update(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        profile: bytes | None = None,
        filename: str | None = None,
        active: bool | None = None,
        runs_on_mac: bool | None = None,
        runs_on_iphone: bool | None = None,
        runs_on_ipad: bool | None = None,
        runs_on_tv: bool | None = None,
        runs_on_vision: bool | None = None,
    ) -> CustomProfile:
        """
        Update a custom profile. Only the fields supplied are sent.

        Omitting ``profile`` leaves the deployed ``.mobileconfig`` alone, which is how a rename or
        a platform change is made without reuploading it.

        :param profile_id: The library item's identifier.
        :type profile_id: str
        :param name: A new name.
        :type name: str | None
        :param profile: New ``.mobileconfig`` contents.
        :type profile: bytes | None
        :param filename: The name to upload under. Defaults to ``<name>.mobileconfig``.
        :type filename: str | None
        :param active: Whether the profile is active.
        :type active: bool | None
        :param runs_on_mac: Whether the profile targets macOS.
        :type runs_on_mac: bool | None
        :param runs_on_iphone: Whether the profile targets iPhone.
        :type runs_on_iphone: bool | None
        :param runs_on_ipad: Whether the profile targets iPad.
        :type runs_on_ipad: bool | None
        :param runs_on_tv: Whether the profile targets Apple TV.
        :type runs_on_tv: bool | None
        :param runs_on_vision: Whether the profile targets Apple Vision Pro.
        :type runs_on_vision: bool | None
        :rtype: CustomProfile
        """
        return self._transport.send(
            endpoints.update_custom_profile(
                profile_id,
                name=name,
                profile=profile,
                filename=filename,
                active=active,
                runs_on_mac=runs_on_mac,
                runs_on_iphone=runs_on_iphone,
                runs_on_ipad=runs_on_ipad,
                runs_on_tv=runs_on_tv,
                runs_on_vision=runs_on_vision,
            )
        )

    def delete(self, profile_id: str) -> None:
        """
        Delete a custom profile.

        :param profile_id: The library item's identifier.
        :type profile_id: str
        """
        self._transport.send(endpoints.delete_custom_profile(profile_id))


class AsyncCustomProfilesAPI:
    """
    Custom profile operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(CustomProfilesAPI.list)
    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> AsyncIterator[CustomProfile]:
        return self._transport.iterate(endpoints.list_custom_profiles(page_size=page_size))

    @copy_doc(CustomProfilesAPI.get)
    async def get(self, profile_id: str) -> CustomProfile:
        return await self._transport.send(endpoints.get_custom_profile(profile_id))

    @copy_doc(CustomProfilesAPI.create)
    async def create(
        self,
        *,
        name: str,
        profile: bytes,
        filename: str | None = None,
        active: bool = False,
        runs_on_mac: bool | None = None,
        runs_on_iphone: bool | None = None,
        runs_on_ipad: bool | None = None,
        runs_on_tv: bool | None = None,
        runs_on_vision: bool | None = None,
    ) -> CustomProfile:
        return await self._transport.send(
            endpoints.create_custom_profile(
                name=name,
                profile=profile,
                filename=filename,
                active=active,
                runs_on_mac=runs_on_mac,
                runs_on_iphone=runs_on_iphone,
                runs_on_ipad=runs_on_ipad,
                runs_on_tv=runs_on_tv,
                runs_on_vision=runs_on_vision,
            )
        )

    @copy_doc(CustomProfilesAPI.update)
    async def update(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        profile: bytes | None = None,
        filename: str | None = None,
        active: bool | None = None,
        runs_on_mac: bool | None = None,
        runs_on_iphone: bool | None = None,
        runs_on_ipad: bool | None = None,
        runs_on_tv: bool | None = None,
        runs_on_vision: bool | None = None,
    ) -> CustomProfile:
        return await self._transport.send(
            endpoints.update_custom_profile(
                profile_id,
                name=name,
                profile=profile,
                filename=filename,
                active=active,
                runs_on_mac=runs_on_mac,
                runs_on_iphone=runs_on_iphone,
                runs_on_ipad=runs_on_ipad,
                runs_on_tv=runs_on_tv,
                runs_on_vision=runs_on_vision,
            )
        )

    @copy_doc(CustomProfilesAPI.delete)
    async def delete(self, profile_id: str) -> None:
        await self._transport.send(endpoints.delete_custom_profile(profile_id))
