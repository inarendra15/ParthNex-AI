from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/login"
)


# ======================================================
# GET CURRENT AUTHENTICATED USER
# ======================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )

        email = payload.get("sub")

        if not email:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # --------------------------------------------------
    # Load User From Database
    # --------------------------------------------------

    user = UserRepository.get_by_email(
        db,
        email,
    )

    if user is None:
        raise credentials_exception

    # --------------------------------------------------
    # Reject Disabled Accounts
    # --------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# ======================================================
# REQUIRE RECRUITER
# ======================================================

def require_recruiter(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:

    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter access required",
        )

    return current_user


# ======================================================
# REQUIRE CANDIDATE
# ======================================================

def require_candidate(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:

    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Candidate access required",
        )

    return current_user