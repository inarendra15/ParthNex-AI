from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.interview import Interview
from app.models.job import Job
from app.models.offer import Offer
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
            .filter(Job.status == "open")
            .scalar()
            or 0
        )

        closed_jobs = (
            db.query(func.count(Job.id))
            .filter(Job.status == "closed")
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Candidate Count
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
        # Application Status Helper
        # ----------------------------------------------

        def application_status_count(
            application_status: str
        ):

            return (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.status
                    == application_status
                )
                .scalar()
                or 0
            )

        # ----------------------------------------------
        # Recruitment Pipeline
        # ----------------------------------------------

        applied = application_status_count(
            "applied"
        )

        screened = application_status_count(
            "screened"
        )

        shortlisted = application_status_count(
            "shortlisted"
        )

        interview = application_status_count(
            "interview"
        )

        selected = application_status_count(
            "selected"
        )

        rejected = application_status_count(
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
                Application.shortlisted.is_(True)
            )
            .scalar()
            or 0
        )

        # ----------------------------------------------
        # Average AI Scores
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
        # Application Conversion Rates
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

        # ==============================================
        # PHASE 12 — INTERVIEW ANALYTICS
        # ==============================================

        total_interviews = (
            db.query(
                func.count(Interview.id)
            )
            .scalar()
            or 0
        )

        def interview_status_count(
            interview_status: str
        ):

            return (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.status
                    == interview_status
                )
                .scalar()
                or 0
            )

        scheduled_interviews = (
            interview_status_count(
                "scheduled"
            )
        )

        completed_interviews = (
            interview_status_count(
                "completed"
            )
        )

        cancelled_interviews = (
            interview_status_count(
                "cancelled"
            )
        )

        rescheduled_interviews = (
            interview_status_count(
                "rescheduled"
            )
        )

        no_show_interviews = (
            interview_status_count(
                "no_show"
            )
        )

        # ----------------------------------------------
        # Average Interview Rating
        # ----------------------------------------------

        average_interview_rating = (
            db.query(
                func.avg(
                    Interview.rating
                )
            )
            .filter(
                Interview.rating.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Interview Recommendation Helper
        # ----------------------------------------------

        def recommendation_count(
            recommendation: str
        ):

            return (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.recommendation
                    == recommendation
                )
                .scalar()
                or 0
            )

        strong_hire = recommendation_count(
            "strong_hire"
        )

        hire = recommendation_count(
            "hire"
        )

        consider = recommendation_count(
            "consider"
        )

        no_hire = recommendation_count(
            "no_hire"
        )

        # ==============================================
        # PHASE 13 — OFFER ANALYTICS
        # ==============================================

        total_offers = (
            db.query(
                func.count(Offer.id)
            )
            .scalar()
            or 0
        )

        def offer_status_count(
            offer_status: str
        ):

            return (
                db.query(
                    func.count(Offer.id)
                )
                .filter(
                    Offer.status == offer_status
                )
                .scalar()
                or 0
            )

        draft_offers = offer_status_count(
            "draft"
        )

        sent_offers = offer_status_count(
            "sent"
        )

        accepted_offers = offer_status_count(
            "accepted"
        )

        rejected_offers = offer_status_count(
            "rejected"
        )

        withdrawn_offers = offer_status_count(
            "withdrawn"
        )

        expired_offers = offer_status_count(
            "expired"
        )

        # ----------------------------------------------
        # Offer Conversion Rates
        # ----------------------------------------------

        offer_acceptance_rate = 0.0
        offer_rejection_rate = 0.0
        offer_pending_rate = 0.0

        if total_offers > 0:

            offer_acceptance_rate = round(
                (
                    accepted_offers
                    / total_offers
                )
                * 100,
                2
            )

            offer_rejection_rate = round(
                (
                    rejected_offers
                    / total_offers
                )
                * 100,
                2
            )

            pending_offers = (
                draft_offers
                + sent_offers
            )

            offer_pending_rate = round(
                (
                    pending_offers
                    / total_offers
                )
                * 100,
                2
            )

        # ==============================================
        # FINAL SUMMARY RESPONSE
        # ==============================================

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
            },

            # ------------------------------------------
            # Phase 12 Interview Analytics
            # ------------------------------------------

            "interviews": {

                "total": (
                    total_interviews
                ),

                "scheduled": (
                    scheduled_interviews
                ),

                "completed": (
                    completed_interviews
                ),

                "cancelled": (
                    cancelled_interviews
                ),

                "rescheduled": (
                    rescheduled_interviews
                ),

                "no_show": (
                    no_show_interviews
                )
            },

            "interview_evaluation": {

                "average_rating": round(
                    float(
                        average_interview_rating
                        or 0
                    ),
                    2
                ),

                "strong_hire": (
                    strong_hire
                ),

                "hire": (
                    hire
                ),

                "consider": (
                    consider
                ),

                "no_hire": (
                    no_hire
                )
            },

            # ------------------------------------------
            # Phase 13 Offer Analytics
            # ------------------------------------------

            "offers": {

                "total": (
                    total_offers
                ),

                "draft": (
                    draft_offers
                ),

                "sent": (
                    sent_offers
                ),

                "accepted": (
                    accepted_offers
                ),

                "rejected": (
                    rejected_offers
                ),

                "withdrawn": (
                    withdrawn_offers
                ),

                "expired": (
                    expired_offers
                )
            },

            "offer_conversion": {

                "acceptance_rate": (
                    offer_acceptance_rate
                ),

                "rejection_rate": (
                    offer_rejection_rate
                ),

                "pending_rate": (
                    offer_pending_rate
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
        # Application Status Helper
        # ----------------------------------------------

        def status_count(
            application_status: str
        ):

            return (
                db.query(
                    func.count(Application.id)
                )
                .filter(
                    Application.job_id == job_id,
                    Application.status
                    == application_status
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
        # Average AI Scores
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
        # Application Conversion Rates
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

        # ==============================================
        # PHASE 12 — PER-JOB INTERVIEW ANALYTICS
        # ==============================================

        total_interviews = (
            db.query(
                func.count(Interview.id)
            )
            .filter(
                Interview.job_id == job_id
            )
            .scalar()
            or 0
        )

        def interview_status_count(
            interview_status: str
        ):

            return (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.job_id == job_id,
                    Interview.status
                    == interview_status
                )
                .scalar()
                or 0
            )

        scheduled_interviews = (
            interview_status_count(
                "scheduled"
            )
        )

        completed_interviews = (
            interview_status_count(
                "completed"
            )
        )

        cancelled_interviews = (
            interview_status_count(
                "cancelled"
            )
        )

        rescheduled_interviews = (
            interview_status_count(
                "rescheduled"
            )
        )

        no_show_interviews = (
            interview_status_count(
                "no_show"
            )
        )

        # ----------------------------------------------
        # Per-Job Average Interview Rating
        # ----------------------------------------------

        average_interview_rating = (
            db.query(
                func.avg(
                    Interview.rating
                )
            )
            .filter(
                Interview.job_id == job_id,
                Interview.rating.isnot(None)
            )
            .scalar()
        )

        # ----------------------------------------------
        # Recommendation Helper
        # ----------------------------------------------

        def recommendation_count(
            recommendation: str
        ):

            return (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.job_id == job_id,
                    Interview.recommendation
                    == recommendation
                )
                .scalar()
                or 0
            )

        strong_hire = (
            recommendation_count(
                "strong_hire"
            )
        )

        hire = (
            recommendation_count(
                "hire"
            )
        )

        consider = (
            recommendation_count(
                "consider"
            )
        )

        no_hire = (
            recommendation_count(
                "no_hire"
            )
        )

        # ==============================================
        # PHASE 13 — PER-JOB OFFER ANALYTICS
        # ==============================================

        total_offers = (
            db.query(
                func.count(Offer.id)
            )
            .filter(
                Offer.job_id == job_id
            )
            .scalar()
            or 0
        )

        def offer_status_count(
            offer_status: str
        ):

            return (
                db.query(
                    func.count(Offer.id)
                )
                .filter(
                    Offer.job_id == job_id,
                    Offer.status == offer_status
                )
                .scalar()
                or 0
            )

        draft_offers = (
            offer_status_count(
                "draft"
            )
        )

        sent_offers = (
            offer_status_count(
                "sent"
            )
        )

        accepted_offers = (
            offer_status_count(
                "accepted"
            )
        )

        rejected_offers = (
            offer_status_count(
                "rejected"
            )
        )

        withdrawn_offers = (
            offer_status_count(
                "withdrawn"
            )
        )

        expired_offers = (
            offer_status_count(
                "expired"
            )
        )

        # ----------------------------------------------
        # Per-Job Offer Conversion Rates
        # ----------------------------------------------

        offer_acceptance_rate = 0.0
        offer_rejection_rate = 0.0
        offer_pending_rate = 0.0

        if total_offers > 0:

            offer_acceptance_rate = round(
                (
                    accepted_offers
                    / total_offers
                )
                * 100,
                2
            )

            offer_rejection_rate = round(
                (
                    rejected_offers
                    / total_offers
                )
                * 100,
                2
            )

            pending_offers = (
                draft_offers
                + sent_offers
            )

            offer_pending_rate = round(
                (
                    pending_offers
                    / total_offers
                )
                * 100,
                2
            )

        # ==============================================
        # FINAL PER-JOB RESPONSE
        # ==============================================

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
            },

            # ------------------------------------------
            # Phase 12 Interview Analytics
            # ------------------------------------------

            "interviews": {

                "total": (
                    total_interviews
                ),

                "scheduled": (
                    scheduled_interviews
                ),

                "completed": (
                    completed_interviews
                ),

                "cancelled": (
                    cancelled_interviews
                ),

                "rescheduled": (
                    rescheduled_interviews
                ),

                "no_show": (
                    no_show_interviews
                )
            },

            "interview_evaluation": {

                "average_rating": round(
                    float(
                        average_interview_rating
                        or 0
                    ),
                    2
                ),

                "strong_hire": (
                    strong_hire
                ),

                "hire": (
                    hire
                ),

                "consider": (
                    consider
                ),

                "no_hire": (
                    no_hire
                )
            },

            # ------------------------------------------
            # Phase 13 Offer Analytics
            # ------------------------------------------

            "offers": {

                "total": (
                    total_offers
                ),

                "draft": (
                    draft_offers
                ),

                "sent": (
                    sent_offers
                ),

                "accepted": (
                    accepted_offers
                ),

                "rejected": (
                    rejected_offers
                ),

                "withdrawn": (
                    withdrawn_offers
                ),

                "expired": (
                    expired_offers
                )
            },

            "offer_conversion": {

                "acceptance_rate": (
                    offer_acceptance_rate
                ),

                "rejection_rate": (
                    offer_rejection_rate
                ),

                "pending_rate": (
                    offer_pending_rate
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

            # ==========================================
            # APPLICATION STATISTICS
            # ==========================================

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

            # ==========================================
            # INTERVIEW STATISTICS
            # ==========================================

            total_interviews = (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.job_id == job.id
                )
                .scalar()
                or 0
            )

            scheduled_interviews = (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.job_id == job.id,
                    Interview.status == "scheduled"
                )
                .scalar()
                or 0
            )

            completed_interviews = (
                db.query(
                    func.count(Interview.id)
                )
                .filter(
                    Interview.job_id == job.id,
                    Interview.status == "completed"
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
            # Average Interview Rating
            # ------------------------------------------

            average_interview_rating = (
                db.query(
                    func.avg(
                        Interview.rating
                    )
                )
                .filter(
                    Interview.job_id == job.id,
                    Interview.rating.isnot(None)
                )
                .scalar()
            )

            # ==========================================
            # PHASE 13 — OFFER STATISTICS
            # ==========================================

            total_offers = (
                db.query(
                    func.count(Offer.id)
                )
                .filter(
                    Offer.job_id == job.id
                )
                .scalar()
                or 0
            )

            def job_offer_status_count(
                offer_status: str
            ):

                return (
                    db.query(
                        func.count(Offer.id)
                    )
                    .filter(
                        Offer.job_id == job.id,
                        Offer.status == offer_status
                    )
                    .scalar()
                    or 0
                )

            draft_offers = (
                job_offer_status_count(
                    "draft"
                )
            )

            sent_offers = (
                job_offer_status_count(
                    "sent"
                )
            )

            accepted_offers = (
                job_offer_status_count(
                    "accepted"
                )
            )

            rejected_offers = (
                job_offer_status_count(
                    "rejected"
                )
            )

            withdrawn_offers = (
                job_offer_status_count(
                    "withdrawn"
                )
            )

            expired_offers = (
                job_offer_status_count(
                    "expired"
                )
            )

            offer_acceptance_rate = 0.0

            if total_offers > 0:

                offer_acceptance_rate = round(
                    (
                        accepted_offers
                        / total_offers
                    )
                    * 100,
                    2
                )

            # ==========================================
            # ADD JOB TO OVERVIEW
            # ==========================================

            overview.append(
                {

                    "job_id": job.id,

                    "title": job.title,

                    "company": job.company,

                    "status": job.status,

                    # ----------------------------------
                    # Application Analytics
                    # ----------------------------------

                    "total_applications": (
                        total_applications
                    ),

                    "ai_shortlisted": (
                        ai_shortlisted
                    ),

                    "interview": (
                        interview
                    ),

                    "selected": (
                        selected
                    ),

                    "rejected": (
                        rejected
                    ),

                    "average_ranking_score": round(
                        float(
                            average_ranking_score
                            or 0
                        ),
                        2
                    ),

                    # ----------------------------------
                    # Phase 12 Interview Analytics
                    # ----------------------------------

                    "total_interviews": (
                        total_interviews
                    ),

                    "scheduled_interviews": (
                        scheduled_interviews
                    ),

                    "completed_interviews": (
                        completed_interviews
                    ),

                    "average_interview_rating": round(
                        float(
                            average_interview_rating
                            or 0
                        ),
                        2
                    ),

                    # ----------------------------------
                    # Phase 13 Offer Analytics
                    # ----------------------------------

                    "total_offers": (
                        total_offers
                    ),

                    "draft_offers": (
                        draft_offers
                    ),

                    "sent_offers": (
                        sent_offers
                    ),

                    "accepted_offers": (
                        accepted_offers
                    ),

                    "rejected_offers": (
                        rejected_offers
                    ),

                    "withdrawn_offers": (
                        withdrawn_offers
                    ),

                    "expired_offers": (
                        expired_offers
                    ),

                    "offer_acceptance_rate": (
                        offer_acceptance_rate
                    )
                }
            )

        return {
            "jobs": overview
        }