import sys
from pathlib import Path

import numpy as np
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
# AI ENGINE
# ======================================================

from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.embeddings.encoder import ResumeEncoder

from ai_engine.analyzer.section_analyzer import SectionAnalyzer
from ai_engine.analyzer.keyword_analyzer import KeywordAnalyzer
from ai_engine.analyzer.experience_analyzer import ExperienceAnalyzer
from ai_engine.analyzer.quality_analyzer import QualityAnalyzer

from ai_engine.recommendation.suggestion_generator import (
    SuggestionGenerator
)

from ai_engine.scorer.ats_scorer import ATSScorer


class ATSService:

    # ==================================================
    # SEMANTIC SCORE
    # ==================================================

    @staticmethod
    def semantic_score(
        resume_text: str,
        job_description: str
    ) -> float:

        # Clean resume text
        cleaned_resume = TextCleaner.clean(
            resume_text
        )

        # Clean job description
        cleaned_job = TextCleaner.clean(
            job_description
        )

        # Generate embeddings
        encoder = ResumeEncoder()

        resume_embedding = encoder.encode(
            cleaned_resume
        )

        job_embedding = encoder.encode(
            cleaned_job
        )

        # --------------------------------------------------
        # Calculate squared L2 distance
        #
        # This is consistent with FAISS IndexFlatL2 used
        # by the candidate matching system.
        # --------------------------------------------------

        resume_vector = np.asarray(
            resume_embedding,
            dtype=np.float32
        )

        job_vector = np.asarray(
            job_embedding,
            dtype=np.float32
        )

        distance = float(
            np.sum(
                (resume_vector - job_vector) ** 2
            )
        )

        # Same scoring logic used by JobMatchingService
        score = max(
            0.0,
            100.0 - distance * 20.0
        )

        return round(score, 2)

    # ==================================================
    # ATS RESUME ANALYSIS
    # ==================================================

    @staticmethod
    def analyze_resume(
        db: Session,
        resume_id: int,
        job_description: str
    ):

        # --------------------------------------------------
        # Find Resume
        # --------------------------------------------------

        resume = (
            db.query(Resume)
            .filter(
                Resume.id == resume_id
            )
            .first()
        )

        if resume is None:
            return {
                "error": "Resume not found"
            }

        # --------------------------------------------------
        # Parse Resume
        # --------------------------------------------------

        resume_text = ResumeParser.parse(
            resume.file_path
        )

        # --------------------------------------------------
        # Section Analysis
        # --------------------------------------------------

        section = SectionAnalyzer.analyze(
            resume_text
        )

        # --------------------------------------------------
        # Keyword / Skill Gap Analysis
        # --------------------------------------------------

        keyword = KeywordAnalyzer.analyze(
            resume_text,
            job_description
        )

        # --------------------------------------------------
        # Experience Analysis
        # --------------------------------------------------

        experience = ExperienceAnalyzer.analyze(
            resume_text
        )

        # --------------------------------------------------
        # Resume Quality Analysis
        # --------------------------------------------------

        quality = QualityAnalyzer.analyze(
            resume_text
        )

        # --------------------------------------------------
        # Strengths / Weaknesses / Suggestions
        # --------------------------------------------------

        report = SuggestionGenerator.generate(
            section,
            keyword,
            experience
        )

        # --------------------------------------------------
        # Semantic Similarity
        # --------------------------------------------------

        semantic_score = ATSService.semantic_score(
            resume_text,
            job_description
        )

        # --------------------------------------------------
        # Final ATS Score
        #
        # Semantic   = 40%
        # Skills     = 30%
        # Sections   = 15%
        # Experience = 10%
        # Quality    = 5%
        # --------------------------------------------------

        ats_score = ATSScorer.calculate(
            semantic_score=semantic_score,
            skill_score=keyword["skill_score"],
            section_score=section["section_score"],
            experience_score=experience["experience_score"],
            quality_score=quality["quality_score"]
        )

        # --------------------------------------------------
        # Final Response
        # --------------------------------------------------

        return {
            "resume_id": resume.id,
            "filename": resume.filename,

            "ats_score": ats_score,
            "semantic_score": semantic_score,

            "section_analysis": section,

            "keyword_analysis": keyword,

            "experience_analysis": experience,

            "quality_analysis": quality,

            "strengths": report["strengths"],

            "weaknesses": report["weaknesses"],

            "suggestions": report["suggestions"]
        }