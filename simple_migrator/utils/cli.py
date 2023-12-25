# migration_tool/utils/cli.py
from typing import List, Optional
import click
import os
from simple_migrator.database.config import DatabaseConfig
from simple_migrator.database.tables.migrations_table import MigrationStatus
from simple_migrator.utils.migration_tools import MigrationTool


def setup_migrator(ctx, url):
    print(ctx)
    migration_tool = MigrationTool(DatabaseConfig.create_from_values(url))
    migration_tool.print_migration_info("setup")
    migration_tool.setup()
    migration_tool.database.setup_table()


def create_migration(ctx, migration_name: str, description: Optional[str]):
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    migration_tool.print_migration_info("create")
    file_name, file_path = migration_tool.create_migration_file(
        migration_name=migration_name
    )
    migration_tool.save_migration(file_name, description)
    print(file_name, file_path)


def apply_migrations():
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    migration_tool.print_migration_info("up")
    migration_files = migration_tool.get_migrations("up")
    print(f"Going to run the following migrations:\n {','.join(migration_files)}")
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
            print(f"Migraiton {migration[0]} completed")
            migration_tool.update_migration(migration[0], MigrationStatus.APPLIED)
        else:
            print(f"Migraiton {migration[0]} failed")
            migration_tool.update_migration(migration[0], MigrationStatus.FAILED)

    if len(up_migrations) != len(migration_files):
        print(
            f"These migrations could not be runned. {list(map(lambda x: x in migration_files, valid_migrations_name))}"
        )
    else:
        print("All Up migration runned successfully.")


def rollback_migrations():
    migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
    migration_tool.print_migration_info("down")
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


def handle_cli_commands(ctx, **kwargs):
    if ctx.obj["command"] == "setup":
        setup_migrator(ctx, **kwargs)
    elif ctx.obj["command"] == "create":
        create_migration(ctx, **kwargs)
    elif ctx.obj["command"] == "up":
        apply_migrations()
    elif ctx.obj["command"] == "down":
        rollback_migrations()
    else:
        click.echo(f"Unknown command:")


@click.pass_context
def setup_cli(ctx, command):
    ctx.obj["command"] = command
    ctx.obj["current_dir"] = os.getcwd()
