from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job_schema import JobCreate, JobUpdate


class JobService:

    # ======================================================
    # CREATE JOB
    # ======================================================

    @staticmethod
    def create_job(
        db: Session,
        data: JobCreate
    ) -> Job:

        job = Job(
            title=data.title,
            company=data.company,
            location=data.location,
            employment_type=data.employment_type,
            description=data.description,
            status="open"
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    # ======================================================
    # GET JOB
    # ======================================================

    @staticmethod
    def get_job(
        db: Session,
        job_id: int
    ) -> Job:

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        return job

    # ======================================================
    # LIST JOBS
    # ======================================================

    @staticmethod
    def list_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 20
    ):

        return (
            db.query(Job)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ======================================================
    # UPDATE JOB
    # ======================================================

    @staticmethod
    def update_job(
        db: Session,
        job_id: int,
        data: JobUpdate
    ) -> Job:

        job = JobService.get_job(
            db,
            job_id
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                job,
                field,
                value
            )

        db.commit()
        db.refresh(job)

        return job

    # ======================================================
    # DELETE JOB
    # ======================================================

    @staticmethod
    def delete_job(
        db: Session,
        job_id: int
    ):

        job = JobService.get_job(
            db,
            job_id
        )

        db.delete(job)
        db.commit()

        return {
            "message": "Job deleted successfully",
            "job_id": job_id
        }