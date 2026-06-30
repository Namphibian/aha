"""Helpers command group for the Aha CLI.

This module provides helper-oriented catalog commands:

- `aha helpers list`: list helper files available in the configured catalog.
- `aha helpers get <helper>`: display helper file content with syntax highlighting.

The command group enforces the same catalog-initialisation and exit-code behavior
used across the CLI:
- exits with code `2` for catalog/config/data precondition failures.
"""

import click
from rich.syntax import Syntax
from rich.table import Table

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
    get_helper_data,
    list_helpers,
)
from aha.ui.console import console
from aha.ui.console_exception_helper import exit_catalog_not_initialised


def _list_helpers_or_exit() -> list[str]:
    """Return helper file names, or exit with code 2 when catalog is unavailable.

    Returns:
        list[str]: Sorted helper file names discovered in the catalog helpers folder.

    Raises:
        click.exceptions.Exit: Always raised with code `2` if catalog is not
            initialised/valid.
    """
    try:
        return list_helpers()
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()


@click.group()
@click.pass_context
def helpers(ctx):
    """Manage helper files from the configured catalog."""
    pass


@helpers.command(name="list")
@click.pass_context
def list_registered_helpers(ctx):
    """List all helper files currently available in the catalog."""
    helpers_list = _list_helpers_or_exit()

    if not helpers_list:
        console.print("[warning]No helpers found.[/warning]")
        return

    table = Table(title="Registered Helpers")
    table.add_column("#", justify="right", style="subtle", no_wrap=True)
    table.add_column("Helper", style="value")

    for index, profile in enumerate(helpers_list, start=1):
        table.add_row(str(index), profile)

    console.print(table)


@helpers.command(name="get")
@click.pass_context
@click.argument("helper")
def get(ctx, helper: str):
    """Fetch and display a helper file by name.

    Args:
        helper: Helper file name (with or without suffix, depending on catalog
            resolution rules).

    Failure behavior:
        - Exits `2` when catalog is not initialised.
        - Exits `2` when helper data validation/loading fails (e.g., missing file
          or invalid file type), after printing a themed error.
    """
    try:
        helper_str: str = get_helper_data(helper)
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)

    syntax = Syntax(helper_str, "yaml+jinja", theme="nord-darker", line_numbers=True)
    console.print(syntax)
