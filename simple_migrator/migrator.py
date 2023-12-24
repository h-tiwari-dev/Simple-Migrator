import click
from dotenv import load_dotenv
from sqlalchemy import desc

from simple_migrator.utils.cli import handle_cli_commands, setup_cli

# Load the environment variables from the .env file
load_dotenv()


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = {}


@cli.command()
@click.argument("database_url", type=str, required=True)
@click.pass_context
def setup(ctx, database_url: str):
    """Create a new migration."""
    setup_cli("setup")
    handle_cli_commands(ctx, url=database_url)


@cli.command()
@click.argument("migration-name", type=str)
@click.option(
    "--description",
    type=str,
    help="Add a migration description to be saved in your migration file",
)
@click.pass_context
def create(ctx, migration_name: str, description: str):
    """Create a new migration."""
    setup_cli("create")
    handle_cli_commands(ctx, migration_name=migration_name, description=description)


@cli.command()
@click.pass_context
def up(ctx):
    """Apply migrations."""
    setup_cli("up")
    handle_cli_commands(ctx)
    # command = UpCommand(ctx.obj["path"], ctx.obj["database_config"])
    # command.execute()


@cli.command()
@click.pass_context
def down(ctx):
    """Rollback migrations."""
    setup_cli("down")
    handle_cli_commands(ctx)
    # command = DownCommand(ctx.obj["path"], ctx.obj["database_config"])
    # command.execute()


if __name__ == "__main__":
    cli()
