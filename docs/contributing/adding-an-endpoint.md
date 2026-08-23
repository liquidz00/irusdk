# Adding an endpoint

This SDK trades a little indirection for a lot of protection against the sync and async clients
drifting apart. The cost is that adding an endpoint touches two files instead of one. This page is
that checklist.

Everything you need is in `spec/iru-openapi.json` — the path, its query parameters, and a response
schema with realistic examples. Read it first; do not guess field names.

:::{note}
`spec/` is not tracked in version control, so a fresh clone will not have it. See
{doc}`api-spec` for how to obtain a copy and why it is kept out of the repository.
:::

## 1. The model

If the response shape is new, add a model in `src/irusdk/models/`.

```python
from . import Model


class Widget(Model):
    """
    A widget as returned by ``GET /api/v1/widgets``.

    :ivar id: The widget's identifier.
    :ivar name: The widget's name.
    """

    id: str | None = None
    name: str | None = None
```

Every field is `str | None = None` and the base permits extras. That is deliberate: see the warning
on {doc}`../reference/models`.

## 2. The endpoint spec

Add a pure function in `src/irusdk/_endpoints/`. It returns a description of the call and performs
no I/O, so it can be unit-tested without HTTP.

```python
def list_widgets(*, active: bool | None = None, page_size: int = 100) -> PagedSpec[Widget]:
    """Build the spec for the paginated widget list."""
    return PagedSpec(
        base=RequestSpec(
            method="GET",
            path="/api/v1/widgets",
            params=drop_none(active=active),
            model=Widget,
        ),
        strategy=OffsetPagination(results_key="results", total_key="count"),
        page_size=page_size,
    )
```

Pick the strategy from the response envelope — the table in {doc}`../guide/pagination` maps every
shape the API uses. Getting this wrong is the most likely way to introduce a bug, so check the
example payload in the spec rather than assuming.

`_endpoints/` must not import anything from `_transport/` or `client.py`.

## 3. Both service methods

Add the sync method and its async twin **in the same file**, adjacent, in `src/irusdk/services/`.

```python
class WidgetsAPI:
    def list(self, *, active: bool | None = None) -> Iterator[Widget]:
        """
        Iterate every widget, paginating transparently.

        :param active: Only widgets in this state.
        :type active: bool | None
        :rtype: Iterator[Widget]
        """
        return self._transport.iterate(endpoints.list_widgets(active=active))


class AsyncWidgetsAPI:
    @copy_doc(WidgetsAPI.list)
    def list(self, *, active: bool | None = None) -> AsyncIterator[Widget]:
        return self._transport.iterate(endpoints.list_widgets(active=active))
```

Three rules here, all of them load-bearing:

- **Write the method out concretely.** No `**kwargs` passthrough to a generic dispatcher, no
  `getattr`, no methods attached at runtime. Autocomplete is the point of a typed SDK.
- **`list()` on the async twin is a plain `def`**, not `async def`. Returning the async iterator
  directly is what makes `async for x in client.widgets.list()` work without a second `await`.
- **`@copy_doc`** puts the sync method's prose on the twin so it is written once.

:::{warning}
A class that defines a method named `list` shadows the builtin inside its own class body. A later
`-> list[Thing]` annotation in that class then resolves to the method and raises `TypeError`. Use
`Sequence[Thing]` instead. `BlueprintsAPI.library_items` is the existing example.
:::

## 4. Wire it into both clients

In `src/irusdk/client.py`, add the attribute to `IruClient` and `AsyncIruClient`, and to both
class docstrings.

## 5. Test it against both clients

Use the `any_client` fixture. It is parametrized over sync and async, so one test body covers both:

```python
@respx.mock
def test_widgets_list(any_client: ClientAdapter) -> None:
    respx.get(f"{API}/widgets").mock(return_value=httpx.Response(200, json=...))

    widgets = any_client.collect(any_client.client.widgets.list)

    assert [w.id for w in widgets] == ["w-1"]
```

`any_client.call(...)` is for single-record methods; `any_client.collect(...)` drains an iterator.
A test that only runs against one client is not enough — the one real sync/async divergence found
so far was in code that only the sync path reached.

## 6. Run the checks

```console
$ make format
$ make lint
$ make test-cov
```

`tests/test_parity.py` will fail if you added a method to one client and not the other, or if the
signatures differ. That is the safety net; do not skip it.

## 7. Optional: a CLI command

If the endpoint is useful from a terminal, add a command in `src/irusdk/cli/`. Keep all Rich usage
in `_console.py`, take `--json`, and decorate with `@handle_errors` so failures print a message
instead of a traceback.
