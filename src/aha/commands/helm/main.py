import click
from typing import NoReturn

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
)
from aha.library.catalog.manager import get_profile_data
from aha.ui.console import console


def _print_catalog_not_initialised() -> None:
    console.print("[warning]Aha catalog is not initialised.[/warning]")
    console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")


def _exit_catalog_not_initialised() -> NoReturn:
    _print_catalog_not_initialised()
    raise click.exceptions.Exit(2)


@click.group()
@click.pass_context
def helm(ctx):
    """Work with Helm."""
    pass


@helm.group()
@click.pass_context
def generate(ctx):
    """Generate a Helm resource"""
    pass


@generate.command("chart")
@click.pass_context
@click.option("--name", "-n", type=str, required=True)
@click.option("--profile", "-p", type=str, required=True)
@click.option("--output-path", "-o", type=str, required=True)
def chart(ctx, name: str, profile: str, output_path: str):
    """Generate a Helm chart"""
    try:
        profile_str, profile_data = get_profile_data(profile)
    except AhaCatalogNotInitialisedException:
        _exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)
