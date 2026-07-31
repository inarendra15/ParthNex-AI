import os
import uuid
import shutil

from fastapi import UploadFile
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository


UPLOAD_DIR = "uploads/resumes"


class ResumeService:

    ALLOWED_TYPES = [
        ".pdf",
        ".doc",
        ".docx"
    ]

    @staticmethod
    def upload(
        db: Session,
        file: UploadFile,
        user_id: int
    ):

        extension = os.path.splitext(file.filename)[1].lower()

        if extension not in ResumeService.ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOC and DOCX are allowed."
            )

        unique_name = (
            str(uuid.uuid4())
            + extension
        )

        os.makedirs(
            UPLOAD_DIR,
            exist_ok=True
        )

        path = os.path.join(
            UPLOAD_DIR,
            unique_name
        )

        with open(path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        resume = Resume(
            filename=file.filename,
            stored_filename=unique_name,
            file_path=path,
            file_type=extension,
            user_id=user_id
        )

        return ResumeRepository.create(
            db,
            resume
        )

    @staticmethod
    def list_resumes(
        db: Session,
        user_id: int
    ):
        return ResumeRepository.get_by_user(
            db,
            user_id
        )

    @staticmethod
    def delete_resume(
        db: Session,
        resume_id: int,
        user_id: int
    ):
        resume = (
            db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
            )
        .first()
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )

        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        ResumeRepository.delete(
            db,
            resume
        )
        return {
        "message": "Resume deleted successfully"
        }