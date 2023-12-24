from datetime import datetime
import re
from typing import List, Optional, Tuple

from sqlalchemy import func
from simple_migrator.database.config import DatabaseConfig
from simple_migrator.database.tables.migrations_table import (
    MigrationStatus,
    MigrationsTable,
)
from simple_migrator.utils.constants import (
    CREATE_DOWN_START_MIGRATIONS,
    CREATE_UP_START_MIGRATIONS,
    END_MIGRATIONS,
    MIGRATIONS_CONFIG_FILE_NAME,
    MIGRATIONS_FOLDER_NAME,
)
from ..database.database import DataBase
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
                os.path.join(os.getcwd(), "templates/config.txt"), "r"
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
        print(f"Updating Migration {file_name} {migration_status}")
        with self.database.Session() as session:
            migration = session.query(MigrationsTable).filter_by(name=file_name).first()
            if migration:
                migration.status = migration_status
                migration.applied_at = datetime.now()
            session.commit()
            session.close()

    def get_migrations(self, migration_type: str) -> List[str]:
        with self.database.Session() as session:
            if migration_type == "up":
                query_result = (
                    session.query(MigrationsTable.name)
                    .filter_by(status=MigrationStatus.PENDING)
                    .all()
                )
                return [value for (value,) in query_result]
            elif migration_type == "down":
                return []
        return []

    def group_migrations(self, migrations_name: List[str]):
        new_group_val = datetime.now()
        print(
            f"Adding the following group value {new_group_val} to these {migrations_name}"
        )
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
                up_migration_sql = up_migration_sql_str.split("\n")

        return list(
            map(lambda x: x.strip(), filter(lambda x: x != "", up_migration_sql))
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
