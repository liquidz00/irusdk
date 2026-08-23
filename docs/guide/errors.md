# Errors and retries

Every exception the SDK raises descends from {class}`~irusdk.IruError`, so one `except` clause
catches anything it can throw:

```python
from irusdk import IruError, NotFoundError

try:
    device = client.devices.get(device_id)
except NotFoundError:
    device = None
except IruError as exc:
    logger.error("Iru request failed: %s", exc)
    raise
```

## The hierarchy

```text
IruError
├── ConfigurationError      bad subdomain, missing token
├── PaginationError         a page sequence that will not terminate
└── APIResponseError        any non-2xx response
    ├── AuthenticationError 401, 403
    ├── NotFoundError       404
    ├── RateLimitError      429, after retries are exhausted
    └── ServerError         5xx
```

Each exception carries context as attributes and renders it into the message:

```pycon
>>> client.devices.get("nope")
NotFoundError: Requested resource was not found (status_code: 404 | url: https://... | detail: Not found.)
```

```python
except APIResponseError as exc:
    print(exc.status_code, exc.url, exc.detail)
```

## What gets retried

Transient failures are retried automatically with exponential backoff and full jitter:

- **Statuses** `429`, `500`, `502`, `503`, `504`.
- **Transport errors** such as connection failures and read timeouts.

A `Retry-After` header is honoured when present, in both its seconds and HTTP-date forms, and
capped at `IruConfig.max_backoff`.

Retries only apply to **idempotent** requests — `GET`, `PUT`, and `DELETE`. A failed `POST` or
`PATCH` is raised immediately rather than risking a duplicate write.

```python
from irusdk import IruConfig

config = IruConfig(max_retries=5, backoff_factor=1.0, max_backoff=30.0)
```

Set `max_retries=0` to disable retries entirely.

## Rate limiting

Iru enforces **50 requests/second** and **10,000 requests/hour** per tenant. The SDK throttles
itself below both, defaulting to 45/sec and 9,500/hour — vendors count retries and redirects
differently than clients do, so the margin is deliberate.

```python
config = IruConfig(requests_per_second=20, requests_per_hour=5_000)
```

When the API does return a `429`, the whole client backs off, not just the request that was
rejected — otherwise concurrent workers would retry into the same wall.

## Logging

The SDK logs to the `irusdk` logger. Retries are logged at `DEBUG`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("irusdk").setLevel(logging.DEBUG)
```
