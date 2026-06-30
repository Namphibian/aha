"""Top-level CLI entrypoint for the Aha command-line application.

This module defines the root Click command group and registers all domain
subcommands that make up the public CLI surface.
"""

import click
from aha.commands.catalog.main import catalog
from aha.commands.helm.main import helm
from aha.commands.profiles.main import profiles
from aha.commands.templates.main import templates
from aha.commands.helpers.main import helpers
from aha.commands.values.main import values


@click.group()
@click.pass_context
def cli(ctx):
    """Aha root CLI group.

    This is the command hub that delegates to subcommand groups for catalog,
    templates, profiles, helm, and helpers workflows.

    Args:
        ctx: Click invocation context for the current command execution.
    """
    pass


# Register command groups on the root CLI.
cli.add_command(catalog)
cli.add_command(templates)
cli.add_command(profiles)
cli.add_command(helm)
cli.add_command(helpers)
cli.add_command(values)


if __name__ == "__main__":
    # Allow module execution via: python -m aha.main
    cli()
