"""Terminal output for the CLI.

All Rich usage is confined here so importing the library never pulls in a console.
"""

import json
from typing import Any, Sequence

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# Semantic palette: call sites name the intent, this owns the colors.
_THEME = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "muted": "dim",
    }
)

# Title-casing mangles the acronyms the API uses; these win over the default.
_LABELS = {
    "device_id": "Device ID",
    "blueprint_id": "Blueprint ID",
    "library_item_id": "Library Item ID",
    "tag_id": "Tag ID",
    "user_id": "User ID",
    "os_version": "OS Version",
    "mdm_enabled": "MDM Enabled",
    "cve_id": "CVE ID",
}

console = Console(theme=_THEME)
err_console = Console(stderr=True, theme=_THEME)


def print_json(payload: Any) -> None:
    """
    Emit a payload as indented JSON on stdout.

    :param payload: Anything :func:`json.dumps` can serialize, with a ``default`` of ``str``.
    """
    console.print_json(json.dumps(payload, default=str))


def print_table(rows: Sequence[dict[str, Any]], columns: Sequence[str], title: str) -> None:
    """
    Render rows as a Rich table.

    :param rows: One dict per row, keyed by column name.
    :param columns: Column names, in display order.
    :param title: The table's title.
    """
    if not rows:
        console.print(f"[muted]No {title.lower()} found.[/muted]")
        return

    table = Table(title=title, title_justify="left", header_style="info")
    for column in columns:
        table.add_column(label(column), overflow="fold")

    for row in rows:
        table.add_row(*[_cell(row.get(column)) for column in columns])

    console.print(table)


def print_record(row: dict[str, Any], columns: Sequence[str], title: str) -> None:
    """
    Render one record as a vertical field/value table.

    A single record laid out across many columns is unreadable in an 80-column terminal, so
    detail views go down the page rather than across it.

    :param row: The record to render.
    :param columns: Field names, in display order.
    :param title: The table's title.
    """
    table = Table(title=title, title_justify="left", show_header=False, box=None, pad_edge=False)
    table.add_column("Field", style="info", no_wrap=True)
    table.add_column("Value", overflow="fold")

    for column in columns:
        table.add_row(label(column), _cell(row.get(column)))

    console.print(table)


def print_error(message: str) -> None:
    """Emit an error on stderr."""
    err_console.print(f"[error]Error:[/error] {message}")


def label(column: str) -> str:
    """
    Turn a field name into a column heading.

    :param column: The snake_case field name.
    :rtype: str
    """
    return _LABELS.get(column, column.replace("_", " ").title())


def _cell(value: Any) -> str:
    if value is None or value == "":
        return "[muted]—[/muted]"
    if isinstance(value, bool):
        return "[success]yes[/success]" if value else "[muted]no[/muted]"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "[muted]—[/muted]"
    return str(value)
