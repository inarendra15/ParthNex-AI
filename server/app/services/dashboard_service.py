from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User


class DashboardService:

    # ==================================================
    # 1. OVERALL DASHBOARD SUMMARY
    # ==================================================

    @staticmethod
    def get_summary(
        db: Session
    ):

        # ----------------------------------------------
        # Job Counts
        # ----------------------------------------------

        total_jobs = (
            db.query(func.count(Job.id))
            .scalar()
            or 0
        )

        open_jobs = (
            db.query(func.count(Job.id))
            .filter(
                Job.status == "open"
            )
            .scalar()
            or 0
        )

        closed_jobs = (
            db.query(func.count(Job.id))
            .filter(
                Job.status == "closed"
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Candidate Count
        #
        # Count unique candidates who have applications.
        # ----------------------------------------------

        total_candidates = (
            db.query(
                func.count(
                    func.distinct(
                        Application.candidate_id
                    )
                )
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Resume Count
        # ----------------------------------------------

        total_resumes = (
            db.query(
                func.count(Resume.id)
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Application Count
        # ----------------------------------------------

        total_applications = (
            db.query(
                func.count(Application.id)
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Recruitment Pipeline Counts
        # ----------------------------------------------

        applied = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "applied"
            )
            .scalar()
            or 0
        )

        screened = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "screened"
            )
            .scalar()
            or 0
        )

        shortlisted = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "shortlisted"
            )
            .scalar()
            or 0
        )

        interview = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "interview"
            )
            .scalar()
            or 0
        )

        selected = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "selected"
            )
            .scalar()
            or 0
        )

        rejected = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.status == "rejected"
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # AI Shortlisted Count
        #
        # AI shortlist state is intentionally separate
        # from the recruitment pipeline status.
        # ----------------------------------------------

        ai_shortlisted = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.shortlisted.is_(True)
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Average Ranking Score
        # ----------------------------------------------

        average_ranking_score = (
            db.query(
                func.avg(
                    Application.ranking_score
                )
            )
            .filter(
                Application.ranking_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Average Semantic Score
        # ----------------------------------------------

        average_semantic_score = (
            db.query(
                func.avg(
                    Application.semantic_score
                )
            )
            .filter(
                Application.semantic_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Average Skill Score
        # ----------------------------------------------

        average_skill_score = (
            db.query(
                func.avg(
                    Application.skill_score
                )
            )
            .filter(
                Application.skill_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Conversion Rates
        # ----------------------------------------------

        ai_shortlist_rate = 0.0
        selection_rate = 0.0

        if total_applications > 0:

            ai_shortlist_rate = round(
                (
                    ai_shortlisted
                    / total_applications
                )
                * 100,
                2
            )

            selection_rate = round(
                (
                    selected
                    / total_applications
                )
                * 100,
                2
            )

        # ----------------------------------------------
        # Final Summary Response
        # ----------------------------------------------

        return {

            "jobs": {
                "total": total_jobs,
                "open": open_jobs,
                "closed": closed_jobs
            },

            "candidates": {
                "total": total_candidates
            },

            "resumes": {
                "total": total_resumes
            },

            "applications": {
                "total": total_applications,
                "ai_shortlisted": ai_shortlisted
            },

            "pipeline": {
                "applied": applied,
                "screened": screened,
                "shortlisted": shortlisted,
                "interview": interview,
                "selected": selected,
                "rejected": rejected
            },

            "average_scores": {

                "ranking": round(
                    float(
                        average_ranking_score
                        or 0
                    ),
                    2
                ),

                "semantic": round(
                    float(
                        average_semantic_score
                        or 0
                    ),
                    2
                ),

                "skills": round(
                    float(
                        average_skill_score
                        or 0
                    ),
                    2
                )
            },

            "conversion_rates": {

                "ai_shortlist_rate": (
                    ai_shortlist_rate
                ),

                "selection_rate": (
                    selection_rate
                )
            }
        }

    # ==================================================
    # 2. PER-JOB ANALYTICS
    # ==================================================

    @staticmethod
    def get_job_analytics(
        db: Session,
        job_id: int
    ):

        # ----------------------------------------------
        # Find Job
        # ----------------------------------------------

        job = (
            db.query(Job)
            .filter(
                Job.id == job_id
            )
            .first()
        )

        if job is None:
            return None

        # ----------------------------------------------
        # Total Applications
        # ----------------------------------------------

        total_applications = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.job_id == job_id
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Helper Function for Pipeline Counts
        # ----------------------------------------------

        def status_count(
            status: str
        ):

            return (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job_id,
                    Application.status == status
                )
                .scalar()
                or 0
            )

        # ----------------------------------------------
        # Recruitment Pipeline
        # ----------------------------------------------

        applied = status_count(
            "applied"
        )

        screened = status_count(
            "screened"
        )

        shortlisted = status_count(
            "shortlisted"
        )

        interview = status_count(
            "interview"
        )

        selected = status_count(
            "selected"
        )

        rejected = status_count(
            "rejected"
        )

        # ----------------------------------------------
        # AI Shortlisted Count
        # ----------------------------------------------

        ai_shortlisted = (
            db.query(
                func.count(Application.id)
            )
            .filter(
                Application.job_id == job_id,
                Application.shortlisted.is_(True)
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Average Ranking Score
        # ----------------------------------------------

        average_ranking_score = (
            db.query(
                func.avg(
                    Application.ranking_score
                )
            )
            .filter(
                Application.job_id == job_id,
                Application.ranking_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Average Semantic Score
        # ----------------------------------------------

        average_semantic_score = (
            db.query(
                func.avg(
                    Application.semantic_score
                )
            )
            .filter(
                Application.job_id == job_id,
                Application.semantic_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Average Skill Score
        # ----------------------------------------------

        average_skill_score = (
            db.query(
                func.avg(
                    Application.skill_score
                )
            )
            .filter(
                Application.job_id == job_id,
                Application.skill_score.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Conversion Rates
        # ----------------------------------------------

        ai_shortlist_rate = 0.0
        interview_rate = 0.0
        selection_rate = 0.0
        rejection_rate = 0.0

        if total_applications > 0:

            ai_shortlist_rate = round(
                (
                    ai_shortlisted
                    / total_applications
                )
                * 100,
                2
            )

            interview_rate = round(
                (
                    interview
                    / total_applications
                )
                * 100,
                2
            )

            selection_rate = round(
                (
                    selected
                    / total_applications
                )
                * 100,
                2
            )

            rejection_rate = round(
                (
                    rejected
                    / total_applications
                )
                * 100,
                2
            )

        # ----------------------------------------------
        # Final Per-Job Response
        # ----------------------------------------------

        return {

            "job": {

                "id": job.id,

                "title": job.title,

                "company": job.company,

                "location": job.location,

                "employment_type": (
                    job.employment_type
                ),

                "status": job.status
            },

            "applications": {

                "total": (
                    total_applications
                ),

                "ai_shortlisted": (
                    ai_shortlisted
                )
            },

            "pipeline": {

                "applied": applied,

                "screened": screened,

                "shortlisted": shortlisted,

                "interview": interview,

                "selected": selected,

                "rejected": rejected
            },

            "average_scores": {

                "ranking": round(
                    float(
                        average_ranking_score
                        or 0
                    ),
                    2
                ),

                "semantic": round(
                    float(
                        average_semantic_score
                        or 0
                    ),
                    2
                ),

                "skills": round(
                    float(
                        average_skill_score
                        or 0
                    ),
                    2
                )
            },

            "conversion_rates": {

                "ai_shortlist_rate": (
                    ai_shortlist_rate
                ),

                "interview_rate": (
                    interview_rate
                ),

                "selection_rate": (
                    selection_rate
                ),

                "rejection_rate": (
                    rejection_rate
                )
            }
        }

    # ==================================================
    # 3. TOP CANDIDATES FOR A JOB
    # ==================================================

    @staticmethod
    def get_top_candidates(
        db: Session,
        job_id: int,
        limit: int = 10
    ):

        # ----------------------------------------------
        # Validate Job
        # ----------------------------------------------

        job = (
            db.query(Job)
            .filter(
                Job.id == job_id
            )
            .first()
        )

        if job is None:
            return None

        # ----------------------------------------------
        # Validate Limit
        #
        # This also protects the service if it is called
        # directly outside the FastAPI endpoint.
        # ----------------------------------------------

        limit = max(
            1,
            min(
                limit,
                100
            )
        )

        # ----------------------------------------------
        # Query Persisted Candidate Rankings
        #
        # Application.candidate_id -> User.id
        # Application.resume_id    -> Resume.id
        #
        # No embedding generation, FAISS search or
        # resume parsing is needed here.
        # ----------------------------------------------

        results = (
            db.query(
                Application,
                User,
                Resume
            )
            .join(
                User,
                User.id
                == Application.candidate_id
            )
            .join(
                Resume,
                Resume.id
                == Application.resume_id
            )
            .filter(
                Application.job_id == job_id
            )
            .order_by(
                Application.ranking_score
                .desc()
                .nullslast(),

                Application.id.asc()
            )
            .limit(limit)
            .all()
        )

        # ----------------------------------------------
        # Build Candidate Response
        # ----------------------------------------------

        candidates = []

        for rank, (
            application,
            user,
            resume
        ) in enumerate(
            results,
            start=1
        ):

            candidates.append(
                {

                    "rank": rank,

                    "candidate_id": (
                        user.id
                    ),

                    "candidate_name": (
                        user.full_name
                    ),

                    "email": (
                        user.email
                    ),

                    "resume_id": (
                        resume.id
                    ),

                    "filename": (
                        resume.filename
                    ),

                    "ranking_score": (
                        application.ranking_score
                    ),

                    "semantic_score": (
                        application.semantic_score
                    ),

                    "skill_score": (
                        application.skill_score
                    ),

                    "ai_shortlisted": (
                        application.shortlisted
                    ),

                    "status": (
                        application.status
                    )
                }
            )

        # ----------------------------------------------
        # Final Response
        # ----------------------------------------------

        return {

            "job_id": (
                job.id
            ),

            "job_title": (
                job.title
            ),

            "total_returned": (
                len(candidates)
            ),

            "candidates": (
                candidates
            )
        }

    # ==================================================
    # 4. JOB-WISE DASHBOARD OVERVIEW
    # ==================================================

    @staticmethod
    def get_jobs_overview(
        db: Session
    ):

        jobs = (
            db.query(Job)
            .order_by(
                Job.created_at.desc(),
                Job.id.desc()
            )
            .all()
        )

        overview = []

        for job in jobs:

            # ------------------------------------------
            # Application Statistics
            # ------------------------------------------

            total_applications = (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job.id
                )
                .scalar()
                or 0
            )

            ai_shortlisted = (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job.id,
                    Application.shortlisted.is_(True)
                )
                .scalar()
                or 0
            )

            interview = (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job.id,
                    Application.status == "interview"
                )
                .scalar()
                or 0
            )

            selected = (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job.id,
                    Application.status == "selected"
                )
                .scalar()
                or 0
            )

            rejected = (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job.id,
                    Application.status == "rejected"
                )
                .scalar()
                or 0
            )

            # ------------------------------------------
            # Average Ranking Score
            # ------------------------------------------

            average_ranking_score = (
                db.query(
                    func.avg(
                        Application.ranking_score
                    )
                )
                .filter(
                    Application.job_id == job.id,
                    Application.ranking_score.isnot(None)
                )
                .scalar()
            )

            # ------------------------------------------
            # Add Job
            # ------------------------------------------

            overview.append(
                {
                    "job_id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "status": job.status,

                    "total_applications": (
                        total_applications
                    ),

                    "ai_shortlisted": (
                        ai_shortlisted
                    ),

                    "interview": interview,

                    "selected": selected,

                    "rejected": rejected,

                    "average_ranking_score": round(
                        float(
                            average_ranking_score
                            or 0
                        ),
                        2
                    )
                }
            )

        return {
            "jobs": overview
        }