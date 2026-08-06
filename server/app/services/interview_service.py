from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.interview import Interview

from app.schemas.interview_schema import (
    InterviewCreate,
    InterviewFeedbackUpdate,
    InterviewStatusUpdate,
    InterviewUpdate,
)


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
        #
        # job_id and candidate_id are derived from the
        # application instead of being trusted from
        # client input.
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

        db.add(interview)

        # ----------------------------------------------
        # Synchronize Application Pipeline
        #
        # Do not downgrade terminal states.
        # ----------------------------------------------

        if application.status not in {
            "selected",
            "rejected",
        }:
            application.status = "interview"

        db.commit()
        db.refresh(interview)

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
        # Apply Updates
        # ----------------------------------------------

        for field, value in update_data.items():
            setattr(
                interview,
                field,
                value
            )

        db.commit()
        db.refresh(interview)

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

        interview.status = data.status

        db.commit()
        db.refresh(interview)

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

        interview.rating = data.rating
        interview.feedback = data.feedback
        interview.recommendation = (
            data.recommendation
        )

        # Feedback represents completion of the
        # interview round.
        interview.status = "completed"

        db.commit()
        db.refresh(interview)

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

        db.delete(interview)
        db.commit()

        return True