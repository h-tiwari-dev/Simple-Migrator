from simple_migrator.database.config import DatabaseConfig
from .database.database_type import DatabaseType
from simple_migrator.migrations_query.base import BaseQuery


class AddMigrationQuery(BaseQuery):
    def get_query(self):
        super().get_query()
        if self.database_type == DatabaseType.MYSQL:
            return
        elif self.database_type == DatabaseType.POSTGRESQL:
            pass
