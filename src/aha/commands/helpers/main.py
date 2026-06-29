import click
from rich.syntax import Syntax
from rich.table import Table
from typing import NoReturn

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
    get_helper_data,
    list_helpers,
)
from aha.ui.console import console


def _print_catalog_not_initialised() -> None:
    console.print("[warning]Aha catalog is not initialised.[/warning]")
    console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")


def _exit_catalog_not_initialised() -> NoReturn:
    _print_catalog_not_initialised()
    raise click.exceptions.Exit(2)


def _list_helpers_or_exit() -> list[str]:
    try:
        return list_helpers()
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()


@click.group()
@click.pass_context
def helpers(ctx):
    """Manage helpers"""
    pass


@helpers.command(name="list")
@click.pass_context
def list_registered_helpers(ctx):
    """List all helpers currently in the system."""
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
    try:
        helper_str: str = get_helper_data(helper)
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)
    syntax = Syntax(helper_str, "yaml+jinja", theme="nord-darker", line_numbers=True)
    console.print(syntax)
