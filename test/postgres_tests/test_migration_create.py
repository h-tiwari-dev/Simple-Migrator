import os
import unittest
from simple_migrator.database.tables.migrations_table import MigrationsTable
from simple_migrator.utils.cli import create_migration 
from simple_migrator.utils.constants import *
from test.postgres_tests.test_migration_setup import TestingMigrationSetup


class TestingMigrationCreate(unittest.TestCase):
    migration_tool = TestingMigrationSetup.setup_test_migrations()

    def test_create_migration(self):
        file_name, file_path = create_migration(
                None, migration_name="TEST_MIG_NAME", description=None)
        self.assertTrue(os.path.exists(file_path))

        with self.migration_tool.database.Session() as session:
            query_result = (
                session.query(MigrationsTable.name)
                .filter_by(name=MigrationsTable.name.in_([file_name]))
                .all()
            )
            database_file_names = [value for (value,) in query_result]
            self.assertTrue(len(database_file_names) >= 1)

if __name__ == '__main__':
    unittest.main()
