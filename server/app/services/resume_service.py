import os
import uuid
import shutil

from fastapi import UploadFile
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.vector_service import VectorService


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
                detail="Only PDF, DOC and DOCX files are allowed."
            )

        unique_name = f"{uuid.uuid4()}{extension}"

        os.makedirs(
            UPLOAD_DIR,
            exist_ok=True
        )

        path = os.path.join(
            UPLOAD_DIR,
            unique_name
        )

        # Save uploaded file
        with open(path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Create Resume object
        resume = Resume(
            filename=file.filename,
            stored_filename=unique_name,
            file_path=path,
            file_type=extension,
            user_id=user_id
        )

        # Save metadata to PostgreSQL
        resume = ResumeRepository.create(
            db,
            resume
        )

        # ===============================
        # Automatically index into FAISS
        # ===============================
        try:
            VectorService.index_resume(
                resume.id,
                resume.file_path
            )
            print(
                f"✅ Resume {resume.id} indexed successfully."
            )

        except Exception as e:

            print(
                f"❌ Vector indexing failed: {e}"
            )

            # Future enhancement:
            # Save indexing status in database
            # Retry indexing using Celery/BackgroundTasks

        return resume

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

        # Delete physical file
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        # Delete from database
        ResumeRepository.delete(
            db,
            resume
        )

        return {
            "message": "Resume deleted successfully"
        }