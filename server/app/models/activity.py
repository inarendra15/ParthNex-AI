from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database.session import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # --------------------------------------------------
    # Related Recruitment Entities
    # --------------------------------------------------

    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=True,
        index=True,
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=True,
        index=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # --------------------------------------------------
    # Activity Information
    # --------------------------------------------------

    activity_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_type = Column(
        String(50),
        nullable=False,
    )

    entity_id = Column(
        Integer,
        nullable=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------
    # State Change Information
    # --------------------------------------------------

    old_status = Column(
        String(50),
        nullable=True,
    )

    new_status = Column(
        String(50),
        nullable=True,
    )

    # --------------------------------------------------
    # Timestamp
    # --------------------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )