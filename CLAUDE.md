# irusdk

A Python SDK and thin CLI for querying and acting on an Iru (formerly Kandji) fleet.

## Scope — read before adding endpoints

This SDK covers the **fleet** surface: devices, device actions, device details, Prism, users, tags,
and blueprints as fleet context.

It deliberately does **not** author library content — Custom Apps, Custom Scripts, Custom Profiles,
In-House Apps. Iru ships `iructl` (https://github.com/kandji-inc/iructl) for that, and it does the
job better: local repo sync, YAML/plist round-tripping, presigned S3 package upload. Those services
existed here briefly and were removed on purpose.

**Do not re-add them.** If a task seems to call for `/api/v1/library/custom-*` write operations,
that is a signal the task belongs to `iructl`, not here. Read-only library shapes stay (see
`models/library.py::LibraryItem`) because blueprints and devices report what is assigned to them.

Blueprints are in scope: every device carries `blueprint_id`/`blueprint_name` and blueprint is a
primary device filter, so listing and reading them is fleet context, not content authoring.

## API facts

- Base URL is tenant-scoped: `https://{subdomain}.api.kandji.io` (US),
  `https://{subdomain}.api.eu.kandji.io` (EU).
- Auth is a static long-lived bearer token. There is no refresh endpoint.
- Rate limits: 10,000 requests/hour and 50 requests/second, per tenant.
- Wire format is snake_case, so models need no alias generator by default.
- `spec/iru-openapi.json` is the best available reference for paths, parameters, and response
  schemas — converted from Iru's Postman collection, with inline JSON Schemas and realistic
  examples for 96 of its 133 operations. Derive models and endpoint parameters from it rather than
  guessing.

  It is **not tracked in version control and is not kept in sync with Iru's API**. It is a local
  snapshot someone exported by hand; treat it as a working reference, not a contract. A fresh clone
  will not have it — see `docs/contributing/api-spec.md` for how to obtain one and why it is not
  committed. Two defects in the conversion to ignore: a stray `POST /` entry, and a typo'd path
  `/api/v1/devices/{device_id}}/action/togglepersonalhotspot`.

## Architecture rules

The SDK ships **both** `IruClient` and `AsyncIruClient`. To keep them from drifting:

- **Endpoints are declared once** in `_endpoints/` as pure functions returning a `RequestSpec` or
  `PagedSpec`. These modules import nothing from `_transport/` or `client.py`.
- **Service classes are hand-written and concretely typed.** No `**kwargs` passthrough, no `getattr`
  dispatch, no dynamically attached methods — that would destroy autocomplete, which is the whole
  point of a typed SDK.
- **Sync and async twins live adjacent in the same file** — both clients in `client.py`, both service
  classes in one `services/*.py`. A missing twin is then visible in the diff.
- `Async*API.list()` is a plain `def` returning `AsyncIterator`, never `async def`. This keeps
  `async for x in client.devices.list()` working without a double-await.
- `tests/test_parity.py` asserts every sync/async pair has matching method names and signatures.
- `_core/` is sync/async-agnostic: it imports no httpx client and no asyncio. Policies there return
  numbers and decisions; the transports own all locking and sleeping.
- Endpoints that fight the declarative model (uploads, multipart, streaming, multi-call flows) use
  `transport.send_raw()` and get hand-written in both service classes. Do not contort `RequestSpec`
  to swallow them.

## Pagination

The API uses several envelope shapes; each maps to a strategy in `_core/pagination.py`:

| Envelope | Params | Endpoints | Concurrent |
|---|---|---|---|
| bare JSON array | `limit`/`offset` | `/devices` | No — terminate on a short page |
| `{count, next, previous, results}` | `limit`/`offset` or `page` | blueprints, library items, ADE | Yes, via `count` |
| `{offset, limit, total, cursor, data}` | `limit`/`offset` | all `/prism/*` | Yes, via `total` (note: `data`, not `results`) |
| `{total, page, size, results}` | `page`/`size` | vulnerability management | Yes, via `total` |
| `{next, previous, results}` | `cursor` | users, admins, audit events | No — follow the `next` URL |

## Services

| Attribute | Class pair | Notes |
|---|---|---|
| `client.devices` | `DevicesAPI` / `AsyncDevicesAPI` | Bare-array offset paging; has `pages()` |
| `client.blueprints` | `BlueprintsAPI` / `AsyncBlueprintsAPI` | Count envelope; has `pages()` |
| `client.users` | `UsersAPI` / `AsyncUsersAPI` | Cursor paging, `sizePerPage` not `limit` |
| `client.tags` | `TagsAPI` / `AsyncTagsAPI` | Count envelope, but no documented page param |

`pages()` exists only where volume warrants it — currently devices and blueprints.

Unwrapped fleet surface worth adding next: device actions (`/devices/{id}/action/*`), device
details sub-resources (apps, library-items, parameters, status), Prism (16 endpoints, all
`{offset, limit, total, cursor, data}`), vulnerabilities, threats, and audit events.

**Gotcha:** a service class that defines a `list` method shadows the builtin inside its class body,
so a later `-> list[Thing]` annotation in that class resolves to the method and raises `TypeError`.
Use `Sequence[Thing]`. See `BlueprintsAPI.library_items`.

## Conventions

- uv for everything; `uv.lock` is committed. `make install-dev`, `make lint`, `make test`.
- ruff only — no mypy. Line length 100.
- Version lives in `src/irusdk/__about__.py` and is bumped by hand; CI reads it and refuses to
  re-tag an existing version.
- Sphinx docstrings (`:param:` / `:type:` / `:return:` / `:rtype:`).
- Comments are rare, short, and explain *why*. Never a comment per line.
