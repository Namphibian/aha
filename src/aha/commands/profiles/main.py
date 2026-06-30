import click
from rich.syntax import Syntax
from rich.table import Table

from aha.library.catalog.manager import (
    get_profile_data,
    list_profiles,
)
from aha.library.catalog.exceptions import (
    AhaCatalogNotInitialisedException,
    AhaCatalogDataException,
)
from aha.library.constants import TEMPLATE_KEY
from aha.ui.console import console
from aha.ui.console_exception_helper import exit_catalog_not_initialised


@click.group()
@click.pass_context
def profiles(ctx):
    """Manage profiles"""
    pass


@profiles.group()
@click.pass_context
def create(ctx):
    pass


# top level added in main
@profiles.group()
@click.pass_context
def delete(ctx):
    pass


@profiles.command(name="get")
@click.pass_context
@click.argument("profile")
def get(ctx, profile: str):
    """Get and displays profile record details"""

    try:
        profile_str, _ = get_profile_data(profile)
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)

    syntax = Syntax(profile_str, "yaml", theme="nord-darker", line_numbers=True)
    console.print(syntax)


@profiles.command(name="list")
@click.pass_context
def list_registered_profiles(ctx):
    """List all registered profiles."""
    profiles_listed: list[str] = []
    try:
        profiles_listed = list_profiles()

        profile_data_map = {}
        if not profiles_listed:
            console.print("[warning]No profiles found.[/warning]")
            return

        for profile in profiles_listed:
            _, profile_data_map[profile] = get_profile_data(profile)
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)

    table = Table(title="Registered Profiles")
    table.add_column("Name", justify="left", style="key", no_wrap=True)
    table.add_column("Description", style="value")
    table.add_column("Mandatory Resource #", justify="right", style="info")
    table.add_column("Optional Resource #", justify="right", style="subtle")
    table.add_column("File Name", style="path")

    for k, v in profile_data_map.items():
        table.add_row(
            v["name"],
            v["description"],
            str(len(v[TEMPLATE_KEY]["mandatory"])),
            str(len(v[TEMPLATE_KEY]["optional"])),
            k,
        )
    console.print(table)
