from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.dependencies.auth import (
    get_current_user,
    require_recruiter,
)

from app.models.application import Application
from app.models.job import Job
from app.models.user import User

from app.schemas.activity_schema import (
    ActivityListResponse,
    ActivityResponse,
)

from app.services.activity_service import ActivityService


router = APIRouter(
    prefix="/activities",
    tags=["Activity & Audit Log"],
)


# ======================================================
# LIST RECENT ACTIVITIES
# Recruiter only
# ======================================================

@router.get(
    "",
    response_model=ActivityListResponse,
)
def list_activities(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    activities = ActivityService.list_activities(
        db=db,
        limit=limit,
    )

    total = ActivityService.count_activities(
        db=db,
    )

    return {
        "total": total,
        "activities": activities,
    }


# ======================================================
# APPLICATION TIMELINE
# Candidate: own application only
# Recruiter: any application
# ======================================================

@router.get(
    "/application/{application_id}",
    response_model=ActivityListResponse,
)
def get_application_timeline(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if (
        current_user.role == "candidate"
        and application.candidate_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own application activity"
            ),
        )

    activities = (
        ActivityService.list_application_activities(
            db=db,
            application_id=application_id,
        )
    )

    return {
        "total": len(activities),
        "activities": activities,
    }


# ======================================================
# JOB ACTIVITY FEED
# Recruiter only
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=ActivityListResponse,
)
def get_job_activities(
    job_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    activities = (
        ActivityService.list_job_activities(
            db=db,
            job_id=job_id,
            limit=limit,
        )
    )

    return {
        "total": len(activities),
        "activities": activities,
    }


# ======================================================
# CANDIDATE ACTIVITY FEED
# Candidate: own activities only
# Recruiter: any candidate
# ======================================================

@router.get(
    "/candidate/{candidate_id}",
    response_model=ActivityListResponse,
)
def get_candidate_activities(
    candidate_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    candidate = (
        db.query(User)
        .filter(
            User.id == candidate_id
        )
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    if (
        current_user.role == "candidate"
        and candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own activities"
            ),
        )

    activities = (
        ActivityService.list_candidate_activities(
            db=db,
            candidate_id=candidate_id,
            limit=limit,
        )
    )

    return {
        "total": len(activities),
        "activities": activities,
    }


# ======================================================
# GET ACTIVITY BY ID
# Candidate: own activity only
# Recruiter: any activity
# ======================================================

@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    activity = ActivityService.get_activity(
        db=db,
        activity_id=activity_id,
    )

    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    if current_user.role == "candidate":

        if (
            activity.candidate_id is None
            or activity.candidate_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Candidates can only view "
                    "their own activities"
                ),
            )

    return activity