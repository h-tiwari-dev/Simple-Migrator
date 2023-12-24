from simple_migrator.database.config import DatabaseConfig


class BaseQuery(DatabaseConfig):
    def __init__(self):
        pass

    def get_query(self):
        pass
