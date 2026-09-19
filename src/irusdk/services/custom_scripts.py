"""Custom script operations."""

from typing import AsyncIterator, Iterator

from .._endpoints import custom_scripts as endpoints
from .._transport.async_transport import AsyncTransport
from .._transport.sync_transport import SyncTransport
from ..models.custom_scripts import CustomScript, ExecutionFrequency
from . import copy_doc


class CustomScriptsAPI:
    """
    Custom script operations on a blocking client.

    :param transport: The client's transport.
    :type transport: SyncTransport
    """

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> Iterator[CustomScript]:
        """
        Iterate every custom script, paginating transparently.

        :param page_size: Records per request.
        :type page_size: int
        :rtype: Iterator[CustomScript]
        """
        return self._transport.iterate(endpoints.list_custom_scripts(page_size=page_size))

    def get(self, script_id: str) -> CustomScript:
        """
        Retrieve one custom script.

        :param script_id: The library item's identifier.
        :type script_id: str
        :rtype: CustomScript
        """
        return self._transport.send(endpoints.get_custom_script(script_id))

    def create(
        self,
        *,
        name: str,
        script: str,
        remediation_script: str | None = None,
        active: bool = False,
        execution_frequency: str = ExecutionFrequency.ONCE,
        restart: bool = False,
        show_in_self_service: bool = False,
        self_service_category_id: str | None = None,
        self_service_recommended: bool = False,
    ) -> CustomScript:
        """
        Create a custom script.

        Iru assigns the new script's ``id`` and ignores any identifier sent with the request, so
        read it back from the returned model rather than choosing one.

        :param name: The script's name.
        :type name: str
        :param script: The audit script's contents.
        :type script: str
        :param remediation_script: The remediation script's contents.
        :type remediation_script: str | None
        :param active: Whether the script is active.
        :type active: bool
        :param execution_frequency: One of :class:`~irusdk.models.custom_scripts.ExecutionFrequency`.
        :type execution_frequency: str
        :param restart: Whether the device restarts after the script runs.
        :type restart: bool
        :param show_in_self_service: Whether to offer the script in Self Service.
        :type show_in_self_service: bool
        :param self_service_category_id: Required when ``show_in_self_service`` is true.
        :type self_service_category_id: str | None
        :param self_service_recommended: Whether to feature the script in Self Service.
        :type self_service_recommended: bool
        :raises ValueError: When the Self Service combination is one Iru rejects.
        :rtype: CustomScript
        """
        return self._transport.send(
            endpoints.create_custom_script(
                name=name,
                script=script,
                remediation_script=remediation_script,
                active=active,
                execution_frequency=execution_frequency,
                restart=restart,
                show_in_self_service=show_in_self_service,
                self_service_category_id=self_service_category_id,
                self_service_recommended=self_service_recommended,
            )
        )

    def update(
        self,
        script_id: str,
        *,
        name: str | None = None,
        script: str | None = None,
        remediation_script: str | None = None,
        active: bool | None = None,
        execution_frequency: str | None = None,
        restart: bool | None = None,
        show_in_self_service: bool | None = None,
        self_service_category_id: str | None = None,
        self_service_recommended: bool | None = None,
    ) -> CustomScript:
        """
        Update a custom script. Only the fields supplied are sent.

        :param script_id: The library item's identifier.
        :type script_id: str
        :param name: A new name.
        :type name: str | None
        :param script: New audit script contents.
        :type script: str | None
        :param remediation_script: New remediation script contents.
        :type remediation_script: str | None
        :param active: Whether the script is active.
        :type active: bool | None
        :param execution_frequency: One of :class:`~irusdk.models.custom_scripts.ExecutionFrequency`.
        :type execution_frequency: str | None
        :param restart: Whether the device restarts after the script runs.
        :type restart: bool | None
        :param show_in_self_service: Whether to offer the script in Self Service.
        :type show_in_self_service: bool | None
        :param self_service_category_id: Required when ``show_in_self_service`` is true.
        :type self_service_category_id: str | None
        :param self_service_recommended: Whether to feature the script in Self Service.
        :type self_service_recommended: bool | None
        :raises ValueError: When the Self Service combination is one Iru rejects.
        :rtype: CustomScript
        """
        return self._transport.send(
            endpoints.update_custom_script(
                script_id,
                name=name,
                script=script,
                remediation_script=remediation_script,
                active=active,
                execution_frequency=execution_frequency,
                restart=restart,
                show_in_self_service=show_in_self_service,
                self_service_category_id=self_service_category_id,
                self_service_recommended=self_service_recommended,
            )
        )

    def delete(self, script_id: str) -> None:
        """
        Delete a custom script.

        :param script_id: The library item's identifier.
        :type script_id: str
        """
        self._transport.send(endpoints.delete_custom_script(script_id))


class AsyncCustomScriptsAPI:
    """
    Custom script operations on an asyncio client.

    :param transport: The client's transport.
    :type transport: AsyncTransport
    """

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    @copy_doc(CustomScriptsAPI.list)
    def list(self, *, page_size: int = endpoints.DEFAULT_PAGE_SIZE) -> AsyncIterator[CustomScript]:
        return self._transport.iterate(endpoints.list_custom_scripts(page_size=page_size))

    @copy_doc(CustomScriptsAPI.get)
    async def get(self, script_id: str) -> CustomScript:
        return await self._transport.send(endpoints.get_custom_script(script_id))

    @copy_doc(CustomScriptsAPI.create)
    async def create(
        self,
        *,
        name: str,
        script: str,
        remediation_script: str | None = None,
        active: bool = False,
        execution_frequency: str = ExecutionFrequency.ONCE,
        restart: bool = False,
        show_in_self_service: bool = False,
        self_service_category_id: str | None = None,
        self_service_recommended: bool = False,
    ) -> CustomScript:
        return await self._transport.send(
            endpoints.create_custom_script(
                name=name,
                script=script,
                remediation_script=remediation_script,
                active=active,
                execution_frequency=execution_frequency,
                restart=restart,
                show_in_self_service=show_in_self_service,
                self_service_category_id=self_service_category_id,
                self_service_recommended=self_service_recommended,
            )
        )

    @copy_doc(CustomScriptsAPI.update)
    async def update(
        self,
        script_id: str,
        *,
        name: str | None = None,
        script: str | None = None,
        remediation_script: str | None = None,
        active: bool | None = None,
        execution_frequency: str | None = None,
        restart: bool | None = None,
        show_in_self_service: bool | None = None,
        self_service_category_id: str | None = None,
        self_service_recommended: bool | None = None,
    ) -> CustomScript:
        return await self._transport.send(
            endpoints.update_custom_script(
                script_id,
                name=name,
                script=script,
                remediation_script=remediation_script,
                active=active,
                execution_frequency=execution_frequency,
                restart=restart,
                show_in_self_service=show_in_self_service,
                self_service_category_id=self_service_category_id,
                self_service_recommended=self_service_recommended,
            )
        )

    @copy_doc(CustomScriptsAPI.delete)
    async def delete(self, script_id: str) -> None:
        await self._transport.send(endpoints.delete_custom_script(script_id))
