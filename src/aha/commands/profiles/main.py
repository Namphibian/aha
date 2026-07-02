import click
from rich.syntax import Syntax
from rich.table import Table

from aha.library.catalog.manager import (
    get_profile_data_for_profile_file,
    list_profile_files,
    prepare_profile_data_map,
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
        profile_str, _ = get_profile_data_for_profile_file(profile)
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
    try:
        profile_data_map = prepare_profile_data_map()
    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)
    except Exception as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)

    table = Table(title="Registered Profiles")
    table.add_column("File Name", style="path")
    table.add_column("Name", justify="left", style="key", no_wrap=True)
    table.add_column("Description", style="value")
    table.add_column("Mandatory Resource #", justify="right", style="info")
    table.add_column("Optional Resource #", justify="right", style="subtle")


    for k, v in profile_data_map.items():
        table.add_row(
            k,
            v["name"],
            v["description"],
            str(len(v[TEMPLATE_KEY]["mandatory"])),
            str(len(v[TEMPLATE_KEY]["optional"])),

        )
    console.print(table)
