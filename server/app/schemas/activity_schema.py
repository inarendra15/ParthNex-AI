from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ======================================================
# ACTIVITY RESPONSE
# ======================================================

class ActivityResponse(BaseModel):

    id: int

    application_id: int | None = None
    job_id: int | None = None
    candidate_id: int | None = None

    activity_type: str

    entity_type: str
    entity_id: int | None = None

    title: str
    description: str | None = None

    old_status: str | None = None
    new_status: str | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ======================================================
# ACTIVITY LIST RESPONSE
# ======================================================

class ActivityListResponse(BaseModel):

    total: int

    activities: list[ActivityResponse]