from urllib.parse import ParseResult, urlparse
import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from simple_migrator.database.database_type import DatabaseType

from simple_migrator.utils.constants import (MIGRATIONS_CONFIG_FILE_NAME,
                                             MIGRATIONS_FOLDER_NAME,
                                             DATABASE_ENV_NAME_DEFAULT)


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    dbc: ParseResult
    database_type: DatabaseType

    @classmethod
    def create_from_values(cls, url: str):
        dbc = urlparse(url)
        return cls(url=url, dbc=dbc, database_type=DatabaseType(dbc.scheme))

    @classmethod
    def create_from_config_file(cls):
        file_path = os.path.join(
                MIGRATIONS_FOLDER_NAME,
                MIGRATIONS_CONFIG_FILE_NAME
        )

        with open(file_path, "r") as file:
            config_data = file.read()
            temp = config_data.split(":")
            db_env_name = ":".join(temp[1:]).replace("\n", "")
            return cls.create_from_env(db_env_name)

    @classmethod
    def create_from_env(cls, db_env_name: Optional[str]):
        load_dotenv()
        if not db_env_name:
            return cls.create_from_config_file()
        else:
            url = os.environ.get(db_env_name, "")
            if not url:
                raise Exception(f"Could not find {db_env_name}")
            return cls.create_from_values(url)

    @classmethod
    def setup_db_config(cls, db_env_name: Optional[str]):
        file_path = os.path.join(
                MIGRATIONS_FOLDER_NAME,
                MIGRATIONS_CONFIG_FILE_NAME
        )

        with open(
            os.path.join(Path(__file__).parent.parent,
                         "templates/config.txt"),
            "r"
        ) as template_file:
            template_content = template_file.read()

        # Replace {variable1} and {variable2} with actual values
        template_content = template_content.format(
            db_env_name=db_env_name if db_env_name else DATABASE_ENV_NAME_DEFAULT,
        )

        with open(file_path, "w") as file:
            file.write(template_content)
        return cls.create_from_config_file()
