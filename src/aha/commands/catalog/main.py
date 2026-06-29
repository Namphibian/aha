from __future__ import annotations

from pathlib import Path

import click
from rich.table import Table

from aha.library.catalog.manager import (
    AhaCatalogNotInitialisedException,
    get_catalog_branch,
    get_catalog_path,
    get_catalog_repo,
    require_catalog_root,
    catalog_manifest_exists,
    save_catalog_config,
)
from aha.library.constants import AHA_CONFIG_FILE, DEFAULT_CATALOG_DIR
from aha.library.git.manager import run_git_command, is_git_repository
from aha.ui.console import console


@click.group()
@click.pass_context
def catalog(ctx):
    """Manage the external templates and profiles catalog."""
    pass


@catalog.command(name="init")
@click.pass_context
@click.option(
    "--repo",
    "-r",
    required=True,
    type=str,
    help="Git repository URL for the Aha catalog.",
)
@click.option(
    "--path",
    "-p",
    "catalog_path",
    type=click.Path(path_type=Path),
    default=DEFAULT_CATALOG_DIR,
    show_default=True,
    help="Local path where the catalog should be cloned.",
)
@click.option(
    "--branch",
    "-b",
    default="main",
    show_default=True,
    help="Git branch to clone.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite catalog config if a catalog is already configured.",
)
def init(ctx, repo: str, catalog_path: Path, branch: str, force: bool):
    """Initialize the external catalog from a Git repository."""
    existing_catalog_path = get_catalog_path()

    if existing_catalog_path and existing_catalog_path.exists() and not force:
        console.print("[warning]A catalog is already configured.[/warning]")
        console.print(f"Current path: [path]{existing_catalog_path}[/path]")
        console.print(
            "Use [key]--force[/key] if you want to replace the catalog configuration."
        )
        raise click.exceptions.Exit(2)

    catalog_path = catalog_path.expanduser().resolve()

    if catalog_path.exists() and any(catalog_path.iterdir()):
        if not is_git_repository(catalog_path):
            console.print(
                f"[error]Target path exists and is not a Git repository:[/error] [path]{catalog_path}[/path]"
            )
            raise click.exceptions.Exit(2)

        console.print(
            f"[warning]Catalog path already exists:[/warning] [path]{catalog_path}[/path]"
        )
        console.print(
            "[info]Skipping clone and saving config for existing repository.[/info]"
        )
    else:
        catalog_path.parent.mkdir(parents=True, exist_ok=True)

        console.print(f"[info]Cloning catalog from[/info] [value]{repo}[/value]")
        console.print(f"[key]Target path:[/key] [path]{catalog_path}[/path]")

        result = run_git_command(
            ["clone", "--branch", branch, repo, str(catalog_path)],
        )

        if result.returncode != 0:
            console.print("[error]Failed to clone catalog repository.[/error]")
            console.print(result.stderr.strip())
            raise click.exceptions.Exit(1)

    if not catalog_manifest_exists(catalog_path):
        console.print(
            "[warning]Warning: catalog.yaml was not found in the catalog root.[/warning]"
        )
        console.print(
            "[subtle]The catalog was initialized, but you should add a catalog.yaml file.[/subtle]"
        )

    save_catalog_config(repo=repo, path=catalog_path, branch=branch)

    console.print("[success]Aha catalog initialized successfully.[/success]")
    console.print(f"[key]Config file:[/key] [path]{AHA_CONFIG_FILE}[/path]")
    console.print(f"[key]Catalog path:[/key] [path]{catalog_path}[/path]")


@catalog.command(name="update")
@click.pass_context
def update(ctx):
    """Pull the latest catalog changes from Git."""
    try:
        catalog_path = require_catalog_root()
    except AhaCatalogNotInitialisedException:
        console.print("[warning]No catalog is configured.[/warning]")
        console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")
        raise click.exceptions.Exit(2)

    if not is_git_repository(catalog_path):
        console.print(
            f"[error]Configured catalog path is not a Git repository:[/error] [path]{catalog_path}[/path]"
        )
        raise click.exceptions.Exit(2)

    console.print(f"[info]Updating catalog at[/info] [path]{catalog_path}[/path]")

    result = run_git_command(["pull", "--ff-only"], cwd=catalog_path)

    if result.returncode != 0:
        console.print("[error]Failed to update catalog.[/error]")
        console.print(result.stderr.strip())
        raise click.exceptions.Exit(1)

    output = result.stdout.strip()

    if output:
        console.print(output)

    console.print("[success]Catalog updated successfully.[/success]")


@catalog.command(name="status")
@click.pass_context
def status(ctx):
    """Show the current catalog configuration and Git status."""
    try:
        catalog_path = require_catalog_root()
    except AhaCatalogNotInitialisedException:
        console.print("[warning]No catalog is configured.[/warning]")
        console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")
        raise click.exceptions.Exit(2)

    repo = get_catalog_repo()
    branch = get_catalog_branch()

    table = Table(title="Aha Catalog Status")
    table.add_column("Property", style="key", no_wrap=True)
    table.add_column("Value", style="value")

    table.add_row("Config file", str(AHA_CONFIG_FILE))
    table.add_row("Repo", repo or "Not configured")
    table.add_row("Branch", branch or "Not configured")
    table.add_row("Path", str(catalog_path))
    table.add_row("Exists", "Yes")
    table.add_row("Git repository", "Yes" if is_git_repository(catalog_path) else "No")
    table.add_row(
        "catalog.yaml", "Yes" if catalog_manifest_exists(catalog_path) else "No"
    )

    console.print(table)

    if not is_git_repository(catalog_path):
        console.print(
            f"[error]Configured catalog path is not a Git repository:[/error] [path]{catalog_path}[/path]"
        )
        raise click.exceptions.Exit(2)

    result = run_git_command(["status", "--short", "--branch"], cwd=catalog_path)

    if result.returncode != 0:
        console.print("[error]Could not read Git status.[/error]")
        console.print(result.stderr.strip())
        raise click.exceptions.Exit(1)

    status_output = result.stdout.strip()

    if status_output:
        console.print()
        console.print("[key]Git status:[/key]")
        console.print(status_output)


@catalog.command(name="path")
@click.pass_context
def path(ctx):
    """Print the local catalog path."""
    try:
        catalog_path = require_catalog_root()
    except AhaCatalogNotInitialisedException:
        console.print("[warning]No catalog is configured.[/warning]")
        console.print("Run: [highlight]aha catalog init --repo <repo-url>[/highlight]")
        raise click.exceptions.Exit(2)

    console.print(f"[path]{catalog_path}[/path]")
