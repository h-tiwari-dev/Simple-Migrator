import os
import shutil
import unittest

from sqlalchemy import MetaData
from simple_migrator.database.tables.constants import MIGRATIONS_TABLE_NAME
from simple_migrator.utils.cli import setup_migrator
from simple_migrator.utils.constants import *


class TestingMigrationSetup(unittest.TestCase):

    @staticmethod
    def setup_test_migrations(
            database_env_name: str = DATABASE_ENV_NAME_DEFAULT
            ):
        os.environ.setdefault(
                database_env_name,
                "postgresql://root:root@localhost:5432/test_db")
        if database_env_name is not DATABASE_ENV_NAME_DEFAULT:
            return setup_migrator(None, database_env_name=None)
        else:
            return setup_migrator(None, database_env_name=database_env_name)

    def test_setup_default_db_name(self):
        migration_tool = self.setup_test_migrations()
        self.assertTrue(os.path.exists(
                os.path.join(
                    MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
                ))
        self.assertTrue(
                migration_tool.database.check_migrations_table_exists())
        # Cleanup
        if os.path.exists(MIGRATIONS_FOLDER_NAME):
            shutil.rmtree(MIGRATIONS_FOLDER_NAME)
        migration_tool.database.execute_transactions([f"DROP TABLE {MIGRATIONS_TABLE_NAME}"])


    def test_setup_custom_db_name(self):
        db_env_name = "DB_ENV_NAME"
        migration_tool = self.setup_test_migrations(database_env_name=db_env_name)
        self.assertTrue(os.path.exists(
                os.path.join(
                    MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
                ))
        self.assertTrue(
                migration_tool.database.check_migrations_table_exists())

        # Cleanup
        if os.path.exists(MIGRATIONS_FOLDER_NAME):
            shutil.rmtree(MIGRATIONS_FOLDER_NAME)
        migration_tool.database.execute_transactions([f"DROP TABLE {MIGRATIONS_TABLE_NAME}"])

if __name__ == '__main__':
    unittest.main()

