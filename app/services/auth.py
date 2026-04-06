from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import DomainException
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import AuthResponse, UserResponse


@dataclass
class GoogleIdentity:
    subject: str
    email: str
    name: str
    avatar_url: str | None
    email_verified: bool


def verify_google_id_token(google_id_token: str) -> GoogleIdentity:
    settings = get_settings()
    try:
        payload: dict[str, Any] = id_token.verify_oauth2_token(
            google_id_token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except Exception as exc:  # pragma: no cover - network/provider errors
        raise DomainException.invalid_google_token() from exc

    if not payload.get("email") or not payload.get("sub"):
        raise DomainException.invalid_google_token()

    email_verified = bool(payload.get("email_verified"))
    if not email_verified:
        raise DomainException.invalid_google_token()

    return GoogleIdentity(
        subject=str(payload["sub"]),
        email=str(payload["email"]).strip().lower(),
        name=str(payload.get("name") or payload["email"]).strip(),
        avatar_url=payload.get("picture"),
        email_verified=email_verified,
    )


def authenticate_with_google(db: Session, google_id_token: str) -> AuthResponse:
    try:
        identity = verify_google_id_token(google_id_token)
    except DomainException:
        raise
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise DomainException.invalid_google_token() from exc

    user = db.scalar(select(User).where(User.google_subject == identity.subject))
    is_new_user = False

    if user is None:
        existing_user = db.scalar(select(User).where(User.email == identity.email))
        if existing_user is not None:
            raise DomainException.conflict(
                detail="Ja existe um usuario com este email vinculado a outra conta Google.",
                code="ACCOUNT_CONFLICT",
            )

        user = User(
            google_subject=identity.subject,
            email=identity.email,
            name=identity.name,
            avatar_url=identity.avatar_url,
            household_id=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new_user = True
    else:
        user.email = identity.email
        user.name = identity.name
        user.avatar_url = identity.avatar_url
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        household_id=user.household_id,
        token_version=user.token_version,
    )

    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            avatar_url=user.avatar_url,
            household_id=user.household_id,
        ),
        is_new_user=is_new_user,
    )
