from typing import List, Optional
import click
from dotenv import load_dotenv

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
@click.option(
    "--files",
    # type=List[str],
    help="List of files you want to migrate up. This won't check if the migrations is already applied and will apply it nonetheless.",
)
@click.pass_context
def up(ctx, files: Optional[List[str]]):
    """Apply migrations."""
    setup_cli("up")
    if files and type(files) != "list":
        files = [files]
    handle_cli_commands(ctx, files=files)
    # command = UpCommand(ctx.obj["path"], ctx.obj["database_config"])
    # command.execute()


@cli.command()
@click.option(
    "--files",
    type=List[str],
    help="List of files you want to rollback. This won't check the last runned migrations.",
)
@click.pass_context
def down(ctx, files):
    """Rollback migrations."""
    setup_cli("down")
    if files and type(files) != "list":
        files = [files]
    handle_cli_commands(ctx, files=files)
    # command = DownCommand(ctx.obj["path"], ctx.obj["database_config"])
    # command.execute()


@cli.command()
@click.argument(
    "mig_type",
    type=click.Choice(
        ["all", "applied", "failed", "last-applied", "pending"],
        case_sensitive=False,
    ),
    default="last-applied"
)
@click.pass_context
def list(ctx, mig_type: str):
    """List Migrations."""
    setup_cli("list")
    handle_cli_commands(ctx, mig_type=mig_type)


if __name__ == "__main__":
    cli()
