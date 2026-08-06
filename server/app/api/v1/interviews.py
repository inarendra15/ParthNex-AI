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

from app.models.user import User

from app.schemas.interview_schema import (
    InterviewCreate,
    InterviewFeedbackUpdate,
    InterviewResponse,
    InterviewStatusUpdate,
    InterviewUpdate,
)

from app.services.interview_service import (
    InterviewService,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interview Management"],
)


# ======================================================
# CREATE / SCHEDULE INTERVIEW
# Recruiter only
# ======================================================

@router.post(
    "",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    interview = (
        InterviewService.create_interview(
            db=db,
            data=data,
        )
    )

    # ----------------------------------------------
    # Application Not Found
    # ----------------------------------------------

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # ----------------------------------------------
    # Duplicate Interview Round
    # ----------------------------------------------

    if (
        isinstance(interview, dict)
        and interview.get("error")
        == "duplicate_round"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Candidate already has an interview "
                "for this round"
            ),
        )

    return interview


# ======================================================
# GET ALL INTERVIEWS
# Recruiter only
# ======================================================

@router.get(
    "",
    response_model=list[InterviewResponse],
)
def get_interviews(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return InterviewService.get_interviews(
        db=db,
        skip=skip,
        limit=limit,
    )


# ======================================================
# GET INTERVIEWS BY APPLICATION
# Candidate: own application only
# Recruiter: any application
# ======================================================

@router.get(
    "/application/{application_id}",
    response_model=list[InterviewResponse],
)
def get_application_interviews(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    interviews = (
        InterviewService.get_application_interviews(
            db=db,
            application_id=application_id,
        )
    )

    if interviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    if current_user.role == "candidate":

        # Even when an application currently has no
        # interviews, ownership must still be checked.
        from app.models.application import Application

        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if (
            application is None
            or application.candidate_id
            != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Candidates can only view "
                    "their own interviews"
                ),
            )

    return interviews


# ======================================================
# GET INTERVIEWS BY JOB
# Recruiter only
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=list[InterviewResponse],
)
def get_job_interviews(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return InterviewService.get_job_interviews(
        db=db,
        job_id=job_id,
    )


# ======================================================
# GET INTERVIEW BY ID
# Candidate: own interview only
# Recruiter: any interview
# ======================================================

@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    interview = (
        InterviewService.get_interview(
            db=db,
            interview_id=interview_id,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    if (
        current_user.role == "candidate"
        and interview.candidate_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own interviews"
            ),
        )

    return interview


# ======================================================
# UPDATE INTERVIEW DETAILS
# Recruiter only
# ======================================================

@router.patch(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    interview = (
        InterviewService.update_interview(
            db=db,
            interview_id=interview_id,
            data=data,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    # ----------------------------------------------
    # Duplicate Interview Round
    # ----------------------------------------------

    if (
        isinstance(interview, dict)
        and interview.get("error")
        == "duplicate_round"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Candidate already has an interview "
                "for this round"
            ),
        )

    return interview


# ======================================================
# UPDATE INTERVIEW STATUS
# Recruiter only
# ======================================================

@router.patch(
    "/{interview_id}/status",
    response_model=InterviewResponse,
)
def update_interview_status(
    interview_id: int,
    data: InterviewStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    interview = (
        InterviewService.update_status(
            db=db,
            interview_id=interview_id,
            data=data,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    return interview


# ======================================================
# ADD / UPDATE INTERVIEW FEEDBACK
# Recruiter only
# ======================================================

@router.patch(
    "/{interview_id}/feedback",
    response_model=InterviewResponse,
)
def update_interview_feedback(
    interview_id: int,
    data: InterviewFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    interview = (
        InterviewService.update_feedback(
            db=db,
            interview_id=interview_id,
            data=data,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    return interview


# ======================================================
# DELETE INTERVIEW
# Recruiter only
# ======================================================

@router.delete(
    "/{interview_id}",
)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    deleted = (
        InterviewService.delete_interview(
            db=db,
            interview_id=interview_id,
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )

    return {
        "message": (
            "Interview deleted successfully"
        ),
        "interview_id": interview_id,
    }