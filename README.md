# irusdk

A Python SDK and thin CLI for **querying and acting on an [Iru](https://www.iru.com) (formerly
Kandji) fleet** — devices, their state, the actions you take against them, and the blueprints,
users, and tags that organise them.

> [!NOTE]
> Kandji is now Iru. The API still serves from `*.api.kandji.io`, and this SDK follows suit.

> [!IMPORTANT]
> `irusdk` does not author library content. To version-control Custom Profiles, Scripts, and Apps,
> use [`iructl`](https://github.com/kandji-inc/iructl) — Iru's own tool, which does that job well.
> The two compose: `iructl` manages what you deploy, `irusdk` tells you what your fleet is doing.
> See [Scope](#scope) below.

## Features

- **Sync and async clients** — `IruClient` and `AsyncIruClient`, same surface, same models.
- **Pydantic models** for API responses, so you get real attributes and IDE autocomplete.
- **Transparent pagination** — list methods iterate every page for you, with concurrent prefetch
  where the API exposes a total.
- **Rate-limit aware** — honors Iru's 50 req/sec and 10,000 req/hour tenant limits, with
  `Retry-After` backoff on 429.
- **Optional CLI** for ad-hoc terminal use.

## Installation

```console
pip install irusdk          # library only
pip install irusdk[cli]     # library plus the `irusdk` command
```

## Quickstart

```python
from irusdk import IruClient

client = IruClient(subdomain="mycompany", token="...")

for device in client.devices.list(platform="Mac"):
    print(device.device_name, device.serial_number, device.os_version)
```

No `with` block is required — construct the client and use it, the way you would `httpx.Client`.
Call `client.close()` when you are finished to release the connection pool promptly, or use the
client as a context manager and let it close itself:

```python
with IruClient(subdomain="mycompany", token="...") as client:
    device = client.devices.get("2cfeb3ac-3b5d-423e-bcff-e2676a3a32da")
```

The async client is the same code plus `async`:

```python
import asyncio

from irusdk import AsyncIruClient


async def main():
    client = AsyncIruClient(subdomain="mycompany", token="...")
    async for device in client.devices.list(platform="Mac"):
        print(device.device_name, device.serial_number)
    await client.aclose()


asyncio.run(main())
```

### What's covered

| Attribute | Endpoints |
| --- | --- |
| `client.devices` | list, pages, get, update, delete, details |
| `client.blueprints` | list, pages, get, create, update, delete, library items, templates |
| `client.users` | list, get, delete |
| `client.tags` | list, create, update, delete |

### Pagination

List methods paginate for you — `client.devices.list()` walks every page and yields `Device`
models. When you want page boundaries, the reported total, or control over how many pages are in
flight, use `pages()` instead:

```python
for page in client.devices.pages(platform="Mac", prefetch=8):
    print(f"page {page.index}: {len(page)} devices of {page.total}")
```

## CLI

```console
export IRU_SUBDOMAIN=mycompany
export IRU_API_TOKEN=...

irusdk devices list --platform Mac
irusdk devices get <device-id>
irusdk blueprints list
irusdk users list --limit 50
irusdk tags create "lab-machines"
```

Every read command takes `--json`.

## Scope

`irusdk` covers the **fleet** surface of the Iru API. It deliberately leaves library-content
authoring to [`iructl`](https://github.com/kandji-inc/iructl).

The two problems are different, and the vendor already solves one of them well. Authoring library
content is a content-lifecycle problem — payloads in git, reviewed in PRs, synced to your tenant,
packages uploaded through presigned S3 URLs. That is what `iructl` is built for. Managing a fleet is
a query-and-act problem — which Macs are on an old OS, which are missing, what is installed where,
lock the one that just walked out the door. That is what this is built for.

There is also a durability argument: `iructl` is maintained by Iru, so when the API changes for
Custom Apps, the people who changed it ship the fix. Anywhere the vendor ships a supported tool,
that tool should win.

| Task | Tool |
| --- | --- |
| Version-control Custom Profiles, Scripts, Apps | `iructl` |
| Upload a Custom App package | `iructl` |
| Declaratively assign library items to blueprints | `iructl` |
| Find every Mac on an outdated OS | `irusdk` |
| Report FileVault or compliance state across the fleet | `irusdk` |
| Lock, erase, or restart a device | `irusdk` |
| Build a dashboard, Slack bot, or scheduled report | `irusdk` |

Blueprints appear in both, for different reasons: `iructl` assigns content *to* them, while
`irusdk` reads them as fleet context, since every device carries a `blueprint_id`.

## Documentation

Full documentation lives at [irusdk.readthedocs.io](https://irusdk.readthedocs.io).

## License

Apache-2.0. See [LICENSE](LICENSE).
