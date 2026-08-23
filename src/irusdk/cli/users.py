"""``irusdk users`` commands."""

import itertools

import click

from ._console import print_json, print_record, print_table
from ._helpers import build_client, handle_errors

LIST_COLUMNS = ("id", "name", "email", "device_count", "active", "archived")
DETAIL_COLUMNS = (*LIST_COLUMNS, "department", "job_title", "created_at", "updated_at")


@click.group("users", short_help="Query users")
def users() -> None:
    """Work with the users known to your tenant."""


@users.command("list", short_help="List users", options_metavar="<options>")
@click.option("--email", help="Only the user with this email address.")
@click.option("--archived/--not-archived", default=None, help="Filter on archived state.")
@click.option("--limit", type=int, help="Stop after this many users.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def list_users(
    obj: dict, email: str | None, archived: bool | None, limit: int | None, as_json: bool
) -> None:
    """List users, following the API's cursor until every page is read."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        results = client.users.list(email=email, archived=archived)
        found = list(itertools.islice(results, limit) if limit else results)

    rows = [u.model_dump(mode="json") for u in found]
    if as_json:
        print_json(rows)
        return
    print_table(rows, LIST_COLUMNS, f"Users ({len(rows)})")


@users.command("get", short_help="Show one user", options_metavar="<options>")
@click.argument("user_id")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON instead of a table.")
@click.pass_obj
@handle_errors
def get_user(obj: dict, user_id: str, as_json: bool) -> None:
    """Show a single user by their USER_ID."""
    with build_client(obj["subdomain"], obj["token"], obj["region"]) as client:
        user = client.users.get(user_id)

    row = user.model_dump(mode="json")
    if as_json:
        print_json(row)
        return
    print_record(row, DETAIL_COLUMNS, "User")
