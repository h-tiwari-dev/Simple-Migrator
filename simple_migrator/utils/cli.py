from typing import List, Optional
import click
import os

from colored import fg, bg, attr
from sqlalchemy.sql.sqltypes import String
from simple_migrator.database.config import DatabaseConfig
from simple_migrator.database.tables.migrations_table import MigrationStatus
from prettytable import PrettyTable

from simple_migrator.utils.migration_tools import MigrationTool


def setup_migrator(ctx, url):
    migration_tool = MigrationTool(DatabaseConfig.create_from_values(url))
    migration_tool.setup()
    migration_tool.database.setup_table()


def create_migration(ctx, migration_name: str, description: Optional[str]):
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    file_name, file_path = migration_tool.create_migration_file(
        migration_name=migration_name
    )
    migration_tool.save_migration(file_name, description)
    print(f"Migration {fg("green")}{file_path}{attr("reset")} created at {fg("green")}{file_path}{attr("reset")}")


def apply_migrations(ctx, files: Optional[List[str]]):
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    migration_files: List[str] = []

    if files and len(files) != 0:
        migration_tool.validate_migrations_from_file_name(files)
        migration_files = files
    else:
        migration_files = [mig.name for mig in migration_tool.get_migrations("pending")]

    print(f"Going to run the following migrations:\n {fg("green")}{','.join(migration_files)}{attr("reset")}")
    up_migrations = list(
        filter(
            lambda x: len(x[1]) != 0,
            [(mig, migration_tool.extract_migration(mig)) for mig in migration_files],
        )
    )
    valid_migrations_name = list(map(lambda x: x[0], up_migrations))
    migration_tool.group_migrations(valid_migrations_name)

    for migration in up_migrations:
        result = migration_tool.database.execute_transactions(migration[1])
        if result:
            print(f"{fg("blue")}Migraiton {migration[0]}: {attr("reset")}{fg("green")}COMPLETED{attr("reset")}")
            migration_tool.update_migration(migration[0], MigrationStatus.APPLIED)
        else:
            print(f"Migraiton {migration[0]}: {fg("red")}FAILED{attr("reset")}")
            migration_tool.update_migration(migration[0], MigrationStatus.FAILED)

    if len(up_migrations) != len(migration_files):
        print(
            f"These migrations could not be runned. \n{fg("red")}{"\n".join(list(filter(lambda x: x in migration_files, valid_migrations_name)))}{attr("reset")}"
        )
    else:
        print("All Up migration runned successfully.")


def rollback_migrations(ctx, files: Optional[List[str]]):
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    last_runned_migrations = []

    if files and len(files) != 0:
        migration_tool.validate_migrations_from_file_name(files)
        last_runned_migrations = files
    else:
        last_runned_migrations = migration_tool.get_last_runned_migrations()
    print(
        f"Going to run the following migrations:\n {[mig for mig in last_runned_migrations]}"
    )
    down_migrations = list(
        filter(
            lambda x: len(x[1]) != 0,
            [
                (mig, migration_tool.extract_migration(mig, "down"))
                for mig in last_runned_migrations
            ],
        )
    )
    valid_migrations_name: List[str] = list(map(lambda x: x[0], down_migrations))
    migration_tool.group_migrations(valid_migrations_name)
    for migration in down_migrations:
        result = migration_tool.database.execute_transactions(migration[1])
        if result:
            print(f"Rollback Migraiton {migration[0]} completed")
            migration_tool.update_migration(migration[0], MigrationStatus.PENDING)
        else:
            print(f"Rollback Migraiton {migration[0]} failed")
            # migration_tool.update_migration(migration[0], MigrationStatus.FAILED)

    if len(down_migrations) != len(last_runned_migrations):
        print(
            f"These migrations rollback could not be runned. {list(map(lambda x: x in down_migrations, last_runned_migrations))}"
        )
    else:
        print("All migration rollback successfully.")


def list_migrations(ctx, mig_type: str):
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    migrations = migration_tool.get_migrations(mig_type)

    table = PrettyTable()
    # Define table headers
    table.field_names = ["Name", "Status", "Applied At"]
    # Add data to the table
    for mig in migrations:
        table.add_row([mig.name, mig.status, mig.applied_at])
    print(table)


def handle_cli_commands(ctx, **kwargs):
    if ctx.obj["command"] == "setup":
        setup_migrator(ctx, **kwargs)
    elif ctx.obj["command"] == "create":
        create_migration(ctx, **kwargs)
    elif ctx.obj["command"] == "up":
        apply_migrations(ctx, **kwargs)
    elif ctx.obj["command"] == "down":
        rollback_migrations(ctx, **kwargs)
    elif ctx.obj["command"] == "list":
        list_migrations(ctx, **kwargs)
    else:
        click.echo(f"Unknown command:")


@click.pass_context
def setup_cli(ctx, command):
    ctx.obj["command"] = command
    ctx.obj["current_dir"] = os.getcwd()
