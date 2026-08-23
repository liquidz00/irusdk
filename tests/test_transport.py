"""Transport behaviour, exercised against both clients."""

import httpx
import pytest
import respx

from conftest import BASE_URL, TOKEN, ClientAdapter, device_payload
from irusdk import (
    AuthenticationError,
    ConfigurationError,
    IruClient,
    NotFoundError,
    RateLimitError,
    ServerError,
)

DEVICE_URL = f"{BASE_URL}/api/v1/devices/device-0001"


@respx.mock
def test_sends_bearer_token_and_user_agent(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=device_payload(1)))

    any_client.call(any_client.client.devices.get, "device-0001")

    request = route.calls.last.request
    assert request.headers["Authorization"] == f"Bearer {TOKEN}"
    assert request.headers["User-Agent"].startswith("irusdk/")


@respx.mock
def test_parses_response_into_model(any_client: ClientAdapter) -> None:
    respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=device_payload(1)))

    device = any_client.call(any_client.client.devices.get, "device-0001")

    assert device.device_name == "Test Mac 1"
    assert device.user.email == "admin@accuhive.io"
    assert device.last_check_in.year == 2024


@respx.mock
def test_preserves_unknown_fields(any_client: ClientAdapter) -> None:
    payload = device_payload(1) | {"a_brand_new_field": "surprise"}
    respx.get(DEVICE_URL).mock(return_value=httpx.Response(200, json=payload))

    device = any_client.call(any_client.client.devices.get, "device-0001")

    assert device.a_brand_new_field == "surprise"


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (401, AuthenticationError),
        (403, AuthenticationError),
        (404, NotFoundError),
        (400, None),
    ],
)
@respx.mock
def test_maps_status_codes_to_exceptions(
    any_client: ClientAdapter, status: int, expected: type[Exception] | None
) -> None:
    respx.get(DEVICE_URL).mock(return_value=httpx.Response(status, json={"detail": "nope"}))

    with pytest.raises(expected or Exception) as excinfo:
        any_client.call(any_client.client.devices.get, "device-0001")

    assert "nope" in str(excinfo.value)
    assert str(status) in str(excinfo.value)


@respx.mock
def test_retries_server_errors_then_succeeds(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICE_URL).mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=device_payload(1)),
        ]
    )

    device = any_client.call(any_client.client.devices.get, "device-0001")

    assert device.device_id == "device-0001"
    assert route.call_count == 2


@respx.mock
def test_raises_after_exhausting_retries(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICE_URL).mock(return_value=httpx.Response(500))

    with pytest.raises(ServerError):
        any_client.call(any_client.client.devices.get, "device-0001")

    # The initial attempt plus max_retries.
    assert route.call_count == 3


@respx.mock
def test_honors_retry_after_on_rate_limit(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICE_URL).mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json=device_payload(1)),
        ]
    )

    any_client.call(any_client.client.devices.get, "device-0001")

    assert route.call_count == 2


@respx.mock
def test_raises_rate_limit_error_when_retries_exhausted(any_client: ClientAdapter) -> None:
    respx.get(DEVICE_URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "0"}))

    with pytest.raises(RateLimitError):
        any_client.call(any_client.client.devices.get, "device-0001")


@respx.mock
def test_does_not_retry_non_idempotent_requests(any_client: ClientAdapter) -> None:
    route = respx.patch(DEVICE_URL).mock(return_value=httpx.Response(500))

    with pytest.raises(ServerError):
        any_client.call(any_client.client.devices.update, "device-0001", asset_tag="x")

    assert route.call_count == 1


@respx.mock
def test_delete_sends_no_body(any_client: ClientAdapter) -> None:
    route = respx.delete(DEVICE_URL).mock(return_value=httpx.Response(204))

    assert any_client.call(any_client.client.devices.delete, "device-0001") is None
    assert route.call_count == 1


def test_requires_a_token() -> None:
    with pytest.raises(ConfigurationError):
        IruClient("accuhive", "")


def test_requires_a_subdomain() -> None:
    with pytest.raises(ConfigurationError):
        IruClient("", "token")


@respx.mock
def test_retries_network_errors_then_succeeds(any_client: ClientAdapter) -> None:
    route = respx.get(DEVICE_URL).mock(
        side_effect=[
            httpx.ConnectError("connection refused"),
            httpx.Response(200, json=device_payload(1)),
        ]
    )

    device = any_client.call(any_client.client.devices.get, "device-0001")

    assert device.device_id == "device-0001"
    assert route.call_count == 2


@respx.mock
def test_reraises_network_errors_once_retries_are_exhausted(any_client: ClientAdapter) -> None:
    respx.get(DEVICE_URL).mock(side_effect=httpx.ConnectError("connection refused"))

    with pytest.raises(httpx.ConnectError):
        any_client.call(any_client.client.devices.get, "device-0001")


@respx.mock
def test_does_not_retry_network_errors_on_non_idempotent_requests(
    any_client: ClientAdapter,
) -> None:
    route = respx.patch(DEVICE_URL).mock(side_effect=httpx.ConnectError("refused"))

    with pytest.raises(httpx.ConnectError):
        any_client.call(any_client.client.devices.update, "device-0001", asset_tag="x")

    assert route.call_count == 1
