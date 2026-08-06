from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.job_schema import (
    JobCreate,
    JobUpdate,
    JobResponse
)

from app.services.job_service import JobService
from app.services.job_matching_service import JobMatchingService


# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ======================================================
# TEST JOB MATCHING
# Existing AI job matching endpoint
# ======================================================

@router.post("/test-match")
def test_match(
    db: Session = Depends(get_db)
):

    job = """
    Python Backend Developer

    Python
    FastAPI
    REST API
    Docker
    PostgreSQL
    Machine Learning
    """

    return JobMatchingService.match_candidates(
        db=db,
        job_description=job,
        top_k=5
    )


# ======================================================
# CREATE JOB
# ======================================================

@router.post(
    "",
    response_model=JobResponse,
    status_code=201
)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db)
):

    return JobService.create_job(
        db=db,
        data=data
    )


# ======================================================
# LIST ALL JOBS
# ======================================================

@router.get(
    "",
    response_model=list[JobResponse]
)
def list_jobs(
    db: Session = Depends(get_db)
):

    return JobService.list_jobs(
        db=db
    )


# ======================================================
# GET SINGLE JOB
# ======================================================

@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    return JobService.get_job(
        db=db,
        job_id=job_id
    )


# ======================================================
# UPDATE JOB
# ======================================================

@router.patch(
    "/{job_id}",
    response_model=JobResponse
)
def update_job(
    job_id: int,
    data: JobUpdate,
    db: Session = Depends(get_db)
):

    return JobService.update_job(
        db=db,
        job_id=job_id,
        data=data
    )


# ======================================================
# DELETE JOB
# ======================================================

@router.delete(
    "/{job_id}"
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):

    return JobService.delete_job(
        db=db,
        job_id=job_id
    )