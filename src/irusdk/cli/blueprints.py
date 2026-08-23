"""``irusdk blueprints`` commands."""

import click

from ._console import print_json, print_record, print_table
from ._helpers import build_client, handle_errors

LIST_COLUMNS = ("id", "name", "type", "computers_count", "description")
DETAIL_COLUMNS = (*LIST_COLUMNS, "icon", "color", "missing_computers_count")
ITEM_COLUMNS = ("id", "name", "type", "active")


@click.group("blueprints", short_help="Query and manage blueprints")
def blueprints() -> None:
    """Work with the blueprints defined in your tenant."""


@blueprints.command("list", short_help="List blueprints", options_metavar="<options>")
@click.option("--name", help="Only blueprints whose name matches.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def list_blueprints(obj: dict, name: str | None, as_json: bool) -> None:
    """List every blueprint in the tenant."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        rows = [b.model_dump(mode="json") for b in client.blueprints.list(name=name)]

    if as_json:
        print_json(rows)
        return
    print_table(rows, LIST_COLUMNS, f"Blueprints ({len(rows)})")


@blueprints.command("get", short_help="Show one blueprint", options_metavar="<options>")
@click.argument("blueprint_id")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def get_blueprint(obj: dict, blueprint_id: str, as_json: bool) -> None:
    """Show a single blueprint by its BLUEPRINT_ID."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        blueprint = client.blueprints.get(blueprint_id)

    row = blueprint.model_dump(mode="json")
    if as_json:
        print_json(row)
        return
    print_record(row, DETAIL_COLUMNS, "Blueprint")


@blueprints.command(
    "library-items", short_help="List a blueprint's library items", options_metavar="<options>"
)
@click.argument("blueprint_id")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def blueprint_library_items(obj: dict, blueprint_id: str, as_json: bool) -> None:
    """List the library items assigned to BLUEPRINT_ID."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        rows = [i.model_dump(mode="json") for i in client.blueprints.library_items(blueprint_id)]

    if as_json:
        print_json(rows)
        return
    print_table(rows, ITEM_COLUMNS, f"Library items ({len(rows)})")
