from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.interview import Interview

from app.schemas.interview_schema import (
    InterviewCreate,
    InterviewFeedbackUpdate,
    InterviewStatusUpdate,
    InterviewUpdate,
)

from app.services.activity_service import ActivityService


class InterviewService:

    # ==================================================
    # CREATE INTERVIEW
    # ==================================================

    @staticmethod
    def create_interview(
        db: Session,
        data: InterviewCreate
    ):

        # ----------------------------------------------
        # Validate Application
        # ----------------------------------------------

        application = (
            db.query(Application)
            .filter(
                Application.id == data.application_id
            )
            .first()
        )

        if application is None:
            return None

        # ----------------------------------------------
        # Prevent Duplicate Interview Round
        # ----------------------------------------------

        existing_round = (
            db.query(Interview)
            .filter(
                Interview.application_id
                == application.id,
                Interview.round_number
                == data.round_number,
            )
            .first()
        )

        if existing_round is not None:
            return {
                "error": "duplicate_round"
            }

        # ----------------------------------------------
        # Create Interview
        # ----------------------------------------------

        interview = Interview(
            application_id=application.id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,

            interview_type=data.interview_type,
            round_number=data.round_number,

            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,

            meeting_link=data.meeting_link,
            interviewer_name=data.interviewer_name,

            status="scheduled",
        )

        try:

            db.add(interview)

            # Flush first so interview.id is available
            # for the activity record.
            db.flush()

            # ------------------------------------------
            # Synchronize Application Pipeline
            # ------------------------------------------

            old_application_status = (
                application.status
            )

            application_status_changed = False

            if application.status not in {
                "selected",
                "rejected",
            }:

                if application.status != "interview":

                    application.status = "interview"

                    application_status_changed = True

            # ------------------------------------------
            # Interview Scheduled Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="interview_scheduled",
                entity_type="interview",
                entity_id=interview.id,
                application_id=interview.application_id,
                job_id=interview.job_id,
                candidate_id=interview.candidate_id,
                title="Interview scheduled",
                description=(
                    f"Interview round "
                    f"{interview.round_number} "
                    f"({interview.interview_type}) "
                    f"was scheduled."
                ),
                old_status=None,
                new_status="scheduled",
                commit=False,
            )

            # ------------------------------------------
            # Application Pipeline Activity
            # ------------------------------------------
            #
            # Scheduling an interview can automatically
            # move an application into the interview
            # stage. Record that transition as well.
            # ------------------------------------------

            if application_status_changed:

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
                        "Application status changed "
                        f"from {old_application_status} "
                        "to interview after interview "
                        "scheduling."
                    ),
                    old_status=old_application_status,
                    new_status="interview",
                    commit=False,
                )

            db.commit()
            db.refresh(interview)

        except IntegrityError:

            db.rollback()

            # The database unique constraint remains
            # the final protection against race
            # conditions.
            return {
                "error": "duplicate_round"
            }

        except Exception:

            db.rollback()
            raise

        return interview

    # ==================================================
    # GET INTERVIEW BY ID
    # ==================================================

    @staticmethod
    def get_interview(
        db: Session,
        interview_id: int
    ):

        return (
            db.query(Interview)
            .filter(
                Interview.id == interview_id
            )
            .first()
        )

    # ==================================================
    # GET ALL INTERVIEWS
    # ==================================================

    @staticmethod
    def get_interviews(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ):

        return (
            db.query(Interview)
            .order_by(
                Interview.scheduled_at.asc(),
                Interview.id.asc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ==================================================
    # GET INTERVIEWS BY APPLICATION
    # ==================================================

    @staticmethod
    def get_application_interviews(
        db: Session,
        application_id: int
    ):

        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if application is None:
            return None

        return (
            db.query(Interview)
            .filter(
                Interview.application_id
                == application_id
            )
            .order_by(
                Interview.round_number.asc(),
                Interview.scheduled_at.asc(),
            )
            .all()
        )

    # ==================================================
    # GET INTERVIEWS BY JOB
    # ==================================================

    @staticmethod
    def get_job_interviews(
        db: Session,
        job_id: int
    ):

        return (
            db.query(Interview)
            .filter(
                Interview.job_id == job_id
            )
            .order_by(
                Interview.scheduled_at.asc(),
                Interview.id.asc(),
            )
            .all()
        )

    # ==================================================
    # UPDATE INTERVIEW DETAILS
    # ==================================================

    @staticmethod
    def update_interview(
        db: Session,
        interview_id: int,
        data: InterviewUpdate
    ):

        interview = (
            InterviewService.get_interview(
                db=db,
                interview_id=interview_id
            )
        )

        if interview is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------------
        # No Fields Supplied
        # ----------------------------------------------

        if not update_data:
            return interview

        # ----------------------------------------------
        # Prevent Duplicate Round During Update
        # ----------------------------------------------

        new_round_number = update_data.get(
            "round_number"
        )

        if (
            new_round_number is not None
            and new_round_number
            != interview.round_number
        ):

            existing_round = (
                db.query(Interview)
                .filter(
                    Interview.application_id
                    == interview.application_id,
                    Interview.round_number
                    == new_round_number,
                    Interview.id
                    != interview.id,
                )
                .first()
            )

            if existing_round is not None:
                return {
                    "error": "duplicate_round"
                }

        # ----------------------------------------------
        # Detect Real Changes
        # ----------------------------------------------

        changed_fields = []

        for field, value in update_data.items():

            old_value = getattr(
                interview,
                field
            )

            if old_value != value:

                setattr(
                    interview,
                    field,
                    value
                )

                changed_fields.append(field)

        # No-op update
        if not changed_fields:
            return interview

        try:

            # ------------------------------------------
            # Interview Details Updated Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type=(
                    "interview_details_updated"
                ),
                entity_type="interview",
                entity_id=interview.id,
                application_id=interview.application_id,
                job_id=interview.job_id,
                candidate_id=interview.candidate_id,
                title="Interview details updated",
                description=(
                    "Updated interview fields: "
                    + ", ".join(changed_fields)
                    + "."
                ),
                commit=False,
            )

            db.commit()
            db.refresh(interview)

        except IntegrityError:

            db.rollback()

            return {
                "error": "duplicate_round"
            }

        except Exception:

            db.rollback()
            raise

        return interview

    # ==================================================
    # UPDATE INTERVIEW STATUS
    # ==================================================

    @staticmethod
    def update_status(
        db: Session,
        interview_id: int,
        data: InterviewStatusUpdate
    ):

        interview = (
            InterviewService.get_interview(
                db=db,
                interview_id=interview_id
            )
        )

        if interview is None:
            return None

        old_status = interview.status
        new_status = data.status

        # ----------------------------------------------
        # No-op Status Update
        # ----------------------------------------------

        if old_status == new_status:
            return interview

        interview.status = new_status

        # ----------------------------------------------
        # Select Activity Type
        # ----------------------------------------------

        activity_type_map = {
            "scheduled": "interview_scheduled",
            "completed": "interview_completed",
            "cancelled": "interview_cancelled",
            "rescheduled": "interview_rescheduled",
            "no_show": "interview_no_show",
        }

        activity_type = activity_type_map.get(
            new_status,
            "interview_status_changed",
        )

        try:

            ActivityService.log_activity(
                db=db,
                activity_type=activity_type,
                entity_type="interview",
                entity_id=interview.id,
                application_id=interview.application_id,
                job_id=interview.job_id,
                candidate_id=interview.candidate_id,
                title="Interview status changed",
                description=(
                    f"Interview status changed "
                    f"from {old_status} to "
                    f"{new_status}."
                ),
                old_status=old_status,
                new_status=new_status,
                commit=False,
            )

            db.commit()
            db.refresh(interview)

        except Exception:

            db.rollback()
            raise

        return interview

    # ==================================================
    # ADD / UPDATE INTERVIEW FEEDBACK
    # ==================================================

    @staticmethod
    def update_feedback(
        db: Session,
        interview_id: int,
        data: InterviewFeedbackUpdate
    ):

        interview = (
            InterviewService.get_interview(
                db=db,
                interview_id=interview_id
            )
        )

        if interview is None:
            return None

        # ----------------------------------------------
        # Capture Existing State
        # ----------------------------------------------

        old_status = interview.status

        old_rating = interview.rating
        old_feedback = interview.feedback
        old_recommendation = (
            interview.recommendation
        )

        # ----------------------------------------------
        # Detect Whether Anything Actually Changed
        # ----------------------------------------------

        feedback_changed = (
            old_rating != data.rating
            or old_feedback != data.feedback
            or old_recommendation
            != data.recommendation
        )

        status_changed = (
            old_status != "completed"
        )

        if (
            not feedback_changed
            and not status_changed
        ):
            return interview

        # ----------------------------------------------
        # Apply Feedback
        # ----------------------------------------------

        interview.rating = data.rating
        interview.feedback = data.feedback
        interview.recommendation = (
            data.recommendation
        )

        # Feedback represents completion.
        interview.status = "completed"

        try:

            # ------------------------------------------
            # Interview Evaluation Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type=(
                    "interview_feedback_updated"
                ),
                entity_type="interview",
                entity_id=interview.id,
                application_id=interview.application_id,
                job_id=interview.job_id,
                candidate_id=interview.candidate_id,
                title="Interview feedback updated",
                description=(
                    "Interview evaluation was "
                    "recorded with recommendation "
                    f"{data.recommendation}."
                ),
                old_status=old_status,
                new_status="completed",
                commit=False,
            )

            db.commit()
            db.refresh(interview)

        except Exception:

            db.rollback()
            raise

        return interview

    # ==================================================
    # DELETE INTERVIEW
    # ==================================================

    @staticmethod
    def delete_interview(
        db: Session,
        interview_id: int
    ):

        interview = (
            InterviewService.get_interview(
                db=db,
                interview_id=interview_id
            )
        )

        if interview is None:
            return False

        # ----------------------------------------------
        # Preserve Historical Information
        # ----------------------------------------------

        deleted_interview_id = interview.id

        application_id = (
            interview.application_id
        )

        job_id = interview.job_id
        candidate_id = interview.candidate_id

        old_status = interview.status

        round_number = interview.round_number

        try:

            # ------------------------------------------
            # Audit Before Delete
            # ------------------------------------------
            #
            # There is no direct interview_id FK in
            # activities, so entity_id safely preserves
            # the deleted interview's historical ID.
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="interview_deleted",
                entity_type="interview",
                entity_id=deleted_interview_id,
                application_id=application_id,
                job_id=job_id,
                candidate_id=candidate_id,
                title="Interview deleted",
                description=(
                    f"Interview round "
                    f"{round_number} was deleted."
                ),
                old_status=old_status,
                new_status=None,
                commit=False,
            )

            db.delete(interview)

            db.commit()

        except Exception:

            db.rollback()
            raise

        return True