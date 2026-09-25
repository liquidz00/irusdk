"""Custom app service, exercised against both clients.

The records here are shaped from a live tenant rather than from the vendor's example, because
the two disagree in one way that matters: the API omits the Self Service keys entirely unless
the app is offered there, rather than sending them as null.
"""

import httpx
import respx

from conftest import BASE_URL, ClientAdapter

API = f"{BASE_URL}/api/v1"
APPS = f"{API}/library/custom-apps"


def _app(index: int, **overrides: object) -> dict:
    """A custom app record shaped like a live one."""
    record = {
        "id": f"app-{index}",
        "name": f"Custom App {index}",
        "active": True,
        "install_type": "package",
        "install_enforcement": "continuously_enforce",
        "unzip_location": "",
        "restart": False,
        "audit_script": "#!/bin/bash\nexit 0",
        "preinstall_script": "",
        "postinstall_script": "",
        "sha256": "46292153742514" + "0" * 50,
        "file_key": f"tenants/t-1/library/custom-apps/app-{index}/dialog-3.1.0_46292153.pkg",
        "file_url": "https://ipaapps.kandji.io/tenants/t-1/dialog-3.1.0_46292153.pkg",
        "file_size": 21133559,
        "file_updated": "2026-09-09T14:56:40Z",
        "created_at": "2026-09-09T14:57:43.908572Z",
        "updated_at": "2026-09-10T12:23:15.516061Z",
        "show_in_self_service": False,
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
            return httpx.Response(200, json=_envelope([_app(1), _app(2)], 3, f"{APPS}?page=2"))
        return httpx.Response(200, json=_envelope([_app(3)], 3))

    respx.get(APPS).mock(side_effect=respond)

    apps = any_client.collect(any_client.client.custom_apps.list)

    assert [a.id for a in apps] == ["app-1", "app-2", "app-3"]


@respx.mock
def test_blank_scripts_and_unzip_location_become_none(any_client: ClientAdapter) -> None:
    respx.get(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_app(1)))

    app = any_client.call(any_client.client.custom_apps.get, "app-1")

    assert app.preinstall_script is None
    assert app.postinstall_script is None
    assert app.unzip_location is None
    assert app.audit_script == "#!/bin/bash\nexit 0"


@respx.mock
def test_absent_self_service_keys_are_none(any_client: ClientAdapter) -> None:
    """The API omits these keys rather than nulling them when the app is not in Self Service."""
    respx.get(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_app(1)))

    app = any_client.call(any_client.client.custom_apps.get, "app-1")

    assert app.self_service_category_id is None
    assert app.self_service_recommended is None
    assert app.unknown_fields == {}


@respx.mock
def test_self_service_keys_are_read_when_present(any_client: ClientAdapter) -> None:
    record = _app(
        2,
        show_in_self_service=True,
        self_service_category_id="8b6464ac-2ed0-49e2-a4e3-35a161953ecb",
        self_service_recommended=False,
    )
    respx.get(f"{APPS}/app-2").mock(return_value=httpx.Response(200, json=record))

    app = any_client.call(any_client.client.custom_apps.get, "app-2")

    assert app.self_service_category_id == "8b6464ac-2ed0-49e2-a4e3-35a161953ecb"
    assert app.self_service_recommended is False


@respx.mock
def test_file_basename_drops_the_storage_prefix(any_client: ClientAdapter) -> None:
    """`file_key` is a full object path; the upload token stays, since it names the object."""
    respx.get(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_app(1)))

    app = any_client.call(any_client.client.custom_apps.get, "app-1")

    assert app.file_basename == "dialog-3.1.0_46292153.pkg"


@respx.mock
def test_file_basename_is_blank_without_a_key(any_client: ClientAdapter) -> None:
    respx.get(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_app(1, file_key=None)))

    app = any_client.call(any_client.client.custom_apps.get, "app-1")

    assert app.file_basename == ""


@respx.mock
def test_an_unknown_field_is_carried_not_raised(any_client: ClientAdapter) -> None:
    record = _app(1, some_new_key="whatever Iru adds next")
    respx.get(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=record))

    app = any_client.call(any_client.client.custom_apps.get, "app-1")

    assert app.unknown_fields == {"some_new_key": "whatever Iru adds next"}
