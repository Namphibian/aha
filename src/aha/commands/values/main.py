import click
from rich.syntax import Syntax
from rich.table import Table

from aha.library.catalog.manager import (
    list_value_files,
    get_values_data,
)
from aha.library.catalog.exceptions import (
    AhaCatalogNotInitialisedException,
    AhaCatalogDataException,
)
from aha.ui.console import console
from aha.ui.console_exception_helper import exit_catalog_not_initialised


def _list_values_or_exit() -> list[str]:
    try:
        return list_value_files()
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()


@click.group()
@click.pass_context
def values(ctx):
    """Manage values"""
    pass


@values.command(name="list")
@click.pass_context
def list_registered_values(ctx):
    """List all the values schemas currently in the system."""
    values_list = _list_values_or_exit()

    if not values_list:
        console.print("[warning]No values_list found.[/warning]")
        return

    table = Table(title="Registered values")
    table.add_column("#", justify="right", style="subtle", no_wrap=True)
    table.add_column("Template", style="value")

    for index, profile in enumerate(values_list, start=1):
        table.add_row(str(index), profile)

    console.print(table)


@values.command(name="get")
@click.pass_context
@click.argument("values")
def get(ctx, values: str):
    try:
        values_str, _ = get_values_data(values)
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)
    syntax = Syntax(values_str, "json", theme="nord-darker", line_numbers=True)
    console.print(syntax)
