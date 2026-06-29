import click
from rich.syntax import Syntax
from rich.table import Table
from typing import NoReturn

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
    get_template_data,
    list_templates,
)
from aha.ui.console import console


def _print_catalog_not_initialised() -> None:
    console.print("[warning]Aha catalog is not initialised.[/warning]")
    console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")


def _exit_catalog_not_initialised() -> NoReturn:
    _print_catalog_not_initialised()
    raise click.exceptions.Exit(2)


def _list_templates_or_exit() -> list[str]:
    try:
        return list_templates()
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()


@click.group()
@click.pass_context
def templates(ctx):
    """Manage templates"""
    pass


@templates.command(name="list")
@click.pass_context
def list_registered_templates(ctx):
    """List all the templates_list currently in the system."""
    templates_list = _list_templates_or_exit()

    if not templates_list:
        console.print("[warning]No templates_list found.[/warning]")
        return

    table = Table(title="Registered Templates")
    table.add_column("#", justify="right", style="subtle", no_wrap=True)
    table.add_column("Template", style="value")

    for index, profile in enumerate(templates_list, start=1):
        table.add_row(str(index), profile)

    console.print(table)


@templates.command(name="get")
@click.pass_context
@click.argument("template")
def get(ctx, template: str):
    try:
        template_str = get_template_data(template)
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)
    syntax = Syntax(template_str, "yaml+jinja", theme="nord-darker", line_numbers=True)
    console.print(syntax)
