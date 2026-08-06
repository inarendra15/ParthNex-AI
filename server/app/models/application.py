from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.database.session import Base


class Application(Base):

    __tablename__ = "applications"

    # Prevent the same candidate from applying
    # to the same job more than once.
    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "candidate_id",
            name="uq_application_job_candidate",
        ),
    )

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

    job_id = Column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ==================================================
    # AI SCORES
    # ==================================================

    ranking_score = Column(
        Float,
        nullable=True,
    )

    semantic_score = Column(
        Float,
        nullable=True,
    )

    skill_score = Column(
        Float,
        nullable=True,
    )

    # ==================================================
    # SHORTLISTING
    # ==================================================

    shortlisted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ==================================================
    # RECRUITMENT PIPELINE STATUS
    # ==================================================
    #
    # applied
    # screened
    # shortlisted
    # interview
    # selected
    # rejected
    #

    status = Column(
        String(50),
        default="applied",
        nullable=False,
        index=True,
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )