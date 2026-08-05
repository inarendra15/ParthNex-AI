from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.ats_schema import ATSRequest

from app.services.ats_service import ATSService


router = APIRouter(
    prefix="/ats",
    tags=["ATS Analysis"]
)


@router.post("/analyze")
def analyze(
    request: ATSRequest,
    db: Session = Depends(get_db)
):

    return ATSService.analyze_resume(
        db=db,
        resume_id=request.resume_id,
        job_description=request.job_description
    )