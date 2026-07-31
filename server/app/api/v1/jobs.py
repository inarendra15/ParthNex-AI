from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.job_matching_service import JobMatchingService

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/test-match")
def test_match(db: Session = Depends(get_db)):

    job = """
    Python Backend Developer

    Python
    FastAPI
    REST API
    Docker
    PostgreSQL
    Machine Learning
    """

    return JobMatchingService.match_candidates(
        db=db,
        job_description=job,
        top_k=5
    )