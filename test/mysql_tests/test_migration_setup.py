import os
import shutil
import unittest
from simple_migrator.utils import migration_tools
from simple_migrator.utils.cli import setup_cli, setup_migrator
from simple_migrator.utils.constants import *


class TestingMigrationSetup(unittest.TestCase):

    def test_setup_mysql_default_db_name(self):
        os.environ.setdefault(
                DATABASE_ENV_NAME_DEFAULT,
                "mysql://root:root@localhost:3306/test_db")
        migration_tool = setup_migrator(None, database_env_name=None)
        self.assertTrue(os.path.exists(
                os.path.join(
                    MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
                ))
        self.assertTrue(
                migration_tool.database.check_migrations_table_exists())
        # Cleanup
        if os.path.exists(MIGRATIONS_FOLDER_NAME):
            shutil.rmtree(MIGRATIONS_FOLDER_NAME)

    def test_setup_mysql_custom_db_name(self):
        db_env_name = "DB_ENV_NAME"
        os.environ.setdefault(
                db_env_name,
                "mysql://root:root@localhost:3306/test_db")
        migration_tool = setup_migrator(None, database_env_name=None)
        self.assertTrue(os.path.exists(
                os.path.join(
                    MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
                ))
        self.assertTrue(
                migration_tool.database.check_migrations_table_exists())

        # Cleanup
        if os.path.exists(MIGRATIONS_FOLDER_NAME):
            shutil.rmtree(MIGRATIONS_FOLDER_NAME)

if __name__ == '__main__':
    unittest.main()

