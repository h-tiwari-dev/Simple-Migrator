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
from pathlib import Path
from .constants import (
    CREATE_DOWN_START_MIGRATIONS,
    CREATE_UP_START_MIGRATIONS,
    END_MIGRATIONS,
    MIGRATIONS_CONFIG_FILE_NAME,
    MIGRATIONS_FOLDER_NAME,
)
import os
import time
import shutil


class MigrationTool:
    def __init__(self, database_config: DatabaseConfig):
        self.database_config = database_config
        self.database = DataBase(url=database_config.url)

    def setup(self):
        # Check if the folder exists
        if not os.path.exists(MIGRATIONS_FOLDER_NAME):
            # If not, create the folder
            os.makedirs(MIGRATIONS_FOLDER_NAME)
            print(f"Migration folder '{MIGRATIONS_FOLDER_NAME}' created.")

        file_path = os.path.join(MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
        print("File_path", file_path)

        # Check if the file exists
        if not os.path.exists(file_path):
            # Read template content from the file
            with open(
                os.path.join(Path(__file__).parent.parent, "templates/config.txt"), "r"
            ) as template_file:
                template_content = template_file.read()

            # Replace {variable1} and {variable2} with actual values
            template_content = template_content.format(
                database_url=self.database_config.url,
            )

            with open(file_path, "w") as file:
                file.write(template_content)

            print(f"Config File '{file_path}' created.")
        else:
            # Recreate the folder and file if they already exist
            print("File already exits. Reinitializing everything!!")
            shutil.rmtree(MIGRATIONS_FOLDER_NAME)
            self.setup()

    @staticmethod
    def create_migration_name(file_name: str):
        return f"{time.time()}_{file_name}"

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

    def save_migration(self, file_name: str, description: Optional[str]):
        with self.database.Session() as session:
            new_row = MigrationsTable(name=file_name, description=description)
            session.add(new_row)
            session.commit()
            session.close()

    def update_migration(self, file_name: str, migration_status: MigrationStatus):
        with self.database.Session() as session:
            migration = session.query(MigrationsTable).filter_by(name=file_name).first()
            if migration:
                migration.status = migration_status
                migration.applied_at = datetime.now()
            session.commit()
            session.close()

    def validate_migrations_from_file_name(self, file_names: List[str]):
        non_existent_files = [file for file in file_names if not os.path.exists(os.path.join(MIGRATIONS_FOLDER_NAME,file))]
        if len(non_existent_files) != 0:
            raise Exception(
                f"Following migrations files does not exists: \n{non_existent_files}\n Are you sure the names are correct?"
            )
        with self.database.Session() as session:
            query_result = (
                session.query(MigrationsTable.name)
                .filter_by(name=MigrationsTable.name.not_in(file_names))
                .all()
            )
            database_file_names = [value for (value,) in query_result]
            if len(database_file_names) != 0:
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
