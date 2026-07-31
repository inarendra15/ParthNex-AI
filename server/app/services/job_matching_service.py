import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Add project root (ParthNex-AI) to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.embeddings.encoder import ResumeEncoder
from ai_engine.vectorstore.faiss_store import ResumeVectorStore

from app.models.resume import Resume
from app.models.user import User


class JobMatchingService:

    @staticmethod
    def match_candidates(
        db: Session,
        job_description: str,
        top_k: int = 5
    ):

        # Clean Job Description
        cleaned_text = TextCleaner.clean(job_description)

        # Generate Embedding
        embedding = ResumeEncoder().encode(cleaned_text)

        # Load FAISS Index
        store = ResumeVectorStore.load()

        # Search Similar Resumes
        search_results = store.search(
            embedding,
            top_k
        )

        candidates = []

        for result in search_results:

            resume = (
                db.query(Resume)
                .filter(
                    Resume.id == result["resume_id"]
                )
                .first()
            )

            if resume is None:
                continue

            user = (
                db.query(User)
                .filter(
                    User.id == resume.user_id
                )
                .first()
            )

            if user is None:
                continue

            candidates.append(
                {
                    "resume_id": resume.id,
                    "candidate_id": user.id,
                    "candidate_name": user.full_name,
                    "email": user.email,
                    "filename": resume.filename,
                    "distance": result["distance"]
                }
            )

        return candidates