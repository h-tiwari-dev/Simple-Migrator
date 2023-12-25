from typing import List, Optional, Tuple
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.sql import text
from .tables.base import Base
from .tables.constants import MIGRATIONS_TABLE_NAME
from .config import DatabaseConfig
from sqlalchemy import Engine, create_engine, orm


class DataBase(DatabaseConfig):
    database_config: DatabaseConfig
    engine: Engine

    def __init__(self, url: str):
        self.database_config = DatabaseConfig.create_from_values(url)
        self.engine = self.create_engine()
        self.Session = orm.sessionmaker(bind=self.engine)

    def check_migrations_table_exists(self) -> bool:
        conn = self.engine.connect()
        result = self.engine.dialect.has_table(conn, MIGRATIONS_TABLE_NAME)
        conn.close()
        return result

    def setup_table(self):
        print("Checking if migration table exists")
        does_migration_table_exists = self.check_migrations_table_exists()
        print(
            f"Migration table {'exists' if does_migration_table_exists else 'not exists'}"
        )
        if not does_migration_table_exists:
            print(f"Creating Table {MIGRATIONS_TABLE_NAME}")
            Base.metadata.create_all(self.engine)

    def create_engine(self):
        return create_engine(self.database_config.url)

    def execute_transactions(self, queries: List[str]):
        Session = scoped_session(self.Session)
        try:
            with Session.begin():
                for query in queries:
                    # print(f"QUERY_TEXT: {query}")
                    # print(f"QUERY: {text(query)}")
                    Session.execute(text(query))
            result = True
        except Exception as e:
            # Rollback the transaction if there was an error
            Session.rollback()
            print(f"Error occured {e}")
            result = False
        finally:
            Session.close()

        return result
