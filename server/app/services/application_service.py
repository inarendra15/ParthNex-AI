from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User

from app.schemas.application_schema import (
    ApplicationCreate,
    ApplicationScoreUpdate,
    ApplicationStatusUpdate,
)


class ApplicationService:

    # ==================================================
    # CREATE APPLICATION
    # ==================================================

    @staticmethod
    def create_application(
        db: Session,
        data: ApplicationCreate,
    ):

        # ----------------------------------------------
        # Validate Job
        # ----------------------------------------------

        job = (
            db.query(Job)
            .filter(Job.id == data.job_id)
            .first()
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        # ----------------------------------------------
        # Validate Candidate
        # ----------------------------------------------

        candidate = (
            db.query(User)
            .filter(User.id == data.candidate_id)
            .first()
        )

        if candidate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )

        # ----------------------------------------------
        # Validate Resume
        # ----------------------------------------------

        resume = (
            db.query(Resume)
            .filter(Resume.id == data.resume_id)
            .first()
        )

        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

        # Resume must belong to candidate
        if resume.user_id != candidate.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume does not belong to candidate",
            )

        # ----------------------------------------------
        # Prevent Duplicate Application
        # ----------------------------------------------

        existing = (
            db.query(Application)
            .filter(
                Application.job_id == data.job_id,
                Application.candidate_id == data.candidate_id,
            )
            .first()
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Candidate has already applied to this job",
            )

        # ----------------------------------------------
        # Create
        # ----------------------------------------------

        application = Application(
            job_id=data.job_id,
            candidate_id=data.candidate_id,
            resume_id=data.resume_id,
            status="applied",
            shortlisted=False,
        )

        try:
            db.add(application)
            db.commit()
            db.refresh(application)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Candidate has already applied to this job",
            )

        return application

    # ==================================================
    # GET APPLICATION
    # ==================================================

    @staticmethod
    def get_application(
        db: Session,
        application_id: int,
    ):

        application = (
            db.query(Application)
            .filter(Application.id == application_id)
            .first()
        )

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        return application

    # ==================================================
    # LIST APPLICATIONS
    # ==================================================

    @staticmethod
    def list_applications(
        db: Session,
    ):

        return (
            db.query(Application)
            .order_by(Application.created_at.desc())
            .all()
        )

    # ==================================================
    # LIST APPLICATIONS FOR JOB
    # ==================================================

    @staticmethod
    def list_job_applications(
        db: Session,
        job_id: int,
    ):

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        return (
            db.query(Application)
            .filter(Application.job_id == job_id)
            .order_by(Application.created_at.desc())
            .all()
        )

    # ==================================================
    # LIST APPLICATIONS FOR CANDIDATE
    # ==================================================

    @staticmethod
    def list_candidate_applications(
        db: Session,
        candidate_id: int,
    ):

        candidate = (
            db.query(User)
            .filter(User.id == candidate_id)
            .first()
        )

        if candidate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found",
            )

        return (
            db.query(Application)
            .filter(
                Application.candidate_id == candidate_id
            )
            .order_by(Application.created_at.desc())
            .all()
        )

    # ==================================================
    # UPDATE RECRUITMENT STATUS
    # ==================================================

    @staticmethod
    def update_status(
        db: Session,
        application_id: int,
        data: ApplicationStatusUpdate,
    ):

        application = ApplicationService.get_application(
            db=db,
            application_id=application_id,
        )

        application.status = data.status

        # Keep shortlist flag synchronized with pipeline
        if data.status == "shortlisted":
            application.shortlisted = True

        elif data.status in {
            "applied",
            "screened",
            "rejected",
        }:
            application.shortlisted = False

        db.commit()
        db.refresh(application)

        return application

    # ==================================================
    # UPDATE AI SCORES
    # ==================================================

    @staticmethod
    def update_scores(
        db: Session,
        application_id: int,
        data: ApplicationScoreUpdate,
    ):

        application = ApplicationService.get_application(
            db=db,
            application_id=application_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                application,
                field,
                value,
            )

        db.commit()
        db.refresh(application)

        return application

    # ==================================================
    # DELETE APPLICATION
    # ==================================================

    @staticmethod
    def delete_application(
        db: Session,
        application_id: int,
    ):

        application = ApplicationService.get_application(
            db=db,
            application_id=application_id,
        )

        db.delete(application)
        db.commit()

        return {
            "message": "Application deleted successfully",
            "application_id": application_id,
        }