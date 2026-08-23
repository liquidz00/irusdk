# Sync and async

The SDK ships two clients with the same surface. Pick whichever fits your program; you do not need
to learn a different API for the other.

::::{tab-set}

:::{tab-item} Sync

```python
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="...")

for device in client.devices.list(platform="Mac"):
    print(device.device_name)

device = client.devices.get("2cfeb3ac-...")
client.close()
```
:::

:::{tab-item} Async

```python
import asyncio

from irusdk import AsyncIruClient


async def main():
    client = AsyncIruClient(subdomain="mycompany", token="...")

    async for device in client.devices.list(platform="Mac"):
        print(device.device_name)

    device = await client.devices.get("2cfeb3ac-...")
    await client.aclose()


asyncio.run(main())
```
:::

::::

The differences are exactly the ones the language forces: `async for` instead of `for`, `await` on
single-record calls, and `aclose()` instead of `close()`. Method names, arguments, defaults, and
models are identical.

## Which to use

**Use the sync client** unless you already have an event loop. It is the path most Mac admins take,
it is what the CLI drives, and it still fetches pages concurrently through a thread pool — so you
get the throughput benefit without touching asyncio.

**Use the async client** when the SDK is one of several I/O sources in an existing async program:
a FastAPI service, an aiohttp worker, a Discord or Slack bot.

## How they stay in step

Both clients are hand-written rather than generated, so their signatures, docstrings, and return
types are explicit for your IDE and for these docs. Keeping two surfaces aligned by hand is exactly
the sort of thing that drifts, so the test suite enforces it:

- Every scenario in the transport and pagination tests runs against **both** clients from one set
  of response fixtures.
- A parity test walks every `XAPI`/`AsyncXAPI` pair and asserts the method names and signatures
  match, ignoring return annotations and coroutine-ness.

Adding a method to one client without the other fails CI.

## Lifecycle

Neither client requires a context manager — construct it and use it, as you would an `httpx`
client. Both also support one:

```python
with IruClient(subdomain="mycompany", token="...") as client:
    ...

async with AsyncIruClient(subdomain="mycompany", token="...") as client:
    ...
```

Closing is worth doing consistently on the async client, where an unclosed `httpx.AsyncClient` can
warn as the event loop shuts down.
