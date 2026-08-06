from sqlalchemy.orm import Session

from app.models.activity import Activity


class ActivityService:

    # ==================================================
    # LOG ACTIVITY
    # ==================================================

    @staticmethod
    def log_activity(
        db: Session,
        *,
        activity_type: str,
        entity_type: str,
        title: str,
        entity_id: int | None = None,
        application_id: int | None = None,
        job_id: int | None = None,
        candidate_id: int | None = None,
        description: str | None = None,
        old_status: str | None = None,
        new_status: str | None = None,
        commit: bool = True,
    ):

        activity = Activity(
            application_id=application_id,
            job_id=job_id,
            candidate_id=candidate_id,

            activity_type=activity_type,

            entity_type=entity_type,
            entity_id=entity_id,

            title=title,
            description=description,

            old_status=old_status,
            new_status=new_status,
        )

        db.add(activity)

        if commit:
            db.commit()
            db.refresh(activity)

        else:
            db.flush()

        return activity

    # ==================================================
    # GET ACTIVITY
    # ==================================================

    @staticmethod
    def get_activity(
        db: Session,
        activity_id: int,
    ):

        return (
            db.query(Activity)
            .filter(
                Activity.id == activity_id
            )
            .first()
        )

    # ==================================================
    # LIST RECENT ACTIVITIES
    # ==================================================

    @staticmethod
    def list_activities(
        db: Session,
        limit: int = 50,
    ):

        limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(Activity)
            .order_by(
                Activity.created_at.desc(),
                Activity.id.desc(),
            )
            .limit(limit)
            .all()
        )

    # ==================================================
    # COUNT ACTIVITIES
    # ==================================================

    @staticmethod
    def count_activities(
        db: Session,
    ):

        return (
            db.query(Activity)
            .count()
        )

    # ==================================================
    # APPLICATION TIMELINE
    # ==================================================

    @staticmethod
    def list_application_activities(
        db: Session,
        application_id: int,
    ):

        return (
            db.query(Activity)
            .filter(
                Activity.application_id
                == application_id
            )
            .order_by(
                Activity.created_at.asc(),
                Activity.id.asc(),
            )
            .all()
        )

    # ==================================================
    # JOB ACTIVITIES
    # ==================================================

    @staticmethod
    def list_job_activities(
        db: Session,
        job_id: int,
        limit: int = 100,
    ):

        limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(Activity)
            .filter(
                Activity.job_id == job_id
            )
            .order_by(
                Activity.created_at.desc(),
                Activity.id.desc(),
            )
            .limit(limit)
            .all()
        )

    # ==================================================
    # CANDIDATE ACTIVITIES
    # ==================================================

    @staticmethod
    def list_candidate_activities(
        db: Session,
        candidate_id: int,
        limit: int = 100,
    ):

        limit = max(
            1,
            min(limit, 100)
        )

        return (
            db.query(Activity)
            .filter(
                Activity.candidate_id
                == candidate_id
            )
            .order_by(
                Activity.created_at.desc(),
                Activity.id.desc(),
            )
            .limit(limit)
            .all()
        )