from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.dependencies.auth import (
    get_current_user,
    require_recruiter,
)

from app.models.user import User

from app.schemas.offer_schema import (
    OfferCreate,
    OfferResponse,
    OfferStatusUpdate,
    OfferUpdate,
)

from app.services.offer_service import OfferService


router = APIRouter(
    prefix="/offers",
    tags=["Offer Management"],
)


# ======================================================
# CREATE OFFER
# Recruiter only
# ======================================================

@router.post(
    "",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_offer(
    data: OfferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.create_offer(
        db=db,
        data=data,
    )


# ======================================================
# LIST ALL OFFERS
# Recruiter only
# ======================================================

@router.get(
    "",
    response_model=list[OfferResponse],
)
def list_offers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.list_offers(
        db=db,
    )


# ======================================================
# GET OFFER BY APPLICATION
# Candidate: own application only
# Recruiter: any application
# ======================================================

@router.get(
    "/application/{application_id}",
    response_model=OfferResponse,
)
def get_application_offer(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    offer = OfferService.get_application_offer(
        db=db,
        application_id=application_id,
    )

    if (
        current_user.role == "candidate"
        and offer.candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own offers"
            ),
        )

    return offer


# ======================================================
# GET OFFERS BY JOB
# Recruiter only
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=list[OfferResponse],
)
def get_job_offers(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.list_job_offers(
        db=db,
        job_id=job_id,
    )


# ======================================================
# GET OFFERS BY CANDIDATE
# Candidate: own offers only
# Recruiter: any candidate
# ======================================================

@router.get(
    "/candidate/{candidate_id}",
    response_model=list[OfferResponse],
)
def get_candidate_offers(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if (
        current_user.role == "candidate"
        and candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own offers"
            ),
        )

    return OfferService.list_candidate_offers(
        db=db,
        candidate_id=candidate_id,
    )


# ======================================================
# GET OFFER BY ID
# Candidate: own offer only
# Recruiter: any offer
# ======================================================

@router.get(
    "/{offer_id}",
    response_model=OfferResponse,
)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    offer = OfferService.get_offer(
        db=db,
        offer_id=offer_id,
    )

    if (
        current_user.role == "candidate"
        and offer.candidate_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Candidates can only view "
                "their own offers"
            ),
        )

    return offer


# ======================================================
# UPDATE OFFER DETAILS
# Recruiter only
# ======================================================

@router.patch(
    "/{offer_id}",
    response_model=OfferResponse,
)
def update_offer(
    offer_id: int,
    data: OfferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.update_offer(
        db=db,
        offer_id=offer_id,
        data=data,
    )


# ======================================================
# UPDATE OFFER STATUS
# Recruiter only
# ======================================================

@router.patch(
    "/{offer_id}/status",
    response_model=OfferResponse,
)
def update_offer_status(
    offer_id: int,
    data: OfferStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.update_status(
        db=db,
        offer_id=offer_id,
        data=data,
    )


# ======================================================
# DELETE OFFER
# Recruiter only
# ======================================================

@router.delete(
    "/{offer_id}",
)
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):

    return OfferService.delete_offer(
        db=db,
        offer_id=offer_id,
    )