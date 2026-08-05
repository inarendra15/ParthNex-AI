import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Add project root (ParthNex-AI) to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.embeddings.encoder import ResumeEncoder
from ai_engine.vectorstore.faiss_store import ResumeVectorStore
from ai_engine.skill_extractor import SkillExtractor
from ai_engine.matcher.skill_matcher import SkillMatcher

from app.models.resume import Resume
from app.models.user import User


class JobMatchingService:

    @staticmethod
    def semantic_score(distance: float):
        score = max(0.0, 100 - distance * 20)
        return round(score, 2)

    @staticmethod
    def match_candidates(
        db: Session,
        job_description: str,
        top_k: int = 5
    ):

        print("\n================ JOB MATCHING STARTED ================\n")

        # Clean job description
        cleaned_job = TextCleaner.clean(job_description)

        # Generate embedding
        embedding = ResumeEncoder().encode(cleaned_job)

        # Extract job skills
        job_skills = SkillExtractor.extract(cleaned_job)

        print("Job Skills:", job_skills)

        # Load FAISS
        store = ResumeVectorStore.load()

        # Search similar resumes
        search_results = store.search(
            embedding,
            top_k
        )

        print("\nFAISS Results:")
        print(search_results)

        candidates = []

        for result in search_results:

            print("\n" + "=" * 60)
            print("Processing Resume ID:", result["resume_id"])

            resume = (
                db.query(Resume)
                .filter(
                    Resume.id == result["resume_id"]
                )
                .first()
            )

            if resume is None:
                print("Resume NOT FOUND")
                continue

            print("Resume File:", resume.filename)
            print("Stored Path:", resume.file_path)

            user = (
                db.query(User)
                .filter(
                    User.id == resume.user_id
                )
                .first()
            )

            if user is None:
                print("User NOT FOUND")
                continue

            print("Candidate:", user.full_name)

            # ------------------------
            # Parse Resume
            # ------------------------

            try:

                print("Parsing Resume...")

                resume_text = ResumeParser.parse(
                    resume.file_path
                )

                resume_text = TextCleaner.clean(
                    resume_text
                )

                print("Resume Parsed Successfully")

            except Exception as e:

                print("PARSING FAILED")
                print(e)

                continue

            # ------------------------
            # Extract Resume Skills
            # ------------------------

            resume_skills = SkillExtractor.extract(
                resume_text
            )

            print("Resume Skills:", resume_skills)

            # ------------------------
            # Skill Matching
            # ------------------------

            skill_result = SkillMatcher.match(
                job_skills,
                resume_skills
            )

            print("Skill Result:", skill_result)

            # ------------------------
            # Semantic Score
            # ------------------------

            semantic_score = JobMatchingService.semantic_score(
                result["distance"]
            )

            overall_score = round(
                semantic_score * 0.7 +
                skill_result["skill_score"] * 0.3,
                2
            )

            print("Semantic Score:", semantic_score)
            print("Overall Score :", overall_score)

            candidate = {
                "candidate_id": user.id,
                "candidate_name": user.full_name,
                "email": user.email,

                "resume_id": resume.id,
                "filename": resume.filename,

                "semantic_score": semantic_score,
                "skill_score": skill_result["skill_score"],
                "overall_score": overall_score,

                "matched_skills": skill_result["matched_skills"],
                "missing_skills": skill_result["missing_skills"]
            }

            print("Candidate Added")
            print(candidate)

            candidates.append(candidate)

        print("\n================ FINAL RESULTS ================\n")
        print(candidates)

        candidates.sort(
            key=lambda x: x["overall_score"],
            reverse=True
        )

        return candidates