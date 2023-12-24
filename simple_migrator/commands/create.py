# migration_tool/commands/create.py
from .base import BaseCommand

class CreateCommand(BaseCommand):
    def get_query(self, migration_name: str):
        print(f"Creating a new migration for database at {self.path}, "
              f"using database name: {self.database_config.name}, "
              f"URL: {self.database_config.url},"
              f"Migration Name: {migration_name},"
              )
        # Add actual create migration logic here
        query = """
        CREATE TABLE IF NOT EXISTS your_table_name (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255)
        );
        """
        return query
