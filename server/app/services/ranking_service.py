import sys
from pathlib import Path

from sqlalchemy.orm import Session


# ======================================================
# PROJECT ROOT
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ======================================================
# DATABASE MODELS
# ======================================================

from app.models.resume import Resume
from app.models.application import Application


# ======================================================
# EXISTING SERVICES
# ======================================================

from app.services.job_matching_service import JobMatchingService
from app.services.activity_service import ActivityService


# ======================================================
# AI ENGINE
# ======================================================

from ai_engine.parsers.parser import ResumeParser

from ai_engine.analyzer.section_analyzer import SectionAnalyzer
from ai_engine.analyzer.experience_analyzer import ExperienceAnalyzer
from ai_engine.analyzer.quality_analyzer import QualityAnalyzer

from ai_engine.ranking.candidate_ranker import CandidateRanker
from ai_engine.ranking.shortlist_engine import ShortlistEngine


class RankingService:

    @staticmethod
    def rank_candidates(
        db: Session,
        job_description: str,
        top_k: int = 10,
        shortlist_threshold: float = 65.0,
        job_id: int | None = None
    ):

        # ==================================================
        # 1. RETRIEVE MATCHING RESUMES / CANDIDATES
        # ==================================================

        matched_candidates = (
            JobMatchingService.match_candidates(
                db=db,
                job_description=job_description,
                top_k=top_k
            )
        )

        enriched_candidates = []

        # ==================================================
        # 2. ENRICH EACH RESUME RESULT
        # ==================================================

        for candidate in matched_candidates:

            resume = (
                db.query(Resume)
                .filter(
                    Resume.id
                    == candidate["resume_id"]
                )
                .first()
            )

            if resume is None:
                continue

            # ----------------------------------------------
            # Parse Resume
            # ----------------------------------------------

            try:

                resume_text = ResumeParser.parse(
                    resume.file_path
                )

            except Exception as e:

                print(
                    "Resume parsing failed:",
                    resume.id,
                    e
                )

                continue

            # ----------------------------------------------
            # Resume Section Analysis
            # ----------------------------------------------

            section_result = (
                SectionAnalyzer.analyze(
                    resume_text
                )
            )

            # ----------------------------------------------
            # Experience Analysis
            # ----------------------------------------------

            experience_result = (
                ExperienceAnalyzer.analyze(
                    resume_text
                )
            )

            # ----------------------------------------------
            # Resume Quality Analysis
            # ----------------------------------------------

            quality_result = (
                QualityAnalyzer.analyze(
                    resume_text
                )
            )

            # ----------------------------------------------
            # Add AI Analysis Scores
            # ----------------------------------------------

            candidate["section_score"] = (
                section_result["section_score"]
            )

            candidate["experience_score"] = (
                experience_result[
                    "experience_score"
                ]
            )

            candidate["quality_score"] = (
                quality_result["quality_score"]
            )

            enriched_candidates.append(
                candidate
            )

        # ==================================================
        # 3. RANK ALL RESUME RESULTS
        # ==================================================

        ranked_candidates = (
            CandidateRanker.rank(
                enriched_candidates
            )
        )

        # ==================================================
        # 4. DEDUPLICATE BY CANDIDATE
        # ==================================================
        #
        # One candidate may have multiple resumes stored
        # and indexed in FAISS.
        #
        # FAISS correctly works at resume level, but the
        # ATS ranking must work at candidate level.
        #
        # CandidateRanker returns results ordered by final
        # ranking_score from highest to lowest.
        #
        # Therefore the first occurrence of candidate_id
        # represents that candidate's best-performing
        # resume for this particular job.
        # ==================================================

        unique_candidates = []
        seen_candidate_ids = set()

        for candidate in ranked_candidates:

            candidate_id = (
                candidate["candidate_id"]
            )

            # ----------------------------------------------
            # Candidate Already Represented
            # ----------------------------------------------

            if candidate_id in seen_candidate_ids:
                continue

            # ----------------------------------------------
            # Keep Candidate's Best Ranked Resume
            # ----------------------------------------------

            seen_candidate_ids.add(
                candidate_id
            )

            unique_candidates.append(
                candidate
            )

        # ----------------------------------------------
        # From this point onward the pipeline operates
        # on unique candidates rather than resumes.
        # ----------------------------------------------

        ranked_candidates = (
            unique_candidates
        )

         # ==================================================
        # 5. ADD FINAL CANDIDATE RANK
        # ==================================================

        for index, candidate in enumerate(
            ranked_candidates,
            start=1
        ):

            candidate["rank"] = index

        # ==================================================
        # 6. SHORTLIST UNIQUE CANDIDATES
        # ==================================================

        shortlist_result = (
            ShortlistEngine.shortlist(
                ranked_candidates,
                threshold=shortlist_threshold
            )
        )

        # ==================================================
        # 7. PERSIST AI RESULTS TO APPLICATIONS
        # ==================================================

        if job_id is not None:

            # ----------------------------------------------
            # Candidate IDs Shortlisted By AI
            # ----------------------------------------------

            shortlisted_candidate_ids = {
                candidate["candidate_id"]
                for candidate
                in shortlist_result["shortlisted"]
            }

            # ----------------------------------------------
            # Update Corresponding Applications
            # ----------------------------------------------

            for candidate in ranked_candidates:

                candidate_id = (
                    candidate["candidate_id"]
                )

                application = (
                    db.query(Application)
                    .filter(
                        Application.job_id
                        == job_id,

                        Application.candidate_id
                        == candidate_id
                    )
                    .first()
                )

                # Candidate can exist in FAISS but may
                # not have applied for this particular job.
                if application is None:
                    continue

                # ------------------------------------------
                # Capture State Before AI Update
                # ------------------------------------------

                old_ranking_score = (
                    application.ranking_score
                )

                old_semantic_score = (
                    application.semantic_score
                )

                old_skill_score = (
                    application.skill_score
                )

                old_shortlisted = (
                    application.shortlisted
                )

                old_status = (
                    application.status
                )

                # ------------------------------------------
                # Determine Shortlist Decision
                # ------------------------------------------

                is_shortlisted = (
                    candidate_id
                    in shortlisted_candidate_ids
                )

                # ------------------------------------------
                # Persist AI Scores
                # ------------------------------------------

                application.ranking_score = (
                    candidate["ranking_score"]
                )

                application.semantic_score = (
                    candidate["semantic_score"]
                )

                application.skill_score = (
                    candidate["skill_score"]
                )

                application.shortlisted = (
                    is_shortlisted
                )

                # ------------------------------------------
                # Automatic Pipeline Status
                # ------------------------------------------
                #
                # AI is allowed to modify only early
                # recruitment stages.
                #
                # Recruiter/final decisions such as
                # interview, selected and rejected must
                # never be overwritten by reranking.
                # ------------------------------------------

                if application.status in {
                    "applied",
                    "screened",
                    "shortlisted",
                }:

                    if is_shortlisted:

                        application.status = (
                            "shortlisted"
                        )

                    else:

                        application.status = (
                            "screened"
                        )

                # ------------------------------------------
                # Detect Material AI Changes
                # ------------------------------------------

                scores_changed = (
                    old_ranking_score
                    != application.ranking_score

                    or old_semantic_score
                    != application.semantic_score

                    or old_skill_score
                    != application.skill_score

                    or old_shortlisted
                    != application.shortlisted
                )

                status_changed = (
                    old_status
                    != application.status
                )

                # ------------------------------------------
                # Audit AI Ranking Update
                # ------------------------------------------
                #
                # An activity is generated only when
                # something actually changed.
                #
                # Identical reranking therefore does not
                # create duplicate/noise audit records.
                # ------------------------------------------

                if scores_changed or status_changed:

                    changed_fields = []

                    if (
                        old_ranking_score
                        != application.ranking_score
                    ):

                        changed_fields.append(
                            "ranking_score"
                        )

                    if (
                        old_semantic_score
                        != application.semantic_score
                    ):

                        changed_fields.append(
                            "semantic_score"
                        )

                    if (
                        old_skill_score
                        != application.skill_score
                    ):

                        changed_fields.append(
                            "skill_score"
                        )

                    if (
                        old_shortlisted
                        != application.shortlisted
                    ):

                        changed_fields.append(
                            "shortlisted"
                        )

                    # --------------------------------------
                    # Build Audit Description
                    # --------------------------------------

                    if changed_fields:

                        description = (
                            "AI ranking updated: "
                            + ", ".join(
                                changed_fields
                            )
                            + "."
                        )

                    else:

                        description = (
                            "AI ranking updated."
                        )

                    if status_changed:

                        description += (
                            f" Application status changed "
                            f"from {old_status} "
                            f"to {application.status}."
                        )

                    # --------------------------------------
                    # Log Activity
                    # --------------------------------------
                    #
                    # commit=False is intentional.
                    #
                    # Application updates and activity
                    # records will be committed together
                    # as one transaction below.
                    # --------------------------------------

                    ActivityService.log_activity(
                        db=db,

                        activity_type=(
                            "application_scores_updated"
                        ),

                        entity_type="application",

                        entity_id=application.id,

                        application_id=(
                            application.id
                        ),

                        job_id=(
                            application.job_id
                        ),

                        candidate_id=(
                            application.candidate_id
                        ),

                        title=(
                            "Application AI scores updated"
                        ),

                        description=description,

                        old_status=(
                            old_status
                            if status_changed
                            else None
                        ),

                        new_status=(
                            application.status
                            if status_changed
                            else None
                        ),

                        commit=False,
                    )

            # ----------------------------------------------
            # Commit Application + Audit Updates Together
            # ----------------------------------------------

            db.commit()

        # ==================================================
        # 8. FINAL RESPONSE
        # ==================================================

        return {
            "total_candidates": len(
                ranked_candidates
            ),

            "shortlisted_count": len(
                shortlist_result["shortlisted"]
            ),

            "not_shortlisted_count": len(
                shortlist_result["not_shortlisted"]
            ),

            "ranked_candidates": (
                ranked_candidates
            ),

            "shortlisted": (
                shortlist_result["shortlisted"]
            ),

            "not_shortlisted": (
                shortlist_result[
                    "not_shortlisted"
                ]
            ),
        }