from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl


class GoogleAuthRequest(BaseModel):
    google_id_token: str


class UserResponse(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    avatar_url: HttpUrl | None = None
    household_id: UUID | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_new_user: bool
