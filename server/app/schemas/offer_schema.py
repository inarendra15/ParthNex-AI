from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ======================================================
# ALLOWED OFFER STATUSES
# ======================================================

OfferStatus = Literal[
    "draft",
    "sent",
    "accepted",
    "rejected",
    "withdrawn",
    "expired",
]


# ======================================================
# CREATE OFFER
# ======================================================

class OfferCreate(BaseModel):

    application_id: int = Field(
        ...,
        gt=0
    )

    offered_role: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    salary: float = Field(
        ...,
        gt=0
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=10
    )

    joining_date: date | None = None

    offer_expiry_date: date | None = None

    notes: str | None = None

    @model_validator(mode="after")
    def validate_offer_dates(self):

        if (
            self.joining_date is not None
            and self.offer_expiry_date is not None
            and self.offer_expiry_date
            > self.joining_date
        ):
            raise ValueError(
                "Offer expiry date cannot be "
                "after joining date"
            )

        return self


# ======================================================
# UPDATE OFFER DETAILS
# ======================================================

class OfferUpdate(BaseModel):

    offered_role: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    salary: float | None = Field(
        default=None,
        gt=0
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=10
    )

    joining_date: date | None = None

    offer_expiry_date: date | None = None

    notes: str | None = None


# ======================================================
# UPDATE OFFER STATUS
# ======================================================

class OfferStatusUpdate(BaseModel):

    status: OfferStatus


# ======================================================
# OFFER RESPONSE
# ======================================================

class OfferResponse(BaseModel):

    id: int

    application_id: int
    job_id: int
    candidate_id: int

    offered_role: str

    salary: float
    currency: str

    joining_date: date | None = None
    offer_expiry_date: date | None = None

    status: OfferStatus

    notes: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }