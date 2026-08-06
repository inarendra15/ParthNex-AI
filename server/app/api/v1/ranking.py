from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.ranking_schema import RankingRequest
from app.services.ranking_service import RankingService


router = APIRouter(
    prefix="/ranking",
    tags=["Candidate Ranking"]
)


@router.post("/candidates")
def rank_candidates(
    request: RankingRequest,
    db: Session = Depends(get_db)
):

    return RankingService.rank_candidates(
        db=db,
        job_description=request.job_description,
        top_k=request.top_k,
        shortlist_threshold=request.shortlist_threshold
    )