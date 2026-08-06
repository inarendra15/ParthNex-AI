from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user

from app.models.resume import Resume
from app.models.user import User

from app.schemas.resume import ResumeResponse

from app.services.resume_service import ResumeService


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


# ======================================================
# UPLOAD RESUME
# Authenticated user
# Resume automatically belongs to current user
# ======================================================

@router.post(
    "/upload",
    response_model=ResumeResponse,
)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return ResumeService.upload(
        db,
        file,
        current_user.id,
    )


# ======================================================
# LIST MY RESUMES
# Authenticated user
# ======================================================

@router.get(
    "/my",
    response_model=List[ResumeResponse],
)
def my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return ResumeService.list_resumes(
        db,
        current_user.id,
    )


# ======================================================
# DOWNLOAD OWN RESUME
# Ownership protected
# ======================================================

@router.get(
    "/download/{resume_id}",
)
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    return FileResponse(
        path=resume.file_path,
        filename=resume.filename,
    )


# ======================================================
# DELETE OWN RESUME
# Ownership protected
# ======================================================

@router.delete(
    "/{resume_id}",
)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return ResumeService.delete_resume(
        db,
        resume_id,
        current_user.id,
    )