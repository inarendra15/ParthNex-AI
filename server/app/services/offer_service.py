from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.offer import Offer

from app.schemas.offer_schema import (
    OfferCreate,
    OfferStatusUpdate,
    OfferUpdate,
)


class OfferService:

    # ==================================================
    # ALLOWED STATUS TRANSITIONS
    # ==================================================

    STATUS_TRANSITIONS = {
        "draft": {
            "sent",
            "withdrawn",
        },

        "sent": {
            "accepted",
            "rejected",
            "withdrawn",
            "expired",
        },

        "accepted": set(),
        "rejected": set(),
        "withdrawn": set(),
        "expired": set(),
    }

    # ==================================================
    # CREATE OFFER
    # ==================================================

    @staticmethod
    def create_offer(
        db: Session,
        data: OfferCreate,
    ):

        # ----------------------------------------------
        # Validate Application
        # ----------------------------------------------

        application = (
            db.query(Application)
            .filter(
                Application.id
                == data.application_id
            )
            .first()
        )

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # ----------------------------------------------
        # Candidate Must Be Selected
        # ----------------------------------------------

        if application.status != "selected":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Offer can only be created for "
                    "a selected application"
                ),
            )

        # ----------------------------------------------
        # Prevent Duplicate Offer
        # ----------------------------------------------

        existing_offer = (
            db.query(Offer)
            .filter(
                Offer.application_id
                == application.id
            )
            .first()
        )

        if existing_offer is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An offer already exists for "
                    "this application"
                ),
            )

        # ----------------------------------------------
        # Create Offer
        #
        # job_id and candidate_id are derived from
        # the trusted Application record.
        # ----------------------------------------------

        offer = Offer(
            application_id=application.id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,

            offered_role=data.offered_role,

            salary=data.salary,
            currency=data.currency.upper(),

            joining_date=data.joining_date,

            offer_expiry_date=(
                data.offer_expiry_date
            ),

            status="draft",

            notes=data.notes,
        )

        try:
            db.add(offer)
            db.commit()
            db.refresh(offer)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An offer already exists for "
                    "this application"
                ),
            )

        return offer

    # ==================================================
    # GET OFFER
    # ==================================================

    @staticmethod
    def get_offer(
        db: Session,
        offer_id: int,
    ):

        offer = (
            db.query(Offer)
            .filter(
                Offer.id == offer_id
            )
            .first()
        )

        if offer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found",
            )

        return offer

    # ==================================================
    # LIST ALL OFFERS
    # ==================================================

    @staticmethod
    def list_offers(
        db: Session,
    ):

        return (
            db.query(Offer)
            .order_by(
                Offer.created_at.desc(),
                Offer.id.desc(),
            )
            .all()
        )

    # ==================================================
    # GET OFFER BY APPLICATION
    # ==================================================

    @staticmethod
    def get_application_offer(
        db: Session,
        application_id: int,
    ):

        # ----------------------------------------------
        # Validate Application
        # ----------------------------------------------

        application = (
            db.query(Application)
            .filter(
                Application.id
                == application_id
            )
            .first()
        )

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # ----------------------------------------------
        # Find Offer
        # ----------------------------------------------

        offer = (
            db.query(Offer)
            .filter(
                Offer.application_id
                == application_id
            )
            .first()
        )

        if offer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Offer not found for "
                    "this application"
                ),
            )

        return offer

    # ==================================================
    # LIST OFFERS FOR JOB
    # ==================================================

    @staticmethod
    def list_job_offers(
        db: Session,
        job_id: int,
    ):

        return (
            db.query(Offer)
            .filter(
                Offer.job_id == job_id
            )
            .order_by(
                Offer.created_at.desc(),
                Offer.id.desc(),
            )
            .all()
        )

    # ==================================================
    # LIST OFFERS FOR CANDIDATE
    # ==================================================

    @staticmethod
    def list_candidate_offers(
        db: Session,
        candidate_id: int,
    ):

        return (
            db.query(Offer)
            .filter(
                Offer.candidate_id
                == candidate_id
            )
            .order_by(
                Offer.created_at.desc(),
                Offer.id.desc(),
            )
            .all()
        )

    # ==================================================
    # UPDATE OFFER DETAILS
    # ==================================================

    @staticmethod
    def update_offer(
        db: Session,
        offer_id: int,
        data: OfferUpdate,
    ):

        offer = OfferService.get_offer(
            db=db,
            offer_id=offer_id,
        )

        # ----------------------------------------------
        # Terminal offers cannot be edited
        # ----------------------------------------------

        if offer.status in {
            "accepted",
            "rejected",
            "withdrawn",
            "expired",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Finalized offer cannot be edited"
                ),
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # ----------------------------------------------
        # Calculate Effective Dates
        #
        # This validates partial PATCH requests against
        # values already stored in the database.
        # ----------------------------------------------

        effective_joining_date = (
            update_data.get(
                "joining_date",
                offer.joining_date,
            )
        )

        effective_expiry_date = (
            update_data.get(
                "offer_expiry_date",
                offer.offer_expiry_date,
            )
        )

        if (
            effective_joining_date is not None
            and effective_expiry_date is not None
            and effective_expiry_date
            > effective_joining_date
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Offer expiry date cannot be "
                    "after joining date"
                ),
            )

        # ----------------------------------------------
        # Apply Updates
        # ----------------------------------------------

        for field, value in update_data.items():

            if (
                field == "currency"
                and value is not None
            ):
                value = value.upper()

            setattr(
                offer,
                field,
                value,
            )

        db.commit()
        db.refresh(offer)

        return offer

    # ==================================================
    # UPDATE OFFER STATUS
    # ==================================================

    @staticmethod
    def update_status(
        db: Session,
        offer_id: int,
        data: OfferStatusUpdate,
    ):

        offer = OfferService.get_offer(
            db=db,
            offer_id=offer_id,
        )

        current_status = offer.status
        new_status = data.status

        # ----------------------------------------------
        # Same status = return current state
        # ----------------------------------------------

        if current_status == new_status:
            return offer

        # ----------------------------------------------
        # Validate Status Transition
        # ----------------------------------------------

        allowed_transitions = (
            OfferService.STATUS_TRANSITIONS.get(
                current_status,
                set(),
            )
        )

        if new_status not in allowed_transitions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Invalid offer status transition: "
                    f"{current_status} -> {new_status}"
                ),
            )

        # ----------------------------------------------
        # Get Associated Application
        # ----------------------------------------------

        application = (
            db.query(Application)
            .filter(
                Application.id
                == offer.application_id
            )
            .first()
        )

        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found",
            )

        # ----------------------------------------------
        # Apply Offer Status
        # ----------------------------------------------

        offer.status = new_status

        # ----------------------------------------------
        # Synchronize Application
        # ----------------------------------------------
        #
        # accepted:
        # Application stays selected.
        #
        # rejected:
        # Candidate explicitly rejected the offer.
        # Application becomes rejected.
        #
        # withdrawn / expired:
        # We preserve the selected application state.
        # This avoids incorrectly treating an expired
        # recruiter offer as candidate rejection.
        # ----------------------------------------------

        if new_status == "accepted":
            application.status = "selected"

        elif new_status == "rejected":
            application.status = "rejected"
            application.shortlisted = False

        # ----------------------------------------------
        # Commit Atomically
        # ----------------------------------------------

        db.commit()

        db.refresh(offer)
        db.refresh(application)

        return offer

    # ==================================================
    # DELETE OFFER
    # ==================================================

    @staticmethod
    def delete_offer(
        db: Session,
        offer_id: int,
    ):

        offer = OfferService.get_offer(
            db=db,
            offer_id=offer_id,
        )

        # ----------------------------------------------
        # Do not delete finalized offers
        # ----------------------------------------------

        if offer.status in {
            "accepted",
            "rejected",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Accepted or rejected offers "
                    "cannot be deleted"
                ),
            )

        db.delete(offer)
        db.commit()

        return {
            "message": "Offer deleted successfully",
            "offer_id": offer_id,
        }