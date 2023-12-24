import enum
from sqlalchemy import Column, DateTime, Enum, Integer, Sequence, String

from .base import Base

from .constants import MIGRATIONS_TABLE_NAME


class MigrationStatus(enum.Enum):
    APPLIED = "applied"
    PENDING = "pending"
    FAILED = "failed"


# Define the model for your table
class MigrationsTable(Base):
    __tablename__ = MIGRATIONS_TABLE_NAME

    id = Column(Integer, Sequence("Val"), primary_key=True, autoincrement=True)
    name = Column(String(50))
    description = Column(String(255))
    applied_at = Column(DateTime)
    status = Column(
        Enum(MigrationStatus), nullable=False, default=MigrationStatus.PENDING
    )
    date_time_group = Column(DateTime)
