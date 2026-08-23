"""CLI behaviour, driven through click's test runner."""

import httpx
import pytest
import respx
from click.testing import CliRunner

from conftest import BASE_URL, SUBDOMAIN, TOKEN, device_payload
from irusdk.cli import cli

DEVICES_URL = f"{BASE_URL}/api/v1/devices"
CREDENTIALS = ["--subdomain", SUBDOMAIN, "--token", TOKEN]


@pytest.fixture
def runner(monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    # Keep an operator's own environment from leaking into the tests.
    for name in ("IRU_SUBDOMAIN", "IRU_API_TOKEN", "IRU_REGION"):
        monkeypatch.delenv(name, raising=False)
    # CI defaults to 80 columns, which crushes a wide table; assume a real terminal.
    monkeypatch.setenv("COLUMNS", "200")
    return CliRunner()


def test_help_lists_the_device_commands(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["-h"])

    assert result.exit_code == 0
    assert "devices" in result.output


def test_version_flag(runner: CliRunner) -> None:
    from irusdk import __version__

    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


@respx.mock
def test_devices_list_renders_a_table(runner: CliRunner) -> None:
    respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[device_payload(1)]))

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "list"])

    assert result.exit_code == 0
    assert "Test Mac 1" in result.output
    assert "SERIAL0001" in result.output


@respx.mock
def test_devices_list_emits_json(runner: CliRunner) -> None:
    respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[device_payload(1)]))

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "list", "--json"])

    assert result.exit_code == 0
    assert "device-0001" in result.output


@respx.mock
def test_devices_list_forwards_filters(runner: CliRunner) -> None:
    route = respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[]))

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "list", "--platform", "Mac"])

    assert result.exit_code == 0
    assert route.calls.last.request.url.params["platform"] == "Mac"


@respx.mock
def test_devices_list_honors_the_limit(runner: CliRunner) -> None:
    respx.get(DEVICES_URL).mock(
        return_value=httpx.Response(200, json=[device_payload(i) for i in range(10)])
    )

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "list", "--limit", "3", "--json"])

    assert result.exit_code == 0
    assert result.output.count('"device_id"') == 3


@respx.mock
def test_devices_get_renders_one_device(runner: CliRunner) -> None:
    respx.get(f"{DEVICES_URL}/device-0001").mock(
        return_value=httpx.Response(200, json=device_payload(1))
    )

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "get", "device-0001"])

    assert result.exit_code == 0
    assert "Test Mac 1" in result.output


@respx.mock
def test_reports_api_errors_without_a_traceback(runner: CliRunner) -> None:
    respx.get(f"{DEVICES_URL}/nope").mock(
        return_value=httpx.Response(404, json={"detail": "Not found."})
    )

    result = runner.invoke(cli, [*CREDENTIALS, "devices", "get", "nope"])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "Traceback" not in result.output


def test_requires_a_subdomain(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--token", TOKEN, "devices", "list"])

    assert result.exit_code == 2
    assert "IRU_SUBDOMAIN" in result.output


def test_requires_a_token(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["--subdomain", SUBDOMAIN, "devices", "list"])

    assert result.exit_code == 2
    assert "IRU_API_TOKEN" in result.output


@respx.mock
def test_reads_credentials_from_the_environment(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("IRU_SUBDOMAIN", SUBDOMAIN)
    monkeypatch.setenv("IRU_API_TOKEN", TOKEN)
    respx.get(DEVICES_URL).mock(return_value=httpx.Response(200, json=[]))

    result = runner.invoke(cli, ["devices", "list"])

    assert result.exit_code == 0


@respx.mock
def test_delete_requires_confirmation(runner: CliRunner) -> None:
    route = respx.delete(f"{DEVICES_URL}/device-0001").mock(return_value=httpx.Response(204))

    aborted = runner.invoke(cli, [*CREDENTIALS, "devices", "delete", "device-0001"], input="n\n")
    assert aborted.exit_code == 1
    assert route.call_count == 0

    confirmed = runner.invoke(cli, [*CREDENTIALS, "devices", "delete", "device-0001", "--yes"])
    assert confirmed.exit_code == 0
    assert route.call_count == 1


@respx.mock
def test_blueprints_list_renders_a_table(runner: CliRunner) -> None:
    respx.get(f"{BASE_URL}/api/v1/blueprints").mock(
        return_value=httpx.Response(
            200,
            json={
                "count": 1,
                "next": None,
                "results": [{"id": "bp-1", "name": "Main Hive", "computers_count": 12}],
            },
        )
    )

    result = runner.invoke(cli, [*CREDENTIALS, "blueprints", "list"])

    assert result.exit_code == 0
    assert "Main Hive" in result.output


@respx.mock
def test_users_list_honors_the_limit(runner: CliRunner) -> None:
    respx.get(f"{BASE_URL}/api/v1/users").mock(
        return_value=httpx.Response(
            200,
            json={
                "next": None,
                "results": [{"id": f"u-{i}", "email": f"u{i}@x.io"} for i in range(5)],
            },
        )
    )

    result = runner.invoke(cli, [*CREDENTIALS, "users", "list", "--limit", "2", "--json"])

    assert result.exit_code == 0
    assert result.output.count('"email"') == 2


@respx.mock
def test_tags_create_reports_the_new_id(runner: CliRunner) -> None:
    respx.post(f"{BASE_URL}/api/v1/tags").mock(
        return_value=httpx.Response(201, json={"id": "t-9", "name": "lab"})
    )

    result = runner.invoke(cli, [*CREDENTIALS, "tags", "create", "lab"])

    assert result.exit_code == 0
    assert "t-9" in result.output
