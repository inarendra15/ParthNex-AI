from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ======================================================
# ALLOWED RECRUITMENT STATUSES
# ======================================================

ApplicationStatus = Literal[
    "applied",
    "screened",
    "shortlisted",
    "interview",
    "selected",
    "rejected",
]


# ======================================================
# CREATE APPLICATION
# ======================================================

class ApplicationCreate(BaseModel):

    job_id: int = Field(
        ...,
        gt=0
    )

    candidate_id: int = Field(
        ...,
        gt=0
    )

    resume_id: int = Field(
        ...,
        gt=0
    )


# ======================================================
# UPDATE APPLICATION STATUS
# ======================================================

class ApplicationStatusUpdate(BaseModel):

    status: ApplicationStatus


# ======================================================
# AI SCORE UPDATE
# Internal/service-level schema
# ======================================================

class ApplicationScoreUpdate(BaseModel):

    ranking_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    semantic_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    skill_score: float | None = Field(
        default=None,
        ge=0,
        le=100
    )

    shortlisted: bool | None = None


# ======================================================
# APPLICATION RESPONSE
# ======================================================

class ApplicationResponse(BaseModel):

    id: int

    job_id: int
    candidate_id: int
    resume_id: int

    ranking_score: float | None
    semantic_score: float | None
    skill_score: float | None

    shortlisted: bool

    status: ApplicationStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )