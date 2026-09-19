"""Custom script service, exercised against both clients.

The list endpoint pages by ``page`` with no size parameter, which is the one envelope the other
service tests do not already cover.
"""

import json

import httpx
import pytest
import respx

from conftest import BASE_URL, ClientAdapter
from irusdk._endpoints import custom_scripts as endpoints

API = f"{BASE_URL}/api/v1"
SCRIPTS = f"{API}/library/custom-scripts"


def _script(index: int, **overrides: object) -> dict:
    """A custom script record shaped like the API's own example."""
    record = {
        "id": f"script-{index}",
        "name": f"Custom Script {index}",
        "active": True,
        "execution_frequency": "every_day",
        "restart": False,
        "script": 'echo "Hello World!"',
        "remediation_script": "",
        "created_at": "2022-03-24T17:30:26.625839Z",
        "updated_at": "2022-03-24T17:30:26.625856Z",
    }
    record.update(overrides)
    return record


def _envelope(records: list[dict], total: int, next_url: str | None = None) -> dict:
    return {"count": total, "next": next_url, "previous": None, "results": records}


@respx.mock
def test_list_walks_every_page(any_client: ClientAdapter) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("page", 1))
        if page == 1:
            return httpx.Response(
                200, json=_envelope([_script(1), _script(2)], 3, f"{SCRIPTS}?page=2")
            )
        return httpx.Response(200, json=_envelope([_script(3)], 3))

    respx.get(SCRIPTS).mock(side_effect=respond)

    scripts = any_client.collect(any_client.client.custom_scripts.list)

    assert [s.id for s in scripts] == ["script-1", "script-2", "script-3"]


@respx.mock
def test_blank_remediation_script_becomes_none(any_client: ClientAdapter) -> None:
    respx.get(f"{SCRIPTS}/script-1").mock(return_value=httpx.Response(200, json=_script(1)))

    script = any_client.call(any_client.client.custom_scripts.get, "script-1")

    assert script.remediation_script is None
    assert script.name == "Custom Script 1"


@respx.mock
def test_create_sends_the_documented_payload(any_client: ClientAdapter) -> None:
    route = respx.post(SCRIPTS).mock(
        return_value=httpx.Response(201, json=_script(9, name="new_custom_script"))
    )

    created = any_client.call(
        any_client.client.custom_scripts.create,
        name="new_custom_script",
        script='echo "hi"',
        execution_frequency="once",
    )

    sent = json.loads(route.calls.last.request.content)
    assert sent == {
        "name": "new_custom_script",
        "script": 'echo "hi"',
        "active": False,
        "execution_frequency": "once",
        "restart": False,
        "show_in_self_service": False,
    }
    assert created.id == "script-9"


@respx.mock
def test_update_sends_only_what_was_given(any_client: ClientAdapter) -> None:
    route = respx.patch(f"{SCRIPTS}/script-1").mock(
        return_value=httpx.Response(200, json=_script(1, active=False))
    )

    any_client.call(any_client.client.custom_scripts.update, "script-1", active=False)

    assert json.loads(route.calls.last.request.content) == {"active": False}


@respx.mock
def test_delete_returns_nothing(any_client: ClientAdapter) -> None:
    route = respx.delete(f"{SCRIPTS}/script-1").mock(return_value=httpx.Response(204))

    assert any_client.call(any_client.client.custom_scripts.delete, "script-1") is None
    assert route.called


def test_no_enforcement_requires_self_service() -> None:
    with pytest.raises(ValueError, match="requires show_in_self_service"):
        endpoints.create_custom_script(
            name="s", script="echo", execution_frequency="no_enforcement"
        )


def test_self_service_requires_a_category() -> None:
    with pytest.raises(ValueError, match="requires self_service_category_id"):
        endpoints.create_custom_script(name="s", script="echo", show_in_self_service=True)


def test_self_service_fields_ride_along_when_valid() -> None:
    spec = endpoints.create_custom_script(
        name="s",
        script="echo",
        execution_frequency="no_enforcement",
        show_in_self_service=True,
        self_service_category_id="cat-1",
        self_service_recommended=True,
    )

    assert spec.json["self_service_category_id"] == "cat-1"
    assert spec.json["self_service_recommended"] is True
