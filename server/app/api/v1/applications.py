from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationScoreUpdate,
    ApplicationStatusUpdate,
)

from app.services.application_service import ApplicationService


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


# ======================================================
# CREATE APPLICATION
# ======================================================

@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=201,
)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
):

    return ApplicationService.create_application(
        db=db,
        data=data,
    )


# ======================================================
# LIST ALL APPLICATIONS
# ======================================================

@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def list_applications(
    db: Session = Depends(get_db),
):

    return ApplicationService.list_applications(
        db=db,
    )


# ======================================================
# LIST APPLICATIONS FOR A JOB
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=list[ApplicationResponse],
)
def list_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
):

    return ApplicationService.list_job_applications(
        db=db,
        job_id=job_id,
    )


# ======================================================
# LIST APPLICATIONS FOR A CANDIDATE
# ======================================================

@router.get(
    "/candidate/{candidate_id}",
    response_model=list[ApplicationResponse],
)
def list_candidate_applications(
    candidate_id: int,
    db: Session = Depends(get_db),
):

    return ApplicationService.list_candidate_applications(
        db=db,
        candidate_id=candidate_id,
    )


# ======================================================
# GET SINGLE APPLICATION
# ======================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):

    return ApplicationService.get_application(
        db=db,
        application_id=application_id,
    )


# ======================================================
# UPDATE RECRUITMENT STATUS
# ======================================================

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
)
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):

    return ApplicationService.update_status(
        db=db,
        application_id=application_id,
        data=data,
    )


# ======================================================
# UPDATE AI SCORES
# ======================================================

@router.patch(
    "/{application_id}/scores",
    response_model=ApplicationResponse,
)
def update_application_scores(
    application_id: int,
    data: ApplicationScoreUpdate,
    db: Session = Depends(get_db),
):

    return ApplicationService.update_scores(
        db=db,
        application_id=application_id,
        data=data,
    )


# ======================================================
# DELETE APPLICATION
# ======================================================

@router.delete(
    "/{application_id}",
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
):

    return ApplicationService.delete_application(
        db=db,
        application_id=application_id,
    )