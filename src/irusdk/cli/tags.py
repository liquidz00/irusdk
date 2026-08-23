"""``irusdk tags`` commands."""

import click

from ._console import print_json, print_table
from ._helpers import build_client, handle_errors

COLUMNS = ("id", "name")


@click.group("tags", short_help="Query and manage tags")
def tags() -> None:
    """Work with the tags defined in your tenant."""


@tags.command("list", short_help="List tags", options_metavar="<options>")
@click.option("--search", help="Only tags whose name matches this string.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def list_tags(obj: dict, search: str | None, as_json: bool) -> None:
    """List every tag in the tenant."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        rows = [t.model_dump(mode="json") for t in client.tags.list(search=search)]

    if as_json:
        print_json(rows)
        return
    print_table(rows, COLUMNS, f"Tags ({len(rows)})")


@tags.command("create", short_help="Create a tag", options_metavar="<options>")
@click.argument("name")
@click.pass_obj
@handle_errors
def create_tag(obj: dict, name: str) -> None:
    """Create a tag called NAME."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        tag = client.tags.create(name)

    click.echo(f"Created tag {tag.name} ({tag.id}).")


@tags.command("delete", short_help="Delete a tag", options_metavar="<options>")
@click.argument("tag_id")
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_obj
@handle_errors
def delete_tag(obj: dict, tag_id: str, yes: bool) -> None:
    """Delete the tag identified by TAG_ID."""
    if not yes:
        click.confirm(f"Delete tag {tag_id}?", abort=True)

    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        client.tags.delete(tag_id)

    click.echo(f"Deleted {tag_id}.")
