import functools
from typing import Callable

from simple_migrator.database.config import DatabaseConfig
from simple_migrator.utils.migration_tools import MigrationTool


def check_unsynced_migrations(func: Callable):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        migration_tool = MigrationTool(DatabaseConfig.create_from_config_file())
        is_unsynced, unsynced_files, unsynced_db_entries = migration_tool.get_unsynced()

        if is_unsynced:
            raise Exception(f"""Migration is unsynced from the database.
                  Please run migration sync to sync your migrations\n
                  The following migrations are unsynced:- \n
                  {unsynced_files} \n
                  {unsynced_db_entries}
                  """)
        else:
            # If everything is in sync, proceed with the original function
            return func(self, *args, **kwargs, migration_tool=migration_tool)
    return wrapper
