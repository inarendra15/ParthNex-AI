from pydantic import BaseModel, EmailStr


# ======================================================
# USER CREATE
# Public registration
# ======================================================

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


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