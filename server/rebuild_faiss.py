from app.database.session import SessionLocal
from app.models.resume import Resume
from app.services.vector_service import VectorService


def rebuild_faiss():
    db = SessionLocal()

    try:
        resumes = db.query(Resume).all()

        print(f"Found {len(resumes)} resumes in database.")

        for resume in resumes:
            print(
                f"\nIndexing resume {resume.id}: "
                f"{resume.filename}"
            )

            try:
                VectorService.index_resume(
                    resume.id,
                    resume.file_path
                )

                print(
                    f"Resume {resume.id} indexed successfully."
                )

            except Exception as e:
                print(
                    f"Failed to index resume {resume.id}: {e}"
                )

        print("\nFAISS rebuild completed.")

    finally:
        db.close()


if __name__ == "__main__":
    rebuild_faiss()