from sqlalchemy import (
    Column,
    Date,
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


class Offer(Base):

    __tablename__ = "offers"

    # ==================================================
    # TABLE CONSTRAINTS
    # ==================================================

    __table_args__ = (
        UniqueConstraint(
            "application_id",
            name="uq_offer_application",
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

    application_id = Column(
        Integer,
        ForeignKey(
            "applications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_id = Column(
        Integer,
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    candidate_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # OFFER DETAILS
    # ==================================================

    offered_role = Column(
        String(200),
        nullable=False,
    )

    salary = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="INR",
    )

    joining_date = Column(
        Date,
        nullable=True,
    )

    offer_expiry_date = Column(
        Date,
        nullable=True,
    )

    # ==================================================
    # OFFER STATUS
    # ==================================================

    status = Column(
        String(50),
        nullable=False,
        default="draft",
    )

    # ==================================================
    # NOTES
    # ==================================================

    notes = Column(
        Text,
        nullable=True,
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )