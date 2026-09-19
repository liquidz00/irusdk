# irusdk

A Python SDK and thin CLI for **querying and acting on an [Iru](https://www.iru.com) (formerly
Kandji) fleet** — devices, their state, the actions you take against them, and the blueprints,
users, and tags that organise them.

> [!NOTE]
> Kandji is now Iru. The API still serves from `*.api.kandji.io`, and this SDK follows suit.

> [!IMPORTANT]
> Library authoring arrived in 0.2.0 and is landing one resource at a time — Custom Scripts,
> Custom Profiles and Self Service categories today, Custom Apps next. Until then
> [`iructl`](https://github.com/kandji-inc/iructl) still covers what this SDK does not, and the two
> compose. See [Scope](#scope) below.

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

`irusdk` covers the Iru API: the **fleet** surface — devices, actions, Prism, users, tags,
blueprints — and, from 0.2.0, **library-content authoring**.

| Library item | Authoring support |
| --- | --- |
| Custom Scripts | available |
| Custom Profiles | available |
| Self Service categories | available (read-only; Iru exposes no write) |
| Custom Apps | planned |
| In-House Apps | not planned |

Earlier releases left authoring to [`iructl`](https://github.com/kandji-inc/iructl) on the
reasoning that content authoring and fleet querying are different problems. The querying half of
that still holds. The authoring half rested on the assumption that the hard part of authoring is
talking to the API — and it is not. The hard part is the repository side: what a component looks
like on disk, which fields a human owns and which the vendor assigns, how a pull reconciles with a
working tree. Those are decisions a repository has to make for itself.

So the seam moved. `irusdk` owns the API and has no opinion about your filesystem; your own tooling
owns the repository.

The durability argument against this is real and is worth keeping visible: `iructl` is maintained
by Iru, so when the API changes, the people who changed it ship the fix. Adopting authoring here
means accepting on-call for that drift. If you do not need repository-side control, `iructl` is
still the shorter path.

| Task | Tool |
| --- | --- |
| Upload a Custom App package | `iructl` |
| Declaratively assign library items to blueprints | `iructl` |
| Read or author Custom Scripts and Profiles | `irusdk` |
| Find every Mac on an outdated OS | `irusdk` |
| Report FileVault or compliance state across the fleet | `irusdk` |
| Lock, erase, or restart a device | `irusdk` |
| Build a dashboard, Slack bot, or scheduled report | `irusdk` |


## Documentation

Full documentation lives at [irusdk.readthedocs.io](https://irusdk.readthedocs.io).

## License

Apache-2.0. See [LICENSE](LICENSE).
