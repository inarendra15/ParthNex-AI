from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

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
# ======================================================

@router.post(
    "",
    response_model=OfferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_offer(
    data: OfferCreate,
    db: Session = Depends(get_db),
):

    return OfferService.create_offer(
        db=db,
        data=data,
    )


# ======================================================
# LIST ALL OFFERS
# ======================================================

@router.get(
    "",
    response_model=list[OfferResponse],
)
def list_offers(
    db: Session = Depends(get_db),
):

    return OfferService.list_offers(
        db=db,
    )


# ======================================================
# GET OFFER BY APPLICATION
# ======================================================

@router.get(
    "/application/{application_id}",
    response_model=OfferResponse,
)
def get_application_offer(
    application_id: int,
    db: Session = Depends(get_db),
):

    return OfferService.get_application_offer(
        db=db,
        application_id=application_id,
    )


# ======================================================
# GET OFFERS BY JOB
# ======================================================

@router.get(
    "/job/{job_id}",
    response_model=list[OfferResponse],
)
def get_job_offers(
    job_id: int,
    db: Session = Depends(get_db),
):

    return OfferService.list_job_offers(
        db=db,
        job_id=job_id,
    )


# ======================================================
# GET OFFERS BY CANDIDATE
# ======================================================

@router.get(
    "/candidate/{candidate_id}",
    response_model=list[OfferResponse],
)
def get_candidate_offers(
    candidate_id: int,
    db: Session = Depends(get_db),
):

    return OfferService.list_candidate_offers(
        db=db,
        candidate_id=candidate_id,
    )


# ======================================================
# GET OFFER BY ID
# ======================================================

@router.get(
    "/{offer_id}",
    response_model=OfferResponse,
)
def get_offer(
    offer_id: int,
    db: Session = Depends(get_db),
):

    return OfferService.get_offer(
        db=db,
        offer_id=offer_id,
    )


# ======================================================
# UPDATE OFFER DETAILS
# ======================================================

@router.patch(
    "/{offer_id}",
    response_model=OfferResponse,
)
def update_offer(
    offer_id: int,
    data: OfferUpdate,
    db: Session = Depends(get_db),
):

    return OfferService.update_offer(
        db=db,
        offer_id=offer_id,
        data=data,
    )


# ======================================================
# UPDATE OFFER STATUS
# ======================================================

@router.patch(
    "/{offer_id}/status",
    response_model=OfferResponse,
)
def update_offer_status(
    offer_id: int,
    data: OfferStatusUpdate,
    db: Session = Depends(get_db),
):

    return OfferService.update_status(
        db=db,
        offer_id=offer_id,
        data=data,
    )


# ======================================================
# DELETE OFFER
# ======================================================

@router.delete(
    "/{offer_id}",
)
def delete_offer(
    offer_id: int,
    db: Session = Depends(get_db),
):

    return OfferService.delete_offer(
        db=db,
        offer_id=offer_id,
    )