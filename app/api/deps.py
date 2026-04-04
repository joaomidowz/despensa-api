from collections.abc import Generator
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import DomainException
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/google", auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    if token is None:
        raise DomainException.unauthorized()

    payload = decode_access_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise DomainException.unauthorized()

    try:
        user_id = UUID(str(subject))
    except ValueError as exc:
        raise DomainException.unauthorized() from exc

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise DomainException.unauthorized()

    return UserResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        household_id=user.household_id,
    )


def require_household(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if current_user.household_id is None:
        raise DomainException.household_required()
    return current_user
