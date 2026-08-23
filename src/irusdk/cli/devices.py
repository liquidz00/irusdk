"""``irusdk devices`` commands."""

import itertools

import click

from ._console import print_json, print_record, print_table
from ._helpers import build_client, handle_errors

LIST_COLUMNS = (
    "device_id",
    "device_name",
    "platform",
    "os_version",
    "serial_number",
    "blueprint_name",
    "last_check_in",
)

DETAIL_COLUMNS = (*LIST_COLUMNS, "model", "agent_version", "mdm_enabled", "is_missing", "tags")


@click.group("devices", short_help="Query and manage devices")
def devices() -> None:
    """Work with the devices enrolled in your tenant."""


@devices.command("list", short_help="List devices", options_metavar="<options>")
@click.option("--platform", help="Mac, iPad, iPhone, AppleTV, Android, or Windows.")
@click.option("--blueprint-id", help="Only devices assigned to this blueprint.")
@click.option("--serial-number", help="Search by serial number.")
@click.option("--device-name", help="Devices whose name contains this string.")
@click.option("--os-version", help="Devices whose OS version contains this string.")
@click.option("--tag-name", help="Only devices carrying this tag.")
@click.option("--user-email", help="Devices assigned to a user with this email.")
@click.option("--ordering", help="Sort field; prefix with '-' to reverse.")
@click.option("--limit", type=int, help="Stop after this many devices.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def list_devices(obj: dict, as_json: bool, limit: int | None, **filters: str | None) -> None:
    """List devices, paginating through the whole fleet unless --limit is given."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        results = client.devices.list(**{k: v for k, v in filters.items() if v is not None})
        devices_found = list(itertools.islice(results, limit) if limit else results)

    rows = [d.model_dump(mode="json") for d in devices_found]
    if as_json:
        print_json(rows)
        return
    print_table(rows, LIST_COLUMNS, f"Devices ({len(rows)})")


@devices.command("get", short_help="Show one device", options_metavar="<options>")
@click.argument("device_id")
@click.option("--details", is_flag=True, help="Fetch the full detail document instead.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def get_device(obj: dict, device_id: str, details: bool, as_json: bool) -> None:
    """Show a single device by its DEVICE_ID."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        if details:
            print_json(client.devices.details(device_id))
            return
        device = client.devices.get(device_id)

    row = device.model_dump(mode="json")
    if as_json:
        print_json(row)
        return
    print_record(row, DETAIL_COLUMNS, "Device")


@devices.command("delete", short_help="Delete a device record", options_metavar="<options>")
@click.argument("device_id")
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_obj
@handle_errors
def delete_device(obj: dict, device_id: str, yes: bool) -> None:
    """Delete the device record identified by DEVICE_ID."""
    if not yes:
        click.confirm(f"Delete device {device_id}?", abort=True)

    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        client.devices.delete(device_id)

    click.echo(f"Deleted {device_id}.")
