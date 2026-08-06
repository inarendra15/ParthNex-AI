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
        # 1. RETRIEVE MATCHING CANDIDATES
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
        # 2. ENRICH EACH CANDIDATE
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
                    f"Ranking parse failed for "
                    f"resume {resume.id}: {e}"
                )

                continue

            # ----------------------------------------------
            # Section Analysis
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
            # Quality Analysis
            # ----------------------------------------------

            quality_result = (
                QualityAnalyzer.analyze(
                    resume_text
                )
            )

            # ----------------------------------------------
            # Add Phase 7 Scores
            # ----------------------------------------------

            enriched_candidate = (
                candidate.copy()
            )

            enriched_candidate[
                "section_score"
            ] = section_result[
                "section_score"
            ]

            enriched_candidate[
                "experience_score"
            ] = experience_result[
                "experience_score"
            ]

            enriched_candidate[
                "quality_score"
            ] = quality_result[
                "quality_score"
            ]

            enriched_candidates.append(
                enriched_candidate
            )

        # ==================================================
        # 3. MULTI-FACTOR RANKING
        # ==================================================

        ranked_candidates = (
            CandidateRanker.rank(
                enriched_candidates
            )
        )

        # ==================================================
        # 4. DEDUPLICATE CANDIDATES
        #
        # Keep only the highest-ranked resume
        # for each candidate.
        # ==================================================

        unique_candidates = []

        seen_candidate_ids = set()

        for candidate in ranked_candidates:

            candidate_id = (
                candidate["candidate_id"]
            )

            if candidate_id in seen_candidate_ids:
                continue

            seen_candidate_ids.add(
                candidate_id
            )

            unique_candidates.append(
                candidate
            )

        # ----------------------------------------------
        # Reassign ranks after deduplication
        # ----------------------------------------------

        for index, candidate in enumerate(
            unique_candidates,
            start=1
        ):

            candidate["rank"] = index

        ranked_candidates = (
            unique_candidates
        )

        # ==================================================
        # 5. AUTOMATIC SHORTLISTING
        # ==================================================

        shortlist_result = (
            ShortlistEngine.shortlist(
                ranked_candidates,
                threshold=shortlist_threshold
            )
        )

        # ==================================================
        # 6. PERSIST AI RESULTS INTO APPLICATIONS
        #
        # This runs only when a stored job_id is supplied.
        #
        # Manual /ranking/candidates calls will continue
        # working without changing application records.
        # ==================================================

        if job_id is not None:

            # ----------------------------------------------
            # Candidate IDs shortlisted by AI
            # ----------------------------------------------

            shortlisted_candidate_ids = {
                candidate["candidate_id"]
                for candidate
                in shortlist_result["shortlisted"]
            }

            # ----------------------------------------------
            # Update corresponding applications
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
                # Determine shortlist decision
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
                    "shortlisted"
                }:

                    if is_shortlisted:

                        application.status = (
                            "shortlisted"
                        )

                    else:

                        application.status = (
                            "screened"
                        )

            # ----------------------------------------------
            # Commit all application updates together
            # ----------------------------------------------

            db.commit()

        # ==================================================
        # 7. FINAL RESPONSE
        # ==================================================

        return {

            "job_description": (
                job_description
            ),

            "top_k": top_k,

            "ranking_weights": {

                "semantic": (
                    CandidateRanker
                    .SEMANTIC_WEIGHT
                ),

                "skills": (
                    CandidateRanker
                    .SKILL_WEIGHT
                ),

                "experience": (
                    CandidateRanker
                    .EXPERIENCE_WEIGHT
                ),

                "quality": (
                    CandidateRanker
                    .QUALITY_WEIGHT
                ),

                "sections": (
                    CandidateRanker
                    .SECTION_WEIGHT
                )
            },

            "threshold": (
                shortlist_result[
                    "threshold"
                ]
            ),

            "total_candidates": (
                shortlist_result[
                    "total_candidates"
                ]
            ),

            "shortlisted_count": (
                shortlist_result[
                    "shortlisted_count"
                ]
            ),

            "not_shortlisted_count": (
                shortlist_result[
                    "not_shortlisted_count"
                ]
            ),

            "ranked_candidates": (
                ranked_candidates
            ),

            "shortlisted": (
                shortlist_result[
                    "shortlisted"
                ]
            ),

            "not_shortlisted": (
                shortlist_result[
                    "not_shortlisted"
                ]
            )
        }