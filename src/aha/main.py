import click
from aha.commands.catalog.main import catalog
from aha.commands.helm.main import helm
from aha.commands.profiles.main import profiles
from aha.commands.templates.main import templates
from aha.commands.helpers.main import helpers


@click.group()
@click.pass_context
def cli(ctx):
    """AHA CLI helps you manage your HELM Chart templates by using profiles."""
    pass


cli.add_command(catalog)
cli.add_command(templates)
cli.add_command(profiles)
cli.add_command(helm)
cli.add_command(helpers)


if __name__ == "__main__":
    cli()
