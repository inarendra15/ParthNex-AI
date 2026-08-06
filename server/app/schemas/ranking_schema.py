from pydantic import BaseModel, Field


class RankingRequest(BaseModel):

    job_description: str = Field(
        ...,
        min_length=1
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=100
    )

    shortlist_threshold: float = Field(
        default=65.0,
        ge=0.0,
        le=100.0
    )