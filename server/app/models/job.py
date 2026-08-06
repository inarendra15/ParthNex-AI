from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime
)
from sqlalchemy.sql import func

from app.database.session import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False,
        index=True
    )

    company = Column(
        String(255),
        nullable=True
    )

    location = Column(
        String(255),
        nullable=True
    )

    employment_type = Column(
        String(100),
        nullable=True
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="open"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )