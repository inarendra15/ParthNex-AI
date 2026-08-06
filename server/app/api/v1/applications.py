from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.dependencies.auth import (
    get_current_user,
    require_recruiter,
)

from app.models.user import User

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
# Candidate: only for self
# Recruiter: allowed
# ======================================================

@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=201,
)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Candidate cannot create an application
    # on behalf of another candidate.
    if (
        current_user.role == "candidate"
        and data.candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only create "
                "their own applications"
            ),
        )

    return ApplicationService.create_application(
        db=db,
        data=data,
    )


# ======================================================
# LIST ALL APPLICATIONS
# Recruiter only
# ======================================================

@router.get(
    "",
    response_model=list[ApplicationResponse],
)
def list_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return ApplicationService.list_applications(
        db=db,
    )


# ======================================================
# LIST APPLICATIONS FOR A JOB
# Recruiter only
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=list[ApplicationResponse],
)
def list_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return ApplicationService.list_job_applications(
        db=db,
        job_id=job_id,
    )


# ======================================================
# LIST APPLICATIONS FOR A CANDIDATE
# Candidate: own applications only
# Recruiter: any candidate
# ======================================================

@router.get(
    "/candidate/{candidate_id}",
    response_model=list[ApplicationResponse],
)
def list_candidate_applications(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if (
        current_user.role == "candidate"
        and candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own applications"
            ),
        )

    return ApplicationService.list_candidate_applications(
        db=db,
        candidate_id=candidate_id,
    )


# ======================================================
# GET SINGLE APPLICATION
# Candidate: own application only
# Recruiter: any application
# ======================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    application = ApplicationService.get_application(
        db=db,
        application_id=application_id,
    )

    if (
        current_user.role == "candidate"
        and application.candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own applications"
            ),
        )

    return application


# ======================================================
# UPDATE RECRUITMENT STATUS
# Recruiter only
# ======================================================

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
)
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return ApplicationService.update_status(
        db=db,
        application_id=application_id,
        data=data,
    )


# ======================================================
# UPDATE AI SCORES
# Recruiter only
# ======================================================

@router.patch(
    "/{application_id}/scores",
    response_model=ApplicationResponse,
)
def update_application_scores(
    application_id: int,
    data: ApplicationScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return ApplicationService.update_scores(
        db=db,
        application_id=application_id,
        data=data,
    )


# ======================================================
# DELETE APPLICATION
# Candidate: own application only
# Recruiter: any application
# ======================================================

@router.delete(
    "/{application_id}",
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    application = ApplicationService.get_application(
        db=db,
        application_id=application_id,
    )

    if (
        current_user.role == "candidate"
        and application.candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only delete "
                "their own applications"
            ),
        )

    return ApplicationService.delete_application(
        db=db,
        application_id=application_id,
    )