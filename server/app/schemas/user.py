from typing import Literal

from pydantic import BaseModel, EmailStr


# ======================================================
# USER CREATE
# ======================================================

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    role: Literal[
        "candidate",
        "recruiter",
    ] = "candidate"


# ======================================================
# USER RESPONSE
# ======================================================

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True