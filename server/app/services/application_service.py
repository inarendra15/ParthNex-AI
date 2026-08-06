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

from app.services.activity_service import ActivityService


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
        # Create Application
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

            # Flush so application.id is available
            # before the transaction is committed.
            db.flush()

            # ------------------------------------------
            # Audit Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="application_created",
                entity_type="application",
                entity_id=application.id,
                application_id=application.id,
                job_id=application.job_id,
                candidate_id=application.candidate_id,
                title="Application created",
                description=(
                    f"{candidate.full_name} applied "
                    f"for {job.title}."
                ),
                old_status=None,
                new_status="applied",
                commit=False,
            )

            # Application + Activity commit together
            db.commit()
            db.refresh(application)

        except IntegrityError:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Candidate has already applied to this job",
            )

        except Exception:

            db.rollback()
            raise

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
            .order_by(
                Application.created_at.desc(),
                Application.id.desc(),
            )
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

        return (
            db.query(Application)
            .filter(
                Application.job_id == job_id
            )
            .order_by(
                Application.created_at.desc(),
                Application.id.desc(),
            )
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

        return (
            db.query(Application)
            .filter(
                Application.candidate_id
                == candidate_id
            )
            .order_by(
                Application.created_at.desc(),
                Application.id.desc(),
            )
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

        application = (
            ApplicationService.get_application(
                db=db,
                application_id=application_id,
            )
        )

        old_status = application.status
        new_status = data.status

        # ----------------------------------------------
        # No-op Status Update
        # ----------------------------------------------

        if old_status == new_status:
            return application

        # ----------------------------------------------
        # Update Status
        # ----------------------------------------------

        application.status = new_status

        # Keep shortlist flag synchronized with pipeline
        if new_status == "shortlisted":

            application.shortlisted = True

        elif new_status in {
            "applied",
            "screened",
            "rejected",
        }:

            application.shortlisted = False

        try:

            # ------------------------------------------
            # Audit Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type=(
                    "application_status_changed"
                ),
                entity_type="application",
                entity_id=application.id,
                application_id=application.id,
                job_id=application.job_id,
                candidate_id=application.candidate_id,
                title="Application status changed",
                description=(
                    f"Application status changed "
                    f"from {old_status} to "
                    f"{new_status}."
                ),
                old_status=old_status,
                new_status=new_status,
                commit=False,
            )

            db.commit()
            db.refresh(application)

        except Exception:

            db.rollback()
            raise

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

        application = (
            ApplicationService.get_application(
                db=db,
                application_id=application_id,
            )
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------------
        # No Fields Supplied
        # ----------------------------------------------

        if not update_data:
            return application

        # ----------------------------------------------
        # Track Changed Fields
        # ----------------------------------------------

        changed_fields = []

        for field, value in update_data.items():

            old_value = getattr(
                application,
                field,
            )

            if old_value != value:

                setattr(
                    application,
                    field,
                    value,
                )

                changed_fields.append(field)

        # Nothing actually changed
        if not changed_fields:
            return application

        try:

            # ------------------------------------------
            # Audit Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type=(
                    "application_scores_updated"
                ),
                entity_type="application",
                entity_id=application.id,
                application_id=application.id,
                job_id=application.job_id,
                candidate_id=application.candidate_id,
                title="Application AI scores updated",
                description=(
                    "Updated AI scoring fields: "
                    + ", ".join(changed_fields)
                    + "."
                ),
                commit=False,
            )

            db.commit()
            db.refresh(application)

        except Exception:

            db.rollback()
            raise

        return application

    # ==================================================
    # DELETE APPLICATION
    # ==================================================

    @staticmethod
    def delete_application(
        db: Session,
        application_id: int,
    ):

        application = (
            ApplicationService.get_application(
                db=db,
                application_id=application_id,
            )
        )

        # ----------------------------------------------
        # Capture Values Before Delete
        # ----------------------------------------------

        deleted_application_id = application.id
        job_id = application.job_id
        candidate_id = application.candidate_id
        old_status = application.status

        try:

            # ------------------------------------------
            # Audit Activity
            # ------------------------------------------
            #
            # application_id is intentionally NULL here.
            #
            # The activities.application_id column has a
            # real FK to applications.id. If we stored
            # the soon-to-be-deleted application ID,
            # PostgreSQL would prevent the deletion.
            #
            # entity_id preserves the historical ID.
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="application_deleted",
                entity_type="application",
                entity_id=deleted_application_id,
                application_id=None,
                job_id=job_id,
                candidate_id=candidate_id,
                title="Application deleted",
                description=(
                    f"Application "
                    f"{deleted_application_id} "
                    f"was deleted."
                ),
                old_status=old_status,
                new_status=None,
                commit=False,
            )

            db.delete(application)

            db.commit()

        except IntegrityError:

            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Application cannot be deleted "
                    "because related recruitment "
                    "records still exist"
                ),
            )

        except Exception:

            db.rollback()
            raise

        return {
            "message": (
                "Application deleted successfully"
            ),
            "application_id": (
                deleted_application_id
            ),
        }