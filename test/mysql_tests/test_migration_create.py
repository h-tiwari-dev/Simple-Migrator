import os
import unittest
from simple_migrator.database.tables.constants import MIGRATIONS_TABLE_NAME
from simple_migrator.database.tables.migrations_table import MigrationsTable
from simple_migrator.utils.cli import create_migration 
from simple_migrator.utils.constants import *
from simple_migrator.utils.migration_tools import MigrationTool
from test.mysql_tests.test_migration_setup import TestingMigrationSetup


class TestingMigrationCreate(unittest.TestCase):
    migration_tool: MigrationTool = TestingMigrationSetup.setup_test_migrations()

    def test_create_migration(self):
        file_name, file_path = create_migration(
                None, migration_name="TEST_MIG_NAME", description=None)
        self.assertTrue(os.path.exists(file_path))

        with self.migration_tool.database.Session() as session:
            query_result = (
                session.query(MigrationsTable.name)
                .filter(MigrationsTable.name.in_([file_name]))
                .all()
            )
            database_file_names = [value for (value,) in query_result]
            self.assertTrue(len(database_file_names) >= 1)
        # Cleanup
        all_files = os.listdir(MIGRATIONS_FOLDER_NAME)
        for file_name in all_files:
            file_path = os.path.join(MIGRATIONS_FOLDER_NAME, file_name)
        
            # Check if the file is not ".config" and is a file (not a directory)
            if file_name != ".config" and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_name}")

        self.migration_tool.database.execute_transactions([f"DELETE FROM {MIGRATIONS_TABLE_NAME}"])


if __name__ == '__main__':
    unittest.main()
