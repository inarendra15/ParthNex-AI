from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:

    @staticmethod
    def create(
        db: Session,
        resume: Resume
    ):
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):
        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .all()
        )

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int
    ):
        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        resume: Resume
    ):
        db.delete(resume)
        db.commit()