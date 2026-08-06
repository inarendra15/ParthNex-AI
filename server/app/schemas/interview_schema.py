from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ======================================================
# ALLOWED VALUES
# ======================================================

InterviewType = Literal[
    "technical",
    "system_design",
    "hr",
    "managerial",
    "behavioral",
    "other",
]

InterviewStatus = Literal[
    "scheduled",
    "completed",
    "cancelled",
    "rescheduled",
    "no_show",
]

InterviewRecommendation = Literal[
    "strong_hire",
    "hire",
    "consider",
    "no_hire",
]


# ======================================================
# CREATE INTERVIEW
# ======================================================

class InterviewCreate(BaseModel):

    application_id: int

    interview_type: InterviewType = "technical"

    round_number: int = Field(
        default=1,
        ge=1,
        le=20,
    )

    scheduled_at: datetime

    duration_minutes: int = Field(
        default=60,
        ge=10,
        le=480,
    )

    meeting_link: str | None = None

    interviewer_name: str | None = None


# ======================================================
# UPDATE INTERVIEW DETAILS
# ======================================================

class InterviewUpdate(BaseModel):

    interview_type: InterviewType | None = None

    round_number: int | None = Field(
        default=None,
        ge=1,
        le=20,
    )

    scheduled_at: datetime | None = None

    duration_minutes: int | None = Field(
        default=None,
        ge=10,
        le=480,
    )

    meeting_link: str | None = None

    interviewer_name: str | None = None


# ======================================================
# UPDATE INTERVIEW STATUS
# ======================================================

class InterviewStatusUpdate(BaseModel):

    status: InterviewStatus


# ======================================================
# INTERVIEW FEEDBACK
# ======================================================

class InterviewFeedbackUpdate(BaseModel):

    rating: float = Field(
        ge=0,
        le=5,
    )

    feedback: str | None = None

    recommendation: InterviewRecommendation


# ======================================================
# INTERVIEW RESPONSE
# ======================================================

class InterviewResponse(BaseModel):

    id: int

    application_id: int
    job_id: int
    candidate_id: int

    interview_type: str
    round_number: int

    scheduled_at: datetime
    duration_minutes: int

    meeting_link: str | None
    interviewer_name: str | None

    status: str

    rating: float | None
    feedback: str | None
    recommendation: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )