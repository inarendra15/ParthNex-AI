from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import File
from fastapi.responses import FileResponse

from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.models.resume import Resume

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User

from app.schemas.resume import ResumeResponse

from app.services.resume_service import ResumeService
from typing import List

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


@router.post(
    "/upload",
    response_model=ResumeResponse
)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ResumeService.upload(
        db,
        file,
        current_user.id
    )

@router.get(
    "/my",
    response_model=List[ResumeResponse]
)
def my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ResumeService.list_resumes(
        db,
        current_user.id
    )

@router.get("/download/{resume_id}")
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return FileResponse(
        resume.file_path,
        filename=resume.filename
    )

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ResumeService.delete_resume(
        db,
        resume_id,
        current_user.id
    )