from pathlib import Path
import pickle

import faiss
import numpy as np


# ---------------------------------------------------
# Project Structure
#
# ParthNex-AI/
# ├── ai_engine/
# │     └── data/
# │            resume.index
# │            resume_ids.pkl
# └── server/
# ---------------------------------------------------

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
        vector = np.array([embedding], dtype=np.float32)
        self.index.add(vector)
        self.resume_ids.append(resume_id)

    def search(self, embedding, top_k=5):

        if self.index.ntotal == 0:
            print("⚠️ FAISS index is empty.")
            return []

        vector = np.array([embedding], dtype=np.float32)

        distances, indices = self.index.search(vector, top_k)

        results = []

        for distance, idx in zip(distances[0], indices[0]):

            if idx == -1:
                continue

            if idx >= len(self.resume_ids):
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

        print("\n========== SAVING FAISS ==========")
        print("Directory :", DATA_DIR)
        print("Index File:", INDEX_FILE)
        print("IDs File  :", IDS_FILE)
        print("Vectors   :", self.index.ntotal)
        print("Resume IDs:", self.resume_ids)

        faiss.write_index(
            self.index,
            str(INDEX_FILE)
        )

        with open(IDS_FILE, "wb") as f:
            pickle.dump(
                self.resume_ids,
                f
            )

        print("✅ FAISS Saved Successfully\n")

    @classmethod
    def load(cls):

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        if not INDEX_FILE.exists():

            print("⚠️ No existing FAISS index found.")
            print("Creating a new index...\n")

            return cls()

        store = cls()

        store.index = faiss.read_index(
            str(INDEX_FILE)
        )

        if IDS_FILE.exists():

            with open(IDS_FILE, "rb") as f:
                store.resume_ids = pickle.load(f)

        print("\n========== LOADED FAISS ==========")
        print("Vectors   :", store.index.ntotal)
        print("Resume IDs:", store.resume_ids)
        print("==================================\n")

        return store