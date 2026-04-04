from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import DomainException
from app.models.household import Household
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.households import GenerateInviteResponse, HouseholdResponse, JoinHouseholdResponse


def _get_user(db: Session, user_id: UUID) -> User:
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise DomainException.unauthorized()
    return user


def _serialize_household(household: Household) -> HouseholdResponse:
    return HouseholdResponse(
        household_id=household.id,
        name=household.name,
        owner_id=household.owner_id,
    )


def _build_invite_url(invite_token: str) -> str:
    settings = get_settings()
    return f"{settings.frontend_base_url.rstrip('/')}/join/{invite_token}"


def create_household(db: Session, current_user: UserResponse, name: str) -> HouseholdResponse:
    user = _get_user(db, current_user.user_id)
    if user.household_id is not None:
        raise DomainException.conflict(
            detail="Voce ja faz parte de uma casa ativa.",
            code="HOUSEHOLD_ALREADY_ASSIGNED",
        )

    clean_name = name.strip()
    if not clean_name:
        generated_suffix = str(user.id)[:8]
        clean_name = f"Casa {generated_suffix}"

    household = Household(
        name=clean_name,
        owner_id=user.id,
    )
    db.add(household)
    db.flush()

    user.household_id = household.id
    db.add(user)
    db.commit()
    db.refresh(household)

    return _serialize_household(household)


def generate_invite(
    db: Session,
    current_user: UserResponse,
    household_id: UUID,
) -> GenerateInviteResponse:
    household = db.scalar(select(Household).where(Household.id == household_id))
    if household is None or household.id != current_user.household_id:
        raise DomainException.resource_not_found()

    if household.owner_id != current_user.user_id:
        raise DomainException(
            detail="Apenas o criador da casa pode gerar convites.",
            code="ONLY_OWNER_CAN_INVITE",
            status_code=403,
        )

    invite_token = f"JOIN-{secrets.token_urlsafe(9)}"
    expires_at = datetime.now(UTC) + timedelta(hours=24)

    household.invite_token = invite_token
    household.invite_expires_at = expires_at
    household.invite_used_at = None
    db.add(household)
    db.commit()

    return GenerateInviteResponse(
        invite_token=invite_token,
        invite_url=_build_invite_url(invite_token),
        expires_at=expires_at,
    )


def join_household(db: Session, current_user: UserResponse, invite_token: str) -> JoinHouseholdResponse:
    user = _get_user(db, current_user.user_id)
    if user.household_id is not None:
        raise DomainException.conflict(
            detail="Voce ja faz parte de uma casa ativa.",
            code="HOUSEHOLD_ALREADY_ASSIGNED",
        )

    household = db.scalar(select(Household).where(Household.invite_token == invite_token))
    if household is None:
        raise DomainException.invite_invalid_or_used()

    now = datetime.now(UTC)
    if household.invite_used_at is not None:
        raise DomainException.invite_invalid_or_used()
    if household.invite_expires_at is None or household.invite_expires_at <= now:
        raise DomainException.invite_invalid_or_used()

    user.household_id = household.id
    household.invite_used_at = now
    db.add(user)
    db.add(household)
    db.commit()

    return JoinHouseholdResponse(
        message="Bem-vindo a casa!",
        household_id=household.id,
        household_name=household.name,
    )
