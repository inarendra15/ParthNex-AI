from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.hashing import Hash
from app.core.security import JWTManager

from app.models.user import User

from app.repositories.user_repository import (
    UserRepository,
)

from app.schemas.user import UserCreate


class UserService:

    # ==================================================
    # REGISTER USER
    # Public registration always creates a candidate
    # ==================================================

    @staticmethod
    def register(
        db: Session,
        request: UserCreate,
    ):

        # ----------------------------------------------
        # Normalize Email
        # ----------------------------------------------

        email = str(request.email).strip().lower()

        # ----------------------------------------------
        # Prevent Duplicate Email
        # ----------------------------------------------

        existing = UserRepository.get_by_email(
            db,
            email,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        # ----------------------------------------------
        # Create Candidate
        #
        # Public registration must never allow the
        # client to assign recruiter privileges.
        # ----------------------------------------------

        user = User(
            full_name=request.full_name.strip(),
            email=email,
            password=Hash.bcrypt(
                request.password
            ),
            role="candidate",
            is_active=True,
        )

        return UserRepository.create(
            db,
            user,
        )

    # ==================================================
    # LOGIN
    # ==================================================

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):

        # ----------------------------------------------
        # Normalize Email
        # ----------------------------------------------

        normalized_email = (
            email.strip().lower()
        )

        # ----------------------------------------------
        # Find User
        # ----------------------------------------------

        user = UserRepository.get_by_email(
            db,
            normalized_email,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # ----------------------------------------------
        # Reject Disabled Account
        # ----------------------------------------------

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # ----------------------------------------------
        # Verify Password
        # ----------------------------------------------

        if not Hash.verify(
            user.password,
            password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # ----------------------------------------------
        # Create JWT
        # ----------------------------------------------

        token = JWTManager.create_access_token(
            {
                "sub": user.email,
                "role": user.role,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }