from fastapi import APIRouter, status

from app.api.responses import (
    HOUSEHOLD_REQUIRED_RESPONSE,
    INVITE_INVALID_OR_USED_RESPONSE,
    NOT_IMPLEMENTED_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.core.exceptions import DomainException
from app.schemas.households import (
    GenerateInviteRequest,
    GenerateInviteResponse,
    HouseholdCreateRequest,
    HouseholdResponse,
    JoinHouseholdRequest,
    JoinHouseholdResponse,
)

router = APIRouter(prefix="/households", tags=["households"])


@router.post(
    "",
    response_model=HouseholdResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def create_household(payload: HouseholdCreateRequest) -> HouseholdResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "/invite",
    response_model=GenerateInviteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def generate_invite(payload: GenerateInviteRequest) -> GenerateInviteResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "/join",
    response_model=JoinHouseholdResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        410: INVITE_INVALID_OR_USED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def join_household(payload: JoinHouseholdRequest) -> JoinHouseholdResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)
