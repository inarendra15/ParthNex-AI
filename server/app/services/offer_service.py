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

from app.services.activity_service import ActivityService


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
    # ACTIVITY TYPE MAPPING
    # ==================================================

    STATUS_ACTIVITY_TYPES = {
        "sent": "offer_sent",
        "accepted": "offer_accepted",
        "rejected": "offer_rejected",
        "withdrawn": "offer_withdrawn",
        "expired": "offer_expired",
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

            # Get offer.id without committing.
            db.flush()

            # ------------------------------------------
            # Audit Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="offer_created",
                entity_type="offer",
                entity_id=offer.id,
                application_id=offer.application_id,
                job_id=offer.job_id,
                candidate_id=offer.candidate_id,
                title="Offer created",
                description=(
                    f"Offer for "
                    f"{offer.offered_role} "
                    f"was created."
                ),
                old_status=None,
                new_status="draft",
                commit=False,
            )

            # Offer + activity commit together.
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

        except Exception:

            db.rollback()
            raise

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
        # Terminal Offers Cannot Be Edited
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

        if not update_data:
            return offer

        # ----------------------------------------------
        # Normalize Currency Before Comparison
        # ----------------------------------------------

        if (
            "currency" in update_data
            and update_data["currency"] is not None
        ):
            update_data["currency"] = (
                update_data["currency"].upper()
            )

        # ----------------------------------------------
        # Calculate Effective Dates
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
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail=(
                    "Offer expiry date cannot be "
                    "after joining date"
                ),
            )

        # ----------------------------------------------
        # Detect Real Changes
        # ----------------------------------------------

        changed_fields = []

        for field, value in update_data.items():

            old_value = getattr(
                offer,
                field,
            )

            if old_value != value:

                setattr(
                    offer,
                    field,
                    value,
                )

                changed_fields.append(field)

        # No-op update
        if not changed_fields:
            return offer

        try:

            ActivityService.log_activity(
                db=db,
                activity_type=(
                    "offer_details_updated"
                ),
                entity_type="offer",
                entity_id=offer.id,
                application_id=offer.application_id,
                job_id=offer.job_id,
                candidate_id=offer.candidate_id,
                title="Offer details updated",
                description=(
                    "Updated offer fields: "
                    + ", ".join(changed_fields)
                    + "."
                ),
                commit=False,
            )

            db.commit()
            db.refresh(offer)

        except Exception:

            db.rollback()
            raise

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
        # Same Status = No-op
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
        # Capture Application State
        # ----------------------------------------------

        old_application_status = (
            application.status
        )

        # ----------------------------------------------
        # Apply Offer Status
        # ----------------------------------------------

        offer.status = new_status

        # ----------------------------------------------
        # Synchronize Application
        # ----------------------------------------------

        if new_status == "accepted":

            application.status = "selected"

        elif new_status == "rejected":

            application.status = "rejected"
            application.shortlisted = False

        new_application_status = (
            application.status
        )

        application_status_changed = (
            old_application_status
            != new_application_status
        )

        # ----------------------------------------------
        # Resolve Offer Activity Type
        # ----------------------------------------------

        activity_type = (
            OfferService.STATUS_ACTIVITY_TYPES.get(
                new_status,
                "offer_status_changed",
            )
        )

        try:

            # ------------------------------------------
            # Offer Status Activity
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type=activity_type,
                entity_type="offer",
                entity_id=offer.id,
                application_id=offer.application_id,
                job_id=offer.job_id,
                candidate_id=offer.candidate_id,
                title="Offer status changed",
                description=(
                    f"Offer status changed from "
                    f"{current_status} to "
                    f"{new_status}."
                ),
                old_status=current_status,
                new_status=new_status,
                commit=False,
            )

            # ------------------------------------------
            # Application Status Activity
            # ------------------------------------------
            #
            # Only generated if the offer transition
            # actually changes the application state.
            # ------------------------------------------

            if application_status_changed:

                ActivityService.log_activity(
                    db=db,
                    activity_type=(
                        "application_status_changed"
                    ),
                    entity_type="application",
                    entity_id=application.id,
                    application_id=application.id,
                    job_id=application.job_id,
                    candidate_id=application.candidate_id,
                    title="Application status changed",
                    description=(
                        "Application status changed "
                        f"from {old_application_status} "
                        f"to {new_application_status} "
                        "after offer status update."
                    ),
                    old_status=old_application_status,
                    new_status=(
                        new_application_status
                    ),
                    commit=False,
                )

            # Offer + application + activities
            # commit together.
            db.commit()

            db.refresh(offer)
            db.refresh(application)

        except Exception:

            db.rollback()
            raise

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
        # Do Not Delete Finalized Offers
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

        # ----------------------------------------------
        # Preserve Historical Values
        # ----------------------------------------------

        deleted_offer_id = offer.id

        application_id = (
            offer.application_id
        )

        job_id = offer.job_id
        candidate_id = offer.candidate_id

        old_status = offer.status

        offered_role = offer.offered_role

        try:

            # ------------------------------------------
            # Audit Before Delete
            # ------------------------------------------
            #
            # Activity has no FK to Offer through
            # entity_id, so the historical offer ID
            # remains safe after deletion.
            # ------------------------------------------

            ActivityService.log_activity(
                db=db,
                activity_type="offer_deleted",
                entity_type="offer",
                entity_id=deleted_offer_id,
                application_id=application_id,
                job_id=job_id,
                candidate_id=candidate_id,
                title="Offer deleted",
                description=(
                    f"Offer for {offered_role} "
                    f"was deleted."
                ),
                old_status=old_status,
                new_status=None,
                commit=False,
            )

            db.delete(offer)

            db.commit()

        except Exception:

            db.rollback()
            raise

        return {
            "message": "Offer deleted successfully",
            "offer_id": deleted_offer_id,
        }