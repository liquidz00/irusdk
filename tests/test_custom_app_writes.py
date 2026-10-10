"""Creating and updating a custom app, including the upload that leaves the tenant.

The installer does not travel through the Iru API: it goes to object storage on a presigned
POST. That hop is the interesting one, and the property worth pinning hardest is that it
carries no Iru credentials -- see `test_the_tenant_token_never_reaches_the_store`.
"""

import httpx
import pytest
import respx

from conftest import BASE_URL, TOKEN, ClientAdapter
from irusdk import PayloadTransferError, ServerError

API = f"{BASE_URL}/api/v1"
APPS = f"{API}/library/custom-apps"
STORE = "https://ipaapps-uploads.kandji.io/"

FILE_KEY = "tenants/t-1/library/custom-apps/uploads/Thing-2.4_a1b2c3d4.pkg"

# `create` defaults to continuously_enforce, which Iru refuses without one of these.
AUDIT = "#!/bin/bash\nexit 0"


async def _no_sleep(_seconds: float) -> None:
    """Stand-in for asyncio.sleep, so the backoff costs no wall clock in tests."""


def _reservation(**overrides: object) -> dict:
    record = {
        "name": "Thing-2.4.pkg",
        "expires": "2026-09-25T15:00:00Z",
        "post_url": STORE,
        "post_data": {"key": FILE_KEY, "policy": "base64policy", "signature": "sig"},
        "file_key": FILE_KEY,
    }
    record.update(overrides)
    return record


def _created(**overrides: object) -> dict:
    record = {
        "id": "app-new",
        "name": "Thing",
        "active": False,
        "install_type": "package",
        "install_enforcement": "continuously_enforce",
        "unzip_location": "",
        "restart": False,
        "audit_script": "",
        "preinstall_script": "",
        "postinstall_script": "",
        "sha256": "ab" * 32,
        "file_key": FILE_KEY,
        "file_url": f"https://ipaapps.kandji.io/{FILE_KEY}",
        "file_size": 1024,
        "file_updated": "2026-09-25T14:00:00Z",
        "created_at": "2026-09-25T14:00:00Z",
        "updated_at": "2026-09-25T14:00:00Z",
        "show_in_self_service": False,
    }
    record.update(overrides)
    return record


@pytest.fixture
def installer(tmp_path):
    """A stand-in installer with recognizable bytes."""
    path = tmp_path / "Thing-2.4.pkg"
    path.write_bytes(b"pkg-bytes-" * 100)
    return path


@respx.mock
def test_upload_reserves_then_stores_and_returns_the_key(
    any_client: ClientAdapter, installer
) -> None:
    respx.post(f"{APPS}/upload").mock(return_value=httpx.Response(200, json=_reservation()))
    store = respx.post(STORE).mock(return_value=httpx.Response(204))

    key = any_client.call(any_client.client.custom_apps.upload, installer)

    assert key == FILE_KEY
    assert store.called


@respx.mock
def test_the_tenant_token_never_reaches_the_store(any_client: ClientAdapter, installer) -> None:
    """The presigned policy authenticates the upload; the store is not the tenant.

    Sending the Iru token to a third-party host would hand over fleet-wide write access for
    nothing, so the storage client is built bare rather than reusing the API client.
    """
    respx.post(f"{APPS}/upload").mock(return_value=httpx.Response(200, json=_reservation()))
    store = respx.post(STORE).mock(return_value=httpx.Response(204))

    any_client.call(any_client.client.custom_apps.upload, installer)

    headers = store.calls.last.request.headers
    assert "authorization" not in headers
    assert TOKEN not in str(headers)


@respx.mock
def test_the_policy_fields_precede_the_file(any_client: ClientAdapter, installer) -> None:
    """The store rejects an upload whose file part arrives before the policy."""
    respx.post(f"{APPS}/upload").mock(return_value=httpx.Response(200, json=_reservation()))
    store = respx.post(STORE).mock(return_value=httpx.Response(204))

    any_client.call(any_client.client.custom_apps.upload, installer)

    body = store.calls.last.request.content
    assert body.index(b'name="key"') < body.index(b'name="file"')
    assert b"pkg-bytes-" in body


@respx.mock
def test_a_rejected_upload_raises_with_what_the_store_said(
    any_client: ClientAdapter, installer
) -> None:
    respx.post(f"{APPS}/upload").mock(return_value=httpx.Response(200, json=_reservation()))
    respx.post(STORE).mock(return_value=httpx.Response(403, text="policy expired"))

    with pytest.raises(PayloadTransferError, match="policy expired"):
        any_client.call(any_client.client.custom_apps.upload, installer)


@respx.mock
def test_a_reservation_with_no_key_raises(any_client: ClientAdapter, installer) -> None:
    respx.post(f"{APPS}/upload").mock(
        return_value=httpx.Response(200, json=_reservation(file_key=None))
    )
    respx.post(STORE).mock(return_value=httpx.Response(204))

    with pytest.raises(PayloadTransferError, match="no file_key"):
        any_client.call(any_client.client.custom_apps.upload, installer)


@respx.mock
def test_upload_registers_an_overridden_name(any_client: ClientAdapter, installer) -> None:
    reserve = respx.post(f"{APPS}/upload").mock(
        return_value=httpx.Response(200, json=_reservation())
    )
    respx.post(STORE).mock(return_value=httpx.Response(204))

    any_client.call(any_client.client.custom_apps.upload, installer, name="Renamed.pkg")

    assert reserve.calls.last.request.read() == b'{"name":"Renamed.pkg"}'


@respx.mock
def test_create_sends_the_key_and_blanks_the_scripts_not_supplied(
    any_client: ClientAdapter,
) -> None:
    create = respx.post(APPS).mock(return_value=httpx.Response(201, json=_created()))

    app = any_client.call(
        any_client.client.custom_apps.create,
        name="Thing",
        file_key=FILE_KEY,
        audit_script=AUDIT,
    )

    sent = create.calls.last.request.read()
    assert app.id == "app-new"
    assert b'"file_key":' in sent
    assert b'"preinstall_script":""' in sent
    assert b'"postinstall_script":""' in sent


@respx.mock
def test_update_sends_only_what_was_supplied(any_client: ClientAdapter) -> None:
    patch = respx.patch(f"{APPS}/app-1").mock(
        return_value=httpx.Response(200, json=_created(id="app-1", active=True))
    )

    any_client.call(any_client.client.custom_apps.update, "app-1", active=True)

    sent = patch.calls.last.request.read()
    assert sent == b'{"active":true}'


@respx.mock
def test_update_can_clear_a_script_slot(any_client: ClientAdapter) -> None:
    """A blank body is a value; only None means "leave it alone"."""
    patch = respx.patch(f"{APPS}/app-1").mock(
        return_value=httpx.Response(200, json=_created(id="app-1"))
    )

    any_client.call(any_client.client.custom_apps.update, "app-1", postinstall_script="")

    assert patch.calls.last.request.read() == b'{"postinstall_script":""}'


def test_an_audit_script_needs_continuous_enforcement(any_client: ClientAdapter) -> None:
    with pytest.raises(ValueError, match="continuously_enforce"):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            install_enforcement="install_once",
            audit_script="#!/bin/bash\nexit 0",
        )


def test_a_zip_app_needs_an_unzip_location(any_client: ClientAdapter) -> None:
    with pytest.raises(ValueError, match="unzip_location"):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            install_type="zip",
            audit_script=AUDIT,
        )


def test_no_enforcement_needs_self_service(any_client: ClientAdapter) -> None:
    with pytest.raises(ValueError, match="show_in_self_service"):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            install_enforcement="no_enforcement",
        )


def test_self_service_needs_a_category(any_client: ClientAdapter) -> None:
    with pytest.raises(ValueError, match="self_service_category_id"):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            show_in_self_service=True,
            audit_script=AUDIT,
        )


@respx.mock
def test_a_partial_update_does_not_guess_the_enforcement_it_was_not_given(
    any_client: ClientAdapter,
) -> None:
    """Editing an audit script alone must not read "enforcement unknown" as "wrong enforcement"."""
    respx.patch(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_created(id="app-1")))

    any_client.call(
        any_client.client.custom_apps.update, "app-1", audit_script="#!/bin/bash\nexit 1"
    )


@respx.mock
def test_a_create_waits_out_the_upload_still_processing(
    any_client: ClientAdapter, monkeypatch
) -> None:
    """Iru answers 503 while it finalizes a freshly uploaded installer.

    The transport will not retry this by itself -- a POST is not idempotent -- so without the
    wait, every create straight after an upload fails. Found against a live tenant.
    """
    monkeypatch.setattr("irusdk.services.custom_apps.time.sleep", lambda _: None)
    monkeypatch.setattr("asyncio.sleep", _no_sleep)
    respx.post(APPS).mock(
        side_effect=[
            httpx.Response(503, json={"detail": "The upload is still being processed."}),
            httpx.Response(503, json={"detail": "The upload is still being processed."}),
            httpx.Response(201, json=_created()),
        ]
    )

    app = any_client.call(
        any_client.client.custom_apps.create,
        name="Thing",
        file_key=FILE_KEY,
        audit_script=AUDIT,
    )

    assert app.id == "app-new"


@respx.mock
def test_a_real_server_error_is_not_waited_out(any_client: ClientAdapter, monkeypatch) -> None:
    """Only the finalizing 503 is waited on; anything else is the caller's problem now."""
    monkeypatch.setattr("irusdk.services.custom_apps.time.sleep", lambda _: None)
    monkeypatch.setattr("asyncio.sleep", _no_sleep)
    respx.post(APPS).mock(return_value=httpx.Response(500, json={"detail": "boom"}))

    with pytest.raises(ServerError):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            audit_script=AUDIT,
        )


@respx.mock
def test_an_update_waits_the_same_way(any_client: ClientAdapter, monkeypatch) -> None:
    monkeypatch.setattr("irusdk.services.custom_apps.time.sleep", lambda _: None)
    monkeypatch.setattr("asyncio.sleep", _no_sleep)
    respx.patch(f"{APPS}/app-1").mock(
        side_effect=[
            httpx.Response(503, json={"detail": "The upload is still being processed."}),
            httpx.Response(200, json=_created(id="app-1")),
        ]
    )

    app = any_client.call(any_client.client.custom_apps.update, "app-1", active=True)

    assert app.id == "app-1"


def test_continuous_enforcement_needs_an_audit_script(any_client: ClientAdapter) -> None:
    """Iru answers {"audit_script": ["Required when choosing continuously_enforce"]}.

    The converse of the check above, and the one that actually bites: `continuously_enforce`
    is the sensible default for a managed app, so an app scaffolded without an audit script
    fails at create time. Found against a live tenant.
    """
    with pytest.raises(ValueError, match="requires a non-empty audit_script"):
        any_client.call(
            any_client.client.custom_apps.create,
            name="Thing",
            file_key=FILE_KEY,
            install_enforcement="continuously_enforce",
        )


@respx.mock
def test_an_update_does_not_demand_an_audit_script(any_client: ClientAdapter) -> None:
    """Iru still holds the script it was given at create; an update need not resend it."""
    respx.patch(f"{APPS}/app-1").mock(return_value=httpx.Response(200, json=_created(id="app-1")))

    any_client.call(
        any_client.client.custom_apps.update,
        "app-1",
        install_enforcement="continuously_enforce",
    )
