# Pagination

List methods paginate for you. `client.devices.list()` walks every page and yields
{class}`~irusdk.models.devices.Device` models, so you never write an offset loop:

```python
for device in client.devices.list(platform="Mac"):
    ...
```

Because it is a generator, nothing is fetched until you iterate, and only one page is held in
memory at a time. To materialise everything, wrap it:

```python
devices = list(client.devices.list())
```

To stop early, slice it — the remaining pages are never requested:

```python
import itertools

first_ten = list(itertools.islice(client.devices.list(), 10))
```

## Taking control with `pages()`

Where volume warrants it — devices and blueprints — a `pages()` method exposes the page boundaries,
the reported total, and how many pages are fetched at once:

```python
for page in client.devices.pages(platform="Mac", prefetch=8):
    print(f"page {page.index}: {len(page)} of {page.total}")
    for device in page:
        ...
```

Each {class}`~irusdk.Page` carries its zero-based `index`, its `items`, and the `total` the API
reported (or `None` where it reports none).

## Why the styles differ

The Iru API does not page consistently, so the SDK carries one strategy per shape and picks the
right one per endpoint. This matters because it determines whether pages can be fetched
concurrently.

The table below describes the whole API, including endpoints this SDK does not wrap — see
{doc}`scope`.

| Envelope | Parameters | Endpoints | Concurrent |
| --- | --- | --- | --- |
| bare JSON array | `limit`/`offset` | `/devices` | No — no total to plan from |
| `{count, next, previous, results}` | `limit`/`offset` | blueprints, library activity | Yes |
| `{count, next, previous, results}` | `page` | ADE devices, library collections | Yes |
| `{offset, limit, total, cursor, data}` | `limit`/`offset` | all `/prism/*` | Yes |
| `{total, page, size, results}` | `page`/`size` | vulnerability management | Yes |
| `{next, previous, results}` | `cursor` | users, admins, audit events | No — cursors are serial |

Where the API reports a total, the SDK fetches the first page, computes every remaining page's
coordinates, and requests them concurrently in bounded batches. Where it does not — the device list
and the cursor endpoints — pages are walked one at a time, because there is no way to know where
page three starts until page two has arrived.

:::{note}
Concurrency is bounded by `IruConfig.max_concurrency` and gated by the same rate limiter as every
other request, so prefetch can never breach the tenant quota.
:::

## Safety valves

Endpoints that report no total end only when they return a short page. Two guards stop a
misbehaving endpoint from looping forever:

- `IruConfig.max_pages` (default `10_000`) caps the pages walked in one sequence.
- If two consecutive pages start with the same record, the SDK raises
  {class}`~irusdk.PaginationError` — the signature of a server ignoring its `offset`.
