from enum import Enum


class DatabaseType(Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"

    @classmethod
    def from_string(cls, enum_str):
        try:
            return cls(enum_str)
        except KeyError:
            raise ValueError(f"Database {enum_str} is not implemented.")
