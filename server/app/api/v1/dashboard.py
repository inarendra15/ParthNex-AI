from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.dependencies.auth import require_recruiter

from app.models.user import User

from app.schemas.dashboard_schema import (
    DashboardSummaryResponse,
    JobAnalyticsResponse,
    JobsOverviewResponse,
    TopCandidatesResponse,
)

from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Recruiter Dashboard"],
)


# ======================================================
# DASHBOARD SUMMARY
# Recruiter only
# ======================================================

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return DashboardService.get_summary(
        db=db
    )


# ======================================================
# JOB-WISE DASHBOARD OVERVIEW
# Recruiter only
# ======================================================

@router.get(
    "/jobs",
    response_model=JobsOverviewResponse,
)
def get_jobs_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return DashboardService.get_jobs_overview(
        db=db
    )


# ======================================================
# TOP CANDIDATES FOR JOB
# Recruiter only
# ======================================================

@router.get(
    "/jobs/{job_id}/top-candidates",
    response_model=TopCandidatesResponse,
)
def get_top_candidates(
    job_id: int,

    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    result = DashboardService.get_top_candidates(
        db=db,
        job_id=job_id,
        limit=limit
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return result


# ======================================================
# PER-JOB ANALYTICS
# Recruiter only
# ======================================================

@router.get(
    "/jobs/{job_id}",
    response_model=JobAnalyticsResponse,
)
def get_job_analytics(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    result = DashboardService.get_job_analytics(
        db=db,
        job_id=job_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return result