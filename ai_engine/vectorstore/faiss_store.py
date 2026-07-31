from pathlib import Path
import pickle

import faiss
import numpy as np


# Project root = ParthNex-AI
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
INDEX_FILE = DATA_DIR / "resume.index"
IDS_FILE = DATA_DIR / "resume_ids.pkl"


class ResumeVectorStore:

    def __init__(self, dimension=384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.resume_ids = []

    def add(self, resume_id, embedding):
        vector = np.array([embedding], dtype="float32")
        self.index.add(vector)
        self.resume_ids.append(resume_id)

    def search(self, embedding, top_k=5):
        vector = np.array([embedding], dtype="float32")

        distances, indices = self.index.search(vector, top_k)

        results = []

        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            results.append(
                {
                    "resume_id": self.resume_ids[idx],
                    "distance": float(distance)
                }
            )

        return results

    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(INDEX_FILE))

        with open(IDS_FILE, "wb") as f:
            pickle.dump(self.resume_ids, f)

    @classmethod
    def load(cls):

        if not INDEX_FILE.exists():
            return cls()

        store = cls()

        store.index = faiss.read_index(str(INDEX_FILE))

        if IDS_FILE.exists():
            with open(IDS_FILE, "rb") as f:
                store.resume_ids = pickle.load(f)

        return store