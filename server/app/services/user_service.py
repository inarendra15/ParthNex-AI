from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.hashing import Hash
from app.core.security import JWTManager
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    def register(db: Session, request: UserCreate):

        existing = UserRepository.get_by_email(
            db,
            request.email
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        user = User(
            full_name=request.full_name,
            email=request.email,
            password=Hash.bcrypt(request.password)
        )

        return UserRepository.create(db, user)

    @staticmethod
    def login(db: Session, email: str, password: str):

        user = UserRepository.get_by_email(db, email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not Hash.verify(user.password, password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        token = JWTManager.create_access_token(
            {
                "sub": user.email,
                "role": user.role
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }