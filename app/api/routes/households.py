from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_household
from app.api.responses import (
    ACCOUNT_CONFLICT_RESPONSE,
    HOUSEHOLD_REQUIRED_RESPONSE,
    INVITE_INVALID_OR_USED_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.schemas.auth import UserResponse
from app.schemas.households import (
    CurrentHouseholdResponse,
    GenerateInviteRequest,
    GenerateInviteResponse,
    HouseholdCreateRequest,
    HouseholdResponse,
    JoinHouseholdRequest,
    JoinHouseholdResponse,
)
from app.services.households import create_household as create_household_service
from app.services.households import generate_invite as generate_invite_service
from app.services.households import get_current_household as get_current_household_service
from app.services.households import join_household as join_household_service

router = APIRouter(prefix="/households", tags=["households"])


@router.get(
    "/current",
    response_model=CurrentHouseholdResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
    },
)
def get_current_household(
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> CurrentHouseholdResponse:
    return get_current_household_service(db, current_user)


@router.post(
    "",
    response_model=HouseholdResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        409: ACCOUNT_CONFLICT_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def create_household(
    payload: HouseholdCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> HouseholdResponse:
    return create_household_service(db, current_user, payload.name)


@router.post(
    "/invite",
    response_model=GenerateInviteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        409: ACCOUNT_CONFLICT_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def generate_invite(
    payload: GenerateInviteRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> GenerateInviteResponse:
    return generate_invite_service(db, current_user, payload.household_id)


@router.post(
    "/join",
    response_model=JoinHouseholdResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        409: ACCOUNT_CONFLICT_RESPONSE,
        410: INVITE_INVALID_OR_USED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def join_household(
    payload: JoinHouseholdRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> JoinHouseholdResponse:
    return join_household_service(db, current_user, payload.invite_token)
