from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================
# BASE JOB SCHEMA
# ======================================================

class JobBase(BaseModel):

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    company: Optional[str] = Field(
        default=None,
        max_length=255
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255
    )

    employment_type: Optional[str] = Field(
        default=None,
        max_length=100
    )

    description: str = Field(
        ...,
        min_length=1
    )


# ======================================================
# CREATE JOB
# ======================================================

class JobCreate(JobBase):
    pass


# ======================================================
# UPDATE JOB
# ======================================================

class JobUpdate(BaseModel):

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    company: Optional[str] = Field(
        default=None,
        max_length=255
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255
    )

    employment_type: Optional[str] = Field(
        default=None,
        max_length=100
    )

    description: Optional[str] = Field(
        default=None,
        min_length=1
    )

    status: Optional[str] = Field(
        default=None,
        max_length=50
    )


# ======================================================
# JOB RESPONSE
# ======================================================

class JobResponse(JobBase):

    id: int
    status: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )