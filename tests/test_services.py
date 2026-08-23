"""The Phase 5 services, exercised against both clients.

Each family pages differently, so these also serve as end-to-end coverage of every pagination
strategy against a real transport.
"""

import json

import httpx
import respx

from conftest import BASE_URL, ClientAdapter

API = f"{BASE_URL}/api/v1"


def _envelope(records: list[dict], total: int, next_url: str | None = None) -> dict:
    return {"count": total, "next": next_url, "previous": None, "results": records}


@respx.mock
def test_blueprints_list_walks_the_count_envelope(any_client: ClientAdapter) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        offset = int(request.url.params.get("offset", 0))
        limit = int(request.url.params.get("limit", 2))
        records = [
            {"id": f"bp-{i}", "name": f"Blueprint {i}"}
            for i in range(offset, min(offset + limit, 5))
        ]
        return httpx.Response(200, json=_envelope(records, total=5))

    respx.get(f"{API}/blueprints").mock(side_effect=respond)

    blueprints = any_client.collect(any_client.client.blueprints.list, page_size=2)

    assert [b.id for b in blueprints] == ["bp-0", "bp-1", "bp-2", "bp-3", "bp-4"]
    assert blueprints[0].name == "Blueprint 0"


@respx.mock
def test_blueprints_pages_report_the_total(any_client: ClientAdapter) -> None:
    respx.get(f"{API}/blueprints").mock(
        return_value=httpx.Response(200, json=_envelope([{"id": "bp-0"}], total=1))
    )

    pages = any_client.collect(any_client.client.blueprints.pages)

    assert len(pages) == 1
    assert pages[0].total == 1


@respx.mock
def test_blueprint_get_and_create(any_client: ClientAdapter) -> None:
    respx.get(f"{API}/blueprints/bp-1").mock(
        return_value=httpx.Response(200, json={"id": "bp-1", "name": "Main", "computers_count": 12})
    )
    create = respx.post(f"{API}/blueprints").mock(
        return_value=httpx.Response(201, json={"id": "bp-2", "name": "New"})
    )

    fetched = any_client.call(any_client.client.blueprints.get, "bp-1")
    created = any_client.call(any_client.client.blueprints.create, "New", description="d")

    assert fetched.computers_count == 12
    assert created.id == "bp-2"
    assert json.loads(create.calls.last.request.read()) == {"name": "New", "description": "d"}


@respx.mock
def test_blueprint_library_items_unwraps_the_envelope(any_client: ClientAdapter) -> None:
    respx.get(f"{API}/blueprints/bp-1/list-library-items").mock(
        return_value=httpx.Response(
            200, json={"results": [{"id": "li-1", "name": "Chrome", "type": "Custom App"}]}
        )
    )

    items = any_client.call(any_client.client.blueprints.library_items, "bp-1")

    assert [i.name for i in items] == ["Chrome"]


@respx.mock
def test_users_follow_the_cursor(any_client: ClientAdapter) -> None:
    first = {
        "next": f"{API}/users?cursor=PAGE2",
        "previous": None,
        "results": [{"id": "u-1", "email": "a@x.io", "name": "A"}],
    }
    second = {"next": None, "previous": None, "results": [{"id": "u-2", "email": "b@x.io"}]}
    route = respx.get(f"{API}/users").mock(
        side_effect=[httpx.Response(200, json=first), httpx.Response(200, json=second)]
    )

    users = any_client.collect(any_client.client.users.list)

    assert [u.id for u in users] == ["u-1", "u-2"]
    assert route.calls[1].request.url.params["cursor"] == "PAGE2"


@respx.mock
def test_users_page_by_size_per_page(any_client: ClientAdapter) -> None:
    route = respx.get(f"{API}/users").mock(
        return_value=httpx.Response(200, json={"next": None, "results": []})
    )

    any_client.collect(any_client.client.users.list, page_size=25)

    params = route.calls.last.request.url.params
    assert params["sizePerPage"] == "25"
    assert "limit" not in params


@respx.mock
def test_tags_send_no_page_size_parameter(any_client: ClientAdapter) -> None:
    route = respx.get(f"{API}/tags").mock(
        return_value=httpx.Response(
            200, json={"count": 1, "next": None, "results": [{"id": "t-1", "name": "lab"}]}
        )
    )

    tags = any_client.collect(any_client.client.tags.list)

    assert [t.name for t in tags] == ["lab"]
    assert not dict(route.calls.last.request.url.params)


@respx.mock
def test_tag_create_and_delete(any_client: ClientAdapter) -> None:
    create = respx.post(f"{API}/tags").mock(
        return_value=httpx.Response(201, json={"id": "t-9", "name": "new"})
    )
    delete = respx.delete(f"{API}/tags/t-9").mock(return_value=httpx.Response(204))

    tag = any_client.call(any_client.client.tags.create, "new")
    any_client.call(any_client.client.tags.delete, "t-9")

    assert tag.id == "t-9"
    assert json.loads(create.calls.last.request.read()) == {"name": "new"}
    assert delete.call_count == 1
