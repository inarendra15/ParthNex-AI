import sys
from pathlib import Path

# Add project root (ParthNex-AI) to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.embeddings.encoder import ResumeEncoder
from ai_engine.vectorstore.faiss_store import ResumeVectorStore


class VectorService:

    @staticmethod
    def index_resume(resume_id: int, file_path: str):

        # Parse Resume
        text = ResumeParser.parse(file_path)

        # Clean Resume
        text = TextCleaner.clean(text)

        # Generate Embedding
        embedding = ResumeEncoder().encode(text)

        # Load existing FAISS index (creates a new one if none exists)
        store = ResumeVectorStore.load()

        # Add Resume
        store.add(resume_id, embedding)

        # Save updated index
        store.save()