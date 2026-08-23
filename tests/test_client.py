"""Client construction, lifecycle, and the raw escape hatch."""

import asyncio

import httpx
import pytest
import respx

from conftest import BASE_URL, SUBDOMAIN, TOKEN, ClientAdapter, IruConfig, device_payload
from irusdk import AsyncIruClient, IruClient

DEVICE_URL = f"{BASE_URL}/api/v1/devices/device-0001"


def test_sync_client_works_without_a_context_manager(config: IruConfig) -> None:
    client = IruClient(SUBDOMAIN, TOKEN, config=config)

    with respx.mock:
        respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=device_payload(1)))
        assert client.devices.get("device-0001").device_id == "device-0001"

    client.close()


def test_async_client_works_without_a_context_manager(config: IruConfig) -> None:
    client = AsyncIruClient(SUBDOMAIN, TOKEN, config=config)

    async def run() -> str:
        with respx.mock:
            respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=device_payload(1)))
            device = await client.devices.get("device-0001")
        await client.aclose()
        return device.device_id

    assert asyncio.run(run()) == "device-0001"


def test_sync_context_manager_closes_the_pool(config: IruConfig) -> None:
    with IruClient(SUBDOMAIN, TOKEN, config=config) as client:
        assert client.base_url == BASE_URL
    assert client._transport._client.is_closed


def test_async_context_manager_closes_the_pool(config: IruConfig) -> None:
    async def run() -> bool:
        async with AsyncIruClient(SUBDOMAIN, TOKEN, config=config) as client:
            assert client.base_url == BASE_URL
        return client._transport._client.is_closed

    assert asyncio.run(run())


def test_close_is_idempotent(config: IruConfig) -> None:
    client = IruClient(SUBDOMAIN, TOKEN, config=config)
    client.close()
    client.close()


def test_repr_shows_the_base_url(config: IruConfig) -> None:
    client = IruClient(SUBDOMAIN, TOKEN, config=config)

    assert repr(client) == f"IruClient(base_url='{BASE_URL}')"

    client.close()


def test_token_is_stripped_before_use(config: IruConfig) -> None:
    client = IruClient(SUBDOMAIN, f"  {TOKEN}  ", config=config)

    with respx.mock:
        route = respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=device_payload(1)))
        client.devices.get("device-0001")

    assert route.calls.last.request.headers["Authorization"] == f"Bearer {TOKEN}"

    client.close()


@respx.mock
def test_details_returns_the_raw_document(any_client: ClientAdapter) -> None:
    document = {"general": {"device_name": "Test Mac 1"}, "hardware_overview": {"chip": "M1"}}
    respx.get(f"{DEVICE_URL}/details").mock(return_value=httpx.Response(200, json=document))

    assert any_client.call(any_client.client.devices.details, "device-0001") == document


@respx.mock
def test_send_raw_returns_the_httpx_response(any_client: ClientAdapter) -> None:
    respx.get(f"{BASE_URL}/api/v1/settings/licensing").mock(
        return_value=httpx.Response(200, json={"seats": 500})
    )

    transport = any_client.client._transport
    response = any_client.call(transport.send_raw, "GET", "/api/v1/settings/licensing")

    assert isinstance(response, httpx.Response)
    assert response.json() == {"seats": 500}


@pytest.mark.parametrize("subdomain", ["accuhive", "https://accuhive.api.kandji.io"])
def test_accepts_a_subdomain_or_a_full_url(subdomain: str, config: IruConfig) -> None:
    client = IruClient(subdomain, TOKEN, config=config)

    assert client.base_url == BASE_URL

    client.close()
