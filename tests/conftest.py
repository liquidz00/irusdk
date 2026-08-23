"""Shared fixtures.

The transport tests run every scenario against both clients from one set of response fixtures, so
a sync/async divergence fails the build rather than hiding in the untested twin.
"""

import asyncio
from typing import Any

import pytest

from irusdk import AsyncIruClient, IruClient, IruConfig

SUBDOMAIN = "accuhive"
TOKEN = "test-token"
BASE_URL = f"https://{SUBDOMAIN}.api.kandji.io"


@pytest.fixture
def config() -> IruConfig:
    """Config tuned for tests: no throttling delay, no retry sleeps."""
    return IruConfig(
        requests_per_second=100_000,
        requests_per_hour=1_000_000,
        max_retries=2,
        backoff_factor=0.001,
        max_backoff=0.01,
    )


@pytest.fixture
def sync_client(config: IruConfig) -> IruClient:
    client = IruClient(SUBDOMAIN, TOKEN, config=config)
    yield client
    client.close()


@pytest.fixture
def async_client(config: IruConfig) -> AsyncIruClient:
    client = AsyncIruClient(SUBDOMAIN, TOKEN, config=config)
    yield client
    asyncio.run(client.aclose())


class ClientAdapter:
    """
    Drives either client through one synchronous interface.

    Lets a single test body cover both, which is the point: a 429 test that only runs against one
    transport is not a test.
    """

    def __init__(self, client: Any, is_async: bool) -> None:
        self.client = client
        self.is_async = is_async

    def call(self, method: Any, *args: Any, **kwargs: Any) -> Any:
        """Invoke a service method, awaiting it when the client is asynchronous."""
        result = method(*args, **kwargs)
        if self.is_async:
            return asyncio.run(_await(result))
        return result

    def collect(self, method: Any, *args: Any, **kwargs: Any) -> list[Any]:
        """Invoke an iterating service method and drain it into a list."""
        result = method(*args, **kwargs)
        if self.is_async:
            return asyncio.run(_drain(result))
        return list(result)


async def _await(value: Any) -> Any:
    return await value


async def _drain(iterator: Any) -> list[Any]:
    return [item async for item in iterator]


@pytest.fixture(params=["sync", "async"])
def any_client(request: pytest.FixtureRequest, config: IruConfig) -> ClientAdapter:
    """Parametrized over both clients, so each test body runs twice."""
    if request.param == "sync":
        client = IruClient(SUBDOMAIN, TOKEN, config=config)
        yield ClientAdapter(client, is_async=False)
        client.close()
    else:
        client = AsyncIruClient(SUBDOMAIN, TOKEN, config=config)
        yield ClientAdapter(client, is_async=True)
        asyncio.run(client.aclose())


def device_payload(index: int) -> dict[str, Any]:
    """A device record shaped like the API's own example."""
    return {
        "device_id": f"device-{index:04d}",
        "device_name": f"Test Mac {index}",
        "model": "MacBook Air (M1, 2020)",
        "serial_number": f"SERIAL{index:04d}",
        "platform": "Mac",
        "os_version": "14.4.1",
        "last_check_in": "2024-07-23T14:11:37.150080Z",
        "user": {
            "email": "admin@accuhive.io",
            "name": "Admin",
            "id": "5344c996-8823-4b37-8d6e-8515fc7c3a0a",
            "is_archived": False,
        },
        "blueprint_id": "ab102b9d-8e9c-420d-a498-f2a1123091c7",
        "blueprint_name": "main hive",
        "mdm_enabled": True,
        "agent_installed": True,
        "is_missing": False,
        "is_removed": False,
        "tags": ["accuhive_02"],
    }
