from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import get_settings
from app.core.exceptions import DomainException


def create_access_token(*, user_id: UUID, email: str, household_id: UUID | None, token_version: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expires_in_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "household_id": str(household_id) if household_id is not None else None,
        "token_version": token_version,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise DomainException.unauthorized() from exc
