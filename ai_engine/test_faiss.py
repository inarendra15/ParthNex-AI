import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.vectorstore.faiss_store import ResumeVectorStore

store = ResumeVectorStore.load()

print("Total vectors:", store.index.ntotal)
print("Resume IDs:", store.resume_ids)