from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.dependencies.auth import (
    get_current_user,
    require_recruiter,
)

from app.models.user import User

from app.schemas.job_schema import (
    JobCreate,
    JobUpdate,
    JobResponse,
)

from app.services.job_service import JobService
from app.services.job_matching_service import JobMatchingService


# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


# ======================================================
# TEST JOB MATCHING
# Recruiter only
# ======================================================

@router.post("/test-match")
def test_match(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
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
        top_k=5,
    )


# ======================================================
# CREATE JOB
# Recruiter only
# ======================================================

@router.post(
    "",
    response_model=JobResponse,
    status_code=201,
)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return JobService.create_job(
        db=db,
        data=data,
    )


# ======================================================
# LIST ALL JOBS
# Any authenticated active user
# ======================================================

@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return JobService.list_jobs(
        db=db,
    )


# ======================================================
# GET SINGLE JOB
# Any authenticated active user
# ======================================================

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return JobService.get_job(
        db=db,
        job_id=job_id,
    )


# ======================================================
# UPDATE JOB
# Recruiter only
# ======================================================

@router.patch(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: int,
    data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return JobService.update_job(
        db=db,
        job_id=job_id,
        data=data,
    )


# ======================================================
# DELETE JOB
# Recruiter only
# ======================================================

@router.delete(
    "/{job_id}",
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return JobService.delete_job(
        db=db,
        job_id=job_id,
    )