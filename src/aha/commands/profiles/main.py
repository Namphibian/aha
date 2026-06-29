import click
from rich.syntax import Syntax
from rich.table import Table
from typing import NoReturn

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
    get_profile_data,
    list_profiles,
)
from aha.ui.console import console


def _print_catalog_not_initialised() -> None:
    console.print("[warning]Aha catalog is not initialised.[/warning]")
    console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")


def _exit_catalog_not_initialised() -> NoReturn:
    _print_catalog_not_initialised()
    raise click.exceptions.Exit(2)


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
    profile_str = ""
    try:
        profile_str, _ = get_profile_data(profile)
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()
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
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()

    profile_data_map = {}
    if not profiles_listed:
        console.print("[warning]No profiles found.[/warning]")
        return

    try:
        for profile in profiles_listed:
            _, profile_data_map[profile] = get_profile_data(profile)
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()
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
            str(len(v["resources"]["mandatory"])),
            str(len(v["resources"]["optional"])),
            k,
        )
    console.print(table)
