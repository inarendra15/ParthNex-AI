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
# DATABASE MODEL
# ======================================================

from app.models.resume import Resume


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
        shortlist_threshold: float = 65.0
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
            # Add Phase 7 scores
            # ----------------------------------------------

            enriched_candidate = (
                candidate.copy()
            )

            enriched_candidate[
                "section_score"
            ] = section_result["section_score"]

            enriched_candidate[
                "experience_score"
            ] = experience_result[
                "experience_score"
            ]

            enriched_candidate[
                "quality_score"
            ] = quality_result["quality_score"]

            enriched_candidates.append(
                enriched_candidate
            )

        # ==================================================
        # 3. MULTI-FACTOR RANKING
        # ==================================================

        ranked_candidates = CandidateRanker.rank(
            enriched_candidates
        )

        # ==================================================
        # 3.1 DEDUPLICATE CANDIDATES
        # Keep only the highest-ranked resume per candidate
        # ==================================================

        unique_candidates = []
        seen_candidate_ids = set()

        for candidate in ranked_candidates:

            candidate_id = candidate["candidate_id"]

            if candidate_id in seen_candidate_ids:
                continue

            seen_candidate_ids.add(candidate_id)

            unique_candidates.append(
                candidate
            )


        # Reassign ranks after deduplication
        for index, candidate in enumerate(
            unique_candidates,
            start=1
        ):
            candidate["rank"] = index


        ranked_candidates = unique_candidates

        # ==================================================
        # 4. AUTOMATIC SHORTLISTING
        # ==================================================

        shortlist_result = (
            ShortlistEngine.shortlist(
                ranked_candidates,
                threshold=shortlist_threshold
            )
        )

        # ==================================================
        # 5. FINAL RESPONSE
        # ==================================================

        return {
            "job_description": job_description,

            "top_k": top_k,

            "ranking_weights": {
                "semantic": (
                    CandidateRanker.SEMANTIC_WEIGHT
                ),
                "skills": (
                    CandidateRanker.SKILL_WEIGHT
                ),
                "experience": (
                    CandidateRanker.EXPERIENCE_WEIGHT
                ),
                "quality": (
                    CandidateRanker.QUALITY_WEIGHT
                ),
                "sections": (
                    CandidateRanker.SECTION_WEIGHT
                )
            },

            "threshold": shortlist_result[
                "threshold"
            ],

            "total_candidates": shortlist_result[
                "total_candidates"
            ],

            "shortlisted_count": shortlist_result[
                "shortlisted_count"
            ],

            "not_shortlisted_count": shortlist_result[
                "not_shortlisted_count"
            ],

            "ranked_candidates": ranked_candidates,

            "shortlisted": shortlist_result[
                "shortlisted"
            ],

            "not_shortlisted": shortlist_result[
                "not_shortlisted"
            ]
        }