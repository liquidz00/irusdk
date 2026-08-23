"""End-to-end pagination, exercised against both clients."""

import httpx
import pytest
import respx

from conftest import BASE_URL, ClientAdapter, device_payload
from irusdk import PaginationError

DEVICES_URL = f"{BASE_URL}/api/v1/devices"


def _page(request: httpx.Request, total: int, page_size: int) -> httpx.Response:
    """Serve a slice of a synthetic device list as a bare JSON array."""
    offset = int(request.url.params.get("offset", 0))
    limit = int(request.url.params.get("limit", page_size))
    records = [device_payload(i) for i in range(offset, min(offset + limit, total))]
    return httpx.Response(200, json=records)


@respx.mock
def test_walks_every_page(any_client: ClientAdapter) -> None:
    respx.get(DEVICES_URL).mock(side_effect=lambda r: _page(r, total=250, page_size=100))

    devices = any_client.collect(any_client.client.devices.list, page_size=100)

    assert len(devices) == 250
    assert devices[0].device_id == "device-0000"
    assert devices[-1].device_id == "device-0249"


@respx.mock
def test_stops_on_an_exact_multiple_of_the_page_size(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICES_URL).mock(side_effect=lambda r: _page(r, total=200, page_size=100))

    devices = any_client.collect(any_client.client.devices.list, page_size=100)

    assert len(devices) == 200
    # Two full pages, then one empty page to learn the sequence ended.
    assert route.call_count == 3


@respx.mock
def test_handles_an_empty_result_set(any_client: ClientAdapter) -> None:
    respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[]))

    assert any_client.collect(any_client.client.devices.list) == []


@respx.mock
def test_forwards_filters_as_query_parameters(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[]))

    any_client.collect(any_client.client.devices.list, platform="Mac", blueprint_id="bp-1")

    params = route.calls.last.request.url.params
    assert params["platform"] == "Mac"
    assert params["blueprint_id"] == "bp-1"
    assert params["limit"] == "300"


@respx.mock
def test_caps_page_size_at_the_api_maximum(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[]))

    any_client.collect(any_client.client.devices.list, page_size=5000)

    assert route.calls.last.request.url.params["limit"] == "300"


@respx.mock
def test_pages_expose_index_and_boundaries(any_client: ClientAdapter) -> None:
    respx.get(DEVICES_URL).mock(side_effect=lambda r: _page(r, total=250, page_size=100))

    pages = any_client.collect(any_client.client.devices.pages, page_size=100)

    assert [p.index for p in pages] == [0, 1, 2]
    assert [len(p) for p in pages] == [100, 100, 50]


@respx.mock
def test_detects_an_endpoint_that_ignores_its_offset(any_client: ClientAdapter) -> None:
    # Always returns the same full page, which a naive loop would follow forever.
    respx.get(DEVICES_URL).mock(
        return_value=httpx.Response(200, json=[device_payload(i) for i in range(10)])
    )

    with pytest.raises(PaginationError, match="ignoring its offset"):
        any_client.collect(any_client.client.devices.list, page_size=10)
