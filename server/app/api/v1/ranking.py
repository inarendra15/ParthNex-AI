from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.ranking_schema import RankingRequest
from app.services.ranking_service import RankingService
from app.services.job_service import JobService


router = APIRouter(
    prefix="/ranking",
    tags=["Candidate Ranking"]
)


# ======================================================
# RANK USING MANUAL JOB DESCRIPTION
# Existing Phase 8 endpoint
# ======================================================

@router.post("/candidates")
def rank_candidates(
    request: RankingRequest,
    db: Session = Depends(get_db)
):

    return RankingService.rank_candidates(
        db=db,
        job_description=request.job_description,
        top_k=request.top_k,
        shortlist_threshold=request.shortlist_threshold
    )


# ======================================================
# RANK USING STORED JOB
# Phase 9 endpoint
# ======================================================

@router.post("/jobs/{job_id}")
def rank_candidates_for_job(
    job_id: int,
    top_k: int = 5,
    shortlist_threshold: float = 65.0,
    db: Session = Depends(get_db)
):

    # Retrieve job from PostgreSQL
    job = JobService.get_job(
        db=db,
        job_id=job_id
    )

    # Run existing Phase 8 ranking pipeline
    result = RankingService.rank_candidates(
        db=db,
        job_description=job.description,
        top_k=top_k,
        shortlist_threshold=shortlist_threshold
    )

    # Add stored job information to response
    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "employment_type": job.employment_type,
            "status": job.status
        },
        **result
    }