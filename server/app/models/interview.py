from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.sql import func

from app.database.session import Base


class Interview(Base):

    __tablename__ = "interviews"

    # ==================================================
    # TABLE CONSTRAINTS
    # ==================================================
    #
    # A single application cannot have two interviews
    # with the same round number.
    #
    # Example:
    #
    # Application 1 + Round 1 -> allowed
    # Application 1 + Round 2 -> allowed
    # Application 1 + Round 2 -> duplicate, not allowed
    #
    # Another application can independently have
    # Round 1, Round 2, etc.
    # ==================================================

    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "round_number",
            name="uq_interview_application_round",
        ),
    )

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    application_id = Column(
        Integer,
        ForeignKey(
            "applications.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ==================================================
    # INTERVIEW INFORMATION
    # ==================================================

    interview_type = Column(
        String(50),
        nullable=False,
        default="technical"
    )

    round_number = Column(
        Integer,
        nullable=False,
        default=1
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    duration_minutes = Column(
        Integer,
        nullable=False,
        default=60
    )

    meeting_link = Column(
        String(500),
        nullable=True
    )

    interviewer_name = Column(
        String(150),
        nullable=True
    )

    # ==================================================
    # INTERVIEW STATUS
    # ==================================================

    status = Column(
        String(50),
        nullable=False,
        default="scheduled"
    )

    # ==================================================
    # INTERVIEW FEEDBACK
    # ==================================================

    rating = Column(
        Float,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    recommendation = Column(
        String(50),
        nullable=True
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

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