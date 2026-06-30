from typing import Any, NoReturn

import click

from aha.ui.console import console


def print_catalog_not_initialised() -> None:
    """Print a consistent themed message for missing catalog initialisation."""
    console.print("[warning]Aha catalog is not initialised.[/warning]")
    console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")


def exit_catalog_not_initialised() -> NoReturn:
    """Print missing-catalog guidance and terminate with exit code 2."""
    print_catalog_not_initialised()
    raise click.exceptions.Exit(2)
