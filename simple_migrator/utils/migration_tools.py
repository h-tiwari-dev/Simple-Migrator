from datetime import datetime
import re
from typing import List, Optional, Tuple

from simple_migrator.database.config import (
    DatabaseConfig
)
from simple_migrator.database.database_class import (
    DataBase
)
from simple_migrator.database.tables.migrations_table import (
    MigrationStatus,
    MigrationsTable,
)

from .constants import (
    CREATE_DOWN_START_MIGRATIONS,
    CREATE_UP_START_MIGRATIONS,
    END_MIGRATIONS,
    MIGRATIONS_CONFIG_FILE_NAME,
    MIGRATIONS_FOLDER_NAME,
)
import os
import time


class MigrationTool:
    def __init__(self, database_config: DatabaseConfig):
        self.database_config = database_config
        self.database = DataBase(url=database_config.url)

    @staticmethod
    def setup(db_env_name: Optional[str]):
        # Check if the folder existsmysql://root:Julia%401984@localhost:3306/test_db
        if not os.path.exists(MIGRATIONS_FOLDER_NAME):
            # If not, create the folder
            os.makedirs(MIGRATIONS_FOLDER_NAME)
            print(f"Migration folder '{MIGRATIONS_FOLDER_NAME}' created.")

        file_path = os.path.join(
            MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
        print("File_path", file_path)
        database_config = DatabaseConfig.setup_db_config(
            db_env_name=db_env_name)
        return MigrationTool(database_config)

    def get_unsynced(self):
        db_migrations = self.get_migrations("all")
        files = [f for f in os.listdir(MIGRATIONS_FOLDER_NAME)
                 if f != ".config" and os.path.isfile(os.path.join(MIGRATIONS_FOLDER_NAME, f))]

        unsynced_files = []
        unsynced_db_entries = {}
        is_unscynced = False

        # Add new migrations to the database
        for file in files:
            migration_name = file
            if migration_name not in [str(m.name) for m in db_migrations]:
                print(migration_name, [str(m.name) for m in db_migrations])
                is_unscynced = True
                unsynced_files.append(migration_name)

        # Remove database migrations that don't have corresponding files
        for migration in db_migrations:
            if migration.name not in [f for f in files]:
                print(migration.name)
                is_unscynced = True
                unsynced_db_entries[str(migration.name)] = migration

        return (is_unscynced, unsynced_files, unsynced_db_entries)

    def sync_migrations(self, migration_status: MigrationStatus = MigrationStatus.APPLIED):
        is_unscynced, unsynced_files, unsynced_db_entries = self.get_unsynced()
        if not is_unscynced:
            print("Database is scynced")

        # Add new migrations to the database
        for file in unsynced_files:
            self.save_migration(file, description="" ,migration_status=migration_status)

        # Remove database migrations that don't have corresponding files
        for key, _ in unsynced_db_entries.items():
            self.remove_migration(str(key))

        print("Scyncing completed")

    @staticmethod
    def create_migration_name(file_name: str) -> str:
        return f"{time.time_ns()}_{file_name}.sql"

    def create_migration_file(self, migration_name: str) -> Tuple[str, str]:
        file_name = MigrationTool.create_migration_name(migration_name)
        file_path = os.path.join(MIGRATIONS_FOLDER_NAME, file_name)
        with open(file_path, "w") as file:
            file.writelines(
                [
                    CREATE_UP_START_MIGRATIONS,
                    "\n" * 5,
                    END_MIGRATIONS,
                    "\n" * 2,
                    CREATE_DOWN_START_MIGRATIONS,
                    "\n" * 5,
                    END_MIGRATIONS,
                ]
            )
        return file_name, file_path

    def remove_migration(self, migration_name: str):
        with self.database.Session() as session:
            migration = session.query(MigrationsTable).filter_by(
                name=migration_name).first()
            if migration:
                session.delete(migration)
                session.commit()

    def save_migration(self, file_name: str, description: Optional[str], migration_status=MigrationStatus.PENDING):
        with self.database.Session() as session:
            new_row = MigrationsTable(
                name=file_name, description=description, status=migration_status)
            session.add(new_row)
            session.commit()
            session.close()

    def update_migrations(self, file_names: List[str], migration_status: MigrationStatus):
        with self.database.Session() as session:
            try:
                migrations = session.query(MigrationsTable).filter(MigrationsTable.name.in_(file_names)).all()
                for migration in migrations:
                    if migration_status is MigrationStatus.APPLIED:
                        migration.status = MigrationStatus.APPLIED
                    elif migration_status is MigrationStatus.FAILED:
                        migration.status = MigrationStatus.FAILED
                    elif migration_status is MigrationStatus.PENDING:
                        migration.status = MigrationStatus.PENDING 
                        
                    migration.applied_at = datetime.now()
                session.commit()
                session.close()
            except Exception as e:
                print(f"Error: {e}")

    def update_migration(self, file_name: str, migration_status: MigrationStatus):
        with self.database.Session() as session:
            migration = session.query(MigrationsTable).filter_by(
                name=file_name).first()
            if migration:
                migration.status = migration_status
                migration.applied_at = datetime.now()
            session.commit()
            session.close()

    def validate_migrations_from_file_name(self, file_names: List[str]):
        non_existent_files = [file for file in file_names if not os.path.exists(
            os.path.join(MIGRATIONS_FOLDER_NAME, file))]
        if len(non_existent_files) != 0:
            raise Exception(
                f"Following migrations files does not exists: \n{non_existent_files}\n Are you sure the names are correct?"
            )
        with self.database.Session() as session:
            query_result = (
                session.query(MigrationsTable.name)
                .filter(MigrationsTable.name.in_(file_names))
                .all()
            )
            database_file_names = [value for (value,) in query_result]
            if len(database_file_names) == 0:
                print(
                    f"Could not find the following migrations in the database {database_file_names}. CREATING THEM."
                )
                for database_file_name in database_file_names:
                    self.save_migration(database_file_name, "")

    def group_migrations(self, migrations_name: List[str]):
        new_group_val = datetime.now()
        with self.database.Session() as session:
            migrations = (
                session.query(MigrationsTable)
                .filter(MigrationsTable.name.in_(migrations_name))
                .all()
            )
            if migrations:
                for mig in migrations:
                    mig.date_time_group = new_group_val
            session.commit()
            session.close()

    def get_last_runned_migrations(self) -> List[str]:
        with self.database.Session() as session:
            # Use group_by, func.max, and order_by to get a list of MyModel objects
            # grouped by datetime and sorted within each group
            max_group_value = (
                session.query(MigrationsTable)
                .filter_by(status=MigrationStatus.APPLIED)
                .order_by(MigrationsTable.date_time_group.desc())
                .first()
            )
            if max_group_value:
                grouped_and_sorted_objects = (
                    session.query(MigrationsTable.name)
                    .filter_by(date_time_group=max_group_value.date_time_group)
                    .all()
                )
                return [value for (value,) in grouped_and_sorted_objects]

            return []

    def get_migrations(self, mig_type: str) -> List[MigrationsTable]:
        with self.database.Session() as session:
            # Use group_by, func.max, and order_by to get a list of MyModel objects
            # grouped by datetime and sorted within each group
            if mig_type == "last-applied":
                max_group_value = (
                    session.query(MigrationsTable)
                    .filter_by(status=MigrationStatus.APPLIED)
                    .order_by(MigrationsTable.date_time_group.desc())
                    .first()
                )
                if max_group_value:
                    grouped_and_sorted_objects = (
                        session.query(MigrationsTable)
                        .filter_by(date_time_group=max_group_value.date_time_group)
                        .all()
                    )
                    return grouped_and_sorted_objects
                return []
            if mig_type == "all":
                result = (
                    session.query(MigrationsTable)
                    .order_by(MigrationsTable.date_time_group.desc())
                    .all()
                )
                return result if result else []
            if mig_type == "applied":
                result = (
                    session.query(MigrationsTable)
                    .filter_by(status=MigrationStatus.APPLIED)
                    .order_by(MigrationsTable.date_time_group.desc())
                    .all()
                )
                return result if result else []
            if mig_type == "pending":
                result = (
                    session.query(MigrationsTable).filter_by(
                        status=MigrationStatus.PENDING
                    )
                    .all()
                )
                return result if result else []
            if mig_type == "failed":
                result = (
                    session.query(MigrationsTable)
                    .filter_by(status=MigrationStatus.FAILED)
                    .order_by(MigrationsTable.date_time_group.desc())
                    .all()
                )
                return result if result else []

            return []

    def extract_migration(self, file_name, mig_type="up") -> List[str]:
        file_path = os.path.join(MIGRATIONS_FOLDER_NAME, file_name)
        up_migration_sql: List[str] = []
        with open(file_path, "r") as file:
            data = file.read()
            migration_start_text = (
                CREATE_UP_START_MIGRATIONS
                if mig_type == "up"
                else CREATE_DOWN_START_MIGRATIONS
            )
            up_migration_sql_re = re.search(
                f"{migration_start_text}(.+?){END_MIGRATIONS}",
                # r"UP-MIGRATION-SQL.*?END",
                data,
                re.DOTALL,
            )
            if up_migration_sql_re:
                up_migration_sql_str = up_migration_sql_re.group(1)
                up_migration_sql = up_migration_sql_str.split(";")

        return list(
            filter(
                lambda x: len(x) != 0,
                map(lambda x: x.replace("\n", " ").strip(), filter(lambda x: x != "", up_migration_sql)))
        )

    def print_migration_info(self, action):
        print(
            f"using database name: {self.database_config.url}, "
            f"URL: {self.database_config.url}"
        )

    def execute(self, query):
        try:
            return self.database.execute_query(query=query)
        except Exception as e:
            print(f"Something went wrong" f"Exception raised: {e}")
