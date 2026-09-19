"""Custom profile service, exercised against both clients.

Create and update send multipart rather than JSON, so these are also the coverage for
``RequestSpec``'s ``data``/``files`` reaching the wire on both transports.
"""

import httpx
import pytest
import respx

from conftest import BASE_URL, ClientAdapter
from irusdk._endpoints import custom_profiles as endpoints

API = f"{BASE_URL}/api/v1"
PROFILES = f"{API}/library/custom-profiles"

MOBILECONFIG = b'<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0"><dict/></plist>\n'


def _profile(index: int, **overrides: object) -> dict:
    """A custom profile record shaped like the API's own example."""
    record = {
        "id": f"profile-{index}",
        "name": f"Custom Profile {index}",
        "active": False,
        "profile": "<xml payload>",
        "mdm_identifier": f"com.kandji.profile.custom.profile-{index}",
        "runs_on_mac": True,
        "runs_on_iphone": False,
        "runs_on_ipad": False,
        "runs_on_tv": False,
        "runs_on_vision": False,
        "created_at": "2023-03-10T19:27:58.677287Z",
        "updated_at": "2023-03-10T20:06:28.622392Z",
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
                200, json=_envelope([_profile(1), _profile(2)], 3, f"{PROFILES}?page=2")
            )
        return httpx.Response(200, json=_envelope([_profile(3)], 3))

    respx.get(PROFILES).mock(side_effect=respond)

    profiles = any_client.collect(any_client.client.custom_profiles.list)

    assert [p.id for p in profiles] == ["profile-1", "profile-2", "profile-3"]


@respx.mock
def test_get_returns_the_iru_assigned_identifier(any_client: ClientAdapter) -> None:
    respx.get(f"{PROFILES}/profile-1").mock(return_value=httpx.Response(200, json=_profile(1)))

    profile = any_client.call(any_client.client.custom_profiles.get, "profile-1")

    assert profile.mdm_identifier == "com.kandji.profile.custom.profile-1"
    assert profile.runs_on_mac is True


@respx.mock
def test_create_uploads_the_mobileconfig_as_a_file_part(any_client: ClientAdapter) -> None:
    route = respx.post(PROFILES).mock(return_value=httpx.Response(201, json=_profile(9)))

    created = any_client.call(
        any_client.client.custom_profiles.create,
        name="Managed Settings",
        profile=MOBILECONFIG,
        runs_on_mac=True,
    )

    request = route.calls.last.request
    body = request.content
    assert request.headers["content-type"].startswith("multipart/form-data")
    assert b'filename="Managed Settings.mobileconfig"' in body
    assert MOBILECONFIG in body
    assert b'name="runs_on_mac"' in body
    assert created.mdm_identifier == "com.kandji.profile.custom.profile-9"


@respx.mock
def test_update_without_a_profile_sends_no_file_part(any_client: ClientAdapter) -> None:
    route = respx.patch(f"{PROFILES}/profile-1").mock(
        return_value=httpx.Response(200, json=_profile(1, name="Renamed"))
    )

    any_client.call(any_client.client.custom_profiles.update, "profile-1", name="Renamed")

    request = route.calls.last.request
    assert b"filename=" not in request.content
    assert b"Renamed" in request.content


@respx.mock
def test_update_replaces_the_profile_when_given_one(any_client: ClientAdapter) -> None:
    route = respx.patch(f"{PROFILES}/profile-1").mock(
        return_value=httpx.Response(200, json=_profile(1))
    )

    any_client.call(any_client.client.custom_profiles.update, "profile-1", profile=MOBILECONFIG)

    assert MOBILECONFIG in route.calls.last.request.content


@respx.mock
def test_delete_returns_nothing(any_client: ClientAdapter) -> None:
    route = respx.delete(f"{PROFILES}/profile-1").mock(return_value=httpx.Response(204))

    assert any_client.call(any_client.client.custom_profiles.delete, "profile-1") is None
    assert route.called


def test_create_requires_a_platform() -> None:
    with pytest.raises(ValueError, match="at least one platform"):
        endpoints.create_custom_profile(name="p", profile=MOBILECONFIG)


def test_create_rejects_every_platform_being_false() -> None:
    with pytest.raises(ValueError, match="at least one platform"):
        endpoints.create_custom_profile(name="p", profile=MOBILECONFIG, runs_on_mac=False)


def test_update_does_not_require_a_platform() -> None:
    spec = endpoints.update_custom_profile("profile-1", name="Renamed")

    assert spec.data == {"name": "Renamed"}
    assert spec.files is None
