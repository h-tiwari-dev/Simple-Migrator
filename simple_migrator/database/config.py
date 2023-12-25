from urllib.parse import ParseResult, urlparse
import os
from typing import Optional
from dataclasses import dataclass

from simple_migrator.database.database_type import DatabaseType

from utils.constants import MIGRATIONS_CONFIG_FILE_NAME, MIGRATIONS_FOLDER_NAME


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
        file_path = os.path.join(MIGRATIONS_FOLDER_NAME, MIGRATIONS_CONFIG_FILE_NAME)
        print("File_path", file_path, os.getcwd())

        with open(file_path, "r") as file:
            config_data = file.read()
            temp = config_data.split(":")
            print(f"CONFIG FILE PATH {temp} {':'.join(temp[1:])}")
            return cls.create_from_values(":".join(temp[1:]).replace("\n", ""))
            print(f"CONFIG FILE PATH {temp}")
