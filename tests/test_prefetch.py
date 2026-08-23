"""Concurrent page prefetch, exercised against both transports.

The device list is a bare array with no total, so it can only ever be walked serially. These
tests drive the transports with a synthetic envelope endpoint to cover the planned, concurrent
path that a real ``{count, next, previous, results}`` endpoint takes.
"""

import asyncio
import time

import httpx
import pytest
import respx

from conftest import BASE_URL, SUBDOMAIN, TOKEN, IruConfig
from irusdk import AsyncIruClient, IruClient
from irusdk._core.pagination import OffsetPagination
from irusdk._core.spec import PagedSpec, RequestSpec
from irusdk.models.devices import Device

WIDGETS_URL = f"{BASE_URL}/api/v1/widgets"
TOTAL = 25
PAGE_SIZE = 5


def _envelope(request: httpx.Request) -> httpx.Response:
    offset = int(request.url.params.get("offset", 0))
    limit = int(request.url.params.get("limit", PAGE_SIZE))
    records = [{"device_id": f"device-{i:04d}"} for i in range(offset, min(offset + limit, TOTAL))]
    return httpx.Response(
        200, json={"count": TOTAL, "next": None, "previous": None, "results": records}
    )


def _spec() -> PagedSpec[Device]:
    return PagedSpec(
        base=RequestSpec(method="GET", path="/api/v1/widgets", model=Device),
        strategy=OffsetPagination(results_key="results", total_key="count"),
        page_size=PAGE_SIZE,
    )


@pytest.fixture(params=["sync", "async"])
def transport(request: pytest.FixtureRequest, config: IruConfig):
    """The raw transport from each client, plus a uniform way to drain its pages."""
    if request.param == "sync":
        client = IruClient(SUBDOMAIN, TOKEN, config=config)
        yield client._transport, lambda gen: list(gen)
        client.close()
    else:
        client = AsyncIruClient(SUBDOMAIN, TOKEN, config=config)
        yield client._transport, lambda gen: asyncio.run(_drain(gen))
        asyncio.run(client.aclose())


async def _drain(gen):
    return [page async for page in gen]


@respx.mock
def test_prefetches_planned_pages_in_order(transport) -> None:
    tp, drain = transport
    respx.get(WIDGETS_URL).mock(side_effect=_envelope)

    pages = drain(tp.pages(_spec(), prefetch=3))

    assert [p.index for p in pages] == [0, 1, 2, 3, 4]
    assert [len(p) for p in pages] == [5, 5, 5, 5, 5]
    assert all(p.total == TOTAL for p in pages)

    ids = [d.device_id for page in pages for d in page.items]
    assert ids == [f"device-{i:04d}" for i in range(TOTAL)]


@respx.mock
def test_plans_exactly_the_remaining_pages(transport) -> None:
    tp, drain = transport
    route = respx.get(WIDGETS_URL).mock(side_effect=_envelope)

    drain(tp.pages(_spec(), prefetch=10))

    # One request per page and no more: the total tells us where to stop.
    assert route.call_count == 5


@respx.mock
def test_a_single_page_result_needs_no_prefetch(transport) -> None:
    tp, drain = transport
    route = respx.get(WIDGETS_URL).mock(
        return_value=httpx.Response(
            200,
            json={"count": 2, "next": None, "results": [{"device_id": "a"}, {"device_id": "b"}]},
        )
    )

    pages = drain(tp.pages(_spec()))

    assert len(pages) == 1
    assert route.call_count == 1


@respx.mock
def test_prefetch_respects_the_rate_limiter(transport) -> None:
    tp, drain = transport
    respx.get(WIDGETS_URL).mock(side_effect=_envelope)

    # 20 requests/sec means the 5 pages cannot complete faster than ~0.2s.
    tp._limiter.__init__(per_second=20, per_hour=1_000_000, now=time.monotonic())
    started = time.monotonic()
    drain(tp.pages(_spec(), prefetch=10))

    assert time.monotonic() - started >= 0.15
